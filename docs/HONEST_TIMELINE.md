# The honest quantum-for-fusion timeline

This page states, in one place, the position that governs every card and benchmark in this repository.

## The claim

**No quantum *advantage* for fusion is claimed this decade. A meaningful role is a post-~2036 prospect.
The tooling and the testing are real today.**

## The reasoning (reproducible in `KQROSS`)

1. The strongest fusion target is **electronic structure** — materials and chemistry — where classical
   cost grows steeply with system size.
2. A useful fault-tolerant algorithm needs **logical** qubits well below physical error rates, produced
   by error correction at ~1e3 physical qubits per logical qubit near threshold.
3. A fusion electronic-structure kernel large enough to beat the best classical method sits near a
   crossover of ~N=50 spin-orbitals, needing on the order of **6e4 physical qubits**.
4. Today's hardware: ~1e2–1e3 physical qubits, **zero** error-corrected logical qubits.
5. Optimistic logical-qubit scaling reaches the required count around 2032; accounting for the
   remaining error-rate, gate-speed, and state-preparation gaps, a genuinely *useful* role arrives only
   after roughly **2036**.

`KLINQ`'s fault-tolerant HHL estimate (~4e4 physical qubits for a fusion-scale linear solve) points the
same way for linear algebra.

## Why we build now anyway

Because the methods, data pipelines, and judgment take years to get right, and they are exactly what a
fusion program will need the day the hardware is ready. Every code here is a real pipeline that runs on
a simulator today and on hardware the moment an account is configured — so the transition is a
configuration change, not a rewrite.

## What "no advantage" does *not* mean

It does not mean the work is premature. It means we report honestly: where quantum ties classical
(`KQERN`), where its scaling is erased by realistic noise (`KSENSE`), where a naive expectation is wrong
(`KTENSOR`), and where the resource gap is decisive (`KQROSS`, `KLINQ`). Those results are the value —
a serious, testable foundation, honestly dated.

## Relationship to our internal research

This public snapshot is a conservative floor. Our internal research runs roughly three to four years
ahead of what we have published; the difference is write-up time, and we intend to keep releasing it.
