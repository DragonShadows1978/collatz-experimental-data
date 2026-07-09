#!/usr/bin/env python3
"""Tests for G12 — must import *this* track's run_all, not g10's."""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ART = HERE.parent / "artifacts"
G10 = HERE.parents[1] / "g10_species_vs_climb" / "scripts"
sys.path.insert(0, str(G10))
from species_orbit import steps_to_species  # noqa: E402

# Load local run_all by path (avoid sys.path shadowing by g10/run_all.py)
_spec = importlib.util.spec_from_file_location("g12_run_all", HERE / "run_all.py")
g12_run = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g12_run)


def test_scorer_source_uses_row_L():
    src = (HERE / "run_all.py").read_text()
    assert 'r["L"]' in src
    assert "r[\"steps_to_species\"] >= L for r" not in src


def test_data_steps_ge_L():
    for L in range(1, 41):
        x = (1 << (L + 1)) - 1
        st = steps_to_species(x, 100000)
        assert st["hit"] and st["steps_to_species"] >= L, (L, st)


def test_summary_u122_confirmed():
    assert g12_run.main() == 0
    d = json.loads((ART / "summary.json").read_text())
    assert "U12.2" in d["predictions"], "must be G12 summary not another track"
    assert d["predictions"]["U12.1"]["verdict"] == "CONFIRMED"
    assert d["predictions"]["U12.2"]["verdict"] == "CONFIRMED"
    assert d["predictions"]["U12.2"]["n_ge_L"] == 40
    assert d["predictions"]["U12.2"]["min_steps_minus_L"] >= 0
    assert d["gates"]["n"] == 40


if __name__ == "__main__":
    test_scorer_source_uses_row_L()
    print("PASS test_scorer_source_uses_row_L")
    test_data_steps_ge_L()
    print("PASS test_data_steps_ge_L")
    test_summary_u122_confirmed()
    print("PASS test_summary_u122_confirmed")
    print("ALL G12 TESTS PASSED")
