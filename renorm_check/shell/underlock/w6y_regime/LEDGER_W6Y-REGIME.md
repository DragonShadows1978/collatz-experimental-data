# W6Y-REGIME — the heartbeat-quantized capacity law is REFUTED as an exact law: edges drift CONTINUOUSLY through the n=2/n=3 transition zone rather than sitting in a regime and jumping (2026-07-04)

Ledger W6Y-REGIME. Work dir
`renorm_check/shell/underlock/w6y_regime/`. Task: test the
heartbeat-quantized capacity law at scale (C=16..26, windows through
3+ heartbeats), after W6X-MULTI's provisional finding that
`⌊53n(C+1)/22⌋` (with 53→106 at n=2) fit C=11..15's two-heartbeat
edges with MAE 1.0 and the Architect's reframe that "the law
graduates — a heartbeat-quantized law."

## Headline result

**The heartbeat-quantized law does NOT hold at scale.** W6X-MULTI's
clean MAE-1.0 fit at C=11..15 was the *center* of the n=2 regime, not a
generalizable law. As C grows into 16..26, the death edge M_edge(C)
drifts CONTINUOUSLY upward through the "no-man's-land" between the n=2
law value `⌊106(C+1)/22⌋` and the n=3 law value `⌊159(C+1)/22⌋`,
landing squarely BETWEEN them for most of C=16..23 (residuals up to
+22 vs law2 and −27 vs law3 — nothing like MAE 1.0), then crossing PAST
the n=3 line around C=24. The diagnostic `edge/(C+1)` ratio, which a
clean heartbeat-quantized law would pin at n·53/22 = n·2.409 and JUMP
between, instead climbs SMOOTHLY: 4.75→4.94 (C=11..15, near the n=2
target 4.818) → 5.47, 6.00, 5.79 (C=16..18, in the void between n=2 and
n=3) → 6.29..7.59 (C=19..26, drifting toward and then PAST n=3's 7.227
without ever pinning — 7.593 at C=26). A smooth crossover, not a
quantized ladder.

## Validation gates (Step 1) — ALL PASS, twice over

Two independent instruments, both reproduce every prior edge exactly
BEFORE any new territory:

- **mx_core (W6X's own validated engine), Reading B**: Tier-1 C=1..10
  edges (4,7,9,12,14,16,19,21,24,26) — alive@edge AND dead@edge+1,
  10/10. W6X-MULTI C=11..15 edges (57,63,68,71,79) with dead@+1, peak
  live-sets (234,435,750,1286,2336), and exact-verified witnesses
  (n0 = 2713, 1071, 4011, 4011, 23751) — 5/5. C=11 saturation through
  the whole one-heartbeat window (alive m=1..53, peak stabilizes at
  234 from m=19). `step1_validation_gates.py`/.log/.json.
- **wy_core (this round's extended incremental instrument)**: an
  exact-big-int backward walk (structurally a different engine from
  mx_core's modular BFS — no truncation in the search itself),
  cross-checked against mx_core at EVERY m (alive/dead AND live-set
  count) for C=1..15, m spanning the heartbeat-2 boundary (m=1..90):
  0 mismatches. Peak-live cross-check at m=53 for C=11..15:
  234/435/750/1286/2336 exact. Full W6X edge reproduction incl. the
  block-2 boundary (last_alive, first_dead, peak): 5/5 exact.
  `step1b_wycore_gate.py`/.log.

## The instrument (`wy_core.py`) — and two honest bugs found + fixed IN-ROUND

`wy_core.py` imports mx_core.py's validated per-layer transition math
(`parity_forced`, `backward_pred_exact`, `letters_for`,
`verify_witness_exact`) UNMODIFIED and adds only an INCREMENTAL
block-walker so a wide m-range can be swept per C in O(m) total work
per heartbeat block (one continuous walk, checkpoint at every m),
instead of mx_core's O(m) from-scratch restarts per m.

Two bugs were found and fixed by the gate (both recorded in
`wy_core.py`'s docstring), which is exactly why the gate ran at every m
before any new C:
1. **v1** tracked rho mod `3^(m_end−j−1)` (a fixed modulus from the
   block's final m) so intermediate checkpoints reused one walk —
   WRONG: the correct modulus at layer j for target precision m is
   `3^(m−j−1)`, checkpoint-dependent. Alive/dead was still correct;
   live-set COUNTS diverged.
2. **v2** (the naive fix) switched to keying states on EXACT rho — this
   gives correct alive/dead but OVER-COUNTS live states relative to
   mx_core's modular abstraction (mx_core's modulus at the terminal
   layer of any m-call is always `3^0=1`, so its terminal live count is
   distinguished by `(u,v)` alone; exact-rho keeps `(rho,u,v)` states
   that mx_core correctly merges). Same failure numbers recurred — the
   red flag that the mechanism, not the key type, was wrong.
3. **Real fix**: walk with exact rho (correct, engine-independent
   alive/dead), but at each checkpoint m read out the live-set count by
   re-keying the exact frontier with mx_core's own modulus (`mod=1` at
   the terminal layer → dedup by `(u,v)`), reproducing mx_core's count
   by construction. `peak_live` uses the exact-frontier size per layer,
   which equals the true modular peak because the peak provably occurs
   EARLY (layer ≤ 19 for the gated C), where the modulus (>10^9) vastly
   exceeds any reachable rho so no merging happens either way — checked
   directly against mx_core's layer_sizes, not assumed. Gate: 0
   mismatches after the fix.

## The extended survival map (Step 2) — C=16..26, Reading B (pre-registered)

`step2_measurement.py` / `.log` / `step2_measurement_full.json` /
`step2_edges_table.csv`. Per-C sweep m=1..max(law3(C)+15, 116),
block-by-block, RSS/state caps 7500 MB / 4,000,000 (never a wall
hit for C≤25; see below for C=26).

| C | edge M(C) | first dead | law1 ⌊53(C+1)/22⌋ | law2 ⌊106(C+1)/22⌋ | law3 ⌊159(C+1)/22⌋ | res vs law2 | res vs law3 | peak live | monotone | edge/(C+1) |
|---|---|---|---|---|---|---|---|---|---|---|
| 16 | 93  | 94  | 40 | 81  | 122 | +12 | −29 | 4,413      | yes | 5.471 |
| 17 | 108 | 109 | 43 | 86  | 130 | +22 | −22 | 8,011      | yes | 6.000 |
| 18 | 110 | 111 | 45 | 91  | 137 | +19 | −27 | 15,536     | yes | 5.789 |
| 19 | 130 | 131 | 48 | 96  | 144 | +34 | −14 | 29,197     | yes | 6.500 |
| 20 | 132 | 133 | 50 | 101 | 151 | +31 | −19 | 53,357     | yes | 6.286 |
| 21 | 139 | 140 | 53 | 106 | 159 | +33 | −20 | 97,582     | yes | 6.318 |
| 22 | 157 | 158 | 55 | 110 | 166 | +47 | −9  | 186,128    | yes | 6.826 |
| 23 | 163 | 164 | 57 | 115 | 173 | +48 | −10 | 359,271    | yes | 6.792 |
| 24 | 188 | 189 | 60 | 120 | 180 | +68 | +8  | 699,681    | yes | 7.520 |
| 25 | 192 | 193 | 62 | 125 | 187 | +67 | +5  | 1,340,027  | yes | 7.385 |
| 26 | 205 | 206 | 65 | 130 | 195 | +75 | +10 | 2,524,517  | yes | 7.593 |

Context rows (from W6X-MULTI, the clean n=2 regime): C=11..15 edges
57/63/68/71/79, ratios 4.750/4.846/4.857/4.733/4.938 — near the n=2
target 106/22 = 4.818, MAE 1.0. **That regime ends by C=16.**

### Growth curve (peak live-set, Reading B)

234 → 435 → 750 → 1286 → 2336 (C=11..15, from W6X) → 4413 → 8011 →
15536 → 29197 → 53357 → 97582 → 186128 → 359271 → 699681 → 1340027 →
2524517 (C=16..26). Per-C ratio ≈ **×1.83 average** (range 1.81–1.95),
tracking the ×1.7 W6X estimate closely (slightly higher). RSS stayed
well within the 8 GB budget throughout: 14 MB at C=16, 694 MB at C=25,
1315 MB peak at C=26 (block 1). CPU-only, no GPU.

### Monotonicity / no revival (robustness)

Reading B was confirmed monotone (alive-then-permanently-dead) for
every C=16..26 within its swept range. Additionally, an extended
no-revival check (`step2d_revival_check.py`/.log) swept C=16..23 all
the way to m=265 (deep into block 5): NO revival anywhere past the
edge for any C — the edges are genuinely final, and Reading B remains a
clean single-edge object at these C (unlike Reading A, which W6X showed
revives). C=24's block-4 tail (m=196..212) separately confirmed dead
throughout (`step2b_c24_norevival.log`).

## THE QUESTIONS (Step 3) — `step3_analysis.py`

**(a) Where does the 2-heartbeat regime end / does law3 pick up?**
The n=2 law is exact-ish (MAE ~1) only through C=15. It is already
broken by C=16 (residual +12 and growing). The edges do NOT jump to
law3 — they *drift* through the gap and cross the law3 line around
**C=24** (res vs law3 flips from −10 at C=23 to +8 at C=24, +10 at
C=26). But law3 is not "picked up" as an exact law either: the
closest-n MAE in the n=3 band (C=19..26) is **11.88**, and in the n=2
band (C=11..18) **7.25** — both far from MAE 1.0. There is no clean
n-heartbeat law in C=16..26; the quantization holds only near each
regime's center. The `edge/(C+1)` ratio at C=26 is 7.593 — already
PAST n=3's target 7.227 and climbing, with no sign of pinning.

**(b) Does ⌊106(C+1)/22⌋ hold through the regime; does a sharper b
fix it?** No. Residuals vs law2 grow MONOTONICALLY +12→+75 across
C=16..26 (systematic drift, not noise). Best single-b fit
`⌊(106C+b)/22⌋` over the searched band has **MAE 43.6** — no constant
rescues the n=2 form; the form itself is wrong for this C range. A
least-squares linear fit `edge ≈ 10.8·C − 80.4` has a slope (10.8)
steeper than ANY single-heartbeat law slope (law1..4 = 2.4/4.8/7.2/9.6)
with residuals still ±9 — the edge is not linear in C either; the slope
itself steepens.

**(c) The regime-transition rule.** The mission's Δ=25 landmark is
confirmed exactly: at the known 1→2 transition (C=10→11), the previous
regime's value law1(11)=⌊53·12/22⌋=28 sits at 53−28=**25** below the
window top (53) — the measured Δ. Applying the SAME rule to the 2→3
transition (graduate when law2(C) > 2·53−25 = 81) predicts graduation
at **C=17** (law2(17)=86 > 81; C=16 is the boundary, law2=81=threshold).
VERDICT on the rule: it correctly flags that a transition is BEGINNING
around C=16–17 (which matches where the n=2 fit breaks), but it is NOT
a clean "graduate to the next exact regime" rule, because there is no
next exact regime to graduate INTO — the post-transition edges drift
rather than snap to law3. The Δ=25 threshold marks the ONSET of the
transition zone, not a jump between two exact laws. Stated precisely:
**the graduation threshold predicts where the current regime's law
STOPS being accurate (C≈16–17), verified; it does NOT predict a
discrete hop, because the object crosses over continuously.**

## Witness discipline (Step 4) — the n0-vs-depth ladder

Every new edge's witness exact-replayed via `verify_witness_exact`
(backward exact-rho reconstruction from ρ=1, TRUE forward Collatz
replay with exact division at every odd step, deficit-range check =
C exactly). ALL `all_ok=True`. n0 (slow-descender start integer) at
each edge (`step4_witnesses_1623.log`, `step2c_independent_verify.log`):

| edge m | C | n0 | deficit range |
|---|---|---|---|
| 93  | 16 | 40,953    | 16 |
| 108 | 17 | 74,475    | 17 |
| 110 | 18 | 74,475    | 18 |
| 130 | 19 | 869,889   | 19 |
| 132 | 20 | 869,889   | 20 |
| 139 | 21 | 2,928,673 | 21 |
| 157 | 22 | 1,476,423 | 22 |
| 163 | 23 | 5,471,367 | 23 |
| 188 | 24 | 7,182,855 | 24 |
| 192 | 25 | 22,701,369 | 25 |
| 205 | 26 | 60,733,323 | 26 |

n0 grows steeply with edge depth — from ~41K at m=93 to ~60.7M at
m=205, versus W6X's deepest n0=40065. Not strictly monotone in m (the
search returns *any* surviving integer, not the smallest — e.g. C=22's
1.48M < C=21's 2.93M), but the envelope climbs by ~3 orders of
magnitude across the swept depth. C=24's n0=7182855 independently
re-derived by mx_core (a different engine) exactly. These are genuine
slow-descenders: run out of runway once the corridor window is long
enough to see their whole trajectory, exactly as the corridor
instrument is designed to detect.

**Witness-engine escalation (honest, 3 engines)**: getting the C=26
witness required escalating engines, recorded fully:
1. **mx_core `_reconstruct_witness`** retains ALL m frontier-layers
   (parent pointers) with NO RSS watchdog — at C=26/m=205 (2.5M-state
   frontier) it blew past 7 GB heading for the 8 GB house limit;
   KILLED. (This engine DID give C=24/C=25 witnesses cleanly at m≤192,
   under budget.)
2. **mx_dfs2** (W6X's explicit-stack exact-DFS, RSS ~12 MB) — its
   NAIVE depth-first order exhausted a 200M-node budget at m=205
   without finding a completing path (bad search order on a deep cell,
   NOT evidence of no witness — the BFS already proved alive@205).
3. **`witness_bounded.py`** (this round): explicit-stack backward DFS
   with a DEFICIT-CENTERING heuristic (try the `a` giving the most
   balanced (u,v) first). GATED on 4 known cells first — reproduces
   the EXACT mx_core/wy_core n0 at C=11 (2713), C=15 (23751), C=16
   (40953), C=20 (869889), all all_ok, RSS ~12 MB, backtracks
   2.9K→1.1M scaling with depth. This is the engine that resolved
   C=26. Every n0 is exact-verified by the same `verify_witness_exact`
   (backward ρ→1, true forward Collatz replay, deficit range = C).

## Independent cross-verification

C=22 (edge 157) and C=24 (edge 188) — the two headline crossover
edges — independently re-derived by mx_core's ORIGINAL modular BFS
(alive@edge, dead@edge+1, witness exact): agrees with wy_core exactly.
`step2c_independent_verify.log`. Two structurally different engines,
zero disagreements.

## Frozen predictions (Architect) — HIT/MISS

- **(a) 2-heartbeat candidate holds C=16 until the 3-heartbeat
  transition — 60%: MISS.** It does not hold even at C=16 (residual
  +12, growing to +75 by C=26). The n=2 law breaks IMMEDIATELY past
  C=15; there is no clean "holds until a transition" — the transition
  is a smooth drift starting right at C=16.
- **(b) Transition rule "graduate when current-regime edge would
  exceed h·53−Δ, Δ≈25" — 50%: PARTIAL/MISS.** The Δ=25 landmark is
  confirmed exactly at the 1→2 boundary, and the threshold correctly
  marks where the n=2 fit starts failing (C≈16–17). But the rule's
  premise — a discrete graduation between two EXACT regimes — is false:
  the object crosses over continuously, so there is no clean hop to
  predict. Measured Δ = 25 (stated either way, per the brief).
- **(c) Live-set growth ~×1.7/C — 60%: HIT (approx).** Measured average
  ×1.83/C (range 1.81–1.95), close to and slightly above ×1.7.

## Honest walls

- **C=26 — NO WALL, completed but SLOW**: peak live-set 2,524,517;
  edge=205 landed in block 4 (m=160..212). The exact-big-int walk slows
  sharply in later blocks (rho grows to 100+ bits, dict ops on 2.5M
  entries get expensive): block times 182 / 385 / 363 / 380 s, total
  1310 s for C=26. RSS stayed at 1.3 GB throughout (never near the 8 GB
  cap) — the binding constraint at this scale is WALL TIME, not memory.
  A targeted per-m mx_core search for C=26 was tried in parallel but
  abandoned (killed to free a core): a single m-call at C=26 (~2.5M
  states, from scratch) takes ~5 min, so a linear m-by-m mx_core sweep
  is infeasible — the wy_core block walk is the only viable instrument
  at this scale, and even it is time-bound. C=27+ would need a faster
  instrument (e.g. bounded-modulus keys with per-block re-keying, or a
  parallelized frontier) — flagged as the next-round engineering wall.
- No RSS or state-cap wall anywhere in C=16..26. The 8 GB budget was
  never the binding constraint; wall time was (total sweep ~44 min).
- **Reading A**: run only as a labeled control where cheap; not swept
  in full this round (W6X already characterized it as the intermittent,
  non-physical frame; Reading B is the pre-registered corridor-truth
  frame and the only one used for the edge table).

## Artifacts (all under `renorm_check/shell/underlock/w6y_regime/`)

- `wy_core.py` — extended incremental instrument (imports mx_core
  unmodified; adds block-walker + the exact-rho / modular-readout fix).
- `step1_validation_gates.py`/.log/.json — mx_core reproduction of all
  prior edges + witnesses.
- `step1b_wycore_gate.py`/.log — wy_core vs mx_core cross-check at every
  m (alive/dead + count + peak), 0 mismatches.
- `step2_measurement.py`/.log/`step2_measurement_full.json`/
  `step2_edges_table.csv` — the C=16..26 edge sweep.
- `step2_scaling_probe.py`/.log/.json — pre-sweep growth-curve probe.
- `step2b_c24_norevival.log`, `step2d_revival_check.py`/.log — no-revival
  robustness (C=16..24 to m=265).
- `step2c_independent_verify.log` — mx_core independent re-derivation of
  C=22, C=24 edges + witnesses.
- `step3_analysis.py`/.log — residuals, fits, transition rule,
  smooth-drift diagnostic.
- `step4_witnesses.py`, `step4_witnesses_1623.log`,
  `step4_c25_witness.log` — n0-vs-depth ladder (C=16..25).
- `witness_bounded.py` + `step4_c26_witness_bounded.log` — memory-light
  deficit-centering witness extractor (gated on 4 known cells; resolved
  C=26 where mx_core OOM'd and mx_dfs2's naive order timed out).
- `n0_ladder.csv` — the full n0-vs-depth table.
- This file + SYNTHESIS.md append.

No git commits, per house rules. CPU only. Peak RSS this round:
~1.3 GB (C=26 block 1), well under the 8 GB / 7500 MB cap.

---

# W7B-DEEP APPEND — high-capacity extension, C=27 upward

Directive: W7B_ORDER.md (`../w7b_deep/`). Extend the validated edge
measurement above C=26, on the 64 GB machine, as far as memory allows.
Two frozen gates: (1) reproduce C=16=93, C=23=163, C=26=205 exactly
before trusting any new cell; (2) a cell is a real edge ONLY if the
corridor is observed to DIE (real integer first_dead) AND M(C) > M(C-1) —
a state/RSS-cap termination is a WALL, not an edge, and is never written
to the edges file.

## Leaner representation (the enabling change)

The C=26 "honest walls" note above flagged that C=27+ needs a faster/
leaner instrument. Root cause found: wy_core.py's frontier was a `dict`
keyed by (rho,u,v) whose VALUE was a full parent tuple + branch int
`((rho,u,v),a)` — a redundant second copy of the key plus an `a`, which
NO caller of walk_block_exact/find_edge_for_C ever reads (witness
extraction is a separate pass in witness_bounded.py). Replaced with a
bare `set` of (rho,u,v) in `../w7b_deep/wy_core_lean.py` (transition
math byte-for-byte identical; only the survivor container changed).

- **bytes/state: 554 → 313** (direct RSS-delta measurement at a C=22
  shallow checkpoint, peak_live=186128: 103.1 MB → 58.3 MB). ~1.77x.
- Confirmed at full scale: **C=26 peak RSS 1315 MB → 725 MB (1.81x)**;
  wall-clock also improved (block times roughly halved, less alloc/GC).
- VALIDATION GATE re-passed EXACTLY on the lean engine: C=16=93,
  C=23=163, C=26=205 — identical peak_live and records, not just edges.

## New genuine edges (each a real death; monotone; appended to
`../w7a_renorm/w7a_new_edges.txt`)

| C | M(C) | first_dead | peak_live | wall | elapsed | edge/(C+1) | ΔM |
|---|---|---|---|---|---|---|---|
| 27 | 208 | 209 | 4,790,754  | None | 2,297.6 s  | 7.43 | +3  |
| 28 | 263 | 264 | 9,489,130  | None | 4,632.5 s  | 9.07 | +55 |
| 29 | 265 | 266 | 18,595,538 | None | 13,768.7 s | 8.83 | +2  |
| 30 | 282 | 283 | 36,804,069 | None | 24,504.6 s | 9.10 | +17 |

- **Monotonicity: HELD at every cell** (208>205, 263>208, 265>263,
  282>265). No revival, no non-monotone step.
- **Peak-live growth ×1.90/C average** across C=26→30 (4.79M/2.52M=1.90,
  9.49M/4.79M=1.98, 18.60M/9.49M=1.96, 36.80M/18.60M=1.98) — slightly
  above the C=16..26 ×1.83 trend and still accelerating.
- **Binding constraint is now state COUNT and WALL TIME, not RSS**: even
  at C=30 (36.8M states) peak RSS was only 8.4 GB of the 32 GB cap used.
  Per-block wall-clock grew to ~3,300 s each (8 blocks/cell) as rho
  reached 100+ bits — big-int arithmetic cost, not memory, dominates.
- The big ΔM jumps (+55 at C=28, +17 at C=30) alternating with tiny ones
  (+3, +2) continue the "smooth drift, no clean quantized ladder"
  picture; edge/(C+1) is now oscillating ~7.4–9.1, still climbing past
  n=3's 7.227 with no pinning.

## Capacity ceiling

Caps used this run: rss_cap_mb = 32,000 (deliberately below the order's
suggested 48,000 — only ~42 GB was actually free at start, other jobs
resident), state_cap = 64,000,000. Projection from the ×1.90/C growth:
C=31 peak ≈ 65–73M states, which EXCEEDS the 64M state_cap — so C=31 is
the expected first genuine wall (state-count, not RSS; RSS would still
have room). [C=31 outcome — edge or WALL — recorded below once the cell
completes; do not infer it from this projection.]

## Artifacts (under `../w7b_deep/`)

- `wy_core_lean.py` — the lean instrument (set-based frontier).
- `sweep_c27_up.py` — driver: inline frozen-gate re-check, then C=27↑
  with the monotonicity + wall-vs-edge gates enforced in code.
- `sweep_output.log` — full block-by-block log incl. the gate re-run.
- `sweep_partial.json` — structured per-cell certificates (append-safe).
- `RESUME_STATE.md` — live resume notes (process is detached; survives
  session end).

No git commits, per house rules. CPU only.

### C=31 outcome — FIRST GENUINE CAPACITY WALL (not an edge)

**WALL at C=31: state cap 64,000,000 exceeded at m=48
(n_exact=69,084,627).** Reported by the instrument, wall != None,
first_dead = None, genuine_death = False. Per the frozen gate this is a
WALL, not an edge — it is NOT written to w7a_new_edges.txt, and the sweep
stopped here (blocks_done=1, elapsed 2,061 s to the wall). The projection
(C=31 peak ≈ 65–73M > 64M cap) landed: the frontier crossed the state cap
at m=48 with 69,084,627 live states — a SHALLOW layer (m=48 of a 53-layer
first block), exactly the "peak precedes truncation" regime, so this is a
genuine peak-live count, not a deep-tail artifact.

Nature of the wall: this is the **state_cap I chose (64M), not a hardware
limit**. RSS at the wall was only 15,872 MB of the 32,000 MB cap — memory
had ~16 GB of headroom left. So C=31 is reachable in principle by raising
state_cap (e.g. to ~150M) and rss_cap toward ~28,000; the 69M-state peak
would fit in ~20–22 GB at the measured ~300 bytes/state. Cost estimate:
one C=31 cell ≈ 8 blocks × ~4,000–5,000 s ≈ 9–11 h of wall time (per-block
cost is now rho-bit-length-bound, growing faster than state count). That
is the next-round engineering lever; not run here to keep the wall
honest and the result reproducible under the caps as stated.

**Summary of the W7B-DEEP run:** genuine death-certified edges extended
from C=26 to **C=30** (M = 208, 263, 265, 282 for C=27..30), monotonicity
held at every cell, gate reproduced exactly on the lean engine; first
state_cap wall at **C=31** under the 64M cap (state count 69,084,627 at
m=48). Instrument memory footprint nearly halved (554 → 313 bytes/state)
— the enabling change that made C=27..30 tractable where the old
dict-based representation had flagged C=27 as its own engineering wall.

### C=31 high-capacity follow-up (state_cap 120M, rss_cap 28,000 MB)

Because the C=31 wall above was the 64M state_cap I *chose* (not hardware
— RSS had ~16 GB of headroom), a follow-up run (`run_c31_highcap.py`,
same frozen gate re-passed exactly) raised state_cap to 120,000,000 and
rss_cap to 28,000 MB to try to capture C=31 as a genuine edge. Also fixed
a latent driver bug: `prev_edge` was hardcoded to M(26)=205; now seeds
from M(c_start−1) so the C=31 monotonicity baseline is correctly M(30)=282.
**Block 1 cleared the old wall**: peak_this_block = 69,084,627 states now
fits under the 120M cap, RSS 16,082 MB of the 28,000 cap (comfortable),
elapsed 2,538 s. Corridor still alive past m=53; blocks 2..8 in progress.
[C=31 final edge/wall — recorded below once the cell completes; if it dies
with a real first_dead and M(31) > 282 it becomes a genuine edge appended
to w7a_new_edges.txt; if it exceeds 120M states or 28 GB RSS first, that
is the new honest wall.]
