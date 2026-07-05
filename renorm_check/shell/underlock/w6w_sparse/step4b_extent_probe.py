#!/usr/bin/env python3
"""
W6W-SPARSE Step 4b -- extent probe after the C=11 break was confirmed
by two independent engines.

Questions:
 (1) Does the C=11 corridor EVER die within the single-heartbeat
     window (m <= 53, the maximum end-anchored window length)? The
     instrument's window is the last m letters of the 53-step
     heartbeat, so m=53 is the construction's own boundary -- beyond
     it, "one heartbeat" no longer contains the window and the
     quantity is undefined without a deeper-anchor extension (the
     E2-class caveat: deeper boundaries unprobed).
 (2) Where do C=12..15 die, if at all, within the window? (Formula
     predicts edges 31, 33, 35, 38.)
 (3) Peak live-set sizes for all of the above (growth-curve output).

Both engines (layered modular BFS from sparse_instrument, exact-int
DFS from step4_independent_rederivation) are run on every cell where
a verdict is recorded; any disagreement is a STOP-and-report bug.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from sparse_instrument import (  # noqa: E402
    sparse_survival, verify_witness_exact, M_edge_formula,
)
from step4_independent_rederivation import (  # noqa: E402
    exists_dfs_exact, end_anchored_letters,
)


def main():
    out = []

    def p(s=""):
        print(s, flush=True)
        out.append(s)

    p("=== W6W-SPARSE Step 4b: extent probe (C=11..15, m up to 53) ===\n")

    for C in [11, 12, 13, 14, 15]:
        formula_C = M_edge_formula(C)
        p(f"--- C={C} (formula predicts M_edge={formula_C}) ---")
        peak_live = 0
        edge = None
        disagreement = None
        last_alive = 0
        for m in range(1, 54):
            res = sparse_survival(m, C, rss_cap_mb=7000.0)
            peak_live = max(peak_live, res["peak_live_states"])
            # cross-check every m >= 28 cell with the second engine
            if m >= 28:
                wit_dfs, _stats = exists_dfs_exact(end_anchored_letters(m), C)
                alive_dfs = wit_dfs is not None
                if alive_dfs != res["alive"]:
                    disagreement = (m, res["alive"], alive_dfs)
                    p(f"  ENGINE DISAGREEMENT at m={m}: BFS={res['alive']} DFS={alive_dfs} -- STOP")
                    break
            if not res["alive"]:
                edge = m - 1
                break
            last_alive = m
        if disagreement:
            p(f"  C={C}: DISAGREEMENT WALL {disagreement} -- verdict withheld")
            continue
        if edge is not None:
            match = (edge == formula_C)
            p(f"  C={C}: DIES at m={edge + 1}; measured_edge={edge} "
              f"formula={formula_C} match={match} peak_live={peak_live}")
        else:
            p(f"  C={C}: ALIVE THROUGH m=53 (the full single-heartbeat window; "
              f"no death observed within the construction's own boundary) "
              f"formula={formula_C} peak_live={peak_live}")
        # verify one witness deep in the window
        probe_m = 53 if edge is None else edge
        res = sparse_survival(probe_m, C, rss_cap_mb=7000.0)
        if res["witness"]:
            v = verify_witness_exact(res["witness"], C, res["letters"])
            p(f"  deep witness (m={probe_m}): all_ok={v['all_ok']} "
              f"n0={v['start_integer']} range={v['range']} "
              f"collatz_replay_ok={v['collatz_replay_ok']}")
        p("")

    (HERE / "step4b_extent_probe.log").write_text("\n".join(out) + "\n")
    p(f"Wrote {HERE / 'step4b_extent_probe.log'}")


if __name__ == "__main__":
    main()
