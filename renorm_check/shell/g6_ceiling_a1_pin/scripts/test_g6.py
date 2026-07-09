#!/usr/bin/env python3
import json
from pathlib import Path
ART = Path(__file__).resolve().parents[1]/"artifacts"
def test():
    d=json.loads((ART/"summary.json").read_text())
    assert d["gates"]["n_ceil_drop"] >= 200
    assert d["predictions"]["T6.3"]["verdict"] == "CONFIRMED"
if __name__=="__main__":
    test(); print("ALL G6 TESTS PASSED")
