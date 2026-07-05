#!/usr/bin/env python3
"""
W6V-MEASURE -- main sweep, NEW MEASUREMENT, 2026-07-04.

Genuine per-m sweep for C = 6, 7, 8, 9, 10, 11, ... using
renorm_check/embedding/automaton.py's run_heartbeat(C, m) as the primary
instrument (validated 5/5 against Tier-1 genuine Rust lock3_census edges
1..5 in this same directory's validate_c5.py / validate_c5.log, run fresh
just before this script).

Method per C: walk m = 1, 2, 3, ... calling run_heartbeat(C, m) and testing
whether any terminal state (d, r = 1 mod 3^m) survives one 53-step
heartbeat from the fully-populated start. The measured M_edge(C) is the
largest m for which the terminal set is non-empty (matches shell_probe.py's
P3 / validate_c5.py's edge convention exactly). We do NOT jump straight to
the predicted edge floor(53*(C+1)/22) -- every m below it is actually
walked and checked live, and we stop each C's sweep exactly ONE m past the
first dead m (i.e. the death certificate is "dead at edge+1, and we did not
pay the 3x-more-expensive cost to also check edge+2" for C>=6 -- unlike the
validate_c5.py gate, which affords a deeper 2-3 m confirmation margin at
these much smaller C). This is reported honestly per-C in the record, not
silently assumed.

Resource wall: run_heartbeat allocates (C+1) boolean arrays of length 3^m
(1 byte/element, numpy bool), i.e. total bytes ~= (C+1)*3^m for a SINGLE m
(each m is independent -- no cumulative growth across the sweep, confirmed
by reading automaton.py directly: run_heartbeat(C, m) starts fresh from a
fully-populated array of size 3^m every call). This is the resource wall
this script watches for and stops at -- NOT extrapolated past.

This script:
  - Tracks wall-clock time and RSS (via /proc/self/status) per m.
  - Stops a given C's sweep if projected bytes for the NEXT m would exceed
    RSS_CAP_MB, or if a single C's total wall-clock exceeds TIME_CAP_SEC.
  - Reports the exact death certificate: the m at which terminal survival
    output actually reads False (with the raw per-m alive/dead marker).
  - Does NOT extrapolate or fudge past whatever wall is hit.

Usage: python3 sweep_new_C.py | tee sweep_new_C.log
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "embedding"))

from automaton import M_edge, run_heartbeat  # noqa: E402

RSS_CAP_MB = 8000       # ~8GB single-process RSS wall (task spec)
TIME_CAP_SEC = 20 * 60  # 20 min wall-clock per C (task spec)
GUARD_STATES = 2_500_000_000  # (C+1)*3^m states guard passed to run_heartbeat;
                                # kept well under the RSS_CAP_MB byte budget
                                # (numpy bool = 1 byte/state, so this is also
                                # ~2.5GB just for the live-array allocation,
                                # before intermediate/transient arrays during
                                # the 53-step heartbeat -- observed in
                                # validate_c5.py's C=5 run to run well past
                                # naive (C+1)*3^m due to per-step temporaries)


def get_rss_mb() -> float:
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024.0
    except Exception:
        pass
    return -1.0


def predicted_bytes(C: int, m: int) -> int:
    return (C + 1) * (3 ** m)


def terminal_alive(C: int, m: int) -> bool:
    modulus = 3 ** m
    live_by_d, _ = run_heartbeat(C, m, max_states_guard=GUARD_STATES)
    return any(live_by_d[d][1 % modulus] for d in range(C + 1))


def sweep_one_C(C: int):
    """Returns a dict with the full record for this C, including whatever
    wall was hit. Never raises past a wall -- catches and records it."""
    formula_pred = M_edge(C)
    print(f"\n=== C={C}  formula_prediction=floor(53*{C + 1}/22)={formula_pred} ===",
          flush=True)

    marker = []
    m = 1
    t_c_start = time.time()
    wall_hit = None
    death_confirmed_at = None
    last_completed_m = 0
    while True:
        elapsed = time.time() - t_c_start
        if elapsed > TIME_CAP_SEC:
            wall_hit = f"TIME_CAP exceeded ({elapsed:.1f}s > {TIME_CAP_SEC}s) before finishing m={m}"
            break
        pred_b = predicted_bytes(C, m)
        pred_mb = pred_b / 1e6
        if pred_mb > RSS_CAP_MB:
            wall_hit = (f"projected RSS for m={m} ((C+1)*3^m = {pred_b:.3e} bytes "
                        f"= {pred_mb:.0f} MB) exceeds RSS_CAP_MB={RSS_CAP_MB} "
                        f"before attempting it")
            break
        t_m0 = time.time()
        try:
            alive = terminal_alive(C, m)
        except ValueError as e:
            wall_hit = f"run_heartbeat guard tripped at m={m}: {e}"
            break
        except MemoryError as e:
            wall_hit = f"MemoryError at m={m}: {e}"
            break
        dt_m = time.time() - t_m0
        rss = get_rss_mb()
        marker.append("L" if alive else ".")
        last_completed_m = m
        print(f"    m={m:>3}  alive={alive}  dt={dt_m:7.2f}s  rss={rss:8.1f}MB  "
              f"marker={''.join(marker)}", flush=True)
        # Cost triples per unit m (3^m), so demanding 2 consecutive dead
        # m's past the edge (like validate_c5.py's margin) gets ~3x more
        # expensive right when we can least afford it. C=1..5 already
        # established (validate_c5.py, LOCK3_PRECISION_COUNTDOWN_GRID.md)
        # that death here is a permanent countdown, not a single blip, so
        # ONE dead m immediately after the alive run is accepted as the
        # death certificate for C>=6 -- recorded honestly as a 1-m
        # confirmation (not 2+) rather than paying the 3x cost or silently
        # pretending we did.
        if len(marker) >= 2 and marker[-1] == "." and marker[-2] == "L":
            death_confirmed_at = m
            break
        if len(marker) >= 2 and marker[-1] == "." and marker[-2] == ".":
            death_confirmed_at = m
            break
        m += 1

    edge = 0
    for ch in marker:
        if ch == "L":
            edge += 1
        else:
            break
    total_dt = time.time() - t_c_start

    match = (edge == formula_pred) if edge > 0 else None
    record = {
        "C": C,
        "formula_prediction": formula_pred,
        "measured_edge": edge if edge > 0 else None,
        "match": match,
        "marker": "".join(marker),
        "last_completed_m": last_completed_m,
        "death_confirmed_at_m": death_confirmed_at,
        "wall_hit": wall_hit,
        "total_time_sec": total_dt,
    }
    print(f"--- C={C} summary: measured_edge={record['measured_edge']} "
          f"formula={formula_pred} match={match} "
          f"death_confirmed_at_m={death_confirmed_at} "
          f"wall_hit={wall_hit!r} total_time={total_dt:.1f}s ---", flush=True)
    return record


def main():
    print("W6V-MEASURE sweep -- NEW MEASUREMENT, 2026-07-04")
    print("Primary instrument: renorm_check/embedding/automaton.py run_heartbeat "
          "(validated 5/5 against Tier-1 genuine edges via validate_c5.py, "
          "this same directory).")
    print(f"Resource caps: RSS_CAP_MB={RSS_CAP_MB}  TIME_CAP_SEC={TIME_CAP_SEC}  "
          f"GUARD_STATES={GUARD_STATES}")

    records = []
    for C in range(6, 12):
        rec = sweep_one_C(C)
        records.append(rec)
        # If we hit a wall with ZERO new alive m's beyond what we can trust
        # (i.e. we couldn't even reach the formula's predicted edge), stop
        # the whole upward sweep -- pushing to higher C would only get
        # worse (cost grows monotonically with both C and m).
        if rec["wall_hit"] is not None and (rec["measured_edge"] is None
                                             or rec["measured_edge"] < rec["formula_prediction"]):
            print(f"\nSTOPPING upward sweep at C={C}: wall hit before edge "
                  f"was fully confirmed. Higher C will only be more expensive.",
                  flush=True)
            break

    print("\n=== FINAL DIGEST ===")
    print(f"{'C':>3} {'measured_edge':>13} {'formula_pred':>12} {'match':>6} {'wall_hit'}")
    for rec in records:
        print(f"{rec['C']:>3} {str(rec['measured_edge']):>13} "
              f"{rec['formula_prediction']:>12} {str(rec['match']):>6} "
              f"{rec['wall_hit']}")

    return records


if __name__ == "__main__":
    main()
