#!/usr/bin/env python3
"""
W6Y-REGIME -- Step 1: validation gates.

Reproduce W6X-MULTI's Reading-B edges for C=11..15 EXACTLY using the
same mx_core.py instrument (imported unmodified, not copied/reinvented)
before doing anything new. Per house rules: gates first.

Also re-verify the C=1..10 one-heartbeat Tier-1 edges under Reading B
(sanity: Reading B must reduce exactly to "end" for m<=53).
"""
from __future__ import annotations

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "w6x_multi"))
import mx_core as mx  # noqa: E402

HERE = Path(__file__).parent

TIER1_EDGES = {1: 4, 2: 7, 3: 9, 4: 12, 5: 14, 6: 16, 7: 19, 8: 21, 9: 24, 10: 26}
W6X_READING_B_EDGES = {11: 57, 12: 63, 13: 68, 14: 71, 15: 79}
W6X_READING_B_DEAD = {11: 58, 12: 64, 13: 69, 14: 72, 15: 80}
W6X_PEAK_LIVE = {11: 234, 12: 435, 13: 750, 14: 1286, 15: 2336}


def check_tier1():
    print("=== GATE A: Tier-1 edges C=1..10, Reading B (m<=53) ===")
    all_ok = True
    for C, edge in TIER1_EDGES.items():
        alive_at = mx.sparse_survival_multi(edge, C, reading="B", want_witness=False)
        dead_at = mx.sparse_survival_multi(edge + 1, C, reading="B", want_witness=False)
        ok = alive_at["alive"] and not dead_at["alive"]
        all_ok &= ok
        print(f"  C={C:2d} edge={edge:3d} alive@edge={alive_at['alive']} "
              f"dead@edge+1={not dead_at['alive']} {'PASS' if ok else 'FAIL'}")
    return all_ok


def check_w6x_reading_b():
    print("\n=== GATE B: W6X-MULTI Reading-B edges C=11..15, reproduced exactly ===")
    all_ok = True
    results = {}
    for C in range(11, 16):
        edge = W6X_READING_B_EDGES[C]
        dead = W6X_READING_B_DEAD[C]
        alive_at = mx.sparse_survival_multi(edge, C, reading="B", want_witness=True)
        dead_at = mx.sparse_survival_multi(dead, C, reading="B", want_witness=False)
        peak = alive_at["peak_live_states"]
        peak_ok = peak == W6X_PEAK_LIVE[C]
        ok = alive_at["alive"] and not dead_at["alive"] and peak_ok
        all_ok &= ok
        witness_verify = None
        if alive_at["witness"] is not None:
            letters = mx.letters_for(edge, "B")
            witness_verify = mx.verify_witness_exact(alive_at["witness"], C, letters)
        results[C] = {
            "edge": edge, "alive_at_edge": alive_at["alive"],
            "dead_at_edge_plus_1": not dead_at["alive"],
            "peak_live": peak, "peak_expected": W6X_PEAK_LIVE[C], "peak_ok": peak_ok,
            "witness_n0": witness_verify["start_integer"] if witness_verify else None,
            "witness_all_ok": witness_verify["all_ok"] if witness_verify else None,
        }
        print(f"  C={C:2d} edge={edge:3d} alive={alive_at['alive']} "
              f"dead@+1={not dead_at['alive']} peak={peak} (expect {W6X_PEAK_LIVE[C]}) "
              f"witness_n0={results[C]['witness_n0']} witness_ok={results[C]['witness_all_ok']} "
              f"{'PASS' if ok and results[C]['witness_all_ok'] else 'FAIL'}")
    return all_ok, results


def check_c11_saturation_through_53():
    print("\n=== GATE C: C=11 alive through entire one-heartbeat window (m=1..53) ===")
    all_alive = True
    peaks = []
    for m in range(1, 54):
        r = mx.sparse_survival_multi(m, 11, reading="B", want_witness=False)
        all_alive &= r["alive"]
        peaks.append(r["peak_live_states"])
    stabilized = peaks[18:53] == [234] * (53 - 19 + 1)  # m=19..53 inclusive -> index 18..52
    print(f"  all alive m=1..53: {all_alive}; peak at m=53: {peaks[-1]} (expect 234); "
          f"stabilizes at 234 from m=19: {stabilized}")
    return all_alive and peaks[-1] == 234


def main():
    ok1 = check_tier1()
    ok2, results_b = check_w6x_reading_b()
    ok3 = check_c11_saturation_through_53()
    all_pass = ok1 and ok2 and ok3
    print(f"\n=== OVERALL: {'ALL GATES PASS' if all_pass else 'GATE FAILURE -- STOP'} ===")
    out = {"tier1_pass": ok1, "w6x_reading_b_pass": ok2, "c11_saturation_pass": ok3,
           "all_pass": all_pass, "reading_b_detail": results_b}
    (HERE / "step1_validation_gates.json").write_text(json.dumps(out, indent=2))
    if not all_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()
