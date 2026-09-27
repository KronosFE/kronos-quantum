# Kronos Quantum — the nine codes

One section per code: what it is, what it computes, the honest result, and the real code or
hardware it stands in for. Every code runs on the free local simulator now and on real quantum
hardware via `KODEX_QC_BACKEND=ibm` (+ token) — the same code path. Full benchmarks in
[BENCHMARKS.md](BENCHMARKS.md).

**The honest line, on every card:** no quantum *advantage* for fusion is claimed this decade. A
meaningful role in fusion is a **post-~2036** prospect. What is real and runnable **today** is the
tooling and the testing.

---

## KQUBIT — variational quantum eigensolver (VQE)
**REAL VQE** (PennyLane) for a molecular (H₂) Hamiltonian — the near-term route to quantum chemistry,
relevant to fusion materials and reaction energetics. Optimizes a parameterized circuit to the ground
state and recovers it to **0.0002 mHa** on the noiseless simulator; a bundled depolarizing-noise sweep
shows how NISQ noise breaks chemical accuracy (why there is no advantage yet). Runs on real hardware
with one env var.
*stands in for: fault-tolerant quantum hardware (not available this decade).*

## KQROSS — fault-tolerant resource estimator
**REAL FT resource estimate** — computes the classical↔quantum crossover N, the surface-code
physical-qubit overhead, and the logical-qubit roadmap year for a fusion electronic-structure kernel
(order-of-magnitude, literature-scaled). Crossover ~N=50 → **~6e4 physical qubits**, roadmap ~2032;
today's hardware is ~1e2–1e3 physical qubits with no error-corrected logical qubits. A **validated
negative result**: no FT advantage this decade.
*stands in for: fault-tolerant quantum hardware (not available this decade).*

## KSENSE — quantum metrology (quantum Fisher information)
**REAL quantum-metrology** (PennyLane mixed-state GHZ) — ideal GHZ interferometry gives Heisenberg
scaling (gain ~ N), but realistic NV/SQUID/SERF **dephasing collapses it back to the standard quantum
limit** (~√N). Over N=2→8 the ideal gain grows 4.0× versus 2.05× dephased ≈ the SQL rate. An **honest
null**: no quantum-sensing advantage for fusion diagnostics this decade.
*stands in for: deployed physical diagnostic hardware.*

## KTENSOR — tensor-network / low-rank ROM
Tensor-network (MPS-style SVD) reduced-order model of the **real CGYRO A1e flux database**. Honest
measured result: the flux is only *modestly* compressible — **effective rank ~2.93 of 4**; a bond-dim-2
MPS keeps ~91% of the variance but ~30% rel-L2 error, and the turbulent↔quiet transition is a sharp,
high-rank feature. A genuine ROM characterization that *corrects* the naive "flux is trivially
low-rank" expectation. Classical SVD/MPS — no quantum-advantage claim.
*stands in for: exact many-body / quantum simulation.*

## KQERN — quantum kernel classifier
**REAL quantum kernel** (PennyLane) — embeds real MAST disruption features into a quantum feature map
and classifies on the fidelity kernel with a classical SVM. MAST-disruption AUC **0.919** vs classical
RBF 0.929 (a tie — a validated null), on real fusion data. A real, runnable quantum-ML pipeline;
hardware-pluggable.
*stands in for: fault-tolerant quantum hardware (not available this decade).*

## KQOPT — QAOA optimizer
**REAL QAOA optimizer** (PennyLane) — solves a combinatorial design QUBO on a real quantum circuit;
plug in your own QUBO. Reaches **100% of the brute-force optimum** on a 6-qubit design QUBO (p=2). No
speedup vs classical at this size; advantage is a post-~2036 prospect.
*stands in for: fault-tolerant quantum hardware (not available this decade).*

## KDYN — Trotterized quantum dynamics
**REAL quantum dynamics** (PennyLane) — Trotterized time-evolution of a transverse-field Ising
"kinetic" Hamiltonian, a stand-in for plasma-like dynamics. First-order Trotter error falls
**1.35→0.034** over 1→32 steps (~1/n) — the honest cost curve for simulating dynamics on a quantum
computer. Accuracy is buyable, but only with circuit depth, which noisy hardware limits until fault
tolerance arrives.
*stands in for: fault-tolerant quantum hardware (not available this decade).*

## KMIT — quantum error mitigation
**REAL error mitigation** — zero-noise extrapolation (ZNE, global unitary folding) + inverse-confusion
readout-error mitigation applied to the real KQUBIT H₂ VQE circuit. ZNE removes **~89%** of the
noise-induced energy error (44.4 → 5.0 mHa); readout mitigation cuts the measurement total-variation
distance to ~0. Mitigation is the genuine NISQ tool practitioners run **today** — it recovers signal
from noise; it is not a speedup.
*stands in for: fault-tolerant quantum hardware (not available this decade).*

## KLINQ — variational quantum linear solver
**REAL quantum linear solver** — a variational quantum linear solver (VQLS) prepares the solution of a
4×4 reduced-MHD (discrete-Laplacian) linear system with a real quantum circuit, recovering the
classical solution at **fidelity 1.0**. Bundled with an honest fault-tolerant HHL resource estimate:
a fusion-scale (N~1e6) solve would need ~4e4 physical qubits — no advantage at real scale; a
meaningful role is a post-~2036 prospect.
*stands in for: fault-tolerant quantum hardware (not available this decade).*

---

### How each ties to Kronos fusion work
- **Materials & chemistry** (KQUBIT, KMIT, KQROSS): first-wall/structural materials and reaction
  energetics are quantum many-body problems — the strongest fusion-relevant target for quantum, once
  fault tolerance exists.
- **Turbulence & reduced models** (KTENSOR, KDYN): built on the real CGYRO A1e turbulence campaign
  (Zenodo DOI 10.5281/zenodo.22136279).
- **Diagnostics & disruptions** (KQERN, KSENSE): tested on real MAST disruption data and realistic
  sensor-dephasing models — and honest that quantum buys no advantage there this decade.
- **Design & control** (KQOPT, KLINQ): combinatorial design search and linear solves that appear across
  the plant, framed with honest resource estimates.
