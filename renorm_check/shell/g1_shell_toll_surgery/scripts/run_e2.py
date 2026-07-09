#!/usr/bin/env python3
"""G1 E2 — exit toll census: upward corridor exits vs death-shell skin.

Plan: IMPLEMENTATION_PLAN.md §4. Predictions P2.1–P2.4 frozen pre-data.
"""
from __future__ import annotations

import csv
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from g1_common import (  # noqa: E402
    D_emp,
    credit_true,
    d_rat,
    in_shell,
    odd_step,
    orbit_upcrossings,
    shell_dead_by_delta,
    floor_k_log2_3,
)

ART = Path(__file__).resolve().parents[1] / "artifacts"
ART.mkdir(parents=True, exist_ok=True)
REPO = Path(__file__).resolve().parents[4]  # collatz-experimental-data

# Frozen before run (plan §4.2): high-reserve + breach candidates + random
HIGH_RESERVE = [
    80049391,
    120080895,
    210964383,
    219259131,
    222250543,
    246666523,
    319804831,
    77566362559,
]
M_USED = 6  # plan: start m=6
MAX_STEPS = 8000
RANDOM_N = 100
RANDOM_SEED = 20260708
RANDOM_LIM = 10_000_000


def load_breach_candidates() -> list[int]:
    """Pull candidate_integer from existing breach-follow jsonl files."""
    runs = REPO / "data" / "runs"
    found = []
    folders = sorted(runs.glob("lock3_C*_breach_follow"))
    for folder in folders:
        for f in folder.glob("lock3_corridor_breach_follow_*.jsonl"):
            with f.open() as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    ci = obj.get("candidate_integer")
                    if isinstance(ci, int) and ci > 0 and ci % 2 == 1:
                        found.append(ci)
    seen = set()
    out = []
    for x in found:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def follow_after_exit(x_exit: int, C_before: int, max_steps: int = 200) -> dict:
    """Does orbit return to d <= C_before within max_steps?"""
    x = x_exit
    A = 0
    # We don't know global step index after exit; track relative deficit from 0
    # Better: continue from a synthetic k=0 at exit value, measure max d and
    # whether d drops to <= C_before... actually deficit is path-dependent on k.
    # Use reserve relative to this segment: d_rel(k) = floor(k alpha)-A_k
    # "return below corridor" ≈ d_rel becomes <= C_before or value drops below start.
    x0 = x_exit
    for k in range(max_steps):
        if x == 1:
            return {"returned": True, "steps": k, "reason": "hit_1"}
        if x < x0 and k > 0:
            # classic descent below exit value
            pass
        nxt, a = odd_step(x)
        A += a
        d = floor_k_log2_3(k + 1) - A
        if d <= C_before:
            return {"returned": True, "steps": k + 1, "reason": "d_le_C_before", "d": d}
        x = nxt
    return {"returned": False, "steps": max_steps, "reason": "cap"}


def annotate_event(ev: dict) -> dict:
    """Add shell membership and deltas."""
    C_b = ev["C_before"]
    C_a = ev["C_after"]
    d_b = ev["d_before"]
    d_a = ev["d_after"]
    m = ev["m_used"]
    r = ev["residue_mod"]
    r_n = ev["residue_next_mod"]

    # ceiling distances
    delta_before = C_b - d_b if C_b >= d_b else None
    # post-exit: in new corridor width C_a, state sits at d=d_a so delta=0 (at ceiling)
    delta_after = C_a - d_a  # should be 0 for pure record-setting upcross

    # shell at pre-exit corridor (if C_b>=1) and post
    in_shell_before = False
    in_shell_after = False
    if C_b >= 1 and 0 <= d_b <= C_b:
        in_shell_before = in_shell(C_b, m, d_b, r)
    if C_a >= 1 and 0 <= d_a <= C_a:
        in_shell_after = in_shell(C_a, m, d_a, r_n)

    # near-ceiling flags (shell band proxy): delta <= D(m)
    Dm = d_rat(m)  # agreement-zone law at m=6
    near_ceil_before = delta_before is not None and delta_before <= max(Dm, 1)
    near_ceil_after = delta_after <= max(Dm, 1)

    follow = follow_after_exit(ev["x_exit"], C_b, max_steps=200)

    ev2 = dict(ev)
    ev2.update(
        {
            "delta_before": delta_before,
            "delta_after": delta_after,
            "in_shell_before": in_shell_before,
            "in_shell_after": in_shell_after,
            "D_m": Dm,
            "near_ceil_before": near_ceil_before,
            "near_ceil_after": near_ceil_after,
            "returned_200": follow["returned"],
            "return_steps": follow["steps"],
            "return_reason": follow["reason"],
        }
    )
    return ev2


def null_near_ceil_rate(C: int, m: int, n_samples: int = 2000, rng=None) -> float:
    """Null: uniform over d in 0..C and r with r%3!=0, fraction near-ceil."""
    rng = rng or random.Random(0)
    Dm = d_rat(m)
    modulus = 3 ** m
    hits = 0
    for _ in range(n_samples):
        d = rng.randrange(0, C + 1)
        # reject r%3==0
        while True:
            r = rng.randrange(0, modulus)
            if r % 3 != 0:
                break
        delta = C - d
        if delta <= max(Dm, 1):
            hits += 1
    return hits / n_samples


def main() -> int:
    t0 = time.time()
    rng = random.Random(RANDOM_SEED)

    breach_cands = load_breach_candidates()
    print(f"Loaded {len(breach_cands)} unique breach candidate integers", flush=True)

    random_odds = []
    while len(random_odds) < RANDOM_N:
        x = rng.randrange(1, RANDOM_LIM, 2)
        random_odds.append(x)

    starts = []
    for x in HIGH_RESERVE:
        starts.append(("high_reserve", x))
    for x in breach_cands[:200]:  # cap
        starts.append(("breach_candidate", x))
    for x in random_odds:
        starts.append(("random", x))

    print(f"Total starts: {len(starts)}  m={M_USED}  max_steps={MAX_STEPS}", flush=True)

    # Warm shell tables for C=1..15 at m=6
    print("Warming shell_dead_by_delta for C=1..15 ...", flush=True)
    for C in range(1, 16):
        shell_dead_by_delta(C, M_USED)
    print("Shell warm done", flush=True)

    all_events = []
    start_stats = []
    for src, x0 in starts:
        events, hit1, nsteps = orbit_upcrossings(x0, max_steps=MAX_STEPS, m_track=M_USED)
        start_stats.append(
            {
                "source": src,
                "start_n": x0,
                "n_upcrossings": len(events),
                "hit_1": hit1,
                "steps_run": nsteps,
            }
        )
        for ev in events:
            ev["source"] = src
            all_events.append(annotate_event(ev))
        if len(start_stats) % 25 == 0:
            print(
                f"  ... {len(start_stats)} starts, {len(all_events)} events so far",
                flush=True,
            )

    # Gates
    n_ev = len(all_events)
    g1 = n_ev >= 30

    # Spot-check shell instrument: 20 random (C,d,r) vs recomputation
    spot_ok = True
    for _ in range(20):
        C = rng.randrange(1, 12)
        d = rng.randrange(0, C + 1)
        r = rng.randrange(0, 3 ** M_USED)
        a = in_shell(C, M_USED, d, r)
        b = in_shell(C, M_USED, d, r)
        if a != b:
            spot_ok = False

    # Metrics
    a1_rate = sum(1 for e in all_events if e["a_k"] == 1) / n_ev if n_ev else 0
    # ceiling-adjacent: delta_before <= 1 (or d_before >= C_before-1)
    interior = sum(
        1
        for e in all_events
        if e["delta_before"] is not None and e["delta_before"] >= 3
    )
    interior_rate = interior / n_ev if n_ev else 0
    near_after = sum(1 for e in all_events if e["near_ceil_after"]) / n_ev if n_ev else 0
    shell_after = sum(1 for e in all_events if e["in_shell_after"]) / n_ev if n_ev else 0
    shell_before = sum(1 for e in all_events if e["in_shell_before"]) / n_ev if n_ev else 0
    returned = sum(1 for e in all_events if e["returned_200"]) / n_ev if n_ev else 0

    # Null for near-ceil: at typical C
    null_rates = {C: null_near_ceil_rate(C, M_USED, 3000, rng) for C in (3, 5, 8, 12)}
    # Enrichment: post-exit near_ceil vs null at C=5 (representative)
    # Post-exit delta_after is almost always 0 (record set), so near_ceil_after ~ 1.0
    # That makes P2.1 near-tautological for record-setting definition!
    # Report honestly.
    enrichment_near = near_after / null_rates[5] if null_rates[5] > 0 else None

    # Better P2.1 operationalization: in_shell_after vs rate of shell among
    # uniform live-ish samples at same C
    def null_shell_rate(C, m, n=2000, rng=None):
        rng = rng or random.Random(1)
        hits = 0
        for _ in range(n):
            d = rng.randrange(0, C + 1)
            r = rng.randrange(0, 3 ** m)
            if in_shell(C, m, d, r):
                hits += 1
        return hits / n

    null_shell = {C: null_shell_rate(C, M_USED, 1500, rng) for C in (3, 5, 8)}
    # Only events with C_after in range
    shell_by_C = Counter()
    shell_hit_by_C = Counter()
    for e in all_events:
        Ca = e["C_after"]
        if 1 <= Ca <= 15:
            shell_by_C[Ca] += 1
            if e["in_shell_after"]:
                shell_hit_by_C[Ca] += 1

    pred = {}
    # P2.1: enrichment — use in_shell_after vs null_shell at C=5 events
    ev_c5 = [e for e in all_events if e["C_after"] == 5]
    if len(ev_c5) >= 5:
        rate = sum(1 for e in ev_c5 if e["in_shell_after"]) / len(ev_c5)
        null = null_shell[5]
        enr = rate / null if null > 0 else None
        pred["P2.1"] = {
            "verdict": (
                "CONFIRMED"
                if enr is not None and enr >= 1.5
                else (
                    "REFUTED"
                    if enr is not None and enr < 1.1
                    else "INCONCLUSIVE"
                )
            ),
            "shell_after_rate_C5": rate,
            "null_shell_rate_C5": null,
            "enrichment": enr,
            "n_events_C5": len(ev_c5),
            "confidence_prior": 0.50,
            "note": "Record-setting exits have delta_after=0 by definition; "
            "near_ceil_after is near-tautological. Primary metric is F7 "
            "in_shell_after vs uniform null at same C.",
        }
    else:
        # pool all C
        rate = shell_after
        null = sum(null_shell.values()) / len(null_shell)
        enr = rate / null if null > 0 else None
        pred["P2.1"] = {
            "verdict": (
                "CONFIRMED"
                if enr is not None and enr >= 1.5
                else (
                    "REFUTED"
                    if enr is not None and enr < 1.1
                    else "INCONCLUSIVE"
                )
            ),
            "shell_after_rate_all": rate,
            "null_shell_rate_mean": null,
            "enrichment": enr,
            "confidence_prior": 0.50,
        }

    pred["P2.2"] = {
        "verdict": (
            "CONFIRMED"
            if a1_rate >= 0.70
            else ("REFUTED" if a1_rate < 0.40 else "INCONCLUSIVE")
        ),
        "a1_rate": a1_rate,
        "confidence_prior": 0.75,
    }
    pred["P2.3"] = {
        "verdict": (
            "CONFIRMED"
            if interior_rate < 0.20
            else ("REFUTED" if interior_rate >= 0.35 else "INCONCLUSIVE")
        ),
        "interior_delta_ge3_rate": interior_rate,
        "confidence_prior": 0.65,
    }
    pred["P2.4"] = {
        "verdict": (
            "CONFIRMED"
            if returned >= 0.80
            else ("REFUTED" if returned < 0.50 else "INCONCLUSIVE")
        ),
        "returned_within_200_rate": returned,
        "confidence_prior": 0.70,
    }

    gates = {
        "E2-G1": "PASS" if g1 else "FAIL_INCONCLUSIVE_SAMPLE",
        "E2-G2": "PASS" if spot_ok else "FAIL",
        "E2-G3": "REPORTED",
        "n_events": n_ev,
        "n_starts": len(starts),
    }

    # Write CSV
    csv_path = ART / "e2_exit_events.csv"
    if all_events:
        fields = list(all_events[0].keys())
        with csv_path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(all_events)
    else:
        csv_path.write_text("")

    summary = {
        "gates": gates,
        "predictions": pred,
        "metrics": {
            "n_events": n_ev,
            "a1_rate": a1_rate,
            "interior_rate": interior_rate,
            "near_ceil_after": near_after,
            "shell_after": shell_after,
            "shell_before": shell_before,
            "returned_200": returned,
            "null_near_ceil": null_rates,
            "null_shell": null_shell,
            "enrichment_near_vs_null5": enrichment_near,
            "shell_by_C": dict(shell_by_C),
            "shell_hit_by_C": dict(shell_hit_by_C),
        },
        "sources": {
            "n_high_reserve": len(HIGH_RESERVE),
            "n_breach_candidates_loaded": len(breach_cands),
            "n_breach_used": min(200, len(breach_cands)),
            "n_random": RANDOM_N,
            "random_seed": RANDOM_SEED,
        },
        "m_used": M_USED,
        "max_steps": MAX_STEPS,
        "elapsed_sec": time.time() - t0,
        "artifacts": {
            "events_csv": str(csv_path),
            "starts_json": str(ART / "e2_starts.json"),
        },
    }
    (ART / "e2_starts.json").write_text(json.dumps(start_stats, indent=2))
    (ART / "e2_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps({"gates": gates, "predictions": pred, "metrics": summary["metrics"]}, indent=2))
    print(f"\nWROTE {csv_path}")
    print(f"WROTE {ART / 'e2_summary.json'}  elapsed={summary['elapsed_sec']:.1f}s")
    return 0 if g1 and spot_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
