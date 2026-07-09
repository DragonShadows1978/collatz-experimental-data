#!/usr/bin/env python3
import run_all as r
def test():
    d = r.compute_results()
    assert d["predictions"]["S17.3"]["verdict"]=="CONFIRMED"
if __name__=="__main__":
    test(); print("ALL G17 TESTS PASSED")
