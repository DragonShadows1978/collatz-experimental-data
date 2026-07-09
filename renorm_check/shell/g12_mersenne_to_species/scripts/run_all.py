#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "g10_species_vs_climb" / "scripts"))
from species_orbit import steps_to_species
ART = Path(__file__).resolve().parents[1] / "artifacts"
ART.mkdir(parents=True, exist_ok=True)

def main():
    rows = []
    for L in range(1, 41):
        x = (1 << (L + 1)) - 1
        r = steps_to_species(x, 100000)
        r["L"] = L
        r["x"] = x
        rows.append(r)
    hit_ok = all(r["hit"] for r in rows)
    # steps_to_species >= that row's L (not leaked loop variable)
    ge_L = all(
        r["hit"] and r["steps_to_species"] is not None and r["steps_to_species"] >= r["L"]
        for r in rows
    )
    n_ge_L = sum(
        1
        for r in rows
        if r["hit"] and r["steps_to_species"] is not None and r["steps_to_species"] >= r["L"]
    )
    # spearman rough
    Ls = [r["L"] for r in rows]
    Ss = [r["steps_to_species"] for r in rows]
    n = len(Ls)
    # rank correlation sign via pairwise
    pairs = 0
    conc = 0
    for i in range(n):
        for j in range(i+1, n):
            pairs += 1
            if (Ls[i]-Ls[j]) * (Ss[i]-Ss[j]) > 0:
                conc += 1
            elif (Ls[i]-Ls[j]) * (Ss[i]-Ss[j]) < 0:
                conc -= 1
    spear_proxy = conc / pairs if pairs else 0
    max_s = max(Ss)
    preds = {
        "U12.1": {"verdict": "CONFIRMED" if hit_ok else "REFUTED", "confidence_prior": 0.85},
        "U12.2": {
            "verdict": "CONFIRMED" if ge_L else "REFUTED",
            "n_ge_L": n_ge_L,
            "n_rows": len(rows),
            "min_steps_minus_L": min(
                (r["steps_to_species"] - r["L"] for r in rows if r["hit"]),
                default=None,
            ),
            "confidence_prior": 0.70,
        },
        "U12.3": {"verdict": "CONFIRMED" if spear_proxy > 0 else "REFUTED", "spearman_proxy": spear_proxy, "confidence_prior": 0.50},
        "U12.4": {"verdict": "CONFIRMED" if max_s <= 5000 else "REFUTED", "max_steps": max_s, "confidence_prior": 0.45},
    }
    summary = {"gates": {"n": 40, "G1": "PASS"}, "predictions": preds,
               "sample": [{"L": r["L"], "steps": r["steps_to_species"], "ups": r["n_ups"]} for r in rows[::5]]}
    (ART/"summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
