# ADVERSE.md — Track 7 (Quantum-COMPUTATION resource estimation)

**Every finding here is a deliverable, not a defect.** The pre-registered expected outcome (AC-43) is
*no plausible crossover this decade for any of the three kernels*, registered as a **PASS of the paper**.
This file states the negative results both ways: what is true, and what a reader must not conclude.

Provenance on everything below: **RESOURCE-EST**. Every estimate assumes fault-tolerant quantum
hardware that does not yet exist; no number here is a measurement. Kronos has no operating plant.

---

## A7-1 — The section headline: quantum loses to classical for all three kernels (AC-05, AC-43)

Read off `crossover_verdict.csv` (mid range, quantum reaction-limited *lower*-bound wall-clock vs the
NAMED optimized classical baseline on NAMED hardware):

| kernel | scientifically-interesting size | logical qubits | T-count | crossover | earliest hardware date | verdict |
|---|---|---|---|---|---|---|
| K1 Vlasov (E3) | N=64 (1.07×10⁹ dof) | 130 | 1.29×10¹³ | **none** | qubit count reachable ~2029 (IBM proj.) — but runtime still loses | **NO CROSSOVER THIS DECADE** |
| K2 equilibrium (E1) | N_g=10⁴ grid | 44 | 1.84×10¹⁷ (end-to-end) | **none** | qubit count reachable ~2029 — runtime loses catastrophically | **NO CROSSOVER THIS DECADE** |
| K3 materials (E8) | M=100 spin-orbitals | 120 | 7.91×10⁹ | **none** | qubit count ~2029–2030 — runtime loses | **NO CROSSOVER THIS DECADE** |

**Both ways.** *True:* on the assumed fault-tolerant hardware, quantum wall-clock exceeds the optimized
classical baseline at every problem size swept, for every kernel. *Must not conclude:* that quantum is
"not yet competitive" (a softening banned by AC-05) — the falsifiable content is that at the qubit/T
bars of AC-43 (≤10² qubits & ≤10⁹ T for 2030; ≤10³ & ≤10¹² for 2035) **no kernel produces a crossover
against an optimized baseline**, and that is stated with its size and date.

**The one-line physical reason** (in every F27 caption): a surface-code *logical* operation takes
~d·t_cycle ≈ 20 µs (baseline d=19, 1 µs cycle), while a classical FLOP takes ~1 ns — a ~10⁵× clock
handicap. Quantum wins only if it needs ≥10⁵× *fewer* operations. None of these kernels clears that.

---

## A7-2 — K2 LEAD ADVERSE: read-in and read-out erase the QLSA speedup (AC-41)

This is the honest core of the section and the reason the rest is credible. QLSA (HHL and successors)
solves **A**ψ=**b** in time polylog(N) — an *apparent* exponential speedup. For the equilibrium linear
solve it is **not available**, for structural reasons quantified in `quantum_resource_estimate.csv`
(K2 rows) as **explicit columns**, not prose:

- **Read-in** (`readin_Tcount`): the right-hand side p′(ψ), FF′(ψ) on a shaped negative-δ boundary has
  no exploitable amplitude structure, so preparing |b⟩ costs **O(N_g)** — 4×10⁴ T-gates at N_g=10⁴.
- **Read-out** (`readout_reruns`): control needs ψ on the **whole grid** (the flux map / coil currents),
  not one expectation value ⟨M⟩. Extracting the full field to accuracy ε needs **O(N_g/ε²)** repetitions
  of (solve + read-in), because measurement destroys the state — **10¹⁰ reruns** at N_g=10⁴, ε=10⁻³.
- **Conditioning** (`kappa`): κ(**A**) ~ N_g for a fine elliptic grid, and QLSA runtime carries κ.

The result: the **end-to-end** T-count is **1.84×10¹⁷** at N_g=10⁴, versus the *misleading* "one solve"
figure of **1.84×10⁷** — a **10¹⁰× inflation** from read-in/read-out alone. Meanwhile the NAMED
classical baseline (EFIT-class multigrid Grad–Shafranov, Lao 1985) solves the same system in **O(N_g)**
≈ 10⁶ FLOPs, milliseconds on one CPU core. **QLSA's end-to-end scaling for this problem's actual output
requirement is worse than classical.** Presenting QLSA as a faster Grad–Shafranov solver is wrong and
is blocked here (F26 K2 panel LEADS with this; the "one solve illusion" is drawn as a dashed line under
the true curve). This is exactly the failure mode catalogued by Aaronson 2015 (doi:10.1038/nphys3272)
and carried in canon E1.6.

---

## A7-3 — K1: the nonlinearity cost is itemized, not hidden (AC-40)

The Vlasov/collision operator is **bilinear** in (f_s, f_s′) while quantum evolution is **linear**. Any
quantum algorithm must first linearize via Carleman / Koopman–von Neumann embedding (Joseph 2020,
doi:10.1103/PhysRevResearch.2.043102), which lifts the state to a tower x, x², …, x^{K_c}. This is
carried as the explicit column `carleman_order_Kc` (low/mid/high = 2/3/4) and it **multiplies the logical
qubit count by K_c** and adds truncation error. Omitting this term is how Vlasov quantum-speedup claims
get inflated; it is itemized in every K1 row of `quantum_resource_estimate.csv`. The one genuinely
favourable structural feature — transport coefficients are low-order *moments* of f, so read-out is
cheap here (unlike K2) — is stated in the taxonomy, but it does not produce a crossover: the
block-encoding normalization (α·τ ~ N²) plus the clock handicap dominate.

**No Vlasov kernel is executed anywhere in this paper** (AC-49). K1 is the *target of the resource
estimate*, resource-estimated only — never "solved."

---

## A7-4 — K3: the active-space reduction is a limitation, stated as such (AC-42)

The materials estimate (`active_space_M` column, M=20–1000 spin-orbitals) is for a **reduced active
space**, not the full materials problem. A W first-wall vacancy or a REBCO unit cell reduced to M≈100
tractable orbitals is a **different problem** from the materials question that actually matters (defect
thermodynamics in a periodic solid with thousands of electrons). The estimate is interpretable **only**
with its active space printed, and the reduction is a limitation of the estimate — it is not evidence
that a quantum computer can answer the retention/binding question at engineering scale.

**The CCSD(T) trap.** F27's K3 panel shows an *apparent* crossover near M≈500 against a **naïve**
CCSD(T) O(M⁷) baseline (dotted line). Per AC-43 this is **rejected**: a crossover manufactured against
an unoptimized classical baseline is a FAIL. Against the **optimized** baseline (DMRG / Block2, dashed
solid line) there is **no crossover** — and in any case M≥500 exceeds the 2035 qubit/T bars. We report
the optimized-baseline verdict and flag the naïve-baseline crossover as the classic inflation artifact.

---

## A7-5 — The estimate assumes hardware that does not exist (AC-38, P3B-10)

Every number rests on: surface-code distance d (selected per Fowler 2012), physical error rate
p ∈ {10⁻⁴, 10⁻³, 3×10⁻³}, cycle time t_cycle ∈ {0.1, 1, 1 µs}, and a magic-state factory model
(15 d² physical qubits/factory, Gidney–Ekerå 2021). **None of this hardware exists.** The baseline
scenario alone needs millions of physical qubits per kernel (e.g. K2 at N_g=10⁴: d=19, ~10⁷ physical
qubits *before* the 10¹⁰ read-out reruns). The reaction-limited wall-clock is a *lower* bound (assumes
factories never stall) — real runtime is longer, which only strengthens the no-crossover verdict.
Ranges (low/mid/high) are carried on T-count and qubits throughout precisely because they swing orders
of magnitude on these assumptions.

---

## A7-6 — Cross-check honesty (founder pt 8)

`cross_check.csv` anchors the model to a **published** FT resource estimate: von Burg et al. 2021
(doi:10.1103/PhysRevResearch.3.033055) report ~2196 logical qubits and ~10¹⁰ Toffoli for FeMoco
(76 spatial / 152 spin-orbitals) at chemical accuracy. Our M=152 mid estimate lands at ~172 logical
qubits (**12× LOWER** — because our scaling model omits their double-factorisation ancillae) and
~3×10¹⁰ T (**3.08× higher**, same order of magnitude). **The qubit factor-of-12 discrepancy is stated,
not smoothed:** our model is a *scaling* model calibrated to the T-count of a published point, and it is
deliberately conservative on qubits — a fuller block-encoding (which we do not implement) would raise
our qubit count toward theirs. K1 anchors to Engel 2019 on the *linear*-Vlasov qubit count (matched:
n_sys=30 at N=64 ≈ their d·log₂N); K2 anchors qualitatively to the Aaronson 2015 caveat set. No kernel's
estimate sits more than ~1 order of magnitude from its published anchor on the quantity it anchors.

---

## Open items / things I could not do

- **No published FT resource estimate exists specifically for the collisional Vlasov operator at
  fault-tolerant scale.** Engel 2019 resource-counts the *linear* Vlasov (no collisions) and gives qubit
  scaling but not FT T-counts; our K1 T-count (QROM coefficient loading + Carleman tower) is therefore a
  *model extrapolation*, anchored on qubits only. Stated as such in `cross_check.csv`.
- **The classical baselines' FLOP rates are nominal** (Perlmutter node 2×10¹² F/s; 1 Xeon core 10¹⁰;
  HPC node 10¹²) — order-of-magnitude, not benchmarked on the specific kernels. This does not change the
  verdict (the quantum deficit is 5–20 orders of magnitude, not a factor of 2).
- **Roadmap dates are vendor projections** (IBM/Google/Quantinuum), attributed and labelled as such
  (AC-46); they are not physics and several have already slipped historically.

---

## FINAL EXPERIMENT F — sensitivity/tornado adverse findings

- **A7-7 (robustness of the negative):** the "NO CROSSOVER THIS DECADE" verdict is not a knife-edge of
  favourable assumptions. Swept over p∈[1e-4,8e-3], cycle time∈[0.1,10 µs], T-gate cost ×[0.25,4], and
  each kernel's structural knob across its plausible range, quantum loses on wall-clock at EVERY point.
  Even at the single most quantum-optimistic corner (all knobs simultaneously most favourable, smallest
  meaningful problem size) quantum still loses: K1 by ~1.6×10⁴×, K2 by ~1.2×10¹⁰×, K3 by ~1.6×10⁴×.
  There is no optimistic corner in the swept space where the verdict flips. Reported both ways: the
  negative is robust, and the *only* thing sensitivity buys the quantum case is a smaller loss margin
  (T-count down 3–6 orders), never a win.
- **A7-8 (which lever matters, honestly):** the dominant driver of the T-count spread is **problem size**
  (K1 grid N, K2 grid unknowns N_g, K3 walk exponent / active space M) — NOT the fault-tolerance
  hardware assumptions. p and cycle time move only the physical-qubit footprint and wall-clock, not the
  logical resource, and do not change any verdict. A reader must not attribute the no-crossover result to
  pessimistic hardware assumptions: optimistic hardware does not rescue it. For K2 specifically the
  second-largest T-count lever is the **read-out error ε** — the read-out penalty is itself one of the
  widest bars, reinforcing the AC-41 lead adverse rather than being incidental to it.
