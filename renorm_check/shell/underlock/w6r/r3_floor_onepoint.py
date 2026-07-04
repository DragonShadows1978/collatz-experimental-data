#!/usr/bin/env python3
"""
W6R-R3 -- Floor-point + one-point structure, root-anchored.

Order text (frozen): "Recompute k* and the floor/one-point checks
(N1/N2 machinery) on root-anchored windows, m = 4..35 sampled + m = 29
mandatory. Frozen: floor law exceptionless AND the one-point (prefix-
congruence-alone) property holds at every m tested including 29..35
-- 55% (the shortcut may genuinely be small-m-only even in the right
frame; finding its true scope is the deliverable)."

Two checks per word, both root-anchored (root_anchored_word, i.e.
anchor_steps=m):

(A) FLOOR LAW (N1's object): at k* = argmax of the loop curve g_loop,
    does EVERY admissible chain satisfy g(k*) >= g_loop(k*)? Tested
    here as: TRUE MINIMUM over admissible length-k* prefixes (N2's
    `min_prefix_cost_and_argmin` branch-and-bound, congruence-only,
    margin-checked) >= g_loop(k*). This is the STRONGEST form (true
    min, not "no violation found within a slack band" as N1's DFS
    tested) -- appropriate since m up to 35 makes an L+3-budget full-
    chain enumeration (N1's own method) combinatorially infeasible at
    this length; N2's true-minimum-over-prefix method is exact and
    scales with k* (up to 35), not with the full chain space.

(B) ONE-POINT PROPERTY (N2's object): is that same true-minimum fact
    forced by the mod-3^k* congruence ALONE (i.e. IS the minimum
    itself, hence the floor claim already follows from (A) once (A)
    is computed via the congruence-only DFS -- no further completion
    check is needed to STATE the one-point property; the property is
    exactly "min over congruence-only length-k* prefixes equals (or
    exceeds) g_loop(k*)", which is precisely what (A)'s DFS computes).
    Following N2's own operationalization: this is checked directly,
    not via completion search (N2's own completion-search side-
    channel was to distinguish "prefix congruence forbids cheap
    prefixes entirely" from "cheap prefixes exist but die by suffix" -
    - a mechanism question, not a floor-value question; the ORDER's
    text for R3 asks specifically about the "floor/one-point CHECKS",
    i.e. does the floor hold and is it a one-point (congruence-only)
    fact -- both answered by the same DFS here, matching N2's own
    "congruence alone" operationalization verbatim).

m-sample: per the order's "m=4..35 sampled + m=29 mandatory" -- uses
a spread covering short (4-12), the historical ground-truth boundary
(13-28), and the breach zone (29-35), with m=29 always included.
"""
from __future__ import annotations

import csv
import sys
import time
import resource
from pathlib import Path

HERE = Path(__file__).parent
W6E = HERE.parent / "w6e"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(W6E))

from root_anchor import (  # noqa: E402
    root_anchored_word, loop_curve, credit_true,
    credit_golden_per8, credit_sqrt2_per12,
)
from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402

A_CAP = 40
A_CAP_WIDE = 80

M_SAMPLE = sorted(set(
    list(range(4, 13)) +           # short
    [13, 16, 20, 24, 28] +          # historical boundary zone
    list(range(29, 36))            # mandatory breach zone, 29..35
))


def rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)


def min_prefix_cost_and_argmin(letters_prefix, a_cap):
    """N2's own method (re-used, unmodified logic): true minimum
    max-partial-sum over ALL residue-admissible (parity-forced,
    congruence-only) exponent sequences of length k*=len(letters_prefix),
    branch-and-bound DFS, sound pruning (max_so_far monotone
    nondecreasing)."""
    k = len(letters_prefix)
    best = [None, None, None]  # cost, a_seq, rho_end

    def dfs(j, rho, running, max_so_far, a_seq):
        if best[0] is not None and max_so_far >= best[0]:
            return
        if j == k:
            if best[0] is None or max_so_far < best[0]:
                best[0], best[1], best[2] = max_so_far, tuple(a_seq), rho
            return
        c = letters_prefix[j]
        parity = forced_parity_for_backward_step(rho)
        if parity is None:
            return
        a_min = 2 if parity == 0 else 1
        for a in range(a_min, a_min + a_cap, 2):
            running2 = running + (a - c)
            rho2 = backward_predecessor_exact(rho, a)
            dfs(j + 1, rho2, running2, max(max_so_far, running2), a_seq + [a])

    dfs(0, 1, 0, 0, [])
    return best[0], best[1], best[2]


def independent_replay_prefix(letters_prefix, a_seq):
    """Fresh from-scratch replay of a prefix argmin witness."""
    rho = 1
    running = 0
    max_so_far = 0
    for c, a in zip(letters_prefix, a_seq):
        parity = forced_parity_for_backward_step(rho)
        assert parity is not None
        assert (a % 2 == 0) == (parity == 0)
        running += (a - c)
        max_so_far = max(max_so_far, running)
        rho = backward_predecessor_exact(rho, a)
    return max_so_far


def run_word(label, credit_fn, m):
    word = root_anchored_word(credit_fn, m)
    g_loop_curve, L, k_star_idx = loop_curve(word)
    k_star_1idx = k_star_idx + 1
    g_loop_at_kstar = g_loop_curve[k_star_idx]
    prefix = word[:k_star_1idx]

    min_cost, argmin_seq, argmin_rho = min_prefix_cost_and_argmin(prefix, A_CAP)
    min_cost_wide, _, _ = min_prefix_cost_and_argmin(prefix, A_CAP_WIDE)
    margin_ok = (min_cost == min_cost_wide)

    floor_holds = (min_cost >= g_loop_at_kstar)
    # "one-point property": the floor is exactly this congruence-only
    # minimum vs the loop value at k* -- report whether the minimum
    # EQUALS g_loop_at_kstar (tightest form: congruence alone pins the
    # exact floor value) vs merely >= (floor holds but congruence-only
    # min could in principle undershoot the loop and still not violate
    # if no completion exists -- N2's finer distinction; here we report
    # both the floor fact and whether it is tight).
    one_point_tight = (min_cost == g_loop_at_kstar)

    replay_val = independent_replay_prefix(prefix, argmin_seq)
    replay_ok = (replay_val == min_cost)

    return {
        "label": label, "m": m, "k_star_1idx": k_star_1idx, "L": L,
        "g_loop_at_kstar": g_loop_at_kstar,
        "min_prefix_cost_congruence_only": min_cost,
        "margin_ok": margin_ok,
        "floor_holds": floor_holds,
        "one_point_tight": one_point_tight,
        "replay_ok": replay_ok,
        "argmin_a_seq": ",".join(map(str, argmin_seq)),
    }


def main():
    t0 = time.time()
    print("=== W6R-R3: floor-point + one-point structure, root-anchored ===\n")
    print(f"m-sample: {M_SAMPLE}\n")

    rows = []
    n_floor_hold = 0
    n_onepoint_tight = 0
    n_total = 0
    honest_walls = []

    families = [
        ("true-word", credit_true),
        ("golden-per8", credit_golden_per8),
        ("sqrt2-per12", credit_sqrt2_per12),
    ]

    for label, credit_fn in families:
        print(f"--- {label} (root-anchored) ---")
        for m in M_SAMPLE:
            r = run_word(label, credit_fn, m)
            rows.append(r)
            n_total += 1
            n_floor_hold += r["floor_holds"]
            n_onepoint_tight += r["one_point_tight"]
            if not r["margin_ok"]:
                honest_walls.append((label, m, "margin_check_failed"))
            if not r["replay_ok"]:
                honest_walls.append((label, m, "replay_failed"))
            flag = "" if r["floor_holds"] else " *** FLOOR VIOLATION ***"
            print(f"  m={m:>3}: k*={r['k_star_1idx']:>3} L={r['L']:>3} "
                  f"g_loop(k*)={r['g_loop_at_kstar']:>3} "
                  f"min_prefix_cost={r['min_prefix_cost_congruence_only']:>3} "
                  f"floor_holds={r['floor_holds']} one_point_tight={r['one_point_tight']} "
                  f"margin={'OK' if r['margin_ok'] else 'FAIL'} "
                  f"replay={'PASS' if r['replay_ok'] else 'FAIL'}{flag}")
        print()

    print(f"Peak RSS: {rss_gb():.3f} GB; wall so far: {time.time()-t0:.1f}s\n")

    out = HERE / "r3_floor_onepoint_table.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote {out.name} ({len(rows)} rows)")

    print(f"\n=== FROZEN PREDICTION VERDICT ===")
    print(f"Floor law exceptionless AND one-point property holds at every m tested "
          f"including 29..35 -- 55% predicted\n")
    print(f"Floor law holds: {n_floor_hold}/{n_total}")
    print(f"One-point (tight, min==g_loop(k*)) holds: {n_onepoint_tight}/{n_total}")

    floor_verdict = "HIT" if n_floor_hold == n_total else f"MISS -- {n_total-n_floor_hold} violation(s)"
    onepoint_verdict = "HIT" if n_onepoint_tight == n_total else f"MISS -- {n_total-n_onepoint_tight} non-tight case(s)"
    print(f"Floor-law verdict: {floor_verdict}")
    print(f"One-point verdict: {onepoint_verdict}")

    # Specifically call out the mandatory m=29 row and the 29..35 zone
    print(f"\n--- m=29 mandatory + 29..35 zone detail ---")
    for r in rows:
        if 29 <= r["m"] <= 35:
            print(f"  {r['label']:12s} m={r['m']:>3}: floor_holds={r['floor_holds']} "
                  f"one_point_tight={r['one_point_tight']}")

    non_tight = [r for r in rows if not r["one_point_tight"]]
    if non_tight:
        print(f"\nNon-tight rows (min_prefix_cost != g_loop(k*)), detail:")
        for r in non_tight:
            print(f"  {r['label']} m={r['m']}: min={r['min_prefix_cost_congruence_only']} "
                  f"g_loop(k*)={r['g_loop_at_kstar']} "
                  f"diff={r['min_prefix_cost_congruence_only']-r['g_loop_at_kstar']}")

    if honest_walls:
        print(f"\nHonest walls: {honest_walls}")
    else:
        print(f"\nNo honest walls: every row's margin check passed and every witness replayed.")

    print(f"\nTotal wall: {time.time()-t0:.1f}s, peak RSS: {rss_gb():.3f} GB")


if __name__ == "__main__":
    main()
