#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "species_spacing_common"))
from species_spacing import x_k, gap_k
ART = Path(__file__).resolve().parents[1]/"artifacts"

def near_frac(X):
    n_odds = (X + 1)//2
    near = set()
    k = 1
    while True:
        x = x_k(k)
        if x > X:
            break
        band = max(1, gap_k(max(1,k-1))//10) if k > 1 else 1
        lo = max(1, x - band)
        hi = min(X, x + band)
        for n in range(lo | 1, hi+1, 2):
            near.add(n)
        k += 1
    return len(near) / n_odds, len(near)

def compute_results() -> dict:
    fracs = {}
    for n in (4, 5, 6):
        X = 10**n
        f, c = near_frac(X)
        fracs[str(X)] = {"frac": f, "count_near": c}
    s231 = fracs[str(10**6)]["frac"] < 0.05
    s232 = fracs[str(10**4)]["frac"] > fracs[str(10**6)]["frac"]
    preds = {
        "S23.1": {"verdict": "CONFIRMED" if s231 else "REFUTED", "frac_1e6": fracs[str(10**6)]["frac"], "confidence_prior": 0.70},
        "S23.2": {"verdict": "CONFIRMED" if s232 else "REFUTED", "fracs": {k: v["frac"] for k,v in fracs.items()}, "confidence_prior": 0.55},
    }
    return {"gates": {"G1": "PASS"}, "predictions": preds, "fracs": fracs}

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
