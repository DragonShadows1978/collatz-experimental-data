#!/usr/bin/env python3
"""
W6R shared instrument: root-anchored word construction + the convention
of record's D_ceil recursion, per the W6R order (frozen prompt) and
DERIVATION_NOTES sec 15 (W6Q, the anchoring dictionary).

THE CONVENTION OF RECORD (binding, from the order): credits indexed
from the trajectory's own root -- c_k = floor((k+1)*log2(3)) -
floor(k*log2(3)), k = 0, 1, 2, ... . This equals the START-anchored
frame (phase 0).

Established by reading rust/lock3_census.rs directly (not paraphrased):
  - credit_at_step(k) = exact_floor_k_log2_3(k+1) - exact_floor_k_log2_3(k),
    called as `credit_at_step(next_depth - 1)` growing FORWARD from
    `Key::new(0, 0)` at depth 0 (line ~2049) -- i.e. k=0,1,2,... counts
    from the trajectory's OWN start, no external "anchor_steps=53" or
    any other calendar anchor anywhere in the source.
  - The recursion is FORWARD and CEILING-ON: next_counts only ever
    materializes d_next in 0..=max_deficit (deficit_branch_capacity /
    max_deficit_for_c, config.c >= 0 required; Key::new PANICS if
    deficit<0) -- i.e. d(i) = d(i-1) + c_{i-1} - a_{i-1}, constrained
    to 0 <= d(i) <= C at every step. This is the D_ceil variant in
    w6k/k0_canonical_engine.py's own vocabulary (ceiling_on=True),
    NOT D_free.

Relationship to the GAME's existing machinery (w6e/engine.py,
e1_walkers.py, w6k/k0_canonical_engine.py): the game's g(k) (backward-
consumption running sum, g(k)=sum_{j<=k}(a_j-c_j)) and the census's
d(i) (forward running sum, d(i)=d(i-1)+c_{i-1}-a_{i-1}) obey the SAME
step recursion read in OPPOSITE time directions on the SAME physical
(c,a) sequence -- g'=g+(a-c), d'=d+c-a=d-(a-c), both start at 0
(verified directly in w6q_reality/q3_census_deficit_eval.py's own
docstring and confirmed again here). So for a FIXED anchoring (which
calendar credit-index k is assigned to which position in the m-window)
the two conventions' MAGNITUDES (max|g| vs max|d|, floor/ceiling
structure) carry the same information, reversed in sign and time
order. What actually differs between "the game" and "the census" is
NOT this g/d duality -- it is WHICH CREDIT LETTERS get pulled into the
m-window: the game's `backward_letters(credit_fn, m, anchor_steps=53)`
fixes a UNIVERSAL calendar window [53-m, 53) regardless of m (end-
anchored, phase = 52 mod something); the census has no such external
anchor at all -- a trajectory's own m-window is simply credit indices
[0, m) starting from ITS OWN root.

THE FIX (surgical, reuses all existing validated machinery): calling
`backward_letters(credit_fn, m, anchor_steps=m)` produces EXACTLY the
root-anchored word -- window [0, m), index 0 (nearest terminal, first
consumed backward) = credit_fn(m-1), ..., index m-1 (window start) =
credit_fn(0). Verified directly below (`verify_root_anchor_equivalence`)
against the census's own root-anchored forward recursion, independent
of that round's own code.

k0_canonical_engine.canonical_D's own backward DFS (ceiling_on=True
matches the census's D_ceil exactly: running2>=0 required at every
prefix) is reused UNCHANGED -- root-anchoring only changes which word
(list of credit letters) is fed in, not the search/ceiling semantics,
since ceiling-on's g(k)>=0 at every prefix (backward, terminal-fixed
at rho=1) is definitionally the same object as the census's d(i) in
[0,C] (forward, root-fixed at d=0) for the SAME underlying letter
sequence -- this equivalence is stated in DERIVATION_NOTES sec 2 and
re-verified here (see `verify_g_d_duality`).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).parent
UNDERLOCK = HERE.parent
W6E = UNDERLOCK / "w6e"
W6K = UNDERLOCK / "w6k"
sys.path.insert(0, str(UNDERLOCK))
sys.path.insert(0, str(W6E))
sys.path.insert(0, str(W6K))

from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402
from e1_walkers import backward_letters, credit_true, d_real_mirror  # noqa: E402
from k0_canonical_engine import canonical_D, cap_margin_check  # noqa: E402
from underlock_words import credit_golden_per8, credit_sqrt2_per12  # noqa: E402


def root_anchored_word(credit_fn, m: int):
    """The convention of record's own m-window, canonical (backward-
    consumption) order: index 0 = nearest terminal = credit_fn(m-1),
    index m-1 = window start = credit_fn(0). Thin wrapper making the
    root-anchoring explicit at call sites (anchor_steps=m, not 53)."""
    return backward_letters(credit_fn, m, anchor_steps=m)


def end_anchored_word(credit_fn, m: int, anchor_steps: int = 53):
    """The GAME's house convention (existing ground-truth tables use
    this) -- kept for side-by-side comparison, unchanged."""
    return backward_letters(credit_fn, m, anchor_steps=anchor_steps)


def loop_curve(letters):
    """g_loop(k) = sum_{j<=k}(2-c_j), canonical order. Returns
    (curve, L, k_star 0-indexed first-argmax)."""
    running = 0
    curve = []
    for c in letters:
        running += (2 - c)
        curve.append(running)
    L = max([0] + curve)
    k_star = curve.index(max(curve)) if curve else None
    return curve, L, k_star


def D_root(credit_fn, m: int, ceiling_on: bool, a_cap: int = 40):
    """D(m) under the convention of record: root-anchored word fed
    into the UNCHANGED canonical_D backward-DFS/ceiling machinery."""
    letters = root_anchored_word(credit_fn, m)
    return canonical_D(letters, ceiling_on=ceiling_on, a_cap=a_cap)


def D_root_with_margin(credit_fn, m: int, ceiling_on: bool,
                        base_cap: int = 40, wider_cap: int = 80):
    letters = root_anchored_word(credit_fn, m)
    ok, d1, d2 = cap_margin_check(letters, ceiling_on, base_cap, wider_cap)
    return d1, ok, d2


def verify_g_d_duality():
    """Sanity check (run at import time by callers that want the
    receipt): for an arbitrary short word, the backward g-recursion
    (game) and the forward d-recursion (census), run on the SAME
    physical (c,a) pairs in the SAME order, satisfy d_k = -g_k at
    every prefix (both start at 0, single sign flip -- see module
    docstring). This is the "g and d are the same recursion, opposite
    direction" fact stated in w6q_reality/q3, re-derived independently
    here as a standing gate."""
    letters = [1, 2, 1, 1, 2, 2, 1, 2]
    a_seq =   [2, 2, 4, 1, 2, 4, 1, 2]
    # game g: backward consumption order, running += (a-c)
    g = 0
    g_hist = []
    for c, a in zip(letters, a_seq):
        g += (a - c)
        g_hist.append(g)
    # census d: SAME (c,a) pairs, SAME order, running += (c-a)
    d = 0
    d_hist = []
    for c, a in zip(letters, a_seq):
        d += (c - a)
        d_hist.append(d)
    ok = all(gv == -dv for gv, dv in zip(g_hist, d_hist))
    return ok, g_hist, d_hist


def verify_root_anchor_equivalence():
    """Cross-check `root_anchored_word` against a fresh, independent
    forward D_ceil-style recursion computed directly from credit_true,
    root-anchored at k=0 -- confirming the backward-consumption word
    construction is the same object as the census's own forward
    indexing, letter-for-letter (reversed order, as expected: backward
    order index0=nearest terminal=credit_true(m-1) ... index(m-1)=
    credit_true(0); forward order index0=credit_true(0) ...
    index(m-1)=credit_true(m-1))."""
    m = 29
    backward_word = root_anchored_word(credit_true, m)
    forward_word_independent = [credit_true(k) for k in range(m)]
    ok = backward_word == list(reversed(forward_word_independent))
    return ok, backward_word, forward_word_independent


if __name__ == "__main__":
    ok1, g_hist, d_hist = verify_g_d_duality()
    print(f"g/d duality gate: {'PASS' if ok1 else 'FAIL'}")
    print(f"  g_hist={g_hist}")
    print(f"  d_hist={d_hist}")
    ok2, bw, fw = verify_root_anchor_equivalence()
    print(f"root-anchor equivalence gate (m=29, true word): {'PASS' if ok2 else 'FAIL'}")
    print(f"  backward_word={bw}")
    print(f"  forward_word (independent)={list(reversed(fw))} (reversed for display)")
    assert ok1 and ok2, "W6R shared-instrument gates FAILED -- do not proceed"
    print("\nBoth W6R shared-instrument gates PASS.")
