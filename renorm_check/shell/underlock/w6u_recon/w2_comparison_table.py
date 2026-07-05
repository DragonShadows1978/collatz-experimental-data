#!/usr/bin/env python3
"""
W6U-RECON step 2 -- build the m=2..32 comparison table:
    m, D_recon(m), mirror-law-formula D_per(m), game-D root-anchored,
    game-D end-anchored

D_recon(m): computed via w1_census_port's DP. GATE 2 in w1 already
established this quantity is DEGENERATE (=0 for all m) under the
task's literal definition -- reported here for completeness/
transparency, not as a trustworthy column. See w1_output.log for the
full diagnosis.

mirror-law formula: D_per(m) = floor((22m-1)/53) -- the corridor's own
22/53 convention (w6r/root_anchor.py's d_real_mirror, cross-checked
directly against w6r/r1_root_break_table.csv's mirror_law_D_real
column for m=24..40, reproduced independently below).

game-D root-anchored: canonical_D(ceiling_on=True) on the ROOT-
anchored word (window [0,m) starting at the trajectory's own root),
i.e. exactly w6r/r1_root_break_table.csv's D_root_ceil column --
reused for m=24..40 (already computed, cross-checked against a fresh
independent re-derivation below) and extended for m=2..23 by direct
computation with the SAME validated instrument (w6k/k0_canonical_engine
.canonical_D), margin-checked.

game-D end-anchored: canonical_D(ceiling_on=True) on the END-anchored
word (window [53-m, 53), the game's universal house convention) --
this is the NATURAL generalization of w6r's L_end (which is only the
LOOP upper bound, not the full minimax); computed here directly with
canonical_D for completeness at every m, since r1's own L_end column
is a loop bound, not necessarily the true minimax (they are known to
coincide whenever universality D=L holds, which is the m<=28 regime,
but we compute the real quantity rather than reuse the loop proxy
uncritically, per house rules on trusting existing tools).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

HERE = Path(__file__).parent
UNDERLOCK = HERE.parent
W6E = UNDERLOCK / "w6e"
W6K = UNDERLOCK / "w6k"
W6R = UNDERLOCK / "w6r"
sys.path.insert(0, str(UNDERLOCK))
sys.path.insert(0, str(W6E))
sys.path.insert(0, str(W6K))

from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402
from k0_canonical_engine import canonical_D, cap_margin_check  # noqa: E402

sys.path.insert(0, str(HERE))
from w1_census_port import credit_at_step, D_recon_sweep  # noqa: E402


# ---------------------------------------------------------------------
# credit / word construction (independently re-derived here, not
# imported from w6r/e1_walkers, to keep this script's core numbers
# self-contained per house rules -- cross-checked against those
# modules' outputs below)
# ---------------------------------------------------------------------

def root_anchored_word(m: int):
    """Backward-consumption order, root-anchored: index 0 = nearest
    terminal = credit_at_step(m-1), index m-1 = credit_at_step(0)."""
    return [credit_at_step(m - 1 - j) for j in range(m)]


def end_anchored_word(m: int, anchor_steps: int = 53):
    """Backward-consumption order, end-anchored at a universal window
    [anchor_steps-m, anchor_steps)."""
    return [credit_at_step(anchor_steps - 1 - j) for j in range(m)]


def mirror_law_D_real(m: int) -> int:
    """D_real_mirror(m) = floor((22m-1)/53) -- w6r/e1_walkers.py's
    d_real_mirror, reproduced independently."""
    return (22 * m - 1) // 53


A_CAP_BASE = 40
A_CAP_WIDE = 80


def game_D(letters, a_cap=A_CAP_BASE, wide_cap=A_CAP_WIDE):
    """canonical_D(ceiling_on=True) with a margin check (base vs wide
    cap must agree, else the cap itself is the binding constraint --
    an honest wall to report, not silently ignored)."""
    d1 = canonical_D(letters, ceiling_on=True, a_cap=a_cap)
    d2 = canonical_D(letters, ceiling_on=True, a_cap=wide_cap)
    margin_ok = (d1 == d2)
    return d1, margin_ok


def independent_game_D_check(letters, a_cap=A_CAP_BASE):
    """A SECOND, independently-written DFS (different pruning /
    traversal shape) for cross-checking canonical_D's answer on a
    handful of cells, per house rules ("independently verify a
    handful by re-deriving")."""
    m = len(letters)
    best = [None]

    def dfs(j, rho, running, path_max):
        if best[0] is not None and path_max >= best[0]:
            return
        if j == m:
            best[0] = path_max if (best[0] is None or path_max < best[0]) else best[0]
            return
        c = letters[j]
        parity = forced_parity_for_backward_step(rho)
        if parity is None:
            return
        start_a = 1 if parity == 1 else 2
        a = start_a
        while a < start_a + a_cap:
            r2 = running + (a - c)
            if r2 >= 0:
                rho2 = backward_predecessor_exact(rho, a)
                dfs(j + 1, rho2, r2, max(path_max, r2))
            a += 2

    dfs(0, 1, 0, 0)
    return best[0]


def main():
    out_lines = []

    def p(s=""):
        print(s)
        out_lines.append(s)

    p("=== W6U-RECON W2: comparison table, m=2..32 ===\n")

    # Cross-check mirror-law formula against r1_root_break_table.csv directly.
    csv_path = W6R / "r1_root_break_table.csv"
    csv_rows = {}
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            csv_rows[int(row["m"])] = row

    p("[Cross-check] mirror_law_D_real from r1_root_break_table.csv vs independent formula:")
    mismatch = False
    for m, row in sorted(csv_rows.items()):
        mine = mirror_law_D_real(m)
        theirs = int(row["mirror_law_D_real"])
        if mine != theirs:
            mismatch = True
            p(f"  m={m}: MISMATCH mine={mine} csv={theirs}")
    p(f"  {'all rows match' if not mismatch else 'MISMATCHES FOUND'} (m={sorted(csv_rows)[0]}..{sorted(csv_rows)[-1]})")

    p("\n[Cross-check] D_root_ceil (game-D root-anchored) from CSV vs fresh canonical_D call, "
      "m=24..32 (overlap range):")
    root_mismatch = False
    for m in range(24, 33):
        letters = root_anchored_word(m)
        d1, margin_ok = game_D(letters)
        if m in csv_rows:
            theirs = int(csv_rows[m]["D_root_ceil"])
            if d1 != theirs:
                root_mismatch = True
                p(f"  m={m}: MISMATCH mine={d1} csv={theirs} (margin_ok={margin_ok})")
            else:
                p(f"  m={m}: MATCH (both {d1}, margin_ok={margin_ok})")
    p(f"  {'all overlap rows match' if not root_mismatch else 'MISMATCHES FOUND'}")

    # Build the full table m=2..32
    M_RANGE = list(range(2, 33))
    rows = []
    honest_walls = []

    for m in M_RANGE:
        d_recon = D_recon_sweep(m, C_max_search=60)  # degenerate (=0), reported for transparency

        mirror = mirror_law_D_real(m)

        root_word = root_anchored_word(m)
        d_root, margin_root_ok = game_D(root_word)
        if not margin_root_ok:
            honest_walls.append((m, "root_margin_fail"))
        d_root_indep = independent_game_D_check(root_word, a_cap=A_CAP_BASE)
        root_crosscheck_ok = (d_root == d_root_indep)
        if not root_crosscheck_ok:
            honest_walls.append((m, "root_independent_dfs_mismatch", d_root, d_root_indep))

        end_word = end_anchored_word(m, anchor_steps=53)
        d_end, margin_end_ok = game_D(end_word)
        if not margin_end_ok:
            honest_walls.append((m, "end_margin_fail"))
        d_end_indep = independent_game_D_check(end_word, a_cap=A_CAP_BASE)
        end_crosscheck_ok = (d_end == d_end_indep)
        if not end_crosscheck_ok:
            honest_walls.append((m, "end_independent_dfs_mismatch", d_end, d_end_indep))

        rows.append({
            "m": m,
            "D_recon": d_recon,
            "mirror_law_D_per": mirror,
            "game_D_root_anchored": d_root,
            "game_D_end_anchored": d_end,
            "root_margin_ok": margin_root_ok,
            "end_margin_ok": margin_end_ok,
            "root_indep_crosscheck_ok": root_crosscheck_ok,
            "end_indep_crosscheck_ok": end_crosscheck_ok,
        })

    p(f"\n{'m':>3} {'D_recon':>8} {'mirror_D_per':>13} {'game_D_root':>12} {'game_D_end':>11} {'root=mirror?':>13} {'end=mirror?':>12}")
    for r in rows:
        root_eq = (r["game_D_root_anchored"] == r["mirror_law_D_per"])
        end_eq = (r["game_D_end_anchored"] == r["mirror_law_D_per"])
        p(f"{r['m']:>3} {r['D_recon']:>8} {r['mirror_law_D_per']:>13} {r['game_D_root_anchored']:>12} "
          f"{r['game_D_end_anchored']:>11} {str(root_eq):>13} {str(end_eq):>12}")

    p(f"\nHonest walls: {honest_walls if honest_walls else 'none'}")

    out_csv = HERE / "w2_comparison_table.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    p(f"\nWrote {out_csv}")

    with open(HERE / "w2_output.log", "w") as f:
        f.write("\n".join(out_lines) + "\n")
    p(f"Wrote {HERE / 'w2_output.log'}")


if __name__ == "__main__":
    main()
