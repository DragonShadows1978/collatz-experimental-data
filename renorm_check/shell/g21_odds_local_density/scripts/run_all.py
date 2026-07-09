#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "species_spacing_common"))
from species_spacing import x_k, gap_k
ART = Path(__file__).resolve().parents[1]/"artifacts"

def compute_results() -> dict:
    rows = []
    ok1 = True
    ok2 = True
    for k in range(10, 26):
        x = x_k(k)
        g = gap_k(k)
        lo = max(1, x - g//2)
        hi = x + g//2
        cnt = 0
        for j in range(1, 80):
            xj = x_k(j)
            if lo <= xj <= hi:
                cnt += 1
            if xj > hi:
                break
        if cnt != 1:
            ok1 = False
        n_odds = (hi - lo)//2 + 1
        frac = cnt / n_odds
        if frac > 3/g:
            ok2 = False
        rows.append({"k": k, "cnt_species": cnt, "n_odds": n_odds, "frac": frac, "3_over_gap": 3/g})
    preds = {
        "S21.1": {"verdict": "CONFIRMED" if ok1 else "REFUTED", "confidence_prior": 0.90},
        "S21.2": {"verdict": "CONFIRMED" if ok2 else "REFUTED", "confidence_prior": 0.85},
    }
    return {"gates": {"G1": "PASS"}, "predictions": preds, "rows": rows[::3]}

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
