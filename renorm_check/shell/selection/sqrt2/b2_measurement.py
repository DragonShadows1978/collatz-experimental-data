#!/usr/bin/env python3
"""
W6C Design B, B2 -- D_sqrt2(m) measurement, m=2..16, per
W6C_SELECTION_ORDER.md's margin rule: corridor wide enough that shell
depth stays >= 3 below the floor; report depth and margin EVERY row;
if margin < 2, widen C and rerun that row.

Starts each row at C_START=12 (per the work order) and escalates C for
that row alone if the margin rule is violated. Progress logging is
per-step (via run_heartbeat_generic's own printed nothing -- we log
per-row here since each row at m<=14 completes in well under a second;
for m=15/16 rows we additionally print elapsed wall time so a stall
during a possible background run is visible).

8GB memory guard: reports estimated peak RSS-relevant footprint before
each row (bool arrays for C+1 levels, current+next; int32 permutation
cache grows unboundedly across rows within one process since
run_heartbeat_generic's _PERM_CACHE is module-level and keyed by
(a, modulus) -- modulus changes every row, so old-modulus permutations
from smaller m are dead weight. This script clears the cache between
rows to bound memory.)

Usage:
  python3 b2_measurement.py 2>&1 | tee b2_measurement.log
  (or via nohup/background for the m=15/16 rows if they run long)
"""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "shell" / "toy_word"))

from sqrt2_automaton import run_heartbeat_generic, credit_sqrt2  # noqa: E402
import toy_automaton as _toy_mod  # noqa: E402

M_MIN, M_MAX = 2, 16
C_START = 12
MAX_STATES_GUARD = 400_000_000  # matches toy_automaton.py default; ~ (C+1)*3^m states


def get_rss_mb() -> float:
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024.0
    except Exception:
        pass
    return -1.0


def measure_row(m: int, C: int):
    """Run one (C, m) row; return (D_val, shell_depth, margin)."""
    modulus = 3 ** m
    live_by_d, history_sizes = run_heartbeat_generic(
        C, m, credit_sqrt2, steps=53, max_states_guard=MAX_STATES_GUARD
    )
    target_residue = 1 % modulus
    alive_depths = [C - d for d in range(C + 1) if live_by_d[d][target_residue]]
    D_val = min(alive_depths) if alive_depths else None

    # shell depth: max ceiling-distance (C-d) among (d,r) with r%3!=0 dead
    import numpy as np
    shell_depth = None
    for d in range(0, C + 1):
        arr = live_by_d[d]
        dead_mask = ~arr
        if not dead_mask.any():
            continue
        idx = np.nonzero(dead_mask)[0]
        nonmult3 = idx[idx % 3 != 0]
        if nonmult3.size > 0:
            shell_depth = C - d
            break
    margin = (C - shell_depth) if shell_depth is not None else C
    return D_val, shell_depth, margin, history_sizes


def row_with_margin_rule(m: int, C0: int = C_START, margin_floor: int = 2,
                          max_C: int = 22):
    """Run row m starting at C0; if margin < margin_floor, widen C and
    rerun THIS row (per the work order's margin rule). Clears the
    permutation cache between attempts to bound memory across escalations."""
    C = C0
    attempts = []
    while True:
        t0 = time.time()
        try:
            D_val, shell_depth, margin, hist = measure_row(m, C)
        except ValueError as e:
            print(f"    m={m} C={C}: STATE-SPACE GUARD HIT: {e}", flush=True)
            attempts.append({"C": C, "D": None, "shell_depth": None,
                              "margin": None, "wall_s": time.time() - t0,
                              "note": "guard_hit"})
            _toy_mod._PERM_CACHE.clear()
            return None, None, None, attempts
        elapsed = time.time() - t0
        rss = get_rss_mb()
        print(f"    m={m:>2} C={C:>2}: D={D_val} shell_depth={shell_depth} "
              f"margin={margin} elapsed={elapsed:.2f}s RSS={rss:.0f}MB", flush=True)
        attempts.append({"C": C, "D": D_val, "shell_depth": shell_depth,
                          "margin": margin, "wall_s": elapsed, "note": ""})
        _toy_mod._PERM_CACHE.clear()  # bound memory across escalations/rows
        if margin is not None and margin >= margin_floor:
            return D_val, shell_depth, margin, attempts
        if C >= max_C:
            print(f"    m={m}: margin rule NOT satisfied even at C={C} "
                  f"(max_C guard) -- reporting last attempt honestly, wall hit.",
                  flush=True)
            return D_val, shell_depth, margin, attempts
        C_new = C + 2
        print(f"    m={m}: margin={margin} < {margin_floor}, widening C {C} -> {C_new} and rerunning row",
              flush=True)
        C = C_new


def main():
    t_start = time.time()
    print("W6C Design B, B2 -- D_sqrt2(m) measurement, m=2..16", flush=True)
    print(f"start: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print(f"Margin rule: start C={C_START}, require margin (C - shell_depth) >= 2, "
          "widen by +2 and rerun row if violated.", flush=True)

    rows = []
    for m in range(M_MIN, M_MAX + 1):
        print(f"\n=== m={m} ===", flush=True)
        t_row0 = time.time()
        D_val, shell_depth, margin, attempts = row_with_margin_rule(m)
        row_elapsed = time.time() - t_row0
        final_C = attempts[-1]["C"]
        rows.append({
            "m": m, "D_sqrt2": D_val, "C_final": final_C,
            "shell_depth": shell_depth, "margin": margin,
            "n_attempts": len(attempts), "row_wall_s": round(row_elapsed, 3),
        })
        print(f"    m={m} FINAL: D_sqrt2={D_val} C={final_C} "
              f"shell_depth={shell_depth} margin={margin} "
              f"row_wall={row_elapsed:.2f}s", flush=True)

    csv_path = Path(__file__).parent / "D_sqrt2_table.csv"
    with open(csv_path, "w", newline="") as f:
        fieldnames = ["m", "D_sqrt2", "C_final", "shell_depth", "margin",
                      "n_attempts", "row_wall_s"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nWrote {csv_path}", flush=True)

    total_elapsed = time.time() - t_start
    print(f"\nTotal elapsed: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)", flush=True)
    print(f"end: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)


if __name__ == "__main__":
    main()
