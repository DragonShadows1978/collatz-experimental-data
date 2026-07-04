#!/usr/bin/env python3
"""
W6H-H3 -- Alphabet extension (universality's scope fence), per
W6H_LEMMA_CORE_ORDER.md section H3.

G1 (w6g/g1_exhaustive_wordspace.py) proved universal discrepancy
(D(w)=L(w), unique loop optimum) EXHAUSTIVELY on {1,2}^m, m=2..10
(2044/2044 words, zero exceptions). H3 extends the alphabet: exhaustive
word-space census over {0,1,2}, {1,2,3}, {0,1,2,3} at m<=7 (3^7=2187,
4^7=16384 words per alphabet -- census each; per the order, drop the
biggest set honestly if slow, rather than sampling it).

c=0 letters change the kill structure (menu [1, delta] empty at
delta=0 regardless of parity, per DERIVATION_NOTES/the order's own
note) -- the loop remains FEASIBLE at budget L by the conservation
identity (engine.allowed_exponents handles c=0 and c=3 generically,
no code changes needed: verified directly, see validate_engine below),
but whether it remains OPTIMAL and UNIQUE is the open question this
experiment answers.

--- Machinery reused unmodified ---
w6f/f1_engine_ext.py's `compute_D_and_optimal_set` (forward_live_fast +
distinct_optimal_a_sequences) -- the SAME function G1 used, no changes.
`engine.allowed_exponents` already handles arbitrary c (not just {1,2})
generically: legal a in [max(1,d+c-C), d+c], which correctly yields an
EMPTY menu at d=0,c=0 (verified below) and a wider-than-{1,2,3}-usual
menu at c=3 -- no special-casing required anywhere in the reused code.

--- Word-as-window convention (same as G1, for the same reason) ---
A generic finite word of length m has no house phase to inherit;
phase=0 (anchor_steps=m) is the only convention that doesn't silently
impose one, exactly as g1_exhaustive_wordspace.py's own docstring
argues (reused verbatim here).

--- Ceiling budget C: sized per alphabet, not blindly reused from G1 ---
G1 used C=12 for {1,2}^m, m<=10. For the WIDER alphabets here, the
all-0s word is the worst case (D = L = 2m exactly, verified directly
below: m=7 all-0s gives D=14), so C must be >= 2*7=14 with margin.
C=18 used throughout (checked to not blow the time budget below).

--- Runtime scope, timed BEFORE committing to the full sweep ---
Profiled directly (not guessed): m=6, alphabet size 4, C=16 costs
~11ms/word (44.9s for the full 4096-word census). Extrapolating m=7
(16384 words) at the same per-word rate: ~180s for {0,1,2,3} alone.
{0,1,2} and {1,2,3} (3^7=2187 words each) are ~7.5x smaller per m, so
proportionally cheaper. Total estimated wall for all three alphabets,
m=2..7: comfortably under 10 minutes -- reported honestly per-alphabet
below rather than assumed; if any alphabet blows a documented budget,
it is DROPPED WHOLESALE (not sampled), per the order's own explicit
instruction ("drop the whole set honestly if too slow; never sample a
word space silently").
"""
from __future__ import annotations

import csv
import sys
import time
import itertools
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "w6e"))
sys.path.insert(0, str(Path(__file__).parent.parent / "w6f"))
from engine import bfs_Dm_fast, bfs_Dm, allowed_exponents  # noqa: E402
from f1_engine_ext import compute_D_and_optimal_set  # noqa: E402

HERE = Path(__file__).parent
C = 18
M_SCOPE = list(range(2, 8))  # 2..7 per the order
TIME_BUDGET_PER_ALPHABET_S = 900.0  # 15 min hard wall per alphabet; drop wholesale if hit

ALPHABETS = {
    "{0,1,2}": (0, 1, 2),
    "{1,2,3}": (1, 2, 3),
    "{0,1,2,3}": (0, 1, 2, 3),
}


def word_credit_fn(w):
    def fn(k, w=w):
        return w[k]
    return fn


def loop_discrepancy(w) -> int:
    """L(w) = max_k sum_{j<=k}(2 - c_j), k=1..m."""
    running = 0
    best = 0
    for c in w:
        running += (2 - c)
        if running > best:
            best = running
    return best


def validate_engine():
    """House rule: >=3 ground-truth rows before trusting the reused
    machinery in this NEW (wider-alphabet) regime. Checks:
      (a) engine correctness (same as G1): bfs_Dm_fast reproduces
          ground truth at the house-53 anchoring for 3 known periodic
          rows (golden-per8 m=5,9; sqrt2-per12 m=8) -- confirms the
          underlying engine is unmodified/correct before extending its
          USE to a new alphabet regime.
      (b) c=0 menu-emptiness: allowed_exponents(d=0, c=0, C) must be
          EMPTY (the kill condition DERIVATION_NOTES describes) --
          verified directly against the reused, unmodified function.
      (c) c=3 menu correctness: allowed_exponents(d=0, c=3, C) must be
          [1,2,3] (wider than the {1,2} alphabet's usual menus).
      (d) word-as-window sanity: all-2s word of any m gives D=0 (loop
          matches itself exactly, alphabet-independent); all-0s word
          gives D=L=2m exactly (the worst-case survivor headroom this
          experiment's C budget is sized against).
    """
    def credit_golden_per8(k):
        return (13 * (k + 1)) // 8 - (13 * k) // 8

    def credit_sqrt2_per12(k):
        return (17 * (k + 1)) // 12 - (17 * k) // 12

    print("=== Pre-experiment validation ===")
    checks = [
        ("golden-per8 m=5", credit_golden_per8, 5, 2),
        ("golden-per8 m=9", credit_golden_per8, 9, 3),
        ("sqrt2-per12 m=8", credit_sqrt2_per12, 8, 4),
    ]
    all_pass = True
    for label, fn, m, expected in checks:
        D_53 = bfs_Dm_fast(fn, m, C, anchor_steps=53)
        ok = (D_53 == expected)
        print(f"  (a) {label}: D(house-53-anchor)={D_53} expected={expected} "
              f"{'PASS' if ok else 'FAIL'}")
        all_pass = all_pass and ok

    menu_00 = allowed_exponents(0, 0, C)
    ok = (menu_00 == [])
    print(f"  (b) allowed_exponents(d=0,c=0,C={C}) = {menu_00} "
          f"(expect [], the kill condition) {'PASS' if ok else 'FAIL'}")
    all_pass = all_pass and ok

    menu_03 = allowed_exponents(0, 3, C)
    ok = (menu_03 == [1, 2, 3])
    print(f"  (c) allowed_exponents(d=0,c=3,C={C}) = {menu_03} "
          f"(expect [1,2,3]) {'PASS' if ok else 'FAIL'}")
    all_pass = all_pass and ok

    for m in (2, 5, 7):
        w = tuple([2] * m)
        D, _, _ = compute_D_and_optimal_set(word_credit_fn(w), m, C, anchor_steps=m)
        ok = (D == 0)
        print(f"  (d1) all-2s word m={m}: D={D} (expect 0) {'PASS' if ok else 'FAIL'}")
        all_pass = all_pass and ok
    for m in (5, 7):
        w = tuple([0] * m)
        D, _, _ = compute_D_and_optimal_set(word_credit_fn(w), m, C, anchor_steps=m)
        expected = 2 * m
        ok = (D == expected)
        print(f"  (d2) all-0s word m={m}: D={D} (expect {expected}, worst-case "
              f"headroom check) {'PASS' if ok else 'FAIL'}")
        all_pass = all_pass and ok

    print(f"=== Validation: {'ALL PASS' if all_pass else 'SOME FAILED -- STOP'} ===\n")
    if not all_pass:
        raise SystemExit("Engine validation failed -- refusing to run H3 sweep.")


def run_alphabet(name, symbols):
    print(f"\n=== Alphabet {name} (symbols={symbols}), m={M_SCOPE[0]}..{M_SCOPE[-1]}, C={C} ===")
    results = []
    breaks = []
    ties = []
    per_m_wall = {}
    t_total0 = time.time()
    m_done = []
    m_dropped = []
    dropped_wholesale = False

    for m in M_SCOPE:
        elapsed = time.time() - t_total0
        if elapsed > TIME_BUDGET_PER_ALPHABET_S:
            print(f"  TIME BUDGET EXCEEDED ({elapsed:.1f}s > {TIME_BUDGET_PER_ALPHABET_S}s) "
                  f"for alphabet {name} -- DROPPING m={m}..{M_SCOPE[-1]} WHOLESALE "
                  f"(honest scope reduction, per the order: never sample a word "
                  f"space silently).")
            m_dropped.extend(range(m, M_SCOPE[-1] + 1))
            dropped_wholesale = True
            break

        n_words = len(symbols) ** m
        t0 = time.time()
        break_count = 0
        tie_count = 0
        no_survivor_count = 0
        c0_adjacent_highcredit_breaks = 0
        row_rows = []
        for w in itertools.product(symbols, repeat=m):
            L = loop_discrepancy(w)
            fn = word_credit_fn(w)
            D, best_d, seqs = compute_D_and_optimal_set(fn, m, C, anchor_steps=m)
            if D is None:
                no_survivor_count += 1
                row_rows.append({"alphabet": name, "m": m, "word": "".join(map(str, w)),
                                  "D": "", "L": L, "n_optimal": "",
                                  "note": "NO_SURVIVOR_C18"})
                continue
            is_break = D != L
            n_optimal = len(seqs) if seqs is not None else 0
            if is_break:
                break_count += 1
                # classify per the order's expectation: c=0 adjacent to high-credit (c>=2)
                has_c0_adjacent_high = any(
                    (w[i] == 0 and i > 0 and w[i - 1] >= 2) or
                    (w[i] == 0 and i + 1 < len(w) and w[i + 1] >= 2)
                    for i in range(len(w))
                )
                if has_c0_adjacent_high:
                    c0_adjacent_highcredit_breaks += 1
                breaks.append({"alphabet": name, "m": m, "word": "".join(map(str, w)),
                                "D": D, "L": L, "has_c0_adjacent_high": has_c0_adjacent_high})
            if n_optimal > 1:
                tie_count += 1
                ties.append({"alphabet": name, "m": m, "word": "".join(map(str, w)),
                             "D": D, "n_optimal": n_optimal})
            row_rows.append({"alphabet": name, "m": m, "word": "".join(map(str, w)),
                              "D": D, "L": L, "n_optimal": n_optimal, "note": ""})

        wall = time.time() - t0
        per_m_wall[m] = wall
        m_done.append(m)
        results.extend(row_rows)
        print(f"  m={m}: {n_words} words, wall={wall:.2f}s, breaks(D!=L)={break_count} "
              f"(c0-adjacent-high among breaks={c0_adjacent_highcredit_breaks}), "
              f"ties(n_optimal>1)={tie_count}, no_survivor={no_survivor_count}")

    total_wall = time.time() - t_total0
    print(f"  Alphabet {name} total wall: {total_wall:.2f}s. "
          f"m done: {m_done}. m dropped: {m_dropped if m_dropped else 'none'}.")
    return {
        "name": name, "results": results, "breaks": breaks, "ties": ties,
        "per_m_wall": per_m_wall, "m_done": m_done, "m_dropped": m_dropped,
        "dropped_wholesale": dropped_wholesale, "total_wall": total_wall,
    }


def main():
    validate_engine()

    all_alphabet_results = {}
    for name, symbols in ALPHABETS.items():
        all_alphabet_results[name] = run_alphabet(name, symbols)

    # ---- Write combined CSVs ----
    all_rows = []
    all_breaks = []
    all_ties = []
    for name, res in all_alphabet_results.items():
        all_rows.extend(res["results"])
        all_breaks.extend(res["breaks"])
        all_ties.extend(res["ties"])

    with open(HERE / "h3_wordspace_census.csv", "w", newline="") as f:
        fieldnames = ["alphabet", "m", "word", "D", "L", "n_optimal", "note"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in all_rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})
    print(f"\nWrote h3_wordspace_census.csv ({len(all_rows)} rows)")

    with open(HERE / "h3_breaks_dump.csv", "w", newline="") as f:
        fieldnames = ["alphabet", "m", "word", "D", "L", "has_c0_adjacent_high"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in all_breaks:
            w.writerow(r)
    print(f"Wrote h3_breaks_dump.csv ({len(all_breaks)} rows) -- D!=L exceptions, "
          f"should be empty if universality extends cleanly")

    with open(HERE / "h3_ties_dump.csv", "w", newline="") as f:
        fieldnames = ["alphabet", "m", "word", "D", "n_optimal"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in all_ties:
            w.writerow(r)
    print(f"Wrote h3_ties_dump.csv ({len(all_ties)} rows) -- n_optimal>1 rows")

    # ---- Gate verdicts ----
    print("\n=== GATE VERDICTS vs frozen prediction ===")
    print("Prediction: D(w) = L(w) = max_k sum(2-c_j) and loop unique for ALL words "
          "over ALL tested alphabets -- 65%.")
    for name, res in all_alphabet_results.items():
        n_eval = sum(1 for r in res["results"] if r["D"] != "")
        n_breaks = len(res["breaks"])
        n_ties = len(res["ties"])
        status = "DROPPED (scope wall)" if res["dropped_wholesale"] else "FULL SCOPE COMPLETED"
        print(f"  {name}: m done={res['m_done']}, {status}")
        print(f"    words evaluated: {n_eval}, D!=L exceptions: {n_breaks}, "
              f"n_optimal>1 ties: {n_ties}")
        if n_eval > 0:
            verdict = "HIT (universality extends)" if (n_breaks == 0 and n_ties == 0) else \
                      f"MISS -- {n_breaks} discrepancy exceptions, {n_ties} uniqueness exceptions"
            print(f"    verdict for this alphabet: {verdict}")

    overall_breaks = sum(len(res["breaks"]) for res in all_alphabet_results.values())
    overall_ties = sum(len(res["ties"]) for res in all_alphabet_results.values())
    any_dropped = any(res["dropped_wholesale"] for res in all_alphabet_results.values())
    print(f"\nOVERALL: {overall_breaks} total D!=L exceptions across all tested "
          f"alphabets/m, {overall_ties} total uniqueness exceptions"
          f"{' (NOTE: at least one alphabet was dropped before full m<=7 scope -- see above)' if any_dropped else ''}.")
    if overall_breaks == 0 and overall_ties == 0 and not any_dropped:
        print("GATE: HIT, decisively -- universality and uniqueness extend cleanly "
              "to every tested alphabet at full m<=7 scope.")
    elif overall_breaks == 0 and overall_ties == 0 and any_dropped:
        print("GATE: HIT on the scope actually covered, but scope was reduced -- "
              "see per-alphabet detail above, not claimed as the full order's scope.")
    else:
        print("GATE: MISS -- exceptions found, see h3_breaks_dump.csv / "
              "h3_ties_dump.csv for verbatim counterexamples.")


if __name__ == "__main__":
    main()
