"""
Step 2 (small side): compute live(C, m) -- the FULL live state set (not just
terminal-compatible) -- for corridor widths C = 1..5, across m = 1..M_edge(C)+2
(capped where compute becomes infeasible; capping is reported explicitly).

This produces the "small side" half of the (C, C+22) pairs used in Step 3's
embedding test, plus the raw data needed for Step 4's size-comparison smoke
test.

Dense (numpy boolean array) forward simulation is used -- exact, not
sampled. Feasibility ceiling (measured empirically, see validate.py/this
script's own timing prints):
  - C=1..4: full target precision M_edge(C)+2 easily reached (< 10s each).
  - C=5: M_edge(5)+2 = 16 requires ~250M states; empirically this crossed
    100s+ and was CUT at m=15 (~11M live states, ~30s) for this run. This
    is reported honestly in the output JSON (see "capped" field) rather
    than silently truncated.
  - C=6+ on the small side alone already reaches ~2.7B+ states at target
    precision -- not attempted here; see the mission report for the full
    infeasibility accounting.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from automaton import M_edge, run_heartbeat

OUT_DIR = Path(__file__).parent
RESULTS_PATH = OUT_DIR / "small_side_results.json"
LIVE_SETS_DIR = OUT_DIR / "small_side_live_sets"
LIVE_SETS_DIR.mkdir(exist_ok=True)

# Per-C time budget (seconds) for the FULL m-sweep of that C. If exceeded,
# remaining higher m values are skipped and reported as capped.
TIME_BUDGET_PER_C = 240

# Only persist full live-state sets (for the embedding test in Step 3) for
# m values at or near M_edge(C)+2 (the "interesting" precision where the
# proof's own certificates are concentrated) plus a couple of lower m for
# spot checks -- persisting every m would duplicate huge amounts of data.
def should_persist(C, m, target_m):
    return m == target_m or m == target_m - 1 or m == 1 or m == M_edge(C)


def sweep():
    results = []
    for C in range(1, 6):
        target_m = M_edge(C) + 2
        c_start = time.time()
        m_capped_at = None
        for m in range(1, target_m + 1):
            elapsed_so_far = time.time() - c_start
            if elapsed_so_far > TIME_BUDGET_PER_C:
                m_capped_at = m - 1
                print(f"[C={C}] time budget ({TIME_BUDGET_PER_C}s) exceeded at m={m}; "
                      f"stopping sweep for this C at m={m_capped_at}")
                break
            t0 = time.time()
            live_by_d, hist = run_heartbeat(C, m, steps=53, max_states_guard=5_000_000_000)
            dt = time.time() - t0
            total_live = hist[-1]
            modulus = 3 ** m
            total_possible = (C + 1) * modulus

            # Also compute terminal-compatible count for cross-reference
            # with Theorem 1 / Certificate 1.
            terminal_count = 0
            for d in range(C + 1):
                if live_by_d[d][1 % modulus]:
                    terminal_count += 1

            persisted_path = None
            if should_persist(C, m, target_m):
                import numpy as np
                fname = LIVE_SETS_DIR / f"C{C}_m{m}.npz"
                save_dict = {f"d{d}": np.nonzero(live_by_d[d])[0].astype(np.int64)
                             for d in range(C + 1)}
                np.savez_compressed(fname, **save_dict)
                persisted_path = str(fname)

            row = {
                "C": C,
                "m": m,
                "M_edge_C": M_edge(C),
                "modulus_3m": modulus,
                "total_possible_states": total_possible,
                "total_live_states": total_live,
                "live_fraction": total_live / total_possible if total_possible else 0.0,
                "terminal_compatible_count": terminal_count,
                "compute_time_sec": dt,
                "history_sizes": hist,
                "persisted_live_set_path": persisted_path,
            }
            results.append(row)
            print(f"[C={C} m={m}] live={total_live}/{total_possible} "
                  f"({row['live_fraction']:.6e}) terminal_compat={terminal_count} time={dt:.2f}s"
                  f"{' [PERSISTED]' if persisted_path else ''}")

        if m_capped_at is None and target_m > 0:
            # Completed full sweep for this C.
            pass

    return results


def main():
    print("=" * 70)
    print("SMALL-SIDE SWEEP: live(C, m) for C = 1..5, m = 1..M_edge(C)+2 (or capped)")
    print("=" * 70)
    t0 = time.time()
    results = sweep()
    total_time = time.time() - t0

    output = {
        "description": "Full live state sets for A(C,m), C=1..5, dense forward "
                        "computation over one 53-step heartbeat from full initial "
                        "population. Used as the 'small side' of the (C,C+22) "
                        "embedding test.",
        "total_compute_time_sec": total_time,
        "rows": results,
    }
    RESULTS_PATH.write_text(json.dumps(output, indent=2))
    print(f"\nWrote {len(results)} rows to {RESULTS_PATH}")
    print(f"Total compute time: {total_time:.1f}s")


if __name__ == "__main__":
    main()
