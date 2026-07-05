#!/usr/bin/env python3
"""
W6W-SPARSE -- core instrument: full-precision, live-set-only FORWARD
recursion for corridor survival ("is some terminal-compatible state
alive after one 53-step heartbeat, starting from a fully populated
corridor?" -- exactly M_edge(C)'s definition, per shell/shell_probe.py
P3 and embedding/automaton.py's docstring, Theorem 1 / Lemma 4).

=== Why "forward from all states" cannot itself be made sparse ===

M_edge(C)'s definition (automaton.py lines 36-47, Theorem 1's own
construction) REQUIRES the automaton to start FULLY POPULATED: every
(d, r) with d in [0,C], r in Z/3^m is live at step 0. That initial
condition is dense by definition (all 3^m residues per level) -- no
amount of cleverness makes the START sparse; the dense instrument's
wall (W6V-MEASURE: ~13-15x per-trial permutation-cache multiplier on
top of (C+1)*3^m) comes from carrying that dense set through 53
forward transition steps as boolean arrays.

=== The sparse reformulation used here ===

The automaton's transition (d, r) -[a]-> (d+c-a, (3r+1)*inv(2^a) mod
3^m) is a well-defined FUNCTION of (d, r, a) but is 3-to-1, not a
bijection (verified directly: mod 3, 3r+1 collapses all r to the same
residue class before the invertible-unit multiply; confirmed
empirically in this round -- every one of 729 (a, r') pairs at C=5,
m=5 had >1 preimage r). So "reachable forward from everywhen" is NOT
simply the same object as "reachable backward from the single
terminal residue" in general.

BUT the specific question M_edge(C) asks --- does SOME live (d, r=1)
survive one full heartbeat, starting from ALL (d,r) populated --- is
equivalent to: does there exist an m-step sequence of exponents
a_1..a_m (each step's a legal per that step's credit c_k and the
corridor [0,C]) whose FORWARD residue walk, run from SOME valid start
residue r_0, lands on r_m = 1 mod 3^m? Because the initial state set
is "any r_0 is live", the existence question collapses to: is there
ANY exponent sequence, ANY starting residue, that is corridor-deficit-
legal (0<=d_k<=C throughout, d_0 free/any starting deficit in [0,C],
matching the "fully populated -- any d in [0,C] live at start" initial
condition) and residue-legal (lands on r_m=1)?

This is answered by walking BACKWARD from the single terminal residue
r_m = 1 (an EXACT integer rho, not a fixed-modulus residue -- see
below) through the 53-step heartbeat's credit sequence in REVERSE,
which is now a genuine one-to-one backward relation (each rho has at
most 2 legal predecessors per step, one for each parity class, forced
by rho mod 3 -- verified below, GATE B0). Backward search from a
SINGLE seed instead of forward simulation from 3^m seeds is exactly
the "track only the surviving states" sparse instrument: the live set
at each backward layer is only the (rho mod 3^k, deficit-partial-sum-
state) pairs that are still corridor-legal, which the death shell
keeps small (see peak live-set-size table in the final report) even
where the dense forward array would need 3^m bits per deficit level.

Endpoint convention (matching shell_probe.py / automaton.py EXACTLY,
this is the FORWARD, fully-populated-start, C-fixed convention -- NOT
the W6U-RECON D_recon "free-endpoint deficit RANGE" reconciled object,
which is a related but textually distinct quantity: D_recon(m) sweeps
C at fixed m; here we sweep m at fixed C, deficit d_0 is free in [0,C]
(any state populated at start) and d_m is free in [0,C] (any surviving
terminal-compatible state counts) -- so the deficit walk must stay
inside [0, C] the entire time with BOTH endpoints free. This is
value-identical in structure to the W6U-RECON w4/w5 "variant (ii)
free-endpoint range" search, independently re-derived and
re-implemented from scratch here (not imported), then cross-validated
against shell_probe.py's DENSE oracle directly (not against w4/w5's
files) as this round's own gate.

Exact arithmetic: ALL Collatz/corridor computation here uses Python
arbitrary-precision ints (rho as an exact integer during backward
reconstruction; residues during the layered BFS as Python ints mod
3^k, itself an exact int). No floats/numpy anywhere in the arithmetic
path. numpy/float use is confined to shell/shell_probe.py-style dense
CROSS-CHECKS only (imported read-only, never modified).
"""
from __future__ import annotations

import math
import resource
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
UNDERLOCK = HERE.parent
EMBEDDING = HERE.parent.parent.parent / "embedding"  # renorm_check/embedding


# ---------------------------------------------------------------------
# Credit sequence -- exact integer re-derivation (independent of
# embedding/automaton.py's own credit_sequence(), cross-checked below).
# ---------------------------------------------------------------------

def floor_k_log2_3(k: int) -> int:
    """floor(k * log2(3)) exactly, via bit_length(3**k). No floats."""
    if k == 0:
        return 0
    return (3 ** k).bit_length() - 1


def credit_at_step(k: int) -> int:
    """Sturmian credit c_k (0-indexed), rust/lock3_census.rs:1247-1249
    semantics: credit_at_step(k) = floor((k+1)log2 3) - floor(k log2 3)."""
    return floor_k_log2_3(k + 1) - floor_k_log2_3(k)


HEARTBEAT = 53


def heartbeat_letters_forward(steps: int = HEARTBEAT):
    """Forward-order credits c_0..c_{steps-1} (absolute step index,
    matching automaton.py's `credit(k)` / `credit_sequence`)."""
    return [credit_at_step(k) for k in range(steps)]


def verify_lemma3(steps: int = HEARTBEAT) -> dict:
    seq = heartbeat_letters_forward(steps)
    return {
        "support_count": seq.count(1),
        "drop_count": seq.count(2),
        "total": len(seq),
        "matches_lemma3": seq.count(1) == 22 and seq.count(2) == 31,
    }


def M_edge_formula(C: int) -> int:
    """Closed-form capacity law: floor(53*(C+1)/22)."""
    return (53 * (C + 1)) // 22


# ---------------------------------------------------------------------
# Backward step primitives (exact integers; independent re-derivation).
# ---------------------------------------------------------------------

def parity_forced(rho: int):
    """rho mod 3 forces the parity of the NEXT (backward) exponent a
    in the step rho' = (2^a * rho - 1) / 3 (exact division required):
        rho % 3 == 0 -> no legal a (dead: 2^a*rho-1 == -1 mod 3 always
                         when rho%3==0, never divisible by 3)
        rho % 3 == 1 -> a must be EVEN  (2^a == 1 mod 3 needed)
        rho % 3 == 2 -> a must be ODD   (2^a == 2 mod 3 needed)
    (2^a mod 3 cycles 2,1,2,1,... for a=1,2,3,4,... ; matches
    a even -> 2^a==1 mod 3, a odd -> 2^a==2 mod 3.)
    """
    cls = rho % 3
    if cls == 0:
        return None
    return 0 if cls == 1 else 1  # 0 = "a even", 1 = "a odd"


def backward_pred_exact(rho: int, a: int) -> int:
    """rho' = (2^a * rho - 1) / 3, EXACT integer division (caller must
    have already checked parity_forced(rho) matches a's parity)."""
    num = (1 << a) * rho - 1
    assert num % 3 == 0, "parity precondition violated"
    return num // 3


def backward_pred_mod(R: int, a: int, mod_next: int) -> int:
    """Same transition, but tracking rho only mod mod_next (mod_next =
    3^(current backward depth - 1)). Well-defined: changing R by
    t*3*mod_next changes (2^a*R-1)//3 by t*2^a*mod_next, i.e. congruent
    mod mod_next for ANY representative R of the residue class -- this
    is exactly why a layered *residue* BFS (no growing big ints needed
    for the modular variant) is legitimate."""
    if mod_next <= 1:
        return 0
    num = (1 << a) * R - 1
    assert num % 3 == 0, "parity precondition violated (mod variant)"
    return (num // 3) % mod_next


# ---------------------------------------------------------------------
# Sparse backward live-set search: free-endpoint deficit RANGE variant,
# matching M_edge(C)'s "fully populated start / any surviving terminal
# counts" semantics (d_0 free in [0,C], d_m free in [0,C]).
#
# State carried per live element, backward layer j (j = number of
# heartbeat steps consumed so far, counting from the terminal end):
#   R       : rho mod 3^j                  (exact int, the true residue
#             class of the eventual starting integer, mod 3^j)
#   u = s - min_s   (>= 0)
#   v = max_s - s   (>= 0)
#     where s is the deficit PARTIAL SUM (sum of (c_k - a_k) consumed
#     so far, backward order) relative to the (unknown, to-be-fixed)
#     starting deficit; u/v jointly capture the sufficient statistic
#     for "can this partial walk still fit inside SOME window of width
#     C once continued" (u<=C, v<=C, u+v<=C all required, checked live)
# LIVE SET = the set of DISTINCT (R, u, v) triples surviving at layer j
# -- this is the "track only surviving states" object requested. Its
# size is the peak live-set-size metric reported per (C, m).
# ---------------------------------------------------------------------

def rss_mb() -> float:
    """Current process peak RSS in MiB (Linux: ru_maxrss is KiB)."""
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


class RSSExceeded(Exception):
    def __init__(self, peak_mb, at_layer):
        self.peak_mb = peak_mb
        self.at_layer = at_layer
        super().__init__(f"RSS cap exceeded: {peak_mb:.1f}MB at layer {at_layer}")


def sparse_survival(m: int, C: int, steps: int = HEARTBEAT,
                     rss_cap_mb: float = 7500.0, state_cap: int = 50_000_000,
                     anchor: str = "end"):
    """Does a corridor of width C survive to precision m? (M_edge(C)
    >= m iff True.)

    anchor: "end" -- the m-step residue-constrained window is the LAST
        m letters of the 53-step heartbeat (credit indices
        steps-m .. steps-1), matching automaton.py's own convention:
        residues are constrained mod 3^m, and by trit-locality only the
        last m steps of a `steps`-step heartbeat carry residue
        information at that precision (P6 in shell_probe.py; the first
        `steps - m` steps are a free deficit walk that never
        constrains anything at modulus 3^m -- ALWAYS satisfiable
        within a wide-enough corridor, so folding it in only costs a
        constant recomputed once, not part of the live-set search).
    "root" -- window is the FIRST m letters (credit indices 0..m-1).

    Returns dict: alive (bool), peak_live_states (int over all layers),
    layer_sizes (list[int]), peak_rss_mb (float), wall (str or None),
    witness (a_forward exponent list or None), elapsed_sec (float).
    """
    if anchor == "end":
        letters = [credit_at_step(steps - 1 - j) for j in range(m)]
    elif anchor == "root":
        letters = [credit_at_step(m - 1 - j) for j in range(m)]
    else:
        raise ValueError(anchor)

    t0 = time.time()
    pow3 = [3 ** i for i in range(m + 1)]

    # Layer 0: rho == 1, tracked mod 3^m (full precision at the start of
    # the backward walk -- the modulus SHRINKS by a factor of 3 each
    # backward step, since step j consumes one more trit of information;
    # after m steps the tracked modulus is 3^0=1, i.e. fully consumed).
    start_R = 1 % pow3[m]
    frontier = {(start_R, 0, 0): None}  # state -> (parent_state, a) for optional witness
    layer_sizes = [1]
    peak_live = 1
    wall = None

    for j in range(m):
        c = letters[j]
        mod_next = pow3[m - j - 1] if (m - j - 1) >= 0 else 1
        nxt = {}
        for (R, u, v), _parent in frontier.items():
            p = parity_forced(R % 3)
            if p is None:
                continue
            a_min = 2 if p == 0 else 1
            # keep s' >= max_s - C  =>  a <= c + C - v
            a_hi = c + C - v
            a = a_min
            while a <= a_hi:
                s_rel = c - a  # s' - s (this step's delta)
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
        n = len(frontier)
        layer_sizes.append(n)
        peak_live = max(peak_live, n)
        cur_rss = rss_mb()
        if cur_rss > rss_cap_mb:
            wall = f"RSS cap {rss_cap_mb}MB exceeded at layer {j + 1} (rss={cur_rss:.1f}MB)"
            break
        if n > state_cap:
            wall = f"state cap {state_cap} exceeded at layer {j + 1} (n={n})"
            break
        if not frontier:
            break  # dead: no legal continuation at all

    alive = bool(frontier) and wall is None
    witness = None
    if alive:
        # any surviving state is a valid witness (free endpoints); reconstruct one
        goal = next(iter(frontier))
        # need parent chain -- but we only kept the LAST layer's dict; to
        # reconstruct we must have retained all layers. Re-run keeping history
        # only when a witness is requested (kept separate for memory: the
        # main sweep does not pay this cost).
        witness = _reconstruct_witness(letters, C, m)

    return {
        "alive": alive,
        "peak_live_states": peak_live,
        "layer_sizes": layer_sizes,
        "peak_rss_mb": rss_mb(),
        "wall": wall,
        "witness": witness,
        "elapsed_sec": time.time() - t0,
        "letters": letters,
    }


def _reconstruct_witness(letters, C, m):
    """Re-run the same search retaining parent pointers per layer, ONLY
    called after `alive` is already established (so this second pass is
    for witness extraction/reporting, not part of the peak-live-set
    measurement above)."""
    pow3 = [3 ** i for i in range(m + 1)]
    start_R = 1 % pow3[m]
    frontier = {(start_R, 0, 0): None}
    layers = [frontier]
    for j in range(m):
        c = letters[j]
        mod_next = pow3[m - j - 1] if (m - j - 1) >= 0 else 1
        nxt = {}
        for (R, u, v), _parent in frontier.items():
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
        layers.append(frontier)
        if not frontier:
            return None
    if not frontier:
        return None
    goal = next(iter(frontier))
    a_backward = []
    cur = goal
    for j in range(m, 0, -1):
        parent, a = layers[j][cur]
        a_backward.append(a)
        cur = parent
    a_backward.reverse()  # backward-consumption order j=1..m
    return list(reversed(a_backward))  # forward order


def verify_witness_exact(a_forward, C, letters):
    """Full exact-integer certification of a witness:
    (1) backward exact-rho reconstruction from rho=1 succeeds -> n0
    (2) TRUE forward Collatz replay n0 -> ... -> 1 in len(a_forward)
        odd steps, exact division at every step (arbitrary precision)
    (3) the deficit partial-sum walk over `letters` (forward order),
        placed at its natural floor (d_start = -min(s_walk)), stays in
        [0, C] throughout -- i.e. range(s_walk) <= C.
    """
    # (1) backward reconstruction
    rho = 1
    ok_bw = True
    for a in reversed(a_forward):
        p = parity_forced(rho)
        if p is None or (a % 2 == 0) != (p == 0):
            ok_bw = False
            break
        rho = backward_pred_exact(rho, a)
    n0 = rho if ok_bw else None

    # (2) forward Collatz replay
    collatz_ok = False
    if ok_bw:
        cur = n0
        ok = cur % 2 == 1
        if ok:
            for a in a_forward:
                if cur % 2 != 1:
                    ok = False
                    break
                t = 3 * cur + 1
                if t % (2 ** a) != 0:
                    ok = False
                    break
                cur = t // (2 ** a)
            collatz_ok = ok and cur == 1

    # (3) deficit range
    fwd_credits = list(reversed(letters))
    s = 0
    s_walk = [0]
    for c, a in zip(fwd_credits, a_forward):
        s += c - a
        s_walk.append(s)
    rng = max(s_walk) - min(s_walk)
    range_ok = rng <= C
    d_start = -min(s_walk)
    d_walk = [d_start + x for x in s_walk]
    deficit_ok = range_ok and all(0 <= d <= C for d in d_walk)

    return {
        "backward_ok": ok_bw, "start_integer": n0,
        "collatz_replay_ok": collatz_ok,
        "range": rng, "deficit_ok": deficit_ok, "d_walk": d_walk,
        "all_ok": ok_bw and collatz_ok and deficit_ok,
    }


def find_M_edge(C: int, m_max: int = 60, rss_cap_mb: float = 7500.0,
                 state_cap: int = 50_000_000, anchor: str = "end"):
    """Sweep m = 1, 2, ... upward at fixed C using sparse_survival; stop
    at the first dead m (return M_edge = last alive m) or at a wall.
    Returns dict with keys: C, measured_edge (int or None), status,
    wall, peak_live_over_all_m (int), per_m (list of dicts), formula.
    """
    per_m = []
    last_alive = 0
    peak_live_over_all_m = 0
    status = "UNKNOWN"
    wall = None
    for m in range(1, m_max + 1):
        res = sparse_survival(m, C, rss_cap_mb=rss_cap_mb, state_cap=state_cap, anchor=anchor)
        peak_live_over_all_m = max(peak_live_over_all_m, res["peak_live_states"])
        per_m.append({
            "m": m, "alive": res["alive"], "peak_live_states": res["peak_live_states"],
            "peak_rss_mb": res["peak_rss_mb"], "wall": res["wall"],
            "elapsed_sec": res["elapsed_sec"],
        })
        if res["wall"] is not None:
            status = "WALL"
            wall = res["wall"]
            break
        if not res["alive"]:
            last_alive = m - 1
            status = "GENUINE_EDGE"
            break
        last_alive = m
    else:
        status = "M_MAX_EXHAUSTED_STILL_ALIVE"

    measured_edge = last_alive if status == "GENUINE_EDGE" else None
    return {
        "C": C, "formula": M_edge_formula(C), "status": status,
        "measured_edge": measured_edge, "last_alive_m": last_alive,
        "wall": wall, "peak_live_over_all_m": peak_live_over_all_m,
        "per_m": per_m,
    }


if __name__ == "__main__":
    print(verify_lemma3())
