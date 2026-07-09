#!/usr/bin/env python3
import json
from pathlib import Path
import g4_core as g

ART = Path(__file__).resolve().parents[1] / "artifacts"


def test_algebra():
    r = g.prove_U_cases()
    assert r["all_ok"]


def test_thm_on_27():
    steps = g.walk_with_C_before(27, 500)
    for s in steps:
        if s["upcrossing"]:
            assert s["thm_U"] is True


def test_drop_runs():
    # synthetic
    assert g.drop_runs([2, 2, 1, 2]) == [2, 1]


def test_artifacts():
    if (ART / "summary.json").is_file():
        d = json.loads((ART / "summary.json").read_text())
        assert d["V0"]["S0.1"]["verdict"] in ("CONFIRMED", "REFUTED")


if __name__ == "__main__":
    test_algebra()
    print("PASS test_algebra")
    test_thm_on_27()
    print("PASS test_thm_on_27")
    test_drop_runs()
    print("PASS test_drop_runs")
    test_artifacts()
    print("PASS test_artifacts")
    print("ALL G4 TESTS PASSED")
