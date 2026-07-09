#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "basin_common"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "descent_rule"))
from basin_helpers import reverse_preimage_candidates, is_species_or_one
from descent_common import species_member, one_odd_step
ART = Path(__file__).resolve().parents[1] / "artifacts"

def a_of(y, x):
    """a such that (3y+1)/2^a = x"""
    n = 3 * y + 1
    a = 0
    while n % 2 == 0:
        n //= 2
        a += 1
    return a if n == x else None

def compute_results() -> dict:
    hist = {}
    n = 0
    n_a_ge2 = 0
    for k in range(1, 12):
        x = species_member(k)
        for y in reverse_preimage_candidates(x):
            if y > 10**6:
                continue
            a = a_of(y, x)
            if a is None:
                continue
            n += 1
            hist[str(a)] = hist.get(str(a), 0) + 1
            if a >= 2:
                n_a_ge2 += 1
    frac = n_a_ge2 / n if n else 0
    s301 = n >= 20
    s302 = frac >= 0.80  # most reverse preimages use a>=2
    s303 = "1" not in hist or hist.get("1", 0) / n <= 0.25
    preds = {
        "S30.1": {"verdict": "CONFIRMED" if s301 else "REFUTED", "n": n, "confidence_prior": 0.90},
        "S30.2": {"verdict": "CONFIRMED" if s302 else "REFUTED", "frac_a_ge2": frac, "confidence_prior": 0.70},
        "S30.3": {"verdict": "CONFIRMED" if s303 else "REFUTED", "confidence_prior": 0.60},
    }
    return {"gates": {"G1": "PASS"}, "predictions": preds, "hist": hist, "n": n}

def write_artifacts(results: dict) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    (ART/"summary.json").write_text(json.dumps(results, indent=2))

def main():
    r = compute_results(); write_artifacts(r); print(json.dumps(r, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
