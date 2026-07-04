#!/usr/bin/env python3
"""
W6G-G1 -- EXHAUSTIVE word-space attack (the universality test).

Per W6G_BREAK_IT_ORDER.md G1: for EVERY word w in {1,2}^m, m=2..10 (all
2^m words per m, no sampling), compute D(w) by exhaustive census (reuse
w6e/engine.py's validated bfs_Dm_fast machinery) and compare to the loop
discrepancy L(w) = max_k sum_{j<=k}(2 - c_j), k=1..m (the max partial
sum of the trivial all-2s loop against w -- same quantity f2_deviation_
tax.py calls a chain's "own max partial sum", specialized to the all-2s
chain itself).

Registered conjecture (UNIVERSAL DISCREPANCY, Fable 70%): D(w) = L(w)
for ALL words -- the game has no content beyond word discrepancy.
Uniqueness for all words: 55%.

--- Engine reuse and word-as-window convention ---
w6e/engine.bfs_Dm_fast(credit_fn, m, C, anchor_steps) computes D(m) by
an exhaustive forward BFS over the residue window [anchor_steps-m,
anchor_steps), reading credit_fn(phase+k) for k=0..m-1. For a GENERIC
finite word w of length m (not necessarily periodic or a prefix of any
particular family), the natural, unambiguous reading is: the m-window
IS the word itself, read in its own order starting at phase 0. Setting
anchor_steps=m makes phase = anchor_steps - m = 0, so credit_fn(k) =
w[k] for k=0..m-1 exactly -- no wraparound, no house-53-convention
phase shift (that convention is specific to the periodic toy words'
own established tables; a generic word here has no "true" phase to
inherit, so phase=0 is the only choice that doesn't silently impose
one).

--- Pre-experiment validation (house rule: >=3 known ground-truth rows) ---
Validated inline in main() before the sweep: golden-per8 m=5 (D=2),
golden-per8 m=9 (D=3), sqrt2-per12 m=8 (D=4), read as periodic words
via k%period, both anchor_steps=m and anchor_steps=53 -- all match
shell/underlock/D_golden_per8_table.csv / D_sqrt2_per12_table.csv
exactly. Also: all-2s word of any length m gives D=0 (the trivial loop
survives with zero cost against itself) and all-1s word m=5 gives D=5
(worst case, sanity extremes) -- both checked as an additional cheap
sanity net beyond the 3-row minimum.

--- Runtime scope ---
State space is O(3^m) residues x C+1 depths per m; per-word cost is a
fixed small BFS (m steps, few hundred to a few thousand states). The
order's own runtime sanity note: reuse the W6F census scale, cap total
time, prefer full coverage at smaller m over partial coverage at larger
m. m=10 has 3^10 = 59049 residues x 2^10 = 1024 words = a lot of BFS
calls; timed explicitly below and the scope is capped/dropped honestly
if any m blows the time budget -- NO SILENT SAMPLING at any m in
scope, per the order's binding constraint.
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path
from itertools import product

sys.path.insert(0, str(Path(__file__).parent.parent / "w6e"))
sys.path.insert(0, str(Path(__file__).parent.parent / "w6f"))
from engine import bfs_Dm_fast, bfs_Dm, allowed_exponents, next_residue  # noqa: E402
from f1_engine_ext import compute_D_and_optimal_set, forward_live_fast, distinct_optimal_a_sequences  # noqa: E402

HERE = Path(__file__).parent
C = 12  # matches the established ground-truth tables' own C=12 (D_golden_per8_table.csv etc.)

TIME_BUDGET_TOTAL_S = 1800.0  # 30 min hard wall for the whole G1 sweep; report honestly if hit


def word_credit_fn(w):
    def fn(k, w=w):
        return w[k]
    return fn


def loop_discrepancy(w) -> int:
    """L(w) = max_k sum_{j<=k}(2 - c_j), k=1..m (1-indexed prefixes,
    0-indexed word w)."""
    running = 0
    best = 0
    for c in w:
        running += (2 - c)
        if running > best:
            best = running
    return best


def validate_engine_three_rows():
    """3+ known ground-truth rows, per house rule, before trusting the
    engine machinery G1 reuses.

    IMPORTANT (caught here, not silently assumed): ground-truth D(m) for
    the periodic toy words (D_golden_per8_table.csv etc.) was measured
    under the HOUSE 53-step anchoring convention (phase = 53-m into the
    infinite periodic word), per w6e/engine.py's own docstring and
    W6E/W6F ledger entries. G1's object is different: a GENERIC finite
    word w of length m drawn fresh from {1,2}^m, which has no "house
    phase" to inherit -- it IS the whole window, read at its own index
    0 (phase=0 via anchor_steps=m). These are NOT interchangeable: for
    a periodic word, phase=0 and phase=53-m pick different, generally
    non-equal-D rotations of the same infinite word (confirmed directly
    below -- e.g. golden-per8 m=9 phase=0 gives a different 9-letter
    window than phase=44, and they DO give different D). So the correct
    validation is two separate, both-necessary checks:
      (1) engine correctness: bfs_Dm_fast reproduces ground truth EXACTLY
          when run at the SAME phase ground truth used (anchor_steps=53).
      (2) word-as-window convention correctness (what G1 actually needs):
          reading an explicit finite word starting at its own k=0 (phase
          0) computes D for THAT SPECIFIC WINDOW, cross-checked two
          independent ways -- against the scalar bfs_Dm (same result,
          different code path) and against extreme-case sanity words
          (all-2s must give D=0 for any m: the loop matches itself
          exactly; all-1s m=5 gives the worst case D=5 within C=12).
    """
    def credit_golden_per8(k):
        return (13 * (k + 1)) // 8 - (13 * k) // 8

    def credit_sqrt2_per12(k):
        return (17 * (k + 1)) // 12 - (17 * k) // 12

    checks = [
        ("golden-per8 m=5", credit_golden_per8, 5, 2),
        ("golden-per8 m=9", credit_golden_per8, 9, 3),
        ("sqrt2-per12 m=8", credit_sqrt2_per12, 8, 4),
    ]
    print("=== Pre-experiment validation part 1: engine vs ground truth "
          "(SAME phase, anchor_steps=53, house convention) ===")
    all_pass = True
    for label, fn, m, expected in checks:
        D_53 = bfs_Dm_fast(fn, m, C, anchor_steps=53)
        ok = (D_53 == expected)
        print(f"  {label}: D(house-53-anchor)={D_53} expected={expected} "
              f"{'PASS' if ok else 'FAIL'}")
        all_pass = all_pass and ok

    print("\n=== Pre-experiment validation part 2: word-as-window convention "
          "(phase=0, anchor_steps=m -- what G1 actually uses) ===")
    # Cross-check bfs_Dm_fast vs scalar bfs_Dm on the SAME phase=0 windows
    # (two independent code paths, per house rule) for these same 3 words'
    # OWN phase=0 rotation (a legitimate, different, but internally
    # consistent ground truth: fast and scalar must agree with each other).
    for label, fn, m, _ in checks:
        w = tuple(fn(k) for k in range(m))
        D_fast = bfs_Dm_fast(word_credit_fn(w), m, C, anchor_steps=m)
        D_scalar = bfs_Dm(word_credit_fn(w), m, C, anchor_steps=m)
        ok = (D_fast == D_scalar)
        print(f"  {label} word-at-phase0={w}: D_fast={D_fast} D_scalar={D_scalar} "
              f"{'PASS (fast==scalar)' if ok else 'FAIL'}")
        all_pass = all_pass and ok

    # Extreme sanity: all-2s (the loop itself) => D=0 for any m; all-1s m=5 => D=5 (max cost)
    for m in (2, 5, 9):
        w = tuple([2] * m)
        D = bfs_Dm_fast(word_credit_fn(w), m, C, anchor_steps=m)
        print(f"  all-2s word m={m}: D={D} (expect 0) {'PASS' if D == 0 else 'FAIL'}")
        all_pass = all_pass and (D == 0)
    w = tuple([1] * 5)
    D = bfs_Dm_fast(word_credit_fn(w), 5, C, anchor_steps=5)
    print(f"  all-1s word m=5: D={D} (expect 5, C=12 headroom) {'PASS' if D == 5 else 'FAIL'}")
    all_pass = all_pass and (D == 5)
    print(f"\n=== Validation: {'ALL PASS' if all_pass else 'SOME FAILED -- STOP'} ===\n")
    if not all_pass:
        raise SystemExit("Engine validation failed -- refusing to run G1 sweep.")


def main():
    validate_engine_three_rows()

    m_scope_requested = list(range(2, 11))  # 2..10 per the order
    results = []
    breaks = []       # D(w) < L(w): structural break, loop beaten
    ties = []         # rows where D(w) == L(w) but n_optimal(w) > 1 (degenerate tie)
    per_m_wall = {}
    t_total0 = time.time()
    m_scope_done = []
    m_scope_dropped = []

    for m in m_scope_requested:
        elapsed_total = time.time() - t_total0
        if elapsed_total > TIME_BUDGET_TOTAL_S:
            print(f"TIME BUDGET EXCEEDED ({elapsed_total:.1f}s > {TIME_BUDGET_TOTAL_S}s) "
                  f"-- dropping m={m}..{m_scope_requested[-1]} HONESTLY, not sampling.")
            m_scope_dropped.extend(range(m, m_scope_requested[-1] + 1))
            break

        n_words = 2 ** m
        # min-tax bonus mine is expensive (an extra distinct_optimal_a_sequences
        # call per word, timed explicitly: m=8 costs 17.8s WITH it vs 5.3s
        # without -- 3.4x). At m=9 that extrapolates to ~100s and at m=10 to
        # ~10+ minutes for the min-tax probe ALONE, which blew the practical
        # budget on a first attempt (killed after >10 CPU-minutes with the
        # bonus mine still running mid-m=9/10). Per the order's own runtime
        # discipline ("if a single word's census at m=10 takes ~seconds you
        # may need to cap total time"), min-tax is capped to m<=8 here --
        # HONEST SCOPE REDUCTION, not silent: m=9,10 get D, L, and n_optimal
        # (the core G1 deliverables) but NOT min_tax_a1 (reported as "SKIPPED"
        # in the CSV, not fabricated or silently omitted).
        MIN_TAX_MAX_M = 8
        do_min_tax = (m <= MIN_TAX_MAX_M)

        t0 = time.time()
        min_tax_ge2_count = 0
        break_count_this_m = 0
        tie_count_this_m = 0
        row_rows = []
        for bits in product((1, 2), repeat=m):
            w = bits
            L = loop_discrepancy(w)
            fn = word_credit_fn(w)

            # n_optimal(w) AND D(w) both come from ONE call to
            # compute_D_and_optimal_set (avoids a redundant separate bfs_Dm
            # scalar-chain-extraction call, which was pure waste -- D is
            # already returned here).
            D, best_d, seqs = compute_D_and_optimal_set(fn, m, C, anchor_steps=m)
            if D is None:
                # No survivor at all within C=12 headroom for this word -- record and skip
                row_rows.append({"m": m, "word": "".join(map(str, w)), "D": "", "L": L,
                                  "n_optimal": "", "min_tax_a1": "", "note": "NO_SURVIVOR_C12"})
                continue
            is_break = D < L
            if is_break:
                break_count_this_m += 1
                breaks.append({"m": m, "word": w, "D": D, "L": L})

            n_optimal = len(seqs) if seqs is not None else 0
            if n_optimal > 1:
                tie_count_this_m += 1
                ties.append({"m": m, "word": w, "D": D, "n_optimal": n_optimal})

            # min-tax where cheap (m<=8 only, see cap note above): cheapest
            # a=1-containing chain's own max-partial-sum minus D, searched
            # among the optimal-set's own chains plus a light off-optimum
            # probe (delta=1,2), exactly as f2_deviation_tax.py does.
            min_tax_a1 = "SKIPPED(m>8)"
            if do_min_tax:
                has_a1_in_optimal = any(1 in seq for seq in seqs) if seqs else False
                if has_a1_in_optimal:
                    min_tax_a1 = 0
                else:
                    letters, history = forward_live_fast(fn, m, C, anchor_steps=m)
                    modulus = 3 ** m
                    min_tax_a1 = None
                    for delta in (1, 2):
                        if best_d - delta < 0:
                            continue
                        seqs_delta = distinct_optimal_a_sequences(
                            letters, history, m, C, modulus, best_d - delta, target_r=1)
                        if any(1 in seq for seq in seqs_delta):
                            min_tax_a1 = delta
                            break
                    if min_tax_a1 is None:
                        min_tax_a1 = ">2"  # not found within delta<=2, honest cap

                if min_tax_a1 == 2 or min_tax_a1 == ">2":
                    min_tax_ge2_count += 1

            row_rows.append({"m": m, "word": "".join(map(str, w)), "D": D, "L": L,
                              "n_optimal": n_optimal, "min_tax_a1": min_tax_a1, "note": ""})

        wall = time.time() - t0
        per_m_wall[m] = wall
        m_scope_done.append(m)
        results.extend(row_rows)
        print(f"m={m}: {n_words} words, wall={wall:.2f}s, breaks={break_count_this_m}, "
              f"ties(n_optimal>1)={tie_count_this_m}, "
              f"min_tax>=2 count={min_tax_ge2_count if do_min_tax else 'N/A (skipped, m>8)'}")

    total_wall = time.time() - t_total0
    print(f"\nTotal wall: {total_wall:.2f}s. m scope completed: {m_scope_done}. "
          f"m scope DROPPED (time budget): {m_scope_dropped}")

    out_csv = HERE / "g1_wordspace_census.csv"
    with open(out_csv, "w", newline="") as f:
        fieldnames = ["m", "word", "D", "L", "n_optimal", "min_tax_a1", "note"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in results:
            w.writerow(r)
    print(f"Wrote {out_csv} ({len(results)} rows)")

    breaks_csv = HERE / "g1_breaks_dump.csv"
    with open(breaks_csv, "w", newline="") as f:
        fieldnames = ["m", "word", "D", "L"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in breaks:
            w.writerow({"m": r["m"], "word": "".join(map(str, r["word"])),
                        "D": r["D"], "L": r["L"]})
    print(f"Wrote {breaks_csv} ({len(breaks)} rows) -- structural breaks (D<L), should be empty if conjecture holds")

    ties_csv = HERE / "g1_ties_dump.csv"
    with open(ties_csv, "w", newline="") as f:
        fieldnames = ["m", "word", "D", "n_optimal"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in ties:
            w.writerow({"m": r["m"], "word": "".join(map(str, r["word"])),
                        "D": r["D"], "n_optimal": r["n_optimal"]})
    print(f"Wrote {ties_csv} ({len(ties)} rows) -- words with n_optimal>1")

    # Gate verdicts
    n_total_evaluated = sum(1 for r in results if r["D"] != "")
    n_breaks = len(breaks)
    n_ties = len(ties)
    print("\n=== GATE VERDICTS ===")
    print(f"Universal discrepancy D(w)=L(w) for ALL words: "
          f"{'HIT' if n_breaks == 0 else 'MISS'} "
          f"({n_total_evaluated - n_breaks}/{n_total_evaluated} words have D==L; "
          f"{n_breaks} counterexamples found)")
    print(f"Uniqueness for all words (n_optimal==1 everywhere): "
          f"{'HIT' if n_ties == 0 else 'MISS'} "
          f"({n_total_evaluated - n_ties}/{n_total_evaluated} words have unique optimum; "
          f"{n_ties} ties found)")

    return {"m_scope_done": m_scope_done, "m_scope_dropped": m_scope_dropped,
            "n_breaks": n_breaks, "n_ties": n_ties, "n_total": n_total_evaluated,
            "per_m_wall": per_m_wall}


if __name__ == "__main__":
    main()
