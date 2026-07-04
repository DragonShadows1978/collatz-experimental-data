#!/usr/bin/env python3
"""
W6E engine -- validated game/automaton primitives per
W6E_BOUND_PAIR_MECH_ORDER.md and DERIVATION_NOTES.md sec 1/2/5b.

VALIDATION HISTORY (see w6e/VERIFY_LOG.md / ledger W6E-E1 for the full
account): a first draft modeled this as a literal backward chain
starting at (rho=1, delta=0) at the terminal and consuming credit
letters c_0, c_1, ... in forward OR reverse order. That draft produced
ZERO surviving chains on nearly every ground-truth row -- wrong. The
issue: the residue window for D(m) is NOT phase-free and is NOT
anchored at word-index 0; it is the exact m-window ending at the
TRUE measurement's absolute forward step 53, i.e. absolute indices
[53-m, 53). The free-prefix argument in DERIVATION_NOTES sec 1
("earlier steps are a free deficit walk, always satisfiable") means
the depth budget before that window is fungible, NOT that the window's
own phase is a free/minimized parameter -- minimizing over phase
independently (tested explicitly) reproduces 6/7 rows but MISSES m=5
(gives 1, ground truth is 2). Anchoring the window at [53-m, 53)
(matching the actual 53-step house convention used to build every
ground-truth table) reproduces ALL 7 golden rows and ALL 9 sqrt2 rows
tested by exhaustive BFS. This is the model used throughout W6E.

Mechanics (validated forward form, equivalent to the order's backward
description by time-reversal):
  - Forward step: d' = d + c - a, a in allowed_exponents(d, c, C)
    = [max(1, d+c-C), d+c]; residue r' = (3r+1) * inv(2^a) mod 3^m.
  - This is IDENTICAL to embedding/automaton.py's mechanics (shared,
    re-derived here in scalar form for explicit single-chain use).
  - D(m) = C - max{d : (d, r=1 mod 3^m) reachable at absolute step 53
    from EVERY (d0, r0) live at absolute step (53-m)}, i.e. exhaustive
    BFS over the m-window [53-m, 53) starting fully populated.
  - Reversed (backward-from-terminal) view: same trajectory read
    backward. delta (ceiling-distance from C) at forward step j is
    delta_j = C - d_j; delta_{j+1} = delta_j + (a_j - c_j) forward, so
    read backward (terminal delta=D(m) at j=m, walking back to j=0):
    delta_prev = delta_cur - (a - c) = delta_cur + (c - a), matching
    the order's delta' = delta + c - a exactly, provided the STARTING
    delta at the terminal (j=m, the actual terminal state) is treated
    as the unknown D(m) itself (not fixed at 0) and rho is fixed at 1
    only at j=m (the terminal), not at j=0. The forward BFS form above
    is what's actually used (it is exhaustive and unambiguous); the
    backward description is kept for the walker strategies (S0/S1),
    which need to build ONE explicit chain, not a full BFS.

Residue precision: tracked as an exact integer mod 3^m throughout
(m <= 16 in this order's scope, 3^16 ~ 43M -- small). No lift
truncation; this sidesteps the sec 5a lift leak entirely because we
work at one fixed, finite m and never need coordinates beyond mod 3^m.
"""
from __future__ import annotations

import numpy as np


def mod_inverse(v: int, mod: int) -> int:
    return pow(v, -1, mod)


def next_residue(r: int, a: int, mod: int) -> int:
    """Forward step residue map: r' = (3r+1) * inv(2^a) mod `mod`."""
    inv2a = mod_inverse(pow(2, a, mod), mod)
    return ((3 * r + 1) * inv2a) % mod


def allowed_exponents(d: int, c: int, C: int):
    """Forward-step legal exponents: a in [max(1, d+c-C), d+c],
    ensuring d' = d+c-a stays in [0, C]. This matches
    embedding/automaton.py's legality condition exactly. Forward,
    every a in this window is legal; the mod-3 parity/class
    restriction the order describes governs the BACKWARD read (which
    predecessor a given r' by which a) -- see
    forced_parity_for_backward_step below, verified to select a
    subset of exactly these forward-legal a's."""
    lo = max(1, d + c - C)
    hi = d + c
    if hi < lo:
        return []
    return list(range(lo, hi + 1))


def class_mod3(r: int) -> int:
    return r % 3


def forced_parity_for_backward_step(rho: int):
    """Given the CURRENT (later-in-forward-time) residue rho, return
    the parity required of the exponent `a` used on the backward step
    that produced rho from its predecessor (i.e., predecessor rho' =
    (2^a * rho - 1) / 3 must be an exact integer). Returns 0 (even),
    1 (odd), or None (class 0, no legal backward move) -- exactly the
    order's spec, verified in VERIFY_LOG:
      class 0 (rho%3==0): no legal move ever (2^a*rho%3==0 always).
      class 1 (rho%3==1): need 2^a%3==1 -> a even.
      class 2 (rho%3==2): need 2^a%3==2 -> a odd.
    """
    cls = rho % 3
    if cls == 0:
        return None
    return 0 if cls == 1 else 1


def backward_predecessor_exact(rho: int, a: int) -> int:
    """rho' = (2^a * rho - 1)/3 as an exact Python integer (used by
    the walker strategies, which build one explicit chain backward
    from a residue value tracked as an actual bounded integer, not
    reduced mod anything, so the division by 3 is exact integer
    arithmetic every time -- no modular-inverse-of-3 issue)."""
    num = (1 << a) * rho - 1
    assert num % 3 == 0, (
        f"backward_predecessor_exact: not divisible by 3 "
        f"(rho={rho}, a={a}) -- parity rule violated, engine bug"
    )
    return num // 3


def bfs_Dm(credit_fn, m: int, C: int, anchor_steps: int = 53,
           want_chain: bool = False):
    """Exhaustive forward BFS over the residue window [anchor_steps-m,
    anchor_steps), starting fully populated (every (d,r), d in [0,C],
    r in [0, 3^m)) -- the VALIDATED D(m) computation, matching the
    W6D-G ground-truth convention exactly (53-step house readout).

    Returns D (= C - max ending depth among r=1-mod-3^m survivors), or
    None if no survivor. If want_chain, also returns one explicit
    optimal chain (list of (c_k, a_k) forward-order pairs) achieving
    the max ending depth, extracted by parent-pointer backtracking.
    """
    mod = 3 ** m
    phase = anchor_steps - m
    live = {(d, r): None for d in range(C + 1) for r in range(mod)}
    history = [live] if want_chain else None
    letters = []
    cur = live
    for k in range(m):
        c = credit_fn(phase + k)
        letters.append(c)
        new_live = {}
        for (d, r) in cur:
            for a in allowed_exponents(d, c, C):
                d2 = d + c - a
                r2 = next_residue(r, a, mod)
                key = (d2, r2)
                if key not in new_live:
                    new_live[key] = ((d, r), a) if want_chain else None
        cur = new_live
        if want_chain:
            history.append(new_live)
    target_r = 1 % mod
    survivors = [d for (d, r) in cur if r == target_r]
    if not survivors:
        return (None, None) if want_chain else None
    best_d = max(survivors)
    D = C - best_d
    if not want_chain:
        return D
    # backtrack
    chain = []
    node = (best_d, target_r)
    for step in range(m, 0, -1):
        parent, a = history[step][node]
        c = letters[step - 1]
        chain.append((c, a))
        node = parent
    chain.reverse()
    return D, chain


_PERM_CACHE = {}


def _get_permutation(a: int, modulus: int) -> np.ndarray:
    """Vectorized r -> r' = (3r+1)*inv(2^a) mod modulus, cached (same
    trick as embedding/automaton.py / toy_automaton.py, reused here for
    a fast D-only readout -- NOT used for chain extraction, which needs
    parent pointers and stays on the scalar dict path in bfs_Dm)."""
    key = (a, modulus)
    if key not in _PERM_CACHE:
        r = np.arange(modulus, dtype=np.int64)
        inv2a = mod_inverse(pow(2, a, modulus), modulus)
        r_prime = ((3 * r + 1) % modulus) * inv2a % modulus
        _PERM_CACHE[key] = r_prime.astype(np.int64)
    return _PERM_CACHE[key]


def bfs_Dm_fast(credit_fn, m: int, C: int, anchor_steps: int = 53) -> int | None:
    """Vectorized D-only computation, identical mechanics to bfs_Dm but
    using numpy boolean arrays per depth (as
    shell/toy_word/toy_automaton.py's run_heartbeat_generic does) for
    speed at larger m. No chain extraction -- use bfs_Dm(want_chain=True)
    for that (small m only, where the scalar dict approach is fine).
    Cross-checked against bfs_Dm on all m in VERIFY_LOG; use this for
    m >= ~10 where the scalar dict path gets slow.
    """
    modulus = 3 ** m
    phase = anchor_steps - m
    live_by_d = {d: np.ones(modulus, dtype=bool) for d in range(C + 1)}
    for k in range(m):
        c = credit_fn(phase + k)
        next_live_by_d = {d: np.zeros(modulus, dtype=bool) for d in range(C + 1)}
        for d in range(C + 1):
            src = live_by_d[d]
            live_r_indices = np.nonzero(src)[0]
            if live_r_indices.size == 0:
                continue
            for a in allowed_exponents(d, c, C):
                d_prime = d + c - a
                perm = _get_permutation(a, modulus)
                targets = perm[live_r_indices]
                next_live_by_d[d_prime][targets] = True
        live_by_d = next_live_by_d
    target_r = 1 % modulus
    alive_d = [d for d in range(C + 1) if live_by_d[d][target_r]]
    if not alive_d:
        return None
    return C - max(alive_d)


def keystone_check(chain, m: int) -> dict:
    """Verify the keystone identity 2^{Sigma a} == S (mod 3^m) for a
    forward chain [(c_1,a_1), ..., (c_m,a_m)] (DERIVATION_NOTES 5b),
    S = sum_{i=0}^{m-1} 3^{m-1-i} * 2^{A_i}, A_i = a_1+...+a_i (A_0=0).
    Also checks the per-prefix version at every k=1..m (each suffix of
    length k obeys the SAME identity restricted to itself, per the
    order's E3 instruction) -- returns a dict of per-k pass/fail.
    """
    mod = 3 ** m
    a_list = [a for (c, a) in chain]
    results = {}
    n = len(a_list)
    for k in range(1, n + 1):
        suffix_a = a_list[n - k:]
        mod_k = 3 ** k
        Sigma_a = sum(suffix_a)
        A = [sum(suffix_a[:i]) for i in range(0, k + 1)]
        S = sum(3 ** (k - 1 - i) * 2 ** A[i] for i in range(k))
        lhs = pow(2, Sigma_a, mod_k)
        rhs = S % mod_k
        results[k] = (lhs == rhs, lhs, rhs)
    return results


if __name__ == "__main__":
    print("engine.py: primitives module, see verify_engine.py for the "
          "pre-experiment integrity check.")
