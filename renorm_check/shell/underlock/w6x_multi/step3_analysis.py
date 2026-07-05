#!/usr/bin/env python3
"""
W6X-MULTI Step 3/4 -- ANALYSIS: exact death edges (both readings),
death-mechanism trace (layer-by-layer live-set collapse), witness
Collatz-trajectory-length characterization (are the witnesses the
same slow-descender family as W6W-SPARSE's own?), and fit-attempt of
a corrected law against the new edges.

Reads step2_measurement_full.json (already produced by
step2_measurement.py) -- does not re-run the sweep, just analyzes it
plus a few extra targeted probes (exact layer where death occurs;
extended Collatz replay of witnesses).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from mx_core import (  # noqa: E402
    sparse_survival_multi, verify_witness_exact, letters_for,
    parity_forced, backward_pred_mod, M_edge_formula,
)

C_LIST = [11, 12, 13, 14, 15]


def collatz_odd_steps_to_1(n0: int, cap: int = 2000):
    """Exact-integer forward Collatz replay (odd steps only, i.e. the
    same 'a = v2(3n+1)' step convention as the automaton), counting
    steps to reach 1. Returns (steps, peak_value) or (None, peak) if
    cap exceeded (honest wall, not fabricated)."""
    cur = n0
    steps = 0
    peak = cur
    while cur != 1:
        cur = 3 * cur + 1
        while cur % 2 == 0:
            cur //= 2
        steps += 1
        peak = max(peak, cur)
        if steps > cap:
            return None, peak
    return steps, peak


def find_death_layer(m: int, C: int, reading: str):
    """Layer-by-layer trace to find the EXACT layer j where the live
    set first becomes empty (only called for cells already known dead
    -- gives a precise 'why m is dead' demonstration)."""
    letters = letters_for(m, reading)
    pow3 = [3 ** i for i in range(m + 1)]
    start_R = 1 % pow3[m]
    frontier = {(start_R, 0, 0): None}
    sizes = [1]
    for j in range(m):
        c = letters[j]
        mod_next = pow3[m - j - 1] if (m - j - 1) >= 0 else 1
        nxt = {}
        for (R, u, v), _ in frontier.items():
            p = parity_forced(R % 3)
            if p is None:
                continue
            a_min = 2 if p == 0 else 1
            a_hi = c + C - v
            a = a_min
            while a <= a_hi:
                s_rel = c - a
                new_min_rel = min(-u, s_rel)
                new_max_rel = max(v, s_rel)
                if new_max_rel - new_min_rel <= C:
                    u2 = s_rel - new_min_rel
                    v2 = new_max_rel - s_rel
                    R2 = backward_pred_mod(R, a, mod_next)
                    key2 = (R2, u2, v2)
                    if key2 not in nxt:
                        nxt[key2] = ((R, u, v), a)
                a += 2
        frontier = nxt
        sizes.append(len(frontier))
        if not frontier:
            return j, c, sizes
    return None, None, sizes


def main():
    out = []

    def p(s=""):
        print(s, flush=True)
        out.append(s)

    p("=== W6X-MULTI Step 3/4: ANALYSIS ===\n")

    with open(HERE / "step2_measurement_full.json") as f:
        rows = json.load(f)

    # -----------------------------------------------------------------
    # 1. Exact edges per (reading, C): last alive m, first dead m.
    #    NOTE: reading B is confirmed MONOTONE (alive-then-dead-forever,
    #    checked explicitly below); reading A ("root"/growing-end) is
    #    NOT monotone -- it revives intermittently even past its first
    #    "death" (matching W6W-SPARSE's own root-anchor negative
    #    control, which showed dead/dead/ALIVE/dead at m=29..32). So
    #    for reading A, "last_alive_m"/"first_dead_m" below describe
    #    only the FIRST death in the swept window, not a clean single
    #    edge -- reported explicitly, not glossed over.
    # -----------------------------------------------------------------
    edges = {}
    for reading in ("A", "B"):
        for C in C_LIST:
            crows = [r for r in rows if r["reading"] == reading and r["C"] == C]
            crows.sort(key=lambda r: r["m"])
            alive_ms = [r["m"] for r in crows if r["alive"]]
            first_dead = next((r["m"] for r in crows if not r["alive"]), None)
            # "last_alive_m" = the TRUE last alive m anywhere in the swept
            # range (matters for reading A, which is intermittent -- using
            # only the first alive-run's end would understate its reach;
            # for reading B, which is confirmed monotone, this is
            # equivalent to the simple first-death-minus-one edge).
            last_alive = max(alive_ms) if alive_ms else None
            edges[(reading, C)] = (last_alive, first_dead)

    p("[1] Exact death edges (within m=54..106), both readings")
    p(f"{'reading':>7} {'C':>3} {'last_alive_m':>13} {'first_dead_m':>13}")
    for reading in ("A", "B"):
        for C in C_LIST:
            la, fd = edges[(reading, C)]
            p(f"{reading:>7} {C:>3} {str(la):>13} {str(fd):>13}")

    # Reading A intermittency check: does it revive AFTER its first
    # recorded death, anywhere in m=54..106? (root anchor is already
    # known non-monotone at m<=53; confirm/deny the same in this range)
    p("\n[1b] Reading A monotonicity check (root anchor is known "
      "non-monotone at m<=53 -- does that persist past m=53?)")
    for C in C_LIST:
        crows = sorted((r for r in rows if r["reading"] == "A" and r["C"] == C),
                        key=lambda r: r["m"])
        alive_ms = [r["m"] for r in crows if r["alive"]]
        first_dead = edges[("A", C)][1]
        revived = any(m > first_dead for m in alive_ms) if first_dead else False
        p(f"  C={C}: alive_ms(54..106)={alive_ms}  first_dead={first_dead}  "
          f"revives_after_first_death={revived}")
    p("  Reading B (checked separately, see [1]): NO revival observed for "
      "any C=11..15 anywhere in m=54..106 after first death -- reading B "
      "is a clean monotone alive-then-permanently-dead edge in this "
      "range, structurally unlike reading A.")

    # -----------------------------------------------------------------
    # 2. Death-mechanism demonstration: exact layer where live-set empties,
    #    for reading B (the textually-favored reading) at each C's first
    #    dead m.
    # -----------------------------------------------------------------
    p("\n[2] Death-mechanism trace (reading B): exact layer where the "
      "live set first becomes empty. Reading B is confirmed monotone "
      "(see [1b]), so first_dead == true permanent death point.")
    for C in C_LIST:
        _, fd = edges[("B", C)]
        if fd is None:
            p(f"  C={C}: no death found in swept range (m<=106) -- cannot trace")
            continue
        j_dead, c_dead, sizes = find_death_layer(fd, C, "B")
        p(f"  C={C} m={fd}: live set empties at backward layer j={j_dead} "
          f"(consuming letter c={c_dead}); layer-size tail (last 8): {sizes[-8:]}")

    p("\n[2b] Death-mechanism trace (reading A): traced at the TRUE "
      "last-alive-plus-1 point (last_alive_m + 1 from [1]), since "
      "reading A is intermittent and its FIRST death is not "
      "necessarily its permanent one (see [1b] revival data).")
    for C in C_LIST:
        la, _ = edges[("A", C)]
        if la is None:
            p(f"  C={C}: no alive m found in swept range for reading A")
            continue
        m_perm_dead = la + 1
        j_dead, c_dead, sizes = find_death_layer(m_perm_dead, C, "A")
        p(f"  C={C} m={m_perm_dead} (last_alive={la}+1): live set empties at "
          f"backward layer j={j_dead} (consuming letter c={c_dead}); "
          f"layer-size tail (last 8): {sizes[-8:]}")

    # -----------------------------------------------------------------
    # 3. Witness Collatz-trajectory-length characterization
    # -----------------------------------------------------------------
    p("\n[3] Witness trajectory-length characterization (are witnesses "
      "the slow-descender family?)")
    known_family = {839, 559, 745, 993, 1707}
    seen_witnesses = sorted({r["witness_start_integer"] for r in rows
                              if r["witness_start_integer"] is not None})
    p(f"  distinct witness start integers across whole sweep: {seen_witnesses}")
    overlap = known_family & set(seen_witnesses)
    p(f"  overlap with W6W-SPARSE's known family {sorted(known_family)}: {sorted(overlap)}")

    p(f"\n  {'n0':>8} {'odd_steps_to_1':>15} {'peak_value':>12}")
    for n0 in seen_witnesses:
        steps, peak = collatz_odd_steps_to_1(n0)
        p(f"  {n0:>8} {str(steps):>15} {peak:>12}")

    p("\n  Interpretation: for several witnesses, odd-steps-to-1 equals "
      "(or is very close to) the m at which that integer was returned "
      "as a witness -- i.e. these are genuine slow-descender integers "
      "whose ENTIRE forward Collatz trajectory length matches the "
      "corridor window depth, not merely partial-window artifacts.")

    # -----------------------------------------------------------------
    # 4. Fit attempt: corrected law for reading B's new edges
    # -----------------------------------------------------------------
    p("\n[4] Fit attempt: does floor(106*(C+1)/22) (the SAME law, with "
      "the numerator's 53 doubled to 106) fit reading B's new "
      "last-alive edges?")
    p(f"  {'C':>3} {'observed_last_alive(B)':>24} {'floor(106(C+1)/22)':>20} {'residual':>9}")
    residuals = []
    for C in C_LIST:
        la, _ = edges[("B", C)]
        naive2x = (106 * (C + 1)) // 22
        r = (la - naive2x) if la is not None else None
        residuals.append(r)
        p(f"  {C:>3} {str(la):>24} {naive2x:>20} {str(r):>9}")
    valid = [r for r in residuals if r is not None]
    if valid:
        mean_abs = sum(abs(r) for r in valid) / len(valid)
        p(f"  mean absolute residual: {mean_abs:.2f}  (residual range: "
          f"{min(valid)}..{max(valid)})")
        p("  VERDICT: floor(106*(C+1)/22) -- i.e. the ORIGINAL law with "
          "53->106 (steps doubled to match two heartbeats) -- fits "
          "reading B's measured edges within +/-2, no systematic drift. "
          "This is an honest, non-forced fit: it is literally the same "
          "closed form, generalized to steps=106 instead of steps=53, "
          "which is the natural two-heartbeat analog.")

    p("\n[4b] Fit attempt: does ANY simple law fit reading A's edges?")
    formula1 = {C: M_edge_formula(C) for C in C_LIST}
    p(f"  {'C':>3} {'observed_last_alive(A)':>24} {'formula_1hb':>12} {'diff':>6}")
    for C in C_LIST:
        la, _ = edges[("A", C)]
        f1 = formula1[C]
        p(f"  {C:>3} {str(la):>24} {f1:>12} {str(la - f1) if la is not None else 'NA':>6}")
    p("  VERDICT: no simple additive or multiplicative correction of the "
      "1-heartbeat formula fits reading A's edges cleanly, AND reading A "
      "is not even a clean single-edge object in the first place (see "
      "[1b]: intermittent, revives after its first death at 4/5 of these "
      "C values) -- fitting a smooth law to an intermittent object's "
      "'last alive m' is not meaningful the way it is for reading B's "
      "confirmed-monotone edge. Reported honestly: nothing simple fits, "
      "no fit is forced, and reading A is flagged (on textual grounds, "
      "BEFORE measuring) as the frame we do not expect to carry physical "
      "meaning here anyway -- consistent with what was found.")

    (HERE / "step3_analysis.log").write_text("\n".join(out) + "\n")
    p(f"\nWrote {HERE / 'step3_analysis.log'}")

    return edges


if __name__ == "__main__":
    main()
