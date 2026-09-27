# The fault-tolerant cost model — one model, three kernels (Track 7)

**Provenance: RESOURCE-EST.** Every number below is produced by `ft_cost_model.py` and read into
`ft_cost_model_params.csv`; none is narrated. **This model assumes fault-tolerant quantum hardware that
does not yet exist.** No estimate here is a measurement. Kronos has no operating plant; this section
touches no plant data of any kind.

This is the single surface-code + magic-state-factory cost model used for **all three** kernels K1
(Vlasov/kinetic, E3), K2 (equilibrium linear-solve, E1), K3 (first-wall/conductor materials, E8). Each
kernel supplies a triple **(logical qubits `n_L`, T-count `N_T`, T-depth `D_T`)** as a function of
problem size; this model converts that triple into a **code distance, a physical-qubit footprint, and a
wall-clock**, under stated hardware assumptions.

## 1. Published relations used (all resolved to DOIs)

| role | reference | identifier |
|---|---|---|
| surface-code error suppression + patch footprint | Fowler, Mariantoni, Martinis & Cleland, *Phys. Rev. A* **86**, 032324 (2012) | doi:10.1103/PhysRevA.86.032324 |
| magic-state factory footprint / reaction-limited runtime / whole-algorithm accounting | Gidney & Ekerå, *Quantum* **5**, 433 (2021) | doi:10.22331/q-2021-04-15-433 |
| scale-to-advantage resource methodology | Beverland et al., arXiv:2211.07629 (2022) | arXiv:2211.07629 |
| fault-tolerant resource-estimation methodology | Sanders et al., *PRX Quantum* **1**, 020312 (2020) | doi:10.1103/PRXQuantum.1.020312 |

## 2. The model, term by term (each symbol is a CSV column in `ft_cost_model_params.csv`)

**Logical error suppression (Fowler 2012).** For surface-code distance `d`, physical error rate `p`, and
threshold `p_th`, the logical error per logical qubit per surface-code cycle is
`p_L(d) = A (p/p_th)^((d+1)/2)`, with `A = 0.1`, `p_th = 1e-2`.

**Distance selection.** We require the total logical error over the whole computation to stay below a
budget `P_fail = 1e-2`: `n_L · D_T · p_L(d) < P_fail`, and pick the smallest odd `d` that satisfies it.
`D_T` (T-depth) is used as the number of logical cycles because in a T-limited computation the logical
clock advances one distilled T per logical cycle.

**Physical-qubit footprint.**
`data qubits = c_area · d² · n_L` with `c_area = 2` (rotated surface-code patch incl. routing);
`factory qubits = c_fac · d² · n_fac` with `c_fac = 15` (one distillation factory ~ 15 d² physical qubits)
and `n_fac = ceil(N_T / D_T)` factories run in parallel to keep the T-consumption reaction-limited.
`physical qubits = data qubits + factory qubits`.

**Wall-clock (reaction-limited — the *optimistic* case for quantum).**
A logical cycle takes `d` surface-code cycles of duration `t_cycle`, so
`wall-clock = D_T · d · t_cycle`. This is a lower bound on runtime: it assumes enough magic-state
factories that distillation never stalls the logical clock. If factories are the bottleneck the runtime
is larger; we deliberately report the *quantum-favourable* bound so that a "no crossover" verdict is
robust.

**Hardware scenarios (three, carried as low/mid/high ranges throughout).**

| scenario | `p` (physical error) | `t_cycle` | reading |
|---|---|---|---|
| optimistic | 1e-4 | 100 ns | deep sub-threshold, aggressive SC clock |
| baseline | 1e-3 | 1 µs | near-term FT target (1e-3 gate error, 1 µs cycle) |
| pessimistic | 3e-3 | 1 µs | near threshold — distance and footprint blow up |

## 3. Validation of the model itself (sanity anchor)

Run at `n_L = 100, N_T = 1e9, D_T = 1e6`, the model returns (baseline) `d = 19`, ~5.5×10⁶ physical
qubits, ~19 s. This sits in the same regime as the independent Gidney–Ekerå RSA-2048 estimate
(2×10⁷ physical qubits, ~8 h, ~10¹¹ Toffolis) once T-counts are matched — i.e. the model is not
optimistic by orders of magnitude relative to a published whole-algorithm estimate. The formal
cross-check per kernel is in `cross_check.csv`.

## 4. What each kernel must supply (and where its honesty rails live)

- **K1 (Vlasov, E3):** `n_L`, `N_T`, `D_T` from Hamiltonian-simulation/qubitization of the discretised
  5-D kinetic operator, **plus the Carleman/Koopman–von Neumann linearisation cost as an explicit line
  item** (the bilinear collision operator is not natively unitary; AC-40). Classical baseline: a NAMED
  gyrokinetic Eulerian code (GENE/CGYRO-class, Candy–Waltz) on NAMED HPC.
- **K2 (equilibrium, E1):** `n_L`, `N_T`, `D_T` from an improved QLSA — **and the read-in (state prep)
  and read-out (measurement/tomography) costs as explicit terms, leading the panel** (AC-41). Classical
  baseline: a NAMED multigrid Grad–Shafranov solver (EFIT-class, Lao 1985) on a NAMED CPU.
- **K3 (materials, E8):** `n_L`, `N_T`, `D_T` from QPE/qubitization of the second-quantised electronic
  Hamiltonian, **with the active-space size (orbitals, electrons) printed and the reduction from the full
  materials problem stated as a limitation** (AC-42). Classical baseline: a NAMED DMRG/CCSD(T) code
  (Block2 / PySCF) on NAMED hardware.
