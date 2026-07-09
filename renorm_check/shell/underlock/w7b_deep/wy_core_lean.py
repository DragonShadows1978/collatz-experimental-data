#!/usr/bin/env python3
"""
W7B-DEEP -- lean-representation variant of ../w6y_regime/wy_core.py.

Built for the C>=27 high-capacity sweep (W7B_ORDER.md). wy_core.py's
find_edge_for_C/walk_block_exact are validated and correct through C=26,
but their survivor-set representation is a dict keyed by the full
(rho_exact, u, v) tuple, valued by a full parent tuple + branch int
((rho, u, v), a). Measured at C=22 (peak_live=186128, shallow depth
m<=53, rho still small): ~554 bytes/state via direct RSS delta
(baseline 11.3MB -> 114.4MB after the walk, 103.1MB / 186128 states).

That value is redundant for this instrument's purpose: walk_block_exact
is called ONLY to measure peak_live / final live-set counts / alive-dead
(see find_edge_for_C and step2_measurement.py -- no caller ever reads
the parent chain off a walk_block_exact/find_edge_for_C result). Witness
reconstruction is a wholly separate pass (witness_bounded.py / mx_core's
own _reconstruct_witness), run only after death/life is established, at
low m, from scratch. So the parent pointer stored on every one of
millions of live states is pure waste for this measurement task: it
duplicates a second full (rho, u, v) tuple (via the parent key) plus an
`a` int, for a fact nothing downstream of this module ever consumes.

Fix: represent the frontier as a bare `set` of (rho, u, v) tuples (dedup
IS the operation we need -- a dict was never buying us anything here
except the discarded parent pointer). No change to any transition math,
modulus logic, or the (u, v) corridor-deficit rule -- byte-for-byte the
same walk, just without recording where each state came from.

Everything else (parity_forced, backward_pred_exact, credit_at_step,
block_of, _readout_count's modulus logic) is reused UNMODIFIED from
mx_core / wy_core (imported, not copied) -- this file only overrides
walk_block_exact and find_edge_for_C.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "w6y_regime"))
sys.path.insert(0, str(Path(__file__).parent.parent / "w6x_multi"))
import wy_core as wy  # noqa: E402 -- reuse credit_at_step, block_of, _readout_count, HEARTBEAT, rss_mb
import mx_core as mx  # noqa: E402 -- reuse parity_forced, backward_pred_exact, credit_at_step

HEARTBEAT = wy.HEARTBEAT
rss_mb = wy.rss_mb
block_of = wy.block_of
_readout_count = wy._readout_count


def walk_block_exact(C: int, block: int, m_end: int,
                      rss_cap_mb: float = 7500.0, state_cap: int = 4_000_000,
                      checkpoints=None):
    """Same transition math as wy_core.walk_block_exact (see that
    module's docstring for the two-bug history / correctness argument
    behind exact-rho tracking -- reused unmodified here), with ONE
    representational change: the frontier is a bare `set` of
    (rho, u, v) triples instead of a `dict` mapping each triple to a
    parent pointer + branch int. No caller of walk_block_exact /
    find_edge_for_C anywhere in w6y_regime or w7a_renorm ever reads a
    parent chain off the result (checked directly), so the parent
    pointer was pure overhead for this measurement task.
    """
    anchor_end = HEARTBEAT * block
    assert m_end <= anchor_end, f"m_end={m_end} must be <= anchor_end={anchor_end} for block {block}"
    checkpoints = set(checkpoints) if checkpoints is not None else set(range(1, m_end + 1))

    frontier = {(1, 0, 0)}  # exact rho=1, no truncation ever -- bare set, no parent pointer
    records = {}
    peak = 1
    wall = None

    t0 = time.time()
    for j in range(m_end):
        m_now = j + 1
        c = mx.credit_at_step(anchor_end - 1 - j)
        nxt = set()
        for (rho, u, v) in frontier:
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
                    nxt.add((rho2, u2, v2))
                a += 2
        frontier = nxt
        n_exact = len(frontier)
        peak = max(peak, n_exact)
        if m_now in checkpoints:
            n = _readout_count(frontier, m_now, j + 1) if frontier else 0
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
    """Same driver logic as wy_core.find_edge_for_C, calling this
    module's lean walk_block_exact instead."""
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


if __name__ == "__main__":
    pass
