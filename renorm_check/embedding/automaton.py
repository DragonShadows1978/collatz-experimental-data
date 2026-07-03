"""
Faithful reimplementation of the residue automaton A(C, m) as defined in
COLLATZ_PROOF.md Section 4.2-4.3, for testing the corridor-embedding
("renormalization") conjecture:

    Does A(C+22, m+53) contain an exact, explicit self-embedding of A(C, m),
    shifted by one Sturmian heartbeat (53 precision levels)?

Definition (verbatim from the proof doc, Section 4.2):
  - States: pairs (d, r) with deficit d in {0, ..., C} and residue
    r in Z/3^m Z.
  - Transitions: (d, r) -> (d + c_k - a, (3r+1)*(2^a)^-1 mod 3^m)
    for each allowed exponent a.
  - Terminal signature: r == 1 (mod 3^m).

Credit sequence: c_k = floor((k+1)*alpha) - floor(k*alpha), alpha = log2(3).
This is exactly the Sturmian word; the first 53 entries contain 22 ones
(support phases) and 31 twos (drop phases) -- Lemma 3, verified below.

Allowed exponents at a transition from deficit d at step with credit c_k:
  a ranges over all a >= 1 (since a = v2(3x+1) >= 1 is forced for the true
  Collatz map on odd x). A transition survives (stays in-corridor) iff the
  new deficit d' = d + c_k - a lies in [0, C]. This matches the proof's
  explicit statements:
    - Part 3 (spectral radius): "at drop phases (c=2): the exponent a
      ranges from 1 to d+2" -- i.e. a in [1, d+c_k] when c_k=2, which is
      exactly the surviving range once we also intersect with a >= 1 and
      d' >= 0 (d' <= d, since a>=1 => d'=d+c-a<=d+c-1).
    - The full surviving range accounting for the corridor floor is
      a in [max(1, d + c_k - C), d + c_k] (i.e. 0 <= d' <= C).
  Values of a outside this range send d' out of [0, C] -- "Corridor exit:
  d' < 0 or d' > C" (Section 8.5's explicit kill condition, reused here
  for the 3-adic-only automaton of Section 4.2) -- and the resulting state
  is simply not added to the live set (it is killed / exits the corridor).

We track the automaton generation-by-generation across one full 53-step
Sturmian heartbeat, starting from the FULLY POPULATED initial state set
(every (d, r) pair live at step 0), exactly as Theorem 1's proof
describes: "The automaton A(C, m) initializes with all states (d, r)
where d in {0,...,C} and r in Z/3^m Z" (Lemma 4 proof, Section 8.3).

"live(C, m)" for this investigation is defined as the terminal-compatible
state set (r == 1 mod 3^m) surviving after running the automaton through
one full 53-step heartbeat from that fully populated start. This matches
Theorem 1's "birth" construction: new terminal-compatible states entering
the live set are tracked at each of the 53 steps, and the desert edge is
where new births cease.

PERFORMANCE NOTE: this module provides two implementations.
  - The reference (slow, obviously-correct) implementation using Python
    sets: `run_heartbeat_reference`. Used only for cross-checking the
    vectorized implementation at small sizes.
  - A vectorized numpy implementation using boolean occupancy arrays per
    deficit level: `run_heartbeat`. For fixed (d, c_k, a), the residue map
    r -> (3r+1)*(2^a)^-1 mod 3^m is applied to an entire boolean liveness
    array via gather/scatter, avoiding per-state Python overhead.
"""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np

ALPHA = math.log2(3)
HEARTBEAT = 53
SUPPORT_COUNT = 22
DROP_COUNT = 31


def _exact_floor_k_log2_3(k: int) -> int:
    """floor(k*log2(3)) via floor(log2(3^k)) = bit_length(3^k) - 1.

    Uses Python's arbitrary-precision ints -- no float involved -- so this
    stays exact arbitrarily far past ALPHA's ~15-17 significant f64 digits,
    unlike `math.floor(k * ALPHA)`. See renorm_check/SYNTHESIS.md F2/W1: the
    amended F5 edge-witness search runs credit_sequence out past step 358,
    well beyond where f64 floors are safe to trust near a convergent
    denominator.
    """
    if k == 0:
        return 0
    return (3 ** k).bit_length() - 1


def credit(k: int) -> int:
    """Sturmian credit at step k (0-indexed): c_k in {1, 2}."""
    return _exact_floor_k_log2_3(k + 1) - _exact_floor_k_log2_3(k)


@lru_cache(maxsize=None)
def credit_sequence(n: int = HEARTBEAT) -> tuple:
    return tuple(credit(k) for k in range(n))


def verify_lemma3() -> dict:
    seq = credit_sequence(HEARTBEAT)
    return {
        "sequence": list(seq),
        "support_count": seq.count(1),
        "drop_count": seq.count(2),
        "total": len(seq),
        "matches_lemma3": seq.count(1) == SUPPORT_COUNT and seq.count(2) == DROP_COUNT,
    }


def M_edge(C: int) -> int:
    """Support-capacity edge: floor(53*(C+1)/22)."""
    return (HEARTBEAT * (C + 1)) // SUPPORT_COUNT


def _extended_gcd(a: int, b: int):
    if a == 0:
        return (b, 0, 1)
    g, x1, y1 = _extended_gcd(b % a, a)
    return (g, y1 - (b // a) * x1, x1)


def mod_inverse(value: int, modulus: int) -> int:
    """Modular inverse via extended Euclidean algorithm."""
    if modulus == 1:
        return 0
    g, x, _ = _extended_gcd(value % modulus, modulus)
    if g != 1:
        raise ValueError(f"{value} has no inverse mod {modulus}")
    return x % modulus


def next_residue(r: int, a: int, modulus: int) -> int:
    """(3r+1) * (2^a)^-1 mod modulus. Scalar reference version."""
    inv2a = mod_inverse(pow(2, a, modulus), modulus)
    return ((3 * r + 1) * inv2a) % modulus


def allowed_exponents(d: int, c_k: int, C: int):
    """Exponents a >= 1 such that d' = d + c_k - a stays within [0, C].
    a in [max(1, d + c_k - C), d + c_k]."""
    lo = max(1, d + c_k - C)
    hi = d + c_k
    if hi < lo:
        return []
    return list(range(lo, hi + 1))


# ---------------------------------------------------------------------------
# Reference (slow, Python-set) implementation -- used only for small-scale
# cross-checks against the vectorized implementation.
# ---------------------------------------------------------------------------

def run_heartbeat_reference(C: int, m: int, steps: int = HEARTBEAT, track_terminal_only: bool = False):
    modulus = 3 ** m
    live = set()
    for d in range(C + 1):
        for r in range(modulus):
            live.add((d, r))

    # Group live residues by deficit for correct source restriction.
    by_d = {d: set() for d in range(C + 1)}
    for d, r in live:
        by_d[d].add(r)

    seq = credit_sequence(steps)
    history_sizes = [len(live)]
    for k in range(steps):
        c_k = seq[k]
        next_by_d = {d: set() for d in range(C + 1)}
        for d in range(C + 1):
            src_residues = by_d[d]
            if not src_residues:
                continue
            a_list = allowed_exponents(d, c_k, C)
            for a in a_list:
                d_prime = d + c_k - a
                for r in src_residues:
                    r_prime = next_residue(r, a, modulus)
                    next_by_d[d_prime].add(r_prime)
        by_d = next_by_d
        live = {(d, r) for d in by_d for r in by_d[d]}
        history_sizes.append(len(live))

    if track_terminal_only:
        terminal = {(d, r) for (d, r) in live if r % modulus == 1 % modulus}
        return terminal, history_sizes
    return live, history_sizes


# ---------------------------------------------------------------------------
# Vectorized (numpy) implementation.
# ---------------------------------------------------------------------------

def _residue_permutation(a: int, modulus: int) -> np.ndarray:
    """Return array P of length `modulus` such that P[r] = (3r+1)*(2^a)^-1 mod modulus.
    We do not assume bijectivity; we directly compute images for every r and
    the caller scatters (OR-accumulates) them into the target array."""
    r = np.arange(modulus, dtype=np.int64)
    inv2a = mod_inverse(pow(2, a, modulus), modulus)
    r_prime = ((3 * r + 1) % modulus) * inv2a % modulus
    return r_prime.astype(np.int64)


_PERM_CACHE = {}


def _get_permutation(a: int, modulus: int) -> np.ndarray:
    key = (a, modulus)
    if key not in _PERM_CACHE:
        _PERM_CACHE[key] = _residue_permutation(a, modulus)
    return _PERM_CACHE[key]


def run_heartbeat(C: int, m: int, steps: int = HEARTBEAT, track_terminal_only: bool = False,
                   max_states_guard: int = 400_000_000):
    """
    Vectorized version. live_by_d[d] is a boolean numpy array of length
    3^m indicating which residues are live at deficit d.

    Returns (final_live_by_d: dict[int, np.ndarray[bool]], history_sizes: list[int])
    or, if track_terminal_only, returns (terminal_set: set[(d,r)], history_sizes).
    """
    modulus = 3 ** m
    total_states = (C + 1) * modulus
    if total_states > max_states_guard:
        raise ValueError(
            f"state space too large: C={C}, m={m}, modulus=3^{m}={modulus}, "
            f"total_states={total_states} > guard {max_states_guard}"
        )

    live_by_d = {d: np.ones(modulus, dtype=bool) for d in range(C + 1)}
    history_sizes = [sum(int(arr.sum()) for arr in live_by_d.values())]

    seq = credit_sequence(steps)
    for k in range(steps):
        c_k = seq[k]
        next_live_by_d = {d: np.zeros(modulus, dtype=bool) for d in range(C + 1)}
        for d in range(C + 1):
            src = live_by_d[d]
            live_r_indices = np.nonzero(src)[0]
            if live_r_indices.size == 0:
                continue
            for a in allowed_exponents(d, c_k, C):
                d_prime = d + c_k - a
                perm = _get_permutation(a, modulus)
                targets = perm[live_r_indices]
                next_live_by_d[d_prime][targets] = True
        live_by_d = next_live_by_d
        history_sizes.append(sum(int(arr.sum()) for arr in live_by_d.values()))

    if track_terminal_only:
        terminal = set()
        target_residue = 1 % modulus
        for d in range(C + 1):
            if live_by_d[d][target_residue]:
                terminal.add((d, target_residue))
        return terminal, history_sizes

    return live_by_d, history_sizes


def terminal_compatible_set(C: int, m: int, steps: int = HEARTBEAT):
    """Convenience wrapper: returns (terminal_live_set, history_sizes)."""
    return run_heartbeat(C, m, steps=steps, track_terminal_only=True)


def full_live_set(C: int, m: int, steps: int = HEARTBEAT):
    """Returns (dict[d -> np.ndarray[bool]], history_sizes) -- the FULL live
    state set (not just terminal-compatible), needed for the embedding test
    which compares entire reach sets, not just the terminal residue."""
    return run_heartbeat(C, m, steps=steps, track_terminal_only=False)
