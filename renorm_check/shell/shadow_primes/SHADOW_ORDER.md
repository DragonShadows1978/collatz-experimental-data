# SHADOW-PRIMES — the shadow-prime spectrum of the Collatz descent (work order)

Executor: cold Sonnet agent. No prior narrative. Exact integer
arithmetic throughout. Every claim carries a number (density, error,
correlation coefficient with CI). "No pattern detectable at this N" is
a valid, expected verdict.

## Origin of the question (David Perry)
The Collatz odd-map is S(x) = (3x+1)/2^v2(3x+1). Everyone studies the
divisor 2 (v2 = the "credit word"). NOBODY systematically studies the
OTHER primes in (3x+1). This round does.

## Established seed fact (given, verify it yourself first)
3x+1 ≡ 1 (mod 3) always, so v3(3x+1) = 0 at EVERY step of EVERY
trajectory — the prime 3 is structurally forbidden from the numerator.
Confirm this on 1000 trajectories as gate 0 (must be 0 exceptions).

## Definitions
For a trajectory n0 -> ... -> 1 (n0 odd), at each step form m = 3*x+1
and record v_p(m) = the p-adic valuation of m, for p in {2,5,7,11,13,
17,19,23}. (Note v3 ≡ 0.) The "v_p word" of the trajectory is the
sequence of v_p(m) over steps. v2 is the known credit word.

## Tasks
1. **Shadow-prime density law.** Over a large sample (>= 5000 odd
   starts up to ~10^6, plus a few deep ones like 27, 703, 6171, 837799),
   measure for each prime p: the fraction of steps with v_p >= 1
   ("hit density"), and mean v_p per step. TEST the hypothesis that
   hit-density = 1/(p-1) (the equidistribution prediction: 3x+1 mod p
   hits 0 with prob ~1/(p-1) since x ranges over units-ish). Report
   measured vs 1/(p-1) vs 1/p for each p, with error.
2. **The v2 correlation (the real question).** Does a shadow prime's
   appearance correlate with the v2 credit-word structure — specifically
   with support steps (v2=1) vs drop steps (v2>=2)? Compute, per prime,
   P(v_p>=1 | v2=1) vs P(v_p>=1 | v2>=2), and a correlation coefficient
   between the v2 word and each v_p word (aligned by step). Is there
   phase structure (do shadow primes cluster at heartbeat positions)?
3. **Co-occurrence among shadow primes.** Do 5 and 7 (and others) avoid,
   cluster, or ignore each other? Build the pairwise co-occurrence matrix
   (observed vs independent-expected) across all steps in the sample.
4. **Descent-position structure.** Does shadow-prime density change along
   the descent (early steps near n0 vs late steps near 1)? Bin by
   fractional descent position; report density-vs-position per prime.
5. **The forbidden-prime generalization.** 3 is forbidden because the map
   is 3x+1. TEST: is there any OTHER structurally suppressed or enhanced
   prime? (e.g. does 3x+1 avoid or prefer any residue classes that
   suppress a prime below its 1/(p-1) baseline?) Report any prime whose
   density deviates from 1/(p-1) by more than sampling error, with the
   mod-arithmetic explanation if you can derive it.

## Rules
Exact integers. Trajectories that don't reach 1 within a large step
cap: note and exclude (shouldn't happen under ~10^6 but guard it).
Report sample sizes and CIs. Work only in shell/shadow_primes/.
Findings -> SHADOW_FINDINGS.md. No commits.

Final message: the density-vs-1/(p-1) table, the v2-correlation verdict
(is shadow-prime appearance tied to credit-word phase — yes/no with
numbers), the co-occurrence matrix highlights, the descent-position
trend, and any structurally special prime beyond 3.
