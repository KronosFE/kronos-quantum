# ADVERSE — Track R3-3 (tensor-network vs classical)

Adverse cases kept both ways. Nothing tuned to the pre-registered bar. The honesty rails below are the
point of the lever, not a caveat appended to a win.

## 1. Classical BEATS tensor-network — the small-system regime (KEPT, in the CSV)
For small phase-space dimension (d=3, N=4, dim=64; d=4, N=5, dim=625) the full operator is tiny and direct
classical diagonalisation / Lanczos reaches iso-accuracy far faster than DMRG, which pays a fixed sweep +
SVD overhead:
- d=3: classical 0.0013 s vs DMRG 0.045 s → **DMRG ~35× SLOWER**.
- d=4: classical 0.0032 s vs DMRG 0.053 s → **DMRG ~16× SLOWER**.
A quantum-inspired tensor method is **not** universally superior. Below the curse-of-dimensionality
crossover, the direct classical solver is the correct tool, and we say so.

## 2. The win is a CLASSICAL win, not a quantum-compute advantage (honesty rail)
The DMRG advantage in the moderate/large-d regime comes entirely from the **area-law entanglement** of the
near-Maxwellian collisional-equilibrium closure state (mid-cut S ≤ 0.7 nats; effective Schmidt rank ≤ ~40,
measured on the exact ground state). This is the ordinary MPS mechanism. It demonstrates that the K1
transport closure is **tensor-network-compressible today** — a real, useful, present-tense result — and it
says **nothing** about a fault-tolerant quantum-computer speedup. The quantum-computation claim remains
track7's OFFLINE resource estimate (provenance RESOURCE-EST; assumes hardware that does not exist). The
three-tier TRL spine is intact: this lever lives in the "runs today, classical hardware" tier.

## 3. The boundary of the claim — where the win would break (flagged, not hidden)
The win holds only while the closure state is low-entanglement (area law). It would erode or reverse for a
genuinely high-entanglement / volume-law state:
- the **fully nonlinear** collision operator far from local equilibrium (the bilinear Landau term the K1
  resource estimate Carleman-linearises);
- the true **5-D velocity grid** mapped onto the 1-D MPS chain with large transverse width — the known
  "DMRG-in-2D/3D" penalty, where required χ grows exponentially in the transverse extent.
We tested double-well (nonlinear-surrogate on-site) and 2-D-grid coupling topologies and did **not** reach
volume-law entanglement at accessible sizes (S stayed ≤ ~1.3 nats), so we could not exhibit a clean DMRG
loss in that regime — and we therefore restrict the positive claim to the area-law closure regime rather
than asserting a general advantage. Locating the χ-blowup crossover is listed as open work.

## 4. The large-d gap to the analytic formula is discretisation, NOT a solver error (resolved)
At d≥10 the only available reference is the continuum coupled-oscillator normal-mode formula, and DMRG sits
~6–9% above it. This is **not** DMRG inaccuracy: at feasible anchors the *exact discretised* ground energy
also differs from the continuum formula by the same ~6% (d=6: 5.76%; d=7: 6.35%), and DMRG is
χ-converged to 5.7e-9 (χ=8 vs χ=48) at d=10. The gap is the finite-grid discretisation of the Laplacian.
Scoring in the CSV uses the exact *discretised* operator as ground truth wherever it is feasible; the
continuum formula is labelled a coarse reference in the `ground_truth_or_verdict` column.

## 5. From-scratch DMRG instead of a library (disclosed)
A real MPS library (`quimb`) was attempted first; its build chain (llvmlite/numba) requires CMake, which is
unavailable in this environment, so the install failed. We used a documented from-scratch two-site DMRG —
permitted by the spec — and, unlike a black-box library call, **proved** its correctness against exact
diagonalisation to machine precision (§Verification in track_README). A development bug in the effective-
Hamiltonian matvec (Hermiticity error 67; variational upper bound violated) was caught by that check and
fixed before any result was produced. A library cross-check is listed as open work.

## 6. d=80 not run (budget-capped, disclosed)
The d=80 feasibility point (classical dim 8⁸⁰≈1.8×10⁷²) is marked `not_run` in the CSV rather than being
extrapolated as if measured. The χ-converged feasibility trend from d≤40 supports that DMRG would run there;
we do not report a number we did not compute.

## 7. Provenance
Every row is SIM. No operating-plant data. No quantum hardware. No ITER data is used in this lever. Ground
truth is exact classical diagonalisation of the same discretised operator.
