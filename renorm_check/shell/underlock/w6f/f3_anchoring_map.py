#!/usr/bin/env python3
"""
W6F-F3 -- boundary-constant anchoring map, per W6F_OPTIMAL_SET_ORDER.md
section F3.

REUSES engine.bfs_Dm_fast (validated numpy-vectorized D-only readout,
w6e/engine.py) unmodified -- only the `anchor_steps` argument (which
sets `phase = anchor_steps - m`, i.e. which m-letter window of the
periodic credit word is used) is varied to realize the two anchoring
conventions.

--- Anchoring conventions (defined EXPLICITLY here, matching
    w6e/e2_phase_pinning.py's definitions so results compose) ---

E2's conventions (see e2_phase_pinning.py docstring, "Two anchoring
conventions, each a 359-letter window"):
  - start-anchored: window k = 0 .. M-1 (the word's OWN index origin,
    phase = 0 relative to the credit function's own k=0).
  - end-anchored: window k = (ANCHOR_STEPS_REAL - M) .. (ANCHOR_STEPS_REAL - 1),
    i.e. the LAST M letters ending at the TRUE measurement's own
    terminal step count (371 for the real system's F5 question; 53 for
    the golden/sqrt2 toy families' own house convention, per
    engine.py's bfs_Dm/bfs_Dm_fast default `anchor_steps=53`).

Translated into engine.bfs_Dm_fast's own `phase = anchor_steps - m`
parameterization (identical mechanics, just phrased via the anchor_steps
argument that function already accepts):
  - start-anchored  <=> anchor_steps = m   (phase = 0, window k=0..m-1)
  - end-anchored    <=> anchor_steps = 53  (phase = 53-m, window
                        k=(53-m)..52 -- the SAME 53-step house
                        convention used throughout W6D-G/W6E for
                        D_golden_per8_table.csv / D_sqrt2_per12_table.csv,
                        i.e. this IS the convention the existing ground
                        truth tables were built under).

Both are periodic-word phase choices (golden-per8 period 8, sqrt2-per12
period 12) -- "anchoring" here means WHICH phase of the period the
m-letter measurement window lands on, exactly the E2 question applied
to D(m) itself instead of a support count.

--- Candidate forms ---
For a family with (p,q) such that D_end(m) = floor((p*m+1)/q) (the
established law, W6D-G RESULTS_D1.md, P1a/P1b in DERIVATION_NOTES):
  - "+1 form":  floor((p*m+1)/q)
  - "-1 mirror": floor((p*m-1)/q) -- SAME (p,q), just the -1 offset.
    This is the established convention used throughout W6E, NOT a
    P=2q-p substitution: e3_prefix_tightness.py's own `prefix_bound(k,
    p, q, mirror=True)` = `(p*k-1)//q` (same p,q, offset only), and
    e1_walkers.py's real-system mirror law is `floor((22m-1)/53)` --
    same (p,q)=(22,53) as the system's own +1-form law, offset only.
    (A first draft of this script tried P=2q-p in the mirror form,
    matching e2_phase_pinning.py's UNRELATED `make_mechanical_word`
    convergent-P convention -- wrong object, caught by cross-checking
    against e1/e3's own `mirror` usage above before trusting the
    result; corrected to same-(p,q) offset-only, per the established
    convention.)

golden-per8: p=3, q=8 (beta=3/8, established D_per=floor((3m+1)/8),
  W6D-G RESULTS_D1.md).
sqrt2-per12: p=7, q=12 (beta=7/12, D_per=floor((7m+1)/12), W6D-G
  RESULTS_D1.md).

Frozen prediction (Fable): end-anchoring pairs with the -1 mirror
form, start-anchoring with the +1 form -- 65%.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "w6e"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import bfs_Dm_fast
from underlock_words import credit_golden_per8, credit_sqrt2_per12

HERE = Path(__file__).parent

FAMILIES = {
    "golden": {"credit_fn": credit_golden_per8, "p": 3, "q": 8},
    "sqrt2": {"credit_fn": credit_sqrt2_per12, "p": 7, "q": 12},
}


def plus1_form(m, p, q):
    return (p * m + 1) // q


def minus1_mirror_form(m, p, q):
    """SAME (p,q) as plus1_form, offset only -- the established
    convention (e3_prefix_tightness.py prefix_bound(mirror=True),
    e1_walkers.py d_real_mirror), NOT a P=2q-p substitution."""
    return (p * m - 1) // q


def C_for_m(m):
    return 12 if m <= 11 else 14


def main():
    all_rows = []
    match_tally = {}  # (family, anchoring, form_label) -> [hits, total]

    for fam, spec in FAMILIES.items():
        credit_fn = spec["credit_fn"]
        p, q = spec["p"], spec["q"]
        print(f"\n=== {fam}-per{q} (p={p}, q={q}) ===")
        for m in range(2, 14):
            C = C_for_m(m)
            D_start = bfs_Dm_fast(credit_fn, m, C, anchor_steps=m)       # phase=0
            D_end = bfs_Dm_fast(credit_fn, m, C, anchor_steps=53)        # phase=53-m

            f_plus = plus1_form(m, p, q)
            f_minus = minus1_mirror_form(m, p, q)

            start_matches_plus = (D_start == f_plus)
            start_matches_minus = (D_start == f_minus)
            end_matches_plus = (D_end == f_plus)
            end_matches_minus = (D_end == f_minus)

            for label, val in [("start_vs_plus1", start_matches_plus),
                                ("start_vs_minus1mirror", start_matches_minus),
                                ("end_vs_plus1", end_matches_plus),
                                ("end_vs_minus1mirror", end_matches_minus)]:
                key = (fam, label)
                match_tally.setdefault(key, [0, 0])
                match_tally[key][0] += int(val)
                match_tally[key][1] += 1

            print(f"  m={m:>2}: D_start={D_start:>2} D_end={D_end:>2} | "
                  f"+1form={f_plus:>2} -1mirror={f_minus:>2} | "
                  f"start==+1:{start_matches_plus} start==-1mir:{start_matches_minus} "
                  f"end==+1:{end_matches_plus} end==-1mir:{end_matches_minus}")

            all_rows.append({
                "family": fam, "m": m, "p": p, "q": q,
                "D_start": D_start, "D_end": D_end,
                "plus1_form": f_plus, "minus1_mirror_form": f_minus,
                "start_matches_plus1": start_matches_plus,
                "start_matches_minus1mirror": start_matches_minus,
                "end_matches_plus1": end_matches_plus,
                "end_matches_minus1mirror": end_matches_minus,
            })

    print("\n\n=== MATCH TALLY (per family x anchoring x candidate form) ===")
    for (fam, label), (hits, total) in sorted(match_tally.items()):
        print(f"  {fam} {label}: {hits}/{total} rows match")

    print("\n=== FROZEN PREDICTION: end-anchoring pairs with the -1 mirror "
          "form, start-anchoring with the +1 form (65%) ===")
    for fam in FAMILIES:
        end_minus_hits, end_minus_total = match_tally[(fam, "end_vs_minus1mirror")]
        start_plus_hits, start_plus_total = match_tally[(fam, "start_vs_plus1")]
        end_plus_hits, end_plus_total = match_tally[(fam, "end_vs_plus1")]
        start_minus_hits, start_minus_total = match_tally[(fam, "start_vs_minus1mirror")]
        print(f"  {fam}:")
        print(f"    end-anchored vs -1mirror: {end_minus_hits}/{end_minus_total}  "
              f"(predicted pairing)")
        print(f"    start-anchored vs +1form: {start_plus_hits}/{start_plus_total}  "
              f"(predicted pairing)")
        print(f"    [contrast] end-anchored vs +1form: {end_plus_hits}/{end_plus_total}")
        print(f"    [contrast] start-anchored vs -1mirror: "
              f"{start_minus_hits}/{start_minus_total}")
        predicted_pairing_clean = (end_minus_hits == end_minus_total and
                                    start_plus_hits == start_plus_total)
        contrast_pairing_clean = (end_plus_hits == end_plus_total and
                                   start_minus_hits == start_minus_total)
        if predicted_pairing_clean and not contrast_pairing_clean:
            verdict = "HIT (predicted pairing clean, contrast pairing is not)"
        elif contrast_pairing_clean and not predicted_pairing_clean:
            verdict = ("MISS -- the OPPOSITE pairing is clean instead "
                       "(end<->+1form, start<->-1mirror)")
        elif predicted_pairing_clean and contrast_pairing_clean:
            verdict = "AMBIGUOUS -- both pairings clean (forms coincide at this scope)"
        else:
            verdict = "MISS -- neither pairing is clean across all rows"
        print(f"    VERDICT ({fam}): {verdict}")

    with open(HERE / "f3_anchoring_map.csv", "w", newline="") as f:
        fieldnames = ["family", "m", "p", "q", "D_start", "D_end",
                      "plus1_form", "minus1_mirror_form",
                      "start_matches_plus1", "start_matches_minus1mirror",
                      "end_matches_plus1", "end_matches_minus1mirror"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in all_rows:
            w.writerow(r)
    print(f"\nWrote f3_anchoring_map.csv ({len(all_rows)} rows)")


if __name__ == "__main__":
    main()
