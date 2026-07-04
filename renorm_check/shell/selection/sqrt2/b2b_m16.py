#!/usr/bin/env python3
"""
W6C Design B, B2b -- the m=16 row, dedicated runner.

b2_measurement.py's m=16 attempt hit run_heartbeat_generic's default
max_states_guard=400M ((C+1)*3^16 = 559.6M states at C=12) -- a
STATE-COUNT guard, not the binding 8GB MEMORY guard. This runner
follows shell/toy_word/capstone_m16.py's proven memory design instead:

  - int32 permutation arrays (172MB each at 3^16), NOT toy_automaton's
    module-level int64 _PERM_CACHE (which would need 6.2GB for perms
    alone at C=16 and bust the 8GB guard);
  - permutations precomputed once per (C, m) attempt, freed between
    attempts;
  - bool occupancy arrays, current + next generation;
  - per-step progress logging (step, credit, live count, elapsed, RSS)
    so a stall is visible while tailing the log in a background run.

Estimated peak at C=16, m=16: 18 perms x 172MB = 3.1GB + 2 x 17 x 43MB
bool = 1.5GB + transient int64 build buffers ~0.9GB => ~5.5GB, inside
the 8GB guard. If an escalation beyond C=18 were demanded by the
margin rule, C=20/22 still fit (~5.8/6.2GB); hard abort if RSS
approaches 7.5GB, reported as an honest wall.

Margin-rule protocol identical to b2_measurement.py: start C=12,
require margin >= 2, widen by +2 and rerun on violation.

Usage: nohup python3 b2b_m16.py > b2b_m16.log 2>&1 &
"""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "embedding"))

import numpy as np
from automaton import allowed_exponents, mod_inverse
from sqrt2_automaton import credit_sqrt2

M = 16
STEPS = 53
C_START = 12
MARGIN_FLOOR = 2
MAX_C = 22
RSS_ABORT_MB = 7500.0


def get_rss_mb() -> float:
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024.0
    except Exception:
        pass
    return -1.0


def build_all_permutations(m: int, max_a: int) -> dict:
    """int32 permutations for a=1..max_a (values < 3^16 < 2^31)."""
    modulus = 3 ** m
    perms = {}
    for a in range(1, max_a + 1):
        r = np.arange(modulus, dtype=np.int64)
        inv2a = mod_inverse(pow(2, a, modulus), modulus)
        r_prime = ((3 * r + 1) % modulus) * inv2a % modulus
        perms[a] = r_prime.astype(np.int32)
        del r, r_prime
        print(f"    perm a={a} built (RSS={get_rss_mb():.0f}MB)", flush=True)
        if get_rss_mb() > RSS_ABORT_MB:
            raise MemoryError(f"RSS {get_rss_mb():.0f}MB > abort ceiling {RSS_ABORT_MB}MB")
    return perms


def run_attempt(C: int, m: int = M, steps: int = STEPS):
    modulus = 3 ** m
    max_a = C + 2  # credits are in {1,2}
    print(f"  [C={C}] building perms a=1..{max_a}, modulus=3^{m}={modulus}", flush=True)
    t0 = time.time()
    perms = build_all_permutations(m, max_a)
    print(f"  [C={C}] perms built in {time.time()-t0:.1f}s RSS={get_rss_mb():.0f}MB", flush=True)

    live_by_d = {d: np.ones(modulus, dtype=bool) for d in range(C + 1)}
    t0 = time.time()
    for k in range(steps):
        c_k = credit_sqrt2(k)
        next_live_by_d = {d: np.zeros(modulus, dtype=bool) for d in range(C + 1)}
        for d in range(C + 1):
            src = live_by_d[d]
            live_r_indices = np.nonzero(src)[0]
            if live_r_indices.size == 0:
                continue
            for a in allowed_exponents(d, c_k, C):
                d_prime = d + c_k - a
                perm = perms[a]
                targets = perm[live_r_indices]
                next_live_by_d[d_prime][targets] = True
        live_by_d = next_live_by_d
        total = sum(int(arr.sum()) for arr in live_by_d.values())
        rss = get_rss_mb()
        print(f"  [C={C}] step {k:2d}/{steps} c_k={c_k} total_live={total} "
              f"elapsed={time.time()-t0:.1f}s RSS={rss:.0f}MB", flush=True)
        if rss > RSS_ABORT_MB:
            raise MemoryError(f"RSS {rss:.0f}MB > abort ceiling {RSS_ABORT_MB}MB")

    del perms

    target_residue = 1 % modulus
    alive_depths = [C - d for d in range(C + 1) if live_by_d[d][target_residue]]
    D_val = min(alive_depths) if alive_depths else None

    shell_depth = None
    for d in range(0, C + 1):
        arr = live_by_d[d]
        dead_mask = ~arr
        if not dead_mask.any():
            continue
        idx = np.nonzero(dead_mask)[0]
        nonmult3 = idx[idx % 3 != 0]
        if nonmult3.size > 0:
            shell_depth = C - d
            break
    del live_by_d
    margin = (C - shell_depth) if shell_depth is not None else C
    return D_val, shell_depth, margin


def main():
    t_start = time.time()
    print(f"W6C Design B, B2b -- D_sqrt2({M}) dedicated runner "
          f"(int32 perms, capstone_m16 memory design)", flush=True)
    print(f"start: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

    C = C_START
    attempts = []
    final = None
    while True:
        print(f"\n=== attempt C={C} ===", flush=True)
        t0 = time.time()
        try:
            D_val, shell_depth, margin = run_attempt(C)
        except MemoryError as e:
            print(f"  MEMORY WALL at C={C}: {e} -- reporting honestly, stopping.", flush=True)
            attempts.append({"C": C, "D": None, "shell_depth": None,
                             "margin": None, "wall_s": round(time.time() - t0, 1),
                             "note": "memory_wall"})
            break
        wall = time.time() - t0
        print(f"  C={C}: D={D_val} shell_depth={shell_depth} margin={margin} "
              f"wall={wall:.1f}s", flush=True)
        attempts.append({"C": C, "D": D_val, "shell_depth": shell_depth,
                         "margin": margin, "wall_s": round(wall, 1), "note": ""})
        if margin is not None and margin >= MARGIN_FLOOR:
            final = (D_val, shell_depth, margin, C)
            break
        if C >= MAX_C:
            print(f"  margin rule unsatisfied at C={C} (MAX_C) -- honest wall.", flush=True)
            final = (D_val, shell_depth, margin, C)
            break
        print(f"  margin={margin} < {MARGIN_FLOOR}: widening C {C} -> {C+2}", flush=True)
        C += 2

    out = Path(__file__).parent / "D_sqrt2_m16.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["C", "D", "shell_depth", "margin", "wall_s", "note"])
        w.writeheader()
        for a in attempts:
            w.writerow(a)
    print(f"\nWrote {out}", flush=True)

    if final:
        D_val, shell_depth, margin, C_final = final
        print(f"\nFINAL: D_sqrt2({M}) = {D_val}  C={C_final} "
              f"shell_depth={shell_depth} margin={margin}", flush=True)
    else:
        print(f"\nFINAL: m={M} row NOT obtained (memory wall) -- reported honestly.", flush=True)

    total = time.time() - t_start
    print(f"Total elapsed: {total:.1f}s ({total/60:.1f} min)", flush=True)
    print(f"end: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)


if __name__ == "__main__":
    main()
