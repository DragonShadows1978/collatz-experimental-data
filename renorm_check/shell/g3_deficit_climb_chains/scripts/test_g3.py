#!/usr/bin/env python3
"""Tests driving shipped G3 core."""
from __future__ import annotations

import json
from pathlib import Path

import g3_core as g3

ART = Path(__file__).resolve().parents[1] / "artifacts"


def test_lemma3():
    assert g3.verify_lemma3()


def test_dual_identity():
    steps = g3.walk_orbit_with_credit(27, 200)
    assert steps and all(s["dual_ok"] for s in steps)


def test_mersenne_a1():
    for L in (1, 5, 10):
        r = g3.mersenne_prefix(L)
        assert r["prefix_all_a1"]


def test_dual_path_a1():
    r = g3.dual_a1_path(4, 0, 0)
    assert "stayed_nonneg" in r and r["L"] == 4


def test_artifacts():
    if (ART / "e1_summary.json").is_file():
        d = json.loads((ART / "e1_summary.json").read_text())
        assert d["gates"]["n_upcrossings"] >= 500
    if (ART / "e3_summary.json").is_file():
        d = json.loads((ART / "e3_summary.json").read_text())
        assert d["gates"]["n_cells"] == 8 * 53 * 11


if __name__ == "__main__":
    test_lemma3()
    print("PASS test_lemma3")
    test_dual_identity()
    print("PASS test_dual_identity")
    test_mersenne_a1()
    print("PASS test_mersenne_a1")
    test_dual_path_a1()
    print("PASS test_dual_path_a1")
    test_artifacts()
    print("PASS test_artifacts")
    print("ALL G3 TESTS PASSED")
