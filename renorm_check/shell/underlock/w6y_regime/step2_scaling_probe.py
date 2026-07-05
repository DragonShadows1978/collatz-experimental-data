#!/usr/bin/env python3
"""
W6Y-REGIME -- Step 2 probe: cheap scaling check before the full sweep.

For each C=16..26, find the candidate edge from the 2-heartbeat law
floor(106*(C+1)/22) and floor(159*(C+1)/22), and measure peak live-set
size and wall time at a handful of m values to sanity-check the ~x1.7
per-C growth claim and decide a safe m-range / state cap for the real
sweep, honestly, before committing to a long run.
"""
from __future__ import annotations
import sys, time, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "w6x_multi"))
import mx_core as mx  # noqa: E402

HERE = Path(__file__).parent


def law2(C):
    return (106 * (C + 1)) // 22


def law3(C):
    return (159 * (C + 1)) // 22


def probe():
    print("C, law2_edge, law3_edge, peak@law2_edge, time@law2_edge(s), rss_mb", flush=True)
    rows = []
    for C in range(16, 27):
        e2 = law2(C)
        t0 = time.time()
        r = mx.sparse_survival_multi(e2, C, reading="B", want_witness=False,
                                      rss_cap_mb=7500.0, state_cap=2_000_000)
        dt = time.time() - t0
        row = dict(C=C, law2_edge=e2, law3_edge=law3(C),
                   peak_live=r["peak_live_states"], alive=r["alive"],
                   wall=dt, rss_mb=r["peak_rss_mb"], wall_flag=r["wall"])
        rows.append(row)
        print(f"C={C:2d} e2={e2:3d} e3={row['law3_edge']:3d} peak={r['peak_live_states']:>8d} "
              f"alive={r['alive']} t={dt:6.2f}s rss={r['peak_rss_mb']:.1f}MB wall={r['wall']}", flush=True)
        (HERE / "step2_scaling_probe.json").write_text(json.dumps(rows, indent=2))
        if dt > 60 or (r["wall"] is not None):
            print(f"  -> stopping probe early at C={C}: too slow or wall hit", flush=True)
            break
    # growth ratio
    print("\nGrowth ratios peak_live[C]/peak_live[C-1]:")
    for i in range(1, len(rows)):
        prev, cur = rows[i-1]["peak_live"], rows[i]["peak_live"]
        ratio = cur / prev if prev else float("nan")
        print(f"  C={rows[i]['C']}: {cur} / {prev} = {ratio:.3f}")


if __name__ == "__main__":
    probe()
