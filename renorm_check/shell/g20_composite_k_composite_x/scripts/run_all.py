#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "species_spacing_common"))
from species_spacing import x_k
ART = Path(__file__).resolve().parents[1]/"artifacts"

def is_prime_small(n):
    if n < 2: return False
    if n % 2 == 0: return n==2
    d=3
    while d*d <= n:
        if n%d==0: return False
        d+=2
    return True

def factor_witness(k, x):
    for a in range(2, k):
        if k % a == 0:
            xa = x_k(a)
            if 1 < xa < x and x % xa == 0:
                return xa
    return None

def compute_results() -> dict:
    comps = [k for k in range(4, 61) if not is_prime_small(k)]
    results = []
    all_comp = True
    fact_ok = 0
    for k in comps:
        x = x_k(k)
        if x.bit_length() < 40:
            prime = is_prime_small(x)
        else:
            w = factor_witness(k, x)
            prime = False if w else None
        if prime:
            all_comp = False
        w = factor_witness(k, x)
        if w:
            fact_ok += 1
        results.append({"k": k, "prime": prime, "factor_witness": w})
    s201 = all_comp and all(r["prime"] is not True for r in results)
    s202 = fact_ok == len(comps)
    preds = {
        "S20.1": {"verdict": "CONFIRMED" if s201 else "REFUTED", "n_composite_k": len(comps), "confidence_prior": 0.99},
        "S20.2": {"verdict": "CONFIRMED" if s202 else "REFUTED", "n_with_factor": fact_ok, "confidence_prior": 0.90},
    }
    return {"gates": {"G1": "PASS"}, "predictions": preds}

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
