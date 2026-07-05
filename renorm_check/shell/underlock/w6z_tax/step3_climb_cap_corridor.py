#!/usr/bin/env python3
"""
W6Z-TAX Step 3 (corrected) -- per-heartbeat RESIDUE-LEGAL climb cap with
the deficit corridor RESTRICTED to [0, C], for C = 1..15.

WHY A REWRITE: the first Step-3 draft used a coarse (mod 3^1) forward DP.
That DECOUPLES parity from the true residue chain and collapses to the
RESIDUE-FREE (phase-relaxed) optimum -- it reproduced B1.1's +31 cap, NOT
B1.2's residue-legal -6 (Gate 2 FAILED, correctly caught). The residue
constraint is only enforced when residues are tracked EXACTLY along each
backward chain from a fixed launch class -- which is exactly what
b1/b2_residue_legal_max_climb.py does. This script REUSES that engine
(imports w6e/engine.py's forced_parity_for_backward_step and
backward_predecessor_exact, the same primitives b2 imports) and adds ONE
new axis: the deficit corridor is bounded to width C.

DEFICIT CORRIDOR SEMANTICS: along the backward chain the deficit partial
sum s_k = Sigma_{j<k}(c_j - a_j) must fit inside a window of width C, i.e.
range(s_0..s_k) <= C at all times -- the SAME [0,C] legality
sparse_instrument uses; here it gates a max-CLIMB objective.

OBJECTIVE: max over residue-legal, corridor-[0,C]-legal exponent chains of
Sigma(c - a) over the 53-letter heartbeat, best launch class mod 27 (18
live classes, b2's launch set). = climb_cap(C).

VALIDATION GATE: C -> large (corridor never binds) must reproduce B1.2's
-6. The b2 wall does NOT bite: one heartbeat is m=53, which b2 completed
EXACTLY (56.7s); the corridor prune only shrinks the search.
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
W6E = HERE.parent / "w6e"
sys.path.insert(0, str(W6E))
from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402

HEARTBEAT = 53
LAUNCH_CLASSES_MOD27 = [r for r in range(27) if r % 3 != 0]
LOG = HERE / "step3_climb_cap_corridor.log"
_loglines = []


def log(s=""):
    print(s, flush=True)
    _loglines.append(s)
    LOG.write_text("\n".join(_loglines) + "\n")


def floor_k_alpha(k: int) -> int:
    if k == 0:
        return 0
    return (3 ** k).bit_length() - 1


def credit_true(k: int) -> int:
    return floor_k_alpha(k + 1) - floor_k_alpha(k)


def backward_letters_window(k_end: int, m: int):
    return [credit_true(k_end - 1 - j) for j in range(m)]


def suffix_ub_table(letters):
    m = len(letters)
    tbl = [0] * (m + 1)
    for j in range(m - 1, -1, -1):
        tbl[j] = tbl[j + 1] + (letters[j] - 1)
    return tbl


def dfs_max_climb_corridor(letters, rho0, C, a_cap, time_budget,
                            node_check_interval=500_000):
    """b2's branch-and-bound DFS, exact big-int residues, PLUS the
    deficit-corridor prune: track (s, min_s, max_s), forbid any step
    making max_s - min_s > C. Objective: max Sigma(c-a)."""
    m = len(letters)
    ub_tbl = suffix_ub_table(letters)
    best = [None]
    t0 = time.time()
    nodes = [0]

    def rec(j, rho, running, s, mn, mx):
        nodes[0] += 1
        if nodes[0] % node_check_interval == 0 and time.time() - t0 > time_budget:
            raise TimeoutError()
        if best[0] is not None and running + ub_tbl[j] <= best[0]:
            return
        if j == m:
            if best[0] is None or running > best[0]:
                best[0] = running
            return
        c = letters[j]
        p = forced_parity_for_backward_step(rho)
        if p is None:
            return
        a_min = 2 if p == 0 else 1
        for a in range(a_min, a_min + a_cap + 1, 2):
            s2 = s + (c - a)
            mn2 = min(mn, s2)
            mx2 = max(mx, s2)
            if mx2 - mn2 > C:
                continue
            rho2 = backward_predecessor_exact(rho, a)
            rec(j + 1, rho2, running + (c - a), s2, mn2, mx2)

    try:
        rec(0, rho0, 0, 0, 0, 0)
        return best[0], nodes[0], False
    except TimeoutError:
        return best[0], nodes[0], True


def climb_cap(C, k_end=306, a_cap=4, time_budget=30):
    letters = backward_letters_window(k_end, HEARTBEAT)
    best = None
    best_launch = None
    walled = False
    for rho0 in LAUNCH_CLASSES_MOD27:
        val, nodes, td = dfs_max_climb_corridor(letters, rho0, C, a_cap, time_budget)
        walled |= td
        if val is not None and (best is None or val > best):
            best = val
            best_launch = rho0
    return best, best_launch, walled


def main():
    t0 = time.time()
    log("=== W6Z-TAX Step 3 (corrected): residue-legal climb cap, corridor [0,C] ===\n")

    log("--- Validation gate: C=200 (corridor never binds) must reproduce "
        "B1.2's -6 per heartbeat ---")
    cap200, launch200, walled200 = climb_cap(200, a_cap=4, time_budget=90)
    log(f"  C=200: climb_cap = {cap200} at launch {launch200} mod 27 (walled={walled200})")
    log(f"  B1.2 published (b2_run_output.log:12): -6 at launch class 20 mod 27")
    gate_ok = (cap200 == -6)
    log(f"  Gate: {'PASS' if gate_ok else '*** FAIL ***'}\n")
    if not gate_ok:
        log("  WARNING: gate did not reproduce -6 exactly -- reported honestly.\n")

    log("--- Climb cap per heartbeat under corridor [0,C], C=1..15 ---")
    log(f"  {'C':>3} {'climb_cap(C)':>12} {'best launch':>12} {'per-letter %':>13} {'walled':>7}")
    rows = []
    for C in range(1, 16):
        cap, launch, walled = climb_cap(C, a_cap=4, time_budget=40)
        per_letter = (100.0 * cap / HEARTBEAT) if cap is not None else float("nan")
        log(f"  {C:>3} {str(cap):>12} {str(launch):>12} {per_letter:>12.3f}% {str(walled):>7}")
        rows.append({"C": C, "climb_cap_corridor": cap, "best_launch_mod27": launch,
                     "per_letter_pct": round(per_letter, 4), "walled": walled})

    log(f"\n  (reference) width-unrestricted C=200: {cap200} at launch {launch200}")
    rows.append({"C": 200, "climb_cap_corridor": cap200, "best_launch_mod27": launch200,
                 "per_letter_pct": round(100.0 * cap200 / HEARTBEAT, 4), "walled": walled200})

    with open(HERE / "step3_climb_cap_corridor.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    log(f"\nWrote {HERE/'step3_climb_cap_corridor.csv'}")

    c15 = [r for r in rows if r["C"] <= 15]
    all_neg = all(r["climb_cap_corridor"] is not None and r["climb_cap_corridor"] < 0 for r in c15)
    log(f"\n=== Frozen prediction (c): climb cap strictly negative at every C (85%): "
        f"all C=1..15 negative? {all_neg} ===")
    log(f"  climb caps C=1..15: {[(r['C'], r['climb_cap_corridor']) for r in c15]}")
    vals = [r['climb_cap_corridor'] for r in c15 if r['climb_cap_corridor'] is not None]
    log(f"  min={min(vals)}  max={max(vals)}")

    log(f"\nTotal wall: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
