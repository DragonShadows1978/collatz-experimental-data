#!/usr/bin/env python3
"""
W6K-K3 -- J1 biconditional retest (replaces W6J-J1, which was
QUARANTINED for having run against W6H-H3's unreliable, direction-
buggy census), per W6K_CONVENTION_PINNING_ORDER.md section K3.

No new prediction (per the order: K1's frozen prediction (c) already
covers this -- see ledger W6K-K1). This script re-derives J1's own
2x2 cross-tab methodology (`min_k_g_loop(word) < 0` vs `D != L`),
UNCHANGED in form, against K1's clean canonical-order census
(`w6k/k1_wordspace_census.csv`, Path C / gated PASS), reported
PER CEILING VARIANT (D_ceil, D_free) as two separate columns, never
collapsed -- matching K1's own crosstab exactly (this script exists
as a focused, dedicated K3 artifact/retest in J1's own original
report shape, not a new computation).
"""
from __future__ import annotations

import csv
from pathlib import Path

HERE = Path(__file__).parent
K1_CSV = HERE / "k1_wordspace_census.csv"


def min_k_g_loop(word: str) -> int:
    """IDENTICAL to w6j/j1_ceiling_mechanism.min_k_g_loop -- min over
    ALL prefixes k=0..len(word)-1, including the empty-prefix baseline
    0 (matching J1's own convention exactly, house rule cross-check
    below)."""
    running = 0
    m = running
    for c in word:
        running += (2 - int(c))
        m = min(m, running)
    return m


def validate_on_known_rows():
    """Same house-rule validation as J1 (hand-checked g_loop), re-run
    here since this is a fresh script reading a different input file."""
    checks = [("22", 0), ("31", -1), ("13", 0)]
    print("=== Pre-experiment validation (house rule, hand-checked g_loop) ===")
    all_ok = True
    for word, expected in checks:
        got = min_k_g_loop(word)
        ok = got == expected
        all_ok = all_ok and ok
        print(f"  word={word!r}: min_k_g_loop={got} expected={expected} "
              f"{'PASS' if ok else 'FAIL'}")
    assert all_ok, "g_loop validation failed -- refusing to run full retest"
    print("All validation checks PASS.\n")


def run_variant(rows, D_field: str, label: str):
    print(f"\n=== Variant: {label} ({D_field} vs L) ===")
    out_rows = []
    for row in rows:
        word = row["word"]
        D = int(row[D_field])
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

    out_csv = HERE / f"k3_j1_crosstab_{D_field.lower()}.csv"
    with open(out_csv, "w", newline="") as f:
        fieldnames = ["alphabet", "m", "word", "D", "L", "is_break",
                      "min_k_g_loop", "predicted_break", "agree"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    print(f"Wrote {out_csv.name} ({len(out_rows)} rows)")

    tt = sum(1 for r in out_rows if r["is_break"] and r["predicted_break"])
    tf = sum(1 for r in out_rows if r["is_break"] and not r["predicted_break"])
    ft = sum(1 for r in out_rows if not r["is_break"] and r["predicted_break"])
    ff = sum(1 for r in out_rows if not r["is_break"] and not r["predicted_break"])

    print("--- 2x2 cross-tab: break/no-break vs min_k_g_loop sign ---")
    print(f"  break & min_k<0      (biconditional holds): {tt}")
    print(f"  break & min_k>=0     (COUNTEREXAMPLE dir A -- break but loop-safe): {tf}")
    print(f"  no-break & min_k<0   (COUNTEREXAMPLE dir B -- loop-unsafe but no break): {ft}")
    print(f"  no-break & min_k>=0  (biconditional holds): {ff}")

    n_total = len(out_rows)
    n_agree = tt + ff
    n_counterex = tf + ft
    print(f"  Total rows: {n_total}, biconditional holds: {n_agree} "
          f"({100*n_agree/n_total:.2f}%), counterexamples: {n_counterex} "
          f"({100*n_counterex/n_total:.2f}%)")

    gate_hit = (n_counterex == 0)
    print(f"  VERDICT ({label}): biconditional holds EXACTLY: "
          f"{'HIT' if gate_hit else 'MISS -- counterexamples exist, dumping verbatim'}")

    counterex_dump = None
    if n_counterex:
        counterex_rows = [r for r in out_rows if not r["agree"]]
        dump_csv = HERE / f"k3_counterexamples_dump_{D_field.lower()}.csv"
        with open(dump_csv, "w", newline="") as f:
            fieldnames = ["alphabet", "m", "word", "D", "L", "is_break",
                          "min_k_g_loop", "predicted_break"]
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in counterex_rows:
                w.writerow({k: r[k] for k in fieldnames})
        print(f"  Wrote {dump_csv.name} ({len(counterex_rows)} rows, verbatim)")
        counterex_dump = dump_csv.name

    return {
        "label": label, "tt": tt, "tf": tf, "ft": ft, "ff": ff,
        "n_total": n_total, "n_agree": n_agree, "n_counterex": n_counterex,
        "gate_hit": gate_hit, "counterex_dump": counterex_dump,
    }


def main():
    validate_on_known_rows()

    if not K1_CSV.exists():
        raise SystemExit(f"K1 census not found at {K1_CSV} -- run k1_alphabet_redo.py first")

    with open(K1_CSV, newline="") as f:
        rows = list(csv.DictReader(f))
    print(f"Loaded {len(rows)} rows from {K1_CSV.name} "
          f"(alphabets: {sorted(set(r['alphabet'] for r in rows))})\n")

    result_ceil = run_variant(rows, "D_ceil", "ceiling-ON")
    result_free = run_variant(rows, "D_free", "ceiling-OFF")

    print("\n=== K3 FINAL SUMMARY (both ceiling variants, per house rules: "
          "never silently collapsed) ===")
    for res in (result_ceil, result_free):
        print(f"  {res['label']}: {res['n_counterex']}/{res['n_total']} counterexamples "
              f"({100*res['n_counterex']/res['n_total']:.2f}%) -- "
              f"{'biconditional HOLDS' if res['gate_hit'] else 'biconditional FAILS'}")
    print("\nNo new prediction this round (per the order): K1's frozen prediction "
          "(c) -- 'the ceiling conjecture biconditional holds under exactly ONE of "
          "the two variants (60%)' -- already covers this retest. K1's own verdict "
          "on (c) was MISS (holds under NEITHER variant exactly). This script's "
          "per-variant counterexample counts and dumps are the decisive, retestable "
          "artifact backing that verdict, independent of K1's own inline crosstab.")


if __name__ == "__main__":
    main()
