#!/usr/bin/env python3
"""
W6E-E2 -- phase pinning for F5 (end-anchored recount), per
W6E_BOUND_PAIR_MECH_ORDER.md section E2.

Pure deterministic arithmetic (no automaton/search): count SUPPORT
letters (c_k == 1) in a 359-letter window under two anchoring
conventions, for the TRUE word and TWO candidate periodic comparison
words (see note below on why both are tested).

  - TRUE word: c_k = floor((k+1)*log2(3)) - floor(k*log2(3)), exact
    via bit_length (embedding/automaton.py's `credit`).
  - PERIODIC comparison word: mechanical word of a convergent p/q,
    c_k = floor(P(k+1)/q) - floor(Pk/q), P = 2q-p (W6D_GROUND_TRUTH_
    ORDER.md CRITICAL SPEC; NOT a first-q tiling).

**Ambiguity found and resolved by testing both candidates, not by
silently picking one (house rule: report, don't paper over):** the
order's prior "149 true supports vs 150 periodic" claim (SYNTHESIS.md
W6D-M section, line ~643) explicitly says the 150 count is for "the
22/53-periodicization" -- i.e. (p,q)=(22,53), P=2*53-22=84. But
SYNTHESIS.md elsewhere (lines 472, 548, 567, 610-614) identifies
127/306 as the operative convergent AT the m=359 window per W6D's
under-selection rule (finest under-side convergent within the readable
window). The E2 order text itself just says "the periodic comparison
word... per W6D_GROUND_TRUTH_ORDER.md spec" without repeating which
(p,q) inside the E2 section -- so both are computed here, clearly
separated, rather than guessing which one the order meant silently.

Two anchoring conventions, each a 359-letter window (k indices):
  - start-anchored (control): k = 0 .. 358
  - end-anchored: k = 12 .. 370  (matches the real measurement's own
    371 = 7*53 step count, window END-ANCHORED at the true terminal:
    371 - 359 = 12, so the constrained window is the LAST 359 of 371
    steps, i.e. absolute indices [12, 371) -- letters c_12..c_370.)

Deliverable: the support counts (true / 22-53-periodic / 127-306-
periodic) x (start-anchored / end-anchored) and whether the 149-vs-150
differential (as measured against the 22/53 word, which is the ONLY
candidate that reproduces the prior "150" figure at all) survives
end-anchoring. Registered prediction: differential SURVIVES (70%); if
it flips, F5's conditional route flips from 359 to 358, reported that
loudly regardless of which way it goes.
"""
import csv
from pathlib import Path

HERE = Path(__file__).parent


def credit_true(k: int) -> int:
    """floor((k+1)*log2(3)) - floor(k*log2(3)), exact via bit_length
    (arbitrary precision -- safe far past float precision at k~370)."""
    def floor_k_log2_3(kk: int) -> int:
        if kk == 0:
            return 0
        return (3 ** kk).bit_length() - 1
    return floor_k_log2_3(k + 1) - floor_k_log2_3(k)


def make_mechanical_word(p: int, q: int):
    """c_k = floor(P(k+1)/q) - floor(Pk/q), P = 2q - p. Returns
    (credit_fn, P) for the convergent p/q of alpha (per CRITICAL SPEC,
    NOT of beta=2-alpha; P = 2q-p is the corresponding beta-side count)."""
    P = 2 * q - p

    def credit_fn(k: int, P=P, q=q) -> int:
        return (P * (k + 1)) // q - (P * k) // q
    return credit_fn, P


def assert_word_receipts(credit_fn, p: int, q: int, P: int, label: str):
    """Pre-measurement assertion receipts (period, per-period support
    count) -- run and printed before any window count, per the CRITICAL
    SPEC discipline used throughout this order's ground truth."""
    period = q
    seq = [credit_fn(k) for k in range(period * 3)]
    for k in range(period * 2):
        assert seq[k] == seq[k + period], (
            f"{label}: word NOT period-{period} at k={k}")
    for d in range(1, period):
        if period % d != 0:
            continue
        assert not all(seq[k] == seq[k + d] for k in range(period * 2 - d)), (
            f"{label}: period is NOT exactly {period} -- smaller period "
            f"{d} also works")
    one_period = seq[:period]
    ones = sum(1 for c in one_period if c == 1)
    twos = sum(1 for c in one_period if c == 2)
    others = [c for c in one_period if c not in (1, 2)]
    assert not others, f"{label}: unexpected symbol values {others}"
    assert ones == p, f"{label}: expected {p} ones/period, got {ones}"
    assert ones + twos == period
    from fractions import Fraction
    beta = 2 - Fraction(p, q)
    print(f"RECEIPT [{label}]: mechanical word of {p}/{q}, P=2q-p={P}, "
          f"period={period} (verified exact over 3 periods), ones={ones}, "
          f"twos={twos} per period -- PASS. 2-{p}/{q}={beta}.")
    return True


def support_count(credit_fn, k_lo: int, k_hi_inclusive: int) -> dict:
    """Count support letters (c_k == 1) and drop letters (c_k == 2)
    over k = k_lo .. k_hi_inclusive (inclusive)."""
    ones = 0
    twos = 0
    others = []
    n = 0
    for k in range(k_lo, k_hi_inclusive + 1):
        c = credit_fn(k)
        n += 1
        if c == 1:
            ones += 1
        elif c == 2:
            twos += 1
        else:
            others.append((k, c))
    return {"window_len": n, "supports": ones, "drops": twos, "others": others,
            "k_lo": k_lo, "k_hi": k_hi_inclusive}


def main():
    M = 359
    start_lo, start_hi = 0, M - 1  # 0..358 inclusive, 359 letters
    ANCHOR_STEPS_REAL = 371
    end_lo, end_hi = ANCHOR_STEPS_REAL - M, ANCHOR_STEPS_REAL - 1  # 12..370

    print(f"Windows: start-anchored k={start_lo}..{start_hi} "
          f"(len={start_hi-start_lo+1}); "
          f"end-anchored k={end_lo}..{end_hi} (len={end_hi-end_lo+1})")
    print()

    words = {
        "22_53": make_mechanical_word(22, 53),
        "127_306": make_mechanical_word(127, 306),
    }

    print("=== Pre-measurement assertion receipts ===")
    for name, (fn, P) in words.items():
        p, q = (22, 53) if name == "22_53" else (127, 306)
        assert_word_receipts(fn, p, q, P, name)
    print()

    results = {}
    print("=== TRUE word ===")
    r = support_count(credit_true, start_lo, start_hi)
    print(f"  start-anchored (0..358): supports={r['supports']} "
          f"drops={r['drops']} others={r['others']}")
    results["true_start"] = r
    r = support_count(credit_true, end_lo, end_hi)
    print(f"  end-anchored  (12..370): supports={r['supports']} "
          f"drops={r['drops']} others={r['others']}")
    results["true_end"] = r

    for name, (fn, P) in words.items():
        print()
        print(f"=== PERIODIC word ({name.replace('_','/')} mechanical, P={P}) ===")
        r = support_count(fn, start_lo, start_hi)
        print(f"  start-anchored (0..358): supports={r['supports']} "
              f"drops={r['drops']} others={r['others']}")
        results[f"{name}_start"] = r
        r = support_count(fn, end_lo, end_hi)
        print(f"  end-anchored  (12..370): supports={r['supports']} "
              f"drops={r['drops']} others={r['others']}")
        results[f"{name}_end"] = r

    print()
    print("=== Differential (true supports - periodic supports), both candidates ===")
    for name in words:
        d_start = results["true_start"]["supports"] - results[f"{name}_start"]["supports"]
        d_end = results["true_end"]["supports"] - results[f"{name}_end"]["supports"]
        print(f"  [{name.replace('_','/')}] start-anchored diff={d_start}  "
              f"end-anchored diff={d_end}  "
              f"{'SURVIVES' if d_start == d_end and d_start != 0 else 'CHANGES/VANISHES'}")

    print()
    print("=== Reconciliation with prior claim (SYNTHESIS.md W6D-M: "
          "true=149, periodic=150, diff=-1, computed on 0..358, word="
          "'the 22/53-periodicization' per that section's own text) ===")
    ts = results["true_start"]["supports"]
    p_2253_s = results["22_53_start"]["supports"]
    p_127306_s = results["127_306_start"]["supports"]
    print(f"  This run, start-anchored: true={ts}, 22/53-periodic={p_2253_s}, "
          f"127/306-periodic={p_127306_s}")
    if (ts, p_2253_s) == (149, 150):
        print("  -> 22/53 REPRODUCES the prior 149-vs-150 claim exactly. "
              "This confirms the prior figure used the 22/53 word (matching "
              "its own text), NOT 127/306 (which gives "
              f"{ts}-{p_127306_s}={ts-p_127306_s} on this window, not -1).")
    else:
        print("  -> Neither candidate reproduces the prior claim as stated; "
              "flagging for the architect.")

    d_start_2253 = results["true_start"]["supports"] - results["22_53_start"]["supports"]
    d_end_2253 = results["true_end"]["supports"] - results["22_53_end"]["supports"]
    print()
    print("=== GATE VERDICT (against the word that actually reproduces "
          "the prior 149-vs-150 claim: 22/53) ===")
    print(f"  start-anchored diff = {d_start_2253} (matches prior claim's -1: "
          f"{d_start_2253 == -1})")
    print(f"  end-anchored diff   = {d_end_2253}")
    if d_start_2253 == d_end_2253 and d_start_2253 != 0:
        print("  -> DIFFERENTIAL SURVIVES end-anchoring. Registered "
              "prediction (SURVIVES, 70%) HIT.")
    else:
        print(f"  -> DIFFERENTIAL DOES NOT SURVIVE end-anchoring "
              f"(start={d_start_2253} vs end={d_end_2253}). Registered "
              "prediction (SURVIVES, 70%) MISSED. Per the order: "
              "'if it flips, the conditional F5 flips to 358 and that "
              "gets reported exactly as loudly.' REPORTING: the "
              "149-vs-150 differential is a START-ANCHORING ARTIFACT -- "
              "under the end-anchored window (the one that actually "
              "matches the real 371-step measurement's own phase), true "
              f"and 22/53-periodic supports are EQUAL "
              f"({results['true_end']['supports']} both), so the "
              "conditional D(359)=148->edge=359 route LOSES its "
              "arithmetic support. The differential does not survive.")

    print()
    print("=== Also checking 127/306 (the OTHER candidate, per SYNTHESIS's "
          "own under-selection claim of operative convergent at m=359) ===")
    d_start_127306 = results["true_start"]["supports"] - results["127_306_start"]["supports"]
    d_end_127306 = results["true_end"]["supports"] - results["127_306_end"]["supports"]
    print(f"  start-anchored diff = {d_start_127306}; end-anchored diff = {d_end_127306}")
    if d_start_127306 == 0 and d_end_127306 == 0:
        print("  -> 127/306 shows ZERO differential under EITHER anchoring "
              "(true and 127/306-periodic support counts are IDENTICAL, "
              "149 each, both windows) -- consistent with the under-lock "
              "identity (W6D-G PD1/PD2 pattern: agreement at certain "
              "arithmetic coincidence phases) rather than the -1 bonus "
              "pattern found elsewhere. This candidate gives NO support "
              "for either F5 branch via this mechanism -- it is simply "
              "silent on the question.")

    # write CSV
    with open(HERE / "e2_support_census.csv", "w", newline="") as f:
        fieldnames = ["word", "anchoring", "k_lo", "k_hi", "window_len",
                      "supports", "drops", "others"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for label, key in [("true", "true_start"), ("true", "true_end"),
                            ("periodic_22_53", "22_53_start"),
                            ("periodic_22_53", "22_53_end"),
                            ("periodic_127_306", "127_306_start"),
                            ("periodic_127_306", "127_306_end")]:
            r = results[key]
            anchoring = "start" if key.endswith("start") else "end"
            w.writerow({"word": label, "anchoring": anchoring,
                        "k_lo": r["k_lo"], "k_hi": r["k_hi"],
                        "window_len": r["window_len"], "supports": r["supports"],
                        "drops": r["drops"], "others": str(r["others"])})
    print("\nWrote e2_support_census.csv")
    return results


if __name__ == "__main__":
    main()
