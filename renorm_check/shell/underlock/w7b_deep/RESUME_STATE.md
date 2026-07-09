# W7B-DEEP — Resume State (written mid-sweep, session may end before completion)

## Is the sweep still running?
Check: `ps aux | grep sweep_c27_up`. It was launched detached
(`nohup python3 sweep_c27_up.py 27 60 > sweep_output.log 2>&1 &` + `disown`
from `w7b_deep/`), so it keeps running after this Claude session ends, as
long as the machine itself stays up. If the process is gone and the sweep
was mid-cell (no "VALIDATED EDGE" / "WALL" line for that C in
sweep_output.log), that cell was interrupted, not completed — do not treat
the last logged block line as a final answer for that C.

## What's done and durably on disk (safe, no data lost if this stops)
- `../w7a_renorm/w7a_new_edges.txt` — genuine validated edges only, appended
  one line at a time as each cell completes (so a mid-run interruption
  never loses an already-certified cell):
  ```
  27 208
  28 263
  29 265
  ```
  Each is a real death (wall=None, first_dead is a real integer), monotone
  vs the previous edge. Full death-certificate detail (peak_live, elapsed,
  block count) is in `sweep_partial.json` (updated after every cell) and
  `sweep_full.json` (written only if the whole run to c_stop completes or
  hits a wall/void/monotonicity-violation and exits its main loop cleanly).
- `sweep_output.log` — full block-by-block log, includes the VALIDATION
  GATE re-run (C=16=93, C=23=163, C=26=205, all OK on the lean engine)
  that ran automatically before any C=27+ cell was trusted.
- `wy_core_lean.py` — the lean instrument (frontier as a bare `set` of
  (rho,u,v) instead of `dict` with a redundant parent-pointer value).
  Validated bytes/state: ~554 (original wy_core.py) -> ~313 (lean) at a
  C=22 shallow-depth checkpoint; ~1.81x RSS reduction confirmed at full
  C=26 sweep too (1315.4MB -> 725.4MB peak).
- `sweep_c27_up.py` — the driver: re-runs the frozen validation gate
  inline, then sweeps C=27 upward, enforcing the monotonicity gate
  (M(C) > M(C-1)) and the wall-vs-edge distinction (a cell only becomes
  an edge if wall is None AND a real first_dead exists within m_max).
  RSS cap 32,000MB / state cap 64,000,000 (see docstring for why 32000
  not the order's suggested 48000: only ~42GB was actually free at sweep
  start, other jobs were resident on the machine).

## FINAL STATE — sweep COMPLETE (stopped at the first genuine wall)
| C | edge M(C) | first_dead | peak_live | elapsed | outcome |
|---|---|---|---|---|---|
| 27 | 208 | 209 | 4,790,754 | 2297.6s | EDGE, appended |
| 28 | 263 | 264 | 9,489,130 | 4632.5s | EDGE, appended |
| 29 | 265 | 266 | 18,595,538 | 13768.7s | EDGE, appended |
| 30 | 282 | 283 | 36,804,069 | 24504.6s | EDGE, appended |
| 31 | — (WALL) | None | 69,084,627 | 2061.4s to wall | **WALL — NOT an edge** |

C=31 hit the first chosen-cap wall in the main sweep: **state cap
64,000,000 exceeded at m=48 (n_exact=69,084,627)**. wall != None,
first_dead = None, genuine_death = False -> correctly NOT written to
w7a_new_edges.txt in that run. The background process (was PID 1390182)
exited cleanly after logging the wall and the SWEEP SUMMARY.

## C=31 HIGH-CAP FOLLOW-UP - COMPLETE (run_c31_highcap.py)
Launched to push past the 64M state_cap wall, since that wall was a chosen
cap, not hardware. Caps: STATE_CAP=120,000,000, RSS_CAP_MB=28,000. Frozen
gate re-passed exactly (C=16=93, C=23=163, C=26=205). Driver bug fixed:
prev_edge seeds from M(c_start-1)=M(30)=282 (the earlier draft hardcoded
205).

Final result from `run_c31_highcap.log`:

| C | edge M(C) | first_dead | peak_live | elapsed | outcome |
|---|---:|---:|---:|---:|---|
| 31 | 284 | 285 | 73,462,829 | 48,855.0s | EDGE, appended |

The high-cap process is no longer running. C=31 is now a genuine-death
edge, not a wall: wall=None, first_dead=285, genuine_death=True,
M(31)=284 > M(30)=282. `w7a_new_edges.txt` now contains `31 284`.
Nothing is left to resume for C=31; a future run would start at C=32 with
fresh caps and the same frozen validation gate.

Peak-live growth per C has been running ~1.9-2x (slightly above the
prior-round's ~1.83x average), and per-block wall-clock cost is now
growing FASTER than the state count alone predicts (rho grows to 100+
bits at these depths; Python big-int arithmetic cost climbs with bit
length, not just live-set size) -- block times for C=30 have been
1315s/3323s/3334s for blocks 1-3 (vs ~350-700s at C=27-28). Expect C=30
alone to take several more hours; each subsequent C roughly doubles the
peak-state count again, so we are close to -- within one or two C values
of -- either the state_cap=64,000,000 wall or the rss_cap=32,000MB wall.
Neither has been hit yet as of this note (C=30 block 3 RSS was 8416.5MB,
well under 32GB; peak states 36.8M, under 64M).

## How to resume
1. Check if PID from `ps aux | grep sweep_c27_up` is still alive and
   letting it keep going is fine -- do nothing, just re-attach a monitor:
   `tail -f w7b_deep/sweep_output.log`.
2. If the process died mid-C (machine reboot, OOM-kill, etc.), the
   partially-swept C is NOT in `w7a_new_edges.txt` (append only happens
   on a fully certified cell) -- safe to just re-run
   `python3 sweep_c27_up.py <next_C> 60` from `w7b_deep/`, where next_C
   is the first C NOT already listed in `w7a_new_edges.txt`. The script
   re-runs the frozen validation gate every time it starts (cheap: C=16
   ~0.5s, C=23 ~107s, C=26 ~950s on the lean engine -- about 18 min of
   overhead per restart, unavoidable per the frozen-gate rule, but worth
   knowing so a restart isn't mistaken for a stall).
3. The monotonicity/wall logic is self-enforcing in the script -- no
   manual bookkeeping needed, just supply the right c_start.

## What "done" looks like
The script stops on its own (no restart needed) when it hits:
- a genuine WALL (state_cap or rss_cap exceeded, logged verbatim,
  NOT written to the edges file), or
- a VOID (swept to m_max with no wall AND no death -- means m_max was
  too small for that C's true edge; would need a larger m_max, not a
  capacity increase, to resolve -- also not written as an edge), or
- a MONOTONICITY VIOLATION (would falsify the frozen gate; stops
  immediately, cell not written), or
- reaching c_stop=60 (unlikely -- the wall will almost certainly arrive
  first given the growth trajectory above).
`sweep_full.json` and the final summary line are only written at that
point. Until then, treat `sweep_partial.json` / `w7a_new_edges.txt` /
`sweep_output.log` as the authoritative live state.
