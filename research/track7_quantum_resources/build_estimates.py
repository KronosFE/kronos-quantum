"""
Track 7 driver — sweeps K1/K2/K3 over problem size, applies the ONE ft cost model, computes
classical wall-clock on NAMED optimized code + NAMED hardware, finds the crossover (or its absence),
and writes quantum_resource_estimate.csv + taxonomy + per-kernel threshold/date rows.

PROVENANCE: RESOURCE-EST. Assumes fault-tolerant hardware that does not yet exist. Not a measurement.
NO Kronos operating-plant data exists.
"""
import numpy as np, pandas as pd, math, os, sys
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from ft_cost_model import ft_costs, HW_SCENARIOS
import kernels as K

# NAMED classical baselines: (code, hardware, sustained FLOP/s)
CLASSICAL = {
  "K1": dict(code="CGYRO/GENE Eulerian gyrokinetic (Candy-Waltz 2003, doi:10.1016/S0021-9991(03)00079-2)",
             hardware="1 node NERSC Perlmutter CPU (AMD EPYC 7763, 64c)", flop_rate=2.0e12),
  "K2": dict(code="EFIT-class multigrid Grad-Shafranov solver (Lao 1985, doi:10.1088/0029-5515/25/11/007)",
             hardware="1 core Intel Xeon (3 GHz, AVX-512)", flop_rate=1.0e10),
  "K3": dict(code="DMRG (Block2, Chan group) [optimized] / CCSD(T) (PySCF) [naive]",
             hardware="1 node HPC (2x AMD EPYC, 256 GB)", flop_rate=1.0e12),
}

def qwall(res, scenario):
    ft = ft_costs(res["n_L"], res["N_T"], res["D_T"], scenario)
    return ft, ft["wall_clock_s"]

rows=[]
# ---------------- K1 sweep: grid points/dim N = 16..256, Carleman order low/mid/high ---------
for N in [16,32,48,64,96,128,192,256]:
    fl_lo, fl_hi = K.K1_classical_flops(N)
    cwall_lo = fl_lo/CLASSICAL["K1"]["flop_rate"]; cwall_hi = fl_hi/CLASSICAL["K1"]["flop_rate"]
    for lvl,Kc in [("low",K.K1_ASSUME["carleman_order_Kc_low"]),
                   ("mid",K.K1_ASSUME["carleman_order_Kc_mid"]),
                   ("high",K.K1_ASSUME["carleman_order_Kc_high"])]:
        r=K.K1_resources(N,Kc)
        ft_b,qw_b = qwall(r,"baseline")
        rows.append(dict(kernel="K1", problem_metric="grid_pts_per_dim_N", problem_size=N,
            range_level=lvl, carleman_order_Kc=Kc, nonlinearity_cost="Carleman/KvN tower x Kc qubits + O(N^3) coeff table (Joseph 2020)",
            dof_classical=N**5, logical_qubits=r["n_L"], T_count=r["N_T"], T_depth=r["D_T"],
            code_distance=ft_b["code_distance"], phys_qubits=ft_b["phys_qubits"], n_factories=ft_b["n_factories"],
            q_wall_s_baseline=qw_b,
            classical_flops_low=fl_lo, classical_flops_high=fl_hi,
            classical_wall_s_low=cwall_lo, classical_wall_s_high=cwall_hi,
            classical_code=CLASSICAL["K1"]["code"], classical_hw=CLASSICAL["K1"]["hardware"],
            classical_flop_rate=CLASSICAL["K1"]["flop_rate"],
            readin_Tcount=np.nan, readout_reruns=np.nan, N_T_solveonly=np.nan, kappa=np.nan, active_space_M=np.nan))
# ---------------- K2 sweep: grid unknowns Ng = 1e3..1e6 ---------------------------------------
for Ng in [1e3,3e3,1e4,3e4,1e5,3e5,1e6]:
    fl_lo, fl_hi = K.K2_classical_flops(Ng)
    cwall_lo=fl_lo/CLASSICAL["K2"]["flop_rate"]; cwall_hi=fl_hi/CLASSICAL["K2"]["flop_rate"]
    r=K.K2_resources(Ng)
    ft_b,qw_b=qwall(dict(n_L=r["n_L"],N_T=r["N_T"],D_T=r["D_T"]),"baseline")
    # for K2 we report BOTH the misleading solve-only and the honest end-to-end
    ft_solve,qw_solve = qwall(dict(n_L=r["n_L"],N_T=r["N_T_solveonly"],D_T=r["D_T"]),"baseline")
    for lvl in ["low","mid","high"]:
        rows.append(dict(kernel="K2", problem_metric="grid_unknowns_Ng", problem_size=Ng,
            range_level=lvl, carleman_order_Kc=np.nan, nonlinearity_cost="n/a (linear system)",
            dof_classical=Ng, logical_qubits=r["n_L"],
            T_count=(r["N_T_solveonly"] if lvl=="low" else r["N_T"]),   # low=optimistic solve-only illusion; mid/high=end-to-end
            T_depth=r["D_T"], code_distance=ft_b["code_distance"],
            phys_qubits=ft_b["phys_qubits"], n_factories=ft_b["n_factories"],
            q_wall_s_baseline=(qw_solve if lvl=="low" else qw_b*r["n_reruns_readout"]),
            classical_flops_low=fl_lo, classical_flops_high=fl_hi,
            classical_wall_s_low=cwall_lo, classical_wall_s_high=cwall_hi,
            classical_code=CLASSICAL["K2"]["code"], classical_hw=CLASSICAL["K2"]["hardware"],
            classical_flop_rate=CLASSICAL["K2"]["flop_rate"],
            readin_Tcount=r["T_readin"], readout_reruns=r["n_reruns_readout"],
            N_T_solveonly=r["N_T_solveonly"], kappa=r["kappa"], active_space_M=np.nan))
# ---------------- K3 sweep: active space M spin-orbitals = 20..1000 ---------------------------
for M in [20,50,100,150,200,300,500,1000]:
    fl_lo, fl_hi = K.K3_classical_flops(M)
    cwall_lo=fl_lo/CLASSICAL["K3"]["flop_rate"]; cwall_hi=fl_hi/CLASSICAL["K3"]["flop_rate"]
    for lvl,(le,we) in [("low",(K.K3_ASSUME["lambda_exponent_on_M_low"],K.K3_ASSUME["walk_Tcount_exponent_on_M_low"])),
                        ("mid",(1.75,1.5)),
                        ("high",(K.K3_ASSUME["lambda_exponent_on_M_high"],K.K3_ASSUME["walk_Tcount_exponent_on_M_high"]))]:
        r=K.K3_resources(M,le,we)
        ft_b,qw_b=qwall(dict(n_L=r["n_L"],N_T=r["N_T"],D_T=r["D_T"]),"baseline")
        rows.append(dict(kernel="K3", problem_metric="active_space_spin_orbitals_M", problem_size=M,
            range_level=lvl, carleman_order_Kc=np.nan,
            nonlinearity_cost="n/a (linear eigenproblem); active-space reduction IS the limitation (AC-42)",
            dof_classical=M, logical_qubits=r["n_L"], T_count=r["N_T"], T_depth=r["D_T"],
            code_distance=ft_b["code_distance"], phys_qubits=ft_b["phys_qubits"], n_factories=ft_b["n_factories"],
            q_wall_s_baseline=qw_b,
            classical_flops_low=fl_lo, classical_flops_high=fl_hi,
            classical_wall_s_low=cwall_lo, classical_wall_s_high=cwall_hi,
            classical_code=CLASSICAL["K3"]["code"], classical_hw=CLASSICAL["K3"]["hardware"],
            classical_flop_rate=CLASSICAL["K3"]["flop_rate"],
            readin_Tcount=np.nan, readout_reruns=np.nan, N_T_solveonly=np.nan, kappa=np.nan, active_space_M=M))

df=pd.DataFrame(rows)
df.to_csv(os.path.join(HERE,"quantum_resource_estimate.csv"), index=False)
print("rows:", len(df))
# quick crossover scan on wall-clock (quantum baseline scenario vs classical OPTIMIZED = *_low wall)
for k in ["K1","K2","K3"]:
    sub=df[(df.kernel==k)&(df.range_level=="mid")].sort_values("problem_size")
    print(f"\n== {k} (mid) : problem_size | q_wall_s | classical_wall_low(optimized) | q<classical? | n_L | T_count ==")
    for _,x in sub.iterrows():
        cw=x["classical_wall_s_low"]
        cross = x["q_wall_s_baseline"] < cw
        print(f"  {x['problem_size']:>8g} | {x['q_wall_s_baseline']:.2e} | {cw:.2e} | {cross} | nL={x['logical_qubits']:.0f} | T={x['T_count']:.2e}")
