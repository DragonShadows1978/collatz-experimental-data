#!/usr/bin/env python3
"""
W6X-MULTI -- core instrument: multi-heartbeat extension of
w6w_sparse/sparse_instrument.py's backward live-set walk.

Mechanically this is EXACTLY sparse_instrument.py's layered modular
BFS (see that file's own docstring for the full derivation -- not
re-derived here, reused as validated), generalized ONLY in how the
`letters` window is built for m > 53 (one or more heartbeat
boundaries). No transition-math changes, no state reset at k=53: the
per-layer update is identical whether m <= 53 or m > 53; only the
absolute step indices feeding `credit_at_step` differ. See
DESIGN_NOTES.md in this directory for the full reasoning, in
particular the two-reading anchor ambiguity for m > 53.

Both end-anchor readings for m > 53 are implemented and exposed as
`reading="A"` / `reading="B"`:
  A ("growing end-anchor", == root anchor): window = absolute indices
    [0, m). letters[j] = credit_at_step(m - 1 - j).
  B ("heartbeat-periodic re-anchoring"): window = last m letters
    ending at anchor_end(m) = 53 * ceil(m/53).
    letters[j] = credit_at_step(anchor_end(m) - 1 - j).
For m <= 53, reading B reduces EXACTLY to sparse_instrument.py's
"end" anchor (anchor_end=53 always); reading A reduces exactly to its
"root" anchor. Both are cross-checked against the original module in
step1_validation_gates.py.

These per-layer transition primitives (parity_forced,
backward_pred_exact, backward_pred_mod, the (R,u,v) live-set update
rule) are intentionally the SAME validated math as
w6w_sparse/sparse_instrument.py -- reused, not reinvented, because
this round's question is entirely about the window/anchor
construction past m=53, not about the per-step transition rule (which
w6w_sparse already gated exhaustively). Only `letters_for()` and the
multi-heartbeat plumbing around it are new.

Exact arithmetic only: Python arbitrary-precision ints throughout the
search and witness-verification path. No floats/numpy in the
arithmetic path (numpy/float confined to read-only dense cross-checks
elsewhere, not used at this scale anyway since m > 20ish is already
dense-infeasible).
"""
from __future__ import annotations

import resource
import time
from pathlib import Path

HERE = Path(__file__).parent

HEARTBEAT = 53
SUPPORT_COUNT = 22
DROP_COUNT = 31


# ---------------------------------------------------------------------
# Credit sequence -- exact integer, valid for ANY k >= 0 (no periodicity
# assumed or required; Sturmian word driven by log2(3) irrationality).
# ---------------------------------------------------------------------

def floor_k_log2_3(k: int) -> int:
    """floor(k * log2(3)) exactly, via bit_length(3**k). No floats."""
    if k == 0:
        return 0
    return (3 ** k).bit_length() - 1


def credit_at_step(k: int) -> int:
    """Sturmian credit c_k (0-indexed): c_k = floor((k+1)log2 3) - floor(k log2 3)."""
    return floor_k_log2_3(k + 1) - floor_k_log2_3(k)


def M_edge_formula(C: int) -> int:
    """Closed-form one-heartbeat capacity law: floor(53*(C+1)/22)."""
    return (53 * (C + 1)) // 22


# ---------------------------------------------------------------------
# Anchor window construction -- THE generalization under test.
# ---------------------------------------------------------------------

def letters_for(m: int, reading: str, steps: int = HEARTBEAT):
    """Build the m-letter backward-consumption window (letters[j] is the
    credit letter consumed at backward layer j, j=0..m-1; layer 0 is
    closest to the terminal r=1).

    reading == "end"  : original one-heartbeat frame, ONLY valid for
                         m <= steps (steps fixed, e.g. 53). window =
                         [steps-m, steps).
    reading == "root" : window = [0, m). (valid for any m; identical
                         to reading "A" for all m, kept for direct
                         cross-check against sparse_instrument.py.)
    reading == "A"    : growing end-anchor, window = [0, m), any m.
                         letters[j] = credit_at_step(m-1-j).
    reading == "B"    : heartbeat-periodic re-anchoring. anchor_end =
                         steps * ceil(m/steps). window =
                         [anchor_end-m, anchor_end).
                         letters[j] = credit_at_step(anchor_end-1-j).
                         Reduces EXACTLY to "end" for m <= steps.
    """
    if reading == "end":
        if m > steps:
            raise ValueError(f"'end' anchor only valid for m<=steps={steps}, got m={m}")
        return [credit_at_step(steps - 1 - j) for j in range(m)]
    if reading in ("root", "A"):
        return [credit_at_step(m - 1 - j) for j in range(m)]
    if reading == "B":
        anchor_end = steps * -(-m // steps)  # steps * ceil(m/steps)
        return [credit_at_step(anchor_end - 1 - j) for j in range(m)]
    raise ValueError(f"unknown reading {reading!r}")


# ---------------------------------------------------------------------
# Backward step primitives -- same validated transition math as
# sparse_instrument.py (this round changes the window, not the step).
# ---------------------------------------------------------------------

def parity_forced(rho: int):
    """rho mod 3 forces the parity of the NEXT (backward) exponent a
    in the step rho' = (2^a * rho - 1) / 3 (exact division required).
    rho%3==0 -> dead (no legal a). rho%3==1 -> a even. rho%3==2 -> a odd."""
    cls = rho % 3
    if cls == 0:
        return None
    return 0 if cls == 1 else 1  # 0 = "a even", 1 = "a odd"


def backward_pred_exact(rho: int, a: int) -> int:
    """rho' = (2^a * rho - 1) / 3, EXACT integer division."""
    num = (1 << a) * rho - 1
    assert num % 3 == 0, "parity precondition violated"
    return num // 3


def backward_pred_mod(R: int, a: int, mod_next: int) -> int:
    """Same transition tracking rho only mod mod_next."""
    if mod_next <= 1:
        return 0
    num = (1 << a) * R - 1
    assert num % 3 == 0, "parity precondition violated (mod variant)"
    return (num // 3) % mod_next


# ---------------------------------------------------------------------
# RSS watchdog
# ---------------------------------------------------------------------

def rss_mb() -> float:
    """Current process peak RSS in MiB (Linux: ru_maxrss is KiB)."""
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


class RSSExceeded(Exception):
    def __init__(self, peak_mb, at_layer):
        self.peak_mb = peak_mb
        self.at_layer = at_layer
        super().__init__(f"RSS cap exceeded: {peak_mb:.1f}MB at layer {at_layer}")


# ---------------------------------------------------------------------
# Sparse backward live-set search, generalized to arbitrary m (multi-
# heartbeat), both anchor readings.
# ---------------------------------------------------------------------

def sparse_survival_multi(m: int, C: int, reading: str = "B",
                           steps: int = HEARTBEAT,
                           rss_cap_mb: float = 7500.0,
                           state_cap: int = 50_000_000,
                           want_witness: bool = True):
    """Does a corridor of width C survive to precision m, under the
    given anchor `reading` ("end"/"root"/"A"/"B")? Returns dict with
    alive, peak_live_states, layer_sizes, peak_rss_mb, wall, witness,
    elapsed_sec, letters, final_live_sample (small sample of the final
    live-set keys for residue-structure inspection).
    """
    letters = letters_for(m, reading, steps=steps)

    t0 = time.time()
    pow3 = [3 ** i for i in range(m + 1)]

    start_R = 1 % pow3[m]
    frontier = {(start_R, 0, 0): None}
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
    final_live_sample = list(frontier.keys())[:2000] if alive else []
    if alive and want_witness:
        witness = _reconstruct_witness(letters, C, m)

    return {
        "alive": alive,
        "peak_live_states": peak_live,
        "final_live_states": len(frontier) if wall is None else None,
        "layer_sizes": layer_sizes,
        "peak_rss_mb": rss_mb(),
        "wall": wall,
        "witness": witness,
        "elapsed_sec": time.time() - t0,
        "letters": letters,
        "final_live_sample": final_live_sample,
        "reading": reading,
        "m": m, "C": C,
    }


def _reconstruct_witness(letters, C, m):
    """Re-run the search retaining parent pointers per layer (only
    called once `alive` is established -- second pass, witness
    extraction only, not part of the peak-live-set measurement)."""
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
    a_backward.reverse()
    return list(reversed(a_backward))


def verify_witness_exact(a_forward, C, letters):
    """Full exact-integer certification of a witness:
    (1) backward exact-rho reconstruction from rho=1 succeeds -> n0
    (2) TRUE forward Collatz replay n0 -> ... -> 1, exact division
        at every step (arbitrary precision)
    (3) deficit partial-sum walk over `letters` (forward order),
        placed at its natural floor, stays in [0, C] throughout.
    """
    rho = 1
    ok_bw = True
    for a in reversed(a_forward):
        p = parity_forced(rho)
        if p is None or (a % 2 == 0) != (p == 0):
            ok_bw = False
            break
        rho = backward_pred_exact(rho, a)
    n0 = rho if ok_bw else None

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


def verify_lemma3(steps: int = HEARTBEAT) -> dict:
    seq = [credit_at_step(k) for k in range(steps)]
    return {
        "support_count": seq.count(1),
        "drop_count": seq.count(2),
        "total": len(seq),
        "matches_lemma3": seq.count(1) == 22 and seq.count(2) == 31,
    }


if __name__ == "__main__":
    print(verify_lemma3())
