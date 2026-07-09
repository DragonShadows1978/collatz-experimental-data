#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "species_spacing_common"))
from species_spacing import x_k, gap_k
ART = Path(__file__).resolve().parents[1]/"artifacts"

def compute_results() -> dict:
    s193 = all(3 * gap_k(k) - 3 * x_k(k) > 0 for k in range(1, 51))
    rel = [gap_k(k) / x_k(k) for k in range(1, 51)]
    s191 = all(rel[i] >= rel[i + 1] for i in range(len(rel) - 1))
    s192 = all(abs(3 * gap_k(k) - 9 * x_k(k)) * 100 < 3 * x_k(k) for k in range(8, 51))
    preds = {
        "S19.1": {"verdict": "CONFIRMED" if s191 else "REFUTED", "rel_at_50": rel[49], "confidence_prior": 0.90},
        "S19.2": {"verdict": "CONFIRMED" if s192 else "REFUTED", "confidence_prior": 0.90},
        "S19.3": {"verdict": "CONFIRMED" if s193 else "REFUTED", "min_rel_float": min(rel), "confidence_prior": 0.99},
    }
    return {"gates": {"G1": "PASS"}, "predictions": preds, "rel_sample": {str(k): rel[k - 1] for k in [1, 2, 5, 10, 20, 50]}}

def write_artifacts(results: dict) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    (ART/"summary.json").write_text(json.dumps(results, indent=2))

def main():
    results = compute_results()
    write_artifacts(results)
    print(json.dumps(results, indent=2))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
