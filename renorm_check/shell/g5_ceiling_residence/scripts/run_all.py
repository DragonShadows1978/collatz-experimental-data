#!/usr/bin/env python3
"""G5: measure ceiling residence sojourns on free orbits."""
from __future__ import annotations
import json, random, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "g4_drop_gate_streaks" / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "g2_a1_climb_realizability" / "scripts"))
from g2_core import HIGH_RESERVE, load_breach_candidates
from g4_core import walk_with_C_before

ART = Path(__file__).resolve().parents[1] / "artifacts"
ART.mkdir(parents=True, exist_ok=True)
REPO = Path(__file__).resolve().parents[4]

def sojourns(steps):
    """Sojourn = maximal consecutive steps ending with d_after == C_run (at ceiling after)."""
    out = []
    i = 0
    n = len(steps)
    while i < n:
        # at ceiling after step if d_after == C (stored as C_run_after or max so far)
        # use C after step: we have C_before and d_after; C_after = max(C_before, d_after)
        C_after = max(steps[i]["C_before"], steps[i]["d_after"])
        if steps[i]["d_after"] != C_after:
            i += 1
            continue
        j = i
        ups = 0
        while j < n:
            Ca = max(steps[j]["C_before"], steps[j]["d_after"])
            if steps[j]["d_after"] != Ca:
                break
            if steps[j]["upcrossing"]:
                ups += 1
            j += 1
        out.append({"len": j - i, "ups": ups, "k0": steps[i]["k"]})
        i = j
    return out

def main():
    t0 = time.time()
    rng = random.Random(20260712)
    breach = load_breach_candidates(REPO / "data" / "runs", 200)
    starts = list(HIGH_RESERVE) + breach + [rng.randrange(1, 10**7, 2) for _ in range(100)]
    all_s = []
    n_steps = n_ceil = n_ups = n_a1 = 0
    for x0 in starts:
        steps = walk_with_C_before(x0, 8000)
        n_steps += len(steps)
        for s in steps:
            Ca = max(s["C_before"], s["d_after"])
            if s["d_after"] == Ca:
                n_ceil += 1
            if s["upcrossing"]:
                n_ups += 1
                if s["a"] == 1:
                    n_a1 += 1
        all_s.extend(sojourns(steps))
    lens = [s["len"] for s in all_s]
    upss = [s["ups"] for s in all_s]
    mean_len = sum(lens) / len(lens) if lens else 0
    max_len = max(lens) if lens else 0
    mean_ups = sum(upss) / len(upss) if upss else 0
    frac_ceil = n_ceil / n_steps if n_steps else 0
    preds = {
        "T5.1": {"verdict": "CONFIRMED" if mean_len <= 4 else "REFUTED", "mean_sojourn": mean_len, "confidence_prior": 0.55},
        "T5.2": {"verdict": "CONFIRMED" if max_len <= 20 else "REFUTED", "max_sojourn": max_len, "confidence_prior": 0.60},
        "T5.3": {"verdict": "CONFIRMED" if mean_ups <= 1.5 else "REFUTED", "mean_ups_per_sojourn": mean_ups, "confidence_prior": 0.55},
        "T5.4": {"verdict": "CONFIRMED" if frac_ceil <= 0.40 else "REFUTED", "frac_steps_at_ceiling": frac_ceil, "confidence_prior": 0.50},
    }
    gates = {"n_sojourns": len(all_s), "n_ups": n_ups, "a1_rate": n_a1 / n_ups if n_ups else 0,
             "G1": "PASS" if len(all_s) >= 500 else "FAIL",
             "G2": "PASS" if (n_a1 / n_ups if n_ups else 0) >= 0.99 else "FAIL"}
    summary = {"gates": gates, "predictions": preds, "n_starts": len(starts), "elapsed": time.time() - t0}
    (ART / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0 if gates["G1"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
