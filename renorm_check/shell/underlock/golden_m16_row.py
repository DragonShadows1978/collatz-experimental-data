#!/usr/bin/env python3
"""
W6D-G -- golden-per8 m=16 row, completing PD1's "(and 16 if run)".

FORWARD PREDICTION (registered here, pre-run, from the exact law
D_per8(m) = floor((3m+1)/8) that fit 12/12 rows m=2..13):
    D_per8(16) = floor(49/8) = 6.
True-word capstone value: D_golden-true(16) = 6 (capstone_m16.csv).
Law arithmetic (3*16 = 48 == 0 mod 8) predicts an AGREEMENT row.

Same heavy-runner design as measure_d_sqrt2_heavy.py (precomputed int32
permutations, per-step logging, margin rule from C=14 -- the true-word
capstone's corridor, which had floor margin 3 there).
Controls first: m=11 (expect 4), m=13 (expect 5) at C=14.
"""
from __future__ import annotations
import csv, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "embedding"))

import numpy as np
from automaton import allowed_exponents, mod_inverse
from underlock_words import credit_golden_per8

STEPS = 53
C_START = 14
MARGIN_FLOOR = 2
MAX_C = 20

def get_rss_mb():
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024.0
    except Exception:
        pass
    return -1.0

def run(C, m, log_prefix=""):
    modulus = 3 ** m
    max_a = C + 2
    print(f"{log_prefix}building permutations a=1..{max_a}, modulus=3^{m}={modulus:,}", flush=True)
    perms = {}
    for a in range(1, max_a + 1):
        r = np.arange(modulus, dtype=np.int64)
        inv2a = mod_inverse(pow(2, a, modulus), modulus)
        perms[a] = (((3 * r + 1) % modulus) * inv2a % modulus).astype(np.int32)
    print(f"{log_prefix}perms built, RSS={get_rss_mb():.0f}MB", flush=True)
    live_by_d = {d: np.ones(modulus, dtype=bool) for d in range(C + 1)}
    t0 = time.time()
    for k in range(STEPS):
        c_k = credit_golden_per8(k)
        nxt = {d: np.zeros(modulus, dtype=bool) for d in range(C + 1)}
        for d in range(C + 1):
            idxs = np.nonzero(live_by_d[d])[0]
            if idxs.size == 0:
                continue
            for a in allowed_exponents(d, c_k, C):
                nxt[d + c_k - a][perms[a][idxs]] = True
        live_by_d = nxt
        if k % 10 == 9 or k == STEPS - 1:
            print(f"{log_prefix}step {k}/{STEPS} elapsed={time.time()-t0:.0f}s RSS={get_rss_mb():.0f}MB", flush=True)
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

print("W6D-G -- golden-per8 m=16 row (PD1 completion)", flush=True)
print(f"start: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
print("FORWARD PREDICTION: D_per8(16) = floor(49/8) = 6 (exact law from 12/12 fit)", flush=True)

# Controls
for m_c, exp in ((11, 4), (13, 5)):
    D, sd, mg = run(C_START, m_c, log_prefix=f"  [control m={m_c}] ")
    status = "PASS" if D == exp else "FAIL"
    print(f"CONTROL m={m_c}: D={D} (expect {exp}) shell_depth={sd} margin={mg} {status}", flush=True)
    if D != exp:
        print("STOP: control failed; not running m=16.", flush=True)
        sys.exit(2)

# The row, with margin rule
C = C_START
while True:
    t0 = time.time()
    D, sd, mg = run(C, 16, log_prefix=f"  [m=16 C={C}] ")
    print(f"[m=16] D={D} shell_depth={sd} margin={mg} C={C} wall={time.time()-t0:.0f}s", flush=True)
    if mg is not None and mg >= MARGIN_FLOOR:
        break
    if C >= MAX_C:
        print("[m=16] margin rule NOT satisfied at max_C -- reporting honestly.", flush=True)
        break
    print(f"[m=16] margin={mg} < {MARGIN_FLOOR}, widening C {C} -> {C+2}", flush=True)
    C += 2

with open(Path(__file__).parent / "D_golden_per8_m16.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["m", "D", "C_final", "shell_depth", "margin", "predicted", "true_word_value"])
    w.writerow([16, D, C, sd, mg, 6, 6])
print("Wrote D_golden_per8_m16.csv", flush=True)
verdict = "PREDICTION CONFIRMED (6)" if D == 6 else f"PREDICTION MISSED (got {D}, predicted 6)"
print(f"VERDICT: {verdict}", flush=True)
print(f"end: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
