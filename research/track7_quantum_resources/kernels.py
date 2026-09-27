"""
Track 7 — the three kernels K1/K2/K3, resource-estimated as a function of problem size.
Each kernel returns (logical qubits n_L, T-count N_T, T-depth D_T) with EVERY algorithmic
assumption carried as a named column, plus the NAMED optimized classical baseline (code + hardware)
and its FLOP/wall-clock curve, and the crossover verdict.

PROVENANCE: RESOURCE-EST. Assumes fault-tolerant hardware that does not yet exist. No measurement.
NO Kronos operating-plant data exists.

Citations (resolved): quantum-Vlasov Engel 2019 (10.1103/PhysRevA.100.062315); plasma-QC survey
Dodin-Startsev 2021 (10.1063/5.0056974); cold-plasma-wave QSP Novikau 2022 (10.1103/PhysRevA.105.062444);
nonlinearity embedding Joseph 2020 (10.1103/PhysRevResearch.2.043102); Hamiltonian-sim primitive
Low-Chuang 2019 (10.22331/q-2019-07-12-163); LCU Berry 2015 (10.1109/FOCS.2015.54); qubitization/QSVT
Gilyen 2019 (10.1145/3313276.3316366); QLSA Harrow-Hassidim-Lloyd 2009 (10.1103/PhysRevLett.103.150502);
improved QLSA Childs-Kothari-Somma 2017 (10.1137/16M1087072); optimal-scaling QLSA Costa 2022
(10.1103/PRXQuantum.3.040303); "read the fine print" Aaronson 2015 (10.1038/nphys3272); QPE/chem
von Burg 2021 (10.1103/PhysRevResearch.3.033055); tensor-hypercontraction Lee 2021 (10.1103/PRXQuantum.2.030305);
linear-T Babbush 2018 (10.1103/PhysRevX.8.041015); classical gyrokinetic anchor Candy-Waltz 2003
(10.1016/S0021-9991(03)00079-2); EFIT Grad-Shafranov Lao 1985 (10.1088/0029-5515/25/11/007).
"""
import numpy as np, pandas as pd, math, os
from ft_cost_model import ft_costs, HW_SCENARIOS, PARAMS

HERE = os.path.dirname(os.path.abspath(__file__))
LOG2E = 1.0/math.log(2)
def log2(x): return math.log(x)*LOG2E

# =====================================================================================
# K1 — kinetic / Vlasov collision operator (E3). 5-D phase space after gyroaveraging.
#   Quantum: Hamiltonian simulation / qubitization / LCU of the discretised operator.
#   NONLINEARITY (bilinear collision op) -> Carleman/Koopman-von Neumann linearisation:
#   the lifted state tower x, x^2, ..., x^K multiplies the qubit count by the truncation
#   order K_c. This is the EXPLICIT nonlinearity line item (AC-40).
# =====================================================================================
K1_ASSUME = {
    "phase_space_dim_d": 5,               # after gyroaveraging (E3.3)
    "carleman_order_Kc_low": 2,           # Koopman/Carleman truncation order (Joseph 2020)
    "carleman_order_Kc_mid": 3,
    "carleman_order_Kc_high": 4,
    "sim_time_collisional_times": 10.0,   # integrate ~10 collision times for a transport-relevant closure
    "target_error_eps": 1e-3,
    "be_ancilla_qubits": 40,              # LCU/QSVT ancillas + clock register (order-of-mag)
    # block-encoding normalisation alpha*tau scaling: stiff kinetic operator, nonlocal collision.
    #   alpha ~ (velocity-space diffusion eigenvalue ~ N^2) x (stiffness factor).  We use N^2.
    "alpha_tau_exponent_on_N": 2.0,
    "alpha_tau_prefactor": 1.0e3,         # includes stiffness Omega_ci/omega_transport ~ 1e9 folded into steps (see note)
    # T per block-encoding query: dominated by coefficient loading (Landau tensor, nonlocal in
    #   3 velocity dims -> O(N^3) distinct couplings) via QROM.  QROM T-count ~ table size.
    "Tcount_per_query_exponent_on_N": 3.0,
    "Tcount_per_query_prefactor": 4.0,    # ~ a few T per QROM entry
}
def K1_resources(N, Kc, A=K1_ASSUME):
    n_sys = math.ceil(A["phase_space_dim_d"]*log2(N))          # qubits for linear 5-D state
    n_L = Kc*n_sys + A["be_ancilla_qubits"]                    # Carleman tower x qubits + ancillas
    alpha_tau = A["alpha_tau_prefactor"]*N**A["alpha_tau_exponent_on_N"]
    Q = alpha_tau + math.log(1.0/A["target_error_eps"])       # qubitization query count
    # Carleman raises the effective block-encoding size: the lifted operator acts on x^{<=Kc},
    # so the per-query coefficient table is O(N^3) but repeated across the Kc-block structure.
    C_be = A["Tcount_per_query_prefactor"]*(N**A["Tcount_per_query_exponent_on_N"])*Kc
    N_T = Q*C_be
    D_T = Q*max(1.0, C_be/1.0)          # sequential block-encoding depth (no factory parallelism inside a query)
    return dict(n_L=n_L, N_T=N_T, D_T=Q*C_be, n_sys=n_sys)

def K1_classical_flops(N, n_steps_per_ctime=100):
    # NAMED baseline: CGYRO/GENE-class Eulerian gyrokinetic (Candy & Waltz 2003).
    # 5-D grid N^5 unknowns; nonlocal velocity-space collision couples ~N^3 -> per-step ~ N^5 * N^3
    # naive; with fast/multigrid velocity solve ~ N^5 * N (we carry naive as 'high', mg as 'low').
    steps = n_steps_per_ctime*int(K1_ASSUME["sim_time_collisional_times"])
    dof = N**5
    flops_high = dof*(N**3)*steps        # naive nonlocal collision
    flops_low  = dof*(N)*steps           # multigrid velocity solve
    return flops_low, flops_high

# =====================================================================================
# K2 — equilibrium / MHD linear-solve (E1). Ax=b per Newton step, A is N_gx N_g sparse
#   from discretising the Grad-Shafranov elliptic operator on a 2-D grid.
#   Quantum: improved QLSA (HHL / Childs-Kothari-Somma / Costa optimal-scaling).
#   LEAD ADVERSE: read-in (state prep O(N)) and read-out (full-field tomography O(N/eps^2))
#   erase the polylog(N) advantage; kappa(A) ~ N_g for a fine elliptic grid.  (AC-41)
# =====================================================================================
K2_ASSUME = {
    "grid_unknowns_low": 1e4,             # 2-D equilibrium grid N_g (canon E1.6: N~1e4-1e5)
    "grid_unknowns_high": 1e5,
    "sparsity_s": 5,                      # 5-point stencil
    "kappa_exponent_on_Ng": 1.0,          # kappa ~ N_g for elliptic operator on fine grid
    "kappa_prefactor": 1.0,
    "target_error_eps": 1e-3,
    "qlsa_query_kappa_power": 1.0,        # Costa 2022 optimal: O(kappa log(1/eps)) queries
    "be_ancilla_qubits": 30,
    "Tcount_per_query_prefactor": 4.0,
    "Tcount_per_query_sparsity_factor": True,  # T per query ~ s * polylog(N)
    # READ-IN: arbitrary b (p'(psi),FF'(psi) on shaped negative-delta boundary -> NO structure)
    #   costs O(N_g) T-gates to prepare |b>.  (canon E1.6)
    "readin_Tcount_prefactor": 4.0,
    "readin_exponent_on_Ng": 1.0,
    # READ-OUT: control needs psi on the WHOLE grid (coil currents/flux map), not one <M>.
    #   Full amplitude read-out = O(N_g) amplitudes x O(1/eps^2) samples, each a full QLSA run.
    "readout_samples_per_amp": None,      # = 1/eps^2, computed
}
def K2_resources(Ng, A=K2_ASSUME):
    n_sys = math.ceil(log2(Ng))
    n_L = n_sys + A["be_ancilla_qubits"]
    kappa = A["kappa_prefactor"]*Ng**A["kappa_exponent_on_Ng"]
    eps = A["target_error_eps"]
    Q_solve = kappa*math.log(1.0/eps)                        # QLSA query count (optimal kappa scaling)
    C_be = A["Tcount_per_query_prefactor"]*A["sparsity_s"]*log2(Ng)
    T_solve = Q_solve*C_be                                   # cost of ONE QLSA solve -> quantum state |psi>
    # read-in cost (per solve)
    T_readin = A["readin_Tcount_prefactor"]*Ng**A["readin_exponent_on_Ng"]
    # read-out: to get the full field to accuracy eps need O(Ng) amplitudes, each O(1/eps^2) samples;
    # each sample requires re-running solve+readin (state is destroyed on measurement).
    samples = 1.0/eps**2
    n_reruns_readout = Ng*samples                            # number of (solve+readin) repetitions
    T_per_run = T_solve + T_readin
    N_T_endtoend = n_reruns_readout*T_per_run               # END-TO-END T-count for the ACTUAL output (full field)
    N_T_solveonly = T_solve + T_readin                      # the misleading 'one solve' number
    D_T = T_per_run                                         # depth of a single run (reruns are repetitions, not depth)
    return dict(n_L=n_L, kappa=kappa, T_solve=T_solve, T_readin=T_readin,
                N_T=N_T_endtoend, N_T_solveonly=N_T_solveonly, n_reruns_readout=n_reruns_readout,
                D_T=D_T, n_sys=n_sys)

def K2_classical_flops(Ng):
    # NAMED baseline: EFIT-class multigrid Grad-Shafranov solver (Lao 1985), single CPU.
    # Multigrid solves an N_g-unknown sparse elliptic system in O(N_g) FLOPs.
    return 50.0*Ng, 200.0*Ng   # low/high constant

# =====================================================================================
# K3 — first-wall / conductor materials (E8). Ground-state energetics via QPE/qubitization
#   of the second-quantised electronic Hamiltonian in an ACTIVE SPACE of M spin-orbitals.
#   Costs follow modern FT chemistry: von Burg 2021 / Lee 2021 (THC) / Babbush 2018 (linear-T).
#   AC-42: active space printed AND the reduction stated as a limitation.
# =====================================================================================
K3_ASSUME = {
    "qubits_per_spinorbital": 1,          # Jordan-Wigner / compact mapping: n_L ~ M
    "qpe_ancilla_bits": 20,               # phase-estimation register (~ chemical accuracy)
    "target_error_Ha": 1.6e-3,            # chemical accuracy
    # T-count for a full QPE with a THC/linear-T block-encoding: N_T ~ (lambda/eps) * C_walk,
    #   C_walk ~ O(M) (linear-T, Babbush 2018) to O(M^2) (double-factorised).  lambda ~ M^{1.5..2}.
    "lambda_exponent_on_M_low": 1.5,
    "lambda_exponent_on_M_high": 2.0,
    "lambda_prefactor": 1.0,              # 1-norm prefactor (Ha), order 1-10 per orbital
    "walk_Tcount_exponent_on_M_low": 1.0, # linear-T encoding (Babbush 2018)
    "walk_Tcount_exponent_on_M_high": 2.0,# double-factorised
    "walk_Tcount_prefactor": 4.0,
}
def K3_resources(M, lam_exp, walk_exp, A=K3_ASSUME):
    n_L = A["qubits_per_spinorbital"]*M + A["qpe_ancilla_bits"]
    lam = A["lambda_prefactor"]*M**lam_exp
    eps = A["target_error_Ha"]
    Q = lam/eps                                            # QPE queries ~ lambda/eps
    C_walk = A["walk_Tcount_prefactor"]*M**walk_exp
    N_T = Q*C_walk
    D_T = N_T                                              # QPE is sequential
    return dict(n_L=n_L, lam=lam, Q=Q, N_T=N_T, D_T=D_T)

def K3_classical_flops(M, n_elec=None):
    # NAMED baseline: DMRG (Block2, Chan group) / CCSD(T) (PySCF), single HPC node.
    # CCSD(T) ~ O(M^7); DMRG ~ O(M^3 * D_bond^2). We carry CCSD(T) M^7 (high) and DMRG-ish M^4 (low).
    flops_low  = 1e2*M**4      # DMRG moderate bond dim
    flops_high = 1e1*M**7      # CCSD(T)
    return flops_low, flops_high

if __name__ == "__main__":
    print("K1 N=64 Kc=3:", {k:(f'{v:.3e}' if isinstance(v,float) else v) for k,v in K1_resources(64,3).items()})
    print("K1 classical N=64:", ['%.3e'%x for x in K1_classical_flops(64)])
    print("K2 Ng=1e4:", {k:(f'{v:.3e}' if isinstance(v,float) else v) for k,v in K2_resources(1e4).items()})
    print("K2 classical Ng=1e4:", ['%.3e'%x for x in K2_classical_flops(1e4)])
    print("K3 M=100 lam1.75 walk1.5:", {k:(f'{v:.3e}' if isinstance(v,float) else v) for k,v in K3_resources(100,1.75,1.5).items()})
    print("K3 classical M=100:", ['%.3e'%x for x in K3_classical_flops(100)])
