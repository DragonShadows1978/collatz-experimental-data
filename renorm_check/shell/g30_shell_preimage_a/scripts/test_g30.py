#!/usr/bin/env python3
import run_all as r
def test():
    d = r.compute_results()
    assert d["n"] >= 1
if __name__ == "__main__":
    test(); print("ALL G30 TESTS PASSED")
