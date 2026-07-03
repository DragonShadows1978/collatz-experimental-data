# W6 Work Order — Shell Transducer Extraction (registered 2026-07-03, Fable)

**Mission:** determine whether the death shell's level-m → level-(m+1)
boundary recursion is a finite transducer driven by the Sturmian credit
word, and if so extract it and validate it against the frozen gates.
**This order STOPS before the m=359 rollout** (E4). The rollout has an
unresolved design dependency (depth extrapolation, see E4) that needs
explicit sign-off after E1–E3 results exist.

**Read first, in this order:**
1. `../SYNTHESIS.md` — rounds 1–2, findings F1–F9, work order W6
2. `shell_probe.py` + `shell_probe.log` — the shell object (P1–P6)
3. `boundary_probe.py` + `boundary_probe.log` — heredity, no cylinder
   compression, sofic signal, word-modulation (B1–B3)
4. `../embedding/automaton.py` — the dense automaton (use as-is; its
   exact-arithmetic credits are law — NO float floors anywhere, W1)

**Definitions.** Live tree at depth δ: the boolean liveness of residues
mod 3^m at deficit d = C−δ after one heartbeat from full start
(`run_heartbeat`), corridor C wide enough that the floor doesn't touch
the shell (C=12 was used for m ≤ 12; raise C if the shell reaches it —
universality F7 makes the choice free as long as depth > shell depth).
Children of node r (level m): r + t·3^m, t ∈ {0,1,2}, at level m+1.
Type of a live node at horizon h: the (own, children, …, depth-h
descendants) liveness pattern. Follower-set refinement: two nodes are
equivalent iff their full descendant trees agree; horizon-h types
approximate this from below.

## E1 — Follower-set stabilization

At depths δ = 0, 1, 2, levels m0 = 8, 9, 10: compute type counts at
horizons h = 2, 3, 4. **Stable** = the h=3 → h=4 refinement splits no
type (count unchanged) at every tested (δ, m0). Report the full count
table either way.
- Stable → proceed to E2.
- Unstable (counts still splitting at h=4) → try h=5 once; if still
  splitting, STOP and report: not sofic at accessible horizons in raw
  coordinates; fallback (Ostrowski reindexing) is a separate order.

## E2 — Transducer extraction (train levels m ≤ 10 ONLY)

Classify every live node at levels m = 5..10 into its type (stabilized
horizon from E1). Tabulate transitions: **(type, c_m) → ordered triple
of child outcomes** (dead, or child's type). The table must be
FUNCTIONAL: if any (type, credit) pair exhibits two different outcomes
anywhere in the training data, the horizon is too shallow — refine
(split that type by one more level of context) and re-tabulate. If the
table does not close by horizon 6, STOP and report with the offending
type's witnesses.

Depth handling: extract per-depth tables for δ = 0..3 SEPARATELY, then
compare. Report whether the tables are identical across δ (depth-
equivariant), identical after a shift, or genuinely δ-dependent. Do
NOT merge them by assumption. Honest limit to state in the report:
dense data covers shell depths ≤ ~9 only.

## E3 — Validation gates (FROZEN — no post-hoc adjustment)

Run the extracted table forward from level 10:
1. **Bit-for-bit regeneration** of dense levels m = 11, 12, 13 (compute
   m=13 dense fresh; memory guard applies — stay under ~8 GB, drop the
   permutation cache between levels if needed). Any single-node
   mismatch = gate FAILED.
2. **Edge readout:** from the regenerated + iterated table, read D(m)
   and confirm all five known edges C=1..5 (M_edge = 4, 7, 9, 12, 14)
   via the correspondence in SYNTHESIS F8.
3. **F9 plateau:** confirm the table's predictions are consistent with
   trit-locality (types of nodes on the residue-1 path can't depend on
   trits above the locality bound).
A table that fails any gate is NOT an instrument. Report failures
plainly; do not tune the table against gate data (that's memorization,
and it will be caught at m=359 where there is no second chance).

## E4 — HARD STOP before rollout

Do NOT iterate to m=359 under this order, even if all gates pass.
Open design question requiring sign-off: the rollout runs the machine
to shell depth ~148, but training data covers depths ≤ ~9; the
depth-equivariance evidence from E2 is the input to that decision, not
a license. Deliver: E1 count table, E2 table + closure report +
depth-equivariance verdict, E3 gate results, and the machine serialized
to `shell/transducer_v1.json` with the code that built it.

## House rules

- Ledger law: update `../IMPLEMENTATION_LEDGER.md` after every phase.
  Commit after every completed phase; this repo is PUBLIC — write
  commit messages for strangers.
- CPU only. No GPU work under this order.
- Exact credits only (`automaton.credit`); if you write any new credit
  code, it must be integer-exact (bit_length construction) and
  cross-checked against `automaton.credit` for k = 0..200000.
- Inconclusive is a result. A capped/failed computation is reported as
  such, never rounded to the nearest convenient answer.
