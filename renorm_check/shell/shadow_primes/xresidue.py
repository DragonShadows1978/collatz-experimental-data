#!/usr/bin/env python3
"""
Supplementary check: is x (the odd value BEFORE the 3x+1 map) uniform mod p?
This tests the real assumption behind the 1/p (or 1/(p-1)) hit-density prediction.
Reuses the same trajectory generation as harness.py (same seed) for consistency.
"""
import json
import math
import random
from collections import defaultdict

PRIMES = [5, 7, 11, 13, 17, 19, 23]

def gen_odd_starts(n_target, hi=1_000_000, seed=12345):
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
    starts = gen_odd_starts(5200)
    x_residue_counts = {p: defaultdict(int) for p in PRIMES}
    n_steps = 0

    for n0 in starts:
        x = n0
        steps = 0
        while x != 1:
            for p in PRIMES:
                x_residue_counts[p][x % p] += 1
            n_steps += 1
            m = 3 * x + 1
            v2 = 0
            y = m
            while y % 2 == 0:
                y //= 2
                v2 += 1
            x = y
            steps += 1
            if steps > 100000:
                break

    print(f"n_steps sampled: {n_steps}")
    results = {}
    for p in PRIMES:
        counts = x_residue_counts[p]
        total = sum(counts.values())
        exp_uniform = total / p
        chi2 = sum((counts.get(res,0)-exp_uniform)**2/exp_uniform for res in range(p))
        # specifically: what fraction of x is in the "hit-triggering" residue (x = -inv(3,p) mod p)?
        inv3 = pow(3, -1, p)
        trig_res = (-inv3) % p
        frac_trig = counts.get(trig_res, 0) / total
        results[p] = dict(total=total, chi2=chi2, dof=p-1, trig_res=trig_res,
                           frac_trig=frac_trig, pred_1_over_p=1.0/p,
                           counts={int(k):v for k,v in counts.items()})
        print(f"p={p:2d}  x mod p chi2={chi2:8.2f} (dof={p-1})  "
              f"trig_res={trig_res:2d}  frac_x_in_trig_res={frac_trig:.5f}  1/p={1.0/p:.5f}  "
              f"diff={frac_trig-1.0/p:+.5f}")

    with open("xresidue.json","w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
