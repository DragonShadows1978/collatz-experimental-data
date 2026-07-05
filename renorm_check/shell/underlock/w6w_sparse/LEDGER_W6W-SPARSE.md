# W6W-SPARSE — sparse live-set instrument; the formula's first break is CONFIRMED at C=11 (2026-07-04)

Ledger W6W-SPARSE. Work dir `renorm_check/shell/underlock/w6w_sparse/`.
Task: build a full-precision, live-set-only forward-recursion instrument
for corridor survival (track only surviving states, never the dense
3^m occupancy arrays), validate it against every genuine Tier-1 cell,
then measure the cells dense enumeration could never reach — C=7's
full edge and the contested C=11 zone (formula 28 vs W6U-RECON's
plateau claim D_recon(29..32)=11).

## The instrument (`sparse_instrument.py`)

M_edge(C)'s defining question — does some terminal-compatible state
(d, r≡1 mod 3^m) survive one 53-step heartbeat from the fully
populated start — is answered by walking BACKWARD from the single
terminal residue rho=1 through the heartbeat's last m letters
(end-anchored window, the frame all six genuine Tier-1 gates select),
tracking the live set of (rho mod 3^(m−j), deficit-range-state u, v)
triples. Free endpoints (d_0 and d_m free in [0,C]) — exactly the
fully-populated-start / any-surviving-terminal semantics of
`embedding/automaton.py`, and value-identical in structure to
W6U-RECON's gate-selected variant (ii), independently re-implemented (layered
modular BFS; no code imported from w6u_recon). All arithmetic exact
Python ints; witness certification replays true Collatz on exact
integers. The dense forward map is 3-to-1 (verified: all 729 (a, r')
pairs at m=5 have >1 preimage), so the backward walk is the only
direction where the live set stays sparse; the death shell then keeps
it TINY: peak 234 states at C=11 where the dense instrument needed
13.8 GB.

## Validation gates (step1_validation_gates.py / step1_output.log) — ALL PASS

- Lemma 3 credit word (independent bit_length re-derivation): 22/31/53 ✓.
- GATE A, Tier-1 C=1..6 (mapping confirmed from automaton.M_edge +
  W6T-PROV table + w6v README, not assumed): sparse edges
  **4, 7, 9, 12, 14, 16 — 6/6 exact**, with fresh dense cross-checks
  in-process at C=1..5 (alive-at-edge AND dead-past-edge) and at C=6
  fresh dense alive-at-16 (capped subprocess, 4836 MB) + the ARCHIVED
  dense death certificate for C=6/m=17 (w6v_measure/sweep_new_C.log:
  m=16 alive dt=143.23s, m=17 dead dt=433.10s). An in-round fresh
  dense re-check of C=6/m=17 is NOT feasible under the ~8 GB cap
  (W6V's own record: 12.0 GB observed) — v1 of this round's gate
  script tried it anyway with a cap that was only reported, not
  enforced; the worker reached VmPeak 13.4 GiB and was killed by a
  peer session. Recorded as a process bug; the worker now hard-aborts
  via a /proc/self/status VmRSS watchdog (0.2s poll). No measurement
  depended on the killed run.
- GATE B, C=7 alive at m=17 (the dense sweep's last reachable fact,
  sweep_new_C_v2.log): sparse confirms, live set 31 states, <1 ms,
  witness exact-verified. Dense needed 13,820 MB / 615 s for this
  same cell.

## Results

### Tier-1 table extension (step2_4_climb.log / .csv / .json)

| C | measured M_edge | formula ⌊53(C+1)/22⌋ | match | peak live-set |
|---|---|---|---|---|
| 7 | **19** (dies at 20) | 19 | Y | 31 |
| 8 | **21** (dies at 22) | 21 | Y | 50 |
| 9 | **24** (dies at 25) | 24 | Y | 80 |
| 10 | **26** (dies at 27) | 26 | Y | 133 |
| 11 | **NO DEATH through m=53** | 28 | **N — FIRST BREAK** | 234 |
| 12 | no death through m=53 | 31 | N | 435 |
| 13 | no death through m=53 | 33 | N | 750 |
| 14 | no death through m=53 | 36 | N | 1286 |
| 15 | no death through m=53 | 38 | N | 2336 |

C=7..10: the first genuine full-precision measurements at these C
(previous status per W6T-PROV: DERIVED, m1-proxy only) — **formula
exact at all four**, death certificates observed (alive at edge, dead
at edge+1). C=7 resolves the cell where dense enumeration died at
m=17: genuine edge 19, exactly the formula.

### C=11 — THE PRIZE (steps 2-4; step4*.log)

The corridor at C=11 **survives m=28 → m=53, the entire single-
heartbeat window**, with a genuine exact-replayed integer witness at
every depth. The witnesses at m=29/30/31/32 reconstruct to start
integers **839, 559, 745, 993 — the same four W6U-RECON trajectories,
re-derived from scratch by an engine that shares no code with
w6u_recon**. Deep witness at m=53: n0=1707, deficit range exactly 11,
53-step exact Collatz replay to 1.

- **Independent re-derivation (required, done):** second engine =
  exact-integer recursive DFS + failure memo (vs layered modular BFS;
  different traversal, state representation, dedup). Agrees at every
  cell m=26..33 (step4_independent_rederivation.log) and at every
  m≥28 cell of C=11..15 up to 53 (step4b, cross-checked per-cell).
- **Anchor robustness (step4c):** steps-invariance gate at anchors
  106/159 passes (C=3,4 edges hold); C=11 survival past 28 holds at
  ALL THREE anchors (53/106/159) — not a one-window artifact.
- **Root-anchored negative control:** dead/dead/ALIVE/dead at
  m=29/30/31/32, C=11 — exactly w5_final_merged_table.csv's
  D_recon_root_variant column (12/12/11/12). The two frames separate
  exactly where W6U said they do, and this round's instrument sits in
  the gate-validated (end-anchored) frame.

**Verdict: the capacity law's first break at C=11 is CONFIRMED at the
Tier-1 standard** — same instrument frame that reproduces every
genuinely measured cell (C=1..6 dense-verified; C=7..10 formula-exact
with death certificates), two independent engines, exact-integer
witnesses. The archived M_edge(11)=28 was never a measurement
(W6T-PROV: DERIVED); the linear-countdown assumption behind it fails
exactly at m=29, where the plateau begins. Moreover the plateau does
not stop at 32: **no death exists anywhere in the one-heartbeat
window at C≥11.** The countdown-ladder concept itself saturates at
C=11 — M_edge(C) as "death edge within one heartbeat" is UNDEFINED
(no death) for C≥11, not merely larger than formula.

**Standing caveat (E2-class, inherited and sharpened):** all of this
is within the one-heartbeat construction (window ≤ 53). Whether a
death edge for C≥11 exists under multi-heartbeat windows (m > 53,
residue constraints spanning heartbeat boundaries) is UNPROBED — that
is now the sharpest open cell on the board. What would falsify the
break: a validated multi-heartbeat extension showing the C=11 corridor
dies at some m ≤ 53 under deficit constraints the one-heartbeat frame
misses, or a demonstration that the end-anchored frame diverges from
genuine corridor reality somewhere in C=7..10's newly measured range
(it doesn't: 4/4 formula-exact there).

### Frozen predictions (architect's, registered pre-measurement)

- Formula exact at C=7..10 (70%): **HIT** — 4/4 exact.
- C=11 closest call: formula holds 55% / plateau 45%: **the 45% side
  landed** — plateau confirmed, formula broken. The favored call
  MISSED.

## Honest walls

- In-round fresh dense re-verification of C=6/m=17: RSS wall
  (~12-13.4 GB vs ~8 GB cap), resolved by citing the archived W6V
  dense certificate. Process bug in v1's cap enforcement recorded
  above.
- m > 53: construction boundary of the end-anchored one-heartbeat
  frame; multi-heartbeat extension not attempted this round (honest
  scope limit, now the registered next question).
- No other walls: every sparse cell ran in <10 ms at <14 MB RSS.

## Artifacts (all under renorm_check/shell/underlock/w6w_sparse/)

`sparse_instrument.py` (core), `step1_validation_gates.py` +
`step1_output.log` + `run2.out`, `dense_oracle_worker.py` (capped),
`step2_4_climb.py` + `.log` + `step2_4_climb_table.csv` +
`step2_4_climb_full.json`, `step4_independent_rederivation.py` +
`.log`, `step4b_extent_probe.py` + `.log`,
`step4c_anchor_robustness.py` + `.log`, this file. No commits, per
house rules. CPU only. Peak RSS this round: 4.8 GB (the one capped
dense gate call); all sparse work <15 MB.
