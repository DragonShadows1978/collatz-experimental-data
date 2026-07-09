#!/usr/bin/env python3
"""Unit tests driving shipped G2 core + re-run entry points lightly."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import g2_core as core

ART = Path(__file__).resolve().parents[1] / "artifacts"


def test_a1_lemma():
    for x in range(1, 5001, 2):
        assert core.a1_iff_3_mod_4(x)


def test_pure_a1_closed_form():
    for L in range(1, 20):
        c = core.pure_a1_cylinder(L)
        assert c.nonempty
        assert c.modulus == 1 << (L + 1)
        assert c.residue == c.modulus - 1
        assert c.min_positive_odd == c.modulus - 1
        assert core.realizes_word(c.min_positive_odd, tuple(1 for _ in range(L)))
        # L+1-st step of all-1s from min_x may fail (not required)


def test_predicts_a():
    for x in [3, 7, 15, 31, 27, 41, 1000003]:
        if x % 2 == 0:
            continue
        for j in (4, 6, 10):
            assert core.predicts_a_matches(x, j)


def test_cylinder_word_matches_pure():
    for L in (1, 2, 3, 5, 8):
        w = tuple(1 for _ in range(L))
        g = core.cylinder_for_word(w, max_bits=L + 6)
        p = core.pure_a1_cylinder(L)
        assert g.nonempty and p.nonempty
        assert core.realizes_word(p.min_positive_odd, w)
        # general engine finds some realizing x
        assert g.min_positive_odd is not None
        assert core.realizes_word(g.min_positive_odd, w)


def test_climb_run_extraction():
    steps = core.walk_orbit(80049391, max_steps=5000)
    ups = [s for s in steps if s["upcrossing"]]
    assert ups and all(s["a"] == 1 for s in ups)
    runs = core.extract_climb_runs(steps, 80049391, "test")
    assert runs
    assert all(r["L"] >= 1 for r in runs)


def test_artifacts_if_present():
    """If full runners have been executed, validate artifact shape."""
    e1 = ART / "e1_summary.json"
    if e1.is_file():
        d = json.loads(e1.read_text())
        assert d["gates"]["n_runs"] >= 100
        assert d["gates"]["a1_upcrossing_rate"] >= 0.99
        assert "Q1.1" in d["predictions"]
    e2 = ART / "e2_summary.json"
    if e2.is_file():
        d = json.loads(e2.read_text())
        assert d["gates"]["E2-G1"] == "PASS"
        rows = d["rows"]
        assert rows[0]["residue"] == 3 and rows[0]["modulus"] == 4
        assert all(r["mod_bits"] >= r["L"] for r in rows)
    e3 = ART / "e3_summary.json"
    if e3.is_file():
        d = json.loads(e3.read_text())
        assert d["gates"]["n_words"] >= 10


if __name__ == "__main__":
    test_a1_lemma()
    print("PASS test_a1_lemma")
    test_pure_a1_closed_form()
    print("PASS test_pure_a1_closed_form")
    test_predicts_a()
    print("PASS test_predicts_a")
    test_cylinder_word_matches_pure()
    print("PASS test_cylinder_word_matches_pure")
    test_climb_run_extraction()
    print("PASS test_climb_run_extraction")
    test_artifacts_if_present()
    print("PASS test_artifacts_if_present")
    print("ALL G2 UNIT TESTS PASSED")
