#!/usr/bin/env python3
"""
W6V-MEASURE -- subprocess trial worker (v2, NEW MEASUREMENT, 2026-07-04).

Runs exactly ONE (C, m) terminal-survival trial and prints a single JSON
line to stdout, then exits. Invoked fresh (one process per trial) by
sweep_new_C_v2.py so that automaton.py's module-level `_PERM_CACHE` starts
EMPTY every time -- eliminating the ~13x observed/naive RSS multiplier
that sweep_new_C.py (v1, long-lived single process) hit, which was traced
to that cache accumulating int64 permutation arrays across every (C, m)
call in the same process and never being cleared.

This does not change the underlying automaton or the edge convention --
same renorm_check/embedding/automaton.py run_heartbeat, same "terminal
state (d, r=1 mod 3^m) survives one 53-step heartbeat" test used by
validate_c5.py and sweep_new_C.py (v1).

Usage: python3 trial_worker.py <C> <m>
Prints: {"C": C, "m": m, "alive": bool, "dt_sec": float, "peak_rss_mb": float}
or {"C": C, "m": m, "error": "..."} on failure (guard trip, MemoryError).
"""

from __future__ import annotations

import json
import resource
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "embedding"))

from automaton import run_heartbeat  # noqa: E402

GUARD_STATES = 3_000_000_000  # naive (C+1)*3^m states guard; with a fresh
                                # process (empty _PERM_CACHE) actual RSS
                                # should track close to naive bytes, not
                                # the ~13x-inflated figure v1 hit.


def main():
    C = int(sys.argv[1])
    m = int(sys.argv[2])
    modulus = 3 ** m
    t0 = time.time()
    try:
        live_by_d, _ = run_heartbeat(C, m, max_states_guard=GUARD_STATES)
        alive = any(live_by_d[d][1 % modulus] for d in range(C + 1))
        dt = time.time() - t0
        peak_rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        print(json.dumps({"C": C, "m": m, "alive": alive, "dt_sec": dt,
                           "peak_rss_mb": peak_rss_mb}))
    except (ValueError, MemoryError) as e:
        dt = time.time() - t0
        peak_rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        print(json.dumps({"C": C, "m": m, "error": str(e), "dt_sec": dt,
                           "peak_rss_mb": peak_rss_mb}))


if __name__ == "__main__":
    main()
