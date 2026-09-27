"""Read-only loaders for the runnable data subset bundled with this repo.

Two small, real datasets are enough to run every quantum code here:

  * `data/cgyro_a1e_flux_map.csv`      -- the completed 16/16 CGYRO A1e nonlinear
    kinetic-electron turbulence flux map (representative fidelity, reduced electron
    mass mu=400).  Used by KTENSOR (low-rank ROM) and available to the others.
    Full CGYRO campaign: Zenodo DOI 10.5281/zenodo.22136279.

  * `data/mast_disruption_features.csv` -- physics features for 591 real MAST shots
    (FAIR-MAST), a fixed 50 ms pre-event window; labels DERIVED from the Ip
    current-quench (heuristic, not physicist-verified).  Used by KQERN.

The circuit-based codes (KQUBIT, KQOPT, KDYN, KSENSE, KQROSS, KMIT, KLINQ) build
their own problems and need no external data.

The `$KRONOS_QUANTUM_DATA` environment variable overrides the data directory.
"""
from __future__ import annotations

import os
from pathlib import Path

_DEFAULT = Path(__file__).resolve().parent.parent / "data"
DATA_ROOT = Path(os.environ.get("KRONOS_QUANTUM_DATA", _DEFAULT))

# feature columns in the order the codes expect (KQERN uses ip_mean, beta_n, li, q95)
FEATURES = ("ip_mean_MA", "ip_std", "ip_slope", "ip_range", "ne_mean",
            "greenwald_proxy", "beta_n", "li", "q95",
            "n1_rms_mean", "n1_rms_slope", "prad_mean", "prad_slope")


def cgyro_flux_map_final():
    """The complete 16/16 CGYRO A1e flux map (mu=400 representative) as a DataFrame
    with columns a_LT, shear, Q_i, Q_e, Q_tot, verdict, source."""
    import pandas as pd
    return pd.read_csv(DATA_ROOT / "cgyro_a1e_flux_map.csv")


def mast_features():
    """Real MAST disruption features -> (X[591,13], y[591], shot_ids[591]).
    Labels heuristic (Ip current-quench derived); see the data note."""
    import numpy as np
    import pandas as pd
    df = pd.read_csv(DATA_ROOT / "mast_disruption_features.csv")
    y = df["disruptive"].to_numpy(int)
    ids = df["shot_id"].to_numpy(int)
    X = df[list(FEATURES)].to_numpy(float)
    return X, y, ids
