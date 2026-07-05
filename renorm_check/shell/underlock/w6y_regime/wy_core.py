#!/usr/bin/env python3
"""
W6Y-REGIME -- extended instrument, built directly on mx_core.py (imported,
not copied -- the per-layer transition math, letters_for() construction,
and witness verification are validated already and reused unmodified).

DESIGN NOTE / TWO BUGS FOUND AND FIXED IN THIS ROUND, reported honestly:

Bug 1 (v1): tried to track rho only MODULO 3^(m_end - j - 1) (a fixed
modulus derived from the block's final m_end) so a single continuous
walk could report live-set sizes at every intermediate checkpoint
m < m_end cheaply. WRONG: the correct modulus at layer j for a target
precision m is 3^(m - j - 1) (see mx_core.sparse_survival_multi), which
depends on the CHECKPOINT's own m, not a fixed m_end.

Bug 2 (v2, the naive "fix"): switched to tracking rho EXACTLY (no
truncation at all) and deduped states by (exact_rho, u, v). This gives
CORRECT alive/dead decisions (0 mismatches vs mx_core on that axis) but
WRONG live-set COUNTS -- inflated relative to mx_core's modular counts.
Root cause, found by direct frontier inspection (C=4, m=3): mx_core's
`mod_next = 3^(m-j-1)` becomes 3^0 = 1 at the terminal layer, so its R
is trivially 0 for EVERY state there -- mx_core's states at m=3 are
distinguished ONLY by (u,v) (4 distinct (u,v) pairs at C=4,m=3, e.g.
(0,4) appears once). The exact-rho engine instead keeps rho values 13
and 17 as SEPARATE states even though both have (u,v)=(0,4) -- both are
genuine distinct integers/backward branches, but mx_core's modular
abstraction is the mathematically correct "minimal sufficient
statistic" for FUTURE legality (rho mod 3^(m-j-1) is exactly what
matters for whether the remaining j..m-1 layers can be completed) and
correctly merges them; exact-rho does not merge and so over-counts
"live states" relative to what mx_core (and W6X-MULTI's peak-live-set
numbers) actually measure. This was caught by
step1b_wycore_gate.py's count-mismatch check (count mismatches at C>=4,
identical failure pattern before and after switching to exact rho --
a red flag that should have been (and was, on reflection) obvious: the
same numbers recurring means the "fix" didn't change the mechanism
that mattered).

REAL FIX (final-live-state count, i.e. the count AT a checkpoint m):
track rho EXACTLY through the walk (so no information is ever lost),
and at EACH checkpoint m, re-key the current exact frontier by
(exact_rho mod 3^(m - j - 1), u, v) -- i.e. apply mx_core's own correct
per-checkpoint modulus as a READOUT-time reduction over the live exact
frontier, not as the walk's own state key. mx_core's mod_next at the
FINAL layer of any m-call is always 3^0=1 (m-(m-1)-1=0 identically),
confirmed both algebraically and by direct mx_core inspection, so the
final-live-state readout at any checkpoint m reduces to dedup by (u,v)
alone. Cross-checked against mx_core after this fix: 0 mismatches,
alive/dead AND final live-set count, C=1..15, m=1..90 spanning the
heartbeat-2 boundary (step1b_wycore_gate.py log).

SEPARATE ISSUE for `peak_live` (the PEAK across all intermediate
layers, mx_core's `peak_live_states`): this is NOT the same object as
the final-checkpoint count above -- mx_core computes it by truncating
to mod 3^(m-j-1) AT EVERY layer j for that call's OWN target m, so
"peak across layers" is itself m-dependent (a different modulus
schedule for every different m). Recomputing this exactly for every
requested checkpoint from one exact-rho walk would cost O(checkpoints x
layers x frontier size) if done naively. Empirical resolution, checked
directly (not assumed): for every C tested (11..15, m=53), the true
peak (per mx_core's own layer_sizes) occurs at a SHALLOW layer
(layer index 12-19 of 53-54 total) where the modulus is still
astronomically large (>10^9, versus frontier sizes in the hundreds to
low thousands) -- i.e. the peak always occurs in the region where
modular truncation has NOT YET started merging any states (no
collision is even possible when the modulus vastly exceeds the number
of distinct reachable rho values). In that regime, the EXACT frontier
size at a layer IS the true modular frontier size at that layer (no
merging occurs either way). Therefore `peak_live` in this module is computed as
the max EXACT frontier size over all layers -- verified equal to
mx_core's own `peak_live_states` at every gated C (see
step1b_wycore_gate.py's peak cross-check). This is not a proof it holds
at all C -- it is an empirical regularity (peak precedes truncation)
checked at every cell this round actually visits, flagged honestly as
an assumption if any single-cell audit later disagrees.
"""
from __future__ import annotations

import sys
import time
import resource
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "w6x_multi"))
import mx_core as mx  # noqa: E402

HEARTBEAT = mx.HEARTBEAT  # 53


def rss_mb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def block_of(m: int) -> int:
    """Which heartbeat block (1-indexed) does m fall in? m in ((h-1)*53, h*53]."""
    return -(-m // HEARTBEAT)  # ceil(m/53)


def _readout_count(frontier_exact, m_now, j_next):
    """Re-key the current EXACT frontier by mx_core's own modulus for
    checkpoint m_now (mod_next = 3^(m_now - j_next - 1) at the layer
    just completed, j_next = m_now here since we've consumed layers
    0..m_now-1) and return the number of DISTINCT (rho mod that
    modulus, u, v) triples -- i.e. exactly mx_core's live-set count
    definition, applied post-hoc to a strictly finer exact partition.
    j_next passed as m_now (all m_now layers consumed, next modulus is
    for a hypothetical next layer at m=m_now, matching mx_core's
    mod_next computed as pow3[m-j-1] with j=m_now-1 -> m-j-1 = m_now -
    (m_now-1) - 1 = 0 when m==m_now, i.e. mx_core's OWN readout modulus
    for "the live set AFTER consuming all of an m_now-layer window" is
    3^0=1 -- checked directly against mx_core.sparse_survival_multi's
    final_live_states below in the validation gate, which loops m=1..M
    calling mx_core fresh each time (m_now IS that call's m, so its
    OWN final mod_next at the last layer is always 3^(m_now-(m_now-1)-1)=3^0=1).
    """
    mod = 1  # matches mx_core: at the final consumed layer for window
    # width m_now, mod_next = 3**(m_now - (m_now-1) - 1) = 3**0 = 1 always.
    seen = set()
    for (rho, u, v) in frontier_exact:
        seen.add((rho % mod, u, v))
    return len(seen)


def walk_block_exact(C: int, block: int, m_end: int,
                      rss_cap_mb: float = 7500.0, state_cap: int = 4_000_000,
                      checkpoints=None):
    """Walk j = 0..m_end-1 within ONE heartbeat block (anchor_end =
    53*block, fixed throughout the block since m<=53*block here), using
    EXACT big-int rho (no modular truncation) as the search's own state
    key (so alive/dead is decided correctly and independently of any
    modulus choice -- a genuinely different engine from mx_core's
    modular BFS). At each requested checkpoint m, the live-set COUNT is
    read out by re-keying the current exact frontier with mx_core's own
    per-checkpoint modulus (see _readout_count and module docstring for
    the bug this fixes) -- this reproduces mx_core's count definition
    exactly, verified in step1b_wycore_gate.py.
    """
    anchor_end = HEARTBEAT * block
    assert m_end <= anchor_end, f"m_end={m_end} must be <= anchor_end={anchor_end} for block {block}"
    checkpoints = set(checkpoints) if checkpoints is not None else set(range(1, m_end + 1))

    frontier = {(1, 0, 0): None}  # exact rho=1, no truncation ever
    records = {}
    peak = 1
    wall = None

    t0 = time.time()
    for j in range(m_end):
        m_now = j + 1
        c = mx.credit_at_step(anchor_end - 1 - j)
        nxt = {}
        for (rho, u, v), _parent in frontier.items():
            p = mx.parity_forced(rho % 3)
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
                    rho2 = mx.backward_pred_exact(rho, a)
                    key2 = (rho2, u2, v2)
                    if key2 not in nxt:
                        nxt[key2] = ((rho, u, v), a)
                a += 2
        frontier = nxt
        n_exact = len(frontier)
        # peak tracked via EXACT frontier size at every layer (see module
        # docstring: verified equal to mx_core's true modular peak
        # whenever the peak precedes truncation onset, which held at
        # every gated cell).
        peak = max(peak, n_exact)
        if m_now in checkpoints:
            n = _readout_count(frontier.keys(), m_now, j + 1) if frontier else 0
            records[m_now] = {"alive": bool(frontier), "live_count": n, "peak_so_far": peak}
        cur_rss = rss_mb()
        if cur_rss > rss_cap_mb:
            wall = f"RSS cap {rss_cap_mb}MB exceeded at m={m_now} (rss={cur_rss:.1f}MB, exact-states={n_exact})"
            break
        if n_exact > state_cap:
            wall = f"state cap {state_cap} exceeded at m={m_now} (n_exact={n_exact})"
            break
        if not frontier:
            for m_rem in sorted(c2 for c2 in checkpoints if c2 > m_now):
                records[m_rem] = {"alive": False, "live_count": 0, "peak_so_far": peak}
            break

    elapsed = time.time() - t0
    return {
        "block": block, "anchor_end": anchor_end, "records": records,
        "peak_live": peak, "wall": wall, "elapsed_sec": elapsed,
        "final_rss_mb": rss_mb(), "final_frontier_size": len(frontier),
    }


def find_edge_for_C(C: int, m_max: int = 159, rss_cap_mb: float = 7500.0,
                     state_cap: int = 4_000_000, verbose=True):
    """Sweep m = 1..m_max for a single C, block by block (fresh walk at
    each heartbeat-block boundary since the anchor jumps -- Reading B
    only, the pre-registered primary reading). Every m in 1..m_max is a
    checkpoint (we want the exact edge, not a sampled grid).

    Death-persistence across block boundaries is NOT assumed -- each
    new block starts its own exact-rho walk from rho=1 at its own
    anchor_end, so a "revival" at a new anchor (as Reading A shows) IS
    detectable in principle; Reading B's prior monotonicity (C<=15) is
    checked, not presumed, by simply reporting records for the full
    swept range.
    """
    all_records = {}
    peak_overall = 0
    wall = None
    last_block_done = 0
    t0 = time.time()
    n_blocks = block_of(m_max)
    for block in range(1, n_blocks + 1):
        m_lo = (block - 1) * HEARTBEAT + 1
        m_hi = min(block * HEARTBEAT, m_max)
        r = walk_block_exact(C, block, m_hi, rss_cap_mb=rss_cap_mb, state_cap=state_cap,
                              checkpoints=range(m_lo, m_hi + 1))
        all_records.update(r["records"])
        peak_overall = max(peak_overall, r["peak_live"])
        last_block_done = block
        if verbose:
            print(f"    C={C} block={block} (m={m_lo}..{m_hi}) peak_this_block={r['peak_live']} "
                  f"wall={r['wall']} elapsed={r['elapsed_sec']:.2f}s rss={r['final_rss_mb']:.1f}MB", flush=True)
        if r["wall"] is not None:
            wall = r["wall"]
            break
    elapsed = time.time() - t0
    return {
        "C": C, "records": all_records, "peak_live": peak_overall,
        "wall": wall, "elapsed_sec": elapsed, "blocks_done": last_block_done,
    }
