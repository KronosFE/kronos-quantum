# Track 7 — Quantum-COMPUTATION resource estimation (three kernels K1/K2/K3)

**Part III-B core result.** A resource-bounded assessment of where offline quantum computation could —
and, this decade, could **not** — help three fusion kernels. The pre-registered expected outcome
(AC-43) is *no crossover this decade*, registered as a **PASS**; the section leads with that negative.

**TRL tier (fixed):** Quantum COMPUTATION — **offline, calibration tier, NEVER in the control loop.**
Every artifact here is **RESOURCE-EST**: it assumes fault-tolerant hardware that does not yet exist and
is not a measurement. **Kronos has no operating plant**; nothing here touches plant data.

---

## What each file establishes

| file | what it establishes |
|---|---|
| `ft_cost_model.md` / `ft_cost_model.py` / `ft_cost_model_params.csv` | The ONE surface-code + magic-state-factory cost model used for all three kernels. Distance selection (Fowler 2012), factory footprint (Gidney–Ekerå 2021), 3 hardware scenarios (optimistic/baseline/pessimistic). Every assumption is a CSV column. Validated against the RSA-2048 whole-algorithm anchor. |
| `kernels.py` | K1/K2/K3 resource models: (logical qubits, T-count, T-depth) vs problem size, plus each kernel's NAMED optimized classical baseline (code + hardware) and FLOP curve. |
| `build_estimates.py` → `quantum_resource_estimate.csv` | **Primary deliverable.** 69 rows: one block per kernel × problem size × {low,mid,high}. 26 columns incl. logical qubits, T-count, T-depth, code distance, physical qubits, factories, quantum wall-clock, classical FLOPs low/high, classical wall-clock, classical code + hardware, and — for K2 — the explicit read-in/read-out/κ/solve-only-vs-end-to-end terms; for K1 the Carleman order; for K3 the active-space size. |
| `build_analysis.py` → `crossover_verdict.csv` | Per-kernel crossover verdict, AC-43 band, honest logical-qubit/error-rate threshold, earliest defensible date. |
| → `taxonomy.csv` (F25) | kernel × algorithm × speedup **CLASS** (not factor) × read-in/out penalty × TRL. |
| → `cross_check.csv` | Anchors K3 to von Burg 2021 (FeMoco), K1 to Engel 2019, K2 to Aaronson 2015; ratio to each published anchor carried. |
| → `roadmap_dates.csv` (F29) | NAMED, attributed vendor hardware roadmaps (IBM/Google/Quantinuum). |
| `track7_citations.csv` | 21 citations, all resolved to DOIs/arXiv ids. |
| `figs/F25_taxonomy.png` | Taxonomy matrix (CLASSES not factors, AC-39). |
| `figs/F26_resource_estimate.png` | 3-panel logical-qubits + T-count vs problem size; **K2 panel LEADS the read-in/read-out adverse** (AC-41). |
| `figs/F27_crossover.png` | Wall-clock crossover — **NO CROSSOVER** for all three vs optimized classical baselines (AC-43). |
| `figs/F29_roadmap.png` | Qubit thresholds vs dated vendor roadmaps; compute tier only, sensing separated (AC-46). |
| `ADVERSE.md` | The negative results, both ways. Required. |

## What I did

1. **One FT cost model** (`ft_cost_model.py`): surface-code logical error `p_L(d)=A(p/p_th)^((d+1)/2)`
   (Fowler 2012), smallest-distance selection against a whole-algorithm failure budget, footprint =
   data patches (2 d² each) + magic-state factories (15 d² each, n_fac = ⌈N_T/D_T⌉), reaction-limited
   wall-clock = D_T·d·t_cycle. Three hardware scenarios carried as low/mid/high everywhere. Sanity-checked
   against Gidney–Ekerå RSA-2048 (same regime once T-counts are matched).
2. **Three kernels** resource-estimated vs problem size, each with its NAMED optimized classical baseline:
   - **K1 Vlasov/kinetic (E3)** — Hamiltonian sim / qubitization / LCU; **Carleman/KvN nonlinearity cost
     itemized** as a column (AC-40); classical = CGYRO/GENE Eulerian gyrokinetic (Candy–Waltz 2003) on a
     Perlmutter node.
   - **K2 equilibrium linear-solve (E1)** — improved QLSA; **read-in O(N) + read-out O(N/ε²) + κ~N as
     explicit terms, LEADING the panel** (AC-41); classical = EFIT-class multigrid Grad–Shafranov
     (Lao 1985) on one CPU core.
   - **K3 materials (E8)** — QPE/qubitization (THC/linear-T); **active space printed, reduction stated as
     a limitation** (AC-42); classical = DMRG (Block2) optimized / CCSD(T) naïve.
3. **Cross-check** (founder pt 8): anchored K3 to von Burg 2021 within ~1 order of magnitude on both
   qubits and T-count; carried low/mid/high **ranges** on T-count and qubits throughout (they swing
   orders of magnitude on assumptions), never point values.
4. **Taxonomy + dated thresholds + figures** F25/F26/F27/F29, provenance RESOURCE-EST on every caption
   with code-distance + cycle-time stated inline.

## Acceptance criteria — bars and outcomes

| AC | requirement | outcome |
|---|---|---|
| **AC-43** (headline) | crossover per kernel or its absence, vs NAMED optimized code on NAMED hardware; bars ≤10² qubits & ≤10⁹ T (2030), ≤10³ & ≤10¹² (2035) | **PASS** — NO CROSSOVER THIS DECADE for K1/K2/K3, computed against named optimized baselines; the pre-registered expected PASS. |
| **AC-05 / ABS-07** | abstract negative result WITH crossover size + qubit/error/date threshold | **PASS** — content supplied in `crossover_verdict.csv` for the abstract sentence (size, qubits, date per kernel). |
| **AC-02 / ABS-03** | 3 of 3 kernels with a complete resource block AND a named optimized classical baseline | **PASS** — all three kernels have full blocks + named baselines (CGYRO/GENE, EFIT multigrid, DMRG). |
| **AC-38** | F25/F26/F27/F29 captions state d, cycle time, magic-state overhead, logical error rate, and "assumes FT hardware that does not yet exist" | **PASS** — all five elements in every RESOURCE-EST caption. |
| **AC-39** | every taxonomy cell carries a speedup CLASS, no bare factor | **PASS** — `taxonomy.csv`, classes only. |
| **AC-40** | K1: logical qubits, T-count, depth, wall-clock PLUS nonlinearity cost itemized | **PASS** — all four quantities + `carleman_order_Kc` and nonlinearity_cost columns. |
| **AC-41** | K2: read-in and read-out each an explicit term; F26 K2 panel leads with them | **PASS** — `readin_Tcount`, `readout_reruns`, `N_T_solveonly` vs end-to-end `T_count` columns; F26 K2 leads. |
| **AC-42** | K3: active-space size printed, reduction stated as a limitation | **PASS** — `active_space_M` column + limitation in taxonomy and ADVERSE. |
| **AC-46** | dated points attributed to NAMED public roadmaps; sensing/compute separated on F29 | **PASS** — `roadmap_dates.csv` attributed; F29 is compute-only, sensing pointed to Track 8b. |
| **AC-49** | "target" qualified as "target of the resource estimate"; zero Vlasov kernels executed | **PASS** — no Vlasov kernel executed; K1 is resource-estimated only (stated in ADVERSE A7-3). |

## Adverse findings (see ADVERSE.md)
- **Headline:** quantum loses to classical for all three kernels at every size swept — NO CROSSOVER THIS
  DECADE (A7-1).
- **K2 LEAD:** read-in + read-out inflate the end-to-end T-count by ~10¹⁰× (1.84×10¹⁷ vs a "one solve"
  illusion of 1.84×10⁷); classical multigrid O(N) wins (A7-2).
- **K1:** the bilinear-collision nonlinearity forces a Carleman tower that multiplies qubits by K_c (A7-3).
- **K3:** the CCSD(T) "apparent crossover" is rejected as an unoptimized-baseline artifact; the
  active-space reduction is a different problem from the engineering-scale materials question (A7-4).
- **All:** the hardware does not exist; ranges span orders of magnitude (A7-5); cross-check discrepancies
  reported not smoothed (A7-6).

## Open items I could not fully close
- No published FT resource estimate exists for the **collisional** Vlasov operator specifically; K1's
  T-count is a model extrapolation anchored on qubits only (Engel 2019 covers the linear case).
- Classical baseline FLOP rates are nominal order-of-magnitude figures, not per-kernel benchmarks — but
  the quantum deficit is 5–20 orders of magnitude, so this does not affect any verdict.

## Reproduce
```
cd track7_quantum_resources
PYTHONPATH="$PWD" python ft_cost_model.py      # -> ft_cost_model_params.csv
PYTHONPATH="$PWD" python build_estimates.py    # -> quantum_resource_estimate.csv
PYTHONPATH="$PWD" python build_analysis.py     # -> crossover_verdict.csv, taxonomy.csv, cross_check.csv, roadmap_dates.csv
# figures: run make_figures.f25/f26/f27/f29 inside a kernel with figure-style's apply_figure_style loaded
```

---

## FINAL EXPERIMENT F — resource-estimate SENSITIVITY / TORNADO (added, defensibility)

**Goal.** Turn the point T-counts and the "NO CROSSOVER THIS DECADE" verdict into a *robust* claim by
varying each assumption across its plausible range. Same derivation functions reused verbatim
(`ft_cost_model.ft_costs`/`code_distance`, `kernels.K1/K2/K3_resources`) — no new model. Provenance
**RESOURCE-EST**; assumes fault-tolerant hardware that does not yet exist; no Kronos plant data.

**Method.** One-at-a-time (OAT) sweep about each kernel's nominal interesting instance
(K1 N=64/K_c=3; K2 N_g=1e4; K3 M=100). Each assumption moved low↔high, others held nominal; recorded
spread in **logical qubits, T-count, physical qubits, quantum wall-clock, and earliest FT-machine year**
(from the NAMED vendor roadmaps). Ranges: physical error rate p∈[1e-4, 8e-3], cycle time∈[0.1, 10 µs],
T-gate cost/query ×[0.25, 4], plus each kernel's structural knob (K1 Carleman order K_c 2–4, grid N
32–128, block-encoding norm α·τ ×[0.1,10]; K2 grid N_g 1e3–1e6, κ exponent 0.5–1.5, read-out ε
1e-2–1e-4; K3 active space M 50–200, λ 1-norm exponent 1.5–2.0, walk T-count exponent 1.0–2.0). Also
ran the single **most quantum-optimistic corner** (all knobs simultaneously most favourable, smallest
meaningful size) to test whether a crossover *ever* appears.

**Files.** `resource_sensitivity.py` → `resource_sensitivity.csv` (90 rows: kernel, assumption_varied,
low_value, high_value, metric, low_result, high_result, swing, log10_swing),
`resource_sensitivity_dominant.csv` (widest-bar assumption per kernel×metric),
`crossover_survival_corner.csv` (optimistic-corner test), `F_resource_tornado.png` (3-panel tornado).

**Dominant assumption (widest tornado bar).** The spread lives almost entirely in **T-count**; logical
qubits and the FT-machine availability year barely move.
- **K1:** T-count dominated by **grid resolution N** (log10 swing ≈ 3.0; runner-up block-encoding norm
  α·τ ≈ 2.0). Qubits swing only 100→160 (Carleman order is the widest qubit bar, +60).
- **K2:** T-count dominated by **grid unknowns N_g** (log10 swing ≈ 6.3; runner-up read-out ε ≈ 4.3 —
  i.e. the read-out penalty itself is the second-largest lever, reinforcing the AC-41 lead adverse).
  Qubits swing only 40→50.
- **K3:** T-count dominated by the **walk/block-encoding T-count exponent** (log10 swing 2.0; active
  space M essentially tied at 1.96). Qubits swing 70→220 (active space M is the widest qubit bar).

**Hardware assumptions do NOT flip the verdict.** Physical error rate p and cycle time have **zero**
effect on logical qubits and T-count (they change code distance → physical-qubit footprint and
wall-clock only, not the algorithmic logical resource). Across the full plausible p/cycle-time range the
earliest FT-machine year stays **pinned at 2029** (first ~200-logical-qubit machine on the IBM roadmap)
for all three kernels; only K3 at the top of the active-space range (M=200 → 220 logical qubits) slips to
**2033**. Logical-qubit counts stay **O(10–10²)** everywhere (K1 100–160, K2 40–50, K3 70–220).

**Crossover survives the full range — including the optimistic corner.** At the single most
quantum-favourable corner of every kernel simultaneously (`crossover_survival_corner.csv`), quantum
wall-clock still LOSES to the optimized classical baseline by a wide margin:
- K1 @ N=32: q/classical ≈ **1.6×10⁴** (8.7×10³ s vs 0.54 s), 90 logical qubits.
- K2 @ N_g=1e3: q/classical ≈ **1.2×10¹⁰** (5.8×10⁴ s vs 5×10⁻⁶ s), 40 logical qubits.
- K3 @ M=50: q/classical ≈ **1.6×10⁴** (9.9 s vs 6.3×10⁻⁴ s), 70 logical qubits.

**Verdict.** The "NO CROSSOVER THIS DECADE" result (AC-43) **SURVIVES the full plausible range of every
assumption, and survives the joint optimistic corner** — there is no single optimistic corner in the
swept space where quantum wins on wall-clock. What varies is only *how far* quantum loses (the T-count,
by 3–6 orders of magnitude), never *whether* it loses. This strengthens AC-43 from a point claim to a
range-robust one. See `F_resource_tornado.png`.
