# W6I — Proof-Shape Recon (work order, Fable, 2026-07-04)

Executor: Sonnet agent, running IN PARALLEL with W6H (which owns
w6h/ and the main ledger for now). Non-overlap rules (binding):
- Work ONLY under shell/underlock/w6i/ (create it).
- Do NOT touch renorm_check/IMPLEMENTATION_LEDGER.md — write your
  four ledger entries into w6i/LEDGER_ENTRIES_W6I.md instead; the
  architect merges after verification.
- Read-only reuse of w6e/, w6f/, w6g/ code; copy anything you need
  to extend INTO w6i/ rather than editing in place.
- Memory discipline: 64GB machine, but any single process climbing
  past ~8GB RSS gets killed and reported as an honest wall (the G5
  precedent). Watch RSS on anything enumeration-shaped.
- No commits. CPU only. Frozen gates; the result is the result.

Purpose: this round does not primarily test the lemma — it probes
WHICH PROOF STRATEGY is right. Deliverables are proof-shape
verdicts, not just pass/fail.

## I1 — Potential-function fitting (does the lemma have a convex proof?)

Build the explicit one-step cost structure on states (δ, ρ mod 3^k,
forced parity) for k = 4..7, δ ≤ 8: for every state and every legal
backward step, edge cost = a − 2 (so the +1-ray is the zero-cost
floor). Attempt to fit a potential Φ ≥ 0 with Φ(1-ray states) = 0
such that every edge satisfies cost + Φ(head) − Φ(tail) ≥ 0, with
equality on the loop (a standard shortest-path/dual feasibility
fit — use Bellman-Ford from the ray: Φ(s) = min cost to reach the
ray from s; then check whether Φ is (i) finite everywhere reachable,
(ii) bounded as k grows, (iii) monotone under the k → k+1 projection
(lift-consistency: does Φ_mod-3^(k+1) project onto Φ_mod-3^k?)).

**Registered predictions (Fable):**
- A finite Φ exists at each fixed k (it must — it's a shortest-path
  value) but FAILS lift-consistency: Φ at level k+1 does not project
  onto level k (the §5a cascade showing up as potential leakage) —
  60%.
- If it IS lift-consistent, the lemma has a one-page dual proof —
  report the explicit Φ table and stop the round early to say so.
- Bonus: max Φ over states at each k (the "deepest hole") — predict
  it grows with k (55%) — if it stabilizes, the game is effectively
  finite-window after all.

## I2 — Ostrowski re-coordinates for the follower-set test

The sofic/transducer route died in raw trit coordinates (E1, round
3). Retry the follower-set stabilization in CF-native coordinates:
represent residues via Ostrowski addresses (digits weighted by the
convergent denominators of log₂3), rebuild the m → m+1 boundary/
follower map in those coordinates for m = 2..13, and test whether
follower-set counts stabilize where trit-space diverged. Validate
the Ostrowski conversion on 10 hand-checked (ρ, m) pairs FIRST.

**Registered prediction (Fable): follower sets also fail to
stabilize in Ostrowski coordinates — 55% (the prediction I most
want to lose: stabilization would reopen an S-adic transducer
proof).** Either way, report the count sequence side-by-side with
the trit-space one.

## I3 — Convergent-locking harness (the Round-3 central question, post-universality)

With universality (D = L), "which convergent's law the system obeys"
is pure word discrepancy. Harness: for ~10 irrationals (log₂3, √2,
√3, √5, √7, φ, ∛2, π−3, e−2, a Liouville-ish α with huge CF entry),
compute L(m) of the TRUE word (exact arithmetic — integer floors via
high-precision rationals, NO floats near floors) for m = 2..300, and
for each m identify which convergent's closed form matches L(m)
exactly. Tabulate the locking schedule: which convergent "owns"
which m-range, vs the CF denominators.

**Registered prediction (Fable): lock transfers at exactly m = next
convergent's denominator (lock-until-denominator rule), refined by
the ±1 boundary cases — 70%.** The Liouville-ish α is the stress
case: giant CF entry = one convergent owning a huge m-range;
verify, don't assume.

## I4 — Lift-cascade effective branching (exploratory, UNGATED)

For 20-step backward chains from ρ ≡ 1 (mod 3^8 working precision),
trace each lift choice's influence: at which later step does a lift
made at step j first change the forced parity of the chain? Build
the histogram of influence delays and the effective branching factor
per step (how many lift choices are ever decisive vs pre-cancelled).
Deliverable: the histogram + a one-paragraph honest reading. No
gate; this is intuition fuel for the lower-bound induction.

## Output

w6i/*.csv + scripts + w6i/LEDGER_ENTRIES_W6I.md (four entries,
main-ledger format, ready to merge). Final digest: per experiment —
proof-shape verdict (DUAL-PROOF VIABLE / S-ADIC VIABLE / RULE
EXTRACTED / histogram), predictions HIT/MISS, honest walls.
