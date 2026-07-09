#!/usr/bin/env python3
from __future__ import annotations
import json, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "g4_drop_gate_streaks" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "g2_a1_climb_realizability" / "scripts"))
from g2_core import HIGH_RESERVE, load_breach_candidates
from g4_core import walk_with_C_before
ART = Path(__file__).resolve().parents[1]/"artifacts"
ART.mkdir(parents=True, exist_ok=True)
REPO = Path(__file__).resolve().parents[4]

def main():
    rng = random.Random(20260712)
    starts = list(HIGH_RESERVE)+load_breach_candidates(REPO/"data"/"runs",200)+[rng.randrange(1,10**7,2) for _ in range(100)]
    ceil_drop_a = []
    sojourn_ends = []  # (c,a) of first step that leaves ceiling after being on it
    for x0 in starts:
        steps = walk_with_C_before(x0, 8000)
        on = False
        for s in steps:
            Ca_before = s["C_before"]
            at_before = s["d_before"] == Ca_before
            Ca_after = max(s["C_before"], s["d_after"])
            at_after = s["d_after"] == Ca_after
            if at_before and s["c"]==2:
                ceil_drop_a.append(s["a"])
            if on and not at_after:
                sojourn_ends.append({"c": s["c"], "a": s["a"], "up": s["upcrossing"]})
            on = at_after
    n = len(ceil_drop_a)
    f2 = sum(1 for a in ceil_drop_a if a==2)/n if n else 0
    f3 = sum(1 for a in ceil_drop_a if a>=3)/n if n else 0
    ends = sojourn_ends
    ne = len(ends)
    end_sup_or_leave = sum(1 for e in ends if e["c"]==1 or e["a"]>=3)/ne if ne else 0
    end_up = sum(1 for e in ends if e["c"]==2 and e["a"]==1)
    preds = {
        "T7.1": {"verdict": "CONFIRMED" if 0.20 <= f2 <= 0.40 else "REFUTED", "frac_a2": f2, "n": n, "confidence_prior": 0.50},
        "T7.2": {"verdict": "CONFIRMED" if f3 >= 0.05 else "REFUTED", "frac_a_ge3": f3, "confidence_prior": 0.55},
        "T7.3": {"verdict": "CONFIRMED" if end_sup_or_leave >= 0.70 else "REFUTED", "frac": end_sup_or_leave, "n_ends": ne, "confidence_prior": 0.50},
        "T7.4": {"verdict": "CONFIRMED" if end_up == 0 else "REFUTED", "n_end_with_up_form": end_up, "confidence_prior": 0.90},
    }
    summary = {"gates": {"n_ceil_drop": n, "n_ends": ne, "G1": "PASS" if n>=200 else "FAIL"}, "predictions": preds}
    (ART/"summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
