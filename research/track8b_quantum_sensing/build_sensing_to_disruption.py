"""
build_sensing_to_disruption.py — Track 8b, FINAL EXPERIMENT E (SECOND downstream task).

QUESTION: does quantum-sensor-grade magnetics (SQUID/SERF/NV noise floors) buy earlier
and/or more reliable DISRUPTION warning versus a conventional inductive-coil noise floor,
when the survey noise levels are injected into the twin disruption feature stream?

This is a bounded PROPAGATION study. It re-uses the Track 4 disruption pipeline VERBATIM
(same twin generator, same causal features, same 3-model ensemble, same FAR-matched
operating point, same >=5 seeds) and changes ONLY the noise on the magnetic pickup
channel (n1_rms = the n=1 Mirnov mode-amplitude signal a magnetometer directly measures).
No Track 4 source file is edited; the magnetics-channel noise is monkeypatched here.

PROVENANCE (LOCKED): SIM (twin propagation) + TRL-SURVEY (noise floors from
quantum_sensing_trl.csv). Kronos has NO operating plant; no quantum sensor has fed data to
any Kronos model. This shows the twin pipeline's SENSITIVITY to a sensor noise model, NOT
that a quantum sensor delivered a disruption warning. Hardware: local CPU (56 cores, no GPU).

NOISE MODEL (every number read off this script into a CSV column):
  sigma_B_phys(class) = noise_floor_T_rtHz * sqrt(BANDWIDTH_HZ)                 [Tesla]
  sigma_sensor_norm   = sigma_B_phys / B_MODE_SCALE_T                          [normalised]
  sigma_mag(class)    = sqrt(INTRINSIC_MAG_FLOOR**2 + sigma_sensor_norm**2)    [normalised]
Rationale for the pieces is stored in the run_meta JSON and the track README.

Outputs:
  sdg_raw_perseed.csv         per (scenario, sigma_mag, seed) AUC/warn/FAR   [backbone]
  (aggregation, headline CSV, crossover CSV and the figure are built by the companion
   aggregation cell / plot script from this raw file so the ~20 min compute runs once.)
"""
import sys, os, json, time
import numpy as np, pandas as pd

TR = os.path.dirname(os.path.abspath(__file__))
T4 = os.path.abspath(os.path.join(TR, "..", "track4_disruption"))
sys.path.insert(0, T4)

import twin_pulses as tp
import features as ft
import run_disruption as rd   # reuse EXACT protocol funcs; __main__ guard => safe to import

# ---------------- noise mapping (all stated, all read into CSV/meta) ----------------
BANDWIDTH_HZ      = 1000.0     # twin sample rate == control-relevant DMS bandwidth
B_MODE_SCALE_T    = 1e-3       # n1_rms=1.0 <-> 1 mT mode field at the sensor (locked/rotating
                               # n=1 precursor amplitude at the wall is ~mT; realistic anchor)
INTRINSIC_MAG_FLOOR = 0.055    # regime-A magnetics fluctuation floor (plasma broadband MHD +
                               # electronics) == the twin's own NOISE['A']; the irreducible
                               # non-sensor noise a PERFECT magnetometer still sees.
MAG_CHANNELS = ("n1_rms",)     # magnetometer directly measures the n=1 Mirnov mode amplitude

SENSORS = [   # (label, noise_floor_T_rtHz) from quantum_sensing_trl.csv
    ("conventional_inductive_coil", 1e-9),
    ("NV_diamond_ensemble",         9e-13),
    ("SQUID",                       1e-15),
    ("SERF_atomic",                 1.6e-16),
]

def sigma_sensor_norm(noise_floor):
    return noise_floor * np.sqrt(BANDWIDTH_HZ) / B_MODE_SCALE_T

def sigma_mag_total(noise_floor, floor=INTRINSIC_MAG_FLOOR):
    return float(np.hypot(floor, sigma_sensor_norm(noise_floor)))

# ---------------- monkeypatch: per-channel magnetics noise ----------------
# generate_pulse() calls tp._add_measurement_noise(sig, regime, rng). We replace it with a
# version that reads module-global _MAG_SIGMA for the magnetic channel(s) and keeps every
# other channel at the twin's intrinsic tp.NOISE[regime]. Dropout behaviour is preserved.
_MAG_SIGMA = INTRINSIC_MAG_FLOOR

def _amn(sig, regime, rng):
    for ch in sig:
        s = _MAG_SIGMA if ch in MAG_CHANNELS else tp.NOISE[regime]
        sig[ch] = sig[ch] + rng.normal(0, s, size=sig[ch].shape)
    if rng.random() < tp.DROPOUT_PROB[regime]:
        ch = rng.choice(list(sig.keys()))
        n = len(sig[ch]); a = rng.integers(0, n - 10); w = rng.integers(3, 12)
        sig[ch][a:a + w] = sig[ch][a]
    return sig

tp._add_measurement_noise = _amn   # install

# ---------------- one pipeline evaluation at a given magnetics-channel sigma ----------------
SEEDS = rd.SEEDS               # [20260726 ... 20260730] — same program seeds
N_TRAIN, N_TEST = 300, 180     # slightly reduced vs Track 4 (400/220) to bound the sweep runtime;
                               # stated in meta. Regime A only (this is a within-machine study).

def eval_one(sig_mag, seed):
    """Train+test the Track-4 ensemble on regime A with n1_rms noise = sig_mag. Returns
    (auc, warn_median_ms, far, tpr, frac_ge30)."""
    global _MAG_SIGMA
    _MAG_SIGMA = sig_mag
    train = tp.make_dataset(N_TRAIN, "A", seed=seed,        disr_frac=0.5, classes=tp.TRAIN_CLASSES)
    test  = tp.make_dataset(N_TEST,  "A", seed=seed + 5000, disr_frac=0.5, classes=tp.TRAIN_CLASSES)
    Xtr, ytr, gtr, Ttr, mtr, _ = ft.build_matrix(train, rd.WARN_HORIZON_MS)
    Xte, yte, gte, Tte, mte, _ = ft.build_matrix(test,  rd.WARN_HORIZON_MS)
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler().fit(Xtr)
    Xtr_s, Xte_s = scaler.transform(Xtr), scaler.transform(Xte)
    models = rd.make_ensemble(seed)
    rd.fit_ensemble(models, Xtr_s, ytr)
    p = rd.predict_ensemble(models, Xte_s)
    auc, _, _ = rd.shot_auc(p, gte, mte)
    thr = rd.pick_threshold_for_far(p, gte, Tte, mte, rd.TARGET_FAR)
    ev = rd.eval_at_threshold(p, gte, Tte, mte, thr)
    return float(auc), ev["warn_median"], ev["far"], ev["tpr"], ev["frac_warned_ge30"]

# two precursor-field scenarios: at what mode-field scale does the sensor noise floor
# stop being swamped by the intrinsic plasma/MHD floor? mT = realistic locked/rotating-mode
# amplitude at the wall; uT = a deliberate weak-field STRESS test to locate the regime where
# quantum sensitivity would begin to matter (and to show it is NOT where disruptions live).
BMODE_SCENARIOS = [
    ("headline_realistic_1mT", 1e-3),   # realistic disruption precursor mode field
    ("weak_field_stress_1uT",  1e-6),   # 1000x weaker: stress test for the sensing floor
]

def sigma_sensor_norm_at(noise_floor, b_mode):
    return noise_floor * np.sqrt(BANDWIDTH_HZ) / b_mode

def sigma_mag_at(noise_floor, b_mode, floor=INTRINSIC_MAG_FLOOR):
    return float(np.hypot(floor, sigma_sensor_norm_at(noise_floor, b_mode)))

def run():
    t0 = time.time()
    rows = []

    # scenario 1+2: 4 sensor classes at each precursor-field scale (sensor noise adds in
    # quadrature to the intrinsic magnetics floor).
    for scen, bmode in BMODE_SCENARIOS:
        for lab, nf in SENSORS:
            ssn = sigma_sensor_norm_at(nf, bmode)
            sig_mag = sigma_mag_at(nf, bmode)
            for seed in SEEDS:
                auc, wm, far, tpr, f30 = eval_one(sig_mag, seed)
                rows.append(dict(scenario=scen, sensor_class=lab, b_mode_scale_T=bmode,
                                 noise_floor_T_rtHz=nf, sigma_sensor_norm=ssn,
                                 sigma_mag=sig_mag, seed=seed, auc=auc, warn_median_ms=wm,
                                 far=far, tpr=tpr, frac_warned_ge30=f30))
            print(f"[{scen} {lab:32s}] sig_sensor={ssn:.3e} sig_mag={sig_mag:.6e}  t={time.time()-t0:.0f}s")

    # scenario 2: SENSITIVITY SWEEP — magnetics-channel noise from tiny to large, to (a) prove
    # the pipeline IS noise-sensitive and (b) locate every sensor class on the curve.
    sweep = np.concatenate([[1e-6], np.logspace(-5, np.log10(0.4), 11)])
    for sig_mag in sweep:
        for seed in SEEDS:
            auc, wm, far, tpr, f30 = eval_one(float(sig_mag), seed)
            rows.append(dict(scenario="sensitivity_sweep", sensor_class="", b_mode_scale_T=np.nan,
                             noise_floor_T_rtHz=np.nan, sigma_sensor_norm=np.nan,
                             sigma_mag=float(sig_mag), seed=seed, auc=auc, warn_median_ms=wm,
                             far=far, tpr=tpr, frac_warned_ge30=f30))
        print(f"[sweep sig_mag={sig_mag:.3e}] t={time.time()-t0:.0f}s")

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(TR, "sdg_raw_perseed.csv"), index=False)

    meta = dict(bandwidth_hz=BANDWIDTH_HZ, b_mode_scenarios=dict(BMODE_SCENARIOS),
                intrinsic_mag_floor=INTRINSIC_MAG_FLOOR, mag_channels=list(MAG_CHANNELS),
                sensors={lab: nf for lab, nf in SENSORS},
                class_sigma_mag={f"{scen}|{lab}": sigma_mag_at(nf, bmode)
                                 for scen, bmode in BMODE_SCENARIOS for lab, nf in SENSORS},
                seeds=SEEDS, n_train=N_TRAIN, n_test=N_TEST,
                warn_horizon_ms=rd.WARN_HORIZON_MS, alarm_k=rd.ALARM_K, target_far=rd.TARGET_FAR,
                hardware="local CPU, 56 cores, no GPU", runtime_s=time.time() - t0,
                provenance="SIM + TRL-SURVEY")
    json.dump(meta, open(os.path.join(TR, "sdg_run_meta.json"), "w"), indent=2)
    print(f"\nDONE {time.time()-t0:.0f}s -> sdg_raw_perseed.csv ({len(df)} rows)")

if __name__ == "__main__":
    run()
