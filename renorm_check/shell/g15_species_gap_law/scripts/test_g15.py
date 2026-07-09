#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "species_spacing_common"))
from species_spacing import gap_k, x_k, verify_gap_identity
import run_all as r

def test_identity():
    assert verify_gap_identity(30)
    for k in (1, 5, 10, 20):
        assert x_k(k+1) - x_k(k) == gap_k(k) == 4**k

def test_compute():
    d = r.compute_results()
    assert d["predictions"]["S15.1"]["verdict"] == "CONFIRMED"
    assert "S15.4" in d["predictions"]

if __name__ == "__main__":
    test_identity(); print("PASS identity")
    test_compute(); print("PASS compute")
    print("ALL G15 TESTS PASSED")
