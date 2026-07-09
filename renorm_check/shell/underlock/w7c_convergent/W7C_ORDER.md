# W7C — One Convergent Scheme? Spectral Exponent vs Edge-Jump Rate (work order)

Executor: cold Sonnet agent. No prior narrative; conclusions ONLY from
the numbers you compute. Every claim carries a residual/error.

## The two established facts (given, verified, on disk)
FACT 1 (spectral, from COLLATZ_PROOF.md:502 + SPECTRAL_RADIUS_RESULTS.txt):
  A "killed-survivor" operator has spectral gap 1-rho(m) decaying as
  ~ c * b^m. Fitted b = 0.063099. It matches (53/84)^6 = 0.063093 to
  0.01%. Here 84/53 is a continued-fraction convergent of log2(3)
  (53/84 = its reciprocal), and 53 is the "heartbeat" period. The
  EXPONENT 6 is flagged in the proof as an unexplained structural
  constant. Raw rho data: renorm_check/rho_sweep_m3_C1_200.csv,
  rho_sweep_m5_anchors.csv, and the two-curve table in
  SPECTRAL_RADIUS_RESULTS.txt.
FACT 2 (edge-jump, measured this session):
  A corridor "edge" M(C): exact for C<=10 as M(C)=floor((C+1)/beta),
  beta=2-log2(3). Breaks at C=11. Full edges:
  C=1..10: 4,7,9,12,14,16,19,21,24,26
  C=11..28: 57,63,68,71,79,93,108,110,130,132,139,157,163,188,192,205,208,263
  The BIG-increment ("jump") positions among C=11..28 sit at word-index
  n = {4,5,6,8,11,13,15,17} which fit floor(9n/4)+2 to +-1. So the jump
  SPACING rate is ~9/4 = 2.25. (More edges C=29+ may land in
  ../w7a_renorm/w7a_new_edges.txt during your run; use them if present.)

## THE QUESTION
Are FACT 1's structure (heartbeat 53, convergent 84/53, exponent 6) and
FACT 2's structure (base slope 1/beta, jump-rate 9/4) two shadows of ONE
convergent quantization of the log2(3) incommensurability?

## Tasks (all exact arithmetic; report the number for each)
1. **CF spine.** Compute the continued fraction of log2(3), of beta, and
   of 1/beta; list convergents p_k/q_k with k. Locate 53, 84, 22, 306,
   665 in these. Tabulate which quantity each convergent belongs to.
2. **The exponent 6.** Re-derive b from the rho data yourself (regress
   ln(1-rho) vs m on the locked/asymptotic regime; report the fit and
   CI). Test (53/84)^6 AND alternatives: is 6 = (sum of CF partial
   quotients up to the 84/53 convergent)? = index of that convergent?
   = something else? Test (q/p)^k for the convergent (p,q)=(84,53) and
   neighbors, k=1..10 — which (convergent, exponent) pair best fits b,
   and is 6 special or a coincidence of THIS convergent?
3. **The 9/4.** Is 9/4 a convergent (or mediant, or semiconvergent) of
   any of: log2(3), beta, 1/beta, log2(3)-1, 1/(2-log2 3)? Compute
   mediants/semiconvergents (Stern-Brocot neighbors) of the relevant
   convergents and see if 9/4 appears. Report the closest structural
   hit and its error. If 9/4 is NOT in any of these, say so plainly.
4. **The bridge test (the point).** Both b and 9/4 are per-heartbeat
   quantities. Test whether ONE scheme generates both: e.g. does the
   jump-rate relate to the spectral exponent as
   rate = f(6, 53, 84) for a simple f? Candidates to TEST (not assume):
   9/4 vs 6*(something); 2.25 vs 84/53 - fraction; the drift of the
   measured jump-rate as C grows (does 9/4 -> 53/22=2.409, i.e. toward
   the base convergent, or lock at 2.25?) using ALL available edges
   including any new C=29+. Report whether the jump-rate is CONVERGING
   to a log2(3) convergent or STABLE at a non-convergent rational.
5. **Verdict.** One of: (A) unified — both are the same convergent
   scheme, state it exactly; (B) related but distinct convergents of
   the same number; (C) 9/4 is genuinely outside log2(3)'s convergent
   structure (a second incommensurability). Back the verdict with the
   residuals from tasks 1-4.

## Rules
Exact arithmetic (Fraction / mpmath high precision for CF). No floats
near a floor or a CF step. Every hypothesis reports its error, and
"coincidence at this precision" is a valid verdict. Work only in
w7c_convergent/. Findings -> W7C_FINDINGS.md. No commits.

Final message: the CF spine table, the re-derived b and its best
(convergent,exponent) fit, the 9/4 structural search result, the
jump-rate drift verdict, and the A/B/C verdict with numbers.
