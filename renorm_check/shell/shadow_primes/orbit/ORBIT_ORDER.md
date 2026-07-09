# SHADOW-ORBIT — Why is prime 19 suppressed? The stationary orbit distribution mod p (work order)

Executor: cold Sonnet agent. Exact integer arithmetic. Adversarial-honest:
the goal is a MECHANISM for a measured anomaly, and "no mechanism found,
19 remains empirically anomalous" is a valid verdict. Every claim carries
a number.

## The established anomaly (given, from SHADOW_FINDINGS.md)
Along Collatz descents, prime p divides (3x+1) at a "hit density". Baseline
= 1/p (derived: a hit needs x ≡ -3^{-1} mod p, exactly 1 residue class).
MEASURED: p=19 hits at ~28.5% BELOW its 1/p baseline -- the only prime whose
CI robustly excludes 1/p, and with the strongest descent-position trend
(thins toward 1, t=-15.5). p=11,13,19 all show real deviation; 19 is extreme.
Ruled out already: pure size; "2 is a primitive root" alone (true for
5,11,13,29,37 which behave normally).

## The hypothesis to TEST
The 1/p baseline assumes the trajectory's value is EQUIDISTRIBUTED mod p.
It may not be. The map x -> 3x+1 -> /2^{v2} induces a dynamics on Z/pZ whose
STATIONARY distribution may be non-uniform, and specifically may put LESS
mass on the hit-residue h_p = -3^{-1} mod p than uniform does. If so, the
suppression = (uniform mass at h_p) - (stationary mass at h_p), and 19's
stationary distribution has a "hole" at its hit-residue.

## Tasks
1. **Empirical stationary distribution mod p.** Over a large trajectory
   sample (reuse/extend the SHADOW harness; >=5000 starts, or one very long
   concatenated orbit), histogram the odd-value residue mod p at every step,
   for p in {5,7,11,13,17,19,23,29,31,37,41,43}. Normalize. This is the
   measured stationary distribution s_p(r).
2. **The hole test.** For each p: compare s_p(h_p) [stationary mass at the
   hit residue] to 1/p [uniform]. Compute suppression = 1 - p*s_p(h_p).
   PREDICT: this suppression should MATCH the measured hit-density
   deviation from task-0 (i.e. the shadow-prime density anomaly IS the
   stationary-hole). Report the correlation across all p between
   "stationary hole at h_p" and "measured hit-density deviation". A tight
   match confirms the mechanism.
3. **Rank and isolate.** Rank primes by stationary-hole depth. Is 19 the
   extreme? Are 11,13 next (matching SHADOW's finding)? What distinguishes
   the holed primes -- test candidate invariants: ord(2 mod p), ord(3 mod p),
   whether ord(2)=ord(3), the multiplicative relationship of 2,3,h_p, the
   2-adic structure of the v2 distribution mod (p-1). Report which invariant
   (if any) predicts hole-depth across ALL tested primes, with residuals.
4. **The map-on-residues operator.** Build the exact transition operator on
   Z/pZ for the odd-map (accounting for the v2 division: from residue r, the
   image is (3r+1)*2^{-v2} but v2 depends on the actual integer, not r alone
   -- approximate by averaging over the v2 distribution, OR build the exact
   operator on Z/(p*2^k)Z for small k and marginalize). Compute its
   stationary eigenvector; does it reproduce the empirical hole at 19? This
   tests whether the hole is a property of the RESIDUE DYNAMICS alone.
5. **Predictive check.** If an invariant from task 3 predicts hole-depth,
   use it to PREDICT which primes in {41,43,47,53,...} are most suppressed,
   then MEASURE those and report hit/miss. A confirmed prediction is the
   difference between "19 is weird" and "here is the law of which primes
   Collatz starves."

## Rules
Exact arithmetic. Report sample sizes, CIs, correlation coefficients.
"Anomaly persists without mechanism" is an honest valid verdict -- do not
manufacture a law. Work only in shell/shadow_primes/orbit/. Findings ->
ORBIT_FINDINGS.md. No commits.

Final message: the stationary-hole table, the correlation between hole-depth
and measured hit-density deviation, the invariant (if any) that predicts
hole-depth, the residue-operator eigenvector verdict for p=19, and the
predictive check hit/miss on new primes.
