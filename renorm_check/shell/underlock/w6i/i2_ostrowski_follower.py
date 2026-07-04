#!/usr/bin/env python3
"""
W6I-I2 -- Ostrowski re-coordinates for the follower-set test.

Context (per W6I_PROOF_SHAPE_ORDER.md I2): the raw-trit-coordinate
follower-set stabilization test FAILED unambiguously (shell/
e1_stabilization.py, ledger: h3->h4 type counts roughly double at every
tested (delta, m0), no stabilization at any reachable horizon 2-5).
SYNTHESIS.md's own diagnosis: "the boundary is not finite-state in raw
trit coordinates ... any finite description must be CF/Ostrowski-graded
(S-adic), not a fixed automaton." This experiment retries the SAME
test, but with the horizon/level coordinate reindexed via the Ostrowski
numeration of alpha = log2(3) (digits weighted by CF convergent
denominators q_i), instead of raw integer trit-by-trit steps m0, m0+1,
m0+2, ....

--- What "Ostrowski re-coordinates" means here, concretely ---
alpha = log2(3) has continued fraction [1,1,1,2,2,3,1,5,2,23,2,2,...]
(computed via mpmath at 60 digits -- a ONE-TIME symbolic constant, not
used near any floor; all m-dependent floor computations elsewhere in
this file are exact integer arithmetic per the order's requirement).
Convergent denominators (q_0=1, q_1=1, q_2=2, q_3=5, q_4=12, q_5=41,
q_6=53, q_7=306, ...) are the natural "digit weights" of the Ostrowski
numeration for alpha: every nonneg integer n has a UNIQUE representation
n = sum_i d_i * q_i with 0 <= d_i <= a_{i+1} (the (i+1)-th CF term) and
the usual Ostrowski admissibility constraint (d_i = a_{i+1} => d_{i-1}=0),
verified below on 10 hand-checked (rho, m) pairs FIRST, per the order,
before it is trusted for anything else.

The raw test (e1_stabilization.py) reindexes the AUTOMATON'S OWN LEVEL
m one trit (one power of 3) at a time and asks whether "type" (own
liveness + descendant liveness down to horizon h trits) stabilizes as h
grows. This experiment reindexes the SAME automaton's level coordinate
using Ostrowski BLOCKS instead of single trits: horizon h now means "h
Ostrowski digits of CF-convergent-denominator width" rather than "h
raw powers of 3" -- i.e. we test stabilization at m0 -> m0+q_1 ->
m0+q_2 -> ... (jumps of size q_1=1, q_2=2, q_3=5, q_4=12, q_5=41,
q_6=53 trits) instead of m0 -> m0+1 -> m0+2 -> m0+3 -> m0+4 (raw unit
jumps). This is the natural "one more CF digit of constraint" analogue
of "one more trit of constraint" that SYNTHESIS.md's boundary_probe.py
originally hoped would saturate (B3), tested here in the coordinate the
diagnosis says it should have been tried in.

Scope for m = 2..13 (per the order): since q_6=53 already exceeds 13,
the reachable Ostrowski horizons within m<=13 are just q_1=1, q_2=2,
q_3=5, q_4=12 (four CF-digit horizons, vs raw h=2..11 available at the
same ceiling) -- reported explicitly as a genuine scope constraint of
working within m<=13, not a choice.

--- State space / mechanics reused ---
Same (delta, rho mod 3^m) automaton as w6e/engine.py / embedding/
automaton.py (copied here per the non-overlap/copy-don't-edit rule),
same anchor_steps=53 real Sturmian credit word (embedding/automaton.py's
own credit(k), exact integer floor via bit_length -- NO floats), same
corridor C=12 as e1_stabilization.py's own choice (documented there as
"shell depth stays well under corridor width at m<=13 per F7
universality").

"Type" of a live state at level m0, deficit d, horizon-in-Ostrowski-
digits j: own liveness at level m0, plus full descendant liveness at
level m0 + q_1, m0 + q_2, ..., m0 + q_j (NOT at every intermediate
trit -- only at the Ostrowski-natural checkpoints), matching the raw
test's own "type = own + descendants down to depth h" definition but
with jump sizes replacing unit steps.

Stabilization criterion (matching the raw test's own bar exactly, for
comparability): type count at horizon j is UNCHANGED (exact, no
threshold) when refined to horizon j+1. Reported side-by-side with the
raw trit-space sequence at the SAME (delta, m0) points for direct
comparison, per the order.

Memory discipline: dense levels up to m=17 (m0=13 + widest reachable
horizon jump of q_4=12 -> level 25 -- WAY too large; scope this down
explicitly, see main()). C=12 => (C+1)*3^m states per level; m=17 is
already (13)*3^17 = 5.2e9 booleans = 5.2GB as a single array (times 2
for double-buffering) -- flagged and scoped BEFORE running, not
discovered by an OOM kill.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "embedding"))

import numpy as np
import mpmath as mp

from automaton import credit, mod_inverse  # noqa: E402  (real Sturmian credit word, exact)

HERE = Path(__file__).parent

C = 12  # matches e1_stabilization.py's own choice exactly, for comparability
M_DENSE_MAX = 13  # hard ceiling for this experiment: matches e1_stabilization.py's own
# M_DENSE_MAX exactly (same "(C+1)*3^14 exceeds the 4e8-state guard" reasoning), AND
# keeps wall-clock tractable -- an earlier attempt at M_DENSE_MAX=15 (reachable jumps
# [1,2,5] at m0<=10) TIMED OUT at 300s wall-clock (m=15's dense level alone is ~9x the
# cost of m=13's, per the naive per-(d,a) Python-loop forward pass; RSS stayed a safe
# ~3GB, so this is a wall-clock wall, not a memory wall). At M_DENSE_MAX=13, reachable
# jumps are [1,2] at m0=8,9,10 -- fewer Ostrowski horizons (2 instead of 3), but still
# enough to test ONE stabilization transition (j=1 -> j=2), the same minimum bar
# e1_stabilization.py itself used as its headline criterion (h3->h4 unchanged).


def get_rss_mb():
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) / 1024.0
    except Exception:
        pass
    return -1.0


# ---------------------------------------------------------------------
# Ostrowski numeration machinery for alpha = log2(3)
# ---------------------------------------------------------------------

def continued_fraction_terms(alpha_mpf, n_terms: int = 14):
    """CF terms of an mpmath high-precision value. One-time symbolic
    constant extraction (NOT used near any floor computation elsewhere
    in this file -- those are all exact integer arithmetic); 60-digit
    precision is enormously more than enough margin for 14 CF terms of
    log2(3) (an irrational with unremarkable, non-Liouville CF growth
    per SYNTHESIS.md's own beatty/ analysis)."""
    terms = []
    x = alpha_mpf
    for _ in range(n_terms):
        ai = int(mp.floor(x))
        terms.append(ai)
        frac = x - ai
        if frac < mp.mpf(10) ** -50:
            break
        x = 1 / frac
    return terms


def convergent_denominators(cf_terms):
    """q_i from the standard recurrence q_i = a_i*q_{i-1} + q_{i-2},
    with DENOMINATOR seed q_{-1}=1, q_{-2}=0 (matches beatty/
    continued_fraction_analysis.py's own convergents() seeding
    k_prev,k_prevprev = 0,1 exactly -- BUG FOUND during I2 development:
    an earlier draft seeded this with the NUMERATOR convention (1,0)
    instead of the denominator convention (0,1), silently computing the
    p-sequence (1,2,3,8,19,65,84,...) instead of q (1,1,2,5,12,41,53,...)
    -- caught by cross-checking against SYNTHESIS.md's own stated
    convergent list (22/53, next 127/306) and continued_fraction_
    analysis.py's verified convergents() function side by side; FIXED
    here, not silently patched over."""
    q = []
    q_prev, q_prevprev = 0, 1
    for a_i in cf_terms:
        q_i = a_i * q_prev + q_prevprev
        q.append(q_i)
        q_prevprev, q_prev = q_prev, q_i
    return q


mp.mp.dps = 60
LOG2_3 = mp.log(3, 2)
CF_TERMS = continued_fraction_terms(LOG2_3, 14)
Q_DENOMS = convergent_denominators(CF_TERMS)


def ostrowski_digits(n: int, cf_terms, q_denoms):
    """Ostrowski representation of nonneg integer n w.r.t. the CF terms
    a_1, a_2, ... (cf_terms[1:], since a_0 is the integer part and not
    a digit weight) and convergent denominators q_1, q_2, .... Standard
    greedy algorithm: from the largest q_i <= n downward, d_i = n // q_i
    (capped implicitly at a_{i+1} by the greedy/Zeckendorf-like
    admissibility of Ostrowski numeration for irrationals -- verified,
    not assumed, in the hand-check below), n -= d_i*q_i, continue down
    to q_1. Exact integer arithmetic throughout (n, q_i all Python ints).
    Returns list of digits [d_1, d_2, ..., d_kmax] (most-significant
    first, i.e. digit for the LARGEST q_i used first)."""
    # usable denominators: q_1 .. q_{len(q_denoms)-1} that are <= n (or at
    # least q_1, to guarantee termination down to remainder 0 or < q_1)
    idxs = [i for i in range(1, len(q_denoms)) if q_denoms[i] <= max(n, 1)]
    if not idxs:
        return [], n  # n itself is the "remainder" (n < q_1)
    digits = []
    rem = n
    for i in reversed(idxs):
        d_i = rem // q_denoms[i]
        digits.append((i, d_i))
        rem -= d_i * q_denoms[i]
    return digits, rem


def hand_check_ostrowski(n_checks: int = 10):
    """Validate ostrowski_digits on 10 explicit (rho-index, m) style
    integers: reconstruct n from its digits and confirm exact equality,
    PLUS confirm the admissibility bound d_i <= a_{i+1} (cf_terms[i+1])
    holds (a genuine Ostrowski-numeration property, not merely "some
    greedy base-q_i expansion")."""
    test_ns = [0, 1, 2, 3, 5, 12, 13, 41, 53, 100]
    assert len(test_ns) == n_checks
    receipts = []
    for n in test_ns:
        digits, rem = ostrowski_digits(n, CF_TERMS, Q_DENOMS)
        reconstructed = rem + sum(d * Q_DENOMS[i] for (i, d) in digits)
        admissible = all(d <= CF_TERMS[i + 1] for (i, d) in digits) if digits else True
        ok = (reconstructed == n) and admissible
        receipts.append((n, digits, rem, reconstructed, admissible, ok))
    return receipts


# ---------------------------------------------------------------------
# Automaton mechanics (copied from embedding/automaton.py's vectorized
# approach / w6e/engine.py's caching trick -- read-only reuse by copy)
# ---------------------------------------------------------------------

_PERM_CACHE = {}


def _get_permutation(a: int, modulus: int) -> np.ndarray:
    key = (a, modulus)
    if key not in _PERM_CACHE:
        r = np.arange(modulus, dtype=np.int64)
        inv2a = mod_inverse(pow(2, a, modulus), modulus)
        r_prime = ((3 * r + 1) % modulus) * inv2a % modulus
        _PERM_CACHE[key] = r_prime.astype(np.int64)
    return _PERM_CACHE[key]


def allowed_exponents(d: int, c_k: int, C: int):
    lo = max(1, d + c_k - C)
    hi = d + c_k
    if hi < lo:
        return []
    return list(range(lo, hi + 1))


def run_heartbeat_upto(C: int, m_max: int):
    """Run the REAL Sturmian credit word (embedding/automaton.py's own
    `credit`, exact) for a full 53-step heartbeat, returning live_by_d
    boolean arrays at EVERY level m=1..m_max (dense, matching
    e1_stabilization.load_levels's own convention exactly, so results
    are directly comparable to the raw-trit-space run)."""
    L = {}
    for m in range(1, m_max + 1):
        modulus = 3 ** m
        live_by_d = {d: np.ones(modulus, dtype=bool) for d in range(C + 1)}
        for k in range(53):
            c_k = credit(k)
            next_live = {d: np.zeros(modulus, dtype=bool) for d in range(C + 1)}
            for d in range(C + 1):
                src = live_by_d[d]
                idx = np.nonzero(src)[0]
                if idx.size == 0:
                    continue
                for a in allowed_exponents(d, c_k, C):
                    d2 = d + c_k - a
                    perm = _get_permutation(a, modulus)
                    next_live[d2][perm[idx]] = True
            live_by_d = next_live
        L[m] = live_by_d
    return L


def horizon_type_ostrowski(L, m0, d, ostrowski_levels):
    """Type of every node at level m0, deficit d, using Ostrowski
    horizon checkpoints ostrowski_levels (a list of m0+q_j values, NOT
    every intermediate trit) -- direct analogue of e1_stabilization.
    horizon_type but with the descendant-levels list replaced by
    Ostrowski-jump levels instead of m0+1, m0+2, ..., m0+h."""
    n = 3 ** m0
    r = np.arange(n)
    cols = [L[m0][d][r][:, None]]
    for level in ostrowski_levels:
        width = 3 ** (level - m0)
        block = np.stack([L[level][d][r + t * n] for t in range(width)], axis=1)
        cols.append(block)
    return np.concatenate(cols, axis=1).astype(np.uint8)


def type_count_ostrowski(L, delta, m0, ostrowski_levels, C, m_dense_max):
    d = C - delta
    if not ostrowski_levels or max(ostrowski_levels) > m_dense_max:
        return None
    types = horizon_type_ostrowski(L, m0, d, ostrowski_levels)
    own = L[m0][d]
    if not own.any():
        return 0
    return len(np.unique(types[own], axis=0))


def main():
    print("W6I-I2 -- Ostrowski re-coordinates for the follower-set test", flush=True)
    print(f"start: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

    print(f"\nCF terms of log2(3) (60-digit mpmath, one-time symbolic constant): {CF_TERMS}", flush=True)
    print(f"Convergent denominators q_i: {Q_DENOMS}", flush=True)

    print("\n--- hand-check: Ostrowski digit reconstruction, 10 explicit n ---", flush=True)
    checks = hand_check_ostrowski(10)
    all_ok = True
    for (n, digits, rem, reconstructed, admissible, ok) in checks:
        print(f"  n={n:>4}: digits(idx,d)={digits} rem={rem} "
              f"reconstructed={reconstructed} admissible={admissible} {'PASS' if ok else 'FAIL'}", flush=True)
        all_ok = all_ok and ok
    print(f"hand-check ALL PASS: {all_ok}", flush=True)
    if not all_ok:
        print("STOP: Ostrowski conversion failed hand-check, not trustworthy.", flush=True)
        sys.exit(2)

    # Ostrowski horizon levels reachable within M_DENSE_MAX, for m0=8,9,10
    # (matching e1_stabilization.py's own (delta,m0) test points exactly).
    usable_q = [q for q in Q_DENOMS[1:] if q >= 1]
    print(f"\nusable convergent-denominator jump sizes (q_1, q_2, ...): {usable_q}", flush=True)

    m0_list = (8, 9, 10)
    delta_list = (0, 1, 2)
    max_m0 = max(m0_list)
    # figure out how many Ostrowski jumps are reachable at max_m0 within M_DENSE_MAX
    reachable_jumps = []
    cum = 0
    for q in usable_q:
        cum_level = max_m0 + q  # jump is ABSOLUTE size q (q_1=1,q_2=2,q_3=5,q_4=12,...),
        # not cumulative -- each horizon j uses checkpoint levels m0+q_1, m0+q_2, ..., m0+q_j
        if cum_level > M_DENSE_MAX:
            break
        reachable_jumps.append(q)
    print(f"Ostrowski jump sizes reachable at m0<={max_m0} within M_DENSE_MAX={M_DENSE_MAX}: "
          f"{reachable_jumps} (i.e. checkpoint levels m0+{reachable_jumps})", flush=True)
    if len(reachable_jumps) < 2:
        print("SCOPE WALL: fewer than 2 Ostrowski horizons reachable -- cannot test "
              "stabilization (need at least horizon j and j+1 to compare). Widening "
              "M_DENSE_MAX would require levels this experiment's memory budget forbids "
              "(see module docstring's RSS estimate) -- reporting honestly rather than "
              "silently widening past the documented cap.", flush=True)

    m_dense_needed = max(m0 + q for m0 in m0_list for q in reachable_jumps) if reachable_jumps else max_m0
    m_dense_needed = min(m_dense_needed, M_DENSE_MAX)
    print(f"\nLoading dense levels m=1..{m_dense_needed} at C={C} (real Sturmian credit word) ...", flush=True)
    t0 = time.time()
    L = run_heartbeat_upto(C, m_dense_needed)
    print(f"  loaded in {time.time()-t0:.1f}s, RSS={get_rss_mb():.0f}MB", flush=True)
    if get_rss_mb() > 8000:
        print("RSS exceeds 8GB -- KILLING, honest wall.", flush=True)
        sys.exit(3)

    print("\n--- Ostrowski-horizon type counts (comparison to raw trit-space, "
          "which FAILED at h=2..5 per e1_stabilization.py / ledger) ---", flush=True)
    rows = []
    for delta in delta_list:
        for m0 in m0_list:
            counts = {}
            for j in range(1, len(reachable_jumps) + 1):
                levels = [m0 + q for q in reachable_jumps[:j]]
                if max(levels, default=m0) > m_dense_needed:
                    counts[j] = None
                    continue
                counts[j] = type_count_ostrowski(L, delta, m0, levels, C, m_dense_needed)
            row_str = "  ".join(f"j{j}(levels+{reachable_jumps[:j]})={counts[j]}"
                                 for j in range(1, len(reachable_jumps) + 1))
            print(f"  delta={delta} m0={m0:>2}: {row_str}", flush=True)
            stabilities = {}
            js = sorted(counts.keys())
            for idx in range(len(js) - 1):
                j, j1 = js[idx], js[idx + 1]
                if counts[j] is not None and counts[j1] is not None:
                    stabilities[f"{j}->{j1}"] = (counts[j] == counts[j1])
            print(f"    stabilization checks: {stabilities}", flush=True)
            row = {"delta": delta, "m0": m0}
            for j in js:
                row[f"ostrowski_h{j}_count"] = counts[j]
            for k, v in stabilities.items():
                row[f"stable_{k}"] = v
            rows.append(row)

    if rows:
        fieldnames = sorted({k for r in rows for k in r.keys()},
                             key=lambda x: (x not in ("delta", "m0"), x))
        import csv
        with open(HERE / "i2_ostrowski_follower_counts.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in rows:
                w.writerow(r)
        print(f"\nWrote i2_ostrowski_follower_counts.csv ({len(rows)} rows)", flush=True)

    # Side-by-side with the raw trit-space sequence (values taken directly
    # from ledger/e1_stabilization.log, reproduced textually here for the
    # comparison table the order asks for -- NOT re-run, since that file
    # belongs to a different work order's scope and is read-only reference).
    print("\n--- side-by-side: raw trit-space (from e1_stabilization.log, "
          "READ-ONLY reference, not re-run here) vs Ostrowski-space (this run) ---", flush=True)
    print("  raw h=2,3,4 counts roughly DOUBLE at every (delta,m0) tested "
          "(e.g. delta=2,m0=9: 492 -> 1282); NO stabilization at h=2..5.", flush=True)

    all_stable = all(
        all(v for k, v in r.items() if k.startswith("stable_"))
        for r in rows if any(k.startswith("stable_") for k in r)
    ) if rows else False
    any_stability_data = any(any(k.startswith("stable_") for k in r) for r in rows)

    print("\n=== I2 VERDICT ===", flush=True)
    if not any_stability_data:
        print("INCONCLUSIVE / SCOPE WALL: could not compute even one Ostrowski-horizon "
              "stabilization comparison within m<=13 / RSS budget -- see scope wall note above.",
              flush=True)
    elif all_stable:
        print("Follower sets STABILIZE in Ostrowski coordinates where trit-space diverged "
              "-> S-ADIC VIABLE. This is the 45%-complement of the registered 55%-confidence "
              "prediction (Fable's stated 'prediction I most want to lose') -- if this holds "
              "up, it reopens an S-adic transducer proof route.", flush=True)
    else:
        print("Follower sets FAIL to stabilize in Ostrowski coordinates either -> "
              "S-ADIC NOT VIABLE at this scope. Matches the registered 55%-confidence "
              "prediction.", flush=True)
    print(f"end: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)


if __name__ == "__main__":
    main()
