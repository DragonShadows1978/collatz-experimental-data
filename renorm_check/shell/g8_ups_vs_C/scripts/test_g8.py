#!/usr/bin/env python3
import json
from pathlib import Path
def test():
    d=json.loads((Path(__file__).resolve().parents[1]/"artifacts"/"summary.json").read_text())
    assert d["gates"]["G1"]=="PASS"
    assert d["predictions"]["T8.1"]["verdict"] in ("CONFIRMED","REFUTED")
if __name__=="__main__":
    test(); print("ALL G8 TESTS PASSED")
