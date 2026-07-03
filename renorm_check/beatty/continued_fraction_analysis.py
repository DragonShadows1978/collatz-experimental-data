#!/usr/bin/env python3
"""
Continued-fraction analysis explaining WHY floor(53(C+1)/22) and floor((C+1)/(2-log2(3)))
diverge starting at C=148, and why the divergence density becomes ~100% almost immediately
after that (not a rare edge case).

Key fact verified here: 22/53 is an exact continued-fraction convergent of the irrational
number (2 - log2(3)) [equivalently, 31/53 is a convergent of (log2(3) - 1)]. This is WHY the
capacity formula floor(53(C+1)/22) tracks the "true" irrational-slope formula so well for
small C -- convergents are the best rational approximations for their denominator size -- but
also why it MUST eventually and then PERSISTENTLY diverge: a single rational convergent p/q
can only track its target irrational within O(1/q) relative precision, and once C approaches
the scale where that absolute error (accumulated over C steps) exceeds 1, floor() disagreements
become the norm rather than the exception.
"""
import json
from pathlib import Path

import mpmath as mp

OUTDIR = Path(__file__).resolve().parent
mp.mp.dps = 60
LOG2_3 = mp.log(3, 2)
TARGET_IRRATIONAL = 2 - LOG2_3  # what 22/53 is secretly approximating


def continued_fraction(x, n_terms=15):
    a = []
    for _ in range(n_terms):
        ai = int(mp.floor(x))
        a.append(ai)
        frac = x - ai
        if frac < mp.mpf(10) ** -50:
            break
        x = 1 / frac
    return a


def convergents(a):
    conv = []
    h_prev, h_prevprev = 1, 0
    k_prev, k_prevprev = 0, 1
    for ai in a:
        h = ai * h_prev + h_prevprev
        k = ai * k_prev + k_prevprev
        conv.append((h, k))
        h_prevprev, h_prev = h_prev, h
        k_prevprev, k_prev = k_prev, k
    return conv


def main():
    cf_terms = continued_fraction(TARGET_IRRATIONAL, 16)
    conv = convergents(cf_terms)

    # locate 22/53 in the convergent list
    idx_2253 = next((i for i, (h, k) in enumerate(conv) if (h, k) == (22, 53)), None)
    assert idx_2253 is not None, "22/53 is NOT a continued-fraction convergent of 2-log2(3) -- unexpected"

    next_conv = conv[idx_2253 + 1] if idx_2253 + 1 < len(conv) else None

    q, q_next = 53, next_conv[1] if next_conv else None
    p = 22
    actual_err = abs(mp.mpf(p) / q - TARGET_IRRATIONAL)
    theoretical_bound = mp.mpf(1) / (q * q_next) if q_next else None

    # CORRECT drift-rate model (verified against the measured task3 sweep -- matches observed
    # max|diff|=330 at C=1e6 to within 0.3%): the two M_edge formulas are
    # floor((C+1)/alpha) [irrational] and floor((C+1)/beta) [rational, beta=22/53=p/q]. What
    # matters for the growth of their difference is the gap between the RECIPROCALS (1/alpha
    # vs 1/beta = 53/22 exactly), since that reciprocal gap is what multiplies (C+1) inside
    # the floor. An earlier version of this analysis used |beta - alpha| directly (the gap in
    # the un-inverted slopes, ~5.68e-5) and produced an onset estimate (~17593) that did NOT
    # match the observed first divergence (C=148) or the observed drift magnitude (330 at
    # C=1e6) -- that was the wrong quantity for this (division-form) formula. The
    # reciprocal-gap model below is the corrected mechanism and matches the measured data.
    inv_alpha = 1 / TARGET_IRRATIONAL
    inv_beta = mp.mpf(53) / 22  # = 1/(22/53) exactly
    reciprocal_gap = inv_alpha - inv_beta
    predicted_diff_at_1e6 = reciprocal_gap * 1_000_000
    onset_scale = mp.mpf('0.5') / abs(reciprocal_gap)  # C at which mean drift alone reaches 0.5
    # NOTE: this "onset_scale" is the MEAN-drift threshold, not the true first-divergence C.
    # The true first divergence (observed C=148) happens earlier because it also depends on
    # where the fractional part of (C+1)*inv_alpha happens to sit relative to an integer
    # boundary at each step (equidistribution / three-distance theorem), which fluctuates
    # around the mean-drift trend rather than following it monotonically. C=148 occurring well
    # before the ~1516 mean-drift threshold is expected variance, not an inconsistency.

    results = {
        "target_irrational": "2 - log2(3)",
        "target_irrational_value": mp.nstr(TARGET_IRRATIONAL, 30),
        "continued_fraction_terms": cf_terms,
        "convergents": [{"index": i, "p": h, "q": k, "value": mp.nstr(mp.mpf(h) / k, 12)}
                         for i, (h, k) in enumerate(conv)],
        "is_22_over_53_a_convergent": True,
        "convergent_index_of_22_53": idx_2253,
        "next_convergent_after_22_53": {"p": next_conv[0], "q": next_conv[1]} if next_conv else None,
        "error_of_22_53_vs_true_irrational_unlnverted_slopes": mp.nstr(actual_err, 20),
        "theoretical_error_bound_1_over_q_qnext_unlnverted_slopes": mp.nstr(theoretical_bound, 20) if theoretical_bound else None,
        "reciprocal_gap_1_over_alpha_minus_53_over_22": mp.nstr(reciprocal_gap, 20),
        "predicted_diff_at_C_1e6_from_reciprocal_gap_model": mp.nstr(predicted_diff_at_1e6, 10),
        "observed_max_abs_diff_at_C_1e6_from_task3_sweep": 330,
        "reciprocal_gap_model_agreement": "predicted 329.93 vs observed 330 -- matches to <0.3%",
        "mean_drift_onset_scale_C": mp.nstr(onset_scale, 10),
        "observed_first_divergence_C": 148,
        "observed_divergence_density_up_to_1e6": 0.99842,
        "conclusion": (
            "22/53 IS an exact continued-fraction convergent of (2 - log2(3)) [equivalently "
            "31/53 is a convergent of (log2(3)-1)], confirming the mission's structural "
            "hypothesis that the 53-step/22-support heartbeat is a rational-convergent "
            "shadow of the true log2(3) Sturmian slope, not an independent integer coincidence. "
            "BUT this also proves the capacity formula floor(53(C+1)/22) is NOT the exact "
            "irrational-slope law -- it is a finite-precision rational stand-in that is "
            "guaranteed by continued-fraction theory to eventually and then persistently "
            "disagree with the true floor((C+1)/(2-log2(3))) law. The reciprocal-gap model "
            "(1/alpha - 53/22, the correct quantity for this division-form formula) predicts "
            "a drift of ~329.9 at C=1e6, matching the measured 330 to <0.3% -- this confirms "
            "the divergence is a genuine, quantitatively-understood linear drift, not noise. "
            "The naive mean-drift onset threshold (~1516, where the average drift alone would "
            "reach 0.5) is much later than the actual observed first divergence (C=148); this "
            "gap is expected, since individual floor() flips depend on the fractional-part "
            "trajectory (equidistribution / three-distance theorem), which fluctuates around "
            "the mean trend rather than tracking it monotonically -- early outlier crossings "
            "well before the mean-onset scale are normal. After onset, divergence density "
            "jumps almost immediately to ~100% (measured 99.842% over C=1..10^6) and |diff| "
            "grows WITHOUT BOUND as C increases, because no finite rational convergent stays "
            "valid forever against an irrational target."
        ),
    }

    with open(OUTDIR / "continued_fraction_analysis.json", "w") as f:
        json.dump(results, f, indent=2)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
