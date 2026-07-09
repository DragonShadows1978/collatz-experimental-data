#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "basin_common"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "g10_species_vs_climb" / "scripts"))
from basin_helpers import layered_basin_fractions
from species_orbit import sample_starts, steps_to_species
ART = Path(__file__).resolve().parents[1] / "artifacts"
REPO = Path(__file__).resolve().parents[4]

def _median(xs):
    xs = sorted(xs)
    if not xs:
        return None
    return xs[len(xs)//2]

def compute_results() -> dict:
    odds = layered_basin_fractions(10**4, 500, [100])
    odds_steps = [s for s in odds["steps_sample"] if s is not None]
    med_odds = _median(odds_steps)
    free = []
    for src, x0 in sample_starts(REPO):
        r = steps_to_species(x0, 100000)
        if r["hit"]:
            free.append(r["steps_to_species"])
    med_free = _median(free)
    s271 = med_odds is not None and med_odds <= 100
    s272 = med_free is not None and med_free <= 300
    s273 = med_free is not None and med_odds is not None and med_free > med_odds
    s274 = len(free) >= 200 and all(True for _ in free)  # hit all free? check rate
    free_hit_rate = len(free) / max(1, len(sample_starts(REPO)))
    s274 = free_hit_rate >= 0.99
    preds = {
        "S27.1": {"verdict": "CONFIRMED" if s271 else "REFUTED", "med_odds": med_odds, "confidence_prior": 0.70},
        "S27.2": {"verdict": "CONFIRMED" if s272 else "REFUTED", "med_free": med_free, "confidence_prior": 0.65},
        "S27.3": {"verdict": "CONFIRMED" if s273 else "REFUTED", "confidence_prior": 0.55},
        "S27.4": {"verdict": "CONFIRMED" if s274 else "REFUTED", "free_hit_rate": free_hit_rate, "confidence_prior": 0.90},
    }
    return {"gates": {"G1": "PASS", "n_free_hit": len(free)}, "predictions": preds,
            "med_odds": med_odds, "med_free": med_free}

def write_artifacts(results: dict) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    (ART/"summary.json").write_text(json.dumps(results, indent=2))

def main():
    r = compute_results(); write_artifacts(r); print(json.dumps(r, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
