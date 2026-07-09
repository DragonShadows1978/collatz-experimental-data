#!/usr/bin/env python3
import run_all as r
def test():
    d = r.compute_results()
    assert d["taxonomy"]=="C_exact_geometric"
if __name__=="__main__":
    test(); print("ALL G24 TESTS PASSED")
