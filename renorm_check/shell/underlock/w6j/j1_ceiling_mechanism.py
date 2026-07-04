#!/usr/bin/env python3
"""
W6J-J1 -- Ceiling-mechanism check (universality's boundary), per
W6J_INTERIOR_BOUNDARY_ORDER.md section J1.

Architect conjecture (DERIVATION_NOTES sec 10b, registered): on any
alphabet, D(w) = L(w) <=> the loop's running sum never dips below 0,
i.e. min_k g_loop(k) >= 0, where g_loop(k) = Sum_{j<=k} (2 - c_j)
(running discrepancy of the trivial +1-ray/all-2s loop against the
word's own credit letters, k = 0..m-1, prefix sums).

Input: w6h/h3_wordspace_census.csv (28,392 rows, alphabets {0,1,2},
{1,2,3}, {0,1,2,3}, m=2..7). This is the FULL census the order names
("the FULL W6H-H3 census output"); {1,2} itself is not a column in
this file (that was G1's separate, disjoint, all-clean 2044/2044
census) -- H3's three alphabets are exactly what this script reads.

Machinery: no new engine code needed for computing g_loop -- it is a
direct, trivial function of the word string alone (no residues, no DP,
just a prefix-sum of (2-digit) over the word's own credit letters,
read directly from the `word` column). Validated on 3 known rows
below (house rule) using hand-computed g_loop traces before running
the full census.
"""
from __future__ import annotations

import csv
from pathlib import Path

HERE = Path(__file__).parent
H3_CSV = HERE.parent / "w6h" / "h3_wordspace_census.csv"


def min_k_g_loop(word: str) -> int:
    """min_k of the running sum g_loop(k) = Sum_{j<=k}(2 - c_j), taken
    over ALL prefixes k=0..len(word)-1 (INCLUDING the empty-prefix
    baseline 0 -- i.e. we track the running sum starting from 0 BEFORE
    consuming any letter and take the min over that value too, since
    "never dips below 0" naturally includes the trivial before-any-step
    state). This matches DERIVATION_NOTES' g_loop(k) definition (prefix
    sums of the loop's own per-step discrepancy 2-c_j) and the h1/h2/f2
    scripts' identical "running += (2-c); track" pattern (e.g.
    h2_two_ray_model.ray_discrepancy_plus1, which tracks max instead of
    min of the exact same running quantity) -- reused convention, new
    min-instead-of-max reduction.
    """
    running = 0
    m = running
    for c in word:
        running += (2 - int(c))
        m = min(m, running)
    return m


def validate_on_known_rows():
    """House rule: validate on >=3 known rows before trusting the full
    sweep. Hand-computed:
      - "22": c=[2,2], g_loop=[0,0], min=0 -- pure +1-ray.
      - "31": c=[3,1], g_loop=[-1,0], min=-1 -- ceiling-breaking digit
        3 first.
      - "13": c=[1,3], g_loop=[1,0], min=0 (running sum is 0 or 1 at
        every prefix, never negative).
    """
    checks = [("22", 0), ("31", -1), ("13", 0)]
    print("=== Pre-experiment validation (house rule, hand-checked g_loop) ===")
    all_ok = True
    for word, expected in checks:
        got = min_k_g_loop(word)
        ok = got == expected
        all_ok = all_ok and ok
        print(f"  word={word!r}: min_k_g_loop={got} expected={expected} "
              f"{'PASS' if ok else 'FAIL'}")
    assert all_ok, "g_loop validation failed -- refusing to run full census"
    print("All validation checks PASS.\n")


def main():
    validate_on_known_rows()

    if not H3_CSV.exists():
        raise SystemExit(f"H3 census not found at {H3_CSV}")

    with open(H3_CSV, newline="") as f:
        rows = list(csv.DictReader(f))
    print(f"Loaded {len(rows)} rows from {H3_CSV.name} "
          f"(alphabets: {sorted(set(r['alphabet'] for r in rows))})")

    out_rows = []
    for row in rows:
        word = row["word"]
        D = int(row["D"])
        L = int(row["L"])
        is_break = (D != L)
        mkg = min_k_g_loop(word)
        predicted_break = (mkg < 0)
        agree = (is_break == predicted_break)
        out_rows.append({
            "alphabet": row["alphabet"], "m": row["m"], "word": word,
            "D": D, "L": L, "is_break": is_break,
            "min_k_g_loop": mkg, "predicted_break": predicted_break,
            "agree": agree,
        })

    out_csv = HERE / "j1_ceiling_crosstab.csv"
    with open(out_csv, "w", newline="") as f:
        fieldnames = ["alphabet", "m", "word", "D", "L", "is_break",
                      "min_k_g_loop", "predicted_break", "agree"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    print(f"Wrote {out_csv.name} ({len(out_rows)} rows)")

    # 2x2 cross-tab
    tt = sum(1 for r in out_rows if r["is_break"] and r["predicted_break"])  # break, mkg<0 (predicted)
    tf = sum(1 for r in out_rows if r["is_break"] and not r["predicted_break"])  # break, mkg>=0 -- COUNTEREXAMPLE dir A
    ft = sum(1 for r in out_rows if not r["is_break"] and r["predicted_break"])  # no break, mkg<0 -- COUNTEREXAMPLE dir B
    ff = sum(1 for r in out_rows if not r["is_break"] and not r["predicted_break"])  # no break, mkg>=0

    print("\n=== 2x2 cross-tab: break/no-break vs min_k_g_loop sign ===")
    print(f"  break & min_k<0      (biconditional holds): {tt}")
    print(f"  break & min_k>=0     (COUNTEREXAMPLE dir A -- break but loop-safe): {tf}")
    print(f"  no-break & min_k<0   (COUNTEREXAMPLE dir B -- loop-unsafe but no break): {ft}")
    print(f"  no-break & min_k>=0  (biconditional holds): {ff}")

    n_total = len(out_rows)
    n_agree = tt + ff
    n_counterex = tf + ft
    print(f"\nTotal rows: {n_total}, biconditional holds: {n_agree} "
          f"({100*n_agree/n_total:.2f}%), counterexamples: {n_counterex} "
          f"({100*n_counterex/n_total:.2f}%)")

    gate_hit = (n_counterex == 0)
    print(f"\n=== GATE VERDICT vs frozen prediction ===")
    print(f"Biconditional holds EXACTLY, every break row min_k<0 and every "
          f"non-break row min_k>=0 (80%): {'HIT' if gate_hit else 'MISS -- counterexamples exist, dumping verbatim'}")

    if n_counterex:
        counterex_rows = [r for r in out_rows if not r["agree"]]
        dump_csv = HERE / "j1_counterexamples_dump.csv"
        with open(dump_csv, "w", newline="") as f:
            fieldnames = ["alphabet", "m", "word", "D", "L", "is_break",
                          "min_k_g_loop", "predicted_break", "agree", "direction"]
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in counterex_rows:
                direction = "A_break_but_loopsafe" if (r["is_break"] and not r["predicted_break"]) else "B_loopunsafe_but_nobreak"
                rr = dict(r)
                rr["direction"] = direction
                w.writerow(rr)
        print(f"Wrote {dump_csv.name} ({len(counterex_rows)} rows) -- FULL VERBATIM DUMP")
        print("\n*** COUNTEREXAMPLES (verbatim, first 30) ***")
        for r in counterex_rows[:30]:
            direction = "A_break_but_loopsafe" if (r["is_break"] and not r["predicted_break"]) else "B_loopunsafe_but_nobreak"
            print(f"  [{direction}] alphabet={r['alphabet']} m={r['m']} word={r['word']} "
                  f"D={r['D']} L={r['L']} min_k_g_loop={r['min_k_g_loop']}")
        if len(counterex_rows) > 30:
            print(f"  ... ({len(counterex_rows)-30} more in {dump_csv.name})")

        # breakdown by alphabet and direction
        from collections import Counter
        by_alpha_dir = Counter()
        for r in counterex_rows:
            direction = "A_break_but_loopsafe" if (r["is_break"] and not r["predicted_break"]) else "B_loopunsafe_but_nobreak"
            by_alpha_dir[(r["alphabet"], direction)] += 1
        print("\nCounterexample breakdown by (alphabet, direction):")
        for k, v in sorted(by_alpha_dir.items()):
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
