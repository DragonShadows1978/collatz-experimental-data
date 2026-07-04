#!/usr/bin/env python3
"""
W6R-R1 -- Does the m=29 break vanish under the convention of record?

Order text (frozen): "Re-run the W6P full-window search (D with
ceiling variant matching the census's deficit recursion -- read the
census code and STATE which variant it implies, with the code line)
on root-anchored true-word windows m = 24..40. Compare to L_root(m)
(the loop's value on the root-anchored word) and to the corridor's
mirror-law values. Frozen (architect, from SYNTHESIS): universality
D = L holds at ALL m under root anchoring -- 70%."

CEILING VARIANT STATEMENT (binding, per the order): rust/lock3_census.rs
line 2081 (`let c = credit_at_step(next_depth - 1);`) inside the growth
loop at line 2080 (`for next_depth in (start_depth+1)..=config.depth`),
combined with `deficit_branch_capacity`/`max_deficit_for_c` (lines
1251-1265: `max_deficit_for_c` returns `None` for c<0, else `Some(c)`;
the growth loop at line 2108 only enumerates `d_next in 0..=max_deficit`)
and `Key::new` (lines 268-271: panics if `deficit < 0`) together
establish: the census's deficit is CEILING-ON in
w6k/k0_canonical_engine.py's vocabulary -- `canonical_D(..., ceiling_on
=True)`, i.e. g(k)>=0 required at every prefix k (equivalently the
census's own d(i) in [0,C] at every step, forward). This is the ONLY
variant used below, per this statement.

Root-anchoring per root_anchor.py: `root_anchored_word(credit_fn, m)`
= `backward_letters(credit_fn, m, anchor_steps=m)` -- window [0,m) in
the census's own indexing (verified against a fresh, independent
forward recursion in root_anchor.verify_root_anchor_equivalence and
r0_validation_gate.py Row B, both PASS).

D_root(m) computed via the UNCHANGED, already-validated
k0_canonical_engine.canonical_D branch-and-bound DFS (the same
instrument W6P-URGENT itself used for its from-scratch D_ceil search,
now fed the root-anchored word instead of the end-anchored one) --
margin-checked (A_CAP=40 vs 80) on every cell, per house rules.

Mirror-law comparator: D_real_mirror(m) = floor((22m-1)/53) (the
corridor's own 22/53 convention -- SYNTHESIS.md / e1_walkers.py
d_real_mirror), reported alongside for context. NOTE (stated plainly,
not glossed over): this mirror law is itself an END-anchored-window
derived quantity (fit to the same m<=28 ground-truth table the game's
end-anchored D matched) -- it is included here as the existing
corridor-side reference point the order asks to "compare to", not
re-derived root-anchored (no such re-derivation exists yet; that
would be new work beyond this order's scope).
"""
from __future__ import annotations

import csv
import sys
import time
import resource
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from root_anchor import (  # noqa: E402
    root_anchored_word, end_anchored_word, loop_curve, credit_true,
    canonical_D, cap_margin_check, d_real_mirror,
)

M_RANGE = list(range(24, 41))  # 24..40 inclusive
A_CAP_BASE = 40
A_CAP_WIDE = 80


def rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)


def independent_replay(letters, a_seq, ceiling_on):
    """Fresh from-scratch recomputation of the backward chain for a
    witness a_seq against a given letters list -- parity-legality and
    running g(k) (ceiling_on-respecting), structurally independent of
    canonical_D's own DFS bookkeeping."""
    sys.path.insert(0, str(HERE.parent / "w6e"))
    from engine import forced_parity_for_backward_step, backward_predecessor_exact
    rho = 1
    running = 0
    g_hist = []
    for c, a in zip(letters, a_seq):
        parity = forced_parity_for_backward_step(rho)
        if parity is None or (a % 2 == 0) != (parity == 0):
            return None, None
        running += (a - c)
        if ceiling_on and running < 0:
            return None, None
        rho = backward_predecessor_exact(rho, a)
        g_hist.append(running)
    return max(g_hist) if g_hist else 0, g_hist


def find_witness(letters, ceiling_on, a_cap, target_D):
    """Recover ONE admissible a-sequence achieving canonical_D's
    reported minimum (for exact-replay), via the same DFS shape,
    stopping at first chain matching target_D exactly."""
    sys.path.insert(0, str(HERE.parent / "w6e"))
    from engine import forced_parity_for_backward_step, backward_predecessor_exact
    m = len(letters)
    found = [None]

    def dfs(j, rho, running, max_so_far, a_seq):
        if found[0] is not None:
            return
        if max_so_far > target_D:
            return
        if j == m:
            if max_so_far == target_D:
                found[0] = list(a_seq)
            return
        c = letters[j]
        parity = forced_parity_for_backward_step(rho)
        if parity is None:
            return
        a_min = 2 if parity == 0 else 1
        for a in range(a_min, a_min + a_cap, 2):
            running2 = running + (a - c)
            if ceiling_on and running2 < 0:
                continue
            rho2 = backward_predecessor_exact(rho, a)
            max2 = max(max_so_far, running2)
            if max2 > target_D:
                continue
            dfs(j + 1, rho2, running2, max2, a_seq + [a])
            if found[0] is not None:
                return

    dfs(0, 1, 0, 0, [])
    return found[0]


def main():
    t0 = time.time()
    print("=== W6R-R1: does the m=29 break vanish under root anchoring? ===\n")
    print("Ceiling variant (stated, per order): D_ceil, i.e. canonical_D(ceiling_on=True)")
    print("  -- matches rust/lock3_census.rs's deficit_branch_capacity/max_deficit_for_c")
    print("     (lines 1251-1265, d_next in 0..=max_deficit, c>=0 required) and Key::new's")
    print("     panic-on-negative-deficit (lines 268-271), fed by the root-anchored")
    print("     forward growth loop (line 2080-2081: credit_at_step(next_depth-1),")
    print("     next_depth counting from the trajectory's OWN root at depth 0, line 2049).\n")

    rows = []
    n_hit_universality = 0
    n_total = 0
    honest_walls = []

    for m in M_RANGE:
        root_word = root_anchored_word(credit_true, m)
        end_word = end_anchored_word(credit_true, m, anchor_steps=53)
        _, L_root, kstar_root = loop_curve(root_word)
        _, L_end, kstar_end = loop_curve(end_word)
        mirror = d_real_mirror(m)

        D_root_val = canonical_D(root_word, ceiling_on=True, a_cap=A_CAP_BASE)
        margin_ok, d1, d2 = cap_margin_check(root_word, ceiling_on=True,
                                              base_cap=A_CAP_BASE, wider_cap=A_CAP_WIDE)
        if not margin_ok:
            honest_walls.append((m, "margin_fail", d1, d2))

        matches_L_root = (D_root_val == L_root)
        n_total += 1
        n_hit_universality += matches_L_root

        # Witness + independent replay for every cell (small m range,
        # cheap to do universally rather than only on a match/mismatch
        # subset -- house rule: exact witnesses, replays, the table).
        witness = find_witness(root_word, True, A_CAP_BASE, D_root_val)
        replay_max, replay_ghist = (None, None)
        replay_ok = None
        if witness is not None:
            replay_max, replay_ghist = independent_replay(root_word, witness, True)
            replay_ok = (replay_max == D_root_val)
        else:
            honest_walls.append((m, "no_witness_recovered", D_root_val, None))

        rows.append({
            "m": m,
            "D_root_ceil": D_root_val,
            "L_root": L_root,
            "kstar_root_1idx": kstar_root + 1 if kstar_root is not None else None,
            "matches_L_root": matches_L_root,
            "L_end": L_end,
            "mirror_law_D_real": mirror,
            "margin_check_ok": margin_ok,
            "witness_a_seq": ",".join(map(str, witness)) if witness else "",
            "replay_ok": replay_ok,
        })

        print(f"  m={m:>3}: D_root(ceil)={D_root_val:>3} L_root={L_root:>3} "
              f"[{'MATCH' if matches_L_root else 'MISS'}] "
              f"L_end={L_end:>3} mirror(end)={mirror:>3} "
              f"margin={'OK' if margin_ok else 'FAIL'} "
              f"replay={'PASS' if replay_ok else ('N/A' if replay_ok is None else 'FAIL')}")

    print(f"\nPeak RSS: {rss_gb():.3f} GB; wall so far: {time.time()-t0:.1f}s\n")

    out = HERE / "r1_root_break_table.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote {out.name} ({len(rows)} rows)")

    n_replay_fail = sum(1 for r in rows if r["replay_ok"] is False)
    n_no_witness = sum(1 for r in rows if r["witness_a_seq"] == "")

    print(f"\n=== FROZEN PREDICTION VERDICT ===")
    print(f"Universality D_root = L_root holds at ALL m under root anchoring -- 70% predicted\n")
    print(f"{n_hit_universality}/{n_total} cells match (D_root == L_root)")
    verdict = "HIT" if n_hit_universality == n_total else f"MISS -- {n_total-n_hit_universality} breach(es)"
    print(f"Verdict: {verdict}")
    if n_replay_fail:
        print(f"*** {n_replay_fail} WITNESS REPLAYS FAILED -- investigate before trusting ***")
    if n_no_witness:
        print(f"*** {n_no_witness} cells had NO witness recovered (see honest_walls) ***")
    if honest_walls:
        print(f"\nHonest walls: {honest_walls}")
    else:
        print(f"\nNo honest walls: every cell's margin check passed and a witness was "
              f"recovered and independently replayed.")

    print(f"\nTotal wall: {time.time()-t0:.1f}s, peak RSS: {rss_gb():.3f} GB")


if __name__ == "__main__":
    main()
