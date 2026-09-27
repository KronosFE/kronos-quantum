#!/usr/bin/env python
"""Run every Kronos Quantum benchmark and regenerate BENCHMARKS.md + benchmarks.json.

Honest numbers only -- each figure is computed live here (fixed seed, CPU, no
network) or sourced from a named on-disk file.  Reproducible.

    PYTHONPATH=. python benchmarks/run_all.py
"""
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import kronos_quantum as Q  # noqa: E402

OUT = Path(__file__).resolve().parent.parent


def main():
    results = {}
    for name in Q.list_codes():
        s = Q.get(name)
        try:
            results[name] = {"card": s.card(), "benchmark": s.benchmark()}
        except Exception as e:  # pragma: no cover
            results[name] = {"card": s.card(), "benchmark": {"error": str(e)}}

    (OUT / "benchmarks" / "benchmarks.json").write_text(
        json.dumps(results, default=str, indent=2))

    lines = ["# Kronos Quantum -- BENCHMARKS", "",
             "Honest numbers only. Each figure is computed live (fixed seed, CPU, no",
             "network) or sourced from a named on-disk file. No quantum *advantage* is",
             "claimed this decade -- a meaningful role in fusion is a post-~2036 prospect;",
             "the tooling is real to test today.", "",
             "| # | Code | What it is | Headline (honest) |", "|--|--|--|--|"]
    for i, n in enumerate(Q.list_codes(), 1):
        c = results[n]["card"]; b = results[n]["benchmark"]
        lines.append(f"| {i:02d} | **{n}** | {c['function']} | {_headline(n, b)} |")
    lines += ["", "_Regenerate: `PYTHONPATH=. python benchmarks/run_all.py`._"]
    (OUT / "BENCHMARKS.md").write_text("\n".join(lines) + "\n")
    print(f"wrote BENCHMARKS.md ({len(results)} codes) + benchmarks.json")


def _headline(name, b):
    if name == "KQUBIT":
        v = b.get("live_vqe", {})
        return (f"**REAL VQE** (PennyLane): recovers H2 ground state to {v.get('recovery_mHa')} mHa on "
                f"{v.get('backend', {}).get('active_backend')}; runs on real QC hardware -- no advantage yet")
    if name == "KQROSS":
        e = b.get("live_resource_estimate", {})
        return (f"**REAL FT resource estimator**: classical<->quantum crossover ~N={e.get('crossover_N_spin_orbitals')} "
                f"needs {e.get('physical_qubits_needed')} physical qubits, roadmap ~{e.get('roadmap_year_reach_logical')} "
                f"-- no FT advantage this decade")
    if name == "KSENSE":
        m = b.get("live_quantum_metrology", {}).get("gain_growth_N2_to_N8", {})
        return (f"**REAL quantum metrology** (GHZ, PennyLane): ideal Heisenberg {m.get('GHZ_ideal')}x vs "
                f"dephased {m.get('GHZ_dephased')}x ~= SQL {m.get('SQL')}x -- dephasing erases the advantage (honest null)")
    if name == "KTENSOR":
        r = b.get("live_low_rank_rom", {}).get("full_16pt_map", {})
        return (f"SVD/MPS ROM of the real CGYRO flux DB: **effective rank ~{r.get('effective_rank')} of 4 -- "
                f"modestly compressible, NOT strongly low-rank** (classical, no quantum-advantage claim)")
    if name == "KQERN":
        q = b.get("live_quantum_kernel", {})
        return (f"**REAL quantum kernel**: MAST-disruption AUC {q.get('quantum_kernel_auc')} vs classical "
                f"{q.get('classical_rbf_auc')} (ties -- honest null); runnable on real QC hardware")
    if name == "KQOPT":
        q = b.get("live_qaoa", {})
        return (f"**REAL QAOA optimizer**: {q.get('approx_ratio')} of optimum on a design QUBO "
                f"({q.get('n_qubits')} qubits); plug in your QUBO, run on real QC hardware -- no speedup yet")
    if name == "KDYN":
        d = b.get("live_trotter", {}); c = d.get("spectral_norm_error_vs_steps", {})
        vals = list(c.values())
        return (f"**REAL Trotter quantum dynamics**: 1st-order error {vals[0] if vals else '?'}->{vals[-1] if vals else '?'} "
                f"over steps (~1/n); runs on real QC hardware -- honest cost curve, no advantage yet")
    if name == "KMIT":
        m = b.get("live_error_mitigation", {}); z = m.get("zne", {}); ro = m.get("readout_mitigation", {})
        return (f"**REAL error mitigation**: ZNE cuts H2 energy error {z.get('error_noisy_mHa')}->"
                f"{z.get('error_zne_mHa')} mHa ({z.get('error_reduction_frac')} removed); readout TV "
                f"{ro.get('tv_distance_noisy')}->{ro.get('tv_distance_mitigated')} -- real NISQ tool today, role post-~2036")
    if name == "KLINQ":
        q = b.get("live_quantum_linear_solver", {}); hhl = q.get("ft_hhl_resource_estimate", {})
        return (f"**REAL quantum linear solver** (VQLS): 4x4 reduced-MHD solve fidelity "
                f"{q.get('solution_fidelity_vs_classical')} vs classical (rel-resid {q.get('residual_rel')}); "
                f"FT-HHL {hhl.get('physical_qubits_needed')} phys qubits -- no advantage, role post-~2036")
    return b.get("note", b.get("headline", "quantum code"))


if __name__ == "__main__":
    sys.exit(main())
