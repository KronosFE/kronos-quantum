# Track 8b — ADVERSE FINDINGS (Quantum SENSING & metrology, E11)

*A negative result is a deliverable. Every finding here is kept and reported both ways.*
*Provenance: TRL-SURVEY (survey tables) + SIM (state-estimation propagation). No Kronos
operating-plant data exists.*

---

## AF-1 (headline adverse) — ZERO quantum-metrology magnetometers are environmentally qualified for equilibrium reconstruction
**AC-34 count = 0.** Of the surveyed quantum field sensors (SQUID, SERF OPM, NV ensemble,
squeezed-light), **none** has been demonstrated to meet the equilibrium-reconstruction need
band *in a reactor-relevant environment* (neutron/gamma dose, Tesla-scale stray field, cryo
constraints). The two most sensitive (SQUID ~1e-15 T/rtHz; SERF OPM 160 aT/rtHz) are the two
that most decisively fail the environment:
- **SQUID** needs a cryostat, a superconducting element and mu-metal shielding — all
  incompatible with in-vessel dose and the machine's own Tesla-scale field.
- **SERF OPM** *physically requires* a near-zero ambient field (<~50 nT) to reach the
  spin-exchange-relaxation-free regime; a tokamak runs at 1–10 T, which destroys the regime.
  Its ~100 Hz intrinsic bandwidth is also below the control need.

F23 therefore **shows the gap**, not a band the devices are assumed to reach. Laboratory
sensitivity is not environmental qualification. The honest survey verdict: **the classical
inductive pickup coil remains the incumbent for magnetic-equilibrium reconstruction**, and the
quantum contribution is a research trajectory, not a drop-in.

## AF-2 — In the strong-field equilibrium regime, sharper sensor noise buys essentially nothing
**F24 / sensing_to_ai_gain.csv.** Propagating each modality's noise through a linearized
magnetic state estimator: moving from a conventional-coil noise model (σ_B ≈ 5e-4 T,
drift/RIEMF-dominated) to a quantum-limited NV model (σ_B ≈ 2.8e-11 T) changes the PINN/GNN
state-estimate error by **only ~0.2%** for the ~6 T equilibrium field. The reconstruction is
**model-floor-limited** (a 0.2% forward-operator/geometry mismatch dominates), not
noise-limited. Quantum sensing improves the state estimate **only where sensor noise is the
bottleneck** — the weak-signal edge/fluctuation regime (there it cuts error ~92%). The paper
must not claim a general state-estimate improvement from quantum magnetometry; the gain is
regime-specific and, at the equilibrium field, negligible.

## AF-3 — "Quantum neutron detection" is largely a category error and is bounded accordingly
Per AC-33: **He-3 proportional counters are not quantum devices in the metrology sense** —
they are classical gas ionization counters. They appear in `quantum_sensing_trl.csv` **only**
as (a) the program's own detector-market cross-link and (b) the counting-statistics baseline
for E11's 1/√N rate rule (1% precision needs 1e4 counts). The genuinely advanced neutron
detectors (single-crystal diamond) are radiation-hard and fusion-deployed, but they are
**classical solid-state ionization detectors**, not quantum-enhanced metrology. There is no
"quantum advantage" neutron-detection result to claim; the honest content is
radiation-hardness and fast timing, both classical properties.

## AF-4 — The one plant-touching sub-shot-noise deployment is not a fusion deployment
Squeezed-light interferometry is genuinely **DEPLOYED sub-SQL** — but in Advanced LIGO, a
vibration-isolated observatory, not a reactor. The squeezer optics are not radiation-qualified
and cannot go in-vessel. It is the clearest real-world example of Heisenberg-scaling in
practice, and it is quarantined as **LAB-STAGE for fusion**. Listing it as "deployed" without
the environment qualifier would be the overselling mechanism AC-35 exists to block.

## AF-5 (method caveat) — the F24 result is a propagation study, not a demonstrated deployment
The sensing→AI gain is computed by **injecting a synthetic noise model** into a linearized
estimator and re-measuring reconstruction error. **No quantum sensor has fed data to any
Kronos model** (AC-37 disclosure). A synthetic noise reduction demonstrates the estimator's
*sensitivity to noise*, NOT that a quantum sensor delivered anything. The state estimator here
is a **stand-in** for the Track 2/3 PINN/GNN (their error models were not yet emitted when this
track ran); the qualitative saturation-vs-noise-limited structure is robust, but the specific
percentages inherit this stand-in's geometry and regularization.

## AF-6 (circularity guard) — the estimator is validated against a simulator, not reality
The forward operator (Biot–Savart filament model) and the "truth" current map are both
synthetic. This validates the *propagation logic* against the *model*, not against an operating
machine. Independent public ground truth for magnetic reconstruction exists (EFIT on published
equilibria; Lao 1985) and is named as the correct external anchor, but was not re-run here.
The F24 numbers are **SIM provenance** and must be captioned as such.
