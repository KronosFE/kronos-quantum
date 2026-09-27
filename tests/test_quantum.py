"""Contract + honesty tests for the Kronos Quantum codes. Fast; runs on the free
local simulator (no network, no hardware)."""
import warnings
import numpy as np
import pytest

warnings.filterwarnings("ignore")
import kronos_quantum as Q
from kronos_quantum.base import Prediction

QUANTUM = ["KQUBIT", "KQROSS", "KSENSE", "KTENSOR", "KQERN", "KQOPT", "KDYN", "KMIT", "KLINQ"]


def test_registry_has_nine_codes():
    assert set(Q.list_codes()) == set(QUANTUM)
    assert len(Q.SURROGATES) == 9


def test_every_code_has_provenance_and_retired_by():
    for name in Q.list_codes():
        c = Q.get(name).card()
        assert c["status"] in ("BUILT", "PARTIAL", "ROADMAP")
        assert c["retired_by"], f"{name} missing retired_by"


def test_contract_returns_prediction():
    inputs = {"KSENSE": 4, "KTENSOR": 2, "KDYN": 16, "KMIT": 0.04}
    for name in Q.list_codes():
        p = Q.run(name, inputs.get(name))
        assert isinstance(p, Prediction)
        y, unc, indom = p.as_tuple()
        assert isinstance(indom, bool)


def test_honest_no_advantage_framing():
    # every quantum card states the honest post-~2036 timeline
    for name in Q.list_codes():
        note = Q.get(name).card()["note"]
        assert "2036" in note, f"{name} card note missing the honest ~2036 framing"


def test_backend_is_free_local_sim_by_default():
    from kronos_quantum import quantum_backend as qc
    bn = qc.backend_note()
    assert bn["ran_on_real_hardware"] is False
    assert "2036" in bn["honest_timeline"]
    assert "KODEX_QC_BACKEND=ibm" in bn["how_to_use_real_qc"]


def test_data_loaders():
    from kronos_quantum import data
    m = data.cgyro_flux_map_final()
    assert m.shape[0] == 16 and {"a_LT", "shear", "Q_tot"}.issubset(m.columns)
    X, y, ids = data.mast_features()
    assert X.shape == (591, 13) and set(np.unique(y)) == {0, 1}


def test_kqubit_recovers_h2_ground_state():
    # VQE on the free local simulator recovers the exact H2 ground state
    b = Q.get("KQUBIT").benchmark()["live_vqe"]
    assert b["recovery_mHa"] < 1.6          # chemical accuracy on the noiseless sim


def test_ktensor_flux_not_strongly_low_rank():
    # the honest measured result: the CGYRO flux DB is only modestly compressible
    r = Q.get("KTENSOR").benchmark()["live_low_rank_rom"]["full_16pt_map"]
    assert r["effective_rank"] > 2.0        # not a trivial rank-1/2 collapse
