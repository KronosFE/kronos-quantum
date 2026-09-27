"""
Track 7 — FINAL EXPERIMENT F: quantum resource-estimate SENSITIVITY / TORNADO.
Turns the point T-counts and the NO-CROSSOVER-THIS-DECADE verdict into a ROBUST claim by
varying each assumption across a plausible range (one-at-a-time / OAT tornado) around the
nominal interesting instance of each kernel, and by testing the single most quantum-optimistic
corner.  REUSES the SAME derivation functions (ft_cost_model.ft_costs / code_distance and
kernels.K1/K2/K3_resources) — no new model is introduced.

PROVENANCE: RESOURCE-EST.  Assumes fault-tolerant hardware that DOES NOT YET EXIST; not a
measurement.  Kronos has NO operating plant.  Metrics: logical qubits, T-count, earliest
hardware-availability year (from NAMED vendor roadmaps), physical qubits, quantum wall-clock.
Hardware: local 56-core CPU (no GPU) only builds the estimate; the estimated machine is FT quantum.
"""
import numpy as np, pandas as pd, math, os, sys, copy
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from ft_cost_model import ft_costs, code_distance, HW_SCENARIOS, PARAMS
import kernels as K

# ---- NAMED classical baselines (copied verbatim from build_estimates.py) --------------------
CLASSICAL = {
  "K1": dict(code="CGYRO/GENE Eulerian gyrokinetic (Candy-Waltz 2003)", hardware="1 node Perlmutter CPU", flop_rate=2.0e12),
  "K2": dict(code="EFIT-class multigrid Grad-Shafranov (Lao 1985)",     hardware="1 core Xeon",           flop_rate=1.0e10),
  "K3": dict(code="DMRG (Block2) optimized / CCSD(T) naive",            hardware="1 node HPC",            flop_rate=1.0e12),
}
# ---- NAMED public roadmaps (copied verbatim from build_analysis.py; AC-46) -------------------
ROADMAP = [
 dict(org="IBM",   year=2029, logical_qubits=200),
 dict(org="IBM",   year=2033, logical_qubits=2000),
 dict(org="Google",year=2030, logical_qubits=100),
 dict(org="Google",year=2035, logical_qubits=1000),
 dict(org="Quantinuum", year=2030, logical_qubits=100),
]
def earliest_year(nL):
    cands = [r["year"] for r in ROADMAP if r["logical_qubits"] >= nL]
    return min(cands) if cands else 9999   # 9999 == beyond all published roadmaps (>2035)

# ---- FT footprint/wall for arbitrary (p, t_cycle): reuse ft_costs via a temp scenario --------
def ft_custom(n_L, N_T, D_T, p_phys, t_cycle):
    HW_SCENARIOS["_tmp"] = (p_phys, t_cycle)
    ft = ft_costs(n_L, N_T, D_T, "_tmp")
    del HW_SCENARIOS["_tmp"]
    return ft

# =============================================================================================
# NOMINAL POINTS (mid range level, baseline HW p=1e-3 t=1e-6) — the "interesting" instance
# =============================================================================================
NOM = dict(p=1e-3, t_cycle=1e-6)
def k1_metrics(N=64, Kc=3, p=NOM["p"], t=NOM["t_cycle"], A=None, tcost_scale=1.0, alpha_scale=1.0):
    a = copy.deepcopy(K.K1_ASSUME)
    a["Tcount_per_query_prefactor"] *= tcost_scale
    a["alpha_tau_prefactor"] *= alpha_scale
    r = K.K1_resources(N, Kc, A=a)
    ft = ft_custom(r["n_L"], r["N_T"], r["D_T"], p, t)
    qwall = ft["wall_clock_s"]
    cw_lo, cw_hi = K.K1_classical_flops(N); cw_lo/=CLASSICAL["K1"]["flop_rate"]
    return dict(logical_qubits=r["n_L"], T_count=r["N_T"], phys_qubits=ft["phys_qubits"],
                q_wall_s=qwall, crossover_year=earliest_year(r["n_L"]), c_wall_opt_s=cw_lo)
def k2_metrics(Ng=1e4, p=NOM["p"], t=NOM["t_cycle"], kappa_exp=1.0, kappa_pref=1.0, eps=1e-3, tcost_scale=1.0):
    a = copy.deepcopy(K.K2_ASSUME)
    a["kappa_exponent_on_Ng"] = kappa_exp; a["kappa_prefactor"] = kappa_pref
    a["target_error_eps"] = eps; a["Tcount_per_query_prefactor"] *= tcost_scale
    a["readin_Tcount_prefactor"] *= tcost_scale
    r = K.K2_resources(Ng, A=a)
    ft = ft_custom(r["n_L"], r["N_T"], r["D_T"], p, t)   # single-run footprint
    qwall_endtoend = r["n_reruns_readout"] * (r["D_T"] * ft["code_distance"] * t)  # reruns * one-run wall
    cw_lo, cw_hi = K.K2_classical_flops(Ng); cw_lo/=CLASSICAL["K2"]["flop_rate"]
    return dict(logical_qubits=r["n_L"], T_count=r["N_T"], phys_qubits=ft["phys_qubits"],
                q_wall_s=qwall_endtoend, crossover_year=earliest_year(r["n_L"]), c_wall_opt_s=cw_lo)
def k3_metrics(M=100, lam_exp=1.75, walk_exp=1.5, p=NOM["p"], t=NOM["t_cycle"], tcost_scale=1.0):
    a = copy.deepcopy(K.K3_ASSUME); a["walk_Tcount_prefactor"] *= tcost_scale
    r = K.K3_resources(M, lam_exp, walk_exp, A=a)
    ft = ft_custom(r["n_L"], r["N_T"], r["D_T"], p, t)
    cw_lo, cw_hi = K.K3_classical_flops(M); cw_lo/=CLASSICAL["K3"]["flop_rate"]
    return dict(logical_qubits=r["n_L"], T_count=r["N_T"], phys_qubits=ft["phys_qubits"],
                q_wall_s=ft["wall_clock_s"], crossover_year=earliest_year(r["n_L"]), c_wall_opt_s=cw_lo)

# =============================================================================================
# OAT tornado: for each kernel, vary each assumption low<->high holding others at nominal.
# Each entry: (assumption_label, low_value, high_value, fn_low_kwargs, fn_high_kwargs)
# =============================================================================================
METRICS = ["logical_qubits", "T_count", "phys_qubits", "q_wall_s", "crossover_year"]

K1_VARY = [
 ("physical_error_rate_p",        1e-4, 8e-3, dict(p=1e-4), dict(p=8e-3)),
 ("cycle_time_s",                 1e-7, 1e-5, dict(t=1e-7), dict(t=1e-5)),
 ("carleman_order_Kc",            2,    4,    dict(Kc=2),   dict(Kc=4)),
 ("grid_resolution_N",            32,   128,  dict(N=32),   dict(N=128)),
 ("Tgate_cost_per_query_scale",   0.25, 4.0,  dict(tcost_scale=0.25), dict(tcost_scale=4.0)),
 ("blockenc_norm_alpha_tau_scale",0.1,  10.0, dict(alpha_scale=0.1),  dict(alpha_scale=10.0)),
]
K2_VARY = [
 ("physical_error_rate_p",        1e-4, 8e-3, dict(p=1e-4), dict(p=8e-3)),
 ("cycle_time_s",                 1e-7, 1e-5, dict(t=1e-7), dict(t=1e-5)),
 ("grid_unknowns_Ng",             1e3,  1e6,  dict(Ng=1e3), dict(Ng=1e6)),
 ("condition_number_exp_on_Ng",   0.5,  1.5,  dict(kappa_exp=0.5), dict(kappa_exp=1.5)),
 ("readout_target_error_eps",     1e-2, 1e-4, dict(eps=1e-2), dict(eps=1e-4)),
 ("Tgate_cost_per_query_scale",   0.25, 4.0,  dict(tcost_scale=0.25), dict(tcost_scale=4.0)),
]
K3_VARY = [
 ("physical_error_rate_p",        1e-4, 8e-3, dict(p=1e-4), dict(p=8e-3)),
 ("cycle_time_s",                 1e-7, 1e-5, dict(t=1e-7), dict(t=1e-5)),
 ("active_space_M",               50,   200,  dict(M=50),   dict(M=200)),
 ("lambda_1norm_exp_on_M",        1.5,  2.0,  dict(lam_exp=1.5), dict(lam_exp=2.0)),
 ("walk_Tcount_exp_on_M",         1.0,  2.0,  dict(walk_exp=1.0), dict(walk_exp=2.0)),
 ("Tgate_cost_per_query_scale",   0.25, 4.0,  dict(tcost_scale=0.25), dict(tcost_scale=4.0)),
]
FN = {"K1": k1_metrics, "K2": k2_metrics, "K3": k3_metrics}
VARY = {"K1": K1_VARY, "K2": K2_VARY, "K3": K3_VARY}

rows = []
for k in ["K1","K2","K3"]:
    fn = FN[k]
    for label, lo, hi, kw_lo, kw_hi in VARY[k]:
        m_lo = fn(**kw_lo); m_hi = fn(**kw_hi)
        for metric in METRICS:
            rlo, rhi = m_lo[metric], m_hi[metric]
            # swing: for year use absolute year diff; else absolute difference (magnitude)
            if metric == "crossover_year":
                swing = abs(rhi - rlo)
                log_swing = np.nan
            else:
                swing = abs(rhi - rlo)
                lo_p = max(rlo, 1e-300); hi_p = max(rhi, 1e-300)
                log_swing = abs(math.log10(hi_p) - math.log10(lo_p))
            rows.append(dict(kernel=k, assumption_varied=label, low_value=lo, high_value=hi,
                             metric=metric, low_result=rlo, high_result=rhi,
                             swing=swing, log10_swing=log_swing))
sens = pd.DataFrame(rows)
sens.to_csv(os.path.join(HERE, "resource_sensitivity.csv"), index=False)
print("resource_sensitivity.csv rows:", len(sens))

# ---- dominant assumption per kernel per metric (widest bar) ----------------------------------
print("\n== DOMINANT ASSUMPTION (widest tornado bar) per kernel ==")
dom_rows=[]
for k in ["K1","K2","K3"]:
    for metric in ["logical_qubits","T_count","crossover_year","phys_qubits","q_wall_s"]:
        sub = sens[(sens.kernel==k)&(sens.metric==metric)].copy()
        key = "swing" if metric=="crossover_year" else "log10_swing"
        sub = sub.sort_values(key, ascending=False)
        top = sub.iloc[0]
        dom_rows.append(dict(kernel=k, metric=metric, dominant_assumption=top.assumption_varied,
                             top_swing=top[key], second=sub.iloc[1].assumption_varied, second_swing=sub.iloc[1][key]))
        if metric in ("T_count","logical_qubits"):
            print(f"  {k} {metric:16s}: {top.assumption_varied:28s} (log10 swing {top[key]:.2f})  [2nd {sub.iloc[1].assumption_varied} {sub.iloc[1][key]:.2f}]")
dom = pd.DataFrame(dom_rows); dom.to_csv(os.path.join(HERE,"resource_sensitivity_dominant.csv"), index=False)

# =============================================================================================
# MOST OPTIMISTIC CORNER: all assumptions at their most quantum-favourable simultaneously,
# smallest scientifically-interesting size. Does a wall-clock crossover appear even here?
# =============================================================================================
print("\n== MOST OPTIMISTIC CORNER — does NO-CROSSOVER survive? ==")
corner=[]
# K1 optimistic: smallest N in range that is still meaningful (N=32), lowest Kc, cheapest T, low alpha, optimistic HW
c1 = k1_metrics(N=32, Kc=2, p=1e-4, t=1e-7, tcost_scale=0.25, alpha_scale=0.1)
# K2 optimistic: smallest Ng, lowest kappa exp, loosest eps, cheapest T, optimistic HW
c2 = k2_metrics(Ng=1e3, p=1e-4, t=1e-7, kappa_exp=0.5, eps=1e-2, tcost_scale=0.25)
# K3 optimistic: smallest M, lowest lambda & walk exp, cheapest T, optimistic HW
c3 = k3_metrics(M=50, lam_exp=1.5, walk_exp=1.0, p=1e-4, t=1e-7, tcost_scale=0.25)
for k,c,size in [("K1",c1,"N=32"),("K2",c2,"Ng=1e3"),("K3",c3,"M=50")]:
    crosses = c["q_wall_s"] < c["c_wall_opt_s"]
    corner.append(dict(kernel=k, corner_size=size, q_wall_s=c["q_wall_s"], classical_opt_wall_s=c["c_wall_opt_s"],
                       q_over_classical=c["q_wall_s"]/max(c["c_wall_opt_s"],1e-300),
                       logical_qubits=c["logical_qubits"], T_count=c["T_count"],
                       crossover_year=c["crossover_year"], quantum_wins=bool(crosses),
                       verdict=("CROSSOVER APPEARS at optimistic corner" if crosses else "NO CROSSOVER — quantum still loses")))
    print(f"  {k} @optimistic {size}: q_wall={c['q_wall_s']:.2e}s vs classical_opt={c['c_wall_opt_s']:.2e}s "
          f"-> q/c={c['q_wall_s']/max(c['c_wall_opt_s'],1e-300):.2e}  quantum_wins={crosses}")
cor = pd.DataFrame(corner); cor.to_csv(os.path.join(HERE,"crossover_survival_corner.csv"), index=False)
print("\nwrote resource_sensitivity_dominant.csv, crossover_survival_corner.csv")
