# Kronos Quantum -- BENCHMARKS

Honest numbers only. Each figure is computed live (fixed seed, CPU, no
network) or sourced from a named on-disk file. No quantum *advantage* is
claimed this decade -- a meaningful role in fusion is a post-~2036 prospect;
the tooling is real to test today.

| # | Code | What it is | Headline (honest) |
|--|--|--|--|
| 01 | **KDYN** | QDYN | **REAL Trotter quantum dynamics**: 1st-order error 1.34637->0.03381 over steps (~1/n); runs on real QC hardware -- honest cost curve, no advantage yet |
| 02 | **KLINQ** | QLINSOLVE | **REAL quantum linear solver** (VQLS): 4x4 reduced-MHD solve fidelity 1.0 vs classical (rel-resid 0.0); FT-HHL ~4e+04 phys qubits -- no advantage, role post-~2036 |
| 03 | **KMIT** | QMITIGATION | **REAL error mitigation**: ZNE cuts H2 energy error 44.38->5.029 mHa (0.887 removed); readout TV 0.1472->0.0 -- real NISQ tool today, role post-~2036 |
| 04 | **KQERN** | QKERNEL | **REAL quantum kernel**: MAST-disruption AUC 0.919 vs classical 0.929 (ties -- honest null); runnable on real QC hardware |
| 05 | **KQOPT** | QOPT | **REAL QAOA optimizer**: 1.0 of optimum on a design QUBO (6 qubits); plug in your QUBO, run on real QC hardware -- no speedup yet |
| 06 | **KQROSS** | QRE | **REAL FT resource estimator**: classical<->quantum crossover ~N=50 needs ~6e+04 physical qubits, roadmap ~2032 -- no FT advantage this decade |
| 07 | **KQUBIT** | QML | **REAL VQE** (PennyLane): recovers H2 ground state to 0.0002 mHa on default; runs on real QC hardware -- no advantage yet |
| 08 | **KSENSE** | QSENSE | **REAL quantum metrology** (GHZ, PennyLane): ideal Heisenberg 4.0x vs dephased 2.05x ~= SQL 2.01x -- dephasing erases the advantage (honest null) |
| 09 | **KTENSOR** | TN | SVD/MPS ROM of the real CGYRO flux DB: **effective rank ~2.93 of 4 -- modestly compressible, NOT strongly low-rank** (classical, no quantum-advantage claim) |

_Regenerate: `PYTHONPATH=. python benchmarks/run_all.py`._
