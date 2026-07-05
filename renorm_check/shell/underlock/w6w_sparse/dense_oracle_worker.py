#!/usr/bin/env python3
"""
W6W-SPARSE -- subprocess-isolated dense-oracle worker, v2 with ENFORCED
RSS cap.

v1 LESSON (recorded honestly): the first version of this worker only
self-REPORTED peak RSS after the fact; it did not enforce the cap. Its
C=6, m=17 run was measured by a peer session at VmPeak 13.4 GiB against
the 7500 MB cap it had been passed, and was externally killed. This
version enforces the cap for real: a watchdog thread reads VmRSS from
/proc/self/status every 0.2s and hard-aborts (os._exit) with a JSON
"wall" record the moment the cap is crossed.

Runs ONE automaton.run_heartbeat(C, m) call in a fresh process (so the
module-level _PERM_CACHE never accumulates across cells, per the
W6V-MEASURE v1->v2 lesson).

Usage: python3 dense_oracle_worker.py <C> <m> <rss_cap_mb>
Output: one JSON line on stdout. Exit 0 = verdict obtained; exit 2 =
RSS wall (JSON line still emitted, alive=null, error names the wall).
"""
import json
import os
import sys
import threading
import time
from pathlib import Path

EMBEDDING = Path(__file__).parent.parent.parent.parent / "embedding"
sys.path.insert(0, str(EMBEDDING))


def vmrss_mb() -> float:
    with open("/proc/self/status") as f:
        for line in f:
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) / 1024.0
    return 0.0


def vmpeak_mb() -> float:
    with open("/proc/self/status") as f:
        for line in f:
            if line.startswith("VmPeak:"):
                return int(line.split()[1]) / 1024.0
    return 0.0


def main():
    C = int(sys.argv[1])
    m = int(sys.argv[2])
    rss_cap_mb = float(sys.argv[3]) if len(sys.argv) > 3 else 7500.0

    peak_seen = [0.0]

    def watchdog():
        while True:
            rss = vmrss_mb()
            peak_seen[0] = max(peak_seen[0], rss)
            if rss > rss_cap_mb:
                print(json.dumps({
                    "C": C, "m": m, "alive": None,
                    "peak_rss_mb": peak_seen[0],
                    "error": f"RSS WALL: VmRSS {rss:.1f}MB > cap {rss_cap_mb}MB "
                             f"(hard-aborted by watchdog)",
                }), flush=True)
                os._exit(2)
            time.sleep(0.2)

    t = threading.Thread(target=watchdog, daemon=True)
    t.start()

    from automaton import run_heartbeat  # noqa: E402  (import after watchdog armed)

    try:
        modulus = 3 ** m
        live_by_d, _ = run_heartbeat(C, m, max_states_guard=2_000_000_000)
        alive = any(live_by_d[d][1 % modulus] for d in range(C + 1))
        print(json.dumps({"C": C, "m": m, "alive": alive,
                           "peak_rss_mb": max(peak_seen[0], vmpeak_mb()),
                           "error": None}), flush=True)
    except MemoryError:
        print(json.dumps({"C": C, "m": m, "alive": None,
                           "peak_rss_mb": max(peak_seen[0], vmpeak_mb()),
                           "error": "MemoryError"}), flush=True)
        sys.exit(2)
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"C": C, "m": m, "alive": None,
                           "peak_rss_mb": max(peak_seen[0], vmpeak_mb()),
                           "error": repr(e)}), flush=True)
        sys.exit(3)


if __name__ == "__main__":
    main()
