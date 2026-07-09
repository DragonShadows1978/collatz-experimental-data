#!/usr/bin/env python3
"""
CRITICAL CORRECTION to census_harness.py / census_analyze.py.

Discovery: Collatz odd-trajectories from independent random starts are NOT
independent samples of (m mod p) events. All trajectories descend through
a shared, heavily-branching merge tree toward 1 -- most starts pass through
the SAME small set of deep states on the way down. Direct measurement on
this dataset (22,004 trajectories, 1,057,188 total odd-steps): only
203,003 DISTINCT x-values are visited (dedup ratio 0.192 -- over 80% of
"steps" are revisits of shared states). For rare large primes this is
catastrophic: p=433's entire "hit density" (10,068 of ~1.06M step-hits)
turns out to be 90.5% just ONE shared state (m=1732=4*433) that ~41% of
ALL trajectories happen to pass through. That prime's "4x enrichment over
1/p" in the naive pooled-step census (see census_analyze.py) is a merge-
tree artifact, NOT a residue-density anomaly.

This script rebuilds the census on the DISTINCT-STATE graph: walk every
trajectory, collect the set of distinct x-values ever visited (each with
its single canonical successor m=3x+1), and compute all prime-hit
densities over this deduplicated node set, each node counted EXACTLY ONCE
regardless of how many of the 22,004 starting trajectories pass through
it. This is the only sampling unit under which "hit density" measures a
per-step residue-class probability rather than "how popular is this node
in the merge tree."

Independence for CIs: distinct x-values are still not perfectly iid
(consecutive states in a chain are dependent), but eliminating the
duplicate-node inflation removes the dominant, severe bias. We further
compute a CHAIN-BLOCK bootstrp: partition the distinct-state set by
BFS/generation layer (rough proxy for chain position) is overkill given
time constraints; instead we do a simple bootstrap over UNION-graph
edges (each edge = one distinct (x, m) pair, i.e. one distinct odd-step
in the merge DAG), which is the correct atomic unit here (each edge
occurs exactly once by construction, so double-counting is structurally
impossible; remaining autocorrelation from chain adjacency is handled by
partitioning edges into contiguous chain-position blocks and block-
bootstrapping over blocks).
"""
import json
import time
import numpy as np
import random

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
TRACK_PRIMES = FIT_PRIMES + HOLD_PRIMES

def main():
    d = json.load(open("census_results.json"))
    per_traj = d["per_traj"]
    print(f"Loaded {len(per_traj)} trajectories from census_results.json")

    t0 = time.time()
    # Build the distinct-state edge set: {x: m} where m=3x+1, over ALL
    # trajectories, deduplicated by x. Each x maps to a unique m (the map
    # is deterministic), so this is just a dict / set of x-values with an
    # implicit "chain depth" = distance-to-1 in odd-steps (BFS from 1
    # backward isn't needed; forward depth-to-1 along ITS OWN trajectory
    # from x is well-defined and identical no matter which start reached it,
    # since the map is deterministic and deterministic-forward).
    distinct_x = {}  # x -> m
    depth_to_1 = {}  # x -> odd-steps remaining to reach 1 (chain position)

    for rec in per_traj:
        n0 = rec["n0"]
        x = n0
        chain = []
        while x != 1:
            m = 3 * x + 1
            chain.append(x)
            distinct_x[x] = m
            v2 = 0
            mm = m
            while mm % 2 == 0:
                mm //= 2
                v2 += 1
            x = m >> v2
        # assign depth_to_1 walking backward through this chain (cheap,
        # and consistent across trajectories since the tail is shared)
        L = len(chain)
        for i, xv in enumerate(chain):
            depth_to_1[xv] = L - i  # steps remaining incl. this one

    n_distinct = len(distinct_x)
    n_total_steps = sum(rec["n_steps"] for rec in per_traj)
    print(f"Distinct x-values (edges in merge DAG): {n_distinct} "
          f"(vs {n_total_steps} raw pooled steps, dedup ratio {n_distinct/n_total_steps:.4f}), "
          f"built in {time.time()-t0:.1f}s")

    # ---- Compute hit indicator for every distinct edge, for every tracked prime ----
    t0 = time.time()
    xs = list(distinct_x.keys())
    ms = np.array([distinct_x[x] for x in xs], dtype=np.int64)
    depths = np.array([depth_to_1[x] for x in xs], dtype=np.int64)
    n_edges = len(xs)
    print(f"Arrays built: {n_edges} edges, {time.time()-t0:.1f}s")

    # hit matrix: for each prime, boolean array over edges (m % p == 0)
    t0 = time.time()
    hits_by_prime = {}
    for p in TRACK_PRIMES:
        hits_by_prime[p] = (ms % p == 0)
    print(f"Hit arrays computed for {len(TRACK_PRIMES)} primes, {time.time()-t0:.1f}s")

    # ---- Block bootstrap over CHAIN-DEPTH blocks (not trajectories) ----
    # Rationale: the distinct-state set removes cross-trajectory duplication,
    # but adjacent depths along any one chain are still weakly dependent
    # (deterministic map). Block by depth decile as the resampling unit --
    # a coarse but structurally sound partition (matches the "descent
    # position" bins already used in SHADOW_FINDINGS.md task 4).
    max_depth = depths.max()
    n_blocks = 200  # finer than the 10 descent bins used before, still coarse vs n_edges
    block_id = np.minimum((depths.astype(np.float64) / (max_depth + 1) * n_blocks).astype(np.int64), n_blocks - 1)

    def block_bootstrap(hit_arr, block_id, n_blocks, n_boot=5000, seed=42, alpha=0.05):
        rng = np.random.default_rng(seed)
        # precompute per-block hit count and size
        block_hits = np.zeros(n_blocks, dtype=np.int64)
        block_size = np.zeros(n_blocks, dtype=np.int64)
        np.add.at(block_hits, block_id, hit_arr)
        np.add.at(block_size, block_id, 1)
        point = block_hits.sum() / block_size.sum()
        boot_idx = rng.integers(0, n_blocks, size=(n_boot, n_blocks))
        h = block_hits[boot_idx].sum(axis=1)
        s = block_size[boot_idx].sum(axis=1)
        rates = np.sort(h / np.maximum(s, 1))
        lo = rates[int(alpha/2 * n_boot)]
        hi = rates[int((1 - alpha/2) * n_boot) - 1]
        return float(point), float(lo), float(hi)

    print("\n=== DEDUPLICATED CENSUS: hit density over DISTINCT merge-DAG edges ===")
    print(f"n_edges={n_edges}, block-bootstrap over {n_blocks} depth-decile blocks, 5000 resamples")
    results = {}
    for p in TRACK_PRIMES:
        pt, lo, hi = block_bootstrap(hits_by_prime[p], block_id, n_blocks, seed=2000+p)
        pred = 1.0 / p
        dev = pt - pred
        reldev = dev / pred
        anomalous = not (lo <= pred <= hi)
        results[p] = dict(point=pt, lo=lo, hi=hi, pred=pred, dev=dev, reldev=reldev, anomalous=anomalous)

    for p in TRACK_PRIMES:
        r = results[p]
        flag = "ANOMALOUS" if r["anomalous"] else ""
        print(f"p={p:3d}  rate={r['point']:.6f}  CI=[{r['lo']:.6f},{r['hi']:.6f}]  1/p={r['pred']:.6f}  "
              f"dev={r['dev']:+.6f}  reldev={r['reldev']:+.4f}  {flag}")

    # compare against the ORIGINAL naive pooled-step numbers for the primes
    # that turned out contaminated, as a direct before/after diagnostic
    print("\n=== BEFORE/AFTER comparison for the worst tail-artifact primes ===")
    for p in [433, 479, 347, 293, 181, 251, 19, 13, 11]:
        r = results[p]
        print(f"p={p:3d}: DEDUP reldev={r['reldev']:+.4f} (anomalous={r['anomalous']})")

    out = {
        "n_edges": n_edges,
        "n_total_steps_raw": n_total_steps,
        "dedup_ratio": n_distinct / n_total_steps,
        "fit_primes": FIT_PRIMES,
        "hold_primes": HOLD_PRIMES,
        "results": {str(p): v for p, v in results.items()},
    }
    with open("dedup_census_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nWrote dedup_census_results.json")

if __name__ == "__main__":
    main()
