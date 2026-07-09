#!/usr/bin/env python3
import json
from pathlib import Path
import run_all as r
def test_multiset():
    ms = r.build_multiset({"1": 2, "2": 1}, seed=0)
    assert sorted(ms) == [1, 1, 2]
    assert len(ms) == 3
def test_art():
    p=Path(__file__).resolve().parents[1]/"artifacts"/"summary.json"
    d=json.loads(p.read_text())
    assert d["predictions"]["T9.2"]["verdict"] in ("CONFIRMED","REFUTED")
    assert d["gates"]["multiset_size"] > 0
if __name__=="__main__":
    test_multiset(); print("PASS test_multiset")
    test_art(); print("PASS test_art")
    print("ALL G9 TESTS PASSED")
