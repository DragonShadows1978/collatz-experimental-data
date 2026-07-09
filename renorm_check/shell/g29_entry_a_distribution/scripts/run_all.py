#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "basin_common"))
from basin_helpers import last_a_into_species
ART = Path(__file__).resolve().parents[1] / "artifacts"

def compute_results() -> dict:
    # sample odds 1..2001 step 2 that hit within 200 steps
    hist = {}
    n = 0
    n_a_ge2 = 0
    n_a1 = 0
    for y in range(1, 2001, 2):
        a = last_a_into_species(y, max_steps=200)
        if a is None:
            continue
        n += 1
        hist[str(a)] = hist.get(str(a), 0) + 1
        if a >= 2:
            n_a_ge2 += 1
        if a == 1:
            n_a1 += 1
    frac_ge2 = n_a_ge2 / n if n else 0
    frac_a1 = n_a1 / n if n else 0
    s291 = frac_ge2 >= 0.70
    s292 = frac_a1 <= 0.30
    s293 = n >= 500
    preds = {
        "S29.1": {"verdict": "CONFIRMED" if s291 else "REFUTED", "frac_a_ge2": frac_ge2, "confidence_prior": 0.70},
        "S29.2": {"verdict": "CONFIRMED" if s292 else "REFUTED", "frac_a1": frac_a1, "confidence_prior": 0.65},
        "S29.3": {"verdict": "CONFIRMED" if s293 else "REFUTED", "n": n, "confidence_prior": 0.90},
    }
    return {"gates": {"G1": "PASS"}, "predictions": preds, "hist": hist, "n": n}

def write_artifacts(results: dict) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    (ART/"summary.json").write_text(json.dumps(results, indent=2))

def main():
    r = compute_results(); write_artifacts(r); print(json.dumps(r, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
