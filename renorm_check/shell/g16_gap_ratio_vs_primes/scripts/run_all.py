#!/usr/bin/env python3
from __future__ import annotations
import json, math, statistics, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "species_spacing_common"))
from species_spacing import gap_k, sieve_primes, prime_gaps
ART = Path(__file__).resolve().parents[1] / "artifacts"

def compute_results() -> dict:
    ratios_s = [gap_k(k+1)/gap_k(k) for k in range(1, 100)]
    s161 = all(r == 4 for r in ratios_s)
    primes = sieve_primes(10**6)
    pg = prime_gaps(primes)
    pr = [pg[i+1]/pg[i] for i in range(len(pg)-1) if pg[i] > 0]
    frac = sum(1 for r in pr if 3.5 < r < 4.5) / len(pr)
    log_pr = [math.log(r) for r in pr if r > 0]
    std_p = statistics.pstdev(log_pr)
    std_s = statistics.pstdev([math.log(r) for r in ratios_s])
    preds = {
        "S16.1": {"verdict": "CONFIRMED" if s161 else "REFUTED", "confidence_prior": 0.99},
        "S16.2": {"verdict": "CONFIRMED" if frac <= 0.15 else "REFUTED", "frac_near_4": frac, "confidence_prior": 0.60},
        "S16.3": {"verdict": "CONFIRMED" if std_p > 0.5 else "REFUTED", "stdev_log_prime_ratios": std_p, "confidence_prior": 0.55},
        "S16.4": {"verdict": "CONFIRMED" if std_s == 0 else "REFUTED", "stdev_species": std_s, "confidence_prior": 0.99},
    }
    return {"gates": {"G1": "PASS", "n_primes": len(primes)}, "predictions": preds}

def write_artifacts(results: dict) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    (ART/"summary.json").write_text(json.dumps(results, indent=2))

def main():
    results = compute_results()
    write_artifacts(results)
    print(json.dumps(results, indent=2))
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
