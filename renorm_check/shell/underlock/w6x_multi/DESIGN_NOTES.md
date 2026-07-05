# W6X-MULTI — design notes (written before coding, per house rules)

## Goal

Extend `w6w_sparse/sparse_instrument.py`'s backward live-set walk past
m=53 into m=54..106+ (multi-heartbeat), to test whether C=11 (and
C=12..15) — which survive the ENTIRE one-heartbeat window m=1..53 with
no death — die somewhere in the second heartbeat's residue-precision
range, or continue to saturate.

## Mechanical extension (no reset at k=53)

`credit_at_step(k)` (bit_length-exact, no floats) is already valid for
any k >= 0, and is NOT periodic mod 53 (Sturmian/Beatty word driven by
irrational log2(3); steps 53..105 are a different substring than
0..52, confirmed empirically below as a sanity check, not relied upon).

The backward walk in sparse_instrument.py consumes one credit letter
per layer j = 0..m-1, using a precomputed `letters` list. Extending m
past 53 requires ONLY extending which absolute step indices populate
`letters` — the per-layer transition code (parity_forced,
backward_pred_mod, the (R,u,v) live-set update, the u<=C/v<=C/u+v<=C
legality check) is IDENTICAL at every layer, heartbeat boundary or
not. There is no boundary-crossing state to reset: (R, u, v) is
already a pure function of "how many credit letters have been
consumed backward so far and what they were," not of absolute step
index mod 53. This satisfies the "no reset" requirement structurally:
the SAME loop, run for more layers, on a longer `letters` list.

Sanity check performed in code (step0_periodicity_check.py): diff
credit_at_step(0..52) against credit_at_step(53..105) (and further
blocks). **Result, reported honestly since it contradicts the a
priori expectation stated in the mission brief:** the credit word IS
EXACTLY periodic with period 53 for the first six heartbeats (block
indices 0..5, i.e. absolute steps 0..317) -- block 1 (53..105) and
block 2 (106..158) are byte-identical to block 0 (0..52). The first
DIFFERING block is block 6 (absolute steps 318..370), first differing
index at absolute step 358 (base c=1, block-6 c=2). This is not a bug:
it is the SAME landmark already on the repo's board (F5/Collatz
program memory: "first divergence C=148: 358 vs 359" -- the credit
word is a Sturmian/Beatty word whose near-periodicity tracks how good
a rational approximation 53/22 is to log2(3); the word is provably
non-periodic in the limit (irrational slope) but empirically repeats
exactly for many periods before the first convergent-driven
correction at step 358). Practical consequence for THIS round: since
our measurement range is m=54..106 (one heartbeat past 53), we are
entirely inside the exactly-periodic-so-far zone (steps 0..158 all
period-53-identical) -- so any difference we observe between Reading
A and Reading B in this range is coming from the WINDOW-anchor
difference alone, not from any drift in the underlying Sturmian word.
This makes the current round's readings cleanly separable in origin,
but also means this round cannot yet test whether the eventual
(step-358+) breakdown of near-periodicity changes anything -- that
would require m near 358+, well beyond this round's 106+ target and
noted as a further-out open question, not attempted here.

## The anchor ambiguity (both readings implemented, never silently picked)

`sparse_instrument.py`'s "end" anchor for m<=53 is defined as: window
= last m letters ending at absolute index 53 (steps-m .. steps-1,
steps=53 FIXED). For m>53 there is no letter at negative absolute
index, so "last m letters ending at 53" is not directly extensible.
Two live generalizations, per the mission brief:

### Reading A -- "growing end-anchor" (== root anchor for all m)

For a given m, window = absolute indices [0, m), i.e.
    letters[j] = credit_at_step(m - 1 - j),  j = 0..m-1
This is literally sparse_instrument.py's existing `anchor="root"` mode
(already implemented, just needs m>53 permitted). For m<=53 this is
NOT the same as the gate-validated "end" anchor (which pins the window
at absolute index 53) -- Reading A only coincides with "end" AT m=53
exactly (window [0,53) either way). For m>53 there is no "true window
end" concept anymore in this reading; it is simply "the whole history
so far," which happens to be textually identical to the "root" anchor
mode. FLAGGED explicitly, as required.

Textual note: W6W-SPARSE's own root-anchored NEGATIVE CONTROL showed
root diverges from corridor truth by m=29 at C=11 (dead/dead/alive/dead
vs end's genuine survival) -- so Reading A inherits a known bad
track record as a MODEL for corridor truth in the m<=53 regime. We
still implement and report it in full (never silently discard), but
flag going in that the textual evidence disfavors it a priori.

### Reading B -- "heartbeat-periodic re-anchoring"

Keep the "last m letters, end-anchored at a heartbeat boundary" logic,
but let the anchor grow in units of 53:
    anchor_end(m) = 53 * ceil(m / 53)
    letters[j] = credit_at_step(anchor_end(m) - 1 - j),  j = 0..m-1
For m<=53: anchor_end=53, reduces EXACTLY to the original gate-
validated "end" anchor. For m in 54..106: anchor_end=106, window
slides so it always ends at the nearest heartbeat multiple >= m.

### Which does the text favor?

`automaton.py`'s Theorem 1 / Lemma 4 construction and shell_probe.py's
P6 trit-locality property ("k-step liveness depends only on r mod
3^(k+1)") are both stated in terms of a FORWARD run of exactly
`steps` total steps, with the residue constraint read off at the END
of that run (r == 1 mod 3^m after `steps` forward steps). The "end"
anchor's validity for m<=53 comes precisely from this: the last m
steps of a 53-step run are the only steps that can still affect a
mod-3^m readout at step 53, by trit locality (P6), so windowing "last
m letters ending at absolute step 53" is not an arbitrary choice, it
is FORCED by which forward run is being modeled (a single 53-step
heartbeat). P4 (steps-invariance, run_heartbeat with steps=106/159)
in shell_probe.py already tests a DIFFERENT axis than either A or B
here: it holds m FIXED at the edge and extends the total forward run
length past 53, confirming the edge doesn't move -- it does not test
extending m itself past 53.

Reading B is the direct generalization of "the window ends where a
heartbeat ends" -- i.e., it says: the natural multi-heartbeat object
is still "the last m letters of a run that is a whole number of
heartbeats long," matching how automaton.py/shell_probe.py always
fix `steps` to a multiple of 53 (53, 106, 159 in P4). This is the
textually closer generalization of the gate-validated frame.

Reading A has no such grounding for m>53 -- it is not "the last m
letters of an N-heartbeat run" for any natural N related to m; it is
just "everything since the start," which is the OTHER (root) frame
already shown to diverge from corridor truth in the validated m<=53
regime.

**Working expectation (not a decision):** Reading B is expected to
track corridor truth; Reading A is expected to reproduce the root
anchor's known divergence. Both are implemented and measured; if they
turn out identical at every tested m this is reported as a finding
(plausible given C=11's stabilization already observed at m>=19 in
one-heartbeat data).

## Implementation plan

1. `mx_core.py` -- the extended instrument: `credit_at_step` (copied
   verbatim, exact/no-float, cross-checked against automaton.py's
   `credit`), `parity_forced`, `backward_pred_exact`,
   `backward_pred_mod` (all copied verbatim from sparse_instrument.py
   -- these primitives are validated already and this round is about
   the WINDOW construction, not the per-layer transition math), plus
   new `letters_for(m, reading)` supporting "A" and "B", plus
   `sparse_survival_multi(m, C, reading, ...)` (same live-set walk,
   generalized letters), RSS watchdog (same pattern, hard-abort at
   7.5GB via resource.getrusage), witness reconstruction + exact
   verification (same verify_witness_exact logic, letters-parametrized).
2. `step0_periodicity_check.py` -- confirm steps 0..52 != steps 53..105
   (sanity, not load-bearing).
3. `step1_validation_gates.py` -- m<=53 reproduction of all 10 Tier-1
   edges (both readings; Reading B must match "end" exactly since it
   reduces identically; Reading A is expected to reproduce "root"'s
   known divergence, reported not suppressed) + C=11 alive-through-53
   + the 234 stabilization check.
4. `step2_measurement.py` -- the main sweep: C=11..15, m=54..106(+ as
   budget allows), BOTH readings, RSS/time watchdog, witness + exact
   verification per alive cell.
5. `step3_independent_engine.py` -- second, structurally different
   engine (see below) re-run on the C=11 headline cells for agreement.
6. `LEDGER_W6X-MULTI.md` + SYNTHESIS.md append.

## Second independent engine (Step 5 requirement)

`w6w_sparse/step4_independent_rederivation.py` already used "exact-int
DFS with failure-memo" as its second engine vs the primary's layered
modular BFS. Per the mission brief ("do not just copy
sparse_instrument.py's DFS witness-reconstruction path and call it
independent"), this round's second engine will differ further in
KIND, not just recursion-vs-loop:

- Primary (mx_core.sparse_survival_multi): backward layered BFS,
  live-set keyed by (R mod 3^(m-j), u, v), dict per layer, iterative.
- Second engine (mx_dfs2.py): FORWARD-checking randomized/structured
  witness search is not viable (dense forward is what we're avoiding),
  so instead: an exact-integer backward DFS that tracks state
  differently -- instead of (R, u, v) with R = rho mod 3^(m-j), it
  tracks the EXACT big-int rho (never truncated, growing arbitrarily
  large as depth increases, exactly like w6w's second engine did) BUT
  with iterative deepening + an explicit stack (not Python recursion)
  and a DIFFERENT dedup key: (j, u, v) only (dropping the residue
  fingerprint from the memo key entirely, relying on the fact that
  for the ALIVE/DEAD decision -- as opposed to counting distinct
  residues -- memoizing on (j,u,v) alone is a valid (if coarser,
  possibly-slower) failure cache IF we additionally verify no false
  memo hit occurs by cross-checking against the primary's live-set
  size at shallow depths). This is a genuinely different traversal
  (explicit stack, coarser memo key, exact big-int rho throughout,
  no modular truncation at all until the final witness check) rather
  than a cosmetic rename of w6w's DFS. Agreement of alive/dead calls
  between mx_core and mx_dfs2 at every tested (C,m,reading) is the
  required independent confirmation.
