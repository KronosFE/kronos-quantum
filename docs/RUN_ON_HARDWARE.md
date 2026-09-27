# Running on real quantum hardware

Every quantum code builds its circuit once and runs it through one backend layer
(`kronos_quantum/quantum_backend.py`). The default is a free, exact local statevector simulator that
runs on any CPU. The **same** circuit runs on shot-based simulation or real hardware by setting
environment variables — no code change.

| `KODEX_QC_BACKEND` | Device | Notes |
|---|---|---|
| unset / `default` | `default.qubit` | exact statevector, free, CPU (the default) |
| `aer` | `qiskit.aer` | local shot-noise simulator |
| `ibm` | `qiskit.remote` | **real IBM Quantum hardware** (needs `KODEX_QC_TOKEN`) |

## Steps

1. Install the hardware extra:
   ```bash
   pip install -e '.[hardware]'      # pennylane-qiskit, qiskit-aer
   ```
2. Set the backend and (for real hardware) your token:
   ```bash
   export KODEX_QC_BACKEND=ibm
   export KODEX_QC_TOKEN=<your IBM Quantum API token>
   # optional: export KODEX_QC_IBM_BACKEND=<specific backend name>   # default: least-busy
   ```
3. Run any code unchanged:
   ```bash
   PYTHONPATH=. python -c "import kronos_quantum as Q; print(Q.run('KQUBIT').note)"
   ```

Each benchmark reports where it actually ran via `backend_note()` (the `backend` field in the
benchmark dict), so a result is never ambiguous about whether it came from the simulator or hardware.

## What to expect on hardware, honestly

- **Noise dominates at depth.** VQE (`KQUBIT`) and dynamics (`KDYN`) lose accuracy quickly on today's
  devices; error mitigation (`KMIT`) claws some of it back but does not eliminate it.
- **No advantage.** On the problem sizes here, hardware will not beat classical methods. That is
  expected. The purpose is a real, tested pipeline — not a speedup.
- **Queueing and cost** are managed by your quantum provider account, not by this repository.

The backend falls back safely to the local simulator if a hardware plugin is missing, so nothing here
breaks in a bare environment.
