#!/usr/bin/env python3
import json
from pathlib import Path
def test():
    d=json.loads((Path(__file__).resolve().parents[1]/"artifacts"/"summary.json").read_text())
    assert d["predictions"]["U14.4"]["verdict"]=="CONFIRMED"
    assert d["gates"]["n_odds"] == 50000
if __name__=="__main__":
    test(); print("ALL G14 TESTS PASSED")
