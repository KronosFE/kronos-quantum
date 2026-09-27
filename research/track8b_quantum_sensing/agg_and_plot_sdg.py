"""
agg_and_plot_sdg.py — aggregate sdg_raw_perseed.csv into the deliverable CSV and figure.

Reads:  sdg_raw_perseed.csv, sdg_run_meta.json
Writes: sensing_to_disruption_gain.csv   (headline table, both B-mode scenarios)
        F_sensing_to_disruption.png       (deliverable figure)
"""
import os, json
import numpy as np, pandas as pd

TR = os.path.dirname(os.path.abspath(__file__))
raw = pd.read_csv(os.path.join(TR, "sdg_raw_perseed.csv"))
meta = json.load(open(os.path.join(TR, "sdg_run_meta.json")))

CONV = "conventional_inductive_coil"
ORDER = [CONV, "NV_diamond_ensemble", "SQUID", "SERF_atomic"]
PRETTY = {CONV: "Inductive coil\n(conventional)", "NV_diamond_ensemble": "NV-diamond",
          "SQUID": "SQUID", "SERF_atomic": "SERF atomic"}

# ---------- aggregate the per-class scenarios into the deliverable table ----------
scen_rows = []
for scen in ["headline_realistic_1mT", "weak_field_stress_1uT"]:
    sub = raw[raw.scenario == scen]
    g = (sub.groupby(["sensor_class", "b_mode_scale_T", "noise_floor_T_rtHz"])
            .agg(AUC=("auc", "mean"), AUC_std=("auc", "std"),
                 median_warning_ms=("warn_median_ms", "mean"),
                 median_warning_ms_std=("warn_median_ms", "std"),
                 FAR=("far", "mean"), FAR_std=("far", "std"),
                 tpr=("tpr", "mean"), n_seeds=("seed", "nunique")).reset_index())
    conv_auc = g.loc[g.sensor_class == CONV, "AUC"].values[0]
    conv_warn = g.loc[g.sensor_class == CONV, "median_warning_ms"].values[0]
    g["delta_AUC_vs_conventional"] = g["AUC"] - conv_auc
    g["delta_warning_ms_vs_conventional"] = g["median_warning_ms"] - conv_warn
    g["scenario"] = scen
    scen_rows.append(g)
tab = pd.concat(scen_rows, ignore_index=True)
tab["provenance"] = "SIM + TRL-SURVEY"
# order columns per deliverable spec (+ dispersion & context)
cols = ["scenario", "sensor_class", "noise_floor_T_rtHz", "b_mode_scale_T", "sigma_note",
        "AUC", "AUC_std", "median_warning_ms", "median_warning_ms_std", "FAR", "FAR_std",
        "tpr", "delta_AUC_vs_conventional", "delta_warning_ms_vs_conventional",
        "n_seeds", "provenance"]
tab["sigma_note"] = "sigma_mag=quad(intrinsic_floor,sensor); floor=%.3f" % meta["intrinsic_mag_floor"]
tab = tab.sort_values(["scenario", "sensor_class"]).reindex(columns=cols)
tab.to_csv(os.path.join(TR, "sensing_to_disruption_gain.csv"), index=False)
print("=== sensing_to_disruption_gain.csv ===")
print(tab.to_string(index=False))

# ---------- sensitivity-sweep aggregate (for the figure curve) ----------
sw = raw[raw.scenario == "sensitivity_sweep"]
swg = (sw.groupby("sigma_mag").agg(AUC=("auc", "mean"), AUC_std=("auc", "std"),
        warn=("warn_median_ms", "mean"), warn_std=("warn_median_ms", "std"),
        far=("far", "mean"), far_std=("far", "std")).reset_index().sort_values("sigma_mag"))
print("\n=== sensitivity_sweep (AUC vs magnetics-channel sigma) ===")
print(swg.to_string(index=False))
swg.to_csv(os.path.join(TR, "sdg_sensitivity_sweep.csv"), index=False)
