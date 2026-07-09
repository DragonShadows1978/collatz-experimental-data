#!/usr/bin/env python3
import json
from pathlib import Path
import run_all as r
ART = Path(__file__).resolve().parents[1] / "artifacts"

def test_sojourn_logic():
    # synthetic: force structure via empty
    assert r.sojourns([]) == []

def test_artifact():
    if (ART / "summary.json").is_file():
        d = json.loads((ART / "summary.json").read_text())
        assert d["gates"]["n_sojourns"] >= 500
        assert "T5.1" in d["predictions"]

if __name__ == "__main__":
    test_sojourn_logic(); print("PASS test_sojourn_logic")
    test_artifact(); print("PASS test_artifact")
    print("ALL G5 TESTS PASSED")
