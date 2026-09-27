# F28 — Caption (provenance-compliant, CLAIM_LEDGER_NOTES §2)

**F28. VQE proof-of-concept: LiH ground state, ideal vs noisy simulator vs exact
diagonalization.**
`SIM` — simulator-only variational quantum eigensolver. All energies computed on a
Qiskit statevector simulator (ideal) and a Qiskit-Aer noise-model backend (depolarizing
1-/2-qubit error 1e-3/1e-2, 1% readout, 8192 shots); the exact reference is classical
full configuration interaction (pyscf FCI/CASCI). **No cloud quantum hardware was used.
No Kronos operating-plant data exists.**
*(a)* Energy vs VQE iteration for LiH in a minimal basis (STO-3G), active space
(2 electrons, 3 orbitals), 4 qubits, UCCSD ansatz: the ideal trace converges onto the FCI
reference within the ±1.6 mHa chemical-accuracy band (green), while the noisy trace
plateaus ~0.36 Ha above it. *(b)* Final energy error vs qubit count across a LiH/H2 ladder
(UCCSD circuit depth annotated as `d…`): ideal statevector VQE stays at chemical accuracy
until depth ~1400 (8 qubits); the noisy backend is already 14× over the bar at 2 qubits
and worsens monotonically to >1300× at 8 qubits. **The scale wall for noisy VQE is at the
smallest instance tested** — this is a **TOY-SCALE demonstration of the METHOD, not of a
quantum advantage.** Classical FCI solves every instance shown here in milliseconds.
