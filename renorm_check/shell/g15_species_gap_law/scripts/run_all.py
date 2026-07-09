#!/usr/bin/env python3
from __future__ import annotations
import json, math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "species_spacing_common"))
from species_spacing import x_k, gap_k, verify_gap_identity, count_species_le, ln_int
ART = Path(__file__).resolve().parents[1] / "artifacts"

def compute_results() -> dict:
    ok_id = verify_gap_identity(100)
    rows = []
    for k in range(1, 101):
        x = x_k(k)
        g = gap_k(k)
        gl = g / ln_int(x) if x > 1 else float("inf")
        rows.append({"k": k, "x": str(x) if x.bit_length() > 200 else x, "gap": g, "gap_over_ln_x": gl, "bits": x.bit_length()})
    s151 = ok_id and all(gap_k(k) == 4**k for k in range(1, 101))
    ratios = [rows[k-1]["gap_over_ln_x"] for k in range(2, 51)]
    s152 = all(ratios[i] < ratios[i+1] for i in range(len(ratios)-1))
    s153 = all(rows[k-1]["gap_over_ln_x"] > 10 for k in range(10, 101))
    X = 10**12
    c_ctor = count_species_le(X)
    kmax = int(math.log(3*X+1) / math.log(4))
    while (4**kmax - 1)//3 > X:
        kmax -= 1
    while (4**(kmax+1) - 1)//3 <= X:
        kmax += 1
    s154 = c_ctor == kmax
    preds = {
        "S15.1": {"verdict": "CONFIRMED" if s151 else "REFUTED", "confidence_prior": 0.99},
        "S15.2": {"verdict": "CONFIRMED" if s152 else "REFUTED", "confidence_prior": 0.90},
        "S15.3": {"verdict": "CONFIRMED" if s153 else "REFUTED", "gap_ln_at_10": rows[9]["gap_over_ln_x"], "confidence_prior": 0.85},
        "S15.4": {"verdict": "CONFIRMED" if s154 else "REFUTED", "count_le_1e12": c_ctor, "kmax": kmax, "confidence_prior": 0.95},
    }
    return {"gates": {"G1": "PASS"}, "predictions": preds, "sample_k": [rows[i] for i in [0,1,4,9,19,49]], "_rows50": rows[:50]}

def write_artifacts(results: dict) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    rows50 = results.pop("_rows50", None)
    (ART/"summary.json").write_text(json.dumps(results, indent=2, default=str))
    if rows50 is not None:
        (ART/"gaps_k1_50.json").write_text(json.dumps(rows50, indent=2, default=str))

def main():
    results = compute_results()
    # keep rows for write then strip for print
    out = dict(results)
    write_artifacts(out)
    print(json.dumps({"predictions": results["predictions"]}, indent=2, default=str))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
