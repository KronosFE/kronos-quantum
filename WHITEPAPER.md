# Quantum Computing for Fusion — the Kronos Approach

**A technical white paper accompanying the `kronos-quantum` codes.**
Kronos Fusion Energy. Version 0.1.0.

---

## Abstract

Quantum computing is widely, and correctly, expected to matter for fusion — most of all for the
quantum many-body problems of materials and chemistry that sit at the edge of classical reach. It does
not matter *yet*. The hardware that would give a genuine advantage on a fusion-scale kernel is a
fault-tolerant machine with tens of thousands of physical qubits, which our own order-of-magnitude
estimates place a decade out, on the far side of roughly 2036. This paper takes the honest position
that follows from that timeline: build, run, and benchmark the quantum tooling **now**, on simulators
and on real hardware where it helps, so that the methods, the data pipelines, and the judgment are
ready when the machines arrive — and report the results without inflation, null results included. The
companion repository ships nine runnable quantum programs that do exactly this across five fusion-relevant
areas. None claims a speedup; each is a real, reproducible pipeline. This is a conservative public floor
on the work, not its ceiling: our internal research runs roughly three to four years ahead of what we
have so far written up.

## 1. Why quantum, and why not yet

The case for quantum computing in fusion is specific, not generic. The strongest target is **electronic
structure**: the energetics of candidate first-wall and structural materials under 14 MeV neutron
damage, defect formation and migration, and reaction pathways relevant to the fuel cycle are quantum
many-body problems whose classical cost grows steeply with system size. A fault-tolerant quantum
computer would, in principle, compute selected properties of such systems at a cost that scales far
more gently. Secondary targets — combinatorial design search, certain linear-algebra kernels, and
sampling — are real but weaker, because classical methods there are strong and the quantum overheads
(state preparation, readout, error correction) are punishing.

The reason the advantage is not here is equally specific. Every useful fault-tolerant algorithm assumes
**logical** qubits with error rates far below what physical qubits deliver, produced by quantum error
correction at an overhead of roughly a thousand physical qubits per logical qubit near threshold. A
fusion electronic-structure kernel large enough to beat the best classical method needs on the order of
tens of logical qubits held coherent through deep circuits — which, at that overhead, is tens of
thousands of physical qubits. Today's devices offer roughly 1e2–1e3 physical qubits and no
error-corrected logical qubits at all. The gap is not a tuning problem; it is several hardware
generations.

The `KQROSS` code makes this concrete and reproducible. It combines a surface-code physical-qubit
overhead (distance d=25), qubitization T-counts for the kernel, and a classical exact-diagonalization
baseline, all order-of-magnitude and literature-scaled, to compute a **crossover**: the smallest
problem at which the quantum runtime undercuts the classical one. It lands near N≈50 spin-orbitals,
needing on the order of **6e4 physical qubits**, with a logical-qubit roadmap reaching that count
around 2032 under optimistic scaling — and, accounting for the remaining error-rate, gate-speed, and
state-preparation requirements, a genuinely *useful* fusion role only after roughly **2036**. This is a
validated negative result, and we treat it as load-bearing: it sets the honest expectation for
everything else in the repository.

## 2. What can be tested today

If the advantage is a decade out, the right thing to do now is to make the *tooling* real: write the
circuits, run them on simulators and on hardware, wire them to real fusion data, and measure honestly
what happens — including where quantum buys nothing. The nine codes fall into five areas.

### 2.1 Materials & chemistry (KQUBIT, KMIT, KQROSS)

**KQUBIT** is a real variational quantum eigensolver for a molecular (H₂) Hamiltonian — the near-term,
NISQ-friendly route to quantum chemistry. It parameterizes a trial state with a shallow circuit,
measures the Hamiltonian's expectation, and drives a classical optimizer downhill to the ground state.
On the noiseless simulator it recovers the exact ground-state energy to **0.0002 mHa**, well inside
chemical accuracy. A bundled per-qubit depolarizing sweep then shows the honest catch: modest noise
pushes the recovered energy past chemical accuracy, which is precisely why there is no advantage on
today's hardware.

**KMIT** attacks that catch with the tools NISQ practitioners actually use. It applies **zero-noise
extrapolation** (via global unitary folding — running the logically-identical circuit at increasing
noise scale and extrapolating to zero) and **readout-error mitigation** (inverting a measurement
confusion matrix) to the real KQUBIT circuit. On a depolarizing-noise model, ZNE removes about **89%**
of the noise-induced energy error (44.4 → 5.0 mHa) and the readout correction drives the measurement
distribution's total-variation distance to zero. Mitigation is real and useful today — it recovers
signal from noise — but it is not a speedup, and its overhead grows with the noise it fights.

**KQROSS** (Section 1) frames when the chemistry advantage could actually arrive.

### 2.2 Turbulence & dynamics (KTENSOR, KDYN)

These build on Kronos's real turbulence campaign: a completed 16/16 CGYRO A1e nonlinear
kinetic-electron flux map at representative fidelity (reduced electron mass μ=400), published as Zenodo
DOI 10.5281/zenodo.22136279.

**KTENSOR** applies a tensor-network (MPS-style singular-value) reduced-order model to that flux
database and reports a genuinely useful, and deflationary, result: the flux is **only modestly
compressible** — an effective rank of about 2.93 out of 4; a bond-dimension-2 approximation keeps ~91%
of the variance but incurs ~30% relative-L2 error, because the turbulent↔quiet transition is a sharp,
high-rank feature. This corrects the naive expectation that turbulence flux is trivially low-rank, and
it is a classical method with no quantum-advantage claim — a bridge concept, honestly labeled.

**KDYN** runs real Trotterized time-evolution of a transverse-field Ising "kinetic" Hamiltonian as a
stand-in for plasma-like dynamics. It measures the first-order Trotter error falling from **1.35 to
0.034** as the step count grows from 1 to 32 — the expected ~1/n curve. This is the honest cost of
simulating dynamics on a quantum computer: accuracy is buyable, but only with circuit depth, which
noise limits until fault tolerance arrives.

### 2.3 Diagnostics & disruptions (KQERN, KSENSE)

**KQERN** is a real quantum-kernel classifier. It embeds real MAST disruption features into a quantum
feature map and classifies on the resulting fidelity kernel with a classical support-vector machine. On
591 real MAST shots it reaches an AUC of **0.919**, against **0.929** for a classical RBF kernel — a
tie, and an honest null. The pipeline is entirely real and hardware-ready; the result says plainly that
a quantum kernel buys no advantage here.

**KSENSE** computes quantum Fisher information for GHZ interferometry. Ideal GHZ states give Heisenberg
scaling (metrological gain ~ N), but realistic NV/SQUID/SERF **dephasing collapses the scaling back to
the standard quantum limit** (~√N): over N=2→8 the ideal gain grows 4.0× while the dephased gain grows
only 2.05×, essentially the SQL rate. Another honest null — no quantum-sensing advantage for fusion
diagnostics this decade — from a real, runnable metrology calculation.

### 2.4 Design & control (KQOPT, KLINQ)

**KQOPT** is a real QAOA optimizer that solves a combinatorial design QUBO on an actual quantum circuit;
you can plug in your own QUBO. It reaches **100%** of the brute-force optimum on a 6-qubit design
problem (p=2). At this size there is no speedup versus classical solvers; the value is a working,
hardware-ready quantum optimizer and an honest baseline to grow from.

**KLINQ** is a variational quantum linear solver that prepares the solution of a 4×4 reduced-MHD
(discrete-Laplacian) linear system with a real quantum circuit, recovering the classical solution at
**fidelity 1.0**. It ships with a fault-tolerant HHL resource estimate showing that a fusion-scale
(N~1e6) sparse solve would need on the order of **4e4 physical qubits** — no advantage at real scale,
consistent with the post-~2036 timeline.

## 3. One backend, simulator now and hardware later

Every quantum code builds its circuit once and runs it through a single backend layer. By default that
is a free, exact local statevector simulator that runs on any CPU. Setting `KODEX_QC_BACKEND=aer`
switches to a local shot-noise simulator; setting `KODEX_QC_BACKEND=ibm` with an API token runs the
*same* circuit on real IBM Quantum hardware. There is no separate "hardware version" of the code to
maintain and fall out of date. This is the mechanism that makes "test now, deploy when the hardware
arrives" a real engineering practice rather than a slogan.

## 4. Reproducibility & honesty discipline

The benchmarks are computed live with fixed seeds, on CPU, with no network access, or sourced from a
named on-disk file. Null and negative results are first-class: KQERN's tie, KSENSE's erased advantage,
KTENSOR's corrected low-rank expectation, and KQROSS's and KLINQ's negative crossovers are the point,
not an embarrassment. A quantum program that honestly reports "no advantage here, and here is exactly
why" is more useful to a serious fusion program than an impressive-looking result that does not survive
scrutiny.

## 5. Where this sits relative to our internal research

This repository is a conservative public floor. Our internal research runs roughly **three to four
years ahead** of what we have published — the gap is one of write-up time, not of substance — and we
intend to keep papering and releasing it as we are able. Nothing here should be read as the limit of
what Kronos can do with quantum computing for fusion.

## 6. An honest roadmap

- **Now → ~2030:** simulator-and-NISQ testing of every kernel; mitigation as the practical lever;
  real-data pipelines (as here). No advantage expected or claimed.
- **~2030 → ~2036:** early fault tolerance; small logical qubit counts; first genuinely error-corrected
  chemistry demonstrations at sub-advantage scale.
- **~2036 and beyond:** the plausible onset of a *useful* fusion role, first in materials and
  chemistry, contingent on logical-qubit counts and error rates meeting the resource estimates here.

We will update these estimates as the hardware and our own research advance.

## References

- Kronos quantum paper series 2.90–2.95 (see [papers/PAPERS.md](papers/PAPERS.md)): Quantum Computing;
  Quantum Optimization & QRL; Quantum ML, Sensing & FTQC; Quantum Algorithms & Control; the Burner
  Quantum Stack; ADAPT-VQE & Quantum Chemistry.
- CGYRO nonlinear kinetic-electron turbulence flux data — Zenodo DOI 10.5281/zenodo.22136279.
- The nine codes and their live benchmarks — [CODES.md](CODES.md), [BENCHMARKS.md](BENCHMARKS.md).

*Competing-interests statement: the author declares no competing financial interests.*
