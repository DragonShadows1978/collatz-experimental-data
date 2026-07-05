#!/usr/bin/env python3
"""
W6V-MEASURE v2 -- subprocess-isolated sweep, NEW MEASUREMENT, 2026-07-04.

Follow-up to sweep_new_C.py (v1), per a peer session's suggestion: v1 ran
the whole sweep in one long-lived process, so automaton.py's module-level
`_PERM_CACHE` (int64 permutation arrays, one per distinct exponent `a`,
never cleared) accumulated across every (C, m) trial in the same process,
inflating RSS to ~13x the naive (C+1)*3^m boolean-array estimate (verified
at two points in v1: C=6/m=17 = 13.28x, C=7/m=17 = 13.00x).

This version runs each (C, m) trial in its OWN fresh subprocess
(trial_worker.py) so _PERM_CACHE starts empty every time, eliminating
CROSS-TRIAL accumulation.

IMPORTANT CORRECTION found while implementing this (verified empirically,
not assumed): even in a single fresh process, run_heartbeat's WITHIN-CALL
permutation cache is still large -- it builds one int64 (8 bytes/elem)
array of length 3^m per distinct exponent `a` used during the 53-step
heartbeat (typically ~C+2 distinct values of `a`), which by itself
already exceeds the naive (C+1)*3^m boolean estimate for any C, since
8*(C+2) > (C+1) always. Measured directly: C=5, m=15 in a fresh process
still showed a ~15x observed/naive multiplier (1286MB vs 86MB naive).
So subprocess isolation removes the CROSS-trial multiplier (good, no more
runaway growth across a whole sweep) but does NOT bring single-trial cost
down to the naive bound -- the true per-trial ceiling is closer to
roughly (C+2)*8*3^m (the permutation-cache bound) than (C+1)*3^m (the
naive boolean-array bound). This is reported honestly below rather than
assumed from the naive formula alone.

Usage: python3 sweep_new_C_v2.py | tee sweep_new_C_v2.log
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
WORKER = HERE / "trial_worker.py"

RSS_CAP_MB = 8000
TIME_CAP_SEC = 20 * 60


def formula_M_edge(C: int) -> int:
    return (53 * (C + 1)) // 22


def run_trial(C: int, m: int, timeout_sec: float):
    """Runs trial_worker.py in a fresh subprocess. Returns parsed dict or
    a dict with an 'error' key (including subprocess-level failures like
    timeout or being OOM-killed, which the worker itself cannot report)."""
    try:
        proc = subprocess.run(
            [sys.executable, str(WORKER), str(C), str(m)],
            capture_output=True, text=True, timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired:
        return {"C": C, "m": m, "error": f"subprocess TIMEOUT after {timeout_sec}s"}
    if proc.returncode != 0:
        # Most likely an OOM kill (negative returncode = killed by signal)
        # or an uncaught exception in the worker.
        return {"C": C, "m": m,
                "error": f"subprocess exited {proc.returncode}; stderr_tail="
                         f"{proc.stderr[-500:]!r}"}
    line = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    try:
        return json.loads(line)
    except (json.JSONDecodeError, IndexError):
        return {"C": C, "m": m, "error": f"could not parse worker stdout: {proc.stdout!r} "
                                          f"stderr={proc.stderr[-500:]!r}"}


def sweep_one_C(C: int):
    formula_pred = formula_M_edge(C)
    print(f"\n=== C={C}  formula_prediction=floor(53*{C + 1}/22)={formula_pred} "
          f"(subprocess-isolated) ===", flush=True)

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
        # Per-trial timeout: don't let one subprocess eat the whole cap.
        remaining = max(30.0, TIME_CAP_SEC - elapsed)
        t_m0 = time.time()
        result = run_trial(C, m, timeout_sec=remaining)
        dt_m = time.time() - t_m0

        if "error" in result:
            wall_hit = f"trial failed at m={m}: {result['error']}"
            print(f"    m={m:>3}  ERROR  dt={dt_m:7.2f}s  {result['error']}", flush=True)
            break

        alive = result["alive"]
        peak_rss = result.get("peak_rss_mb", -1.0)
        marker.append("L" if alive else ".")
        last_completed_m = m
        print(f"    m={m:>3}  alive={alive}  dt={dt_m:7.2f}s  "
              f"peak_rss={peak_rss:8.1f}MB  marker={''.join(marker)}", flush=True)

        if peak_rss > RSS_CAP_MB:
            wall_hit = f"peak_rss {peak_rss:.1f}MB exceeded RSS_CAP_MB={RSS_CAP_MB} at m={m}"
            break

        if len(marker) >= 2 and marker[-1] == "." :
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

    saw_death = "." in marker
    if saw_death:
        genuine_edge = edge
        match = (genuine_edge == formula_pred)
        status = "GENUINE_EDGE"
    else:
        genuine_edge = None
        match = None
        status = "INCONCLUSIVE_NO_DEATH_OBSERVED"

    record = {
        "C": C,
        "formula_prediction": formula_pred,
        "measured_edge": genuine_edge,
        "last_m_tested_alive": edge if not saw_death else None,
        "status": status,
        "match": match,
        "marker": "".join(marker),
        "last_completed_m": last_completed_m,
        "death_confirmed_at_m": death_confirmed_at,
        "wall_hit": wall_hit,
        "total_time_sec": total_dt,
    }
    print(f"--- C={C} summary: status={status} measured_edge={record['measured_edge']} "
          f"last_m_tested_alive={record['last_m_tested_alive']} formula={formula_pred} "
          f"match={match} wall_hit={wall_hit!r} total_time={total_dt:.1f}s ---", flush=True)
    return record


def main():
    print("W6V-MEASURE v2 sweep (subprocess-isolated) -- NEW MEASUREMENT, 2026-07-04")
    print("Each (C, m) trial runs in its own fresh subprocess via trial_worker.py, "
          "so automaton.py's _PERM_CACHE starts empty every trial (eliminates "
          "cross-trial accumulation seen in sweep_new_C.py v1).")
    print(f"Resource caps: RSS_CAP_MB={RSS_CAP_MB}  TIME_CAP_SEC={TIME_CAP_SEC} (per C)")

    records = []
    for C in range(7, 12):
        rec = sweep_one_C(C)
        records.append(rec)
        if rec["wall_hit"] is not None and rec["status"] == "INCONCLUSIVE_NO_DEATH_OBSERVED":
            print(f"\nSTOPPING upward sweep at C={C}: wall hit before any death "
                  f"was observed. Higher C will only be more expensive.", flush=True)
            break

    print("\n=== FINAL DIGEST (v2) ===")
    print(f"{'C':>3} {'status':>28} {'measured_edge':>13} {'last_alive_m':>12} "
          f"{'formula_pred':>12} {'match':>6} {'wall_hit'}")
    for rec in records:
        print(f"{rec['C']:>3} {rec['status']:>28} {str(rec['measured_edge']):>13} "
              f"{str(rec['last_m_tested_alive']):>12} {rec['formula_prediction']:>12} "
              f"{str(rec['match']):>6} {rec['wall_hit']}")

    return records


if __name__ == "__main__":
    main()
