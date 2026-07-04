#!/usr/bin/env python3
"""
W6S step 3 -- final reconciliation. Determines whether the game's
backward-terminal-anchored g(k) and the census's LITERAL (root-
anchored, forward, two-sided-ceiling) d(k) are the same mathematical
object under any anchoring correction, and whether the mismatch found
in s2 is specific to m=29 (which would explain why m=24..28 "agreed")
or a uniform structural fact (which would mean the m=24..28 agreement
was never actually a test of this same comparison).

Method: repeat the s2 comparison (game g, backward-consumption,
terminal-anchored vs census-literal d, forward, root-anchored) on the
KNOWN-OPTIMAL all-2s loop chain (W6R-R2's independently-verified
unique optimal chain for m<=28) at m=20..29, and report both
quantities' max/min side by side.
"""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).parent


def credit_true(k: int) -> int:
    def floor_klog2_3(kk: int) -> int:
        if kk == 0:
            return 0
        return (3 ** kk).bit_length() - 1
    return floor_klog2_3(k + 1) - floor_klog2_3(k)


def game_g_backward_terminal(a_backward, m):
    """The game's OWN formal definition (DERIVATION_NOTES sec 2):
    delta_k = delta_T - sum_{j<=k}(a_j - c_j), root-anchored LETTERS
    (credit indices 0..m-1) but walked BACKWARD from the TERMINAL
    (rho=1), i.e. g(k) = sum_{j<=k}(a_j-c_j) accumulated counting from
    the chain's END. This is what k0_canonical_engine.canonical_D and
    W6R's D_root both actually compute (DFS starts at rho=1, running=0,
    consumes letters index0=nearest-terminal=credit_true(m-1) first)."""
    letters_backward = [credit_true(m - 1 - j) for j in range(m)]
    running = 0
    g = [0]
    for c, a in zip(letters_backward, a_backward):
        running += (a - c)
        g.append(running)
    return g


def census_literal_d_forward_root(a_forward, m):
    """The census's LITERAL rule, read directly from rust/lock3_census.rs:
    - credit indexed k=0,1,2,... from the trajectory's OWN start
      (run_census line 2081 / run_census_lean line 2418:
      `let c = credit_at_step(next_depth - 1)`, root Key::new(0,0) at
      depth 0, lines 2049/2395).
    - d(i) = d(i-1) + c_{i-1} - a_{i-1}, i.e. the SAME (c,a) pairs as
      the game but walked FORWARD from depth 0 (the trajectory's own
      start), not backward from the terminal.
    - Hard two-sided ceiling: the growth loop's `for d_next in
      0..=max_deficit` (lines 2103/2467, max_deficit = config.c, the
      CLI --C capacity, required non-negative via `c.expect("--C is
      required")`, line 751) means a child state is materialized ONLY
      if the resulting d_next is in [0, config.c] AND a>=1 (lines
      2098-2100/2470-2472, `if a < 1 { continue; }`); `Key::new` itself
      (lines 268-273) panics on deficit<0. run_census_lean's own inline
      comments (lines ~2432-2436) name d_next>C explicitly a "breach
      upward" / exit event -- states outside [0,C] are NEVER part of
      the tracked tree going forward, in either direction."""
    d = 0
    dseq = [0]
    for i, a in enumerate(a_forward):
        c = credit_true(i)
        d += (c - a)
        dseq.append(d)
    return dseq


def main():
    out = []

    def p(s=""):
        print(s)
        out.append(s)

    p("=== W6S step 3: is the g(backward-terminal) vs d(forward-root) mismatch")
    p("    specific to m=29, or a uniform structural fact present at every m? ===\n")
    p("Test object: the all-2s loop chain (W6R-R2 independently confirmed unique")
    p("optimal chain for m<=28, 39/39 cells, 3-way independence gate PASS).\n")

    p(f"{'m':>3} {'max_g_backward_terminal':>24} {'L_root(=max_g,loop optimal)':>28} "
      f"{'max_d_census_literal':>21} {'min_d_census_literal':>21}")
    rows = []
    for m in range(20, 30):
        a_backward = [2] * m
        a_forward = list(reversed(a_backward))
        g = game_g_backward_terminal(a_backward, m)
        d = census_literal_d_forward_root(a_forward, m)
        row = {"m": m, "max_g": max(g), "max_d": max(d), "min_d": min(d)}
        rows.append(row)
        p(f"{m:>3} {max(g):>24} {max(g):>28} {max(d):>21} {min(d):>21}")

    p("\nObservation: max_d_census_literal stays at (or near) 0 across ALL of")
    p("m=20..29 -- it is NEVER close to the capacity ceiling on the positive")
    p("(upper) side at ANY m in this range, not just m=29. min_d goes")
    p("increasingly, uniformly negative as m grows (roughly -m/2), again with")
    p("no qualitative change at m=29 specifically.")
    p("\nThis means: the g(backward-terminal) vs d(forward-root) mismatch found")
    p("in s2 for the true-word m=29 witness is NOT a phenomenon that switches on")
    p("at m=29 -- it is present, in the same form and the same rough magnitude,")
    p("at every m tested (20..29), INCLUDING m=24..28 where the game's OWN")
    p("D_root(m) matched L_root(m) (W6R-R1's 'clean' rows). The m=24..28")
    p("'agreement' W6R found was agreement between D_root (game, backward-")
    p("terminal g) and L_root (the loop's own g, same backward-terminal")
    p("convention) -- an internal, same-convention comparison. It was NEVER a")
    p("comparison against the census's literal forward-root d at all. So there")
    p("is no 'inert for m=24..28, active at m=29' translation term to name:")
    p("the game-vs-census-literal mismatch is a permanent structural gap, not")
    p("an m=29-triggered one.")

    p("\n=== THE ACTUAL MECHANISM (named precisely) ===")
    p("The game's D(m) (DERIVATION_NOTES sec 2: 'delta_k = delta_T -")
    p("sum_{j<=k}(a_j-c_j)') is a MINIMAX OVER CHAINS THAT TERMINATE AT rho=1,")
    p("evaluated by walking BACKWARD from that fixed terminal -- it answers")
    p("'how much capacity must be banked in advance for an m-step chain ending")
    p("at 1 to never go bankrupt on the way down to the terminal.' This is an")
    p("END-boundary-value problem by construction (the terminal condition")
    p("rho=1 is what fixes rho at j=0 in the DFS).")
    p("")
    p("The census's literal deficit recursion (rust/lock3_census.rs, credit_at_step")
    p("called from run_census/run_census_lean's growth loop, lines 2080-2081 /")
    p("2417-2418, combined with the branch materialization rule at lines 2093-2103 /")
    p("2461-2472 and Key::new panic-on-negative at lines 268-273) is a")
    p("START-boundary-value problem: it grows a tree FORWARD from an arbitrary")
    p("root (Key::new(0,0), deficit=0, depth=0) with NO constraint that the")
    p("tree terminate at rho=1 after any particular number of steps -- 'reaching")
    p("valid1' (residue-compatible with terminal=1) is tracked as an emergent")
    p("event (valid1_shadow_birth_count / valid1_lineage_birth_count, wherever")
    p("in the tree it happens to occur), and M_edge(C) itself (the archived")
    p("comparator, max_valid1_lineage_lifetime, rust/lock3_census.rs lines")
    p("2632-2637) is defined as next_depth - birth_depth -- BIRTH-DEPTH")
    p("relative, i.e. anchored at whatever depth a lineage happens to become")
    p("valid1, not at depth 0 and not at the terminal.")
    p("")
    p("THREE DIFFERENT ANCHOR CONVENTIONS, THREE DIFFERENT QUANTITIES:")
    p("  1. Game's g:      backward-consumption, TERMINAL-anchored (rho=1 fixed")
    p("                    at DFS root, letters walked backward from there).")
    p("  2. Census's own d: forward, ROOT-anchored (depth=0, Key::new(0,0)")
    p("                    fixed at growth-loop start, letters walked forward).")
    p("  3. M_edge(C):     forward, BIRTH-anchored (lifetime relative to")
    p("                    whichever depth a lineage entered valid1 status).")
    p("W6Q found (1) vs (2) diverge (839 chain: g max=11, census-own d max=1,")
    p("min=-11). W6R's 'root-anchoring fix' changed WHICH CREDIT LETTERS are")
    p("pulled into the game's window (convention 1's own letters, re-selected")
    p("to start counting from k=0 instead of k=24) but did NOT change")
    p("convention 1 into convention 2 or 3 -- it is STILL a backward,")
    p("terminal-anchored quantity (D_root's own DFS still starts at rho=1).")
    p("This is why W6R's 'fix' relocated the break's NUMBERS (D_root=12 vs")
    p("L_root=13, rather than D_end=11 vs M_edge-implied L_end=12) but did not")
    p("make it vanish: it never touched the actual source of the mismatch,")
    p("which is (1)-vs-(2)/(3)'s boundary direction, not the calendar offset")
    p("within convention (1).")

    with open(HERE / "s3_output.log", "w") as f:
        f.write("\n".join(out) + "\n")
    with open(HERE / "s3_uniform_mismatch_table.json", "w") as f:
        json.dump(rows, f, indent=2)


if __name__ == "__main__":
    main()
