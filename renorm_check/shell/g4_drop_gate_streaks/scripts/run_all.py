#!/usr/bin/env python3
"""G4 full execution."""
from __future__ import annotations

import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from g4_core import (  # noqa: E402
    HIGH_RESERVE,
    credit,
    drop_runs,
    greedy_up_walker,
    load_breach_candidates,
    prove_U_cases,
    up_streaks_detailed,
    walk_with_C_before,
)

ART = Path(__file__).resolve().parents[1] / "artifacts"
ART.mkdir(parents=True, exist_ok=True)
REPO = Path(__file__).resolve().parents[4]
SEED = 20260711


def main() -> int:
    t0 = time.time()
    report: dict = {}

    # ----- V0 Theorem U -----
    cases = prove_U_cases()
    assert cases["all_ok"], cases["rows_fail"]
    print("V0 algebra cases PASS", cases["n"])

    rng = random.Random(SEED)
    breach = load_breach_candidates(REPO / "data" / "runs", cap=200)
    randoms = [rng.randrange(1, 10_000_000, 2) for _ in range(100)]
    starts = list(HIGH_RESERVE) + breach + randoms

    free_ups = 0
    free_fail = 0
    all_streaks = []
    post_up = []  # (c_next, up_next)
    drop_pair_at = []  # for each consecutive c=2,c=2 in orbit steps, whether up-streak of 2

    for x0 in starts:
        steps = walk_with_C_before(x0, 8000)
        for s in steps:
            if s["upcrossing"]:
                free_ups += 1
                if not s["thm_U"]:
                    free_fail += 1
        all_streaks.extend(up_streaks_detailed(steps))
        for i, s in enumerate(steps):
            if not s["upcrossing"]:
                continue
            if i + 1 < len(steps):
                nxt = steps[i + 1]
                post_up.append(
                    {
                        "c_next": nxt["c"],
                        "up_next": nxt["upcrossing"],
                        "a_next": nxt["a"],
                    }
                )
        # drop pairs in this orbit's credit along path
        for i in range(len(steps) - 1):
            if steps[i]["c"] == 2 and steps[i + 1]["c"] == 2:
                both_up = steps[i]["upcrossing"] and steps[i + 1]["upcrossing"]
                drop_pair_at.append(both_up)

    s01 = {
        "verdict": "CONFIRMED" if free_fail == 0 and free_ups >= 1000 else "REFUTED",
        "n_ups": free_ups,
        "n_fail": free_fail,
        "confidence_prior": 0.95,
    }
    print(f"S0.1 free sample ups={free_ups} fail={free_fail}")

    # S0.2 small odds
    small_fail = 0
    small_ups = 0
    for x in range(1, 100_001, 2):
        steps = walk_with_C_before(x, 200)
        for s in steps:
            if s["upcrossing"]:
                small_ups += 1
                if not s["thm_U"]:
                    small_fail += 1
    s02 = {
        "verdict": "CONFIRMED" if small_fail == 0 else "REFUTED",
        "n_ups": small_ups,
        "n_fail": small_fail,
        "confidence_prior": 0.90,
    }
    print(f"S0.2 small odds ups={small_ups} fail={small_fail}")

    v0 = {
        "gates": {
            "V0-G1": "PASS",  # slack proof in ledger
            "V0-G2": "PASS" if free_fail == 0 else "FAIL",
            "V0-G3": "PASS" if small_fail == 0 else "FAIL",
        },
        "algebra_cases": cases,
        "predictions": {"S0.1": s01, "S0.2": s02},
        "lemma": (
            "d' = d + c - a; upcross needs c-a > slack=C-d ≥ 0; "
            "c-a ≤ 1 ⇒ slack=0 and (c,a)=(2,1). Hence every upcrossing is "
            "at-ceiling, drop-phase, a=1."
        ),
    }
    (ART / "v0_theorem_U.json").write_text(json.dumps(v0, indent=2))

    # ----- E1 drop runs -----
    N = 10000
    seq = [credit(k) for k in range(N)]
    runs = drop_runs(seq)
    block = [credit(k) for k in range(53)]
    block_runs = drop_runs(block)
    R_max = max(runs) if runs else 0
    R_block = max(block_runs) if block_runs else 0
    mean_run = sum(runs) / len(runs) if runs else 0
    s11 = {
        "verdict": "CONFIRMED" if R_max == R_block else "REFUTED",
        "R_max_10k": R_max,
        "R_max_block53": R_block,
        "confidence_prior": 0.60,
    }
    s12 = {
        "verdict": "CONFIRMED" if R_max <= 3 else "REFUTED",
        "R_max": R_max,
        "confidence_prior": 0.55,
    }
    s13 = {
        "verdict": "CONFIRMED" if 1.2 <= mean_run <= 2.0 else "REFUTED",
        "mean_drop_run": mean_run,
        "confidence_prior": 0.50,
    }
    e1 = {
        "predictions": {"S1.1": s11, "S1.2": s12, "S1.3": s13},
        "drop_run_hist": dict(Counter(runs)),
        "block_run_hist": dict(Counter(block_runs)),
        "R_max": R_max,
    }
    (ART / "e1_drop_runs.json").write_text(json.dumps(e1, indent=2))
    print("E1", e1["predictions"])

    # ----- E2 streaks vs drop -----
    max_S = max((st["S"] for st in all_streaks), default=0)
    s21_ok = all(st["S"] <= R_max for st in all_streaks) and all(
        st["all_c2"] and st["all_a1"] for st in all_streaks
    )
    s21 = {
        "verdict": "CONFIRMED" if s21_ok else "REFUTED",
        "max_S": max_S,
        "R_max": R_max,
        "all_streaks_c2_a1": all(st["all_c2"] and st["all_a1"] for st in all_streaks),
        "confidence_prior": 0.85,
    }
    s22 = {
        "verdict": "CONFIRMED" if max_S <= R_block else "REFUTED",
        "max_S": max_S,
        "R_block": R_block,
        "confidence_prior": 0.70,
    }
    n_pairs = len(drop_pair_at)
    n_pair_up = sum(1 for b in drop_pair_at if b)
    frac_pair = n_pair_up / n_pairs if n_pairs else 0
    s23 = {
        "verdict": "CONFIRMED" if frac_pair <= 0.50 else "REFUTED",
        "frac_drop_pairs_are_double_up": frac_pair,
        "n_drop_pairs": n_pairs,
        "confidence_prior": 0.55,
    }
    e2 = {
        "predictions": {"S2.1": s21, "S2.2": s22, "S2.3": s23},
        "streak_hist": dict(Counter(st["S"] for st in all_streaks)),
        "n_streaks": len(all_streaks),
    }
    (ART / "e2_streaks.json").write_text(json.dumps(e2, indent=2))
    print("E2", e2["predictions"])

    # ----- E3 support interruption -----
    n_post = len(post_up)
    n_sup = sum(1 for p in post_up if p["c_next"] == 1)
    n_second = sum(1 for p in post_up if p["up_next"])
    n_sup_second = sum(1 for p in post_up if p["c_next"] == 1 and p["up_next"])
    frac_sup = n_sup / n_post if n_post else 0
    frac_sec = n_second / n_post if n_post else 0
    s31 = {
        "verdict": "CONFIRMED" if frac_sup >= 0.50 else "REFUTED",
        "frac_post_up_support": frac_sup,
        "confidence_prior": 0.45,
    }
    s32 = {
        "verdict": "CONFIRMED" if frac_sec <= 0.35 else "REFUTED",
        "frac_second_up": frac_sec,
        "confidence_prior": 0.55,
    }
    s33 = {
        "verdict": "CONFIRMED" if n_sup_second == 0 else "REFUTED",
        "n_support_then_up": n_sup_second,
        "confidence_prior": 0.90,
    }
    e3 = {
        "predictions": {"S3.1": s31, "S3.2": s32, "S3.3": s33},
        "n_post_up": n_post,
    }
    (ART / "e3_support_interrupt.json").write_text(json.dumps(e3, indent=2))
    print("E3", e3["predictions"])

    # ----- E4 greedy -----
    best53 = {"ups": -1}
    best106 = {"ups": -1}
    max_g_streak = 0
    for d0 in range(0, 11):
        for k0 in range(53):
            r53 = greedy_up_walker(k0, d0, 53)
            r106 = greedy_up_walker(k0, d0, 106)
            max_g_streak = max(max_g_streak, r53["max_streak"], r106["max_streak"])
            if r53["ups"] > best53["ups"]:
                best53 = r53
            if r106["ups"] > best106["ups"]:
                best106 = r106
    s41 = {
        "verdict": "CONFIRMED" if best53["ups"] <= 15 else "REFUTED",
        "max_ups_53": best53["ups"],
        "arg": best53,
        "confidence_prior": 0.50,
    }
    s42 = {
        "verdict": "CONFIRMED" if best106["ups"] <= 30 else "REFUTED",
        "max_ups_106": best106["ups"],
        "arg": best106,
        "confidence_prior": 0.50,
    }
    s43 = {
        "verdict": "CONFIRMED" if max_g_streak <= R_max else "REFUTED",
        "max_greedy_streak": max_g_streak,
        "R_max": R_max,
        "confidence_prior": 0.80,
    }
    e4 = {
        "predictions": {"S4.1": s41, "S4.2": s42, "S4.3": s43},
    }
    (ART / "e4_greedy.json").write_text(json.dumps(e4, indent=2))
    print("E4", e4["predictions"])

    summary = {
        "elapsed_sec": time.time() - t0,
        "V0": v0["predictions"],
        "E1": e1["predictions"],
        "E2": e2["predictions"],
        "E3": e3["predictions"],
        "E4": e4["predictions"],
        "R_max_drop_run": R_max,
        "free_ups": free_ups,
    }
    (ART / "summary.json").write_text(json.dumps(summary, indent=2))
    print("G4 DONE", json.dumps({k: {a: b["verdict"] for a, b in v.items()} for k, v in [
        ("V0", v0["predictions"]),
        ("E1", e1["predictions"]),
        ("E2", e2["predictions"]),
        ("E3", e3["predictions"]),
        ("E4", e4["predictions"]),
    ]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
