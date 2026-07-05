#!/usr/bin/env python3
"""
W6W-SPARSE Steps 2-4 -- the climb. Only run after step1_validation_gates.py
has PASSED (this script does not re-check the gates; it assumes them green).

Step 2: C=7 full measurement (formula predicts M_edge=19; dense sweep
        died at m=17 from RSS -- first genuinely new Tier-1 datum).
Step 3: Climb C=8 (formula 21), C=9 (24), C=10 (26), C=11 (28) -- record
        measured M_edge (or wall), formula, match, peak live-set size
        at each C. Self-monitor RSS, stop gracefully under an ~8GB cap.
Step 4: At C=11, sweep m PAST 28 explicitly (the prize): does the
        corridor die at 28 (plateau claim gets a frame-artifact
        diagnosis) or live to 29..32+ (formula-break candidate,
        independent re-derivation required)?

Runs in foreground (invoked via nohup by the driver); writes JSON + CSV
+ a plain-text log as it goes so partial progress survives a kill.
"""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
EMBEDDING = HERE.parent.parent.parent / "embedding"
sys.path.insert(0, str(EMBEDDING))
sys.path.insert(0, str(HERE))

from sparse_instrument import (  # noqa: E402
    sparse_survival, verify_witness_exact, M_edge_formula, credit_at_step,
)

RSS_CAP_MB = 7500.0  # ~8GB nominal cap, stop gracefully before hard OOM
LOG_PATH = HERE / "step2_4_climb.log"
CSV_PATH = HERE / "step2_4_climb_table.csv"
JSON_PATH = HERE / "step2_4_climb_full.json"

_log_lines = []


def log(s=""):
    print(s, flush=True)
    _log_lines.append(s)
    LOG_PATH.write_text("\n".join(_log_lines) + "\n")


def measure_C(C: int, m_max: int, rss_cap_mb: float = RSS_CAP_MB):
    """Sweep m=1..m_max at fixed C, recording every row (not just the
    edge), so partial progress is visible even if a wall is hit."""
    rows = []
    peak_live_over_all_m = 0
    status = None
    wall = None
    measured_edge = None
    last_alive = 0
    t_c0 = time.time()
    for m in range(1, m_max + 1):
        t0 = time.time()
        res = sparse_survival(m, C, rss_cap_mb=rss_cap_mb)
        dt = time.time() - t0
        peak_live_over_all_m = max(peak_live_over_all_m, res["peak_live_states"])
        rows.append({
            "C": C, "m": m, "alive": res["alive"],
            "peak_live_states": res["peak_live_states"],
            "peak_rss_mb": res["peak_rss_mb"], "elapsed_sec": dt,
            "wall": res["wall"],
        })
        log(f"  C={C:>2} m={m:>3}  alive={res['alive']!s:>5}  "
            f"peak_live={res['peak_live_states']:>10}  "
            f"peak_rss={res['peak_rss_mb']:>8.1f}MB  dt={dt:>7.3f}s"
            + (f"  WALL: {res['wall']}" if res["wall"] else ""))
        if res["wall"] is not None:
            status = "WALL"
            wall = res["wall"]
            break
        if not res["alive"]:
            measured_edge = m - 1
            last_alive = m - 1
            status = "GENUINE_EDGE"
            break
        last_alive = m
    else:
        status = "M_MAX_EXHAUSTED_STILL_ALIVE"
        last_alive = m_max

    total_dt = time.time() - t_c0
    return {
        "C": C, "status": status, "measured_edge": measured_edge,
        "last_alive_m": last_alive, "wall": wall,
        "peak_live_over_all_m": peak_live_over_all_m,
        "total_time_sec": total_dt, "rows": rows,
    }


def main():
    all_records = []
    all_rows = []

    log("=== W6W-SPARSE Steps 2-4: the climb ===")
    log(f"RSS cap: {RSS_CAP_MB} MB per process (self-monitored via "
        f"resource.getrusage)\n")

    # -------------------------------------------------------------
    # Step 2: C=7, target formula M_edge=19 (first cell dense
    # enumeration could not finish -- died at m=17 from RSS).
    # -------------------------------------------------------------
    log("--- Step 2: C=7 full measurement (formula predicts 19) ---")
    rec7 = measure_C(7, m_max=25)
    all_records.append(rec7)
    all_rows.extend(rec7["rows"])
    formula7 = M_edge_formula(7)
    log(f"C=7 result: status={rec7['status']} measured_edge={rec7['measured_edge']} "
        f"formula={formula7} match={rec7['measured_edge'] == formula7} "
        f"peak_live={rec7['peak_live_over_all_m']} wall={rec7['wall']}\n")

    if rec7["status"] == "WALL":
        log("STEP 2 HIT A WALL before establishing C=7's true edge. Per house "
            "rules this is reported honestly; the climb below still proceeds "
            "for lower-cost C values already queued but the C=7 cell itself "
            "stays a wall, not a silently narrowed/fudged result.")

    # -------------------------------------------------------------
    # Step 3: climb C=8..11 (formula predicts 21, 24, 26, 28)
    # -------------------------------------------------------------
    log("--- Step 3: climb C=8..11 ---")
    m_max_by_C = {8: 27, 9: 30, 10: 32, 11: 40}
    for C in [8, 9, 10, 11]:
        formula_C = M_edge_formula(C)
        log(f"\nC={C} (formula predicts {formula_C}):")
        rec = measure_C(C, m_max=m_max_by_C[C])
        all_records.append(rec)
        all_rows.extend(rec["rows"])
        log(f"C={C} result: status={rec['status']} measured_edge={rec['measured_edge']} "
            f"formula={formula_C} match={rec['measured_edge'] == formula_C} "
            f"peak_live={rec['peak_live_over_all_m']} wall={rec['wall']}")
        if rec["status"] == "WALL":
            log(f"STOPPING upward climb at C={C}: wall hit. Higher C is only "
                f"more expensive under this instrument too (peak live-set size "
                f"grows with C, see growth table).")
            break

    # -------------------------------------------------------------
    # Step 4: THE PRIZE -- at C=11, sweep m PAST 28 explicitly.
    # (measure_C(11, ...) above already did this if it got far enough;
    # this section makes the m=29..32+ region an explicit, separately
    # logged and verified result regardless of how Step 3 ended.)
    # -------------------------------------------------------------
    log("\n--- Step 4: THE PRIZE -- C=11, m past 28 ---")
    rec11 = next((r for r in all_records if r["C"] == 11), None)
    if rec11 is None:
        log("C=11 was never reached in Step 3 (wall hit earlier) -- Step 4 "
            "cannot run. Reporting as incomplete, not fabricating a result.")
    else:
        # Explicitly report m=28..32 (and beyond, up to whatever measure_C(11,...)
        # covered) as the decisive cells.
        by_m = {r["m"]: r for r in rec11["rows"]}
        log("Decisive cells (C=11):")
        for m in range(26, 34):
            if m in by_m:
                r = by_m[m]
                log(f"  m={m}: alive={r['alive']} peak_live={r['peak_live_states']} "
                    f"peak_rss={r['peak_rss_mb']:.1f}MB wall={r['wall']}")
            else:
                log(f"  m={m}: NOT REACHED (sweep stopped earlier -- "
                    f"status={rec11['status']}, wall={rec11['wall']})")

        died_at_28 = (rec11["status"] == "GENUINE_EDGE" and rec11["measured_edge"] == 28)
        lives_past_28 = any(by_m.get(m, {}).get("alive") for m in range(29, 33) if m in by_m)

        log(f"\nC=11 verdict (raw, pre-independent-rederivation): "
            f"died_at_28={died_at_28}  lives_past_28_at_least_one_m={lives_past_28}")

        if lives_past_28:
            log("Corridor LIVES past m=28 at C=11 under the sparse instrument. "
                "This is the formula-break candidate -- independent "
                "re-derivation is REQUIRED before reporting (see "
                "step4_independent_rederivation.py).")
            # Verify each living witness exactly.
            for m in range(29, 33):
                if m in by_m and by_m[m]["alive"]:
                    res = sparse_survival(m, 11, rss_cap_mb=RSS_CAP_MB)
                    if res["witness"]:
                        v = verify_witness_exact(res["witness"], 11, res["letters"])
                        log(f"  m={m} witness exact-verify: all_ok={v['all_ok']} "
                            f"start_integer={v['start_integer']} "
                            f"collatz_replay_ok={v['collatz_replay_ok']} "
                            f"deficit_range={v['range']}")
        elif died_at_28:
            log("Corridor DIES at m=28 at C=11 under the sparse instrument "
                "(matches the archived/DERIVED formula value exactly). This "
                "means the D_recon(29..32)=11 plateau claim (SYNTHESIS.md "
                "W6U-RECON final), if the plateau claim is about the SAME "
                "quantity as M_edge, is contradicted by THIS instrument -- "
                "but the plateau claim's own object (D_recon, END-anchored "
                "FREE-endpoint deficit RANGE swept over C at FIXED m) needs "
                "explicit comparison against M_edge's object (fixed C, swept "
                "m, ALSO free-endpoint per this instrument's own construction "
                "-- see step4_reconcile_with_plateau.py) before concluding "
                "'frame artifact' -- do not hand-wave, name the mechanism.")
        else:
            log("Neither confirmed: sweep did not reach a clean verdict "
                "(check wall/status above). Reporting as incomplete.")

    # -------------------------------------------------------------
    # Final tables
    # -------------------------------------------------------------
    log("\n=== Tier-1 table extension (C vs measured/wall vs formula vs peak live-set) ===")
    log(f"{'C':>3} {'measured_edge':>14} {'formula':>8} {'match':>6} {'peak_live_set':>14} {'status':>28}")
    for rec in all_records:
        formula_C = M_edge_formula(rec["C"])
        match = (rec["measured_edge"] == formula_C) if rec["measured_edge"] is not None else None
        log(f"{rec['C']:>3} {str(rec['measured_edge']):>14} {formula_C:>8} "
            f"{str(match):>6} {rec['peak_live_over_all_m']:>14} {rec['status']:>28}")

    with open(CSV_PATH, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["C", "m", "alive", "peak_live_states",
                                           "peak_rss_mb", "elapsed_sec", "wall"])
        w.writeheader()
        for r in all_rows:
            w.writerow(r)
    log(f"\nWrote {CSV_PATH}")

    with open(JSON_PATH, "w") as f:
        json.dump(all_records, f, indent=2, default=str)
    log(f"Wrote {JSON_PATH}")
    log(f"\nWrote {LOG_PATH}")


if __name__ == "__main__":
    main()
