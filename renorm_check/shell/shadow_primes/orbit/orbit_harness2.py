#!/usr/bin/env python3
"""
ORBIT harness v2: same trajectory sample as orbit_harness.py (same seed,
same 20,004 starts) but ALSO records PER-TRAJECTORY hit counts and step
counts, so we can build a conservative CI using n_trajectories as the
effective independent sample size (steps within one trajectory are NOT
independent draws -- SHADOW_FINDINGS.md flagged this exact issue and
found raw-step CIs misleadingly tight, chi2/dof 120-1380 when pooling
autocorrelated steps vs ~0.5-1.3 using independent trajectory starts).

This is the sample used for BOTH the hole table (with honest CIs) and
the task-5 predictive-check measurement on new primes.
"""
import json
import random
from collections import defaultdict

PRIMES = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67]

def gen_odd_starts(n_target, hi=1_000_000, seed=20260705):
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
    N_SAMPLE = 20000
    starts = gen_odd_starts(N_SAMPLE)
    print(f"Generated {len(starts)} odd starts")

    # per-trajectory hit-rate for each prime (for conservative independent-unit CI)
    traj_hit_rate = {p: [] for p in PRIMES}  # list of per-trajectory hits/len
    x_residue_counts = {p: defaultdict(int) for p in PRIMES}
    hit_counts = {p: 0 for p in PRIMES}
    n_steps = 0
    n_ok = 0
    n_fail = 0

    for n0 in starts:
        x = n0
        steps = 0
        traj_hits = {p: 0 for p in PRIMES}
        ok = True
        while x != 1:
            for p in PRIMES:
                x_residue_counts[p][x % p] += 1
                if (3 * x + 1) % p == 0:
                    hit_counts[p] += 1
                    traj_hits[p] += 1
            n_steps += 1
            m = 3 * x + 1
            y = m
            while y % 2 == 0:
                y //= 2
            x = y
            steps += 1
            if steps > 200000:
                ok = False
                break
        if ok:
            n_ok += 1
            for p in PRIMES:
                traj_hit_rate[p].append(traj_hits[p] / steps)
        else:
            n_fail += 1
            print(f"FAILED TO CONVERGE: {n0}")

    print(f"n_steps={n_steps} n_ok={n_ok} n_fail={n_fail}")

    results = {"n_steps": n_steps, "n_ok": n_ok, "n_fail": n_fail, "primes": {}}
    for p in PRIMES:
        counts = x_residue_counts[p]
        total = sum(counts.values())
        inv3 = pow(3, -1, p)
        trig_res = (-inv3) % p
        frac_trig = counts.get(trig_res, 0) / total
        rates = traj_hit_rate[p]
        n_traj = len(rates)
        mean_rate = sum(rates) / n_traj
        var_rate = sum((r - mean_rate) ** 2 for r in rates) / (n_traj - 1)
        se_rate = (var_rate / n_traj) ** 0.5
        results["primes"][p] = dict(
            total=total, trig_res=trig_res, frac_trig_stationary=frac_trig,
            pred_1_over_p=1.0 / p, hole=1.0 / p - frac_trig,
            hit_density=hit_counts[p] / total,
            n_traj=n_traj, traj_mean_hit_rate=mean_rate, traj_se_hit_rate=se_rate,
            traj_ci95_lo=mean_rate - 1.96 * se_rate, traj_ci95_hi=mean_rate + 1.96 * se_rate,
        )
        excl = not (mean_rate - 1.96 * se_rate <= 1.0 / p <= mean_rate + 1.96 * se_rate)
        print(f"p={p:3d} frac_trig={frac_trig:.5f} 1/p={1/p:.5f} traj_mean={mean_rate:.5f} "
              f"traj_CI95=[{mean_rate-1.96*se_rate:.5f},{mean_rate+1.96*se_rate:.5f}] "
              f"excludes_1/p(traj-level)={excl}")

    with open("orbit_stationary2.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Wrote orbit_stationary2.json")

if __name__ == "__main__":
    main()
