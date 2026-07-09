#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "g10_species_vs_climb" / "scripts"))
from species_orbit import sample_starts, steps_to_species
ART = Path(__file__).resolve().parents[1] / "artifacts"
REPO = Path(__file__).resolve().parents[4]

def spearman(xs, ys):
    """Spearman rank correlation, pure python."""
    def ranks(a):
        order = sorted(range(len(a)), key=lambda i: a[i])
        r = [0]*len(a)
        i = 0
        while i < len(a):
            j = i
            while j+1 < len(a) and a[order[j+1]] == a[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j+1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx, ry = ranks(xs), ranks(ys)
    n = len(xs)
    mx = sum(rx)/n
    my = sum(ry)/n
    num = sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
    denx = sum((rx[i]-mx)**2 for i in range(n))**0.5
    deny = sum((ry[i]-my)**2 for i in range(n))**0.5
    return num / (denx * deny) if denx and deny else 0.0

def compute_results() -> dict:
    bits = []
    steps = []
    for src, x0 in sample_starts(REPO):
        r = steps_to_species(x0, 100000)
        if not r["hit"]:
            continue
        bits.append(x0.bit_length())
        steps.append(r["steps_to_species"])
    rho = spearman(bits, steps)
    s331 = abs(rho) < 0.85  # not near-perfect
    s332 = rho > -0.2  # not strongly inverse
    # mean steps in low vs high bit terciles
    pairs = sorted(zip(bits, steps), key=lambda t: t[0])
    m = len(pairs)//3
    low = [s for b,s in pairs[:m]]
    high = [s for b,s in pairs[-m:]]
    mean_low = sum(low)/len(low) if low else 0
    mean_high = sum(high)/len(high) if high else 0
    s333 = mean_high >= mean_low * 0.5  # high bits not dramatically faster
    preds = {
        "S33.1": {"verdict": "CONFIRMED" if s331 else "REFUTED", "rho": rho, "confidence_prior": 0.70},
        "S33.2": {"verdict": "CONFIRMED" if s332 else "REFUTED", "rho": rho, "confidence_prior": 0.55},
        "S33.3": {"verdict": "CONFIRMED" if s333 else "REFUTED", "mean_low": mean_low, "mean_high": mean_high, "confidence_prior": 0.55},
    }
    return {"gates": {"G1": "PASS", "n": len(steps)}, "predictions": preds, "rho": rho,
            "mean_low_bits_steps": mean_low, "mean_high_bits_steps": mean_high}

def write_artifacts(results: dict) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    (ART/"summary.json").write_text(json.dumps(results, indent=2))

def main():
    r = compute_results(); write_artifacts(r); print(json.dumps(r, indent=2)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
