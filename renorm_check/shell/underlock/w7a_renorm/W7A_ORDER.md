# W7A — Corridor Edge Law Above the C=10 Transition (work order)

Executor: cold Sonnet agent. You have NO prior context on this
problem — that is intentional. Follow this spec; form conclusions
ONLY from the data you compute. Do not consult any narrative
outside this file and the cited artifacts.

## The measured fact (given, exact, cross-checked)
For a family of integer "capacity" values C, an exact instrument
(wy_core.py in ../w6y_regime/) computes an "edge" M(C) = the maximum
depth m at which a corridor survives. Measured edges:
C=1..10: 4,7,9,12,14,16,19,21,24,26
C=11..26: 57,63,68,71,79,93,108,110,130,132,139,157,163,188,192,205
Extended edges C=27..40 arrive in w7a_new_edges.txt (read it; use
whatever cells are present).

## Established (do not re-litigate)
- M(C) = floor((C+1)/beta), beta = 2 - log2(3) = 0.4150375, is EXACT
  for C=1..10 (residual 0/10) and BREAKS at C=11 (jumps 26->57).
- The 306-denominator convergent does NOT rescue it (same slope,
  better rational; verified).
- r(C)/(C+1) does NOT converge (rules out a smooth linear correction).

## Your tasks (frozen — report what the data says, misses included)
1. **Increment word.** d(C)=M(C)-M(C-1) for C>=11. Classify each as
   a 2-symbol word by a threshold you SELECT and justify from the
   data's own bimodality (report the histogram). Compute symbol
   density and test whether it stabilizes as more cells are added.
2. **Beatty/Sturmian test.** Is the word Sturmian (each length-n
   factor count = n+1)? Compute the factor complexity p(n) for
   n=1..5. Is the density an algebraic number near a natural constant
   (candidates to TEST, not assume: beta=0.415, 2beta-... , 1/phi,
   {C*beta} fractional-part patterns)? Report the closest match and
   its error.
3. **Positional law.** At which C do the "high" increments occur? Test
   whether high-symbol positions follow a Beatty sequence
   floor(n*k)+c for some constant k — fit k, report residuals.
4. **Second-order slope.** Fit M(C) ~ a*C^p (power law) and
   M(C) ~ a*C + b*C*log(C) — report which the data prefers and the
   exponent/coefficients with residuals. This distinguishes a
   genuine super-linear regime from an artifact.

## Rules
- Exact integer arithmetic on M(C); no floats in the edge values.
- Every conclusion carries its residual/error. "Inconclusive at this
  N" is a valid, expected answer — the word may be too short.
- Write findings to w7a_renorm/W7A_FINDINGS.md. Do not edit anything
  outside w7a_renorm/. No commits.
- Final message: the increment-word classification, the Sturmian
  verdict, the density constant + error, the positional-law fit, and
  which growth model M(C) obeys — each with the number that backs it.
