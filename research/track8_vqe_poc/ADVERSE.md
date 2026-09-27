# Track 8 — ADVERSE FINDINGS (kept and reported both ways)

*A negative result is a deliverable. This track's central adverse finding is exactly the
candor that makes Track 7's resource estimates credible: on a simulated NISQ device, VQE
does not reach chemical accuracy even on a 2-qubit molecule.*

**Provenance:** `SIM` — simulator only. No cloud hardware. No Kronos operating-plant data.

---

## AF-1 — The noisy backend never reaches chemical accuracy (the noise ceiling)

Chemical accuracy = 1 kcal/mol = **1.594 mHa**. On the ideal statevector simulator, VQE
hits it at every instance. On the Aer noisy backend (depolarizing p1=1e-3 / p2=1e-2,
readout 1%, 8192 shots, 5 seeds) it **never** does:

| instance | qubits | UCCSD depth | ideal err (mHa) | noisy err mean±std (mHa) | × over chem-acc |
|---|---|---|---|---|---|
| H2 | 2 | 11 | 0.0000 | **22.63 ± 6.38** | 14× |
| LiH (2e,3o) | 4 | 234 | 0.0000 | **363.34 ± 4.87** | 228× |
| LiH (2e,4o) | 6 | 673 | 0.0001 | **991.09 ± 3.59** | 622× |
| LiH (2e,5o) | 8 | 1434 | 0.0514 | **2079.41 ± 4.11** | 1305× |

**Where noisy VQE fails:** at the *smallest instance tested*. There is no toy molecule
in this ladder for which unmitigated noisy VQE is chemically accurate. The failure is
driven by circuit depth: UCCSD depth explodes (11 → 234 → 673 → 1434) far faster than
qubit count (2 → 4 → 6 → 8), and every gate carries a depolarizing error, so the
accumulated infidelity scales with depth. This is the mechanism behind the "scale wall."

## AF-2 — Even at below-hardware gate error, the depth-234 LiH circuit misses the bar

Noise-threshold sweep at the primary 4-qubit / depth-234 LiH instance (`vqe_noise_
threshold_sweep.csv`), varying the 2-qubit gate error `p2`:

| p2 (2q gate error) | noisy err mean±std (mHa) | reaches chem-acc? |
|---|---|---|
| 1e-4 | 14.35 ± 3.83 | no |
| 3e-4 | **4.58 ± 2.62** (best) | no |
| 1e-3 | 31.70 ± 4.13 | no |
| 3e-3 | 137.44 ± 13.63 | no |
| 1e-2 | 363.14 ± 5.80 | no |

Even at `p2 = 1e-4` — **below** the ~1e-3 two-qubit error of current superconducting and
trapped-ion hardware — the error is **14.35 mHa (~9× over the 1.594 mHa bar)**. The
lowest floor anywhere in the sweep is **4.58 mHa at p2=3e-4 (~3× over the bar)**, with no
error mitigation and finite (8192) shots. The non-monotonic dip at 3e-4 is
shot-noise/optimizer interplay, not a real optimum; the honest reading is *the floor sits
several mHa above chemical accuracy across the whole sub-1e-3 error range for this depth
— nowhere does it cross the bar*. **Conclusion:** for a depth-234 UCCSD circuit,
reaching chemical accuracy requires either (i) error rates well below current hardware
*and* error mitigation, or (ii) a shallower ansatz (e.g. ADAPT-VQE, Grimsley 2019) —
i.e. exactly the fault-tolerant / algorithmic improvements Track 7 resource-estimates.

## AF-3 — What this does NOT show (banned-claim guard)

- This is **not** a materials result. LiH (2e,3o) in STO-3G is a toy instance, not a
  breeder-ceramic property calculation. *"We computed fusion materials on a quantum
  computer"* is false twice over — simulator not hardware, toy instance not a materials
  answer (AC-44 fail_action language).
- This is **not** a quantum advantage. UCCSD/VQE is a known method; classical FCI solves
  every instance here in milliseconds. The exact reference **is** the classical baseline,
  and it wins at this scale by a wide margin.
- Quantum computation stays on the **offline calibration tier, never in the control
  loop** (three-tier spine). Nothing in this track feeds a real-time controller.

## Honest framing (both ways)
- *Negative:* on simulated NISQ hardware, VQE cannot reach chemical accuracy for even the
  smallest fusion-relevant molecule without fault-tolerance-class improvements.
- *Positive:* the **method is correct** — the ideal statevector VQE recovers the FCI
  ground state to < 0.1 mHa at every scale, confirming the ansatz, mapping, and optimizer
  are sound. The gap to usefulness is entirely the hardware noise, which is precisely the
  quantity Track 7 estimates the fault-tolerant cost of closing.
