#!/usr/bin/env python3
from __future__ import annotations
import json, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "g4_drop_gate_streaks" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "g2_a1_climb_realizability" / "scripts"))
from g2_core import HIGH_RESERVE, load_breach_candidates
from g4_core import walk_with_C_before
ART = Path(__file__).resolve().parents[1] / "artifacts"
ART.mkdir(parents=True, exist_ok=True)
REPO = Path(__file__).resolve().parents[4]

def main():
    rng = random.Random(20260712)
    starts = list(HIGH_RESERVE) + load_breach_candidates(REPO/"data"/"runs", 200) + [rng.randrange(1,10**7,2) for _ in range(100)]
    ceil_drop = []  # (a, up)
    ups_ok = 0
    ups_total = 0
    for x0 in starts:
        for s in walk_with_C_before(x0, 8000):
            at_ceil_before = s["d_before"] == s["C_before"]
            if at_ceil_before and s["c"] == 2:
                ceil_drop.append(s["a"])
            if s["upcrossing"]:
                ups_total += 1
                if s["thm_U"]:
                    ups_ok += 1
    n = len(ceil_drop)
    n_a1 = sum(1 for a in ceil_drop if a == 1)
    p = n_a1 / n if n else 0
    miss = 1 - p
    preds = {
        "T6.1": {"verdict": "CONFIRMED" if p >= 0.40 else "REFUTED", "p_a1": p, "n": n, "confidence_prior": 0.55},
        "T6.2": {"verdict": "CONFIRMED" if p <= 0.90 else "REFUTED", "p_a1": p, "confidence_prior": 0.55},
        "T6.3": {"verdict": "CONFIRMED" if ups_total and ups_ok == ups_total else "REFUTED", "ups": ups_total, "thm_U_ok": ups_ok, "confidence_prior": 0.95},
        "T6.4": {"verdict": "CONFIRMED" if miss >= 0.10 else "REFUTED", "miss_rate": miss, "confidence_prior": 0.55},
    }
    gates = {"n_ceil_drop": n, "G1": "PASS" if n >= 200 else "FAIL"}
    summary = {"gates": gates, "predictions": preds, "a_hist": {str(k): ceil_drop.count(k) for k in sorted(set(ceil_drop))}}
    (ART/"summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0 if gates["G1"]=="PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
