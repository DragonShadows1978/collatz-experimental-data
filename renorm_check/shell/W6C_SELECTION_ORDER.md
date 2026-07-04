# W6C Work Order — Convergent-Selection Mechanism (registered 2026-07-03, Fable)

**Question:** W6B established that a Sturmian-driven corridor locks to a
rational convergent of its word's slope. What SELECTS the convergent?
Two candidate rules survive the golden data (which cannot separate them,
since golden's lock 3/8 is simultaneously the coarser and the under-side
choice):
- **R-coarse:** the lock is the coarsest scale-appropriate convergent;
  upgrades need ≳2 full return cycles. → real system at m=359 uses
  22/53 → D(359)=149 → C=148 edge = **358**.
- **R-under:** the lock is the under-side convergent (shell quantizes
  toward LESS death — consistent with every golden miss-row lagging the
  laws). → real system at m=359 could use 127/306 (under, den 306 ≤ 359)
  → D(359)=148 → C=148 edge = **359**.
The two rules map to OPPOSITE F5 answers. This order is designed to
separate them.

**Exactness law (binding, all designs):** credit words only from
quadratic surds so floors are exact integer arithmetic —
⌊k·√n⌋ = isqrt(n·k²), no floats anywhere. Cross-check every credit
function against 60-digit Decimal for k=0..100000 before measurement.
Candidate-law tables (irrational + convergents) computed and written
down BEFORE any D value is read, per house pre-registration discipline.

**Shared machinery:** `shell/toy_word/toy_automaton.py`'s
`run_heartbeat_generic` (T1-validated). D(m) readout exactly as
SYNTHESIS F8 / W6B: min ceiling-distance of a live terminal, corridor
wide enough that shell depth stays ≥3 below the floor (report depth and
margin every run; widen C and rerun if margin < 2). 8GB memory guard;
int32 permutation arrays; long runs launched in background with
per-step progress logging.

**Coordination law:** each design writes ONLY to its own directory
under `shell/selection/` and its own RESULTS file. Do NOT edit
IMPLEMENTATION_LEDGER.md or SYNTHESIS.md (integration happens after all
designs land — avoids concurrent-edit races). No git commits.

---

## Design A — Does the real word's aperiodicity bite at all? (dir: selection/real_word/)

A1. Real automaton (α = log₂3, exact credits from automaton.credit),
    TWO words: the true word vs the 53-periodicized word (repeat
    credits c_0..c_52). D(m) for m=2..13 at steps = 106 AND 159
    (at steps=53 the words are identical by construction — that run is
    the control and must match shell_probe P5 exactly).
    - Registered prediction (Fable): **identical D(m) everywhere** —
      the corridor cannot see aperiodicity at these scales.
    - Any row that differs: report loudly; that row is aperiodicity
      biting below the wall and REOPENS the F5=359 case directly.
A2. Window slide: fixed m ∈ {8, 10}, true word, steps swept over
    53..106 in steps of 1 (each run reads a different length-~m factor
    of the word near its end). Record D vs steps, and each window's
    support-count (number of 1-credits in the final m+1 letters).
    - Registered prediction (Fable): variation ≤ 1, correlated with
      window support-count; no drift.

## Design B — THE CRUX: √2 separates the rules (dir: selection/sqrt2/)

Word slope α = √2 (⌊k√2⌋ = isqrt(2k²)); β = 2−√2 ≈ 0.58579.
Convergents: 1/2, 3/5 (over), 7/12 (under), 17/29, 41/70.
B1. Controls: heredity + universality spot-checks (m=2..6, C ∈ {8,12}).
B2. D_√2(m), m=2..16, corridor wide enough per the margin rule
    (expect C≈14-16 needed at m=16 — β is larger, shell is faster;
    verify margin every row; the m=16 row is optional if the guard
    binds — the decisive row is cheap).
B3. Decisive row m=12 (3^12 dense = trivial): with fitted offsets from
    the agreement region, 7/12 (under) predicts D=6; 3/5 (over) AND
    the irrational law predict D=7.
    - Registered prediction (Fable): **6 — R-under wins.** Stated
      uncertainty: this is a mechanism hunch from golden's lag-side
      misses, not a derivation. If 7: R-coarse survives (the slope is
      already excluded as a standalone law by W6B; transfer inference
      says 7 → R-coarse). If neither/mixed across rows: the rule is
      richer than both candidates — report raw, no aggregation.

## Design C — Selection table across families (dir: selection/families/)

Same pipeline for: α = √3 (isqrt(3k²)), α = √6−1 (isqrt(6k²)−k),
α = √7−1 (isqrt(7k²)−k). For each: candidate-law tables first, then
D(m) m=2..14 (wider if cheap), per-row law matching, and the side
(over/under) + denominator of the winning convergent. √3's own
side-discriminating row is m=15 (under-convergents predict 3, over
predict 4) — include it if the memory guard allows.
    - Registered prediction (Fable): every family locks to a convergent
      rather than its slope (lock universality); side-pattern per
      family should agree with Design B's verdict.

## Reporting

Each design: RESULTS_<X>.md in its own directory — controls, tables
(laws vs measured, per-row), verdict vs the registered predictions,
runtime/memory, walls hit (inconclusive is a result). Final message
back: the verdicts and the per-design one-paragraph summary. The F5
implication mapping stays as registered above — do not re-derive or
soften it in the results files.
