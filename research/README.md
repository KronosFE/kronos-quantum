# Research tracks

These are the deeper research artifacts the polished `kronos_quantum` codes were distilled from — the
raw analyses, sweeps, figures, citations, and honest adverse-findings notes. They are provided as an
**archive of provenance**, not as part of the installable package: each track was produced in the
broader Kronos research corpus and documents itself in its own `track_README.md`. Read them to see the
work behind the headline numbers.

Every track ships an **`ADVERSE.md`** — the pre-registered failures, caveats, and null results. We keep
these deliberately; a quantum result that survives its own adverse review is worth more than one that
was never challenged.

| Track | Feeds | What's inside |
|---|---|---|
| `track7_quantum_resources` | **KQROSS** | fault-tolerant resource model: qubitization T-counts, surface-code overhead, classical baselines, the crossover verdict, roadmap dates, and a resource-sensitivity tornado |
| `track8_vqe_poc` | **KQUBIT**, **KMIT** | VQE proof-of-concept: convergence, noise-threshold sweeps, the raw matrix, and the scaling wall |
| `track8b_quantum_sensing` | **KSENSE** | quantum-sensing evaluation: precision scaling across devices, sensing-to-disruption gain, TRL mapping, and sensitivity-vs-bandwidth |
| `track_R3_3_tensor_network` | **KTENSOR** | tensor-network vs classical: DMRG/kernel experiments, entanglement and effective Schmidt rank, feasibility verdicts |

**Honest framing (shared with the whole repo):** no quantum advantage for fusion is claimed this
decade; a meaningful role is a post-~2036 prospect. These tracks are the evidence for that position —
including the resource gap (track7) and the null results (track8b) that make the case.

**Note on running them:** the track scripts were written inside the full research corpus and reference
its layout; they are here for transparency and citation, not as turnkey scripts. The turnkey, runnable
form of this work is the `kronos_quantum` package at the repository root.
