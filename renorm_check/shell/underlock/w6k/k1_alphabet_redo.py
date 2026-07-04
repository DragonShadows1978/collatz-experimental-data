#!/usr/bin/env python3
"""
W6K-K1 -- Alphabet-extension redo (replaces W6H-H3's {1,2,3}/
{0,1,2,3} results, which K0/SYNTHESIS retracted as unreliable due to
the direction seam), per W6K_CONVENTION_PINNING_ORDER.md section K1.

GATED ON K0: Path B (f1_engine_ext.compute_D_and_optimal_set /
engine.bfs_Dm*) FAILED the K0 canonical-order gate (see ledger
W6K-K0) -- its `phase+k` ascending letter consumption is the REVERSE
of the canonical order. Per house rules, K1 does NOT use Path B.
This script uses Path C (`w6k/k0_canonical_engine.canonical_D`,
24/24 K0 PASS) exclusively. Reuses H3's SCAFFOLDING (per-alphabet
time-budget loop, wholesale-drop discipline, CSV dump shape) --
deliberately NOT its conventions (word-as-window forward consumption
via compute_D_and_optimal_set), per the order's own instruction.

Word-as-window convention (same rationale as H3/G1): a generic finite
word has no house phase to inherit; the word IS the whole canonical-
order window, letters given already in CONSUMPTION order (index 0 =
nearest terminal -- for a bare word with no further context, this
just means: read the word left-to-right as the sequence consumed
first-to-last backward from the terminal).

L(w), computed over the SAME canonical order as D: L(w) = max_k
sum_{j<=k} (2 - c_j), k=1..m -- the discrepancy of the trivial
"always a=2" (loop) strategy, i.e. g_loop(k) = sum_{j<=k}(2-c_j) and
L(w) = max_k g_loop(k) (matching D_free's own definition structurally,
with a forced instead of optimized).

Deliverables (per the order): break counts per (alphabet, ceiling-
variant) for BOTH D_ceil and D_free vs L; break dumps; and the
cross-tab against min_k g_loop(k) < 0 (the architect's ceiling
mechanism conjecture, W6H sec 10b: "D = L <=> min_k g_loop(k) >= 0"),
retried here on trustworthy (Path C) data.

Frozen predictions (re-registered on clean instruments, per the order):
  (a) ceiling-ON: D_ceil = max(L, 0) fails somewhere -- 50%
  (b) ceiling-OFF: D_free = L everywhere on ALL alphabets -- 45%
  (c) ceiling conjecture biconditional (breaks <=> min g_loop < 0)
      holds under exactly ONE of the two variants -- 60%
"""
from __future__ import annotations

import csv
import sys
import time
import itertools
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from k0_canonical_engine import canonical_D  # noqa: E402

M_SCOPE = list(range(2, 8))  # 2..7 per the order
TIME_BUDGET_PER_ALPHABET_S = 900.0  # 15 min hard wall per alphabet; drop wholesale if hit
A_CAP = 30  # margin-checked below (2x check on worst-case-shaped words at m up to 7)

ALPHABETS = {
    "{1,2,3}": (1, 2, 3),
    "{0,1,2,3}": (0, 1, 2, 3),
}


def loop_discrepancy_canonical(w) -> int:
    """L(w) = max_k sum_{j<=k}(2-c_j), canonical order (w already given
    in consumption order, index0=nearest terminal -- for a bare word
    this is simply left-to-right)."""
    running = 0
    best = 0
    for c in w:
        running += (2 - c)
        if running > best:
            best = running
    return best


def min_g_loop_canonical(w) -> int:
    """min_k g_loop(k), same canonical order/definition as L above,
    for the ceiling-mechanism cross-tab (architect's conjecture)."""
    running = 0
    best = 0
    for c in w:
        running += (2 - c)
        if running < best:
            best = running
    return best


def validate_cap_margin():
    """House rule: confirm A_CAP is not the binding constraint on a
    representative subsample before trusting the full census (K0
    already validated canonical_D against the hand table at cap=40
    with a 2x margin check; here we re-check specifically at the
    A_CAP=30 this script uses, on worst-case-shaped words for the
    WIDER alphabets K0 never tested -- all-0s/all-3s/alternating,
    m up to 7)."""
    print("=== Pre-census validation: A_CAP margin check on worst-case-shaped words ===")
    probes = []
    for m in (5, 6, 7):
        probes.append(tuple([0] * m))
        probes.append(tuple([3] * m))
        probes.append(tuple(([0, 3] * ((m + 1) // 2))[:m]))
        probes.append(tuple(([3, 0] * ((m + 1) // 2))[:m]))
    all_ok = True
    for w in probes:
        for ceiling_on in (True, False):
            d1 = canonical_D(w, ceiling_on, a_cap=A_CAP)
            d2 = canonical_D(w, ceiling_on, a_cap=A_CAP * 2)
            ok = (d1 == d2)
            all_ok = all_ok and ok
            if not ok:
                print(f"  *** MARGIN FAIL *** word={w} ceiling_on={ceiling_on}: "
                      f"cap={A_CAP}->{d1}, cap={A_CAP*2}->{d2}")
    print(f"  {'ALL PASS' if all_ok else 'SOME FAILED -- widen A_CAP'} "
          f"({len(probes)} probe words x 2 ceiling variants = {len(probes)*2} checks)\n")
    if not all_ok:
        raise SystemExit("A_CAP margin check failed -- refusing to run census with an "
                          "unvalidated exponent cap.")


def run_alphabet(name, symbols):
    print(f"\n=== Alphabet {name} (symbols={symbols}), m={M_SCOPE[0]}..{M_SCOPE[-1]} ===")
    results = []
    breaks_ceil = []
    breaks_free = []
    per_m_wall = {}
    t_total0 = time.time()
    m_done = []
    m_dropped = []
    dropped_wholesale = False

    crosstab = {
        "ceil": {"TP": 0, "TN": 0, "FP": 0, "FN": 0},
        "free": {"TP": 0, "TN": 0, "FP": 0, "FN": 0},
    }

    for m in M_SCOPE:
        elapsed = time.time() - t_total0
        if elapsed > TIME_BUDGET_PER_ALPHABET_S:
            print(f"  TIME BUDGET EXCEEDED ({elapsed:.1f}s > {TIME_BUDGET_PER_ALPHABET_S}s) "
                  f"for alphabet {name} -- DROPPING m={m}..{M_SCOPE[-1]} WHOLESALE "
                  f"(honest scope reduction, per the order: never sample silently).")
            m_dropped.extend(range(m, M_SCOPE[-1] + 1))
            dropped_wholesale = True
            break

        n_words = len(symbols) ** m
        t0 = time.time()
        break_ceil_count = 0
        break_free_count = 0
        row_rows = []
        for w in itertools.product(symbols, repeat=m):
            L = loop_discrepancy_canonical(w)
            ming = min_g_loop_canonical(w)
            D_ceil = canonical_D(w, True, a_cap=A_CAP)
            D_free = canonical_D(w, False, a_cap=A_CAP)

            is_break_ceil = (D_ceil != L)
            is_break_free = (D_free != L)
            if is_break_ceil:
                break_ceil_count += 1
                breaks_ceil.append({"alphabet": name, "m": m, "word": "".join(map(str, w)),
                                     "D_ceil": D_ceil, "L": L, "min_g_loop": ming})
            if is_break_free:
                break_free_count += 1
                breaks_free.append({"alphabet": name, "m": m, "word": "".join(map(str, w)),
                                     "D_free": D_free, "L": L, "min_g_loop": ming})

            conj_pred = (ming >= 0)
            for variant, D in (("ceil", D_ceil), ("free", D_free)):
                actual = (D == L)
                if actual and conj_pred:
                    crosstab[variant]["TP"] += 1
                elif (not actual) and (not conj_pred):
                    crosstab[variant]["TN"] += 1
                elif actual and not conj_pred:
                    crosstab[variant]["FP"] += 1
                else:
                    crosstab[variant]["FN"] += 1

            row_rows.append({"alphabet": name, "m": m, "word": "".join(map(str, w)),
                              "D_ceil": D_ceil, "D_free": D_free, "L": L,
                              "min_g_loop": ming,
                              "break_ceil": is_break_ceil, "break_free": is_break_free})

        wall = time.time() - t0
        per_m_wall[m] = wall
        m_done.append(m)
        results.extend(row_rows)
        print(f"  m={m}: {n_words} words, wall={wall:.2f}s, "
              f"breaks(D_ceil!=L)={break_ceil_count}, breaks(D_free!=L)={break_free_count}")

    total_wall = time.time() - t_total0
    print(f"  Alphabet {name} total wall: {total_wall:.2f}s. m done: {m_done}. "
          f"m dropped: {m_dropped if m_dropped else 'none'}.")
    return {
        "name": name, "results": results, "breaks_ceil": breaks_ceil,
        "breaks_free": breaks_free, "per_m_wall": per_m_wall, "m_done": m_done,
        "m_dropped": m_dropped, "dropped_wholesale": dropped_wholesale,
        "total_wall": total_wall, "crosstab": crosstab,
    }


def main():
    validate_cap_margin()

    all_alphabet_results = {}
    for name, symbols in ALPHABETS.items():
        all_alphabet_results[name] = run_alphabet(name, symbols)

    all_rows = []
    all_breaks_ceil = []
    all_breaks_free = []
    for name, res in all_alphabet_results.items():
        all_rows.extend(res["results"])
        all_breaks_ceil.extend(res["breaks_ceil"])
        all_breaks_free.extend(res["breaks_free"])

    with open(HERE / "k1_wordspace_census.csv", "w", newline="") as f:
        fieldnames = ["alphabet", "m", "word", "D_ceil", "D_free", "L", "min_g_loop",
                      "break_ceil", "break_free"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in all_rows:
            w.writerow(r)
    print(f"\nWrote k1_wordspace_census.csv ({len(all_rows)} rows)")

    with open(HERE / "k1_breaks_ceil_dump.csv", "w", newline="") as f:
        fieldnames = ["alphabet", "m", "word", "D_ceil", "L", "min_g_loop"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in all_breaks_ceil:
            w.writerow(r)
    print(f"Wrote k1_breaks_ceil_dump.csv ({len(all_breaks_ceil)} rows)")

    with open(HERE / "k1_breaks_free_dump.csv", "w", newline="") as f:
        fieldnames = ["alphabet", "m", "word", "D_free", "L", "min_g_loop"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in all_breaks_free:
            w.writerow(r)
    print(f"Wrote k1_breaks_free_dump.csv ({len(all_breaks_free)} rows)")

    print("\n=== GATE VERDICTS vs frozen predictions (K1) ===")
    for name, res in all_alphabet_results.items():
        n_eval = len(res["results"])
        n_breaks_ceil = len(res["breaks_ceil"])
        n_breaks_free = len(res["breaks_free"])
        status = "DROPPED (scope wall)" if res["dropped_wholesale"] else "FULL SCOPE COMPLETED"
        print(f"\n  {name}: m done={res['m_done']}, {status}, words evaluated={n_eval}")
        print(f"    D_ceil!=L breaks: {n_breaks_ceil}  |  D_free!=L breaks: {n_breaks_free}")
        ct = res["crosstab"]
        for variant in ("ceil", "free"):
            c = ct[variant]
            total = sum(c.values())
            acc = (c["TP"] + c["TN"]) / total if total else float("nan")
            print(f"    conjecture cross-tab (D_{variant}): TP={c['TP']} TN={c['TN']} "
                  f"FP={c['FP']} FN={c['FN']}  accuracy={acc:.4f}  "
                  f"biconditional_holds_exactly={'YES' if (c['FP']==0 and c['FN']==0) else 'NO'}")

    overall_breaks_ceil = sum(len(res["breaks_ceil"]) for res in all_alphabet_results.values())
    overall_breaks_free = sum(len(res["breaks_free"]) for res in all_alphabet_results.values())
    overall_n = sum(len(res["results"]) for res in all_alphabet_results.values())
    any_dropped = any(res["dropped_wholesale"] for res in all_alphabet_results.values())

    print(f"\nOVERALL: {overall_n} words evaluated across both alphabets. "
          f"D_ceil!=L: {overall_breaks_ceil} ({100*overall_breaks_ceil/overall_n:.2f}%). "
          f"D_free!=L: {overall_breaks_free} ({100*overall_breaks_free/overall_n:.2f}%)."
          f"{' (scope reduced -- see per-alphabet detail)' if any_dropped else ''}")

    max_l0_fail_count = sum(1 for r in all_rows if r["D_ceil"] != max(r["L"], 0))
    pred_a_hit = max_l0_fail_count > 0
    print(f"\n(a) D_ceil = max(L,0) fails somewhere (50%): "
          f"{'HIT' if pred_a_hit else 'MISS'} -- {max_l0_fail_count} rows where "
          f"D_ceil != max(L,0) (out of {overall_n})")

    pred_b_hit = (overall_breaks_free == 0) and not any_dropped
    print(f"(b) D_free = L everywhere, all alphabets (45%): "
          f"{'HIT' if pred_b_hit else 'MISS'} -- {overall_breaks_free} D_free!=L exceptions"
          f"{' (scope was reduced)' if any_dropped else ''}")

    holds_ceil = all(
        (res["crosstab"]["ceil"]["FP"] == 0 and res["crosstab"]["ceil"]["FN"] == 0)
        for res in all_alphabet_results.values()
    )
    holds_free = all(
        (res["crosstab"]["free"]["FP"] == 0 and res["crosstab"]["free"]["FN"] == 0)
        for res in all_alphabet_results.values()
    )
    n_holding = int(holds_ceil) + int(holds_free)
    pred_c_hit = (n_holding == 1)
    print(f"(c) biconditional holds under EXACTLY ONE variant (60%): "
          f"{'HIT' if pred_c_hit else 'MISS'} -- holds_under_ceil={holds_ceil}, "
          f"holds_under_free={holds_free} ({n_holding} variant(s) holding cleanly)")


if __name__ == "__main__":
    main()
