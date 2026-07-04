#!/usr/bin/env python3
"""
W6D-G -- rerun confirmation for every row where a periodic-convergent
word's D(m) disagrees with its true-word counterpart, per the order:
"Any row where a periodic-convergent word and its true Sturmian word
disagree must be rerun once for confirmation and then reported loudly."

Reruns each flagged row at steps=106 (double the standard heartbeat,
matching the G1 steps-invariance spot-check convention) AND at a widened
C (+4) to rule out floor contamination, using the SAME
run_heartbeat_generic path as measure_d.py (int32-patched permutation
cache). Confirms the disagreement is stable, not a margin artifact.
"""
from __future__ import annotations
import csv, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "toy_word"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "embedding"))

import numpy as np
import toy_automaton as _toy_mod
from toy_automaton import run_heartbeat_generic
from automaton import mod_inverse
from underlock_words import credit_golden_per8, credit_sqrt2_per12

def _get_permutation_int32(a, modulus):
    key = (a, modulus)
    if key not in _toy_mod._PERM_CACHE:
        r = np.arange(modulus, dtype=np.int64)
        inv2a = mod_inverse(pow(2, a, modulus), modulus)
        r_prime = ((3 * r + 1) % modulus) * inv2a % modulus
        _toy_mod._PERM_CACHE[key] = r_prime.astype(np.int32)
    return _toy_mod._PERM_CACHE[key]
_toy_mod._get_permutation = _get_permutation_int32

def measure(credit_fn, C, m, steps):
    modulus = 3 ** m
    live_by_d, _ = run_heartbeat_generic(C, m, credit_fn, steps=steps, max_states_guard=400_000_000)
    target = 1 % modulus
    alive = [C - d for d in range(C+1) if live_by_d[d][target]]
    D = min(alive) if alive else None
    _toy_mod._PERM_CACHE.clear()
    return D

def read_csv(path):
    with open(path) as f:
        return list(csv.DictReader(f))

true_golden = {int(r["m"]): int(r["D_toy"]) for r in read_csv("../toy_word/D_toy_table.csv")}
true_golden[16] = 6
per8_table = {int(r["m"]): (int(r["D"]), int(r["C_final"])) for r in read_csv("D_golden_per8_table.csv")}

true_sqrt2 = {int(r["m"]): int(r["D_sqrt2"]) for r in read_csv("../selection/sqrt2/D_sqrt2_table.csv")}
per12_table = {int(r["m"]): (int(r["D"]), int(r["C_final"])) for r in read_csv("D_sqrt2_per12_table.csv")}

golden_dis = [m for m in range(2,14) if true_golden[m] != per8_table[m][0]]
sqrt2_dis = [m for m in range(2,14) if true_sqrt2[m] != per12_table[m][0]]

print("golden-per8 disagreement rows:", golden_dis)
print("sqrt2-per12 disagreement rows:", sqrt2_dis)

results = []
print("\n=== golden-per8 reruns (steps=106, C+4) ===")
for m in golden_dis:
    D_orig, C_orig = per8_table[m]
    C_wide = C_orig + 4
    t0=time.time()
    D_rerun_steps = measure(credit_golden_per8, C_orig, m, steps=106)
    D_rerun_C = measure(credit_golden_per8, C_wide, m, steps=53)
    elapsed = time.time()-t0
    stable = (D_rerun_steps == D_orig) and (D_rerun_C == D_orig)
    print(f"  m={m:2d}: D_orig={D_orig} true={true_golden[m]} | "
          f"rerun@steps=106,C={C_orig}: D={D_rerun_steps} | "
          f"rerun@steps=53,C={C_wide}: D={D_rerun_C} | "
          f"STABLE={stable} elapsed={elapsed:.2f}s")
    results.append(("golden-per8", m, D_orig, true_golden[m], D_rerun_steps, D_rerun_C, stable))

print("\n=== sqrt2-per12 reruns (steps=106, C+4) ===")
for m in sqrt2_dis:
    D_orig, C_orig = per12_table[m]
    C_wide = C_orig + 4
    t0=time.time()
    D_rerun_steps = measure(credit_sqrt2_per12, C_orig, m, steps=106)
    D_rerun_C = measure(credit_sqrt2_per12, C_wide, m, steps=53)
    elapsed = time.time()-t0
    stable = (D_rerun_steps == D_orig) and (D_rerun_C == D_orig)
    print(f"  m={m:2d}: D_orig={D_orig} true={true_sqrt2[m]} | "
          f"rerun@steps=106,C={C_orig}: D={D_rerun_steps} | "
          f"rerun@steps=53,C={C_wide}: D={D_rerun_C} | "
          f"STABLE={stable} elapsed={elapsed:.2f}s")
    results.append(("sqrt2-per12", m, D_orig, true_sqrt2[m], D_rerun_steps, D_rerun_C, stable))

out_path = Path("rerun_disagreements.csv")
with open(out_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["word", "m", "D_orig", "D_true", "D_rerun_steps106", "D_rerun_Cwide", "stable"])
    for row in results:
        w.writerow(row)
print(f"\nWrote {out_path}")
