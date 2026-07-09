#!/usr/bin/env python3
import run_all as r
def test():
    d = r.compute_results()
    assert d["predictions"]["S16.1"]["verdict"]=="CONFIRMED"
    assert d["predictions"]["S16.4"]["verdict"]=="CONFIRMED"
if __name__=="__main__":
    test(); print("ALL G16 TESTS PASSED")
