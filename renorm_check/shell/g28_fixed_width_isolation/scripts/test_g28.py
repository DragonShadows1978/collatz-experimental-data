#!/usr/bin/env python3
import run_all as r
def test():
    d = r.compute_results()
    assert "S28.1" in d["predictions"]
    assert d["gates"]["W"] == 1000
if __name__ == "__main__":
    test(); print("ALL G28 TESTS PASSED")
