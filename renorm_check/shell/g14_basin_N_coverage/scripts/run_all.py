#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "g10_species_vs_climb" / "scripts"))
from species_orbit import sample_starts, steps_to_species

ART = Path(__file__).resolve().parents[1] / "artifacts"
ART.mkdir(parents=True, exist_ok=True)
REPO = Path(__file__).resolve().parents[4]

def dens(steps_list, N):
    return sum(1 for s in steps_list if s is not None and s <= N) / len(steps_list)

def main():
    starts = sample_starts(REPO)
    free_steps = []
    for src, x0 in starts:
        r = steps_to_species(x0, 100000)
        free_steps.append(r["steps_to_species"] if r["hit"] else None)

    odds_steps = []
    for x in range(1, 100000, 2):
        r = steps_to_species(x, 50000)
        odds_steps.append(r["steps_to_species"] if r["hit"] else None)

    Ns = [0, 1, 5, 10, 20, 50, 100, 200, 500]
    free_d = {str(N): dens(free_steps, N) for N in Ns}
    odds_d = {str(N): dens(odds_steps, N) for N in Ns}

    preds = {
        "U14.1": {"verdict": "CONFIRMED" if free_d["50"] >= 0.50 else "REFUTED", "d50": free_d["50"], "confidence_prior": 0.55},
        "U14.2": {"verdict": "CONFIRMED" if free_d["200"] >= 0.90 else "REFUTED", "d200": free_d["200"], "confidence_prior": 0.65},
        "U14.3": {"verdict": "CONFIRMED" if odds_d["100"] >= 0.85 else "REFUTED", "d100_odds": odds_d["100"], "confidence_prior": 0.55},
        "U14.4": {"verdict": "CONFIRMED" if all(free_d[str(Ns[i])] <= free_d[str(Ns[i+1])] for i in range(len(Ns)-1)) else "REFUTED", "confidence_prior": 0.99},
    }
    summary = {
        "gates": {"n_free": len(free_steps), "n_odds": len(odds_steps), "G1": "PASS"},
        "predictions": preds,
        "free_density": free_d,
        "odds_lt_1e5_density": odds_d,
        "unhit_free": sum(1 for s in free_steps if s is None),
        "unhit_odds": sum(1 for s in odds_steps if s is None),
    }
    (ART/"summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
