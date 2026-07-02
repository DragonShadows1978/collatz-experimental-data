from fractions import Fraction
from itertools import product


def affine_data(word):
    """
    Return (A, k, B) for exponent word w.

    F_w(x) = (3^k*x + B) / 2^A

    Recurrence:
        B_{j+1} = 3*B_j + 2^{A_j}
        A_{j+1} = A_j + a_j
    """
    A = 0
    B = 0
    k = 0

    for a in word:
        if a < 1:
            raise ValueError("All exponents must be positive integers.")
        B = 3 * B + (1 << A)
        A += a
        k += 1

    return A, k, B


def action(word):
    """
    Classify a word by comparing 3^k and 2^A.
    """
    A, k, B = affine_data(word)
    two_A = 1 << A
    three_k = 3 ** k

    if three_k > two_A:
        return "positive"
    if three_k < two_A:
        return "contractive"
    return "neutral"


def fixed_point(word):
    """
    Return the exact fixed point x = B / (2^A - 3^k)
    as a Fraction.
    """
    A, k, B = affine_data(word)
    return Fraction(B, (1 << A) - (3 ** k))


def F(word, x):
    """
    Apply the affine block map F_w to x exactly as a Fraction.
    This does not check whether x follows the word as a Collatz
    valuation path. Lock 1 is about the affine repeated engine.
    """
    A, k, B = affine_data(word)
    return Fraction((3 ** k) * x + B, 1 << A)


def verify_positive_engine(word, sample_x_values=(1, 3, 5, 7, 11, 101)):
    """
    Verify the Lock 1 claims for one positive-action word:
    - fixed point is negative;
    - F_w(x) > x for positive sample x.
    """
    A, k, B = affine_data(word)
    two_A = 1 << A
    three_k = 3 ** k

    assert B > 0, f"B should be positive for nonempty word {word}"

    if three_k <= two_A:
        return None

    fp = fixed_point(word)
    assert fp < 0, f"Positive-action word has nonnegative fixed point: {word}, fp={fp}"

    for x in sample_x_values:
        y = F(word, x)
        assert y > x, f"Positive-action word did not increase x: word={word}, x={x}, y={y}"

    return {
        "word": word,
        "A": A,
        "k": k,
        "B": B,
        "2^A": two_A,
        "3^k": three_k,
        "fixed_point": fp,
        "ghost": fp,
    }


def enumerate_words(max_len=6, max_a=6):
    """
    Enumerate exponent words of length 1..max_len
    with entries 1..max_a.
    """
    for length in range(1, max_len + 1):
        for word in product(range(1, max_a + 1), repeat=length):
            yield word


def run_examples():
    examples = [
        (1,),
        (1, 1),
        (1, 2),
        (2,),
        (2, 1),
        (1, 1, 1),
        (1, 2, 1),
        (1, 2, 2),
        (1, 1, 2, 3),
    ]

    print("Concrete examples")
    print("=================")

    for word in examples:
        A, k, B = affine_data(word)
        act = action(word)
        fp = fixed_point(word)
        print()
        print(f"word = {word}")
        print(f"  A = {A}, k = {k}, B = {B}")
        print(f"  2^A = {1 << A}, 3^k = {3 ** k}")
        print(f"  action = {act}")
        print(f"  fixed point = {fp} ≈ {float(fp):.12g}")

        if act == "positive":
            print("  Lock 1 check: positive-action ghost is negative.")
            print(f"  F_w(1) = {F(word, 1)} > 1")
        elif act == "contractive":
            print("  Contractive word: not a Lock 1 positive engine.")
        else:
            print("  Neutral word: should not occur for nonempty words.")


def run_bounded_scan(max_len=6, max_a=6):
    print()
    print("Bounded verification scan")
    print("=========================")
    print(f"Enumerating all words with length <= {max_len}, exponents <= {max_a}")

    total = 0
    positive = 0
    contractive = 0
    neutral = 0

    most_negative = None

    for word in enumerate_words(max_len=max_len, max_a=max_a):
        total += 1
        act = action(word)

        if act == "positive":
            positive += 1
            result = verify_positive_engine(word)
            fp = result["fixed_point"]
            if most_negative is None or fp < most_negative[1]:
                most_negative = (word, fp)

        elif act == "contractive":
            contractive += 1

        else:
            neutral += 1

    print(f"total words      = {total}")
    print(f"positive action  = {positive}")
    print(f"contractive      = {contractive}")
    print(f"neutral          = {neutral}")

    assert neutral == 0, "Nonempty neutral words should not exist."
    print("neutral check    = passed")

    print("Lock 1 scan      = passed")
    print("Every positive-action word scanned had a negative fixed point.")
    print("Every positive-action word scanned increased positive sample x values.")

    if most_negative is not None:
        word, fp = most_negative
        print(f"most negative scanned ghost: word={word}, fixed_point={fp} ≈ {float(fp):.12g}")


if __name__ == "__main__":
    run_examples()
    run_bounded_scan(max_len=6, max_a=6)
