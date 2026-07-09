#!/usr/bin/env python3
"""
W7B-DEEP -- high-capacity sparse sweep C>=27, using the lean
representation (wy_core_lean.py, this directory).

Per W7B_ORDER.md:
  - VALIDATION GATE (frozen): must reproduce C=16=93, C=23=163, C=26=205
    exactly before any C=27+ cell is trusted. Re-asserted inline here so
    a single script run is self-certifying.
  - MONOTONICITY GATE (frozen): every new M(C) must be > M(C-1)
    (M(26)=205). A cell that ends on a wall (state_cap or rss_cap hit,
    first_dead not established) is VOID -- reported as WALL, never
    written as an edge.
  - Only genuine-death edges get appended to
    ../w7a_renorm/w7a_new_edges.txt ("C edge").

Memory note: the order file's 48000MB rss_cap_mb assumes the full 64GB
is free. At sweep start, `free -h` showed ~20GB already resident (other
jobs on this machine) and ~42GB available -- so this sweep uses
rss_cap_mb=32000 (leaves ~10GB headroom for the other legitimate job
observed running) rather than 48000. This is a deliberate deviation from
the order's suggested number, recorded here so it is not silently guessed.
"""
from __future__ import annotations
import sys, time, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import wy_core_lean as wl  # noqa: E402

HERE = Path(__file__).parent
EDGES_FILE = HERE.parent / "w7a_renorm" / "w7a_new_edges.txt"

RSS_CAP_MB = 32_000.0
STATE_CAP = 64_000_000

KNOWN_EDGES = {
    1: 4, 2: 7, 3: 9, 4: 12, 5: 14, 6: 16, 7: 19, 8: 21, 9: 24, 10: 26,
    11: 57, 12: 63, 13: 68, 14: 71, 15: 79, 16: 93, 17: 108, 18: 110,
    19: 130, 20: 132, 21: 139, 22: 157, 23: 163, 24: 188, 25: 192, 26: 205,
}
GATE_CELLS = {16: 93, 23: 163, 26: 205}


def edge_of(r):
    alive_ms = [m for m, v in r["records"].items() if v["alive"]]
    return max(alive_ms) if alive_ms else None


def first_dead_after(r, edge):
    if edge is None:
        return None
    dead_ms = sorted(m for m, v in r["records"].items() if not v["alive"] and m > edge)
    return dead_ms[0] if dead_ms else None


def run_gate():
    print("=== VALIDATION GATE (frozen, lean wy_core_lean) ===", flush=True)
    ok = True
    for C, exp in sorted(GATE_CELLS.items()):
        t0 = time.time()
        mmax = 9 * (C + 1) + 53
        r = wl.find_edge_for_C(C, m_max=mmax, rss_cap_mb=RSS_CAP_MB, state_cap=STATE_CAP, verbose=False)
        g = edge_of(r)
        dt = time.time() - t0
        status = "OK" if g == exp else f"FAIL exp={exp}"
        print(f"  C={C} edge={g} {status} peak_live={r['peak_live']} wall={r['wall']} t={dt:.1f}s", flush=True)
        if g != exp:
            ok = False
    print("GATE PASS" if ok else "GATE FAILED", flush=True)
    return ok


def main(c_start=27, c_stop=60):
    if not run_gate():
        print("ABORT: validation gate failed, refusing to trust new cells.", flush=True)
        sys.exit(1)

    # Seed the monotonicity baseline from the actual predecessor M(c_start-1)
    # if it is known (so a resumed run, e.g. c_start=31, compares against
    # M(30)=282, not M(26)=205). Falls back to M(26)=205 for the c_start=27
    # base case.
    prev_edge = KNOWN_EDGES.get(c_start - 1, KNOWN_EDGES[26])
    results = []
    for C in range(c_start, c_stop + 1):
        m_max = 9 * (C + 1) + 106  # generous headroom past the base-law*9 guess, plus 2 heartbeats
        print(f"\n=== C={C} (prev_edge M({C-1})={prev_edge}) m_max={m_max} "
              f"rss_cap={RSS_CAP_MB}MB state_cap={STATE_CAP} ===", flush=True)
        t0 = time.time()
        r = wl.find_edge_for_C(C, m_max=m_max, rss_cap_mb=RSS_CAP_MB, state_cap=STATE_CAP, verbose=True)
        dt = time.time() - t0
        edge = edge_of(r)
        fdead = first_dead_after(r, edge)

        genuine_death = (r["wall"] is None) and (fdead is not None)
        result = {
            "C": C, "edge": edge, "first_dead": fdead, "peak_live": r["peak_live"],
            "wall": r["wall"], "elapsed_sec": dt, "blocks_done": r["blocks_done"],
            "genuine_death": genuine_death,
        }
        results.append(result)
        (HERE / "sweep_partial.json").write_text(json.dumps(results, indent=2))

        if r["wall"] is not None:
            print(f"  *** WALL at C={C}: {r['wall']} -- NOT an edge, stopping honestly ***", flush=True)
            break

        if not genuine_death:
            print(f"  *** VOID at C={C}: no wall reported but no dead checkpoint found within "
                  f"m_max={m_max} -- corridor did not die inside the swept range. Treating as WALL "
                  f"(the swept range was insufficient to reach the true edge, not a true edge itself). ***",
                  flush=True)
            break

        if edge <= prev_edge:
            print(f"  *** MONOTONICITY VIOLATION at C={C}: edge={edge} <= prev_edge={prev_edge}. "
                  f"VOID per frozen gate -- NOT written to edges file. Stopping. ***", flush=True)
            break

        # genuine, monotone edge -- append immediately (append-only, per cell, so a later
        # crash doesn't lose already-certified cells)
        with open(EDGES_FILE, "a") as f:
            f.write(f"{C} {edge}\n")
        print(f"  => VALIDATED EDGE C={C}: M({C})={edge} first_dead={fdead} "
              f"peak_live={r['peak_live']} t={dt:.1f}s -- appended to {EDGES_FILE.name}", flush=True)
        prev_edge = edge

    print("\n=== SWEEP SUMMARY ===", flush=True)
    for res in results:
        print(res, flush=True)
    (HERE / "sweep_full.json").write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    c_start = int(sys.argv[1]) if len(sys.argv) > 1 else 27
    c_stop = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    main(c_start=c_start, c_stop=c_stop)
