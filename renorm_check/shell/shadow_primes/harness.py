#!/usr/bin/env python3
"""
Shadow-prime spectrum harness.

For each odd start n0, walk the Collatz odd-map trajectory to 1.
At each step, m = 3x+1. Record v_p(m) for p in PRIMES (2,5,7,11,13,17,19,23).
(v3 is identically 0, verified separately in gate0.py, not tracked here.)

Collect per-trajectory step records:
  - step index (0-based) and fractional descent position (step/len)
  - v2 (credit word) and v_p for each shadow prime
Then aggregate:
  1. hit density P(v_p>=1) and mean v_p, vs 1/(p-1) and 1/p predictions
  2. P(v_p>=1 | v2==1) vs P(v_p>=1 | v2>=2), correlation(v2, v_p) per prime
  3. co-occurrence matrix among shadow primes (observed vs independent-expected)
  4. density vs fractional descent-position bins
  5. residue-class analysis of m mod p to look for structural suppression/enhancement,
     analogous to the v3=0 mechanism.

Exact integer arithmetic throughout (trial division). No commits; write-only
to shadow_primes/ per instructions.
"""
import json
import math
import random
import statistics
from collections import defaultdict

PRIMES = [2, 5, 7, 11, 13, 17, 19, 23]

def trajectory_records(n0, cap=100000):
    """
    Walk odd trajectory from n0 to 1. At each step form m=3x+1.
    Return list of dict(step, m, v={p: v_p(m)}), or None if didn't converge.
    """
    x = n0
    recs = []
    steps = 0
    while x != 1:
        m = 3 * x + 1
        v = {p: vp_one(m, p) for p in PRIMES}
        recs.append((steps, m, v))
        # advance: divide out all 2's (this IS v2, reuse it)
        v2 = v[2]
        x = m >> v2  # m // 2**v2
        steps += 1
        if steps > cap:
            return None
    return recs

def vp_one(m, p):
    v = 0
    while m % p == 0:
        m //= p
        v += 1
    return v

def gen_odd_starts(n_target, hi=1_000_000, seed=12345):
    """Deterministic pseudo-random sample of odd starts in [1, hi], plus deep starts."""
    rng = random.Random(seed)
    starts = set()
    deep = [27, 703, 6171, 837799]
    for d in deep:
        starts.add(d)
    while len(starts) < n_target + len(deep):
        cand = rng.randrange(1, hi) | 1  # force odd
        starts.add(cand)
    starts = list(starts)
    rng.shuffle(starts)
    return starts

def main():
    N_SAMPLE = 5200
    starts = gen_odd_starts(N_SAMPLE)
    print(f"Generated {len(starts)} odd starts (target {N_SAMPLE} + deep set)")

    all_traj = {}
    n_ok = 0
    n_fail = 0
    total_steps = 0
    max_len = 0

    for n0 in starts:
        recs = trajectory_records(n0)
        if recs is None:
            n_fail += 1
            print(f"FAILED TO CONVERGE: {n0}")
            continue
        n_ok += 1
        total_steps += len(recs)
        max_len = max(max_len, len(recs))
        all_traj[n0] = recs

    print(f"Trajectories OK: {n_ok}, failed: {n_fail}, total odd-steps: {total_steps}, max traj len: {max_len}")

    # Save raw aggregate stats to a compact JSON (not full step data - too large potentially)
    # But we need per-step data for correlation analysis. Let's stream-aggregate instead
    # of holding everything, since total_steps could be large. We already hold all_traj in
    # memory; check size.
    import sys
    print(f"Approx memory: all_traj has {len(all_traj)} trajectories")

    # ---- Task 1: hit density and mean v_p per prime ----
    hits = {p: 0 for p in PRIMES}
    sumv = {p: 0 for p in PRIMES}
    n_steps_total = 0

    # ---- Task 2: v2-conditional correlation ----
    # v2==1 (support) vs v2>=2 (drop)
    support_steps = 0
    drop_steps = 0
    hits_given_support = {p: 0 for p in PRIMES}
    hits_given_drop = {p: 0 for p in PRIMES}

    # for correlation coefficient between v2 word and v_p word (aligned by step)
    # accumulate sums for Pearson correlation: sum_v2, sum_vp, sum_v2sq, sum_vpsq, sum_v2vp, n
    corr_acc = {p: {"n":0,"sx":0,"sy":0,"sxx":0,"syy":0,"sxy":0} for p in PRIMES}
    # also correlation using binary hit indicator (v_p>=1) instead of v_p magnitude
    corr_acc_bin = {p: {"n":0,"sx":0,"sy":0,"sxx":0,"syy":0,"sxy":0} for p in PRIMES}

    # ---- Task 3: co-occurrence matrix among shadow primes (binary hit indicator) ----
    cooc = {p: {q: 0 for q in PRIMES} for p in PRIMES}  # cooc[p][q] = count both v_p>=1 and v_q>=1 (p!=q), diag = hits[p]

    # ---- Task 4: descent-position bins ----
    NBINS = 10
    bin_steps = [0] * NBINS
    bin_hits = {p: [0]*NBINS for p in PRIMES}

    # ---- Task 5: residue class of m mod p (raw, unconditioned on v_p) ----
    # For structural suppression check: distribution of m mod p^1 (i.e. is m mod p uniform over
    # nonzero residues, or skewed?) We'll tally m mod p across ALL steps for each p.
    residue_counts = {p: defaultdict(int) for p in PRIMES}

    for n0, recs in all_traj.items():
        L = len(recs)
        for (step, m, v) in recs:
            n_steps_total += 1
            v2 = v[2]
            is_support = (v2 == 1)
            is_drop = (v2 >= 2)
            if is_support:
                support_steps += 1
            else:
                drop_steps += 1

            frac_pos = step / L if L > 0 else 0.0
            b = min(NBINS - 1, int(frac_pos * NBINS))
            bin_steps[b] += 1

            hit_flags = {}
            for p in PRIMES:
                vpp = v[p]
                hit = 1 if vpp >= 1 else 0
                hit_flags[p] = hit
                hits[p] += hit
                sumv[p] += vpp
                if is_support:
                    hits_given_support[p] += hit
                if is_drop:
                    hits_given_drop[p] += hit
                bin_hits[p][b] += hit

                residue_counts[p][m % p] += 1

                # correlation accumulators: x = v2 (or hit2), y = v_p (or hit_p)
                acc = corr_acc[p]
                acc["n"] += 1
                acc["sx"] += v2
                acc["sy"] += vpp
                acc["sxx"] += v2*v2
                acc["syy"] += vpp*vpp
                acc["sxy"] += v2*vpp

                accb = corr_acc_bin[p]
                hit2 = 1 if v2 >= 1 else 0  # always 1, v2>=1 always true; use is_drop as binary instead
                x_bin = 1 if is_drop else 0
                accb["n"] += 1
                accb["sx"] += x_bin
                accb["sy"] += hit
                accb["sxx"] += x_bin*x_bin
                accb["syy"] += hit*hit
                accb["sxy"] += x_bin*hit

            # co-occurrence (pairwise, off-diagonal counts both-hit; diagonal = hits[p])
            for p in PRIMES:
                for q in PRIMES:
                    if hit_flags[p] and hit_flags[q]:
                        cooc[p][q] += 1

    # ---- Save all aggregates to JSON for the report-writing step ----
    def pearson(acc):
        n = acc["n"]
        if n == 0:
            return None
        mx = acc["sx"] / n
        my = acc["sy"] / n
        cov = acc["sxy"]/n - mx*my
        varx = acc["sxx"]/n - mx*mx
        vary = acc["syy"]/n - my*my
        if varx <= 0 or vary <= 0:
            return 0.0
        return cov / math.sqrt(varx*vary)

    results = {
        "n_trajectories": n_ok,
        "n_failed": n_fail,
        "n_steps_total": n_steps_total,
        "support_steps": support_steps,
        "drop_steps": drop_steps,
        "hits": hits,
        "sumv": sumv,
        "hits_given_support": hits_given_support,
        "hits_given_drop": hits_given_drop,
        "corr_magnitude": {p: pearson(corr_acc[p]) for p in PRIMES},
        "corr_binary": {p: pearson(corr_acc_bin[p]) for p in PRIMES},
        "cooc": cooc,
        "bin_steps": bin_steps,
        "bin_hits": bin_hits,
        "residue_counts": {p: dict(residue_counts[p]) for p in PRIMES},
        "max_traj_len": max_len,
        "starts_sample": starts[:20],  # just a peek
    }

    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Wrote results.json")

if __name__ == "__main__":
    main()
