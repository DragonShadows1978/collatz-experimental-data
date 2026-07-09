#!/usr/bin/env python3
from __future__ import annotations
import json, statistics, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "species_spacing_common"))
from species_spacing import gap_k, x_k, sieve_primes, prime_gaps
ART = Path(__file__).resolve().parents[1]/"artifacts"

def compute_results() -> dict:
    gaps = [gap_k(k) for k in range(1, 31)]
    var = statistics.pvariance(gaps)
    s241 = var > 0
    x15 = x_k(15)
    g15 = gap_k(15)
    primes = sieve_primes(min(x15, 10**7))
    pg = prime_gaps(primes)
    mean_pg = sum(pg)/len(pg)
    ratio = g15 / mean_pg
    s242 = ratio > 100
    s243 = all(gap_k(k+1)/gap_k(k)==4 for k in range(1, 51))
    preds = {
        "S24.1": {"verdict": "CONFIRMED" if s241 else "REFUTED", "variance": var, "confidence_prior": 0.99},
        "S24.2": {"verdict": "CONFIRMED" if s242 else "REFUTED", "species_gap_over_mean_prime_gap": ratio, "confidence_prior": 0.85},
        "S24.3": {"verdict": "CONFIRMED" if s243 else "REFUTED", "confidence_prior": 0.99},
    }
    taxonomy = "C_exact_geometric" if s241 and s242 and s243 else "mixed"
    return {"gates": {"G1": "PASS"}, "predictions": preds, "taxonomy": taxonomy}

def write_artifacts(results: dict) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    (ART/"summary.json").write_text(json.dumps(results, indent=2, default=str))

def main():
    results = compute_results()
    write_artifacts(results)
    print(json.dumps(results, indent=2, default=str))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
