#!/usr/bin/env python3
import run_all as r
def test():
    d = r.compute_results()
    assert "S32.1" in d["predictions"]
    assert "10000" in d["rows"]
if __name__ == "__main__":
    test(); print("ALL G32 TESTS PASSED")
