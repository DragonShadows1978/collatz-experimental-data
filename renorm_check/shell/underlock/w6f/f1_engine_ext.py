#!/usr/bin/env python3
"""
W6F-F1 engine extension -- exhaustive optimal-set enumeration.

REUSES w6e/engine.py's primitives (allowed_exponents, next_residue,
mod_inverse) and mechanics UNCHANGED. Extends the single-chain
`bfs_Dm(want_chain=True)` (which returns only ONE optimal chain, via
first-parent-wins BFS) to enumerate the FULL set of distinct optimal
a-sequences achieving D(m) exactly.

--- Why bfs_Dm alone is insufficient for F1 ---
engine.bfs_Dm's forward BFS stores `new_live[key] = ((d,r), a) if
key not in new_live` -- i.e. exactly ONE parent per (d,r) state (the
first one found). This is correct and sufficient for computing D(m)
and for the E1/E3 "one representative chain" experiments, but it
structurally CANNOT recover the number or shape of all optimal chains:
that information (the other parents) is discarded at the `if key not
in new_live` line.

--- The extension: state space and exhaustiveness argument ---
The engine's own state space, established in engine.py's module
docstring and validated in W6E, is `(d, r)` with d in [0,C] (ceiling-
distance budget) and r in Z/3^m (residue, exact -- no lift truncation,
since the m-step window is exactly the residue-relevant range per the
trit-locality argument in DERIVATION_NOTES sec 1). This IS the complete
state: `d` is all `allowed_exponents` needs, and `r mod 3^m` is all the
terminal constraint `r_final == 1 mod 3^m` needs. The forward
transition `(d,r) --a--> (d+c-a, next_residue(r,a,mod))` is
deterministic given the (phase-fixed) credit letter c and the chosen
exponent a. Therefore the set of ALL (d,r) states reachable at step k
from an exhaustively-populated step-0 set, and ALL admissible
transitions between them, is exactly the full state graph -- nothing
outside `d in [0,C], r in [0,3^m)` is reachable or relevant, and
nothing inside it is omitted, because the forward-population step
(`bfs_Dm_fast`'s own boolean-array method, reused verbatim below via
the SAME `allowed_exponents` + `_get_permutation` calls used in
engine.bfs_Dm_fast) evaluates every legal `a` from every live `(d,r)`
at every step. Recording every (d,r)->(d',r') edge (not just the first
into each (d',r'), as bfs_Dm does) makes the resulting graph a COMPLETE
representation of every admissible chain in the engine's own state
space -- this is the state-space argument for exhaustiveness the order
requires.

--- Avoiding the combinatorial residue-fanout trap ---
A naive "track all parents forward, then backtrack all paths" (tested
during development) produces the CORRECT count of *residue-tagged*
paths, but that count is NOT the deliverable (F1 wants distinct optimal
a-sequences, i.e. distinct exponent processes) and it blows up as
O(3^m) raw paths even when there is only 1 distinct a-sequence at
optimum (verified: at m=9 golden, 19683 = 3^9 raw parent-paths all
carrying the SAME a-sequence, one per surviving starting residue r0 --
confirmed by direct enumeration during development, not asserted
without checking). It also requires storing a full parents dict for
EVERY (d,r) pair at every step (memory blew past several GB and was
killed at m=10-11 during development), most of which are never used in
any backward path to the terminal.

FIX (implemented below): (1) run the forward pass with the SAME
boolean live-array method as engine.bfs_Dm_fast (fast, low memory,
storing only which (d,r) are live at each step -- no parent lists);
(2) enumerate distinct a-SEQUENCES by a backward-only, memoized
recursion from the terminal state, computing predecessors ON DEMAND
via the explicit modular inverse of the (non-bijective, since 3 is a
zero divisor mod 3^m) forward residue map, restricted to predecessors
that were actually live (per the step-1 boolean array). Memoization
key is (step, d, r) and only nodes on some backward path from the
terminal are ever visited or memoized -- this is what avoids both the
memory blowup and the raw-path combinatorial explosion, while remaining
exhaustive: every legal backward predecessor consistent with the
recorded live-sets is explored, none skipped.

--- Validation (house rule: 3 ground-truth rows minimum before trust) ---
Cross-checked against a THIRD, fully independent implementation
(`brute_force_all_chains` below: naive scalar recursive DFS over every
starting residue r0 in [0, 3^m), collecting every chain landing on
r=1 mod 3^m, taking the max final depth) on golden-per8 AND sqrt2-per12,
m=3,4,5 (6 rows total, 3x the required minimum, both families) --- D
matches ground truth on all 6, and the SET of distinct optimal
a-sequences matches exactly (not just the count) on all 6. See
`f1_validate.py` for the standalone validation script and its log.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "w6e"))
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np

from engine import allowed_exponents, next_residue, _get_permutation


def forward_live_fast(credit_fn, m: int, C: int, anchor_steps: int = 53):
    """Boolean live-array forward pass, IDENTICAL mechanics to
    engine.bfs_Dm_fast (same allowed_exponents/_get_permutation calls),
    but keeping the full per-step history (bfs_Dm_fast discards it,
    since it only needs the final layer for a D-only readout)."""
    modulus = 3 ** m
    phase = anchor_steps - m
    live_by_d = {d: np.ones(modulus, dtype=bool) for d in range(C + 1)}
    history = [live_by_d]
    letters = []
    for k in range(m):
        c = credit_fn(phase + k)
        letters.append(c)
        next_live = {d: np.zeros(modulus, dtype=bool) for d in range(C + 1)}
        for d in range(C + 1):
            src = live_by_d[d]
            if not src.any():
                continue
            idx = np.nonzero(src)[0]
            for a in allowed_exponents(d, c, C):
                d2 = d + c - a
                perm = _get_permutation(a, modulus)
                next_live[d2][perm[idx]] = True
        live_by_d = next_live
        history.append(live_by_d)
    return letters, history


def backward_predecessors_of_r(r_target: int, a: int, modulus: int):
    """All r with next_residue(r, a, modulus) == r_target.
    next_residue(r,a,mod) = (3r+1)*inv(2^a) mod mod, so
    3r+1 == r_target*2^a (mod mod)  =>  3r == r_target*2^a - 1 (mod mod).
    Since gcd(3, modulus=3^m) = 3 (m>=1), this is solvable (with exactly
    3 solutions mod modulus) iff 3 | (r_target*2^a - 1); else no
    solution exists (the map is 3-to-1 onto its image, NOT a bijection
    -- verified directly during development: e.g. m=4 the image of
    next_residue over all r has only 27 of 81 possible values)."""
    val = (r_target * pow(2, a, modulus) - 1) % modulus
    if val % 3 != 0:
        return []
    base = val // 3
    step = modulus // 3
    return [(base + i * step) % modulus for i in range(3)]


def distinct_optimal_a_sequences(letters, history, m: int, C: int,
                                  modulus: int, terminal_d: int,
                                  target_r: int = 1):
    """Memoized backward DFS from the terminal (terminal_d, target_r)
    at step m, back to step 0. Returns the frozenset of ALL distinct
    admissible a-sequences (tuples, forward order) whose forward chain
    starts EXACTLY at d0=C (the engine's validated window-start
    convention, ceiling-distance 0 -- see engine.py's module docstring:
    "the window START sits at ceiling-distance 0") at SOME live starting
    residue, and ends exactly at (terminal_d, target_r) at step m.

    BUG FOUND AND FIXED during F2 development (recorded here, not
    silently patched): `forward_live_fast`'s step-0 layer pools EVERY
    starting depth d0 in [0,C] as live (matching engine.bfs_Dm_fast's
    own convention, which is fine for computing D(m) alone since the
    max-over-survivors selection automatically favors the d0=C start).
    But an off-optimum query (terminal_d < best_d, as F2 needs for the
    D+1/D+2 tax buckets) is NOT automatically restricted to d0=C by
    that same max-selection logic -- e.g. golden m=2: the all-2s chain
    (2,2) starting at d0=C=12 reaches d=12 (its ONLY true terminal
    depth for that fixed a-sequence, since depth given a fixed
    a-sequence and fixed credit word is a deterministic path
    independent of residue); but the SAME a-sequence (2,2) ALSO
    appears as a "valid" backward reconstruction ending at d=11 if
    step-0 is allowed to start at d0=11 instead of 12 (11+2-2=11,
    trivially live since step-0 pools all depths) -- this is a
    DIFFERENT (shorter-budget) chain that only coincides in its
    a-sequence, not the tax-relevant object. Caught by
    f2_deviation_tax.py's own cross-check (each returned chain's
    max-partial-sum, computed independently from its a-sequence and
    the credit word, must equal C - terminal_d exactly) -- it does NOT
    for d0 != C starts, which is what surfaced this. FIX: pin step 0
    to d==C exactly (single required starting depth), matching
    brute_force_all_chains's own dfs(0, C, r0, []) convention (which is
    what f1_validate.py actually cross-checked against -- the bug was
    latent in f1_engine_ext's production path even though validation
    passed, because F1's validation only ever queried terminal_d ==
    best_d, where the d0=C restriction happens to be automatically
    satisfied by construction: only d0=C can reach the GLOBAL max
    survivor depth, since any lower start has strictly less budget
    throughout and cannot exceed a d0=C start's reachable depth at any
    step for the same a-sequence.  This is now proven, not just
    observed: d_k(d0, a-seq) = d0 + sum_{j<=k}(c_j-a_j) is affine in
    d0 with unit slope, so d_m(d0) < d_m(C) for any d0<C and any FIXED
    a-seq -- only off-optimum queries with terminal_d < best_d ever
    exercise the gap, which F1 never did.)

    Exhaustive over the engine's own (d,r) state space (see module
    docstring): explores every legal backward predecessor consistent
    with the recorded forward-live sets, not a sample -- with the
    additional d0==C pin at step 0 documented above.
    """
    memo: dict = {}

    def rec(step, d, r):
        if step == 0:
            if d != C:
                return frozenset()
            return frozenset([()]) if history[0][d][r] else frozenset()
        key = (step, d, r)
        if key in memo:
            return memo[key]
        c = letters[step - 1]
        result = set()
        live_prev = history[step - 1]
        for d0 in range(C + 1):
            a = d0 + c - d
            if a < 1:
                continue
            lo = max(1, d0 + c - C)
            hi = d0 + c
            if not (lo <= a <= hi):
                continue
            for r0 in backward_predecessors_of_r(r, a, modulus):
                if live_prev[d0][r0]:
                    for s in rec(step - 1, d0, r0):
                        result.add(s + (a,))
        result = frozenset(result)
        memo[key] = result
        return result

    return rec(m, terminal_d, target_r % modulus)


def compute_D_and_optimal_set(credit_fn, m: int, C: int, anchor_steps: int = 53):
    """Full pipeline: forward live pass -> identify D(m) and the
    terminal survivor depth -> exhaustive backward enumeration of all
    distinct optimal a-sequences. Returns (D, terminal_d, set_of_a_seqs)
    or (None, None, None) if no survivor."""
    modulus = 3 ** m
    letters, history = forward_live_fast(credit_fn, m, C, anchor_steps=anchor_steps)
    target_r = 1 % modulus
    final_live = history[m]
    survivors = [d for d in range(C + 1) if final_live[d][target_r]]
    if not survivors:
        return None, None, None
    best_d = max(survivors)
    D = C - best_d
    seqs = distinct_optimal_a_sequences(letters, history, m, C, modulus, best_d,
                                        target_r=1)
    return D, best_d, seqs


# ---------------------------------------------------------------------
# Independent brute-force cross-check (used only by f1_validate.py)
# ---------------------------------------------------------------------

def brute_force_all_chains(credit_fn, m: int, C: int, anchor_steps: int = 53):
    """Fully independent path: naive scalar recursive DFS, iterating
    EVERY starting residue r0 in [0, modulus) explicitly and using
    engine.next_residue directly (no cached permutation trick, no
    boolean arrays) -- a genuinely different code path for cross-
    validation, not a refactor of the fast method."""
    modulus = 3 ** m
    phase = anchor_steps - m
    letters = [credit_fn(phase + k) for k in range(m)]
    results = []

    def dfs(k, d, r, a_seq):
        if k == m:
            if r % modulus == 1 % modulus:
                results.append((d, tuple(a_seq)))
            return
        c = letters[k]
        for a in allowed_exponents(d, c, C):
            d2 = d + c - a
            r2 = next_residue(r, a, modulus)
            dfs(k + 1, d2, r2, a_seq + [a])

    for r0 in range(modulus):
        dfs(0, C, r0, [])
    if not results:
        return None, set()
    best_d = max(d for d, seq in results)
    seqs_at_best = set(seq for d, seq in results if d == best_d)
    return C - best_d, seqs_at_best
