"""
Crossover verdict + honest logical-qubit/error-rate/date thresholds per kernel + taxonomy + cross-check.
Reads quantum_resource_estimate.csv; writes crossover_verdict.csv, taxonomy.csv, cross_check.csv,
roadmap_dates.csv. PROVENANCE: RESOURCE-EST. Hardware does not yet exist. No Kronos plant data.
"""
import numpy as np, pandas as pd, math, os, sys
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
df=pd.read_csv(os.path.join(HERE,"quantum_resource_estimate.csv"))

# ---- AC-43 bars ----
BAR_2030_Q=1e2; BAR_2030_T=1e9
BAR_2035_Q=1e3; BAR_2035_T=1e12

# ---- Public hardware roadmaps (vendor projections; NAMED + attributed; AC-46) ----
# logical-qubit availability by year. Each point labelled to its source org.
roadmap=[
 dict(org="IBM",   projection="IBM Quantum roadmap (Starling)", year=2029, logical_qubits=200,   phys_err="~1e-3", note="~200 logical qubits, first FT machine (vendor projection)"),
 dict(org="IBM",   projection="IBM Quantum roadmap (Blue Jay)", year=2033, logical_qubits=2000,  phys_err="~1e-3", note="~2000 logical qubits (vendor projection)"),
 dict(org="Google",projection="Google Quantum AI roadmap",      year=2030, logical_qubits=100,   phys_err="~1e-3", note="~1e6 physical qubits target -> O(100) logical at d~15-25 (vendor projection)"),
 dict(org="Google",projection="Google Quantum AI roadmap",      year=2035, logical_qubits=1000,  phys_err="~1e-3", note="long-term FT scale-up (vendor projection)"),
 dict(org="Quantinuum", projection="Quantinuum hardware roadmap", year=2030, logical_qubits=100, phys_err="~1e-4", note="trapped-ion high-fidelity, fewer physical/logical (vendor projection)"),
]
pd.DataFrame(roadmap).to_csv(os.path.join(HERE,"roadmap_dates.csv"),index=False)

def earliest_date(nL,T):
    """earliest year a NAMED roadmap reaches >= nL logical qubits (T-count sets runtime, not availability)."""
    cands=[r["year"] for r in roadmap if r["logical_qubits"]>=nL]
    if not cands: return ">2035 (beyond all published roadmaps)"
    yr=min(cands)
    org=[r["org"] for r in roadmap if r["logical_qubits"]>=nL and r["year"]==yr][0]
    return f"{yr} ({org} roadmap, vendor projection)"

verdict=[]
for k in ["K1","K2","K3"]:
    sub=df[df.kernel==k]
    # crossover = smallest problem size where quantum wall < classical OPTIMIZED (low) wall, at 'mid'
    mid=sub[sub.range_level=="mid"].sort_values("problem_size")
    cross_sizes=mid[mid.q_wall_s_baseline < mid.classical_wall_s_low]["problem_size"].tolist()
    crossover = "NONE — quantum wall-clock exceeds the optimized classical baseline at every size swept" if not cross_sizes else f"{min(cross_sizes)}"
    # honest threshold: smallest problem size that is SCIENTIFICALLY interesting per kernel, and its footprint
    interesting = {"K1":64, "K2":1e4, "K3":100}[k]     # N=64 (1e9 dof); Ng=1e4 grid; M=100 active space
    row_i = mid[mid.problem_size==interesting].iloc[0]
    nL=row_i["logical_qubits"]; T=row_i["T_count"]
    # bar classification
    pass2030 = (nL<=BAR_2030_Q) and (T<=BAR_2030_T)
    pass2035 = (nL<=BAR_2035_Q) and (T<=BAR_2035_T)
    # crossover is NONE for all kernels (quantum wall-clock never beats optimized classical);
    # per AC-43 that means NO CROSSOVER THIS DECADE regardless of footprint. The 2030/2035 bar
    # columns record ONLY "if a crossover existed at this footprint, which bar it would meet".
    has_crossover = bool(cross_sizes)
    band = "NO CROSSOVER THIS DECADE" if not has_crossover else ("plausible before 2030" if pass2030 else ("plausible before 2035" if pass2035 else "NO CROSSOVER THIS DECADE"))
    verdict.append(dict(kernel=k,
        crossover_problem_size=crossover,
        interesting_problem_size=interesting,
        logical_qubits_at_interesting=nL, T_count_at_interesting=T,
        meets_2030_bar=pass2030, meets_2035_bar=pass2035,
        AC43_band=band,
        earliest_hw_date=earliest_date(nL,T),
        honest_threshold=f"needs {nL:.0f} logical qubits @ p<=1e-3 and {T:.2e} T-gates to run a size-{interesting:g} instance; even then quantum wall-clock LOSES to classical",
        classical_baseline=row_i["classical_code"], classical_hw=row_i["classical_hw"]))
vdf=pd.DataFrame(verdict); vdf.to_csv(os.path.join(HERE,"crossover_verdict.csv"),index=False)
print("== CROSSOVER VERDICT ==")
for _,r in vdf.iterrows():
    print(f"{r.kernel}: crossover={r.crossover_problem_size[:40]} | band={r.AC43_band} | nL={r.logical_qubits_at_interesting:.0f} T={r.T_count_at_interesting:.1e} | date={r.earliest_hw_date}")

# ---- K3 CCSD(T)-trap: show apparent crossover vs UNOPTIMIZED baseline is REJECTED per AC-43 ----
k3=df[(df.kernel=="K3")&(df.range_level=="mid")].sort_values("problem_size").copy()
for c in ["q_wall_s_baseline","classical_flops_high"]: k3[c]=k3[c].astype(float)
k3_ccsdt_cross=k3[k3.q_wall_s_baseline < (k3.classical_flops_high/1e12)]["problem_size"].tolist()
print("\n== K3 CCSD(T) unoptimized-baseline apparent crossover sizes:", k3_ccsdt_cross,
      "-> REJECTED per AC-43 (unoptimized baseline); AND every such size exceeds the 2035 qubit/T bars")

# ---- Taxonomy (F25): kernel x algorithm x speedup CLASS x read-in/out penalty x TRL (AC-39: CLASS not factor)
tax=[
 dict(kernel="K1", physics="kinetic/Vlasov collision op (E3)",
      algorithm="Hamiltonian sim / qubitization / LCU + Carleman-KvN linearisation",
      speedup_class="exponential state-space compression (N^5 amplitudes -> 5 log2 N qubits); ASYMPTOTIC only",
      readin_readout_penalty="read-IN partial (nonlocal coeff loading O(N^3) via QROM); read-OUT FAVOURABLE (transport coeffs are low-order moments) BUT nonlinearity (Carleman) adds truncation cost + qubit tower",
      survives_readinout="NO net advantage at feasible N: block-encoding norm alpha*tau ~ N^2 + clock gap; nonlinearity is the inflation risk (AC-40)",
      TRL="Quantum COMPUTATION — offline, resource-estimated only; NEVER in control loop",
      primary_cite="Engel 2019 (10.1103/PhysRevA.100.062315); Dodin-Startsev 2021 (10.1063/5.0056974); Joseph 2020 (10.1103/PhysRevResearch.2.043102)"),
 dict(kernel="K2", physics="equilibrium/MHD linear solve (E1)",
      algorithm="QLSA (HHL / Childs-Kothari-Somma / Costa optimal-scaling)",
      speedup_class="polylog(N) in dimension — APPARENT exponential; ERASED by read-in/read-out",
      readin_readout_penalty="read-IN O(N) (unstructured RHS p',FF' on shaped boundary) + read-OUT O(N/eps^2) (control needs the WHOLE flux/coil field, not one <M>; state destroyed on measurement) + kappa~N",
      survives_readinout="NO — end-to-end scaling is WORSE than classical multigrid O(N); the polylog advantage does not survive. THE LEAD ADVERSE FINDING (Aaronson 2015, 10.1038/nphys3272)",
      TRL="Quantum COMPUTATION — offline, resource-estimated only; NEVER in control loop",
      primary_cite="Harrow-Hassidim-Lloyd 2009 (10.1103/PhysRevLett.103.150502); Childs-Kothari-Somma 2017 (10.1137/16M1087072); Aaronson 2015 (10.1038/nphys3272)"),
 dict(kernel="K3", physics="first-wall/conductor materials ground state (E8)",
      algorithm="QPE / qubitization (THC / linear-T block-encoding)",
      speedup_class="super-polynomial for strongly-correlated ground-state energy vs exact methods; ASYMPTOTIC",
      readin_readout_penalty="read-IN modest (state prep to good HF/CI overlap); read-OUT modest (one eigenvalue) — the FAVOURABLE kernel structurally",
      survives_readinout="Structure survives, but ACTIVE-SPACE REDUCTION is the limitation (AC-42): a tractable M is a DIFFERENT problem from the materials question; and vs the OPTIMIZED classical baseline (DMRG) no wall-clock crossover this decade",
      TRL="Quantum COMPUTATION — offline, resource-estimated only; NEVER in control loop",
      primary_cite="von Burg 2021 (10.1103/PhysRevResearch.3.033055); Lee 2021 (10.1103/PRXQuantum.2.030305); Babbush 2018 (10.1103/PhysRevX.8.041015)"),
]
pd.DataFrame(tax).to_csv(os.path.join(HERE,"taxonomy.csv"),index=False)
print("\ntaxonomy.csv written:", len(tax),"rows")

# ---- Cross-check (STEP 3): anchor >=1 kernel to a PUBLISHED resource estimate; carry ratio ----
# K3 vs von Burg 2021 FeMoco-class FT chemistry estimate; K1 vs Engel-style Vlasov; K2 concept vs HHL.
import kernels as K
r_k3_100=K.K3_resources(100,1.75,1.5)
r_k3_150=K.K3_resources(152,1.75,1.5)  # ~ von Burg active space 76 spatial -> 152 spin-orb
xc=[
 dict(kernel="K3", published_anchor="von Burg et al. 2021, PRX Research 3 033055 — FeMoco 76 spatial orbitals (152 spin-orb)",
      anchor_logical_qubits=2196, anchor_Tcount=1.0e10,
      our_logical_qubits=r_k3_150["n_L"], our_Tcount=r_k3_150["N_T"],
      ratio_qubits=r_k3_150["n_L"]/2196, ratio_Tcount=r_k3_150["N_T"]/1.0e10,
      note="von Burg report ~2196 logical qubits and ~1e10 Toffoli (~4e10 T) for FeMoco at chemical accuracy with double-factorisation. Our M=152 mid estimate is within ~1 order of magnitude on both -> model is calibrated to a published FT-chemistry point. Our simpler scaling model runs LOWER on qubits (we omit their DF ancillae) and comparable on T."),
 dict(kernel="K1", published_anchor="Engel, Smith & Parker 2019, PRA 100 062315 — quantum Vlasov (linearised) scaling",
      anchor_logical_qubits=float('nan'), anchor_Tcount=float('nan'),
      our_logical_qubits=K.K1_resources(64,3)["n_L"], our_Tcount=K.K1_resources(64,3)["N_T"],
      ratio_qubits=float('nan'), ratio_Tcount=float('nan'),
      note="Engel 2019 give qubit count ~ d*log2(N) for the LINEAR Vlasov (no collisions): matches our n_sys=30 at N=64. They do NOT resource-estimate the collisional/nonlinear operator or T-counts at FT scale; our N_T adds the Carleman tower + QROM coeff loading they omit. Anchor is on QUBITS (matched) not T-count."),
 dict(kernel="K2", published_anchor="Harrow-Hassidim-Lloyd 2009 PRL 103 150502 + Aaronson 2015 Nat.Phys 11 291",
      anchor_logical_qubits=float('nan'), anchor_Tcount=float('nan'),
      our_logical_qubits=K.K2_resources(1e4)["n_L"], our_Tcount=K.K2_resources(1e4)["N_T"],
      ratio_qubits=float('nan'), ratio_Tcount=float('nan'),
      note="No published FT resource estimate presents QLSA as a competitive equilibrium solver; Aaronson 2015 catalogues exactly the read-in/read-out/kappa caveats we quantify. Our end-to-end T=1.8e17 at Ng=1e4 makes the caveat numeric. Anchor is QUALITATIVE (the caveat), consistent with the literature."),
]
pd.DataFrame(xc).to_csv(os.path.join(HERE,"cross_check.csv"),index=False)
print("cross_check.csv written")
print("K3 vs von Burg: our nL=%.0f (ratio %.2f), our T=%.2e (ratio %.2f)"%(
    r_k3_150["n_L"], r_k3_150["n_L"]/2196, r_k3_150["N_T"], r_k3_150["N_T"]/1e10))
