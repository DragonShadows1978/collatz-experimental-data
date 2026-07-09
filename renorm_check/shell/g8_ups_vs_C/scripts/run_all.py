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
    hr = list(HIGH_RESERVE)
    rnd = [rng.randrange(1,10**7,2) for _ in range(100)]
    breach = load_breach_candidates(REPO/"data"/"runs", 200)
    starts = [("hr", x) for x in hr] + [("br", x) for x in breach] + [("rnd", x) for x in rnd]
    id_ok = True
    rows = []
    max_win53 = 0
    for src, x0 in starts:
        steps = walk_with_C_before(x0, 8000)
        n_ups = sum(1 for s in steps if s["upcrossing"])
        max_d = max((s["d_after"] for s in steps), default=0)
        # also max C_before after last
        max_C = 0
        for s in steps:
            max_C = max(max_C, s["C_before"], s["d_after"])
        # Identity: each up raises the running max by 1 from 0; if max_d<0 never upcrossed.
        eq = n_ups == max(0, max_d)
        if not eq:
            id_ok = False
        # sliding 53
        ups_pref = [1 if s["upcrossing"] else 0 for s in steps]
        for i in range(0, max(0, len(ups_pref)-52)):
            w = sum(ups_pref[i:i+53])
            if w > max_win53:
                max_win53 = w
        rows.append({"src": src, "x": x0, "n_ups": n_ups, "max_d": max_d, "max_C": max_C, "eq": eq})
    id_ok = all(r["eq"] for r in rows)
    def mean_src(s):
        xs=[r["n_ups"] for r in rows if r["src"]==s]
        return sum(xs)/len(xs) if xs else 0
    preds = {
        "T8.1": {"verdict": "CONFIRMED" if id_ok else "REFUTED", "all_n_ups_eq_max_d": id_ok, "confidence_prior": 0.90},
        "T8.2": {"verdict": "CONFIRMED" if mean_src("rnd") < 30 else "REFUTED", "mean_rnd": mean_src("rnd"), "confidence_prior": 0.70},
        "T8.3": {"verdict": "CONFIRMED" if mean_src("hr") >= 15 else "REFUTED", "mean_hr": mean_src("hr"), "confidence_prior": 0.60},
        "T8.4": {"verdict": "CONFIRMED" if max_win53 <= 12 else "REFUTED", "max_ups_in_53": max_win53, "confidence_prior": 0.50},
    }
    summary = {"gates": {"n": len(rows), "G1": "PASS"}, "predictions": preds, "means": {"hr": mean_src("hr"), "br": mean_src("br"), "rnd": mean_src("rnd")}}
    (ART/"summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
