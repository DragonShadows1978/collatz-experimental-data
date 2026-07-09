#!/usr/bin/env python3
"""
ORBIT stationary-distribution harness.

Extends SHADOW's xresidue.py: sample many long odd-map trajectories,
histogram x (the pre-image value, mod p) at EVERY odd step, for a wider
prime list including candidates for the predictive check.

Exact integer arithmetic (trial division for v2; no floats until the
final normalization/report stage).

Also records hit-density (v_p(3x+1)>=1) per prime, on the SAME sample,
so the hole-vs-deviation comparison in orbit_analyze.py is apples-to-apples
(SHADOW_FINDINGS used a 5,204-start / 239,686-step sample; we go larger
here to tighten CIs and extend to new primes).
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

    x_residue_counts = {p: defaultdict(int) for p in PRIMES}
    hit_counts = {p: 0 for p in PRIMES}
    n_steps = 0
    n_ok = 0
    n_fail = 0
    max_len = 0

    for n0 in starts:
        x = n0
        steps = 0
        ok = True
        while x != 1:
            for p in PRIMES:
                x_residue_counts[p][x % p] += 1
                m3 = 3 * x + 1
                if m3 % p == 0:
                    hit_counts[p] += 1
            n_steps += 1
            m = 3 * x + 1
            v2 = 0
            y = m
            while y % 2 == 0:
                y //= 2
                v2 += 1
            x = y
            steps += 1
            if steps > 200000:
                ok = False
                break
        if ok:
            n_ok += 1
            max_len = max(max_len, steps)
        else:
            n_fail += 1
            print(f"FAILED TO CONVERGE: {n0}")

    print(f"n_steps sampled: {n_steps}, trajectories ok: {n_ok}, failed: {n_fail}, max_len: {max_len}")

    results = {"n_steps": n_steps, "n_ok": n_ok, "n_fail": n_fail, "max_len": max_len, "primes": {}}
    for p in PRIMES:
        counts = x_residue_counts[p]
        total = sum(counts.values())
        inv3 = pow(3, -1, p)
        trig_res = (-inv3) % p  # h_p = -3^{-1} mod p
        frac_trig = counts.get(trig_res, 0) / total
        exp_uniform = total / p
        chi2 = sum((counts.get(res, 0) - exp_uniform) ** 2 / exp_uniform for res in range(p))
        hits = hit_counts[p]
        results["primes"][p] = dict(
            total=total,
            trig_res=trig_res,
            frac_trig_stationary=frac_trig,     # s_p(h_p) measured on x (pre-image)
            pred_1_over_p=1.0 / p,
            hole=1.0 / p - frac_trig,            # suppression of stationary mass at h_p
            chi2=chi2,
            dof=p - 1,
            hit_density=hits / total,            # P(v_p(3x+1)>=1), same sample
            hit_deviation=1.0 / p - hits / total,  # positive = suppressed vs 1/p
            counts={int(k): v for k, v in counts.items()},
        )
        print(f"p={p:2d} s_p(h_p)={frac_trig:.5f} 1/p={1/p:.5f} hole={1/p-frac_trig:+.5f} "
              f"hit_dens={hits/total:.5f} hit_dev={1/p-hits/total:+.5f} chi2={chi2:.1f}")

    with open("orbit_stationary.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Wrote orbit_stationary.json")

if __name__ == "__main__":
    main()
