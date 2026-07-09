#!/usr/bin/env python3
"""Unit tests driving shipped E3 code (no hard-coded reimplementation of ΔM)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import run_e3

TRACK = Path(__file__).resolve().parents[1]
ART = TRACK / "artifacts"


def test_load_edges_monotone_and_gates():
    edges, sources = run_e3.load_edges()
    assert min(edges) == 1 and max(edges) == 31
    assert len(edges) == 31
    # W7B validation gate
    assert edges[16] == 93
    assert edges[23] == 163
    assert edges[26] == 205
    # W7B genuine-death append
    assert edges[27] == 208
    assert edges[31] == 284
    assert len(sources) >= 2


def test_compute_delta_matches_consecutive_M():
    edges, _ = run_e3.load_edges()
    rows = run_e3.compute_delta_rows(edges)
    by_c = {r["C"]: r for r in rows}
    # Hand re-derive two consecutive rows from edge table
    assert by_c[28]["delta_M"] == edges[28] - edges[27] == 55
    assert by_c[31]["delta_M"] == edges[31] - edges[30] == 2
    assert by_c[16]["delta_M"] == edges[16] - edges[15] == 14
    # Every delta equals M(C)-M(C-1)
    for c in range(2, max(edges) + 1):
        assert by_c[c]["delta_M"] == edges[c] - edges[c - 1]
        assert by_c[c]["M"] == edges[c]


def test_p31_scores_real_deltas():
    edges, _ = run_e3.load_edges()
    rows = run_e3.compute_delta_rows(edges)
    p = run_e3.score_p31(rows)
    assert p["verdict"] in ("CONFIRMED", "REFUTED", "INCONCLUSIVE")
    assert p["n_deltas"] == 30  # C=2..31
    assert "deltas" in p and len(p["deltas"]) == 30
    assert p["n_small_le3"] + p["n_large_gt3"] == 30


def test_main_writes_artifacts():
    """Drive the real entry point; require non-empty CSV + summary JSON."""
    rc = run_e3.main()
    assert rc == 0
    csv_path = ART / "e3_delta_M.csv"
    sum_path = ART / "e3_summary.json"
    assert csv_path.is_file() and csv_path.stat().st_size > 0
    assert sum_path.is_file() and sum_path.stat().st_size > 0
    data = json.loads(sum_path.read_text())
    assert "predictions" in data and "P3.1" in data["predictions"]
    v = data["predictions"]["P3.1"]["verdict"]
    assert v in ("CONFIRMED", "REFUTED", "INCONCLUSIVE")
    # no wall rows — only genuine edges C=1..31
    edges = {int(k): v for k, v in data["edges"].items()}
    assert set(edges) == set(range(1, 32))
    # ΔM arithmetic in summary matches
    for row in data["delta_rows"]:
        if row["delta_M"] == "" or row["delta_M"] is None:
            continue
        c = row["C"]
        assert row["delta_M"] == edges[c] - edges[c - 1]


if __name__ == "__main__":
    test_load_edges_monotone_and_gates()
    print("PASS test_load_edges_monotone_and_gates")
    test_compute_delta_matches_consecutive_M()
    print("PASS test_compute_delta_matches_consecutive_M")
    test_p31_scores_real_deltas()
    print("PASS test_p31_scores_real_deltas")
    test_main_writes_artifacts()
    print("PASS test_main_writes_artifacts")
    print("ALL E3 TESTS PASSED")
