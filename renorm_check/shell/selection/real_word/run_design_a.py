#!/usr/bin/env python3
"""
Design A (W6C_SELECTION_ORDER.md): does the real word's aperiodicity bite?

A1: D(m) for m=2..13 at steps=53 (control, must match shell_probe P5 and
    true==periodicized by construction), steps=106, steps=159, for BOTH the
    true log2(3) Sturmian word (automaton.credit) and its 53-periodicized
    tiling (repeat credits c_0..c_52 cyclically).

A2: fixed m in {8, 10}, true word, steps swept 53..106 inclusive. Record D
    and the support-count (# of credit==1 letters) among the final m+1
    credits of the word up to that step count.

Exact arithmetic throughout (automaton.credit uses bit_length on Python
bigints -- no floats). int32 permutation arrays per the work order's
memory-guard instruction (values fit easily: modulus <= 3^13 < 2^31).
C=12 fixed per the work order; widen and rerun if floor margin < 2.

Usage: python3 run_design_a.py 2>&1 | tee run_design_a.log
"""

from __future__ import annotations

import itertools
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "embedding"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "toy_word"))

from automaton import credit as true_credit, mod_inverse, allowed_exponents  # noqa: E402

C_FIXED = 12
OUT_DIR = Path(__file__).resolve().parent
LOG_PATH = OUT_DIR / "progress_a.log"


def log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")


# ---------------------------------------------------------------------------
# Credit functions: true word vs 53-periodicized word.
# ---------------------------------------------------------------------------

_TRUE_TILE = tuple(true_credit(k) for k in range(53))  # c_0..c_52, exact


def credit_true(k: int) -> int:
    return true_credit(k)


def credit_periodic(k: int) -> int:
    return _TRUE_TILE[k % 53]


# ---------------------------------------------------------------------------
# Int32 vectorized heartbeat runner (own copy per work order: int32 arrays).
# ---------------------------------------------------------------------------

_PERM_CACHE: dict[tuple[int, int], np.ndarray] = {}


def _get_permutation(a: int, modulus: int) -> np.ndarray:
    key = (a, modulus)
    cached = _PERM_CACHE.get(key)
    if cached is not None:
        return cached
    r = np.arange(modulus, dtype=np.int64)
    inv2a = mod_inverse(pow(2, a, modulus), modulus)
    r_prime = ((3 * r + 1) % modulus) * inv2a % modulus
    perm = r_prime.astype(np.int32)
    _PERM_CACHE[key] = perm
    return perm


def run_heartbeat(C: int, m: int, credit_fn, steps: int,
                   max_states_guard: int = 400_000_000):
    """Returns (live_by_d: dict[int, np.ndarray[bool]], seq: tuple[int,...])."""
    modulus = 3 ** m
    total_states = (C + 1) * modulus
    if total_states > max_states_guard:
        raise ValueError(
            f"state space too large: C={C}, m={m}, modulus=3^{m}={modulus}, "
            f"total_states={total_states} > guard {max_states_guard}"
        )
    live_by_d = {d: np.ones(modulus, dtype=bool) for d in range(C + 1)}
    seq = tuple(credit_fn(k) for k in range(steps))
    for k in range(steps):
        c_k = seq[k]
        next_live_by_d = {d: np.zeros(modulus, dtype=bool) for d in range(C + 1)}
        for d in range(C + 1):
            src = live_by_d[d]
            live_r_indices = np.nonzero(src)[0].astype(np.int32)
            if live_r_indices.size == 0:
                continue
            for a in allowed_exponents(d, c_k, C):
                d_prime = d + c_k - a
                perm = _get_permutation(a, modulus)
                targets = perm[live_r_indices]
                next_live_by_d[d_prime][targets] = True
        live_by_d = next_live_by_d
    return live_by_d, seq


def D_readout(live_by_d: dict[int, np.ndarray], C: int, m: int):
    """D(m) = min ceiling-distance (C-d) of a live terminal (r=1 mod 3^m).
    Returns (D or None, shell_depth, margin) where shell_depth = C - d_min_live
    among ALL live d (not just terminal) is not needed here; per work order
    we report D itself and floor margin = d_live_min (distance of the
    shallowest live terminal's d from the floor d=0) -- i.e. margin to the
    corridor floor for the live terminal actually used for D.
    """
    modulus = 3 ** m
    target = 1 % modulus
    alive_d = [d for d in range(C + 1) if live_by_d[d][target]]
    if not alive_d:
        return None, None, None
    d_max = max(alive_d)  # shallowest ceiling-distance => largest d
    D = C - d_max
    margin = d_max  # distance from floor (d=0); this is what "rerun if <2" guards
    return D, D, margin


# ---------------------------------------------------------------------------
# Sanity check: steps=53 control.
# ---------------------------------------------------------------------------

SHELL_PROBE_P5 = {  # C=10 in shell_probe.py; m=2..12
    2: 0, 3: 1, 4: 1, 5: 2, 6: 2, 7: 2, 8: 3, 9: 3, 10: 4, 11: 4, 12: 4,
}


def sanity_check():
    log("=== SANITY CHECK: steps=53 control ===")
    log(f"Reproducing shell_probe P5 at C=10 for m=2..12 (must MATCH exactly)")
    all_ok = True
    for m in range(2, 13):
        live_by_d, _ = run_heartbeat(10, m, credit_true, steps=53)
        D, depth, margin = D_readout(live_by_d, 10, m)
        expected = SHELL_PROBE_P5[m]
        ok = D == expected
        all_ok &= ok
        log(f"  m={m:>2}: D_true(C=10,steps=53)={D} expected(P5)={expected} "
            f"{'MATCH' if ok else 'MISMATCH!!'}")
    if not all_ok:
        raise AssertionError("P5 reproduction FAILED -- bug in runner, stop")
    log("P5 reproduction: ALL MATCH.")

    log(f"Checking periodicized == true at steps=53, C={C_FIXED}, m=2..13 "
        f"(identical by construction; any difference is a bug)")
    all_ok = True
    for m in range(2, 14):
        live_true, _ = run_heartbeat(C_FIXED, m, credit_true, steps=53)
        live_periodic, _ = run_heartbeat(C_FIXED, m, credit_periodic, steps=53)
        D_t, _, marg_t = D_readout(live_true, C_FIXED, m)
        D_p, _, marg_p = D_readout(live_periodic, C_FIXED, m)
        # full state-array identity check, not just D
        identical_full = all(
            np.array_equal(live_true[d], live_periodic[d]) for d in range(C_FIXED + 1)
        )
        ok = identical_full and (D_t == D_p)
        all_ok &= ok
        log(f"  m={m:>2}: D_true={D_t} D_periodic={D_p} full_state_identical={identical_full} "
            f"margin_true={marg_t} margin_periodic={marg_p} {'MATCH' if ok else 'MISMATCH!!'}")
    if not all_ok:
        raise AssertionError("steps=53 true==periodicized sanity check FAILED -- bug, stop")
    log("steps=53 control: ALL MATCH (true == periodicized, as required by construction).")
    log("=== SANITY CHECK PASSED ===\n")


# ---------------------------------------------------------------------------
# A1
# ---------------------------------------------------------------------------

def run_A1():
    log("=== A1: true vs 53-periodicized word, m=2..13, steps=106 and 159 ===")
    rows = []
    for steps in (106, 159):
        for m in range(2, 14):
            t0 = time.time()
            live_true, _ = run_heartbeat(C_FIXED, m, credit_true, steps=steps)
            D_true, depth_true, margin_true = D_readout(live_true, C_FIXED, m)
            live_periodic, _ = run_heartbeat(C_FIXED, m, credit_periodic, steps=steps)
            D_periodic, depth_periodic, margin_periodic = D_readout(live_periodic, C_FIXED, m)
            equal = (D_true == D_periodic)
            dt = time.time() - t0
            row = dict(m=m, steps=steps, D_true=D_true, D_periodic=D_periodic,
                       equal=equal, margin_true=margin_true,
                       margin_periodic=margin_periodic, runtime_s=round(dt, 2))
            rows.append(row)
            flag = "" if equal else "  <<< DIFFERS !!!"
            low_margin = (margin_true is not None and margin_true < 2) or \
                         (margin_periodic is not None and margin_periodic < 2)
            margin_flag = "  [LOW MARGIN]" if low_margin else ""
            log(f"  steps={steps:>3} m={m:>2}: D_true={D_true} (margin {margin_true}) "
                f"D_periodic={D_periodic} (margin {margin_periodic}) "
                f"equal={equal} runtime={dt:.2f}s{flag}{margin_flag}")
            if not equal:
                log(f"    !!! RE-CHECKING row m={m} steps={steps} (differs -- rerun per protocol) !!!")
                live_true2, _ = run_heartbeat(C_FIXED, m, credit_true, steps=steps)
                D_true2, _, _ = D_readout(live_true2, C_FIXED, m)
                live_periodic2, _ = run_heartbeat(C_FIXED, m, credit_periodic, steps=steps)
                D_periodic2, _, _ = D_readout(live_periodic2, C_FIXED, m)
                log(f"    RERUN: D_true={D_true2} D_periodic={D_periodic2} "
                    f"(original: D_true={D_true} D_periodic={D_periodic}) "
                    f"reproducible={D_true2 == D_true and D_periodic2 == D_periodic}")
    log("=== A1 complete ===\n")
    return rows


# ---------------------------------------------------------------------------
# A2
# ---------------------------------------------------------------------------

def support_count_final_window(word_len: int, window: int) -> int:
    """Number of credit==1 letters among the final `window` letters of the
    true word of length `word_len` (i.e. credit_true(word_len-window) ..
    credit_true(word_len-1))."""
    start = max(0, word_len - window)
    return sum(1 for k in range(start, word_len) if credit_true(k) == 1)


def run_A2():
    log("=== A2: window slide, m in {8, 10}, true word, steps=53..106 ===")
    rows = []
    for m in (8, 10):
        window = m + 1
        for steps in range(53, 107):
            t0 = time.time()
            live_true, _ = run_heartbeat(C_FIXED, m, credit_true, steps=steps)
            D, depth, margin = D_readout(live_true, C_FIXED, m)
            support = support_count_final_window(steps, window)
            dt = time.time() - t0
            row = dict(m=m, steps=steps, D=D, support_count=support,
                       margin=margin, runtime_s=round(dt, 3))
            rows.append(row)
            margin_flag = "  [LOW MARGIN]" if (margin is not None and margin < 2) else ""
            log(f"  m={m:>2} steps={steps:>3}: D={D} support_count={support}/{window} "
                f"margin={margin} runtime={dt:.3f}s{margin_flag}")
    log("=== A2 complete ===\n")
    return rows


def main():
    LOG_PATH.write_text("")  # fresh progress log each run
    t_start = time.time()
    log(f"Design A run starting. C_FIXED={C_FIXED}")
    sanity_check()
    a1_rows = run_A1()
    a2_rows = run_A2()
    total_dt = time.time() - t_start
    log(f"TOTAL RUNTIME: {total_dt:.1f}s ({total_dt/60:.2f} min)")

    import json
    with open(OUT_DIR / "a1_results.json", "w") as f:
        json.dump(a1_rows, f, indent=2)
    with open(OUT_DIR / "a2_results.json", "w") as f:
        json.dump(a2_rows, f, indent=2)
    log(f"Wrote {OUT_DIR / 'a1_results.json'} and {OUT_DIR / 'a2_results.json'}")
    log("DONE.")


if __name__ == "__main__":
    main()
