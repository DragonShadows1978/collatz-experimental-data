"""
Gate 3 -- Closed-form certifier.

is_one_step_species(x) (implemented in descent_common.py) determines
species membership using ONLY:
    n = 3x+1
    n & (n-1) == 0   (power of two test)
    j = n.bit_length() - 1
    j even -> (True, k=j//2)   else -> (False, None)

No trajectory simulation, no loop -- O(digits) work.

This gate:
  1. Re-checks agreement with brute one-step simulation on EVERY x from
     gate 2 (all odd x < 10^7, plus the same huge random x set) -- must
     be 100% agreement.
  2. Certifies a handful of true species members at 1000+ digits
     (constructed via (4^k-1)/3 for k chosen so x has 1000+ digits) --
     must return (True, k) correctly.
  3. Rejects a handful of ~1000+ digit NON-members (nearby odd numbers
     not of that form, and random large odd numbers) -- must return
     (False, None).
  4. Times is_one_step_species across a range of digit lengths (10, 100,
     1000, 10000, 100000 digits) to demonstrate near-linear / O(digits)
     scaling, NOT trajectory-simulation-like behavior. Presented as a
     timing table.
"""

import sys
import time
import random
import math

sys.path.insert(0, "/mnt/ForgeRealm/collatz-experimental-data/renorm_check/shell/descent_rule")
from descent_common import species_member, one_odd_step, is_one_step_species, Timer

OUT_PATH = "/mnt/ForgeRealm/collatz-experimental-data/renorm_check/shell/descent_rule/gate3_results.txt"

LIMIT = 10 ** 7


def part1_agreement_check(log):
    """Agreement between is_one_step_species and brute one_odd_step on
    every odd x < 10^7, plus the same huge-random-x set gate 2 used
    (re-derived here with the same seed for exact reproducibility)."""
    log("-" * 70)
    log("Part 1: agreement with brute simulation, all odd x < 10^7")
    log("-" * 70)

    mismatches = []
    n_tested = 0
    t0 = time.perf_counter()
    for x in range(1, LIMIT, 2):
        n_tested += 1
        brute_is_1 = (one_odd_step(x) == 1)
        cert_says, cert_k = is_one_step_species(x)
        if brute_is_1 != cert_says:
            mismatches.append((x, brute_is_1, cert_says, cert_k))
    t_elapsed = time.perf_counter() - t0

    log(f"Tested {n_tested:,} odd x < {LIMIT:,}")
    log(f"Mismatches (brute vs certifier): {len(mismatches)}  {mismatches[:20]}")
    log(f"Elapsed: {t_elapsed:.3f}s")

    # Same huge random x set as gate 2 (same seed, same construction, so
    # this reproduces exactly rather than re-reading gate2's output file)
    log("Huge random x set (same seed as gate 2, seed=20260705):")
    random.seed(20260705)
    digit_targets = ([200, 500, 1000, 1500, 2000, 3000] * 3)[:18]
    huge_mismatches = []
    for i, ndigits in enumerate(digit_targets):
        nbits = int(ndigits / 0.30103) + 1
        candidate = random.getrandbits(nbits) | 1
        candidate |= (1 << (nbits - 1))
        brute_is_1 = (one_odd_step(candidate) == 1)
        cert_says, cert_k = is_one_step_species(candidate)
        agree = (brute_is_1 == cert_says)
        log(f"  sample {i:2d}: bit_length={candidate.bit_length():5d}  "
            f"brute_S=1:{brute_is_1}  cert:{cert_says},{cert_k}  agree={agree}")
        if not agree:
            huge_mismatches.append((i, candidate, brute_is_1, cert_says, cert_k))

    log(f"Huge-x mismatches: {len(huge_mismatches)}")

    total_mismatches = len(mismatches) + len(huge_mismatches)
    agreement_rate = 1.0 - (total_mismatches / (n_tested + len(digit_targets)))
    log(f"TOTAL mismatches across all {n_tested + len(digit_targets):,} tests: "
        f"{total_mismatches}")
    log(f"Agreement rate: {agreement_rate * 100:.10f}%")
    return total_mismatches == 0, agreement_rate


def part2_certify_thousand_digit_members(log):
    log("-" * 70)
    log("Part 2: certify true species members at 1000+ digits")
    log("-" * 70)

    # x=(4^k-1)/3 has bit_length ~= 2k. For 1000+ digits (~3322+ bits),
    # need k >~ 1662. Pick a spread of k values well past that floor.
    test_ks = [1662, 1700, 2000, 3000, 5000, 10000]
    all_correct = True
    for k in test_ks:
        x = species_member(k)
        ndigits = len(str(x))
        with Timer() as t:
            says, found_k = is_one_step_species(x)
        correct = (says is True and found_k == k)
        all_correct = all_correct and correct
        log(f"  k={k:6d}  x.bit_length()={x.bit_length():6d}  "
            f"decimal_digits={ndigits:6d}  certifier=({says},{found_k})  "
            f"correct={correct}  t={t.elapsed:.6f}s")
    log(f"All {len(test_ks)} thousand+-digit species members correctly certified: "
        f"{all_correct}")
    return all_correct


def part3_reject_thousand_digit_nonmembers(log):
    log("-" * 70)
    log("Part 3: reject ~1000+ digit NON-members")
    log("-" * 70)

    all_correct = True
    tests = []

    # (a) Nearby odd numbers next to a true species member (off by 2, 4, ...)
    k = 1700  # x has ~3400 bits, comfortably 1000+ digits
    base = species_member(k)
    for delta in [2, -2, 4, -4, 100, -100]:
        candidate = base + delta
        if candidate % 2 == 0:
            candidate += 1  # keep it odd
        tests.append(("near-species+%d" % delta, candidate))

    # (b) Random large odd numbers, unrelated to any species member
    random.seed(99999999)
    for ndigits in [1000, 1500, 2000, 3000]:
        nbits = int(ndigits / 0.30103) + 1
        candidate = random.getrandbits(nbits) | 1
        candidate |= (1 << (nbits - 1))
        tests.append(("random-%ddigits" % ndigits, candidate))

    for label, x in tests:
        with Timer() as t:
            says, found_k = is_one_step_species(x)
        # Cross-check against brute one-step (cheap, one step even for huge x)
        brute_is_1 = (one_odd_step(x) == 1)
        correct = (says is False and found_k is None and not brute_is_1)
        all_correct = all_correct and correct
        log(f"  {label:22s}  bit_length={x.bit_length():6d}  "
            f"certifier=({says},{found_k})  brute_S_eq_1={brute_is_1}  "
            f"correctly_rejected={correct}  t={t.elapsed:.6f}s")

    log(f"All {len(tests)} non-members correctly rejected: {all_correct}")
    return all_correct


def part4_timing_table(log):
    log("-" * 70)
    log("Part 4: timing vs digit length (demonstrates O(digits) scaling,")
    log("        NOT trajectory-simulation-like behavior)")
    log("-" * 70)

    digit_lengths = [10, 100, 1000, 10000, 100000]
    # add one more decade to make the scaling trend crisper, cheap to do
    digit_lengths_extended = digit_lengths + [300000]

    random.seed(424242)
    n_repeats = 5001  # repeat many times for a measurable, averaged timing
    # (single calls at small digit counts are sub-microsecond; averaging
    # over many repeats gives a stable estimate for the table)

    rows = []
    for ndigits in digit_lengths_extended:
        nbits = int(ndigits / 0.30103) + 1
        # Use a species member for consistency (worst case still O(digits):
        # a positive hit still only needs one bit_length() call after the
        # power-of-two test passes; a random non-member returns after the
        # power-of-two test fails, which is even cheaper -- report species
        # members here since that's the more expensive of the two paths.)
        # Choose k so bit_length matches target ~ 2k
        k = max(1, nbits // 2)
        x = species_member(k)
        actual_bits = x.bit_length()
        actual_digits = len(str(x))

        # warm up
        is_one_step_species(x)

        t0 = time.perf_counter()
        for _ in range(n_repeats):
            says, found_k = is_one_step_species(x)
        t_elapsed = time.perf_counter() - t0
        per_call_us = (t_elapsed / n_repeats) * 1e6

        rows.append((ndigits, actual_digits, actual_bits, n_repeats,
                     t_elapsed, per_call_us))
        log(f"  target_digits={ndigits:7d}  actual_digits={actual_digits:7d}  "
            f"bits={actual_bits:7d}  repeats={n_repeats}  "
            f"total_t={t_elapsed:.6f}s  per_call={per_call_us:.3f}us  "
            f"result=({says},{found_k})")

    # Report ratios to show near-linear (or sub-linear, since bit_length()
    # and the bitwise AND are both near-linear-or-better in CPython's
    # bigint implementation) scaling -- NOT the exponential/unbounded-step
    # blowup that trajectory simulation would show for large numbers with
    # long orbits.
    log("")
    log("Scaling check (per_call_time / digits, should stay roughly flat")
    log("or grow much slower than digit count for O(digits)-ish scaling):")
    for (ndigits, actual_digits, actual_bits, n_repeats, t_elapsed,
         per_call_us) in rows:
        ratio = per_call_us / actual_digits if actual_digits else float("nan")
        log(f"  digits={actual_digits:7d}  per_call={per_call_us:10.3f}us  "
            f"per_call/digit={ratio:.6f}us/digit")

    return rows


def main():
    lines = []
    def log(s):
        print(s)
        lines.append(s)

    log("=" * 70)
    log("GATE 3 -- Closed-form certifier")
    log("=" * 70)

    ok1, agreement_rate = part1_agreement_check(log)
    ok2 = part2_certify_thousand_digit_members(log)
    ok3 = part3_reject_thousand_digit_nonmembers(log)
    rows = part4_timing_table(log)

    log("=" * 70)
    log("GATE 3 SUMMARY")
    log("=" * 70)
    log(f"Part 1 (agreement with brute sim, all odd x<10^7 + huge x): "
        f"{ok1}  (agreement_rate={agreement_rate*100:.10f}%)")
    log(f"Part 2 (certify 1000+ digit species members): {ok2}")
    log(f"Part 3 (reject 1000+ digit non-members): {ok3}")
    log(f"Part 4 (timing table): see rows above, "
        f"{len(rows)} digit-length points measured")
    all_ok = ok1 and ok2 and ok3
    log(f"GATE 3 OVERALL: {'PASS' if all_ok else 'FAIL'}")
    log("=" * 70)

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\nWrote results to {OUT_PATH}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
