# Lock 4 — Bridge Obstruction Notes (Fable, started 2026-07-04 night)

Goal: upgrade Theorem 5 (no unbounded escape) from sketch to theorem
per the red team's own ruling (problem list §7): one deterministic
Bridge Obstruction inequality, with every term exactly defined. This
file pins the definitions in the CERTIFIED GAME's coordinates so the
existing instruments (canonical engine, one-point machinery) apply
unchanged.

## 1. The objects, exactly

- **Corridor capacity C, deficit d ∈ [0, C]**: as in the shell/
  capacity work. Ascent = deficit increasing (moving up toward a new
  record); descent = decreasing.
- **Phase letters**: the true word's credit letters c_k ∈ {1, 2}
  (support = 1, drop = 2), canonical end-anchored windows, exact
  bit_length arithmetic — same conventions as the capacity program.
- **Step law (forward)**: d' = d + c − a, with a ≥ 1 and PARITY
  forced by the residue class mod 3 (identical legality to the
  certified game; ascent at a drop phase requires a = 1, which
  requires class 2; support phases with even-forced a ≥ 2 force
  descent).
- **RESERVE at a point** := C − d (headroom below the current
  record ceiling).
- **CLIMB of a segment** := Σ(c − a) over the segment (net deficit
  gained; positive = ascent).
- **USABLE RESERVE over a k-window** := the maximum CLIMB achievable
  by ANY residue-legal exponent sequence over that window — an
  exact finite quantity, computable by the canonical engine run
  with the objective flipped (max Σ(c−a) instead of min max
  partial sum). THIS replaces every "expected/observed/drift"
  locution in the current draft.
- **LAUNCH STATE** := the (residue class, deficit) at the start of a
  climb attempt. Usable reserve may depend on it; the inequality
  must hold for the WORST launch state (max over launches).
- **CRASH TAX** := the forced net descent over the steps immediately
  following a maximal climb segment (support-phase forcing +
  battered residue class). Measured, then bounded.
- **BRIDGE i** := the window between consecutive convergent scales
  (first bridge: the 306-letter window between the q = 53 corridor
  regime and the m = 359 edge at C = 148/149 — the F5 territory).
- **REQUIRED SUPPORT at arrival** := the capacity the Lock 3 edge
  demands at the next scale (first bridge: the C ≈ 149 requirement;
  in general M_edge^{-1} at q_{i+1}).

## 2. The target inequality (Bridge Obstruction)

For every bridge i and every launch state:

  USABLE_RESERVE(bridge_i, launch) + RESERVE(launch)
      < REQUIRED_SUPPORT(q_{i+1}),

with the gap growing in i (later bridges worse). First bridge
concretely: max residue-legal climb over the 306-letter window,
plus the launch headroom available at the q=53 scale, must fall
strictly short of ~149.

## 3. Two accountings to reconcile (registered, pre-measurement)

The current draft's "306(2 − log₂3) ≈ 127" is a VALUATION-side
reserve estimate. The phase-side estimate is different: with
supports forcing a ≥ 2 and drops allowing a = 1, the phase-relaxed
(residue-free) max climb over k letters is
Σc − (drops·1 + supports·2) = ⌊kα⌋ − k − supports(k) ≈ k(2α − 3)
≈ 0.17k → ≈ 52 for k = 306. If even the RELAXED bound is < 149,
the first bridge needs no residue arithmetic at all. The two
accountings (127 vs ~52) measure different things; B1 measures both
exactly and the notes get updated with which one the inequality
should ride on. (Architect's live algebra distrusted until the DP
speaks — the week's rule.)

## 4. Why this should fall to the same machinery

Max-climb over a window is the mirror of min-max-partial-sum: same
state space, same parity forcing, same order-gap rigidity. The
one-point lemma's engine (congruence classes vs feasible cost
window) should cap climbs exactly as it floors descents. If B1
shows the climb cap is convergent-quantized (a ⌊·⌋ law like
everything else in this object), Lock 4's inequality becomes finite
arithmetic per bridge plus a monotonicity argument in i — the same
shape as everything the program has already proven into.
