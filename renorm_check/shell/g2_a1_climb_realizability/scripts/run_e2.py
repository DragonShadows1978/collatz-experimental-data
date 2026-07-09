#!/usr/bin/env python3
"""G2 E2 — pure a=1 cylinders L=1..24+. Predictions Q2.1–Q2.4."""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from g2_core import pure_a1_cylinder, pure_a1_table, realizes_word  # noqa: E402

ART = Path(__file__).resolve().parents[1] / "artifacts"
ART.mkdir(parents=True, exist_ok=True)
L_MAX = 32  # ≥24


def main() -> int:
    t0 = time.time()
    rows = pure_a1_table(L_MAX)
    print(f"E2 pure a=1 cylinders L=1..{L_MAX}", flush=True)

    # Gates
    r1 = rows[0]
    g1 = r1["residue"] == 3 and r1["modulus"] == 4 and r1["nonempty"]
    g2 = all(r["nonempty"] and r["min_positive_odd"] is not None for r in rows)
    # also verify each min realizes word
    for r in rows:
        L = r["L"]
        x = r["min_positive_odd"]
        assert x is not None and realizes_word(x, tuple(1 for _ in range(L))), L
    bits = [r["mod_bits"] for r in rows]
    g3 = all(bits[i] <= bits[i + 1] for i in range(len(bits) - 1))

    # Q2.1: all L≤24 nonempty
    q21_ok = all(r["nonempty"] for r in rows if r["L"] <= 24)
    q21 = {
        "verdict": "CONFIRMED" if q21_ok else "REFUTED",
        "all_nonempty_L_le_24": q21_ok,
        "confidence_prior": 0.65,
    }

    # Q2.2: m(L) ≥ L  (mod_bits = L+1 for closed form, so ≥ L)
    q22_ok = all(r["mod_bits"] >= r["L"] for r in rows)
    q22 = {
        "verdict": "CONFIRMED" if q22_ok else "REFUTED",
        "mod_bits_by_L": {r["L"]: r["mod_bits"] for r in rows},
        "confidence_prior": 0.75,
    }

    # Q2.3: log2(min_x) ≥ 0.5*L - O(1) on L=1..16
    # closed form min_x = 2^{L+1}-1 ⇒ log2 ≈ L+1 ≥ 0.5 L
    pts = [(r["L"], r["log2_min_x"]) for r in rows if r["L"] <= 16]
    # fit c: require log2_min_x >= 0.5*L - 1 for all
    q23_ok = all(lx is not None and lx >= 0.5 * L - 1 for L, lx in pts)
    # linear regression slope rough
    if len(pts) >= 2:
        Ls = [p[0] for p in pts]
        Ys = [p[1] for p in pts]
        n = len(Ls)
        meanL = sum(Ls) / n
        meanY = sum(Ys) / n
        num = sum((L - meanL) * (y - meanY) for L, y in zip(Ls, Ys))
        den = sum((L - meanL) ** 2 for L in Ls) or 1.0
        slope = num / den
    else:
        slope = None
    q23 = {
        "verdict": "CONFIRMED" if q23_ok and (slope is None or slope >= 0.5) else "REFUTED",
        "slope_log2_min_vs_L": slope,
        "points_L1_16": pts,
        "confidence_prior": 0.50,
    }

    # Q2.4: residue ≡ -1 mod 2^{L+1} for all L (inverse limit → -1)
    q24_ok = all(r["residue"] == r["modulus"] - 1 for r in rows)
    # distance of min_x to -1 in 2-adics: min_x + 1 = 2^{L+1}
    q24 = {
        "verdict": "CONFIRMED" if q24_ok else "REFUTED",
        "all_residue_is_minus_one": q24_ok,
        "note": "min_positive_odd = 2^{L+1}-1 ≡ -1 mod 2^{L+1}; inverse limit is -1 in Z2",
        "confidence_prior": 0.55,
    }

    gates = {
        "E2-G1": "PASS" if g1 else "FAIL",
        "E2-G2": "PASS" if g2 else "FAIL",
        "E2-G3": "PASS" if g3 else "FAIL",
        "L_max": L_MAX,
    }

    csv_path = ART / "e2_cylinders.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    summary = {
        "gates": gates,
        "predictions": {"Q2.1": q21, "Q2.2": q22, "Q2.3": q23, "Q2.4": q24},
        "rows": rows,
        "elapsed_sec": time.time() - t0,
        "artifacts": {"csv": str(csv_path)},
    }
    (ART / "e2_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({"gates": gates, "predictions": summary["predictions"]}, indent=2))
    print(f"WROTE {csv_path}")
    return 0 if all(v == "PASS" for v in gates.values() if v in ("PASS", "FAIL")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
