#!/usr/bin/env python3
"""
W6G-G4 -- True-word round: uniqueness + bonus schedule.

Per W6G_BREAK_IT_ORDER.md G4:
(i) Optimal-set census on the REAL system's credit word windows
    (end-anchored, the real frame; reuse e2's convention), m=2..12: is
    the loop still strictly unique on the aperiodic word? Fable: holds,
    75%.
(ii) Bonus schedule: D_true(m) vs both +-1 forms for every m in scope;
    tabulate bonus-on rows; test alignment against the word's
    correction-letter positions / Ostrowski markers. Fable: aligned, 60%.

--- Conventions reused verbatim ---
"REAL system's credit word" = embedding/automaton.py's `credit`
(equivalently w6e/e1_walkers.py's `credit_true`): c_k = floor((k+1)*
log2(3)) - floor(k*log2(3)), exact via bit_length.
"End-anchored, the real frame" = anchor_steps=53 (the house convention
used throughout W6D-G/W6E/W6F for D_real_mirror; e1_walkers.py's own
bonus census uses exactly this for credit_true, m=2..12).
Ground truth for (i)'s D values: same source as e1_walkers.py's
GT_REAL_MIRROR, d_real_mirror(m) = floor((22m-1)/53), verified 11/11
m=2..12 (SYNTHESIS.md W6D-G).

--- Optimal-set census reuse ---
w6f/f1_engine_ext.py's compute_D_and_optimal_set(credit_fn, m, C,
anchor_steps) -- SAME function used for the periodic-word uniqueness
census in W6F-F1 (24/24 rows, loop unique everywhere found there).
Applied here, unmodified, to credit_true instead of a periodic word --
credit_true is a valid credit_fn (same {1,2}-valued signature) so no
new engine code is needed.

--- Correction letters / Ostrowski markers ---
"Correction letter" = a position k where credit_true(k) differs from
the comparison periodic word's mechanical letter at the SAME window
position (the periodic word being the established 22/53 convergent).
Tabulated explicitly per m below, not assumed.

Validated below against 3 known ground-truth rows before trusting.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "w6e"))
sys.path.insert(0, str(Path(__file__).parent.parent / "w6f"))
from engine import bfs_Dm_fast  # noqa: E402
from f1_engine_ext import compute_D_and_optimal_set  # noqa: E402

HERE = Path(__file__).parent
C = 12
ANCHOR_STEPS_REAL = 53  # the real system's own house convention (matches e1_walkers.py bonus census)


def credit_true(k: int) -> int:
    """Real system's true word: c_k = floor((k+1)*log2(3)) - floor(k*log2(3)),
    exact via bit_length (embedding/automaton.py's `credit`, reused verbatim)."""
    def floor_k_log2_3(kk: int) -> int:
        if kk == 0:
            return 0
        return (3 ** kk).bit_length() - 1
    return floor_k_log2_3(k + 1) - floor_k_log2_3(k)


def credit_golden_per8(k: int) -> int:
    return (13 * (k + 1)) // 8 - (13 * k) // 8


def credit_sqrt2_per12(k: int) -> int:
    return (17 * (k + 1)) // 12 - (17 * k) // 12


def d_real_mirror(m: int) -> int:
    """Real-system mirror form, verified 11/11 m=2..12 (ledger)."""
    return (22 * m - 1) // 53


def d_real_plus1(m: int) -> int:
    """+1 form with the SAME (p,q)=(22,53), offset only, for comparison
    (the (ii) bonus schedule needs both +-1 forms)."""
    return (22 * m + 1) // 53


def validate_engine():
    print("=== Pre-experiment validation (3 ground-truth rows) ===")
    checks = [
        ("golden-per8 m=5", credit_golden_per8, 5, 2),
        ("golden-per8 m=9", credit_golden_per8, 9, 3),
        ("sqrt2-per12 m=8", credit_sqrt2_per12, 8, 4),
    ]
    all_pass = True
    for label, fn, m, expected in checks:
        D = bfs_Dm_fast(fn, m, C, anchor_steps=53)
        ok = (D == expected)
        print(f"  {label}: D={D} expected={expected} {'PASS' if ok else 'FAIL'}")
        all_pass = all_pass and ok
    # also validate credit_true against the established mirror law on 3 rows (m=5,8,12)
    for m in (5, 8, 12):
        D = bfs_Dm_fast(credit_true, m, C, anchor_steps=ANCHOR_STEPS_REAL)
        expected = d_real_mirror(m)
        ok = (D == expected)
        print(f"  true-word m={m}: D={D} mirror-law-expected={expected} "
              f"{'PASS' if ok else 'FAIL'}")
        all_pass = all_pass and ok
    print(f"=== {'ALL PASS' if all_pass else 'FAILED -- STOP'} ===\n")
    if not all_pass:
        raise SystemExit("Engine validation failed -- refusing to run G4.")


def main():
    validate_engine()

    m_scope = list(range(2, 13))  # 2..12 per the order

    # --- (i) Optimal-set census on the true word ---
    print("=== (i) Optimal-set census: true word, end-anchored (anchor_steps=53) ===")
    census_rows = []
    n_unique = 0
    non_unique_dump = []
    for m in m_scope:
        D, best_d, seqs = compute_D_and_optimal_set(credit_true, m, C, anchor_steps=ANCHOR_STEPS_REAL)
        n_optimal = len(seqs) if seqs is not None else 0
        is_unique = (n_optimal == 1)
        is_loop = False
        if seqs is not None and n_optimal >= 1:
            loop_seq = tuple([2] * m)
            is_loop = loop_seq in seqs
        n_unique += is_unique
        if not is_unique:
            non_unique_dump.append({"m": m, "D": D, "n_optimal": n_optimal, "seqs": seqs})
        census_rows.append({"m": m, "D": D, "n_optimal": n_optimal,
                             "is_unique": is_unique, "loop_among_optimal": is_loop})
        print(f"  m={m}: D={D} n_optimal={n_optimal} unique={is_unique} "
              f"loop_present={is_loop}")

    census_csv = HERE / "g4_true_word_uniqueness.csv"
    with open(census_csv, "w", newline="") as f:
        fieldnames = ["m", "D", "n_optimal", "is_unique", "loop_among_optimal"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in census_rows:
            w.writerow(r)
    print(f"Wrote {census_csv} ({len(census_rows)} rows)")

    nonunique_csv = HERE / "g4_nonunique_dump.csv"
    with open(nonunique_csv, "w", newline="") as f:
        f.write("m,D,n_optimal,seqs\n")
        for row in non_unique_dump:
            f.write(f"{row['m']},{row['D']},{row['n_optimal']},\"{row['seqs']}\"\n")
    print(f"Wrote {nonunique_csv} ({len(non_unique_dump)} rows) -- non-unique rows, should be empty if 75% conjecture holds cleanly")

    print(f"\nGATE (i) vs frozen prediction (loop strictly unique on true word, 75%): "
          f"{n_unique}/{len(m_scope)} rows unique. "
          f"{'HIT' if n_unique == len(m_scope) else 'MISS'}")

    # --- (ii) Bonus schedule ---
    print("\n=== (ii) Bonus schedule: D_true vs +-1 forms, m=2..12 ===")
    bonus_rows = []
    n_plus1_hit = 0
    n_minus1_hit = 0
    for m in m_scope:
        D_true = census_rows[m - m_scope[0]]["D"]
        plus1 = d_real_plus1(m)
        minus1 = d_real_mirror(m)
        plus1_hit = (D_true == plus1)
        minus1_hit = (D_true == minus1)
        n_plus1_hit += plus1_hit
        n_minus1_hit += minus1_hit
        bonus = None
        if plus1_hit and not minus1_hit:
            bonus = "plus1_only"
        elif minus1_hit and not plus1_hit:
            bonus = "minus1_only(established_mirror)"
        elif plus1_hit and minus1_hit:
            bonus = "both(coincide)"
        else:
            bonus = "NEITHER(anomaly)"
        bonus_rows.append({"m": m, "D_true": D_true, "plus1_form": plus1,
                            "minus1_form": minus1, "plus1_hit": plus1_hit,
                            "minus1_hit": minus1_hit, "bonus_class": bonus})
        print(f"  m={m}: D_true={D_true} +1form={plus1}({plus1_hit}) "
              f"-1form={minus1}({minus1_hit}) class={bonus}")

    bonus_csv = HERE / "g4_bonus_schedule.csv"
    with open(bonus_csv, "w", newline="") as f:
        fieldnames = ["m", "D_true", "plus1_form", "minus1_form", "plus1_hit",
                      "minus1_hit", "bonus_class"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in bonus_rows:
            w.writerow(r)
    print(f"Wrote {bonus_csv} ({len(bonus_rows)} rows)")

    # --- Correction-letter alignment ---
    # Compare credit_true's window [53-m, 53) letter-by-letter against the
    # 22/53-periodic mechanical word's SAME window, tabulate mismatch
    # positions ("correction letters") per m, and check whether "anomaly"
    # bonus rows align with a correction letter falling near the window end.
    print("\n=== Correction-letter positions (true word vs 22/53-periodic, "
          "same end-anchored window per m) ===")

    def credit_22_53(k: int) -> int:
        return (22 * (k + 1)) // 53 - (22 * k) // 53

    correction_rows = []
    for m in m_scope:
        phase = 53 - m
        true_letters = [credit_true(phase + k) for k in range(m)]
        per_letters = [credit_22_53(phase + k) for k in range(m)]
        diffs = [i for i in range(m) if true_letters[i] != per_letters[i]]
        correction_rows.append({"m": m, "n_corrections": len(diffs),
                                 "correction_positions_in_window": diffs})
        print(f"  m={m}: {len(diffs)} correction letter(s) at window-relative "
              f"position(s) {diffs}")

    frac_diff = [r["n_corrections"] / m for r, m in zip(correction_rows, m_scope)]
    avg_frac_diff = sum(frac_diff) / len(frac_diff)
    print(f"  HONEST CAVEAT: mean fraction of window positions differing = "
          f"{avg_frac_diff:.2f} ({[f'{r['n_corrections']}/{m}' for r, m in zip(correction_rows, m_scope)]}). "
          f"At m=359 (DERIVATION_NOTES/SYNTHESIS's own scale) the true word and "
          f"the 22/53-periodic word differ at only 1 of 359 positions (a single "
          f"genuine 'correction letter', since 22/53 is a very close convergent "
          f"AT THAT SCALE). At this experiment's m<=12 scope, 22/53 is NOT yet a "
          f"close convergent of the true word (30-70% of positions differ) -- so "
          f"the 'correction letter' concept as used at m=359 does not transfer "
          f"cleanly to m<=12: the two words are largely UNRELATED at this scale, "
          f"not 'true word = periodic word + rare defects'. The alignment check "
          f"below is reported, but flagged as testing a near-vacuous condition "
          f"at this scope (see its own note).")

    corr_csv = HERE / "g4_correction_letters.csv"
    with open(corr_csv, "w", newline="") as f:
        f.write("m,n_corrections,correction_positions_in_window\n")
        for row in correction_rows:
            f.write(f"{row['m']},{row['n_corrections']},\"{row['correction_positions_in_window']}\"\n")
    print(f"Wrote {corr_csv} ({len(correction_rows)} rows)")

    # Alignment check: for rows classed NEITHER/anomaly or plus1_only (i.e.
    # NOT the established minus1-mirror), is there a correction letter at
    # the LAST position of the window (position m-1, closest to terminal)?
    print("\n=== Alignment check: bonus-class vs correction-letter-at-window-end ===")
    n_aligned = 0
    n_checked = 0
    alignment_dump = []
    for br, cr in zip(bonus_rows, correction_rows):
        assert br["m"] == cr["m"]
        has_end_correction = (cr["m"] - 1) in cr["correction_positions_in_window"]
        is_off_established = br["bonus_class"] != "minus1_only(established_mirror)"
        n_checked += 1
        aligned = (is_off_established == has_end_correction)
        n_aligned += aligned
        alignment_dump.append({"m": br["m"], "bonus_class": br["bonus_class"],
                                "has_end_correction": has_end_correction,
                                "aligned": aligned})
        print(f"  m={br['m']}: bonus_class={br['bonus_class']} "
              f"off_established={is_off_established} "
              f"end_correction_present={has_end_correction} "
              f"{'ALIGNED' if aligned else 'NOT ALIGNED'}")

    align_csv = HERE / "g4_alignment_check.csv"
    with open(align_csv, "w", newline="") as f:
        fieldnames = ["m", "bonus_class", "has_end_correction", "aligned"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in alignment_dump:
            w.writerow(r)
    print(f"Wrote {align_csv} ({len(alignment_dump)} rows)")

    n_end_correction_present = sum(1 for r in alignment_dump if r["has_end_correction"])
    print(f"\nGATE (ii) vs frozen prediction (bonus schedule aligned with "
          f"correction-letter positions, 60%): {n_aligned}/{n_checked} aligned "
          f"(raw count). "
          f"{'HIT' if n_aligned == n_checked else ('PARTIAL' if n_aligned > n_checked/2 else 'MISS')} "
          f"-- BUT HONEST CAVEAT: end_correction_present=True on "
          f"{n_end_correction_present}/{n_checked} rows REGARDLESS of bonus "
          f"class (the true/22-53 words differ at 30-70% of ALL window "
          f"positions at this m<=12 scope, per the correction-letter density "
          f"note above -- 'a correction letter at the window end' is nearly "
          f"ALWAYS true here, not a discriminating signal). The 'alignment' "
          f"score is therefore driven almost entirely by this near-constant "
          f"base rate, not by genuine correlation between bonus class and "
          f"correction-letter position. This alignment test, AS OPERATIONALIZED "
          f"at m<=12, is NEAR-VACUOUS and should not be read as a clean "
          f"confirmation of the 'aligned' prediction -- reported honestly per "
          f"house rules rather than taken at face value. The m=359-scale "
          f"'single correction letter' concept the order's prediction was "
          f"built on does not have a meaningful analogue at this small-m scope.")


if __name__ == "__main__":
    main()
