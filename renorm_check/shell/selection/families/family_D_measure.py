#!/usr/bin/env python3
"""
Design C step (d) -- D(m) measurement for the three word families,
m=2..14 (m=15 where the 8GB guard allows), 53 steps, fully populated
start, per W6C_SELECTION_ORDER.md / SYNTHESIS F8's D(m) readout:

  D(m) = min ceiling-distance (C-d) of a live terminal (d, r=1 mod 3^m)
  after one 53-step heartbeat from the fully populated start.

Margin rule (binding): start at C=12, report shell depth (max
ceiling-distance among dead, non-multiple-of-3 residues -- the
death-shell boundary, exactly as capstone_m16.py's
compute_D_and_shell_depth) and floor margin (C - shell_depth) every
row. If margin < 2, widen C and rerun that row.

int32 permutation arrays (values < 3^15 < 2^31, safe). Progress logged
per step (elapsed, live count, RSS) since m=13..15 runs take real time.
Designed to be launched via `python3 family_D_measure.py <family> |
tee <family>_D.log` in the background per the work order's guidance
for long runs.
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "embedding"))

import numpy as np
from automaton import allowed_exponents, mod_inverse
from family_credits import FAMILIES

STEPS = 53
C_START = 12
M_MIN = 2
M_MAX_DEFAULT = 15  # try 15; guard may cap it per-row


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
    return perms


def run_heartbeat_with_progress(C: int, m: int, credit_fn, steps: int, log_prefix: str):
    modulus = 3 ** m
    max_credit = 2
    max_a = C + max_credit
    total_states = (C + 1) * modulus
    guard = 6_000_000_000  # 6e9 states as an int32-array proxy guard (well under 8GB in practice)
    print(f"{log_prefix}modulus=3^{m}={modulus}, C={C}, total_states={total_states}", flush=True)

    t_perm0 = time.time()
    perms = build_all_permutations(m, max_a)
    print(f"{log_prefix}permutations built (a=1..{max_a}) in {time.time()-t_perm0:.1f}s "
          f"RSS={get_rss_mb():.0f}MB", flush=True)

    live_by_d = {d: np.ones(modulus, dtype=bool) for d in range(C + 1)}
    total0 = sum(int(arr.sum()) for arr in live_by_d.values())
    print(f"{log_prefix}step init: total_live={total0} RSS={get_rss_mb():.0f}MB", flush=True)

    t0 = time.time()
    for k in range(steps):
        c_k = credit_fn(k)
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
        if (k + 1) % 10 == 0 or k == steps - 1:
            total = sum(int(arr.sum()) for arr in live_by_d.values())
            elapsed = time.time() - t0
            print(f"{log_prefix}step {k+1:2d}/{steps} c_k={c_k} total_live={total} "
                  f"elapsed={elapsed:.1f}s RSS={get_rss_mb():.0f}MB", flush=True)
    del perms
    return live_by_d


def compute_D_and_shell_depth(live_by_d: dict, C: int, m: int):
    modulus = 3 ** m
    target_residue = 1 % modulus
    alive_depths = [C - d for d in range(C + 1) if live_by_d[d][target_residue]]
    D_m = min(alive_depths) if alive_depths else None

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
    return D_m, shell_depth


def measure_row(name: str, m: int, C: int, credit_fn, max_widen: int = 3):
    """Measure D(m) at corridor C; widen C by +4 and rerun (up to
    max_widen times) if floor margin < 2, per the margin rule."""
    attempt = 0
    C_try = C
    while True:
        t_row0 = time.time()
        log_prefix = f"    [{name} m={m} C={C_try}] "
        live_by_d = run_heartbeat_with_progress(C_try, m, credit_fn, STEPS, log_prefix)
        D_m, shell_depth = compute_D_and_shell_depth(live_by_d, C_try, m)
        margin = (C_try - shell_depth) if shell_depth is not None else C_try
        row_elapsed = time.time() - t_row0
        print(f"    [{name} m={m}] C={C_try} D={D_m} shell_depth={shell_depth} "
              f"margin={margin} elapsed={row_elapsed:.1f}s", flush=True)
        del live_by_d
        if margin is None or margin >= 2 or attempt >= max_widen:
            return {"m": m, "C_used": C_try, "D": D_m, "shell_depth": shell_depth,
                     "margin": margin, "elapsed_s": round(row_elapsed, 1),
                     "widened": attempt > 0}
        print(f"    [{name} m={m}] margin {margin} < 2 -- widening C and rerunning "
              f"(attempt {attempt+1}/{max_widen})", flush=True)
        C_try += 4
        attempt += 1


def measure_family(name: str, m_max: int = M_MAX_DEFAULT, memory_guard_bytes: int = 8 * 1024**3):
    credit_fn = FAMILIES[name]["credit_fn"]
    print(f"\n=== D(m) measurement: family {name}, m={M_MIN}..{m_max}, C_start={C_START} ===",
          flush=True)
    print(f"start time: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    t_family0 = time.time()

    results = []
    for m in range(M_MIN, m_max + 1):
        # Rough memory estimate for this row at the max C we might widen to
        # (C_START + 4*3 = 24 worst case): permutations (int32, ~4 bytes)
        # for a=1..C_max+2, plus two generations of bool arrays.
        modulus = 3 ** m
        C_worst = C_START + 4 * 3
        est_perm_bytes = (C_worst + 2) * modulus * 4
        est_bool_bytes = 2 * (C_worst + 1) * modulus
        est_total = est_perm_bytes + est_bool_bytes
        if est_total > memory_guard_bytes:
            print(f"  [{name} m={m}] SKIPPED: estimated worst-case memory "
                  f"{est_total/1e9:.2f}GB > 8GB guard. Wall hit at m={m}.", flush=True)
            results.append({"m": m, "C_used": None, "D": None, "shell_depth": None,
                             "margin": None, "elapsed_s": None, "widened": False,
                             "wall": "memory_guard"})
            continue
        row = measure_row(name, m, C_START, credit_fn)
        row["wall"] = ""
        results.append(row)

    total_elapsed = time.time() - t_family0
    print(f"=== {name} D(m) measurement done: {total_elapsed:.1f}s "
          f"({total_elapsed/60:.1f} min) ===", flush=True)

    out_path = Path(__file__).parent / f"{name}_D.csv"
    fieldnames = ["m", "C_used", "D", "shell_depth", "margin", "elapsed_s", "widened", "wall"]
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in results:
            w.writerow(r)
    print(f"Wrote {out_path}", flush=True)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("family", choices=list(FAMILIES.keys()))
    parser.add_argument("--m-max", type=int, default=M_MAX_DEFAULT)
    args = parser.parse_args()
    measure_family(args.family, m_max=args.m_max)
