"""
Gate 2 -- Converse / exclusivity gate.

Over ALL odd x < 10^7 (5,000,000 odd numbers), compute brute-force
one-step S(x) and check whether S(x) == 1. Independently determine
whether x is of the form (4^k - 1)/3 via membership in a precomputed
set. Compare: the set of x with S(x)=1 must EXACTLY equal the species
set below 10^7.

Report false positives (x in species-set-membership but S(x) != 1 --
should be impossible) and false negatives (S(x) == 1 but x not in
species set) -- expect ZERO of each.

Then test a handful of random HUGE odd x (hundreds to thousands of
digits) confirming S(x) != 1 for all of them (one step only, cheap
even for huge x).

Efficient implementation: precompute the species set below 10^7 (there
are only ~12 members: (4^k-1)/3 < 10^7 for k up to ~11), and iterate
all 5,000,000 odd x with a tight pure-Python loop computing S(x)
directly (this is the honest brute force the spec calls for -- no
shortcutting via the closed-form test here, since gate 3 is what
introduces and validates the closed-form shortcut separately).
"""

import sys
import time
import random

sys.path.insert(0, "/mnt/ForgeRealm/collatz-experimental-data/renorm_check/shell/descent_rule")
from descent_common import species_member, one_odd_step, Timer

OUT_PATH = "/mnt/ForgeRealm/collatz-experimental-data/renorm_check/shell/descent_rule/gate2_results.txt"

LIMIT = 10 ** 7


def build_species_set_below(limit):
    """All (4^k-1)/3 values strictly less than `limit`, k=1,2,3,...
    Returns (set_of_values, dict k->value) for k in range covered."""
    s = set()
    k_to_x = {}
    k = 1
    while True:
        x = species_member(k)
        if x >= limit:
            break
        s.add(x)
        k_to_x[k] = x
        k += 1
    return s, k_to_x


def main():
    lines = []
    def log(s):
        print(s)
        lines.append(s)

    log("=" * 70)
    log("GATE 2 -- Converse / exclusivity gate")
    log("=" * 70)

    species_set, k_to_x = build_species_set_below(LIMIT)
    log(f"Species members below {LIMIT:,}: {len(species_set)}")
    log(f"  k -> x: {k_to_x}")

    false_positives = []  # x in species_set but S(x) != 1
    false_negatives = []  # S(x) == 1 but x not in species_set
    n_tested = 0
    n_species_hits = 0
    n_s_eq_1 = 0

    t0 = time.perf_counter()

    # Iterate all odd x < LIMIT: x = 1, 3, 5, ..., LIMIT-1
    for x in range(1, LIMIT, 2):
        n_tested += 1
        s_x = one_odd_step(x)
        is_s1 = (s_x == 1)
        in_species = (x in species_set)

        if is_s1:
            n_s_eq_1 += 1
        if in_species:
            n_species_hits += 1

        if in_species and not is_s1:
            false_positives.append(x)
        if is_s1 and not in_species:
            false_negatives.append(x)

    t_elapsed = time.perf_counter() - t0

    log(f"Total odd x tested (x = 1,3,5,...,{LIMIT-1}): {n_tested:,}")
    log(f"Number of x with S(x) == 1 (brute): {n_s_eq_1}")
    log(f"Number of x matching species-set membership: {n_species_hits}")
    log(f"False positives (species-membership but S(x)!=1): "
        f"{len(false_positives)}  values={false_positives}")
    log(f"False negatives (S(x)==1 but not species-membership): "
        f"{len(false_negatives)}  values={false_negatives}")
    log(f"Elapsed wall clock for full sweep: {t_elapsed:.3f}s "
        f"({n_tested / t_elapsed:,.0f} x/sec)")

    gate2_exact_match = (len(false_positives) == 0 and len(false_negatives) == 0
                         and n_s_eq_1 == n_species_hits)
    log(f"EXACT SET MATCH (0 FP, 0 FN): {gate2_exact_match}")

    # --- Random huge odd x test ---
    log("-" * 70)
    log("Random HUGE odd x test (hundreds to thousands of digits)")
    log("-" * 70)

    random.seed(20260705)  # today's mission date, for reproducibility
    huge_test_results = []
    digit_targets = [200, 500, 1000, 1500, 2000, 3000] * 3  # 18 samples > "10-20" requested minimum
    # trim to a clean count between 10 and 20 as spec asks ("10-20")
    digit_targets = digit_targets[:18]

    for i, ndigits in enumerate(digit_targets):
        nbits = int(ndigits / 0.30103) + 1
        # random odd integer with ~nbits bits
        candidate = random.getrandbits(nbits) | 1  # force odd
        candidate |= (1 << (nbits - 1))  # force top bit so bit length is as expected
        with Timer() as t:
            s_val = one_odd_step(candidate)
        is_member = (candidate in species_set)  # trivially False, x is huge & random
        # Also cross check with closed form to see if by freak chance it's
        # a species member (it won't be, but check honestly)
        n = 3 * candidate + 1
        closed_form_says_species = (n & (n - 1) == 0) and ((n.bit_length() - 1) % 2 == 0)
        result_ok = (s_val != 1)
        huge_test_results.append(
            (i, candidate.bit_length(), s_val != 1, closed_form_says_species, t.elapsed)
        )
        log(f"  sample {i:2d}: x.bit_length()={candidate.bit_length():5d}  "
            f"S(x)!=1: {result_ok}  closed_form_species={closed_form_says_species}  "
            f"t={t.elapsed:.6f}s")

    all_huge_not_species = all(r[2] for r in huge_test_results)
    log(f"All {len(huge_test_results)} random huge x have S(x) != 1: "
        f"{all_huge_not_species}")

    log("=" * 70)
    log("GATE 2 SUMMARY")
    log("=" * 70)
    log(f"Odd x tested < {LIMIT:,}: {n_tested:,}")
    log(f"Species members found (brute S(x)==1): {n_s_eq_1}")
    log(f"False positives: {len(false_positives)}")
    log(f"False negatives: {len(false_negatives)}")
    log(f"Exact match: {gate2_exact_match}")
    log(f"Huge random x sampled: {len(huge_test_results)}, all S(x)!=1: "
        f"{all_huge_not_species}")
    log(f"Sweep wall clock: {t_elapsed:.3f}s")
    log("=" * 70)

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\nWrote results to {OUT_PATH}")

    ok = gate2_exact_match and all_huge_not_species
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
