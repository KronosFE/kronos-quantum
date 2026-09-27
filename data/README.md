# Data

Two small, real datasets are enough to run every code in this repository. The circuit-based codes
(KQUBIT, KQOPT, KDYN, KSENSE, KQROSS, KMIT, KLINQ) build their own problems and need no external data.

## `cgyro_a1e_flux_map.csv`  (16 rows)
The completed 16/16 **CGYRO A1e** nonlinear kinetic-electron turbulence flux map, at representative
fidelity (reduced electron mass μ=400). Columns: `a_LT`, `shear`, `Q_i`, `Q_e`, `Q_tot`, `verdict`
(turbulent/quiet), `source`. Used by **KTENSOR** (low-rank ROM) and available to the others.

- **Full published dataset:** Zenodo DOI **[10.5281/zenodo.22136279](https://doi.org/10.5281/zenodo.22136279)**.
- Honest scope: representative fidelity; a fully-converged real-mass "gold" validation point is a
  separate, deferred check.

## `mast_disruption_features.csv`  (591 rows)
Physics features for 591 real **MAST** shots (from the open FAIR-MAST archive), extracted over a fixed
50 ms pre-event window. Columns: `shot_id`, `disruptive` (0/1), then 13 features
(`ip_mean_MA`, `ip_std`, `ip_slope`, `ip_range`, `ne_mean`, `greenwald_proxy`, `beta_n`, `li`, `q95`,
`n1_rms_mean`, `n1_rms_slope`, `prad_mean`, `prad_slope`). Used by **KQERN**.

- Honest caveats: labels are **derived from the Ip current-quench** (a heuristic, not physicist-verified);
  `n1_rms` is a broadband Mirnov fluctuation RMS (a low-n MHD-activity proxy), not a
  toroidally-decomposed n=1 amplitude. The features are the extracted, model-ready form of the raw
  FAIR-MAST signals.

## Loading

```python
from kronos_quantum import data
flux = data.cgyro_flux_map_final()      # DataFrame, 16 x 7
X, y, ids = data.mast_features()        # X[591,13], y[591], shot ids
```

Override the data directory with `KRONOS_QUANTUM_DATA=/path/to/data`.
