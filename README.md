# Kronos Quantum

**Honest, runnable quantum computing for fusion.** Nine real quantum programs that execute on a free
local simulator today, and on real quantum hardware the moment you plug in an account — the same code,
one environment variable. Built and benchmarked by [Kronos Fusion Energy](https://www.kronosfusionenergy.com),
a family-owned American fusion company.

> **The honest headline.** A quantum *advantage* for fusion is not here yet. Fault-tolerant hardware at
> the scale a fusion kernel needs is a **post-~2036** prospect — our own resource estimates put a
> useful electronic-structure crossover at tens of thousands of physical qubits, against the roughly
> 1e2–1e3 physical qubits (and zero error-corrected logical qubits) hardware has today. **What is real
> and runnable now is the tooling and the testing.** This repository is where we do that testing in the
> open: real circuits, real fusion data, real numbers — including the null results.

## What's here

- **`kronos_quantum/`** — nine runnable quantum codes (see [CODES.md](CODES.md)):
  VQE, a fault-tolerant resource estimator, quantum metrology, a tensor-network ROM, a quantum kernel
  classifier, QAOA, Trotterized dynamics, error mitigation, and a variational quantum linear solver.
- **`data/`** — the runnable data subset (a completed CGYRO turbulence flux map and real MAST
  disruption features) plus pointers to the full published datasets.
- **`WHITEPAPER.md`** — the technical white paper: the honest quantum-for-fusion thesis, the method
  behind each code, the results, and where each ties to the machine.
- **`papers/PAPERS.md`** — the peer-reviewable Kronos quantum paper series (2.90–2.95) that these codes
  accompany.
- **`research/`** — the deeper research tracks the polished codes were distilled from.
- **`benchmarks/`**, **`tests/`** — reproducible, honest benchmarks and a green test suite.

## Where the published work sits relative to our actual research

Everything shared here is a **public snapshot**. Our internal research runs roughly **three to four
years ahead** of what we have published — not because the later work is secret, but because writing it
all up rigorously takes time we have not yet spent. We intend to keep papering and releasing it as we
can. Read this repository as a faithful, conservative floor on what Kronos can do with quantum
computing for fusion, not the ceiling.

## Quickstart

```bash
pip install -e .            # numpy, scipy, scikit-learn, pandas, pennylane (free local simulator)
PYTHONPATH=. python -c "
import kronos_quantum as Q
print(Q.list_codes())                       # the nine codes
p = Q.run('KQUBIT')                          # VQE on the local simulator
print(p.note)                                # recovers H2 ground state to ~0.0002 mHa
"
```

Regenerate the honest benchmark table and run the tests:

```bash
PYTHONPATH=. python benchmarks/run_all.py    # writes BENCHMARKS.md (9 codes)
PYTHONPATH=. python -m pytest tests/ -q       # 8 passed
```

Registry-by-design: you always go through `Q.get(name)` / `Q.run(name, x)`; `from kronos_quantum import
KQUBIT` fails on purpose. Every code returns a `Prediction(y, uncertainty, in_domain)` and exposes an
honest `card()` and `benchmark()`.

## Run it on real quantum hardware

The default backend is a free, exact local simulator. The *same* circuits run on real hardware or a
shot-based simulator by setting one environment variable — no code change:

```bash
export KODEX_QC_BACKEND=ibm            # or 'aer' for local shot noise
export KODEX_QC_TOKEN=<your IBM Quantum API token>
PYTHONPATH=. python -c "import kronos_quantum as Q; print(Q.run('KQOPT').note)"
```

See [docs/RUN_ON_HARDWARE.md](docs/RUN_ON_HARDWARE.md). Install the extra with `pip install -e '.[hardware]'`.

## The nine codes at a glance

| Code | What it is | Honest result |
|---|---|---|
| **KQUBIT** | VQE (quantum chemistry) | recovers H₂ ground state to 0.0002 mHa; NISQ noise breaks it |
| **KQROSS** | FT resource estimator | crossover ~N=50 → ~6e4 physical qubits, roadmap ~2032 |
| **KSENSE** | quantum metrology | dephasing erases Heisenberg scaling back to the SQL (null) |
| **KTENSOR** | tensor-network ROM | CGYRO flux is only modestly compressible (rank ~2.93/4) |
| **KQERN** | quantum kernel | MAST disruption AUC 0.919 vs classical 0.929 (tie) |
| **KQOPT** | QAOA | 100% of a 6-qubit design QUBO optimum; no speedup at this size |
| **KDYN** | Trotter dynamics | 1st-order error 1.35→0.034 over steps (~1/n) |
| **KMIT** | error mitigation | ZNE removes ~89% of the noise energy error |
| **KLINQ** | quantum linear solver | 4×4 reduced-MHD solve at fidelity 1.0; FT-HHL ~4e4 qubits |

Full detail in [CODES.md](CODES.md); numbers in [BENCHMARKS.md](BENCHMARKS.md).

## Data

Two small real datasets run everything here (the circuit codes build their own problems):

- **`data/cgyro_a1e_flux_map.csv`** — the completed 16/16 CGYRO A1e nonlinear kinetic-electron
  turbulence flux map (representative fidelity, reduced electron mass μ=400). Full campaign:
  **Zenodo DOI [10.5281/zenodo.22136279](https://doi.org/10.5281/zenodo.22136279)**.
- **`data/mast_disruption_features.csv`** — physics features for 591 real MAST shots (FAIR-MAST), a
  fixed 50 ms pre-event window; labels derived from the Ip current-quench (heuristic).

See [data/README.md](data/README.md).

## Honesty discipline

- Real benchmarks on real held-out data; **null and negative results are kept, not hidden** (KQERN
  ties classical, KSENSE erases its own advantage, KTENSOR corrects the low-rank expectation).
- **No quantum-advantage claim this decade**, on every card — a meaningful fusion role is post-~2036.
- CPU-only, fixed seeds, no network in the benchmarks.

## License & citation

Apache-2.0 (see [LICENSE](LICENSE)). Please cite via [CITATION.cff](CITATION.cff).

---

*Kronos Fusion Energy. Quantum computing will matter for fusion; we are honest that its hardware role is
still roughly a decade out, and we are doing the real testing today so we are ready when it arrives.*
