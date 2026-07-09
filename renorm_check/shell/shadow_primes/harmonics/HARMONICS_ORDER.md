# SHADOW-HARMONICS — Are anomalous primes harmonics of the Sturmian heartbeat? (work order)

Executor: cold Sonnet agent. Exact integer arithmetic, large samples with
CIs. Adversarial-honest: a census that finds NO harmonic structure is a
full, valid, important result. Do NOT reverse-fit a harmonic law onto a
scattered set. Every claim carries a number.

## MANDATORY OUTPUT DISCIPLINE (read renorm_check/shell/LEDGER_SYNTHESIS_POLICY.md)
You MUST write, before finishing:
- a LEDGER entry appended to renorm_check/IMPLEMENTATION_LEDGER.md: the
  PROCESS receipt -- approaches tried, paths abandoned AND WHY, bugs and
  how caught, course corrections, exact artifact paths, "not complete
  until" gaps. Chronological, receipt-grade.
- a SYNTHESIS entry appended to renorm_check/SYNTHESIS.md: the interpreted
  verdict in context.
Your chat summary is a courtesy only; these two files are the record. An
agent that only writes a findings file has NOT finished.

## Established (given; verify the seeds)
- Shadow primes: p divides (3x+1) at hit-density ~1/p (derived: 1 residue
  class). MEASURED anomaly (renorm_check/shell/shadow_primes/SHADOW_FINDINGS.md,
  results.json): p=19 is suppressed ~28.5% below 1/p (CI-robust); p=11,13
  also deviate. Reuse harness.py / analyze.py there.
- The Sturmian heartbeat: 53-step period (84/53 = 6th convergent of
  log2(3)), 22 support + 31 drop. Spectral radius of the killed-survivor
  graph locks at rho=0.960647 (gap 0.039353); the gap-per-step decays as
  (53/84)^6 (SPECTRAL_RADIUS_RESULTS.txt, COLLATZ_PROOF.md:502). 84/53 sits
  at CONVERGENT INDEX 6 -- exponent = index.

## FROZEN PREDICTION (register before any fitting -- David/orchestrator)
The p=19 suppression magnitude (measured |dev|=0.01499) is conjectured to
equal (53/84)^9 = 0.015848 (within one density CI). Test this as ONE
specific falsifiable point. It may be a coincidence -- report hit or miss
honestly, do not privilege it.

## Tasks
1. **Full anomaly census.** Measure hit-density vs 1/p for ALL primes p up
   to at least 200 (exclude p=3, identically forbidden). Large sample
   (>=20000 starts, or long concatenated orbits) with CIs corrected for
   within-trajectory autocorrelation (one independent sample/trajectory
   or block-bootstrap). Flag every prime whose CI-robust deviation from
   1/p exceeds sampling error. Rank by |deviation|. Is 19 the extreme? How
   many anomalous primes are there, and at what magnitudes?
2. **The harmonic test (the point).** For the anomalous set, test whether
   they relate to the heartbeat/convergent arithmetic. Candidate structural
   predictors (TEST each, report which if any predicts anomaly across ALL
   primes, with residuals): ord(2 mod p); ord(3 mod p); whether
   ord(2)=ord(3); p mod 53; the multiplicative order of (2^k*3^j) that
   generates the hit-residue; whether p divides 2^53-3^something or a
   convergent numerator/denominator (53,84,306,485,665,...); resonance
   p | (2^a - 3^b) for small a,b near the heartbeat. Does the ANOMALOUS
   set cluster on any of these, vs the non-anomalous set as control?
3. **Harmonic magnitude law.** IF anomalous primes cluster structurally:
   does the suppression MAGNITUDE follow a (53/84)^k law for integer k that
   depends on the prime's heartbeat relationship (e.g. k = some function of
   ord(2 mod p) or p mod 53)? Fit k per anomalous prime; is k integer and
   structurally predicted, or scattered? (The frozen 19->k=9 prediction is
   one row of this table.)
4. **Spectral cross-correlation.** Across all primes, correlate the
   shadow-suppression with heartbeat/spectral quantities. Is there a single
   dynamical object (the orbit's stationary distribution) that produces BOTH
   the spectral radius AND the prime suppression? State the correlation
   coefficient and whether it is structural or coincidental.
5. **Predictive check.** If a harmonic law emerges, PREDICT the anomaly
   status + magnitude of primes in 200-500 you did not use to fit, then
   MEASURE them. Hit/miss is the verdict between "law" and "pattern-match".

## Verdict (required, blunt)
One of: (A) HARMONIC -- anomalous primes are heartbeat harmonics, law
stated + predictively confirmed; (B) ANOMALOUS-BUT-NOT-HARMONIC -- real
anomalies exist but don't relate to the heartbeat (19 is special for
another reason); (C) NO ROBUST ANOMALY BEYOND SAMPLING -- the deviations
wash out at higher N. Back it with census numbers, the predictor residuals,
and the predictive-check hit rate.

## Rules
Exact arithmetic; CIs corrected for autocorrelation; frozen prediction
registered before fitting; predictive check on held-out primes is decisive.
Work only in shell/shadow_primes/harmonics/. No commits. Ledger + Synthesis
are mandatory (above).

Final message: the anomaly census (ranked), the harmonic-predictor verdict,
the (53/84)^k magnitude-law table incl. the 19->k=9 test, the spectral
cross-correlation coefficient, the held-out predictive hit rate, and the
A/B/C verdict.
