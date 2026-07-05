#!/usr/bin/env python3
"""
W6Y-REGIME -- Step 2: the extended survival map, C=16..26.

Strategy (honest, stated up front): a full linear sweep of m=1..159 for
every C would restart the O(m)-layer walk at every heartbeat-block
boundary anyway (wy_core.find_edge_for_C already does exactly one walk
per block, cheap), so a linear sweep IS what we run -- but bounded by an
m_max per C chosen to comfortably bracket both the law2 (2-heartbeat)
and law3 (3-heartbeat) candidate edges, not the full 159 for every C
(the scaling probe showed C=25 already takes ~130s just to REACH its
law2 edge with a from-scratch mx_core call at a single m; wy_core's
block walk amortizes this across the whole block so cost is dominated
by the peak live-set size at the END of the swept range, not by m
itself).

Per-C m_max: max(law3_edge(C) + 15, 106 + 10) -- enough past the law2
candidate to see a wrong-direction edge, and enough to span into block 3
(107+) for every C so the 2->3 transition question can be answered
honestly instead of assumed.

RSS/state caps: 7500 MB / 4,000,000 states (matches mx_core/wy_core
defaults, well inside the ~8GB budget). If a cap is hit for a given C,
the sweep for that C stops HONESTLY at the wall and this is reported,
not silently truncated or extrapolated.
"""
from __future__ import annotations
import sys, json, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "w6x_multi"))
import wy_core as wy  # noqa: E402
import mx_core as mx  # noqa: E402

HERE = Path(__file__).parent


def law1(C):
    return (53 * (C + 1)) // 22


def law2(C):
    return (106 * (C + 1)) // 22


def law3(C):
    return (159 * (C + 1)) // 22


def sweep_C(C, rss_cap_mb=7500.0, state_cap=4_000_000, verbose=True):
    m_max = max(law3(C) + 15, 116)
    t0 = time.time()
    r = wy.find_edge_for_C(C, m_max=m_max, rss_cap_mb=rss_cap_mb, state_cap=state_cap, verbose=verbose)
    elapsed = time.time() - t0

    recs = r["records"]
    alive_ms = sorted(m for m, v in recs.items() if v["alive"])
    dead_ms = sorted(m for m, v in recs.items() if not v["alive"])
    last_alive = max(alive_ms) if alive_ms else None
    first_dead_after_last_alive = None
    if last_alive is not None:
        candidates = [m for m in dead_ms if m > last_alive]
        first_dead_after_last_alive = min(candidates) if candidates else None

    # monotonicity check: any dead m followed by a later alive m?
    monotone = True
    revival_at = []
    seen_dead = False
    for m in sorted(recs.keys()):
        if not recs[m]["alive"]:
            seen_dead = True
        elif seen_dead:
            monotone = False
            revival_at.append(m)

    result = {
        "C": C, "m_max_swept": m_max, "law1_edge": law1(C), "law2_edge": law2(C),
        "law3_edge": law3(C), "edge": last_alive, "first_dead": first_dead_after_last_alive,
        "peak_live": r["peak_live"], "wall": r["wall"], "blocks_done": r["blocks_done"],
        "monotone": monotone, "revival_at": revival_at,
        "elapsed_sec": elapsed,
    }
    if verbose:
        print(f"  => C={C}: edge={last_alive} first_dead={first_dead_after_last_alive} "
              f"peak={r['peak_live']} monotone={monotone} wall={r['wall']} "
              f"t={elapsed:.1f}s m_max={m_max}", flush=True)
    return result, recs


def main():
    all_results = []
    all_grids = {}
    for C in range(16, 27):
        print(f"=== C={C} (law1={law1(C)} law2={law2(C)} law3={law3(C)}) ===", flush=True)
        res, recs = sweep_C(C)
        all_results.append(res)
        all_grids[C] = recs
        (HERE / "step2_measurement_partial.json").write_text(
            json.dumps({"results": all_results}, indent=2))
        if res["wall"] is not None:
            print(f"  *** WALL HIT at C={C}: {res['wall']} -- stopping honestly ***", flush=True)
            break

    (HERE / "step2_measurement_full.json").write_text(
        json.dumps({"results": all_results, "grids": {str(k): v for k, v in all_grids.items()}}, indent=2))

    # summary CSV
    with open(HERE / "step2_edges_table.csv", "w") as f:
        f.write("C,law1_edge,law2_edge,law3_edge,edge,first_dead,peak_live,monotone,revival_at,wall,elapsed_sec\n")
        for res in all_results:
            f.write(f"{res['C']},{res['law1_edge']},{res['law2_edge']},{res['law3_edge']},"
                    f"{res['edge']},{res['first_dead']},{res['peak_live']},{res['monotone']},"
                    f"\"{res['revival_at']}\",\"{res['wall']}\",{res['elapsed_sec']:.2f}\n")

    print("\n=== SUMMARY ===")
    for res in all_results:
        print(res)


if __name__ == "__main__":
    main()
