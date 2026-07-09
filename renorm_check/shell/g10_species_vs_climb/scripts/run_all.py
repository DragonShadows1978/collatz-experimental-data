#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from species_orbit import (  # noqa: E402
    is_one_step_species,
    one_odd_step,
    sample_starts,
    species_member,
    steps_to_species,
)
ART = Path(__file__).resolve().parents[1] / "artifacts"
ART.mkdir(parents=True, exist_ok=True)
REPO = Path(__file__).resolve().parents[4]

def main():
    # cert sanity
    for k in range(1, 30):
        x = species_member(k)
        assert is_one_step_species(x)[0]
        assert one_odd_step(x) == 1

    starts = sample_starts(REPO)
    rows = []
    for src, x0 in starts:
        r = steps_to_species(x0, 100000)
        r["src"] = src
        r["start"] = x0
        rows.append(r)

    hits = [r for r in rows if r["hit"]]
    hit_rate = len(hits) / len(rows)
    u102_ok = all(
        r["steps_to_species"] is not None and r["steps_to_species"] >= r["n_ups"]
        for r in hits
    )
    deep = [r for r in hits if r["n_ups"] >= 10]
    if deep:
        ratios = [r["steps_to_species"] / max(r["n_ups"], 1) for r in deep]
        mean_ratio = sum(ratios) / len(ratios)
    else:
        mean_ratio = None
    u103_ok = mean_ratio is not None and 2 <= mean_ratio <= 50

    # species members
    sp_ok = all(steps_to_species(species_member(k), 10)["steps_to_species"] == 0 for k in range(1, 20))

    preds = {
        "U10.1": {"verdict": "CONFIRMED" if hit_rate == 1.0 else ("REFUTED" if hit_rate < 0.99 else "INCONCLUSIVE"),
                  "hit_rate": hit_rate, "n": len(rows), "confidence_prior": 0.85},
        "U10.2": {"verdict": "CONFIRMED" if u102_ok else "REFUTED", "confidence_prior": 0.70},
        "U10.3": {"verdict": "CONFIRMED" if u103_ok else ("INCONCLUSIVE" if mean_ratio is None else "REFUTED"),
                  "mean_ratio": mean_ratio, "n_deep": len(deep), "confidence_prior": 0.50},
        "U10.4": {"verdict": "CONFIRMED" if sp_ok else "REFUTED", "confidence_prior": 0.95},
    }
    summary = {"gates": {"n_starts": len(rows), "G1": "PASS" if len(rows) >= 200 else "FAIL"},
               "predictions": preds,
               "sample_deep": deep[:5] if deep else [],
               "max_ups": max(r["n_ups"] for r in rows),
               "max_steps_to_sp": max((r["steps_to_species"] or 0) for r in hits)}
    (ART / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    # compact csv-like
    with (ART / "rows.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps({k: r[k] for k in ("src","start","hit","steps_to_species","n_ups","max_d")}, default=str) + "\n")
    print(json.dumps(summary, indent=2, default=str))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
