#!/usr/bin/env python3
import run_all as r
def test():
    d = r.compute_results()
    assert "S25.1" in d["predictions"]
    assert d["rows"]["1000"]["n_shell"] >= d["rows"]["1000"]["n_spine"]
if __name__ == "__main__":
    test(); print("ALL G25 TESTS PASSED")
