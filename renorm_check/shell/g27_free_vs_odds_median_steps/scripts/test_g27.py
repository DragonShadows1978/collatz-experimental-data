#!/usr/bin/env python3
import run_all as r
def test():
    d = r.compute_results()
    assert "S27.1" in d["predictions"]
    assert d["med_odds"] is not None
if __name__ == "__main__":
    test(); print("ALL G27 TESTS PASSED")
