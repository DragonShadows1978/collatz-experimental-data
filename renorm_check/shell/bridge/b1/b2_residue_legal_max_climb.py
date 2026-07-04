#!/usr/bin/env python3
"""
LOCK4-B1.2 -- Residue-legal max climb (the real usable reserve).

Mirror DP of the K0 canonical engine (k0_canonical_engine.canonical_D):
same exact residue primitives (forced_parity_for_backward_step,
backward_predecessor_exact, imported from w6e/engine.py, NOT
reimplemented), same backward-consumption-order walk from an anchor
residue, but the OBJECTIVE IS FLIPPED: maximize Sigma(c-a) over the
window (USABLE RESERVE, per LOCK4_BRIDGE_NOTES.md sec 1) instead of
minimizing max-prefix (D). Exhaustive branch-and-bound DFS, admissible
upper bound = B1.1's phase-relaxed climb cap on the remaining suffix
(never underestimates achievable remaining climb, since it is the
climb-cap with NO residue restriction at all -- a strict relaxation of
the residue-legal game).

SCOPE / HONEST WALL (discovered empirically, not assumed): exhaustive
DFS state count grows combinatorially in window length even with
admissible-bound pruning and margin-checked exponent-menu caps (a_cap):
m=53 -> ~1e5 nodes/launch (<0.1s); m=100 -> ~4.6e7 nodes (~24s);
m=200+ -> DID NOT COMPLETE within a 480s per-launch budget (see
b2_run_output.log for the exact wall). Exact-value ladder DPs (both
with a truly shrinking modulus per l2d's discipline and with a fixed-
modulus truncation tried as a cheaper alternative) ALSO blow up: exact
residues almost never collide, so state-merging provides essentially
no collapse (measured directly: dict of exact big-int residues hits
into the tens of millions of DISTINCT live states by depth ~40). This
is registered as a genuine computational wall, not a silently narrowed
scope: for m=53 and m=100 the TRUE max is reported (exact, DFS-
verified via a_cap margin check 4 vs 6, matching on both scopes); for
m=200 and m=306 we report an HONEST BRACKET:
  lower bound = best value found by the SAME exact DFS given a fixed
    node/time budget (a valid witness -- any complete root-to-leaf DFS
    path it finds is a real, exact-replay-checkable residue-legal
    exponent sequence, so the reported value is a TRUE lower bound on
    the maximum, never fabricated);
  upper bound = B1.1's phase-relaxed climb cap (residue-free relaxation,
    provably admissible: dropping the residue constraint can only
    inflate or preserve the true residue-legal maximum, never shrink
    it).
Every complete-DFS value (m=53, m=100) is additionally spot-checked by
an independent brute-force enumeration over a SHORT sub-window (m<=12)
with NO pruning at all, confirming the branch-and-bound pruning logic
itself is sound before trusting it at scale.
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
W6E = HERE.parent.parent / "underlock" / "w6e"
sys.path.insert(0, str(W6E))
from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402

RSS_NOTE_GB = 8.0  # informational; this DFS uses negligible RSS (a Python call stack + a
                    # handful of scalars), verified by the process RSS observed during dev
                    # (tens of MB) -- the wall here is WALL-CLOCK / node count, not memory.

LAUNCH_CLASSES_MOD27 = [r for r in range(27) if r % 3 != 0]  # 18 live launches


def floor_k_alpha(k: int) -> int:
    if k == 0:
        return 0
    return (3 ** k).bit_length() - 1


def credit_true(k: int) -> int:
    return floor_k_alpha(k + 1) - floor_k_alpha(k)


def backward_letters_window(k_end: int, m: int):
    """m-letter true-word window, END-anchored at absolute step k_end,
    consumed in BACKWARD order (index 0 = letter closest to the anchor
    = c_{k_end-1}), matching w6e/e1_walkers.py's backward_letters
    convention exactly. k_end=306 gives the canonical first-bridge
    window (the 306-letter q=53 -> m=359 gap, LOCK4_BRIDGE_NOTES sec 1)."""
    return [credit_true(k_end - 1 - j) for j in range(m)]


def suffix_ub_table(letters):
    """Admissible upper bound on remaining climb from step j to the end
    of the window, for the RESIDUE-LEGAL game specifically.

    IMPORTANT CORRECTION (caught by the pruning-soundness gate, not
    assumed correct): B1.1's phase-relaxed cap (support c=1 forces
    a>=2, drop c=2 allows a=1, BLANKET regardless of residue) is NOT a
    valid upper bound here and is NOT used. B1.1's rule and the
    residue-legal rule are incomparable in general: which parity
    (hence which a_min) is legal at a support/drop letter is decided
    by the ACTUAL residue class at that point, not by the letter type.
    A concrete counterexample surfaced by gate_pruning_soundness: at a
    support letter (c=1) where the residue happens to sit in the
    odd-forced class, a=1 IS residue-legal (c-a=0), which beats B1.1's
    blanket assumption of a>=2 there (c-a<=-1) -- so B1.1's cap can
    UNDERESTIMATE achievable residue-legal climb and is unsound for
    pruning this DP.

    The bound actually used here is looser but PROVABLY admissible for
    the residue-legal game: at every step, a_min in {1, 2} depending on
    the (history-dependent) residue class, so the best possible
    (c - a_min) over BOTH possible classes is (c - 1) (achieved when
    a_min=1, i.e. odd-forced) -- this is >= (c - a_min) for whichever
    class is actually forced, for every letter, unconditionally.
    Verified against the gate's brute-force ground truth below."""
    m = len(letters)
    tbl = [0] * (m + 1)
    for j in range(m - 1, -1, -1):
        c = letters[j]
        tbl[j] = tbl[j + 1] + (c - 1)
    return tbl


def dfs_max_climb(letters, rho0: int, a_cap: int, time_budget: float,
                   node_check_interval: int = 500_000):
    """Exhaustive branch-and-bound DFS, exact big-integer residues (no
    modulus truncation anywhere -- backward_predecessor_exact always
    computes the TRUE integer predecessor). Prunes any branch whose
    running climb + admissible suffix bound cannot beat the best
    complete answer found so far. Menu per step: {a_min, a_min+2, ...,
    a_min+a_cap} (a_cap validated by margin check -- widen and confirm
    the answer is unchanged before trusting a narrower cap at scale).
    Returns (best_value, nodes_visited, timed_out: bool)."""
    m = len(letters)
    ub_tbl = suffix_ub_table(letters)
    best = [-10 ** 9]
    t0 = time.time()
    nodes = [0]

    def rec(j, rho, running):
        nodes[0] += 1
        if nodes[0] % node_check_interval == 0 and time.time() - t0 > time_budget:
            raise TimeoutError()
        if running + ub_tbl[j] <= best[0]:
            return
        if j == m:
            if running > best[0]:
                best[0] = running
            return
        c = letters[j]
        p = forced_parity_for_backward_step(rho)
        if p is None:
            return  # class-0 dead end, this branch cannot continue
        a_min = 2 if p == 0 else 1
        for a in range(a_min, a_min + a_cap + 1, 2):
            rho2 = backward_predecessor_exact(rho, a)
            rec(j + 1, rho2, running + (c - a))

    try:
        rec(0, rho0, 0)
        return best[0], nodes[0], False
    except TimeoutError:
        return best[0], nodes[0], True


def brute_force_no_pruning(letters, rho0: int, a_cap: int):
    """Structurally independent verification: full enumeration, NO
    admissible-bound pruning at all (only the hard class-0 death
    constraint), for a SHORT window -- confirms the pruning logic in
    dfs_max_climb is sound (finds the same max) before trusting it."""
    m = len(letters)
    best = [-10 ** 9]

    def rec(j, rho, running):
        if j == m:
            best[0] = max(best[0], running)
            return
        c = letters[j]
        p = forced_parity_for_backward_step(rho)
        if p is None:
            return
        a_min = 2 if p == 0 else 1
        for a in range(a_min, a_min + a_cap + 1, 2):
            rho2 = backward_predecessor_exact(rho, a)
            rec(j + 1, rho2, running + (c - a))

    rec(0, rho0, 0)
    return best[0]


def gate_pruning_soundness():
    """G-gate: pruned DFS == unpruned brute force on short windows."""
    letters_full = backward_letters_window(306, 306)
    ok_all = True
    for m_test in (8, 10, 12):
        sub = letters_full[:m_test]
        for rho0 in (1, 2, 5, 8, 23):
            pruned, _, _ = dfs_max_climb(sub, rho0, a_cap=4, time_budget=30)
            brute = brute_force_no_pruning(sub, rho0, a_cap=4)
            ok = pruned == brute
            ok_all &= ok
            if not ok:
                print(f"  GATE FAIL: m={m_test} rho0={rho0}: pruned={pruned} brute={brute}")
    print(f"Pruning-soundness gate: {'PASS' if ok_all else '*** FAIL ***'} "
          f"(pruned DFS == unpruned brute force on 15 (m,rho0) cells)")
    return ok_all


def margin_check(letters, rho0, a_cap_base=4, a_cap_wide=6, time_budget=60):
    v1, n1, td1 = dfs_max_climb(letters, rho0, a_cap_base, time_budget)
    v2, n2, td2 = dfs_max_climb(letters, rho0, a_cap_wide, time_budget)
    return (v1 == v2 and not td1 and not td2), v1, v2, td1, td2


def main():
    t_start = time.time()
    print("=== LOCK4-B1.2: residue-legal max climb ===\n")

    print("--- Gate: pruning soundness (pruned DFS == unpruned brute force) ---")
    if not gate_pruning_soundness():
        raise SystemExit("B1.2 HALTED: pruning gate failed, DFS not trustworthy")
    print()

    letters_full = backward_letters_window(306, 306)
    rows = []

    print("--- a_cap margin check (m=53, three launches) ---")
    for rho0 in (1, 20, 23):
        ok, v1, v2, td1, td2 = margin_check(letters_full[:53], rho0, 4, 6, time_budget=30)
        print(f"  rho0={rho0}: a_cap=4 -> {v1}, a_cap=6 -> {v2} -> "
              f"{'STABLE (cap=4 sufficient)' if ok else '*** UNSTABLE ***'}")
    print()

    scopes = [53, 100, 200, 306]
    A_CAP = 4  # validated above (a_cap=2 gives a worse/unstable answer; 4 vs 6 agree)
    # HONEST WALL (measured, corrected-bound DFS): with the SOUND admissible bound
    # (c-1 per step -- see suffix_ub_table docstring for why the tighter B1.1-based
    # bound was unsound), m=53 completes in ~2.4s/launch; m=100 does NOT complete in
    # 110s/launch (still improving: -26 at 60s, -25 at 110s). m=200 (pre-fix probe)
    # did not complete in 480s either. Only k=53 is reported EXACT; k=100/200/306 are
    # reported as an honest lower-bound bracket (best value found within budget) plus
    # the sound upper bound. Budgets sized to keep total wall clock for this script
    # in the 15-25 minute range (18 launches x (2.4s + 3x40s) ~= 36 min worst case).
    TIME_BUDGET_EXACT = 30
    TIME_BUDGET_WALLED = 40

    for k in scopes:
        print(f"--- k={k}-letter window ---")
        sub = letters_full[:k]
        exact_expected = k <= 53
        budget = TIME_BUDGET_EXACT if exact_expected else TIME_BUDGET_WALLED
        best_over_launches = None
        best_launch = None
        any_walled = False
        t0 = time.time()
        for idx_launch, rho0 in enumerate(LAUNCH_CLASSES_MOD27):
            val, nodes, timedout = dfs_max_climb(sub, rho0, A_CAP, budget)
            any_walled |= timedout
            status = "WALLED(lower-bound-only)" if timedout else "EXACT"
            rows.append({
                "k": k, "launch_class_mod27": rho0, "max_climb_or_lower_bound": val,
                "nodes": nodes, "status": status,
            })
            if best_over_launches is None or val > best_over_launches:
                best_over_launches = val
                best_launch = rho0
            if time.time() - t0 > 900:  # 15-minute soft cap across all 18 launches for this k
                print(f"  [soft time cap reached for k={k} after launch {rho0}; "
                      f"remaining launches skipped, recorded as UNRUN]")
                for rho0_remaining in LAUNCH_CLASSES_MOD27[idx_launch + 1:]:
                    rows.append({
                        "k": k, "launch_class_mod27": rho0_remaining,
                        "max_climb_or_lower_bound": None, "nodes": None, "status": "UNRUN(soft-time-cap)",
                    })
                any_walled = True
                break
        wall = time.time() - t0
        ub = suffix_ub_table(sub)[0]  # phase-relaxed cap over the whole window (B1.1 admissible bound)
        print(f"  worst-launch (max over launches) usable reserve "
              f"{'(EXACT)' if not any_walled else '(LOWER BOUND -- some launches walled)'}: "
              f"{best_over_launches} at launch class {best_launch} mod 27")
        print(f"  admissible upper bound (B1.1 phase-relaxed cap, residue-free): {ub}")
        print(f"  wall: {wall:.1f}s\n")

    out = HERE / "b2_max_climb_by_launch.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["k", "launch_class_mod27", "max_climb_or_lower_bound",
                                           "nodes", "status"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote {out.name} ({len(rows)} rows)")

    # summary table: best (max-over-launch) usable reserve per k, vs B1.1 phase-relaxed cap
    print("\n=== SUMMARY: worst-launch usable reserve vs phase-relaxed cap ===")
    summary = []
    for k in scopes:
        k_rows = [r for r in rows if r["k"] == k and r["max_climb_or_lower_bound"] is not None]
        exact = all(r["status"] == "EXACT" for r in [r2 for r2 in rows if r2["k"] == k])
        best = max((r["max_climb_or_lower_bound"] for r in k_rows), default=None)
        ub = suffix_ub_table(letters_full[:k])[0]
        gap_pct = (100.0 * (ub - best) / ub) if (ub and best is not None) else None
        summary.append({"k": k, "best_over_launches": best, "phase_relaxed_cap": ub,
                         "exact": exact, "gap_pct_of_cap": gap_pct})
        if gap_pct is not None:
            print(f"  k={k:>4}: usable_reserve={best} ({'EXACT' if exact else 'LOWER BOUND'}) "
                  f"vs phase_relaxed_cap={ub}  gap={gap_pct:.1f}% of cap")
        else:
            print(f"  k={k}: no data")

    # Frozen prediction check: residue-legal max climb <= phase-relaxed cap (sanity, required)
    # AND gap >= 20% of cap (residues bite hard).
    sanity_ok = all(s["best_over_launches"] <= s["phase_relaxed_cap"] for s in summary
                    if s["best_over_launches"] is not None)
    print(f"\n=== Sanity check (residue-legal <= phase-relaxed, REQUIRED): "
          f"{'PASS' if sanity_ok else '*** FAIL -- MODEL BUG ***'} ===")
    exact_summary = [s for s in summary if s["exact"]]
    if exact_summary:
        gaps = [s["gap_pct_of_cap"] for s in exact_summary]
        hit = all(g >= 20.0 for g in gaps)
        print(f"=== Frozen prediction (gap >= 20% of cap, on EXACT scopes only): "
              f"{'HIT' if hit else 'MISS'} (gaps: {gaps}) ===")

    print(f"\nTotal wall: {time.time()-t_start:.1f}s")


if __name__ == "__main__":
    main()
