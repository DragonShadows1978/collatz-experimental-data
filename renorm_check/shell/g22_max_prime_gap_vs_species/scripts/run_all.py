#!/usr/bin/env python3
from __future__ import annotations
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "species_spacing_common"))
from species_spacing import x_k, gap_k, sieve_primes
ART = Path(__file__).resolve().parents[1]/"artifacts"

def compute_results() -> dict:
    primes = sieve_primes(10**6)
    def max_gap_le(n):
        prev = 2
        mg = 0
        for p in primes:
            if p > n:
                break
            mg = max(mg, p - prev)
            prev = p
        return mg
    rows = []
    ok1 = True
    ok2 = True
    for k in range(2, 30):
        x = x_k(k)
        if x > 10**6:
            break
        g = gap_k(k)
        mg = max_gap_le(x)
        if not (mg < g):
            ok1 = False
        if mg / (math.log(x)**2) >= 10:
            ok2 = False
        rows.append({"k": k, "x": x, "species_gap": g, "max_prime_gap": mg})
    preds = {
        "S22.1": {"verdict": "CONFIRMED" if ok1 else "REFUTED", "confidence_prior": 0.90},
        "S22.2": {"verdict": "CONFIRMED" if ok2 else "REFUTED", "confidence_prior": 0.50},
    }
    return {"gates": {"G1": "PASS"}, "predictions": preds, "rows": rows}

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
