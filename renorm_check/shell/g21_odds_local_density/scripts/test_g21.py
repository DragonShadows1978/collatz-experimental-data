#!/usr/bin/env python3
import run_all as r
def test():
    d = r.compute_results()
    assert "S21.1" in d["predictions"]
if __name__=="__main__":
    test(); print("ALL G21 TESTS PASSED")
