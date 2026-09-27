"""
Track 7 — ONE fault-tolerant cost model, used for all three kernels K1/K2/K3.
Surface-code + magic-state-factory resource model. Every assumption is a CSV column
(ft_cost_model_params.csv); no number is narrated.

Published relations used (all citations resolved in resolved_citations.csv / track7_citations.csv):
 - Surface-code logical error suppression + physical-qubit-per-logical:
     Fowler, Mariantoni, Martinis & Cleland, Phys. Rev. A 86, 032324 (2012)  doi:10.1103/PhysRevA.86.032324
 - Magic-state distillation / factory footprint + reaction-limited runtime, whole-algorithm accounting:
     Gidney & Ekera, Quantum 5, 433 (2021)                                   doi:10.22331/q-2021-04-15-433
     Beverland et al., "Assessing requirements to scale to practical quantum advantage" (2022) arXiv:2211.07629
 - Resource-estimation methodology (T-count -> runtime/footprint):
     Sanders et al., PRX Quantum 1, 020312 (2020)                            doi:10.1103/PRXQuantum.1.020312

Convention: PROVENANCE = RESOURCE-EST. Assumes fault-tolerant hardware that does not yet exist.
NO Kronos operating-plant data exists; nothing here is a measurement.
"""
import numpy as np, pandas as pd, math, os

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------
# FIXED ASSUMPTIONS (each becomes a CSV column). Three hardware scenarios.
# ----------------------------------------------------------------------------
PARAMS = {
    # surface-code / hardware
    "p_th_surface_code":      1.0e-2,   # surface-code threshold (Fowler 2012)
    "A_logical_prefactor":    0.10,     # p_L = A (p/p_th)^((d+1)/2)  (Fowler 2012)
    "c_area_qubits_per_logical": 2.0,   # physical data+routing qubits per logical patch ~ 2 d^2
    "c_area_factory":         15.0,     # physical qubits per magic-state factory ~ c_fac d^2 (Litinski/Gidney-scale)
    "target_total_fail_prob": 1.0e-2,   # whole-algorithm allowed logical failure probability
    "T_per_toffoli":          4.0,      # T-gates per Toffoli (standard 4T Toffoli)
}

# hardware scenarios: (physical error rate, surface-code cycle time)
HW_SCENARIOS = {
    # name        p_phys   t_cycle[s]   note
    "optimistic": (1.0e-4, 1.0e-7),   # aggressive SC clock 100 ns, deep-sub-threshold error
    "baseline":   (1.0e-3, 1.0e-6),   # 1 us SC cycle, 1e-3 gate error (near-term FT target)
    "pessimistic":(3.0e-3, 1.0e-6),   # near threshold -> huge distance blow-up
}

def code_distance(p_phys, n_logical, algo_cycles, p_th=PARAMS["p_th_surface_code"],
                  A=PARAMS["A_logical_prefactor"], p_fail=PARAMS["target_total_fail_prob"]):
    """Smallest odd distance d s.t. total logical error over the whole computation < p_fail.
    Total logical error ~ n_logical * algo_cycles * p_L(d), p_L(d)=A (p/p_th)^((d+1)/2).
    """
    if p_phys >= p_th:
        return math.inf
    budget_per_cycle_per_qubit = p_fail / max(n_logical * algo_cycles, 1.0)
    ratio = p_phys / p_th
    d = 3
    while d < 1001:
        pL = A * ratio ** ((d + 1) / 2.0)
        if pL < budget_per_cycle_per_qubit:
            return d
        d += 2
    return math.inf  # cannot suppress within d<=1001

def ft_costs(n_logical_algorithm, T_count, T_depth, scenario):
    """Map an algorithm's (logical qubits, T-count, T-depth) to a full FT footprint + wall-clock.
    algo_cycles ~ T_depth surface-code *logical cycles*; each logical cycle = d surface-code cycles.
    Reaction-limited runtime (best case for quantum): wall = T_depth * d * t_cycle,
    with enough factories (n_fac = ceil(T_count / T_depth)) to feed one T per logical cycle.
    """
    p_phys, t_cycle = HW_SCENARIOS[scenario]
    d = code_distance(p_phys, n_logical_algorithm, max(T_depth, 1))
    if not math.isfinite(d):
        return dict(scenario=scenario, p_phys=p_phys, t_cycle_s=t_cycle, code_distance=np.inf,
                    phys_qubits=np.inf, n_factories=np.inf, wall_clock_s=np.inf)
    data_qubits = PARAMS["c_area_qubits_per_logical"] * d**2 * n_logical_algorithm
    n_fac = max(1, math.ceil(T_count / max(T_depth, 1)))
    factory_qubits = PARAMS["c_area_factory"] * d**2 * n_fac
    phys_qubits = data_qubits + factory_qubits
    wall_clock = T_depth * d * t_cycle          # reaction-limited (optimistic for quantum)
    return dict(scenario=scenario, p_phys=p_phys, t_cycle_s=t_cycle, code_distance=int(d),
                data_qubits=data_qubits, factory_qubits=factory_qubits, n_factories=n_fac,
                phys_qubits=phys_qubits, wall_clock_s=wall_clock)

def write_params_csv():
    rows = []
    for k,v in PARAMS.items():
        rows.append(dict(param=k, value=v, kind="fixed",
                         source="Fowler2012 / Gidney-Ekera2021 / Beverland2022 / Sanders2020"))
    for name,(p,t) in HW_SCENARIOS.items():
        rows.append(dict(param=f"p_phys[{name}]", value=p, kind="hw_scenario",
                         source="near-term FT target band (Beverland2022; Google/IBM roadmaps)"))
        rows.append(dict(param=f"t_cycle_s[{name}]", value=t, kind="hw_scenario",
                         source="superconducting surface-code cycle 0.1-1 us"))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE,"ft_cost_model_params.csv"), index=False)
    return df

if __name__ == "__main__":
    df = write_params_csv()
    print(df.to_string(index=False))
    # sanity: a mid problem
    print("\n-- sanity ft_costs (n_log=100, T=1e9, Tdepth=1e6) --")
    for s in HW_SCENARIOS:
        print(s, ft_costs(100, 1e9, 1e6, s))
