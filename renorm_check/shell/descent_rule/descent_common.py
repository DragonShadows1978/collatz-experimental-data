"""
descent_common.py

Shared helpers for the One-Step Descent Species mission
(see DESCENT_RULE_SPEC.md in this directory).

Exact integer arithmetic only. No floats anywhere in load-bearing code.
"""

import sys
import time

# Python 3.11+ guards int<->str conversion above 4300 digits (a DoS
# mitigation). This mission legitimately builds integers with hundreds of
# thousands of digits and needs str(x)/len(str(x)) for reporting decimal
# digit counts. Raise the cap. This is display/reporting only -- no
# load-bearing arithmetic anywhere in this mission ever goes through
# str() (all constructor/certifier logic is pure int arithmetic:
# *, +, //, %, &, bit_length()).
sys.set_int_max_str_digits(2_000_000)


def species_member(k):
    """Construct x = (4^k - 1) / 3 for integer k >= 1. Exact integer division
    (verified exact, not floor division masking a remainder, by the caller's
    gates); returns a native Python int (arbitrary precision)."""
    if k < 1:
        raise ValueError("k must be >= 1")
    num = (4 ** k) - 1
    assert num % 3 == 0, f"(4^{k}-1) not divisible by 3 -- should be impossible"
    return num // 3


def one_odd_step(x):
    """Brute-force ground truth: apply ONE odd-step of the Collatz map to
    odd positive integer x. S(x) = (3x+1) / 2^v2(3x+1).

    Returns the resulting integer (which is odd, since all factors of two
    are divided out). This is a real trajectory computation (one step),
    used only as ground truth in gates 2/3, never inside the closed-form
    certifier itself.
    """
    n = 3 * x + 1
    # divide out all factors of 2 -- exact integer bit-shifting, no floats
    while n & 1 == 0:
        n >>= 1
    return n


def is_power_of_two(n):
    """Exact bitwise power-of-two test for positive integer n."""
    return n > 0 and (n & (n - 1)) == 0


def is_one_step_species(x):
    """THE CLOSED-FORM CERTIFIER (Gate 3).

    Determines whether odd positive integer x satisfies S(x) = 1 in
    exactly one odd-step, WITHOUT running any trajectory / loop.

    Method (per spec): compute n = 3x+1; test n is a power of two via
    n & (n-1) == 0; if so, exponent j = n.bit_length() - 1; test j even;
    if so k = j // 2, return (True, k). Otherwise (False, None).

    This is O(digits) work: one multiply, one bitwise AND, one
    bit_length() call -- all near-linear (or better, for bit_length) in
    the number of bits of x. No while-loop, no repeated division.
    """
    n = 3 * x + 1
    if not is_power_of_two(n):
        return (False, None)
    j = n.bit_length() - 1
    if j % 2 != 0:
        return (False, None)
    k = j // 2
    return (True, k)


class Timer:
    """Trivial wall-clock context manager, wraps time.perf_counter()."""

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *exc):
        self.elapsed = time.perf_counter() - self.start
        return False
