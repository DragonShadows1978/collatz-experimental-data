#!/usr/bin/env python3
"""
W6D-G -- rerun confirmation for the sqrt2-per12 m=14..16 disagreement
rows (vs true-word D_sqrt2_table.csv values 9/9/10), per the order's
"rerun once for confirmation" rule. Rerun at C=18 (widened +2 from the
original C=16) -- in a deterministic pipeline, varying the corridor
width is the meaningful confirmation (identical-C rerun is a no-op).
Same heavy-runner design (precomputed int32 permutations, per-step log).
"""
from __future__ import annotations
import csv, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "embedding"))

import numpy as np
from automaton import allowed_exponents, mod_inverse
from underlock_words import credit_sqrt2_per12

STEPS = 53
C_RERUN = 18

def get_rss_mb():
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024.0
    except Exception:
        pass
    return -1.0

def run(C, m):
    modulus = 3 ** m
    max_a = C + 2
    print(f"  [m={m} C={C}] building permutations a=1..{max_a}, modulus=3^{m}={modulus:,}", flush=True)
    perms = {}
    for a in range(1, max_a + 1):
        r = np.arange(modulus, dtype=np.int64)
        inv2a = mod_inverse(pow(2, a, modulus), modulus)
        perms[a] = (((3 * r + 1) % modulus) * inv2a % modulus).astype(np.int32)
    print(f"  [m={m} C={C}] perms built, RSS={get_rss_mb():.0f}MB", flush=True)
    live_by_d = {d: np.ones(modulus, dtype=bool) for d in range(C + 1)}
    t0 = time.time()
    for k in range(STEPS):
        c_k = credit_sqrt2_per12(k)
        nxt = {d: np.zeros(modulus, dtype=bool) for d in range(C + 1)}
        for d in range(C + 1):
            idxs = np.nonzero(live_by_d[d])[0]
            if idxs.size == 0:
                continue
            for a in allowed_exponents(d, c_k, C):
                nxt[d + c_k - a][perms[a][idxs]] = True
        live_by_d = nxt
        if k % 10 == 9 or k == STEPS - 1:
            print(f"  [m={m} C={C}] step {k}/{STEPS} elapsed={time.time()-t0:.0f}s RSS={get_rss_mb():.0f}MB", flush=True)
    del perms
    target = 1 % modulus
    alive = [C - d for d in range(C + 1) if live_by_d[d][target]]
    D = min(alive) if alive else None
    shell_depth = None
    for d in range(C + 1):
        dead = ~live_by_d[d]
        if not dead.any():
            continue
        idx = np.nonzero(dead)[0]
        if idx[idx % 3 != 0].size > 0:
            shell_depth = C - d
            break
    margin = (C - shell_depth) if shell_depth is not None else C
    return D, shell_depth, margin

EXPECT = {14: 8, 15: 8, 16: 9}  # original C=16 values being confirmed
rows = []
for m in (14, 15, 16):
    t0 = time.time()
    D, sd, mg = run(C_RERUN, m)
    stable = (D == EXPECT[m])
    print(f"[m={m}] RERUN@C={C_RERUN}: D={D} shell_depth={sd} margin={mg} "
          f"(original C=16 D={EXPECT[m]}) CONFIRMED={stable} wall={time.time()-t0:.0f}s", flush=True)
    rows.append({"m": m, "D_rerun_C18": D, "D_orig_C16": EXPECT[m],
                  "shell_depth": sd, "margin": mg, "confirmed": stable})

with open(Path(__file__).parent / "rerun_heavy_confirm.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["m", "D_rerun_C18", "D_orig_C16", "shell_depth", "margin", "confirmed"])
    w.writeheader()
    for r in rows:
        w.writerow(r)
print("Wrote rerun_heavy_confirm.csv", flush=True)
