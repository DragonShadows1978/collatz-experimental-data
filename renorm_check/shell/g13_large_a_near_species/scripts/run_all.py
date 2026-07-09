#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "g10_species_vs_climb" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "g2_a1_climb_realizability" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "descent_rule"))
from descent_common import is_one_step_species
from g2_core import odd_step
from species_orbit import sample_starts

ART = Path(__file__).resolve().parents[1] / "artifacts"
ART.mkdir(parents=True, exist_ok=True)
REPO = Path(__file__).resolve().parents[4]

def last_a_before_species(x0, max_steps=100000):
    x = x0
    if x % 2 == 0:
        while x % 2 == 0 and x > 0:
            x //= 2
    if x == 1 or is_one_step_species(x)[0]:
        return None  # already there
    last_a = None
    all_a = []
    for k in range(max_steps):
        if x == 1 or is_one_step_species(x)[0]:
            return {"last_a": last_a, "all_a": all_a, "steps": k}
        nxt, a = odd_step(x)
        all_a.append(a)
        last_a = a
        x = nxt
    return None

def main():
    starts = sample_starts(REPO)
    lasts = []
    means_all = []
    for src, x0 in starts:
        r = last_a_before_species(x0)
        if r is None or r["last_a"] is None:
            continue
        lasts.append(r["last_a"])
        means_all.append(sum(r["all_a"]) / len(r["all_a"]))
    n = len(lasts)
    mean_last = sum(lasts) / n
    frac_ge2 = sum(1 for a in lasts if a >= 2) / n
    frac_a1 = sum(1 for a in lasts if a == 1) / n
    mean_all = sum(means_all) / n
    preds = {
        "U13.1": {"verdict": "CONFIRMED" if mean_last >= 3 else "REFUTED", "mean_last_a": mean_last, "n": n, "confidence_prior": 0.55},
        "U13.2": {"verdict": "CONFIRMED" if frac_ge2 >= 0.50 else "REFUTED", "frac_a_ge2": frac_ge2, "confidence_prior": 0.70},
        "U13.3": {"verdict": "CONFIRMED" if frac_a1 <= 0.40 else "REFUTED", "frac_a1": frac_a1, "confidence_prior": 0.50},
        "U13.4": {"verdict": "CONFIRMED" if mean_last > mean_all else "REFUTED", "mean_last": mean_last, "mean_all_steps": mean_all, "confidence_prior": 0.60},
    }
    from collections import Counter
    summary = {"gates": {"n": n, "G1": "PASS" if n >= 100 else "FAIL"}, "predictions": preds,
               "last_a_hist": dict(Counter(lasts))}
    (ART/"summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
