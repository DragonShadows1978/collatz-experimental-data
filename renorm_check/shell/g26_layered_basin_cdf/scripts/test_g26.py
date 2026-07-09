#!/usr/bin/env python3
import run_all as r
def test():
    d = r.compute_results()
    assert d["predictions"]["S26.4"]["verdict"] in ("CONFIRMED","REFUTED")
    assert float(d["frac"]["0"]) <= float(d["frac"]["100"])
if __name__ == "__main__":
    test(); print("ALL G26 TESTS PASSED")
