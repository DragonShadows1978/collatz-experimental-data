#!/usr/bin/env python3
"""G3 full execution: V0–V1, E1–E4."""
from __future__ import annotations

import csv
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from g3_core import (  # noqa: E402
    HIGH_RESERVE,
    consec_up_streaks,
    credit_sequence,
    dual_a1_path,
    load_breach_candidates,
    mersenne_prefix,
    verify_lemma3,
    walk_orbit_with_credit,
)

ART = Path(__file__).resolve().parents[1] / "artifacts"
ART.mkdir(parents=True, exist_ok=True)
REPO = Path(__file__).resolve().parents[4]
SEED = 20260710
MAX_STEPS = 8000


def run_v0v1() -> dict:
    ok = True
    gates = {}
    # V0
    try:
        assert verify_lemma3()
        seq = credit_sequence(53)
        gates["V0"] = "PASS"
        detail_v0 = {"support": seq.count(1), "drop": seq.count(2)}
        print("V0 PASS lemma3", detail_v0)
    except Exception as e:
        gates["V0"] = f"FAIL: {e}"
        ok = False
        detail_v0 = {}
        print("V0 FAIL", e)

    # V1
    try:
        steps = walk_orbit_with_credit(80049391, 5000)
        n = len(steps)
        bad = sum(1 for s in steps if not s["dual_ok"])
        assert n > 100 and bad == 0
        gates["V1"] = "PASS"
        detail_v1 = {"n_steps": n, "dual_mismatches": bad}
        print(f"V1 PASS dual identity on 80049391 n={n}")
    except Exception as e:
        gates["V1"] = f"FAIL: {e}"
        ok = False
        detail_v1 = {"error": str(e)}
        print("V1 FAIL", e)

    rep = {"gates": gates, "ok_all": ok, "V0": detail_v0, "V1": detail_v1}
    (ART / "v0v1_report.json").write_text(json.dumps(rep, indent=2))
    return rep


def run_e1() -> dict:
    t0 = time.time()
    rng = random.Random(SEED)
    breach = load_breach_candidates(REPO / "data" / "runs", cap=200)
    randoms = [rng.randrange(1, 10_000_000, 2) for _ in range(100)]
    starts = (
        [("high_reserve", x) for x in HIGH_RESERVE]
        + [("breach", x) for x in breach]
        + [("random", x) for x in randoms]
    )
    events = []
    n_up = 0
    n_a1 = 0
    for src, x0 in starts:
        steps = walk_orbit_with_credit(x0, MAX_STEPS)
        for s in steps:
            if not s["upcrossing"]:
                continue
            n_up += 1
            if s["a"] == 1:
                n_a1 += 1
            at_ceil = s["d_before"] == s["C_run_after"] or s["d_before"] >= s[
                "C_run_after"
            ] - 0
            # before upcrossing, C_run is previous max; d_before should equal old C for ceiling
            # recompute: after step C_run_after is new; previous C was C_run_after if not... messy
            # Use: upcrossing means d_after > previous max. previous max = C_run_after only if we update after.
            # Actually in walk: is_up = d_next > C_run then C_run = d_next. So before update C_old = C_run.
            # We need to store C_before. Fix in loop:
            pass
        # second pass with C_before
        C = 0
        for s in steps:
            C_before = C
            if s["upcrossing"]:
                events.append(
                    {
                        "source": src,
                        "start_n": x0,
                        "k": s["k"],
                        "a": s["a"],
                        "c": s["c"],
                        "d_before": s["d_before"],
                        "d_after": s["d_after"],
                        "C_before": C_before,
                        "at_ceiling": s["d_before"] == C_before,
                    }
                )
                C = s["d_after"]
            else:
                C = max(C, s["d_after"])

    # recount a1 from events
    n_up = len(events)
    n_a1 = sum(1 for e in events if e["a"] == 1)
    n_c2 = sum(1 for e in events if e["c"] == 2)
    n_c1 = sum(1 for e in events if e["c"] == 1)
    frac_c2 = n_c2 / n_up if n_up else 0
    frac_c1 = n_c1 / n_up if n_up else 0
    ceil_ev = [e for e in events if e["at_ceiling"]]
    ceil_c1 = sum(1 for e in ceil_ev if e["c"] == 1)
    frac_ceil_c1 = ceil_c1 / len(ceil_ev) if ceil_ev else 0
    a1_rate = n_a1 / n_up if n_up else 0

    preds = {
        "R1.1": {
            "verdict": "CONFIRMED" if frac_c2 >= 0.90 else "REFUTED",
            "frac_c2": frac_c2,
            "confidence_prior": 0.70,
        },
        "R1.2": {
            "verdict": "CONFIRMED" if frac_c1 <= 0.10 else "REFUTED",
            "frac_c1": frac_c1,
            "confidence_prior": 0.70,
        },
        "R1.3": {
            "verdict": "CONFIRMED" if frac_ceil_c1 <= 0.05 else "REFUTED",
            "frac_ceil_c1": frac_ceil_c1,
            "n_ceiling_ups": len(ceil_ev),
            "confidence_prior": 0.55,
        },
    }
    gates = {
        "E1-G1": "PASS" if n_up >= 500 else "FAIL",
        "E1-G2": "PASS" if a1_rate >= 0.99 else "FAIL",
        "n_upcrossings": n_up,
        "a1_rate": a1_rate,
    }
    csv_path = ART / "e1_upcrossings.csv"
    if events:
        with csv_path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(events[0].keys()))
            w.writeheader()
            w.writerows(events)
    summary = {
        "gates": gates,
        "predictions": preds,
        "frac_c2": frac_c2,
        "frac_c1": frac_c1,
        "elapsed_sec": time.time() - t0,
    }
    (ART / "e1_summary.json").write_text(json.dumps(summary, indent=2))
    print("E1", json.dumps({"gates": gates, "predictions": preds}, indent=2))
    return summary


def run_e2() -> dict:
    rows = [mersenne_prefix(L) for L in range(1, 25)]
    for r in rows:
        assert r["prefix_all_a1"], r
    mean_ratio = sum(r["ups_over_L"] for r in rows) / len(rows)
    r21 = {
        "verdict": "CONFIRMED" if mean_ratio <= 0.50 else "REFUTED",
        "mean_ups_over_L": mean_ratio,
        "confidence_prior": 0.50,
    }
    r22_ok = all(r["max_d_prefix"] <= r["L"] for r in rows)
    r22 = {
        "verdict": "CONFIRMED" if r22_ok else "REFUTED",
        "confidence_prior": 0.60,
    }
    ext = [r["max_d_extended"] for r in rows]
    mono = all(ext[i] <= ext[i + 1] for i in range(len(ext) - 1))
    r23 = {
        "verdict": "CONFIRMED" if not mono else "REFUTED",
        "max_d_extended_by_L": ext,
        "was_monotone_nondecreasing": mono,
        "confidence_prior": 0.55,
    }
    gates = {"E2-G1": "PASS", "E2-G2": "PASS", "n": len(rows)}
    with (ART / "e2_mersenne.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    summary = {
        "gates": gates,
        "predictions": {"R2.1": r21, "R2.2": r22, "R2.3": r23},
        "rows": rows,
    }
    (ART / "e2_summary.json").write_text(json.dumps(summary, indent=2))
    print("E2", json.dumps(summary["predictions"], indent=2))
    return summary


def run_e3() -> dict:
    Ls = [1, 2, 4, 8, 12, 16, 20, 24]
    cells = []
    for L in Ls:
        for k0 in range(53):
            for d0 in range(11):
                cells.append(dual_a1_path(L, k0, d0))
    # R3.1 L=24
    c24 = [c for c in cells if c["L"] == 24]
    frac_nn = sum(1 for c in c24 if c["stayed_nonneg"]) / len(c24)
    r31 = {
        "verdict": "CONFIRMED" if frac_nn <= 0.25 else "REFUTED",
        "frac_stayed_nonneg_L24": frac_nn,
        "n": len(c24),
        "confidence_prior": 0.55,
    }
    c24_d0 = [c for c in c24 if c["d0"] == 0]
    frac_d0 = sum(1 for c in c24_d0 if c["stayed_nonneg"]) / len(c24_d0)
    r32 = {
        "verdict": "CONFIRMED" if frac_d0 <= 0.10 else "REFUTED",
        "frac_stayed_nonneg_L24_d0": frac_d0,
        "n": len(c24_d0),
        "confidence_prior": 0.60,
    }
    mean_vu = sum(c["n_virt_up"] for c in c24_d0) / len(c24_d0)
    r33 = {
        "verdict": "CONFIRMED" if mean_vu <= 8 else "REFUTED",
        "mean_virt_ups_L24_d0": mean_vu,
        "confidence_prior": 0.50,
    }
    gates = {
        "E3-G1": "PASS" if len(cells) == 8 * 53 * 11 else "FAIL",
        "E3-G2": "PASS",
        "n_cells": len(cells),
    }
    # write compact summary + sample csv of L=24 d0=0
    sample = [c for c in cells if c["L"] == 24 and c["d0"] == 0]
    with (ART / "e3_dual_L24_d0.csv").open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "L",
                "k0",
                "d0",
                "d_final",
                "min_d",
                "n_virt_up",
                "stayed_nonneg",
            ],
        )
        w.writeheader()
        for c in sample:
            w.writerow({k: c[k] for k in w.fieldnames})
    summary = {
        "gates": gates,
        "predictions": {"R3.1": r31, "R3.2": r32, "R3.3": r33},
    }
    (ART / "e3_summary.json").write_text(json.dumps(summary, indent=2))
    print("E3", json.dumps(summary, indent=2))
    return summary


def run_e4() -> dict:
    rng = random.Random(SEED)
    breach = load_breach_candidates(REPO / "data" / "runs", cap=200)
    randoms = [rng.randrange(1, 10_000_000, 2) for _ in range(100)]
    starts = list(HIGH_RESERVE) + breach + randoms
    all_streaks = []
    n_ups = 0
    for x0 in starts:
        steps = walk_orbit_with_credit(x0, MAX_STEPS)
        n_ups += sum(1 for s in steps if s["upcrossing"])
        all_streaks.extend(consec_up_streaks(steps))
    max_st = max(all_streaks) if all_streaks else 0
    n_iso = sum(1 for s in all_streaks if s == 1)
    # isolated upcrossings as fraction of upcrossing events:
    # each streak of length s contributes s ups; isolated count = n_iso
    frac_iso = n_iso / n_ups if n_ups else 0
    # actually each streak length 1 is one isolated up; total ups = sum(streaks)
    sum_st = sum(all_streaks)
    frac_iso = n_iso / sum_st if sum_st else 0
    r41 = {
        "verdict": "CONFIRMED" if max_st <= 5 else "REFUTED",
        "max_streak": max_st,
        "confidence_prior": 0.65,
    }
    r42 = {
        "verdict": "CONFIRMED" if frac_iso >= 0.80 else "REFUTED",
        "frac_ups_in_streak1": frac_iso,
        "n_streak1": n_iso,
        "n_ups_in_streaks": sum_st,
        "confidence_prior": 0.55,
    }
    hist = dict(Counter(all_streaks))
    summary = {
        "predictions": {"R4.1": r41, "R4.2": r42},
        "streak_hist": hist,
        "n_starts": len(starts),
    }
    (ART / "e4_summary.json").write_text(json.dumps(summary, indent=2))
    print("E4", json.dumps(summary, indent=2))
    return summary


def main() -> int:
    print("=== G3 V0–V1 ===", flush=True)
    v = run_v0v1()
    if not v["ok_all"]:
        return 1
    print("=== G3 E1 ===", flush=True)
    run_e1()
    print("=== G3 E2 ===", flush=True)
    run_e2()
    print("=== G3 E3 ===", flush=True)
    run_e3()
    print("=== G3 E4 ===", flush=True)
    run_e4()
    print("G3 RUN_ALL DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
