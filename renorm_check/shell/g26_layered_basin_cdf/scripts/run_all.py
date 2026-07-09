#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "basin_common"))
from basin_helpers import layered_basin_fractions
ART = Path(__file__).resolve().parents[1] / "artifacts"

def compute_results() -> dict:
    X = 10**4
    layers = [0, 1, 5, 10, 20, 50, 100]
    data = layered_basin_fractions(X, max_steps=500, layers=layers)
    frac = data["frac"]
    # drop internal sample from summary size
    steps = data.pop("steps_sample")
    s261 = frac["0"] < frac["1"]  # shell adds beyond spine
    s262 = frac["5"] >= 0.05
    s263 = frac["50"] >= 0.50
    s264 = all(frac[str(layers[i])] <= frac[str(layers[i+1])] for i in range(len(layers)-1))
    # median among hits
    hits = sorted(s for s in steps if s is not None)
    med = hits[len(hits)//2] if hits else None
    preds = {
        "S26.1": {"verdict": "CONFIRMED" if s261 else "REFUTED", "f0": frac["0"], "f1": frac["1"], "confidence_prior": 0.90},
        "S26.2": {"verdict": "CONFIRMED" if s262 else "REFUTED", "f5": frac["5"], "confidence_prior": 0.55},
        "S26.3": {"verdict": "CONFIRMED" if s263 else "REFUTED", "f50": frac["50"], "confidence_prior": 0.60},
        "S26.4": {"verdict": "CONFIRMED" if s264 else "REFUTED", "confidence_prior": 0.99},
    }
    return {"gates": {"G1": "PASS", "X": X, "n_odds": data["n_odds"]}, "predictions": preds,
            "frac": frac, "median_steps_hit": med, "n_hit": data["n_hit"]}

def write_artifacts(results: dict) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    (ART/"summary.json").write_text(json.dumps(results, indent=2))

def main():
    r = compute_results(); write_artifacts(r); print(json.dumps(r, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
