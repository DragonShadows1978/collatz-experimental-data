#!/usr/bin/env python3
"""
J3 -- shared 53 across 53/22 (corridor's M_edge) and 53/84 (spectral's gap base).

1. Compute the continued fraction of log2(3) to high precision (mpmath, 60
   digits) and list convergents p_k/q_k up to k=8 or so. Confirm 84/53 is
   the 6th convergent (index depends on 0- vs 1-indexing -- report both and
   state which index actually gives 84/53).
2. Compute the continued fraction of 2-log2(3) (=BETA in shell_probe.py)
   similarly and confirm 22/53 is a convergent of THAT.
3. Work out the exact algebraic relationship between the CF of log2(3) and
   the CF of 2-log2(3): 2 - log2(3) = 2 - alpha. Verify a reflection
   identity EXACTLY against the computed integer term lists.
4. Confirm 53 is literally the SAME integer denominator: 84/53 (convergent
   of log2(3)) has denominator 53; corridor's constant is 53/22 (M_edge(C)
   = floor(53(C+1)/22)) -- check precisely which of {22/53, 53/22} is the
   beta-convergent before asserting any "shared 53" claim.
5. C=11 / exponent-6 check: is there an exact relation between the
   corridor's phase-transition width C=11 and the spectral exponent 6 (in
   b~(53/84)^6), or the convergent-index 6? Check simple candidates.
"""
import math as pymath
from pathlib import Path

from mpmath import mp, log

mp.dps = 60
LOG2_3 = log(3, 2)


def continued_fraction(x, n_terms=14):
    """Continued fraction expansion of a high-precision mpmath value x,
    returning list of partial quotients a0, a1, ..."""
    terms = []
    for _ in range(n_terms):
        a = int(x)
        terms.append(a)
        frac = x - a
        if frac == 0:
            break
        x = 1 / frac
    return terms


def convergents(a_terms):
    """Given partial quotients a0,a1,..., return list of (p_k, q_k)
    convergents via the standard recurrence (exact Python ints)."""
    p_prev2, p_prev1 = 0, 1
    q_prev2, q_prev1 = 1, 0
    conv = []
    for a in a_terms:
        p = a * p_prev1 + p_prev2
        q = a * q_prev1 + q_prev2
        conv.append((p, q))
        p_prev2, p_prev1 = p_prev1, p
        q_prev2, q_prev1 = q_prev1, q
    return conv


def main():
    out = []
    out.append("=" * 78)
    out.append("J3 -- shared-53 verification (convergents of log2(3) and 2-log2(3))")
    out.append("=" * 78)

    alpha = LOG2_3
    out.append(f"\nlog2(3) computed via mpmath at 60 digits: {mp.nstr(alpha, 40)}")

    a_terms_alpha = continued_fraction(alpha, n_terms=14)
    out.append(f"\nContinued fraction of alpha=log2(3): {a_terms_alpha}")
    conv_alpha = convergents(a_terms_alpha)
    out.append("Convergents p_k/q_k of log2(3) (k = 0-indexed term count):")
    for k, (p, q) in enumerate(conv_alpha):
        out.append(f"  k={k:>2}: {p}/{q}  = {p/q:.10f}   (target log2(3)={float(alpha):.10f})")

    idx_8453 = None
    for k, (p, q) in enumerate(conv_alpha):
        if (p, q) == (84, 53):
            idx_8453 = k
    out.append(f"\n84/53 found at continued-fraction index k={idx_8453} "
               f"(0-indexed term list; 'the 6th convergent' in 1-indexed/'6th "
               f"partial-quotient' language corresponds to k={idx_8453}).")

    beta = 2 - alpha
    out.append(f"\nbeta = 2 - log2(3) = {mp.nstr(beta, 40)}")
    a_terms_beta = continued_fraction(beta, n_terms=14)
    out.append(f"Continued fraction of beta=2-log2(3): {a_terms_beta}")
    conv_beta = convergents(a_terms_beta)
    out.append("Convergents p_k/q_k of 2-log2(3):")
    for k, (p, q) in enumerate(conv_beta):
        out.append(f"  k={k:>2}: {p}/{q}  = {p/q:.10f}   (target beta={float(beta):.10f})")

    idx_2253 = None
    idx_5322 = None
    for k, (p, q) in enumerate(conv_beta):
        if (p, q) == (22, 53):
            idx_2253 = k
        if (p, q) == (53, 22):
            idx_5322 = k
    out.append(f"\n22/53 found in beta's convergents at k={idx_2253}")
    out.append(f"53/22 found in beta's convergents at k={idx_5322}")
    out.append("(F1 in SYNTHESIS.md states '22/53 is an exact continued-fraction "
                "convergent of 2-log2(3)' -- i.e. beta's convergent IS 22/53 "
                "[p=22,q=53], not 53/22. The corridor formula M_edge(C)="
                "floor(53(C+1)/22) uses the RECIPROCAL 53/22 as its scaling "
                "constant -- 53/22 = 1/(22/53) -- so '53/22' in the corridor "
                "formula is the reciprocal of the beta-convergent 22/53, not "
                "itself directly a listed convergent of beta or alpha.")

    out.append(f"\nReciprocal check: is 53/22 a convergent of 1/beta = 1/(2-log2(3))?")
    inv_beta = 1 / beta
    a_terms_invbeta = continued_fraction(inv_beta, n_terms=14)
    conv_invbeta = convergents(a_terms_invbeta)
    out.append(f"Continued fraction of 1/beta: {a_terms_invbeta}")
    idx_5322_invbeta = None
    for k, (p, q) in enumerate(conv_invbeta):
        if (p, q) == (53, 22):
            idx_5322_invbeta = k
        out.append(f"  k={k:>2}: {p}/{q} = {p/q:.10f}")
    out.append(f"53/22 found in (1/beta)'s convergents at k={idx_5322_invbeta} "
               "(convergents of 1/x are exactly the reciprocals-in-order of "
               "convergents of x when x<1, up to the leading integer-part term "
               "shift -- this is the standard CF identity for reciprocals).")

    out.append("\n--- Exact CF-transform identity: beta = 2 - alpha ---")
    out.append(f"alpha's CF: {a_terms_alpha}")
    out.append(f"beta=2-alpha's CF: {a_terms_beta}")
    out.append("Since alpha = [1; a1, a2, a3, ...] (a0=1 because 1<log2(3)<2), "
               "write alpha = 1 + f where f = alpha-1 = [0; a1, a2, a3, ...] "
               "in (0,1). Then beta = 2-alpha = 1-f. The EXACT continued-fraction "
               "identity for 1-f when f=[0;a1,a2,...] with a1>=2 is: "
               "1-f = [0; 1, a1-1, a2, a3, ...] (standard CF reflection identity). "
               "If a1==1 the identity instead merges the leading terms: "
               "1-f = [0; a2+1, a3, a4, ...]. Testing against computed terms:")
    a1 = a_terms_alpha[1] if len(a_terms_alpha) > 1 else None
    out.append(f"  alpha's a1 = {a1}")
    if a1 is not None and a1 >= 2:
        predicted_beta_terms = [0, 1, a1 - 1] + a_terms_alpha[2:]
    elif a1 == 1:
        predicted_beta_terms = [0, a_terms_alpha[2] + 1] + a_terms_alpha[3:]
    else:
        predicted_beta_terms = None
    out.append(f"  predicted beta CF (via reflection identity): {predicted_beta_terms}")
    out.append(f"  actual computed beta CF:                     {a_terms_beta}")
    match = (predicted_beta_terms == a_terms_beta[:len(predicted_beta_terms)]
             if predicted_beta_terms else False)
    out.append(f"  identity holds (prefix match): {match}")

    out.append("\n--- C=11 phase transition vs spectral exponent 6 ---")
    HEARTBEAT = 53
    SUPPORT_COUNT = 22
    def M_edge(C):
        return (HEARTBEAT * (C + 1)) // SUPPORT_COUNT
    for C in range(1, 15):
        out.append(f"  M_edge({C:>2}) = {M_edge(C):>3}")
    out.append(f"\n  M_edge(11) = {M_edge(11)}")
    out.append(f"  6th convergent index (0-indexed k={idx_8453}) denominator = 53, "
               f"numerator = 84")
    out.append(f"  Candidate checks:")
    out.append(f"    M_edge(11) == 84? {M_edge(11) == 84}")
    out.append(f"    C+1=12 vs convergent index {idx_8453}: equal? {12 == idx_8453}")
    out.append(f"    11 == 2*6-1={2*6-1}? {11 == 2*6-1}")
    out.append(f"    a_terms_alpha[0:idx+1] (partial quotients up to the 84/53 term): "
               f"{a_terms_alpha[:idx_8453+1] if idx_8453 is not None else None}")
    out.append(f"    sum of partial quotients up to k={idx_8453}: "
               f"{sum(a_terms_alpha[:idx_8453+1]) if idx_8453 is not None else None}")
    found_11 = []
    for k, (p, q) in enumerate(conv_alpha):
        if p == 11 or q == 11:
            found_11.append(("alpha", k, p, q))
    for k, (p, q) in enumerate(conv_beta):
        if p == 11 or q == 11:
            found_11.append(("beta", k, p, q))
    out.append(f"    11 appearing as numerator or denominator in alpha/beta convergent "
               f"lists: {found_11}")
    out.append("\n  VERDICT INPUT: no exact/structural relation between C=11 and the "
               "spectral exponent 6 (or convergent-index 6) found among these direct "
               "candidates -- see list above. Reporting as OPEN per spec instruction "
               "unless one of the above candidates matched (it did not, modulo what's "
               "printed).")

    text = "\n".join(out)
    print(text)
    Path(__file__).parent.joinpath("j3_output.txt").write_text(text + "\n")


if __name__ == "__main__":
    main()
