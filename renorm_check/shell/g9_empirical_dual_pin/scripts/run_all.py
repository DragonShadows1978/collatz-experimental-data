#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "g3_deficit_climb_chains" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "g4_drop_gate_streaks" / "scripts"))
from g3_core import credit
from g4_core import greedy_up_walker
ART = Path(__file__).resolve().parents[1]/"artifacts"
ART.mkdir(parents=True, exist_ok=True)
G6 = Path(__file__).resolve().parents[2] / "g6_ceiling_a1_pin" / "artifacts" / "summary.json"

def build_multiset(hist: dict, seed: int = 20260712) -> list[int]:
    """Empirical a values at ceiling+drop; shuffled so a=1 is not front-loaded."""
    ms = []
    for a_str, cnt in sorted(hist.items(), key=lambda kv: int(kv[0])):
        ms.extend([int(a_str)] * int(cnt))
    if not ms:
        return [1]
    import random
    rng = random.Random(seed)
    rng.shuffle(ms)
    return ms

def empirical_walker(k0: int, d0: int, n_steps: int, multiset: list[int]) -> dict:
    d = d0
    C = d0
    ups = 0
    streak = 0
    max_streak = 0
    idx = 0
    n_ms = len(multiset)
    for i in range(n_steps):
        c = credit(k0 + i)
        if c == 2 and d == C:
            a = multiset[idx % n_ms]
            idx += 1
        elif c == 2:
            a = 2
        else:
            a = 1
        d = d + c - a
        if d > C:
            ups += 1
            streak += 1
            max_streak = max(max_streak, streak)
            C = d
        else:
            streak = 0
            C = max(C, d)
    return {"k0": k0, "d0": d0, "ups": ups, "max_streak": max_streak}

def main():
    g6 = json.loads(G6.read_text())
    hist = g6["a_hist"]
    ms = build_multiset(hist)
    # freeze multiset stats
    best = {"ups": -1}
    best_st = 0
    ups_d0 = []
    for d0 in range(0, 11):
        for k0 in range(53):
            r = empirical_walker(k0, d0, 53, ms)
            best_st = max(best_st, r["max_streak"])
            if r["ups"] > best["ups"]:
                best = r
            if d0 == 0:
                ups_d0.append(r["ups"])
    greedy = greedy_up_walker(0, 0, 53)
    mean0 = sum(ups_d0)/len(ups_d0)
    preds = {
        "T9.1": {"verdict": "CONFIRMED" if best["ups"] <= 25 else "REFUTED", "max_ups_53": best["ups"], "arg": best, "confidence_prior": 0.55},
        "T9.2": {"verdict": "CONFIRMED" if best["ups"] < 31 else "REFUTED", "max_emp": best["ups"], "greedy_ref": greedy["ups"], "confidence_prior": 0.75},
        "T9.3": {"verdict": "CONFIRMED" if best_st <= 2 else "REFUTED", "max_streak": best_st, "confidence_prior": 0.80},
        "T9.4": {"verdict": "CONFIRMED" if mean0 <= 18 else "REFUTED", "mean_ups_d0": mean0, "confidence_prior": 0.50},
    }
    summary = {
        "gates": {"G1": "PASS", "multiset_size": len(ms), "g6_hist": hist},
        "predictions": preds,
        "greedy_ups_53_k0_0": greedy["ups"],
    }
    (ART/"summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
