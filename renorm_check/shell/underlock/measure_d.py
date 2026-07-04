#!/usr/bin/env python3
"""
W6D-G -- G1/G3 measurement: D(m) tables for golden-per8, sqrt2-per12
(m=2..13), and golden-tile8 (m=2..10), per
shell/W6D_GROUND_TRUTH_ORDER.md. sqrt2-per12's heavy tail (m=14..16) is
run separately by measure_d_sqrt2_heavy.py (dedicated int32 runner,
precomputed permutations, per-step logging -- same design as
shell/toy_word/capstone_m16.py, since the order flags m=14..16 as the
only heavy rows).

D(m) readout exactly as W6B/W6C: min ceiling-distance (C - d) of a live
terminal (d, r=1 mod 3^m), 53 steps from the fully populated start.
Margin rule every row: report shell depth + floor margin; if margin < 2,
widen C by +2 and rerun THAT row. Reuses run_heartbeat_generic from
toy_automaton.py directly (per the order), with its permutation cache
monkey-patched to build int32 arrays (order's explicit instruction;
modulus=3^13 = 1,594,323 is far inside int32 range). 8GB memory guard
via RSS logging every row plus the shared max_states_guard.

Steps-invariance spot check (G1): two rows per word rerun at steps=106;
values must not move.

Usage:
  python3 measure_d.py 2>&1 | tee measure_d.log
"""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "toy_word"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "embedding"))

import numpy as np

import toy_automaton as _toy_mod
from toy_automaton import run_heartbeat_generic
from automaton import mod_inverse
from underlock_words import (
    credit_golden_per8, credit_sqrt2_per12, credit_golden_tile8,
    run_all_assertions,
)

MAX_STATES_GUARD = 400_000_000  # (C+1) * 3^m states; matches house convention
MEM_GUARD_MB = 8 * 1024  # 8GB guard, checked via RSS logging


def get_rss_mb() -> float:
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024.0
    except Exception:
        pass
    return -1.0


def _get_permutation_int32(a: int, modulus: int) -> np.ndarray:
    """int32 variant of toy_automaton._get_permutation, per the order's
    'int32 permutation arrays' instruction. All moduli used in this
    script (3^m, m<=13) are far inside int32 range (3^13=1,594,323 <<
    2^31-1), so int32 halves permutation-array memory vs the module
    default int64 with no precision loss."""
    key = (a, modulus)
    if key not in _toy_mod._PERM_CACHE:
        r = np.arange(modulus, dtype=np.int64)  # int64 headroom during modinv arithmetic
        inv2a = mod_inverse(pow(2, a, modulus), modulus)
        r_prime = ((3 * r + 1) % modulus) * inv2a % modulus
        _toy_mod._PERM_CACHE[key] = r_prime.astype(np.int32)
    return _toy_mod._PERM_CACHE[key]


# Monkey-patch toy_automaton's permutation getter to the int32 variant so
# run_heartbeat_generic (which calls _get_permutation internally) uses it.
_toy_mod._get_permutation = _get_permutation_int32


def measure_row(credit_fn, C: int, m: int, steps: int):
    """Run one (C, m) row for the given credit_fn; return
    (D_val, shell_depth, margin, history_sizes)."""
    modulus = 3 ** m
    live_by_d, history_sizes = run_heartbeat_generic(
        C, m, credit_fn, steps=steps, max_states_guard=MAX_STATES_GUARD
    )
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
    margin = (C - shell_depth) if shell_depth is not None else C
    return D_val, shell_depth, margin, history_sizes


def row_with_margin_rule(word_label: str, credit_fn, m: int, C0: int,
                          steps: int = 53, margin_floor: int = 2,
                          max_C: int = 24):
    C = C0
    attempts = []
    while True:
        t0 = time.time()
        modulus = 3 ** m
        est_states = (C + 1) * modulus
        print(f"    [{word_label}] m={m:>2} C={C:>2}: modulus=3^{m}={modulus:,}, "
              f"est_states={est_states:,} (guard={MAX_STATES_GUARD:,})", flush=True)
        try:
            D_val, shell_depth, margin, hist = measure_row(credit_fn, C, m, steps)
        except ValueError as e:
            print(f"    [{word_label}] m={m} C={C}: STATE-SPACE GUARD HIT: {e}", flush=True)
            attempts.append({"C": C, "D": None, "shell_depth": None,
                              "margin": None, "wall_s": time.time() - t0,
                              "note": "guard_hit"})
            _toy_mod._PERM_CACHE.clear()
            return None, None, None, attempts
        elapsed = time.time() - t0
        rss = get_rss_mb()
        mem_note = "" if rss < MEM_GUARD_MB else " *** 8GB MEMORY GUARD EXCEEDED ***"
        print(f"    [{word_label}] m={m:>2} C={C:>2}: D={D_val} shell_depth={shell_depth} "
              f"margin={margin} steps={steps} elapsed={elapsed:.2f}s RSS={rss:.0f}MB{mem_note}",
              flush=True)
        attempts.append({"C": C, "D": D_val, "shell_depth": shell_depth,
                          "margin": margin, "wall_s": round(elapsed, 3), "note": ""})
        _toy_mod._PERM_CACHE.clear()
        if margin is not None and margin >= margin_floor:
            return D_val, shell_depth, margin, attempts
        if C >= max_C:
            print(f"    [{word_label}] m={m}: margin rule NOT satisfied even at C={C} "
                  f"(max_C guard) -- reporting last attempt honestly, wall hit.", flush=True)
            return D_val, shell_depth, margin, attempts
        C_new = C + 2
        print(f"    [{word_label}] m={m}: margin={margin} < {margin_floor}, "
              f"widening C {C} -> {C_new} and rerunning row", flush=True)
        C = C_new


def run_word_table(word_label: str, credit_fn, m_min: int, m_max: int,
                    C_start: int, out_csv: Path, invariance_check_ms: list):
    print(f"\n### {word_label}: D(m) table, m={m_min}..{m_max}, C_start={C_start} ###",
          flush=True)
    rows = []
    for m in range(m_min, m_max + 1):
        t_row0 = time.time()
        print(f"\n=== {word_label} m={m} ===", flush=True)
        D_val, shell_depth, margin, attempts = row_with_margin_rule(
            word_label, credit_fn, m, C_start)
        row_elapsed = time.time() - t_row0
        final_C = attempts[-1]["C"]
        rows.append({
            "m": m, "D": D_val, "C_final": final_C,
            "shell_depth": shell_depth, "margin": margin,
            "n_attempts": len(attempts), "row_wall_s": round(row_elapsed, 3),
        })
        print(f"    [{word_label}] m={m} FINAL: D={D_val} C={final_C} "
              f"shell_depth={shell_depth} margin={margin} row_wall={row_elapsed:.2f}s",
              flush=True)

    with open(out_csv, "w", newline="") as f:
        fieldnames = ["m", "D", "C_final", "shell_depth", "margin",
                      "n_attempts", "row_wall_s"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote {out_csv}", flush=True)

    print(f"\n--- {word_label}: steps-invariance spot check (steps=106) ---", flush=True)
    inv_results = []
    row_by_m = {r["m"]: r for r in rows}
    for m in invariance_check_ms:
        if m not in row_by_m or row_by_m[m]["D"] is None:
            continue
        C_use = row_by_m[m]["C_final"]
        D53 = row_by_m[m]["D"]
        t0 = time.time()
        D106, shell_depth106, margin106, _ = measure_row(credit_fn, C_use, m, steps=106)
        elapsed = time.time() - t0
        _toy_mod._PERM_CACHE.clear()
        match = (D106 == D53)
        print(f"    [{word_label}] m={m} C={C_use}: D(steps=53)={D53} D(steps=106)={D106} "
              f"{'MATCH' if match else '*** MISMATCH ***'} elapsed={elapsed:.2f}s", flush=True)
        inv_results.append({"m": m, "C": C_use, "D_53": D53, "D_106": D106, "match": match})
    return rows, inv_results


def main():
    t_start = time.time()
    here = Path(__file__).parent
    print("W6D-G -- G1/G3 measurement: golden-per8, sqrt2-per12 (m<=13), golden-tile8",
          flush=True)
    print(f"start: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

    print("\n=== Pre-measurement assertions (period + per-period support counts) ===",
          flush=True)
    for r in run_all_assertions():
        print(f"  {r}", flush=True)

    # --- G1: golden-per8, m=2..13 ---
    rows_g, inv_g = run_word_table(
        "golden-per8", credit_golden_per8, 2, 13, C_start=12,
        out_csv=here / "D_golden_per8_table.csv",
        invariance_check_ms=[6, 11],
    )

    # --- G1: sqrt2-per12, m=2..13 (heavy tail m=14..16 handled separately) ---
    rows_s, inv_s = run_word_table(
        "sqrt2-per12", credit_sqrt2_per12, 2, 13, C_start=12,
        out_csv=here / "D_sqrt2_per12_table.csv",
        invariance_check_ms=[6, 11],
    )

    # --- G3: golden-tile8, m=2..10 (contrast control) ---
    rows_t, inv_t = run_word_table(
        "golden-tile8", credit_golden_tile8, 2, 10, C_start=12,
        out_csv=here / "D_golden_tile8_table.csv",
        invariance_check_ms=[6, 9],
    )

    total_elapsed = time.time() - t_start
    print(f"\nTotal elapsed: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)", flush=True)
    print(f"end: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)


if __name__ == "__main__":
    main()
