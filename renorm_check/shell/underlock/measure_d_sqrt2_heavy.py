#!/usr/bin/env python3
"""
W6D-G -- dedicated heavy runner for sqrt2-per12, m=14..16, per the order's
note that these are the only heavy rows (the true-word W6C run needed
C=16 and a dedicated int32 runner at m=16, ~30 min). Same design as
shell/toy_word/capstone_m16.py: permutations for all needed exponents
precomputed ONCE and cached in a plain dict (int32), per-step progress
logging (step index, elapsed, total live count, RSS) so a stall is
visible while backgrounded.

Margin rule: start C=16 (matching the true-word table's C_final=16 at
m=14/16 in D_sqrt2_table.csv), widen by +2 and rerun if margin < 2.

Controls FIRST: recompute m=11 and m=13 at this runner's start C and
compare against measure_d.py's already-written D_sqrt2_per12_table.csv
values (D=6, D=7) -- confirms this independent code path agrees before
trusting the heavy rows.

Usage (background):
  nohup python3 measure_d_sqrt2_heavy.py > measure_d_sqrt2_heavy.log 2>&1 &
"""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "embedding"))

import numpy as np
from automaton import allowed_exponents, mod_inverse

from underlock_words import credit_sqrt2_per12

STEPS = 53
C_START = 16
MARGIN_FLOOR = 2
MAX_C = 22


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
    modulus = 3 ** m
    perms = {}
    for a in range(1, max_a + 1):
        r = np.arange(modulus, dtype=np.int64)
        inv2a = mod_inverse(pow(2, a, modulus), modulus)
        r_prime = ((3 * r + 1) % modulus) * inv2a % modulus
        perms[a] = r_prime.astype(np.int32)
        if a % 4 == 0 or a == max_a:
            print(f"    precomputed permutation a={a}/{max_a} (RSS={get_rss_mb():.0f}MB)", flush=True)
    return perms


def run_heavy_heartbeat(C: int, m: int, steps: int = STEPS, log_prefix: str = ""):
    modulus = 3 ** m
    max_credit = 2  # sqrt2 credit in {1,2}, Beatty word slope in (1,2)
    max_a = C + max_credit
    print(f"{log_prefix}building permutations for a=1..{max_a}, modulus=3^{m}={modulus:,}", flush=True)
    t_perm0 = time.time()
    perms = build_all_permutations(m, max_a)
    print(f"{log_prefix}permutations built in {time.time()-t_perm0:.1f}s, RSS={get_rss_mb():.0f}MB", flush=True)

    live_by_d = {d: np.ones(modulus, dtype=bool) for d in range(C + 1)}
    total0 = sum(int(arr.sum()) for arr in live_by_d.values())
    print(f"{log_prefix}step -1 (init): total_live={total0} RSS={get_rss_mb():.0f}MB", flush=True)

    t0 = time.time()
    for k in range(steps):
        c_k = credit_sqrt2_per12(k)
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
        elapsed = time.time() - t0
        print(f"{log_prefix}step {k:2d}/{steps} c_k={c_k} total_live={total} "
              f"elapsed={elapsed:.1f}s RSS={get_rss_mb():.0f}MB", flush=True)

    del perms
    return live_by_d


def compute_D_and_shell_depth(live_by_d: dict, C: int, m: int):
    modulus = 3 ** m
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
    return D_val, shell_depth


def run_control(m: int, expected: int, C: int):
    print(f"\n=== CONTROL: D_sqrt2-per12({m}) at C={C} (expect {expected}, from "
          f"D_sqrt2_per12_table.csv) ===", flush=True)
    live_by_d = run_heavy_heartbeat(C, m, steps=STEPS, log_prefix=f"  [control m={m}] ")
    D_val, shell_depth = compute_D_and_shell_depth(live_by_d, C, m)
    print(f"  [control m={m}] D@C={C} = {D_val} (expected {expected}) shell_depth={shell_depth}",
          flush=True)
    del live_by_d
    return D_val


def row_with_margin_rule(m: int, C0: int):
    C = C0
    attempts = []
    while True:
        t0 = time.time()
        print(f"\n=== THE ROW: sqrt2-per12 m={m} at C={C} ===", flush=True)
        live_by_d = run_heavy_heartbeat(C, m, steps=STEPS, log_prefix=f"  [m={m} C={C}] ")
        D_val, shell_depth = compute_D_and_shell_depth(live_by_d, C, m)
        del live_by_d
        elapsed = time.time() - t0
        margin = (C - shell_depth) if shell_depth is not None else C
        print(f"  [m={m}] D={D_val} shell_depth={shell_depth} margin={margin} "
              f"C={C} elapsed={elapsed:.1f}s RSS={get_rss_mb():.0f}MB", flush=True)
        attempts.append({"C": C, "D": D_val, "shell_depth": shell_depth,
                          "margin": margin, "wall_s": round(elapsed, 1)})
        if margin is not None and margin >= MARGIN_FLOOR:
            return D_val, shell_depth, margin, attempts
        if C >= MAX_C:
            print(f"  [m={m}] margin rule NOT satisfied even at C={C} (max_C guard) "
                  "-- reporting last attempt honestly, wall hit.", flush=True)
            return D_val, shell_depth, margin, attempts
        C_new = C + 2
        print(f"  [m={m}] margin={margin} < {MARGIN_FLOOR}, widening C {C} -> {C_new} "
              "and rerunning row", flush=True)
        C = C_new


def main():
    t_start = time.time()
    print("W6D-G -- sqrt2-per12 heavy runner, m=14..16", flush=True)
    print(f"start: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

    # Controls first: m=11 (expect D=6), m=13 (expect D=7) at C_START.
    d11 = run_control(11, expected=6, C=C_START)
    d13 = run_control(13, expected=7, C=C_START)
    control_pass = (d11 == 6) and (d13 == 7)
    print(f"\n=== CONTROL SUMMARY: D(11)@C={C_START}={d11} (expect 6), "
          f"D(13)@C={C_START}={d13} (expect 7) -- {'PASS' if control_pass else 'FAIL'} ===",
          flush=True)
    if not control_pass:
        print("STOP: controls FAILED -- not running the heavy rows.", flush=True)
        sys.exit(2)

    rows = []
    for m in (14, 15, 16):
        D_val, shell_depth, margin, attempts = row_with_margin_rule(m, C_START)
        final_C = attempts[-1]["C"]
        rows.append({"m": m, "D": D_val, "C_final": final_C,
                      "shell_depth": shell_depth, "margin": margin,
                      "n_attempts": len(attempts),
                      "row_wall_s": round(sum(a["wall_s"] for a in attempts), 1)})
        print(f"[m={m}] FINAL: D={D_val} C={final_C} shell_depth={shell_depth} "
              f"margin={margin}", flush=True)

    out_path = Path(__file__).parent / "D_sqrt2_per12_heavy_table.csv"
    with open(out_path, "w", newline="") as f:
        fieldnames = ["m", "D", "C_final", "shell_depth", "margin", "n_attempts", "row_wall_s"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote {out_path}", flush=True)

    total_elapsed = time.time() - t_start
    print(f"\nTotal elapsed: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)", flush=True)
    print(f"end: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)


if __name__ == "__main__":
    main()
