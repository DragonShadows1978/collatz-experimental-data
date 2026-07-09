#!/usr/bin/env python3
"""
Full prime-anomaly census harness.

Extends shadow_primes/harness.py from 7 hand-picked primes to ALL primes
p in [5, 500] (p=2 forced-hit, p=3 forced-zero, both excluded from the
density census; excludes/marks separately). Two prime bands:
  - FIT band:  5 <= p <= 200   (used for census + predictor fitting)
  - HELD-OUT band: 200 < p <= 500  (touched ONLY by the frozen predictor,
    never used to adjust/fit anything)

Independence fix (per SHADOW_FINDINGS.md caveat): steps within one
trajectory are NOT independent (deterministic chain). The correct
sampling unit is the TRAJECTORY. For every trajectory we record, per
prime, (hits, n_steps) -> a per-trajectory hit-rate. Census CIs are
computed by block bootstrap over trajectories (resample trajectories
with replacement, recompute pooled rate), NOT by pooling all steps into
one iid binomial as if steps were independent.

Exact integer arithmetic (trial division), deterministic seed.
"""
import json
import random
import time

FIT_LO, FIT_HI = 5, 200
HOLD_LO, HOLD_HI = 201, 500

def sieve(n):
    is_p = [True] * (n + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, n + 1, i):
                is_p[j] = False
    return [i for i in range(2, n + 1) if is_p[i]]

ALL_PRIMES = sieve(HOLD_HI)
FIT_PRIMES = [p for p in ALL_PRIMES if FIT_LO <= p <= FIT_HI]
HOLD_PRIMES = [p for p in ALL_PRIMES if HOLD_LO <= p <= HOLD_HI]
TRACK_PRIMES = FIT_PRIMES + HOLD_PRIMES  # p=3 excluded (identically forbidden, proven elsewhere)

def vp_and_strip(m, p):
    v = 0
    while m % p == 0:
        m //= p
        v += 1
    return v

def trajectory_hits(n0, primes, cap=200000):
    """
    Walk odd trajectory from n0 to 1. At each step m=3x+1, for each tracked
    prime record whether p | m (hit) -- do NOT need the full v_p, just the
    binary hit indicator for the census (matches the established 1/p model:
    hit iff x = -3^{-1} mod p, i.e. p | m at all, v_p>=1).
    Returns (n_steps, hits_dict) or None if not converged within cap.
    """
    x = n0
    n_steps = 0
    hits = {p: 0 for p in primes}
    while x != 1:
        m = 3 * x + 1
        v2 = 0
        mm = m
        while mm % 2 == 0:
            mm //= 2
            v2 += 1
        for p in primes:
            if m % p == 0:
                hits[p] += 1
        x = m >> v2
        n_steps += 1
        if n_steps > cap:
            return None
    return n_steps, hits

def gen_odd_starts(n_target, hi=2_000_000, seed=20260705):
    rng = random.Random(seed)
    starts = set()
    deep = [27, 703, 6171, 837799]
    for d in deep:
        starts.add(d)
    while len(starts) < n_target + len(deep):
        cand = rng.randrange(1, hi) | 1
        starts.add(cand)
    starts = list(starts)
    rng.shuffle(starts)
    return starts

def main():
    N_TRAJ = 22000  # >= 20000 independent trajectories as ordered
    starts = gen_odd_starts(N_TRAJ)
    print(f"Census: {len(starts)} odd starts, tracking {len(TRACK_PRIMES)} primes "
          f"({len(FIT_PRIMES)} fit [{FIT_LO}-{FIT_HI}] + {len(HOLD_PRIMES)} held-out [{HOLD_LO}-{HOLD_HI}])")

    t0 = time.time()
    # Per-trajectory records: list of (n0, n_steps, {p: hits})
    # This IS the independent-sample unit for CIs.
    per_traj = []
    n_ok = 0
    n_fail = 0
    total_steps = 0

    for i, n0 in enumerate(starts):
        res = trajectory_hits(n0, TRACK_PRIMES)
        if res is None:
            n_fail += 1
            print(f"FAILED TO CONVERGE: {n0}")
            continue
        n_steps, hits = res
        per_traj.append({"n0": n0, "n_steps": n_steps, "hits": hits})
        n_ok += 1
        total_steps += n_steps
        if (i + 1) % 2000 == 0:
            elapsed = time.time() - t0
            print(f"  {i+1}/{len(starts)} done, {total_steps} steps so far, {elapsed:.1f}s elapsed")

    elapsed = time.time() - t0
    print(f"DONE: {n_ok} ok, {n_fail} failed, {total_steps} total odd-steps, {elapsed:.1f}s")

    # Aggregate pooled (naive) stats too, for comparison against the trajectory-level stats.
    pooled_hits = {p: 0 for p in TRACK_PRIMES}
    for rec in per_traj:
        for p in TRACK_PRIMES:
            pooled_hits[p] += rec["hits"][p]

    out = {
        "n_trajectories": n_ok,
        "n_failed": n_fail,
        "n_steps_total": total_steps,
        "fit_primes": FIT_PRIMES,
        "hold_primes": HOLD_PRIMES,
        "pooled_hits": pooled_hits,
        "per_traj": per_traj,
        "seed": 20260705,
        "hi": 2_000_000,
        "n_target": N_TRAJ,
        "elapsed_sec": elapsed,
    }
    with open("census_results.json", "w") as f:
        json.dump(out, f)
    print("Wrote census_results.json")

if __name__ == "__main__":
    main()
