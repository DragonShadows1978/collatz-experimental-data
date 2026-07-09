#!/usr/bin/env python3
import run_all as r
def test():
    d = r.compute_results()
    assert d["predictions"]["S19.3"]["verdict"]=="CONFIRMED"
if __name__=="__main__":
    test(); print("ALL G19 TESTS PASSED")
