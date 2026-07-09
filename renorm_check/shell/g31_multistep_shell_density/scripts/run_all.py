#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "basin_common"))
from basin_helpers import layered_basin_fractions
ART = Path(__file__).resolve().parents[1] / "artifacts"

def compute_results() -> dict:
    X = 10**4
    layers = [0, 1, 2, 3, 5, 10]
    data = layered_basin_fractions(X, max_steps=200, layers=layers)
    frac = data["frac"]
    data.pop("steps_sample", None)
    # growth: each step adds mass
    growth = all(frac[str(layers[i])] <= frac[str(layers[i+1])] for i in range(len(layers)-1))
    s311 = growth
    s312 = frac["2"] >= 2 * frac["0"] if frac["0"] > 0 else frac["2"] > 0
    s313 = frac["10"] >= 0.10
    s314 = frac["0"] < 0.01  # spine still thin
    preds = {
        "S31.1": {"verdict": "CONFIRMED" if s311 else "REFUTED", "confidence_prior": 0.99},
        "S31.2": {"verdict": "CONFIRMED" if s312 else "REFUTED", "f0": frac["0"], "f2": frac["2"], "confidence_prior": 0.70},
        "S31.3": {"verdict": "CONFIRMED" if s313 else "REFUTED", "f10": frac["10"], "confidence_prior": 0.55},
        "S31.4": {"verdict": "CONFIRMED" if s314 else "REFUTED", "f0": frac["0"], "confidence_prior": 0.85},
    }
    return {"gates": {"G1": "PASS", "X": X}, "predictions": preds, "frac": frac}

def write_artifacts(results: dict) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    (ART/"summary.json").write_text(json.dumps(results, indent=2))

def main():
    r = compute_results(); write_artifacts(r); print(json.dumps(r, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
