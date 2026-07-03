"""
Step 4: cheap smoke test -- compare |live(C+22, m+53)| to |live(C,m)| by
size alone, looking for an exact factor or closed-form formula.

This is explicitly NOT a proof of embedding (matching sizes doesn't imply
an explicit correspondence exists) -- it is reported as a separate,
clearly-labeled result from the explicit-map test in embedding_test.py.

CRITICAL LIMITATION: |live(C+22, m+53)| cannot be computed directly (dense
enumeration is impossible at these sizes -- see automaton.py and
oracle.py docstrings). So this script instead:
  1. Reports the EXACT |live(C,m)| values from the small-side dense sweep
     (small_side_sweep.py's output) across all tested (C,m).
  2. Looks for a closed-form pattern in |live(C,m)| itself as a function
     of (C,m) that we CAN observe directly -- legitimate structural
     evidence about the SMALL side alone.
  3. For the big side, reports what CAN be established: the total
     state-space size (C2+1)*3^m2 (trivial arithmetic, no computation
     needed) and, via the SAME oracle used in embedding_test.py, a
     RANDOM-SAMPLE estimate of the live fraction by querying the oracle
     on uniformly random (d,r) points -- this is a Monte Carlo estimate,
     explicitly labeled as such, with sample size and confidence caveats
     stated plainly. It is NOT an exact count.
"""

from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from automaton import M_edge
from oracle import query_membership

OUT_DIR = Path(__file__).parent
SMALL_SIDE_RESULTS = OUT_DIR / "small_side_results.json"
RESULTS_PATH = OUT_DIR / "size_comparison_results.json"

HEARTBEAT = 53
CORRIDOR_SHIFT = 22

MONTE_CARLO_SAMPLES = 60
ORACLE_CALL_CAP = 400_000


def load_small_side():
    if not SMALL_SIDE_RESULTS.exists():
        return []
    data = json.loads(SMALL_SIDE_RESULTS.read_text())
    return data["rows"]


def monte_carlo_big_side_fraction(C2, m2, n_samples, seed):
    """
    Estimate the live fraction of A(C2, m2) after one 53-step heartbeat by
    querying the backward-reachability oracle at n_samples uniformly
    random (d, r) points. Returns a dict with the estimate, decided/
    inconclusive counts, and raw per-sample results.

    This is a MONTE CARLO ESTIMATE, not an exact count. With
    n_samples ~ 60, the standard error on a fraction p is roughly
    sqrt(p(1-p)/60) ~ 0.06 at p=0.5 -- enough to distinguish "roughly
    half the space is live" from "a small fraction is live", but it
    cannot resolve fine structure.
    """
    modulus2 = 3 ** m2
    rng = random.Random(seed)
    shared_memo = {}
    live_count = 0
    decided_count = 0
    inconclusive_count = 0
    raw = []
    for _ in range(n_samples):
        d = rng.randint(0, C2)
        r = rng.randint(0, modulus2 - 1)
        res = query_membership(C2, m2, d, r, steps=HEARTBEAT,
                                call_cap=ORACLE_CALL_CAP, shared_memo=shared_memo)
        if res.inconclusive:
            inconclusive_count += 1
            status = "inconclusive"
        else:
            decided_count += 1
            if res.live:
                live_count += 1
                status = "live"
            else:
                status = "dead"
        raw.append({"d": d, "r": r, "status": status, "calls": res.calls})
    estimate = (live_count / decided_count) if decided_count > 0 else None
    return {
        "n_samples": n_samples,
        "n_decided": decided_count,
        "n_inconclusive": inconclusive_count,
        "n_live_among_decided": live_count,
        "estimated_live_fraction": estimate,
        "raw_samples": raw,
    }


def main():
    print("=" * 70)
    print("SIZE COMPARISON (Step 4 smoke test)")
    print("=" * 70)

    small_rows = load_small_side()
    print(f"Loaded {len(small_rows)} small-side (C,m) rows.")

    print("\n-- Part 1: small-side |live(C,m)| structural check --")
    small_summary = []
    for row in small_rows:
        C, m = row["C"], row["m"]
        total_live = row["total_live_states"]
        total_possible = row["total_possible_states"]
        frac = row["live_fraction"]
        small_summary.append({
            "C": C, "m": m,
            "total_live": total_live,
            "total_possible": total_possible,
            "live_fraction": frac,
        })
        print(f"  C={C} m={m}: live={total_live} possible={total_possible} frac={frac:.6e}")

    print("\n-- Part 2: big-side Monte Carlo live-fraction estimate --")
    best_per_C = {}
    for row in small_summary:
        C = row["C"]
        if C not in best_per_C or row["m"] > best_per_C[C]["m"]:
            best_per_C[C] = row

    mc_results = []
    for C, row in sorted(best_per_C.items()):
        m = row["m"]
        C2 = C + CORRIDOR_SHIFT
        m2 = m + HEARTBEAT
        print(f"  Monte Carlo for C2={C2} m2={m2} ({MONTE_CARLO_SAMPLES} samples)...")
        t0 = time.time()
        mc = monte_carlo_big_side_fraction(C2, m2, MONTE_CARLO_SAMPLES, seed=1000 + C)
        elapsed = time.time() - t0
        mc["C"] = C
        mc["m"] = m
        mc["C2"] = C2
        mc["m2"] = m2
        mc["elapsed_sec"] = elapsed
        mc["small_side_live_fraction_exact"] = row["live_fraction"]
        ratio = None
        if mc["estimated_live_fraction"] is not None and row["live_fraction"] > 0:
            ratio = mc["estimated_live_fraction"] / row["live_fraction"]
        mc["fraction_ratio_big_over_small"] = ratio
        mc_results.append(mc)
        print(f"    decided={mc['n_decided']}/{mc['n_samples']} "
              f"live_frac_est={mc['estimated_live_fraction']} "
              f"(small_side_exact={row['live_fraction']:.6e}) "
              f"ratio={ratio} time={elapsed:.1f}s")

    output = {
        "description": "Size comparison: exact small-side |live(C,m)| structural "
                        "data (Part 1) plus a Monte Carlo ESTIMATE (NOT exact) of "
                        "the big-side live fraction via the backward-reachability "
                        "oracle (Part 2). This test is NOT proof of embedding -- "
                        "matching/related sizes do not imply an explicit "
                        "correspondence. See embedding_test.py for the explicit-map "
                        "test, which is the actual embedding claim under test.",
        "small_side_structural": small_summary,
        "big_side_monte_carlo": mc_results,
    }
    RESULTS_PATH.write_text(json.dumps(output, indent=2))
    print(f"\nWrote results to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
