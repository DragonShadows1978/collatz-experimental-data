"""
Gate 1 -- Direct construction gate.

For k = 1 .. K_large, construct x = (4^k - 1)/3 exactly, confirm:
  (a) 3x+1 == 4**k  (exact integer equality)
  (b) 3x+1 is a power of two (bitwise: n & (n-1) == 0)
  (c) the exponent (bit_length-1) is even
  (d) one real odd-step S(x) actually yields 1 (brute simulation, not the
      closed-form shortcut -- this is the "real Collatz map" check the
      spec asks for)

Pushes k until x reaches several thousand DECIMAL DIGITS (x has roughly
2k bits, i.e. ~2k*log10(2) =~ 0.602*k decimal digits). Reports the
largest k and bit-length reached plus wall clock and RSS.

Exact integer arithmetic throughout -- no floats anywhere load-bearing.
"""

import sys
import time
import resource

sys.path.insert(0, "/mnt/ForgeRealm/collatz-experimental-data/renorm_check/shell/descent_rule")
from descent_common import species_member, one_odd_step, is_power_of_two, Timer

OUT_PATH = "/mnt/ForgeRealm/collatz-experimental-data/renorm_check/shell/descent_rule/gate1_results.txt"


def check_one_k(k):
    """Run all four checks for a single k. Returns (ok, x_bitlen, details)."""
    x = species_member(k)

    # (a) exact integer equality 3x+1 == 4**k
    n = 3 * x + 1
    four_k = 4 ** k
    check_a = (n == four_k)

    # (b) power-of-two bitwise test
    check_b = is_power_of_two(n)

    # (c) exponent even
    j = n.bit_length() - 1
    check_c = (j % 2 == 0)

    # (d) real one odd-step brute simulation actually yields 1
    s_x = one_odd_step(x)
    check_d = (s_x == 1)

    ok = check_a and check_b and check_c and check_d
    return ok, x.bit_length(), (check_a, check_b, check_c, check_d)


def main():
    lines = []
    def log(s):
        print(s)
        lines.append(s)

    log("=" * 70)
    log("GATE 1 -- Direct construction gate")
    log("=" * 70)

    # Milestone k values to report explicitly (log-spaced), then push to
    # the maximum k that's still cheap. x has bit_length ~= 2k, so k in
    # the thousands already gives x thousands of bits. We push k into the
    # tens of thousands to get x with tens of thousands of bits, and see
    # how far is "fast/cheap" as instructed.
    milestone_ks = [1, 2, 5, 10, 50, 100, 500, 1000, 1500, 2000, 5000,
                    10000, 20000, 50000, 100000]

    all_ok = True
    max_k_verified = 0
    max_bitlen_verified = 0

    t_total_start = time.perf_counter()

    for k in milestone_ks:
        with Timer() as t:
            ok, bitlen, details = check_one_k(k)
        status = "PASS" if ok else "FAIL"
        log(f"k={k:>7}  x.bit_length()={bitlen:>7}  "
            f"checks(3x+1==4^k, pow2, j_even, S(x)==1)={details}  "
            f"[{status}]  t={t.elapsed:.6f}s")
        if not ok:
            all_ok = False
        else:
            max_k_verified = k
            max_bitlen_verified = bitlen

    # Now push further: find the largest k reachable within a modest time
    # budget by doubling, to see how far is fast/cheap, per instructions.
    log("-" * 70)
    log("Pushing further: doubling k until per-k check time exceeds ~5s")
    log("-" * 70)

    k = 100000
    push_budget_seconds = 5.0
    while True:
        k2 = k * 2
        with Timer() as t:
            ok, bitlen, details = check_one_k(k2)
        status = "PASS" if ok else "FAIL"
        log(f"k={k2:>9}  x.bit_length()={bitlen:>9}  "
            f"checks={details}  [{status}]  t={t.elapsed:.6f}s")
        if not ok:
            all_ok = False
            break
        max_k_verified = k2
        max_bitlen_verified = bitlen
        if t.elapsed > push_budget_seconds:
            log(f"Stopping push: t={t.elapsed:.6f}s exceeded budget "
                f"{push_budget_seconds}s at k={k2}")
            break
        k = k2
        if k2 > 5_000_000:
            log("Stopping push: reached hard cap k=5,000,000 for this gate")
            break

    t_total_elapsed = time.perf_counter() - t_total_start

    rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_mb = rss_kb / 1024.0

    log("=" * 70)
    log("GATE 1 SUMMARY")
    log("=" * 70)
    log(f"All checks passed: {all_ok}")
    log(f"Largest k verified: {max_k_verified}")
    log(f"Largest x.bit_length() verified: {max_bitlen_verified}")
    log(f"Approx decimal digits of largest x: "
        f"{int(max_bitlen_verified * 0.30103)}")
    log(f"Total wall clock for gate 1: {t_total_elapsed:.4f}s")
    log(f"Peak RSS (this process): {rss_mb:.2f} MB "
        f"({rss_kb} KB, via resource.getrusage RUSAGE_SELF.ru_maxrss)")
    log("=" * 70)

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\nWrote results to {OUT_PATH}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
