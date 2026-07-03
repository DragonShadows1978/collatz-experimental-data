#!/usr/bin/env python3
"""
Task 3 (high-precision, exact-arithmetic version): find every C in [1, 10^6] where
    floor(53*(C+1)/22)                         [rational-slope formula from the proof]
diverges from
    floor((C+1) / (2 - log2(3)))               [true irrational-slope analogue]

Uses mpmath at 60 decimal digits of precision (>>> far beyond float64's ~15-17 digits)
so that floor() near an integer boundary is not a rounding artifact. Cross-checked at
C=148 (the first divergence found by the float64 pass in beatty_search.py) against a
120-digit run to confirm it is a genuine mathematical divergence, not a precision bug.

Also computes the RATE of divergence (density of mismatches) up to 10^6, and the
running max |diff|, since a single early divergence (C=148, inside the very fit range
the proof claims exactness over) is the headline finding but the growth pattern matters
for interpreting whether the rational formula is "occasionally off by one" vs.
"systematically drifting."
"""
import json
from pathlib import Path

import mpmath as mp

OUTDIR = Path(__file__).resolve().parent

mp.mp.dps = 60  # 60 decimal digits -- gives ~200 bits, safe for C up to 10^6 and beyond
LOG2_3 = mp.log(3, 2)
DENOM = 2 - LOG2_3  # true irrational analogue of 22/53


def M_edge_rational(C: int) -> int:
    return (53 * (C + 1)) // 22


def M_edge_irrational_hp(C: int) -> int:
    return int(mp.floor((C + 1) / DENOM))


def main():
    LIMIT = 1_000_000

    # Confirm C=148 with a much higher precision (120 digits) as an independent sanity check.
    mp.mp.dps = 120
    log2_3_120 = mp.log(3, 2)
    denom_120 = 2 - log2_3_120
    val_148 = (148 + 1) / denom_120
    confirm_148 = {
        "C": 148,
        "precision_digits": 120,
        "exact_value_(C+1)/(2-log2_3)": mp.nstr(val_148, 40),
        "floor": int(mp.floor(val_148)),
        "target_rational": M_edge_rational(148),
        "genuine_divergence": int(mp.floor(val_148)) != M_edge_rational(148),
        "distance_from_next_integer_below": mp.nstr(val_148 - mp.floor(val_148), 40),
    }
    mp.mp.dps = 60  # restore working precision for the bulk sweep

    divergences = []
    max_abs_diff = 0
    running_diff_at = []
    checkpoint_every = 50000

    for C in range(1, LIMIT + 1):
        t = M_edge_rational(C)
        v = M_edge_irrational_hp(C)
        if v != t:
            d = v - t
            divergences.append({"C": C, "target_rational": t, "irrational_value": v, "diff": d})
            if abs(d) > max_abs_diff:
                max_abs_diff = abs(d)
        if C % checkpoint_every == 0:
            running_diff_at.append({
                "C": C,
                "cumulative_divergence_count": len(divergences),
                "max_abs_diff_so_far": max_abs_diff,
            })

    first = divergences[0] if divergences else None
    last = divergences[-1] if divergences else None

    summary = {
        "method": "mpmath at 60 decimal digits precision (120 digits for the C=148 spot-check); "
                  "exact integer floor-division for the rational side. NOT float64.",
        "range_searched": [1, LIMIT],
        "confirm_C148_at_120_digits": confirm_148,
        "total_divergences_found": len(divergences),
        "divergence_density": len(divergences) / LIMIT,
        "first_divergence": first,
        "last_divergence_in_range": last,
        "max_abs_diff_observed": max_abs_diff,
        "running_checkpoints": running_diff_at,
        "sample_divergences_first_50": divergences[:50],
        "sample_divergences_last_50": divergences[-50:],
        "interpretation": (
            "The empirically-exact formula floor(53(C+1)/22) = floor((C+1)/(22/53)) is a rational "
            "CONVERGENT-based approximation of the true irrational relationship "
            "floor((C+1)/(2-log2(3))); see continued_fraction_analysis.py/.json for the full "
            "derivation. 22/53 is an exact continued-fraction convergent of (2-log2(3)) (confirmed "
            "there), which is why the two formulas track closely for small C. But because this is a "
            "DIVISION-form formula, the relevant per-unit-C drift rate is the gap between the "
            "RECIPROCALS, (1/(2-log2(3))) - 53/22 =~ 3.2993e-4, not the raw slope gap "
            "|22/53-(2-log2(3))| =~ 5.684e-5 (an earlier, incorrect estimate). The reciprocal-gap "
            "rate predicts a drift of ~329.9 at C=1e6, matching the measured max|diff|=330 to "
            "<0.3% -- confirming this is a real, quantitatively-understood LINEAR drift, not noise "
            "or a rare edge case. Divergence density jumps to ~100% almost immediately after the "
            "first mismatch (measured 99.842% over C=1..1e6) because once the accumulated drift "
            "exceeds roughly half an integer, floor() disagreements become the norm rather than "
            "the exception, and the drift only continues to grow with C. A NEW, better convergent "
            "of log2(3) beyond 22/53 (continued fraction of (2-log2(3)) = "
            "[0;2,2,2,3,1,5,2,23,2,2,1,1,55,1,...], next convergent 127/306) does not rescue this: "
            "no finite rational convergent stays valid forever against an irrational target."
        ),
    }

    # NOTE: the full per-C divergence list (998,420 rows for C=1..1e6) is written ONLY to
    # task3_divergences.csv, not embedded in the JSON summary -- embedding it made the JSON
    # ~117MB, unwieldy for any downstream synthesis/reading step. The JSON keeps the summary,
    # checkpoints, and small samples only.
    with open(OUTDIR / "task3_high_precision_divergence.json", "w") as f:
        json.dump({"summary": summary}, f, indent=2)

    import csv
    with open(OUTDIR / "task3_divergences.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["C", "target_rational", "irrational_value", "diff"])
        w.writeheader()
        for d in divergences:
            w.writerow(d)

    print(json.dumps({k: v for k, v in summary.items() if k not in
                       ("running_checkpoints", "sample_divergences_first_50", "sample_divergences_last_50")},
                      indent=2))
    print("\nfirst 10 divergences:", divergences[:10])
    print("\nrunning checkpoints:", running_diff_at)


if __name__ == "__main__":
    main()
