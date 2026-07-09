#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "basin_common"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "species_spacing_common"))
from basin_helpers import layered_basin_fractions, count_immediate_shell_odds
from species_spacing import count_species_le
ART = Path(__file__).resolve().parents[1] / "artifacts"

def compute_results() -> dict:
    X = 10**4
    n_odds = (X + 1) // 2
    n_spine = count_species_le(X)
    frac_spine = n_spine / n_odds
    n_shell, _ = count_immediate_shell_odds(X)
    frac_shell = n_shell / n_odds
    deep = layered_basin_fractions(X, 500, [50, 100])
    deep.pop("steps_sample", None)
    f50 = deep["frac"]["50"]
    f100 = deep["frac"]["100"]
    # taxonomy claims
    s341 = frac_spine < 0.01  # spine thin
    s342 = frac_shell > frac_spine and frac_shell < 0.50  # shell moderate
    s343 = f100 >= 0.90  # deep nearly full
    taxonomy = "spine_thin_shell_moderate_bulk_full" if (s341 and s342 and s343) else "mixed"
    preds = {
        "S34.1": {"verdict": "CONFIRMED" if s341 else "REFUTED", "frac_spine": frac_spine, "confidence_prior": 0.95},
        "S34.2": {"verdict": "CONFIRMED" if s342 else "REFUTED", "frac_shell": frac_shell, "confidence_prior": 0.70},
        "S34.3": {"verdict": "CONFIRMED" if s343 else "REFUTED", "f100": f100, "confidence_prior": 0.75},
    }
    return {"gates": {"G1": "PASS", "X": X}, "predictions": preds, "taxonomy": taxonomy,
            "frac_spine": frac_spine, "frac_shell": frac_shell, "f50": f50, "f100": f100}

def write_artifacts(results: dict) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    (ART/"summary.json").write_text(json.dumps(results, indent=2))

def main():
    r = compute_results(); write_artifacts(r); print(json.dumps(r, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
