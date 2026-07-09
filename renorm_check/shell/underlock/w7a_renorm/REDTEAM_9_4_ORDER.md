# RED TEAM: Is 9/4 a real finding or an artifact? (work order)

Executor: cold Sonnet agent, ADVERSARIAL stance. Your job is to BREAK
the claim, not confirm it. Default to "artifact" and make the data
force you off that position. Exact integer arithmetic.

## The claim under audit
Session finding (SUSPECT): "the big increments in the corridor-edge
sequence M(C) occur at positions spaced at rate 9/4 = 2.25, fitting
floor(9n/4)+2 (or +3)." A prior blind analysis (W7C_FINDINGS.md)
already noted the fit "breaks down for k>=3" and that "the single
largest delta (55, at n=18/C=28) was EXCLUDED from the claimed jump
set despite exceeding every claimed jump's delta -- unexplained." That
exclusion is your prime suspect.

## The data (exact, do not alter)
M(C): C=1..28 = 4,7,9,12,14,16,19,21,24,26,57,63,68,71,79,93,108,110,
130,132,139,157,163,188,192,205,208,263
Increments d(C)=M(C)-M(C-1), C=11..28 =
31,6,5,3,8,14,15,2,20,2,7,18,6,25,4,13,3,55
More cells (C=29+) may be in w7a_new_edges.txt -- use them if present.

## Adversarial tasks
1. **Threshold sensitivity.** The "big vs small" split defines the H
   positions. Sweep the H/L threshold over ALL plausible cut values.
   Does the 9/4 fit survive only for a NARROW threshold window, or is
   it robust? A pattern that exists for exactly one hand-tuned
   threshold is an artifact. Report the threshold range (if any) for
   which floor(9n/4)+c fits, and the fit quality across it.
2. **The excluded +55.** Redo the H-position fit INCLUDING C=28's +55
   (it is the largest increment; excluding it is indefensible unless
   justified). Does 9/4 survive with it in? Report the fit both ways.
3. **Null / look-elsewhere test.** Generate the H-position sequence and
   ask: what fraction of RANDOM 2-symbol words of the same length and
   density admit a floor(k*n)+c fit at comparable SSE for SOME simple
   rational k? If many random words fit some k this well, 9/4 is
   look-elsewhere noise. Quantify (Monte Carlo, report the p-value-like
   fraction).
4. **Overfitting count.** floor(9n/4)+c has how many free parameters
   (9, 4, c, the threshold, the +55 exclusion) vs how many data points
   it explains? Compute the ratio honestly. A "law" with as many knobs
   as points is not a law.
5. **Provenance trace.** Where did 9/4 FIRST appear this session? Was it
   derived, or reverse-fit to the H positions then rationalized? State
   which, from the evidence.

## Verdict (required, blunt)
One of: VALID (9/4 survives threshold sweep + the +55 + the null test);
FRAGILE (survives only under specific choices -- state them);
ARTIFACT (does not survive -- it was a reverse-fit that dropped its
worst point). Back it with the numbers from tasks 1-4.

## Rules
Adversarial: try to kill it. Exact arithmetic. Work only in
w7a_renorm/. Findings -> REDTEAM_9_4_FINDINGS.md. No commits.
Final message: the threshold-sensitivity result, the with-+55 fit, the
null-test fraction, the parameter-count ratio, and the blunt verdict.
