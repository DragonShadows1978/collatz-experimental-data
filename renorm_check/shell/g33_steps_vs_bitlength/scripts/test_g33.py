#!/usr/bin/env python3
import run_all as r
def test():
    d = r.compute_results()
    assert d["gates"]["n"] > 50
    assert "rho" in d
if __name__ == "__main__":
    test(); print("ALL G33 TESTS PASSED")
