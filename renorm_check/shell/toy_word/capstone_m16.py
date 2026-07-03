#!/usr/bin/env python3
"""
W6B CAPSTONE -- D_toy(16), per renorm_check/shell/W6B_TOY_WORD_ORDER.md's
successor capstone, registered in IMPLEMENTATION_LEDGER.md's "Verification
note (Fable)" appended to the W6B section, and in SYNTHESIS.md's W6B
section.

Registered predictions (frozen before this run, DO NOT alter):
  convergent-pinning hypothesis   ==> D_toy(16) = 6
  irrational law (Fable)          ==> D_toy(16) = 7

Protocol:
  1. CONTROLS FIRST at C=14: recompute D_toy(11) and D_toy(13) at C=14.
     Must equal the prior run's C=23 values (D_toy(11)=4, D_toy(13)=5,
     from D_toy_table.csv). Mismatch => STOP, do not run the m=16 row.
  2. THE ROW: D_toy(16) at C=14, 53 steps, golden credit word.
  3. Report D_toy(16) and the shell depth (max over d of (C-d) among
     states with r%3 != 0 that are DEAD after 53 steps) with its margin
     to the C=14 floor (C=14, so floor ceiling-distance is 14).

Definitions match toy_automaton.py / t3_measurement.py exactly:
  - credit_toy(k) = floor_kphi(k+1) - floor_kphi(k),
    floor_kphi(k) = (k + isqrt(5*k*k)) // 2  (exact integer, no floats).
  - D_toy(m) = min over d of (C-d) such that state (d, r=1) is live
    after 53 steps.

Memory design (hard 8GB ceiling, CPU only):
  m=16 => modulus = 3^16 = 43,046,721.
  C=14 => 15 deficit levels (d=0..14).
  Boolean occupancy: 15 * 43,046,721 bytes ~= 646MB per generation;
  current+next buffers ~= 1.3GB.
  Residue permutation arrays, int32 (values < 2^31), one per exponent
  a=1..16: ~172MB each, ~2.75GB for all 16 cached simultaneously.
  Total ~4.1GB steady-state, comfortably under 8GB with numpy/Python
  overhead. All permutations for exponents 1..16 are precomputed once
  and cached (not recomputed per step) since this fits in budget.

Progress logging: one line per step with step index, elapsed, total
live count, and RSS (via /proc/self/status), so a stall is visible
when tailing the log during a `run_in_background` run.
"""

from __future__ import annotations

import csv
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "embedding"))

import numpy as np
from automaton import allowed_exponents, mod_inverse

STEPS = 53
C_CAPSTONE = 14


def credit_toy(k: int) -> int:
    """Golden-ratio credit: c_k = floor((k+1)*phi) - floor(k*phi).
    Exact via floor(k*phi) = (k + isqrt(5*k^2)) // 2. No floats."""
    def floor_k_phi(kk: int) -> int:
        return (kk + math.isqrt(5 * kk * kk)) // 2
    return floor_k_phi(k + 1) - floor_k_phi(k)


def cross_check_credit_toy(n: int = 100_000) -> int:
    """Cross-check credit_toy against toy_automaton.py's own credit_toy for
    k=0..n. Required zero mismatches before any measurement."""
    from toy_automaton import credit_toy as credit_toy_reference
    mismatches = 0
    for k in range(n + 1):
        if credit_toy(k) != credit_toy_reference(k):
            mismatches += 1
    return mismatches


def get_rss_mb() -> float:
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    kb = int(line.split()[1])
                    return kb / 1024.0
    except Exception:
        pass
    return -1.0


def build_all_permutations(m: int, max_a: int) -> dict:
    """Precompute residue permutations for exponents a=1..max_a, cached in
    a plain dict (not the module-level _PERM_CACHE, so this script's memory
    footprint is explicit and self-contained)."""
    modulus = 3 ** m
    perms = {}
    for a in range(1, max_a + 1):
        r = np.arange(modulus, dtype=np.int64)
        inv2a = mod_inverse(pow(2, a, modulus), modulus)
        r_prime = ((3 * r + 1) % modulus) * inv2a % modulus
        perms[a] = r_prime.astype(np.int32)
        print(f"    precomputed permutation a={a} (RSS={get_rss_mb():.0f}MB)", flush=True)
    return perms


def run_capstone_heartbeat(C: int, m: int, steps: int = STEPS, log_prefix: str = ""):
    """Same mechanics as toy_automaton.run_heartbeat_generic (embedding/
    automaton.py's run_heartbeat, golden credits), but with permutations
    precomputed once for all needed exponents (max exponent reachable is
    C + max(credit) = C + 2), and with per-step progress logging
    (step index, total live count, RSS) for visibility during a long
    background run."""
    modulus = 3 ** m
    max_credit = 2  # golden credit_toy in {1, 2} same as true word (Beatty word, slope in (1,2))
    max_a = C + max_credit
    print(f"{log_prefix}building permutations for a=1..{max_a}, modulus=3^{m}={modulus}", flush=True)
    t_perm0 = time.time()
    perms = build_all_permutations(m, max_a)
    print(f"{log_prefix}permutations built in {time.time()-t_perm0:.1f}s, RSS={get_rss_mb():.0f}MB", flush=True)

    live_by_d = {d: np.ones(modulus, dtype=bool) for d in range(C + 1)}
    total0 = sum(int(arr.sum()) for arr in live_by_d.values())
    print(f"{log_prefix}step -1 (init): total_live={total0} RSS={get_rss_mb():.0f}MB", flush=True)

    t0 = time.time()
    for k in range(steps):
        c_k = credit_toy(k)
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
    """D_toy(m) = min over d of (C-d) such that (d, r=1) is live.
    Shell depth = max over d of (C-d) among states with r%3 != 0 that are
    DEAD (i.e. the deepest ceiling-distance at which a non-multiple-of-3
    residue is still dead -- the death-shell boundary)."""
    modulus = 3 ** m
    target_residue = 1 % modulus

    alive_depths = [C - d for d in range(C + 1) if live_by_d[d][target_residue]]
    D_toy_m = min(alive_depths) if alive_depths else None

    # Shell depth: max ceiling-distance (C-d) among (d,r) with r%3!=0 that
    # are dead. Scan from d=0 upward (largest C-d first) for efficiency;
    # first dead non-multiple-of-3 residue found gives the max.
    shell_depth = None
    for d in range(0, C + 1):  # d=0 => C-d=C is the largest ceiling-distance
        arr = live_by_d[d]
        # residues with r % 3 != 0
        # vectorized: find any dead index with r%3 != 0
        dead_mask = ~arr
        if not dead_mask.any():
            continue
        idx = np.nonzero(dead_mask)[0]
        nonmult3 = idx[idx % 3 != 0]
        if nonmult3.size > 0:
            shell_depth = C - d
            break
    return D_toy_m, shell_depth


def run_control(m: int, expected: int, C: int = C_CAPSTONE):
    print(f"\n=== CONTROL: D_toy({m}) at C={C} (expect {expected}, prior C=23 value) ===", flush=True)
    live_by_d = run_capstone_heartbeat(C, m, steps=STEPS, log_prefix=f"  [control m={m}] ")
    D_val, shell_depth = compute_D_and_shell_depth(live_by_d, C, m)
    print(f"  [control m={m}] D_toy({m})@C={C} = {D_val}  (expected {expected})  "
          f"shell_depth={shell_depth}", flush=True)
    del live_by_d
    return D_val


def main():
    t_start = time.time()
    print("W6B CAPSTONE -- D_toy(16) at C=14", flush=True)
    print(f"start time: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

    print("\n=== Pre-flight: credit_toy cross-check vs toy_automaton.py, k=0..100000 ===", flush=True)
    mismatches = cross_check_credit_toy(100_000)
    print(f"mismatches: {mismatches}", flush=True)
    if mismatches != 0:
        print("STOP: credit_toy cross-check FAILED. Aborting.", flush=True)
        sys.exit(1)
    print("credit_toy cross-check PASSED (0 mismatches, k=0..100000)", flush=True)

    # --- Controls ---
    d11 = run_control(11, expected=4)
    d13 = run_control(13, expected=5)

    control_pass = (d11 == 4) and (d13 == 5)
    print(f"\n=== CONTROL SUMMARY: D_toy(11)@C=14={d11} (expect 4), "
          f"D_toy(13)@C=14={d13} (expect 5) -- {'PASS' if control_pass else 'FAIL'} ===",
          flush=True)

    csv_rows = []
    csv_rows.append({"m": 11, "D_toy": d11, "role": "control", "expected": 4,
                      "C": C_CAPSTONE, "shell_depth": "", "floor_margin": ""})
    csv_rows.append({"m": 13, "D_toy": d13, "role": "control", "expected": 5,
                      "C": C_CAPSTONE, "shell_depth": "", "floor_margin": ""})

    if not control_pass:
        print("\nSTOP: controls FAILED. Corridor C=14 is floor-contaminated "
              "at this precision -- the capstone needs a wider corridor. "
              "NOT running the m=16 row.", flush=True)
        write_csv(csv_rows)
        print(f"\nTotal elapsed: {time.time()-t_start:.1f}s", flush=True)
        sys.exit(2)

    # --- The row: m=16 ---
    print(f"\n=== THE ROW: D_toy(16) at C={C_CAPSTONE} ===", flush=True)
    print("Registered predictions: convergent-pinning => 6; irrational (Fable) => 7", flush=True)
    live_by_d = run_capstone_heartbeat(C_CAPSTONE, 16, steps=STEPS, log_prefix="  [m=16] ")
    D16, shell_depth_16 = compute_D_and_shell_depth(live_by_d, C_CAPSTONE, 16)
    floor_margin = None
    if shell_depth_16 is not None:
        floor_margin = C_CAPSTONE - shell_depth_16
    print(f"\nD_toy(16) @ C={C_CAPSTONE} = {D16}", flush=True)
    print(f"shell depth (m=16) = {shell_depth_16}  (floor margin to C={C_CAPSTONE}: {floor_margin})", flush=True)

    if D16 == 6:
        verdict = "CONVERGENT-PINNING (6) -- matches convergent-pinning hypothesis"
    elif D16 == 7:
        verdict = "IRRATIONAL LAW (7) -- matches Fable's registered prediction"
    else:
        verdict = f"NEITHER 6 NOR 7 (got {D16}) -- offset model itself appears broken; report plainly"
    print(f"VERDICT: {verdict}", flush=True)

    csv_rows.append({"m": 16, "D_toy": D16, "role": "capstone",
                      "expected": "6(pinning)/7(irrational)",
                      "C": C_CAPSTONE, "shell_depth": shell_depth_16,
                      "floor_margin": floor_margin})
    write_csv(csv_rows)

    total_elapsed = time.time() - t_start
    print(f"\nTotal elapsed: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)", flush=True)
    print(f"end time: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)


def write_csv(rows):
    out_path = Path(__file__).parent / "capstone_m16.csv"
    fieldnames = ["m", "D_toy", "role", "expected", "C", "shell_depth", "floor_margin"]
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
