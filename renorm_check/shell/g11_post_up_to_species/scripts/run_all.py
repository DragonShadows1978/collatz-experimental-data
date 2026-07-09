#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "g10_species_vs_climb" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "g4_drop_gate_streaks" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "g2_a1_climb_realizability" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "descent_rule"))
from descent_common import is_one_step_species
from g2_core import odd_step
from species_orbit import sample_starts, steps_to_species
from g4_core import walk_with_C_before

ART = Path(__file__).resolve().parents[1] / "artifacts"
ART.mkdir(parents=True, exist_ok=True)
REPO = Path(__file__).resolve().parents[4]

def post_last_up_to_species(x0, max_steps=100000):
    steps = walk_with_C_before(x0, max_steps)
    last_up_k = None
    for s in steps:
        if s["upcrossing"]:
            last_up_k = s["k"]
    # continue from end of steps if needed for species
    r = steps_to_species(x0, max_steps)
    if not r["hit"] or last_up_k is None:
        return {"has_up": last_up_k is not None, "hit": r["hit"], "post": None,
                "steps_to_species": r["steps_to_species"], "n_ups": r["n_ups"]}
    post = r["steps_to_species"] - last_up_k - 1  # steps after last up index until species
    # species is checked at beginning of step k = steps_to_species, so after last_up_k
    # number of steps from after last up to species = steps_to_species - (last_up_k+1)
    post = r["steps_to_species"] - (last_up_k + 1)
    if post < 0:
        post = 0
    return {"has_up": True, "hit": True, "post": post, "last_up_k": last_up_k,
            "steps_to_species": r["steps_to_species"], "n_ups": r["n_ups"]}

def main():
    starts = sample_starts(REPO)
    rows = []
    for src, x0 in starts:
        r = post_last_up_to_species(x0)
        r["src"] = src
        r["start"] = x0
        rows.append(r)
    with_up = [r for r in rows if r["has_up"] and r["hit"] and r["post"] is not None]
    u111 = all(r["post"] <= r["steps_to_species"] for r in with_up)
    deep = [r for r in with_up if r["n_ups"] >= 5]
    if deep:
        ratios = [r["post"] / max(r["steps_to_species"], 1) for r in deep]
        mean_r = sum(ratios) / len(ratios)
    else:
        mean_r = None
    posts = sorted(r["post"] for r in with_up)
    med = posts[len(posts)//2] if posts else None
    frac100 = sum(1 for r in with_up if r["post"] <= 100) / len(with_up) if with_up else 0
    preds = {
        "U11.1": {"verdict": "CONFIRMED" if u111 else "REFUTED", "confidence_prior": 0.95},
        "U11.2": {"verdict": "CONFIRMED" if mean_r is not None and mean_r <= 0.60 else ("INCONCLUSIVE" if mean_r is None else "REFUTED"),
                  "mean_ratio": mean_r, "n": len(deep), "confidence_prior": 0.55},
        "U11.3": {"verdict": "CONFIRMED" if med is not None and med <= 50 else "REFUTED", "median_post": med, "confidence_prior": 0.50},
        "U11.4": {"verdict": "CONFIRMED" if frac100 >= 0.80 else "REFUTED", "frac_post_le_100": frac100, "confidence_prior": 0.55},
    }
    summary = {"gates": {"n_with_up": len(with_up), "G1": "PASS" if len(with_up) >= 50 else "FAIL"}, "predictions": preds}
    (ART/"summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
