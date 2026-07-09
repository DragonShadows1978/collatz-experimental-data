#!/usr/bin/env python3
import run_all as r
def test():
    d = r.compute_results()
    assert float(d["frac"]["0"]) <= float(d["frac"]["10"])
if __name__ == "__main__":
    test(); print("ALL G31 TESTS PASSED")
