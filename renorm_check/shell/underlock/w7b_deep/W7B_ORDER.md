# W7B — High-Capacity Sparse Sweep, C >= 27 (work order)

Executor: cold Sonnet agent. Follow this spec; the gates are frozen.

## Situation
An exact "sparse live-set" instrument (../w6y_regime/wy_core.py) computes
the survival edge M(C) of a corridor. It is VALIDATED and correct
through C=26 (edges C=11..26 = 57,63,68,71,79,93,108,110,130,132,139,
157,163,188,192,205 — all monotone increasing, cross-checked). At C=27
it hits its own limit: state_cap=4,000,000 exceeded at m=36
(n_exact=4,684,886), so it FALSELY reports edge=36 (a budget wall, not a
death — min_dead was None, the corridor never actually died). All prior
C=27..40 numbers from a naive sweep are INVALID for this reason.

## Task
Extend the true, validated edge measurement to C=27 upward, as far as
memory allows on this 64GB machine.

1. Raise capacity. find_edge_for_C takes state_cap (default 4M) and
   rss_cap_mb (default 7500); the machine has 64GB. Profile bytes/state
   FIRST; if the representation is heavy (>~1KB/state), make it leaner
   (survivors are (residue, deficit) pairs — compact dtype/dedup, not
   python objects) before scaling. Then lift state_cap (try 64M, higher)
   and rss_cap_mb (~48000). Report bytes/state before and after.
2. VALIDATION GATE (frozen, hard): the modified instrument must reproduce
   C=16=93, C=23=163, C=26=205 EXACTLY before any new cell is trusted.
3. MONOTONICITY GATE (frozen, hard): every new M(C) MUST be > M(C-1)
   (M(26)=205). Any cell <= the previous edge, or that ends on a
   state/RSS wall rather than an observed death (min_dead must be a real
   integer, not None), is VOID — record "WALL at m=X, edge unknown",
   never as an edge.
4. Sweep C=27 upward. Per cell record: edge (or WALL), first_dead,
   peak_live_states, bytes/state, wall-clock, death certificate. Stop at
   the first genuine wall you cannot lift within 48GB; report which C and
   how many states it needed — that ceiling is itself a result.
5. Append ONLY genuine-death edges to ../w7a_renorm/w7a_new_edges.txt
   ("C edge"). Full findings to w7b_deep/W7B_FINDINGS.md.

## Rules
Exact integer arithmetic; every edge carries its death certificate.
"WALL, not an edge" is an expected honest outcome — say it plainly, never
dress a wall as a measurement (that failure is why this order exists).
Work only in w7b_deep/ and the append. No commits.

Final message: bytes/state before/after, validated new edges with death
certificates, the first genuine capacity wall (C and state count), and
whether monotonicity held.
