#!/usr/bin/env python3
"""
Validation gate for wy_core.py's incremental walker: it duplicates the
per-layer loop body from mx_core.py (for performance -- continuous walk
instead of O(m) restarts), so it must be independently cross-checked
against mx_core.sparse_survival_multi at every m, not just at block
boundaries, before being trusted for new territory (C=16..26).
"""
from __future__ import annotations
import sys, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "w6x_multi"))
import mx_core as mx  # noqa: E402
import wy_core as wy  # noqa: E402

HERE = Path(__file__).parent


def cross_check(C, m_max):
    """Compare wy_core.find_edge_for_C's per-m alive/dead + live_count
    against mx_core.sparse_survival_multi at every m, for a C small
    enough that mx_core's restart-per-m approach is still cheap."""
    r = wy.find_edge_for_C(C, m_max=m_max, verbose=False)
    mismatches = []
    count_mismatches = []
    for m in range(1, m_max + 1):
        ref = mx.sparse_survival_multi(m, C, reading="B", want_witness=False)
        got = r["records"].get(m)
        if got is None:
            mismatches.append((m, "MISSING", ref["alive"]))
            continue
        if got["alive"] != ref["alive"]:
            mismatches.append((m, got["alive"], ref["alive"]))
        ref_count = ref["final_live_states"] if ref["wall"] is None else None
        if ref_count is not None and got["live_count"] != ref_count:
            count_mismatches.append((m, got["live_count"], ref_count))
    return mismatches, count_mismatches, r


W6X_PEAK_LIVE = {11: 234, 12: 435, 13: 750, 14: 1286, 15: 2336}


def main():
    all_ok = True
    # Test at C=11..15 (known W6X edges, cheap) and C=1..10 (Tier-1)
    for C in list(range(1, 16)):
        m_max = 60 if C <= 15 else 30
        mism, cmism, r = cross_check(C, m_max)
        ok = not mism and not cmism
        all_ok &= ok
        print(f"C={C:2d} m_max={m_max}: alive/dead mismatches={len(mism)} "
              f"count mismatches={len(cmism)} {'PASS' if ok else 'FAIL'}", flush=True)
        if mism:
            print(f"   sample alive/dead mismatches: {mism[:5]}")
        if cmism:
            print(f"   sample count mismatches: {cmism[:5]}")

    print("\n=== Peak live-set cross-check at m=53 (known W6X-MULTI values) ===", flush=True)
    for C in range(11, 16):
        r53 = wy.find_edge_for_C(C, m_max=53, verbose=False)
        expected = W6X_PEAK_LIVE[C]
        ok = r53["peak_live"] == expected
        all_ok &= ok
        print(f"C={C}: wy peak={r53['peak_live']} expected={expected} {'PASS' if ok else 'FAIL'}", flush=True)

    print(f"\n=== wy_core cross-check vs mx_core: {'ALL PASS' if all_ok else 'FAILURE'} ===")
    if not all_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
