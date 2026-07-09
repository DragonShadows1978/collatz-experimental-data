#!/usr/bin/env python3
import json
from pathlib import Path
def test():
    d=json.loads((Path(__file__).resolve().parents[1]/"artifacts"/"summary.json").read_text())
    assert d["gates"]["n_with_up"] >= 50
    assert d["predictions"]["U11.1"]["verdict"]=="CONFIRMED"
if __name__=="__main__":
    test(); print("ALL G11 TESTS PASSED")
