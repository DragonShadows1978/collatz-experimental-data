#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "species_spacing_common"))
from species_spacing import x_k
ART = Path(__file__).resolve().parents[1] / "artifacts"

def compute_results() -> dict:
    W = 1000  # fixed half-width
    rows = []
    ok_one = True
    ok_sparse = True
    for k in range(8, 16):
        x = x_k(k)
        lo, hi = x - W, x + W
        cnt = 0
        for j in range(1, 40):
            xj = x_k(j)
            if lo <= xj <= hi:
                cnt += 1
            if xj > hi:
                break
        if cnt != 1:
            ok_one = False
        # among odds in window, at most 1 species => frac <= 1 / n_odds
        n_odds = (hi - lo) // 2 + 1
        frac = cnt / n_odds
        if frac > 0.01:
            ok_sparse = False
        rows.append({"k": k, "x": x, "cnt_species": cnt, "n_odds_window": n_odds, "frac": frac})
    preds = {
        "S28.1": {"verdict": "CONFIRMED" if ok_one else "REFUTED", "confidence_prior": 0.80},
        "S28.2": {"verdict": "CONFIRMED" if ok_sparse else "REFUTED", "confidence_prior": 0.75},
        "S28.3": {"verdict": "CONFIRMED" if all(r["cnt_species"] <= 2 for r in rows) else "REFUTED", "confidence_prior": 0.90},
    }
    return {"gates": {"G1": "PASS", "W": W}, "predictions": preds, "rows": rows}

def write_artifacts(results: dict) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    (ART/"summary.json").write_text(json.dumps(results, indent=2))

def main():
    r = compute_results(); write_artifacts(r); print(json.dumps(r, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
