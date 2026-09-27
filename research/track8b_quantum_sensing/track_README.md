# Track 8b — Quantum SENSING & metrology for fusion (E11)
### The higher-TRL, plant-touching half of the quantum story — the tier that FEEDS the AI

**Provenance posture (LOCKED).** Every table here is **TRL-SURVEY** (public literature, each
row a resolved DOI). The sensing→AI coupling (F24) is **SIM** (a bounded noise-propagation
study). **Kronos has no operating plant; no quantum sensor has fed any Kronos model.** All
figure captions carry their provenance tag and the DEPLOYED-vs-LAB-STAGE split.

**Hardware for any timing statement:** local CPU (56 cores, no GPU). All computations here are
sub-second; **no latency claim** is derived from this track.

**Design point** (from `CONSOLIDATED_2026-07-31/design_space/reference_design_card.csv`):
R₀=2.0 m, a=1.0 m, B₀=10 T, Ip=31.47 MA, nₑ=5.42×10²⁰ m⁻³.

---

## What each file establishes

| file | what it is | provenance |
|---|---|---|
| `quantum_sensing_trl.csv` | 9-row modality survey: sensitivity, bandwidth, dynamic range, radiation-hardness, **two TRL columns** (home-domain vs fusion-diagnostic), in-loop-capable, deployed-vs-lab, **is_quantum_metrology**, **survives_fusion_env verdict + per-row reasoning**. Every row ≥1 resolved DOI. | TRL-SURVEY |
| `sensing_precision_scaling.csv` | E11 theory laws Δφ_SQL=1/√N vs Δφ_Heis=1/N across N=10²–10¹². **Both are THEORETICAL scaling laws** (AC-50). | TRL-SURVEY |
| `precision_scaling_devices.csv` | 5 demonstrated devices overlaid on F22, each with dB-below-SQL, DEPLOYED/LAB-STAGE population, resolved DOI. | TRL-SURVEY |
| `sensing_to_ai_gain.csv` | Before/after PINN/GNN state-estimate error under conventional-coil vs quantum-limited (NV, SQUID) noise models, in two regimes, mean±std over 20 seeds. | SIM |
| `resolved_citations.csv` | 20 anchors, all DOIs resolved ≥ abstract via OpenAlex. | — |
| `build_track8b.py` | Reproduces every number and the F24 model. Seed 20260726. | — |
| `F21_trl_map.png` | Modality × TRL (home vs fusion) heatmap + quantum/classical + in-loop + survivability cut. | TRL-SURVEY |
| `F22_precision_scaling.png` | log-log SQL (∝N^−1/2) and Heisenberg (∝N^−1) theory slopes + demonstrated devices (marker fill=DEPLOYED/LAB, shape). | TRL-SURVEY |
| `F23_sensitivity_vs_bandwidth.png` | Sensitivity vs bandwidth; **shows the reactor-qualification GAP**; marker=survivability verdict, colour=in-loop status. | TRL-SURVEY |
| `F24_sensing_to_ai_gain.png` | State error vs sensor noise, two regimes; quantum gain only where noise-limited. | SIM+TRL-SURVEY |
| `ADVERSE.md` | Six adverse findings, kept and reported both ways. | — |

---

## The three-tier TRL spine — where this track sits
This is the **Quantum SENSING** tier: near-term, diagnostics-tier, **feeds the AI state
estimate, never the actuator path**. It is the only tier where quantum *touches the plant*.
Nothing here crosses into the AI tier (in-loop control) or the Quantum-COMPUTATION tier
(offline, resource-estimated). The GNN/PINN *consume* the sharpened state — quantum sensing
improves the input; it does not replace the AI.

## Headline honest cut
- **Deployed & radiation-hard for fusion today:** classical inductive coils (incumbent) and
  diamond neutron detectors. Neither is quantum-enhanced metrology.
- **Quantum, but not yet reactor-qualified:** NV-diamond ensemble is the single fusion-plausible
  quantum magnetometer (radiation-hard host, high-field capable), at TRL 2 for fusion.
- **Quantum & most sensitive, but disqualified by environment:** SQUID and SERF OPM.
- **Quantum & genuinely sub-shot-noise, but not in a reactor:** squeezed light (LIGO).

## Novelty (precise)
NV/SQUID/OPM magnetometry and squeezed-light metrology are **KNOWN**. Track 8b's contribution
is the **sensing→AI pipeline framing**: a quantitative, TRL-honest map of which modality could
feed which AI module, and a bounded propagation showing *where* a sharper sensor actually moves
the state estimate (weak-signal regimes) and where it does not (the strong equilibrium field).

## Open items / could-not-do
1. **Track 2/3 error models not yet emitted** when this track ran — F24 uses a linearized
   Biot–Savart state estimator as a **stand-in** for the PINN/GNN. When Tracks 2/3 publish their
   held-out error models, re-run `build_track8b.py` with their operator to replace the stand-in.
2. **No independent public benchmark re-run.** EFIT-on-published-equilibria (Lao 1985) is named
   as the correct external ground truth for magnetic reconstruction but was not executed here;
   the F24 study stays SIM.
3. **Radiation-hardness numbers are qualitative** (survives_fusion_env verdict + reasoning), not
   a dose-curve per modality — the literature does not provide dose-resolved sensitivity for most
   of these devices in a fusion spectrum. Rows are sourced to the best available identifier and
   the verdict states the mechanism.
