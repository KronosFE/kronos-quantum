# Track 8 — Quantum-COMPUTATION proof-of-concept, small & real (E8)

**Tier:** Quantum COMPUTATION — *offline, calibration tier, NEVER in the control loop*
(three-tier TRL spine, CLAIM_LEDGER_NOTES §1). This track exists to demonstrate the
**method** on a real chemistry instance at toy scale, and — by reporting the noise
ceiling honestly — to make Track 7's fault-tolerant resource estimates credible.

**Data posture:** `SIM` — simulator only. Statevector (ideal) + Qiskit-Aer noisy
backend model. **No cloud quantum hardware was used. No Kronos operating-plant data
exists.** This posture is stated in the F28 caption and in every table below.

---

## What I did

1. **Stack (Step 1).** Verified `kronos-quantum`: qiskit 2.5.1, qiskit-aer 0.17.2,
   qiskit-nature 0.8.0, qiskit-algorithms 0.4.0, pyscf 2.13.1, openfermion 1.8.1,
   pennylane 0.45.1. Built exact references with **pyscf FCI/CASCI** and cross-checked
   each against dense diagonalization of the mapped qubit operator (agreement < 1 µHa).

2. **VQE (Step 2).** Primary instance **LiH** (Li-tritide / lithium-ceramic breeder
   analog), minimal basis (STO-3G), active space **(2 electrons, 3 spatial orbitals)**
   → **4 qubits**, parity mapper, **UCCSD** ansatz, HF initial state, **COBYLA**
   optimizer. Ran on:
   - (a) ideal statevector estimator (exact expectation values), and
   - (b) Aer **noisy** backend: depolarizing 1-qubit `p1 = 1e-3`, 2-qubit `p2 = 1e-2`,
     symmetric readout `1e-2`, **8192 shots**, **5 random seeds** (20260726–20260730)
     for dispersion.
   A **qubit ladder** (H2 2q → LiH 2e3o 4q → LiH 2e4o 6q → LiH 2e5o 8q) locates the
   scale wall. Every energy is read off the reproducing script into a CSV column.

3. **Convergence + scale wall (Step 3).** `vqe_convergence.csv` (per-iteration ideal,
   noisy, exact, error in Ha and kcal/mol). `vqe_scale_wall.csv` (final error vs qubit
   count/depth). `vqe_noise_threshold_sweep.csv` (gate-error sweep at the primary
   instance). F28 plots the traces + the wall. **Baseline = exact diagonalization
   (FCI/CASCI); multi-seed with std** per AC guidance.

4. **Handoff (Step 4).** `vqe_for_calibration.csv` — the converged ideal and noisy
   ground-state energies of the primary LiH instance, for Track 6's calibration-loop
   demo to inject as the high-fidelity closure point.

---

## Acceptance criteria (pre-registered in Gate 0)

### AC-44 (NUMERIC, owner track8_vqe_poc) — **PASS (statevector) / reported (noisy)**
> *Metric:* absolute energy error vs exact diagonalization (Ha) on statevector and noisy
> backends; qubit count / circuit depth at which noisy convergence stops reaching
> chemical accuracy. *Threshold:* statevector error ≤ 1.6 mHa; noisy reported whatever
> it is; scale wall annotated on F28 as a specific qubit count or depth.

- **Statevector, primary LiH (4q): error = 0.0000 mHa ≤ 1.594 mHa → PASS.**
  Statevector reaches chemical accuracy at **every** ladder rung (2q/4q/6q = 0.0000 mHa;
  8q = 0.0514 mHa, still < 1.594).
- **Noisy backend (mean ± std over 5 seeds), reported:** 2q **22.63 ± 6.38 mHa**;
  4q **363.34 ± 4.87 mHa**; 6q **991.09 ± 3.59 mHa**; 8q **2079.41 ± 4.11 mHa**.
  Noisy **never** reaches chemical accuracy — not even at 2 qubits.
- **Scale wall annotated on F28** as a specific qubit count/depth: **the noisy backend
  is already 14× over chemical accuracy at 2 qubits / depth 11, and the gap widens
  monotonically** (228× at 4q/d234, 622× at 6q/d673, 1305× at 8q/d1434). The wall for
  *noisy* VQE is therefore at **the smallest instance tested** under an unmitigated NISQ
  noise model; the wall for *ideal* VQE (finite optimizer/COBYLA budget) first shows at
  **8 qubits / depth 1434**, where statevector error rises off the 1e-3 floor to
  0.051 mHa.

### AC-45 (BINARY-DISCLOSURE, track8_vqe_poc + track12_repro) — **PASS**
> No cloud quantum hardware used; disclosure in every quantum figure caption and methods.
- F28 caption carries `SIM (simulator-only, no cloud hardware)`. Every CSV note and this
  README state it. **No hardware claim anywhere.**

---

## Files

| file | what it establishes |
|---|---|
| `vqe_convergence.csv` | per-iteration ideal / noisy / exact energies + error (Ha, kcal/mol), all 4 instances. Source for F28 panel A. |
| `vqe_scale_wall.csv` | per-instance final ideal & noisy error (mean±std, 5 seeds), qubit count, transpiled depth, chem-acc verdict. Source for F28 panel B. |
| `vqe_noise_threshold_sweep.csv` | noisy error vs 2-qubit gate error at the primary 4q/depth-234 instance — the noise threshold study. |
| `vqe_for_calibration.csv` | **Track 6 handoff:** converged ground-state energy (ideal + noisy) as the high-fidelity closure point. |
| `resolved_citations.csv` | 6 citations, every one a resolvable DOI (Peruzzo 2014, Kandala 2017, Preskill 2018, Grimsley 2019, Cerezo 2021, Tilly 2022). |
| `F28_vqe_convergence.png` | the figure: convergence traces + scale wall. |
| `vqe_matrix_raw.json` | raw per-iteration histories for all runs (reproducibility). |
| `ADVERSE.md` | the noise ceiling — where noisy VQE fails to reach chemical accuracy, kept and reported both ways. |

## Reproducibility
Env `kronos-quantum`. Seeds 20260726–20260730. STO-3G, parity mapper, UCCSD, COBYLA.
Noise model: depolarizing p1=1e-3 / p2=1e-2, readout 1e-2, 8192 shots. Exact reference =
pyscf FCI (H2) / CASCI in the same active space (LiH), cross-checked vs dense
diagonalization of the qubit operator.

## Novelty (precise, per CLAIM_LEDGER_NOTES §6)
VQE and UCCSD are **known methods** (Peruzzo 2014; the whole point of this track is to
demonstrate the method, not a quantum advantage). The Kronos contribution is **not** new
quantum computing; it is the honest placement of quantum computation on the offline
calibration tier with a resource-estimated crossover (Track 7) and a
quantum-calibrates-surrogate handoff (Track 6, fed by `vqe_for_calibration.csv`).

## Open items
- Error mitigation (ZNE, readout correction) was **not** applied — deliberately, so the
  raw noise ceiling is visible. Mitigation would lower but not close the 4q gap; see
  ADVERSE.md. A follow-up could quantify the mitigation headroom.
- Larger active spaces / dissociation curves are out of scope for a toy-scale PoC.
