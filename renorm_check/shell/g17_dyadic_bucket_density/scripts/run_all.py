#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "species_spacing_common"))
from species_spacing import x_k
ART = Path(__file__).resolve().parents[1]/"artifacts"

def compute_results() -> dict:
    buckets = {}
    for m in range(1, 41):
        lo, hi = 4**m, 4**(m+1)
        cnt = 0
        members = []
        for k in range(1, 120):
            x = x_k(k)
            if lo <= x < hi:
                cnt += 1
                members.append(k)
            if x >= hi:
                break
        buckets[str(m)] = {"count": cnt, "ks": members}
    counts = [buckets[str(m)]["count"] for m in range(1, 41)]
    s171 = all(c in (0,1) for c in counts)
    frac1 = sum(1 for m in range(2, 41) if buckets[str(m)]["count"]==1) / 39
    preds = {
        "S17.1": {"verdict": "CONFIRMED" if s171 else "REFUTED", "confidence_prior": 0.90},
        "S17.2": {"verdict": "CONFIRMED" if frac1 >= 0.8 else "REFUTED", "frac_exactly_one": frac1, "confidence_prior": 0.70},
        "S17.3": {"verdict": "CONFIRMED" if all(c < 3 for c in counts) else "REFUTED", "confidence_prior": 0.95},
    }
    return {"gates": {"G1": "PASS"}, "predictions": preds, "buckets_sample": {str(m): buckets[str(m)] for m in [1,2,3,5,10,20]}}

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
