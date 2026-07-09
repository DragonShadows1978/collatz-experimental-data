#!/usr/bin/env python3
"""G2 E1 — climb-run census. Predictions Q1.1–Q1.3 frozen in IMPLEMENTATION_PLAN."""
from __future__ import annotations

import csv
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from g2_core import (  # noqa: E402
    HIGH_RESERVE,
    count_upcrossings,
    extract_climb_runs,
    extract_gap_words,
    load_breach_candidates,
    walk_orbit,
)

ART = Path(__file__).resolve().parents[1] / "artifacts"
ART.mkdir(parents=True, exist_ok=True)
REPO = Path(__file__).resolve().parents[4]
SEED = 20260709
MAX_STEPS = 8000
RANDOM_N = 100
RANDOM_LIM = 10_000_000


def main() -> int:
    t0 = time.time()
    rng = random.Random(SEED)
    breach = load_breach_candidates(REPO / "data" / "runs", cap=200)
    random_odds = []
    while len(random_odds) < RANDOM_N:
        random_odds.append(rng.randrange(1, RANDOM_LIM, 2))

    starts = (
        [("high_reserve", x) for x in HIGH_RESERVE]
        + [("breach_candidate", x) for x in breach]
        + [("random", x) for x in random_odds]
    )
    print(f"E1 starts={len(starts)} seed={SEED}", flush=True)

    all_runs = []
    all_gap_words = Counter()
    start_stats = []
    n_up = 0
    n_up_a1 = 0

    for src, x0 in starts:
        steps = walk_orbit(x0, max_steps=MAX_STEPS)
        ups = [s for s in steps if s["upcrossing"]]
        n_up += len(ups)
        n_up_a1 += sum(1 for s in ups if s["a"] == 1)
        runs = extract_climb_runs(steps, x0, src)
        all_runs.extend(runs)
        for w in extract_gap_words(steps, max_len=12):
            all_gap_words[w] += 1
        start_stats.append(
            {
                "source": src,
                "start_n": x0,
                "n_upcrossings": len(ups),
                "n_climb_runs": len(runs),
                "max_d": max((s["d"] for s in steps), default=0),
                "max_L": max((r["L"] for r in runs), default=0),
            }
        )
        if len(start_stats) % 50 == 0:
            print(f"  ... {len(start_stats)} starts, {len(all_runs)} runs", flush=True)

    a1_rate = n_up_a1 / n_up if n_up else 0.0
    L_hist = Counter(r["L"] for r in all_runs)
    max_L = max(L_hist) if L_hist else 0

    # Q1 predictions
    q11 = {
        "verdict": "CONFIRMED" if max_L <= 20 else ("REFUTED" if max_L >= 40 else "INCONCLUSIVE"),
        "max_L": max_L,
        "confidence_prior": 0.70,
    }
    # geometric-like: counts L=1 >= L=2 >= L=3 (if present)
    c1, c2, c3 = L_hist.get(1, 0), L_hist.get(2, 0), L_hist.get(3, 0)
    geo = c1 > 0 and c1 >= c2 and (c2 >= c3 or c3 == 0)
    q12 = {
        "verdict": "CONFIRMED" if geo else "REFUTED",
        "counts_L1_L2_L3": [c1, c2, c3],
        "L_hist": dict(sorted(L_hist.items())),
        "confidence_prior": 0.55,
    }

    def mean_ups(src_name):
        xs = [s["n_upcrossings"] for s in start_stats if s["source"] == src_name]
        return sum(xs) / len(xs) if xs else 0.0

    m_hr, m_rand = mean_ups("high_reserve"), mean_ups("random")
    q13_ok = m_hr >= 1.0 and m_rand < 5.0
    q13 = {
        "verdict": "CONFIRMED" if q13_ok else "REFUTED",
        "mean_upcrossings_high_reserve": m_hr,
        "mean_upcrossings_random": m_rand,
        "mean_upcrossings_breach": mean_ups("breach_candidate"),
        "confidence_prior": 0.60,
    }

    gates = {
        "E1-G1": "PASS" if len(all_runs) >= 100 else "FAIL",
        "E1-G2": "PASS" if a1_rate >= 0.99 else "FAIL",
        "n_runs": len(all_runs),
        "n_upcrossings": n_up,
        "a1_upcrossing_rate": a1_rate,
    }

    csv_path = ART / "e1_climb_runs.csv"
    if all_runs:
        fields = list(all_runs[0].keys())
        with csv_path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(all_runs)

    # top gap words for E3
    top_words = [
        {"word": list(w), "word_str": ",".join(map(str, w)), "count": c, "length": len(w)}
        for w, c in all_gap_words.most_common(20)
    ]

    summary = {
        "gates": gates,
        "predictions": {"Q1.1": q11, "Q1.2": q12, "Q1.3": q13},
        "L_hist": dict(sorted(L_hist.items())),
        "max_L": max_L,
        "n_starts": len(starts),
        "seed": SEED,
        "max_steps": MAX_STEPS,
        "top_gap_words": top_words,
        "elapsed_sec": time.time() - t0,
        "artifacts": {"csv": str(csv_path)},
    }
    (ART / "e1_starts.json").write_text(json.dumps(start_stats, indent=2))
    (ART / "e1_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({"gates": gates, "predictions": summary["predictions"]}, indent=2))
    print(f"WROTE {csv_path} runs={len(all_runs)}")
    return 0 if gates["E1-G1"] == "PASS" and gates["E1-G2"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
