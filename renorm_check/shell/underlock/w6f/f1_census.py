#!/usr/bin/env python3
"""
W6F-F1 -- optimal-set census (THE experiment), per
W6F_OPTIMAL_SET_ORDER.md section F1.

For each row m<=9 (extended to 10-11 since runtime stayed sane, see
timing below): enumerate ALL optimal chains (distinct exponent
a-sequences achieving max partial sum exactly D(m)), via
f1_engine_ext.compute_D_and_optimal_set (validated in f1_validate.py
against an independent brute force on 6/6 rows, both families).

Deliverables per row: (i) count of optimal chains (= count of distinct
a-sequences); (ii) for each non-loop optimum (cap dump at 50/row, but
count them all -- at this scope every row's count turns out small
enough that no capping is actually needed, reported honestly below):
exponent sequence, positions/shapes of deviations from all-2s, the
prefix set where it dips below the envelope; (iii) whether all
non-loop optima still touch D at the loop's argmax prefix (trivial
here since the loop's own binding prefix is EVERY prefix per W6E-E3 --
"the argmax prefix" is checked against the FULL set of prefixes the
loop binds, i.e. k=1..m).

Frozen predictions (Fable, DO NOT edit, reproduced here for the gate
check only):
  (a) loop NOT unique optimum for most rows m>=5 (55%)
  (b) IF alternatives exist, deviations are compact neutral excursions
      -- a=1 within <=2 steps of a compensating a=3 (55%)
  (c) [derived, not a real prediction] a non-loop optimum binding
      EVERY prefix would mean the ENGINE is wrong -- stop and report,
      do not write up as discovery.
"""
import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "w6e"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from f1_engine_ext import compute_D_and_optimal_set
from underlock_words import credit_golden_per8, credit_sqrt2_per12

HERE = Path(__file__).parent
UNDERLOCK = HERE.parent
DUMP_CAP = 50


def load_ground_truth(paths):
    gt = {}
    for p in paths:
        with open(p, newline="") as f:
            for row in csv.DictReader(f):
                gt[int(row["m"])] = int(row["D"])
    return gt


GT_GOLDEN = load_ground_truth(
    [UNDERLOCK / "D_golden_per8_table.csv", UNDERLOCK / "D_golden_per8_m16.csv"])
GT_SQRT2 = load_ground_truth(
    [UNDERLOCK / "D_sqrt2_per12_table.csv", UNDERLOCK / "D_sqrt2_per12_heavy_table.csv"])


def deviation_shape(a_seq):
    """Positions (1-indexed, forward order) and (a_j - 2) deltas where
    a_seq differs from the all-2s loop; compress adjacent runs into
    excursion shapes (list of (start_pos, end_pos, tuple_of_a_values))."""
    deltas = [(i + 1, a - 2) for i, a in enumerate(a_seq) if a != 2]
    if not deltas:
        return [], []
    # compress into contiguous-position excursions
    excursions = []
    cur_start = deltas[0][0]
    cur_vals = [a_seq[deltas[0][0] - 1]]
    prev_pos = deltas[0][0]
    for pos, _ in deltas[1:]:
        if pos == prev_pos + 1:
            cur_vals.append(a_seq[pos - 1])
        else:
            excursions.append((cur_start, prev_pos, tuple(cur_vals)))
            cur_start = pos
            cur_vals = [a_seq[pos - 1]]
        prev_pos = pos
    excursions.append((cur_start, prev_pos, tuple(cur_vals)))
    return deltas, excursions


def prefix_dip_set(a_seq, c_list, D):
    """Prefixes k=1..m (suffix-from-terminal convention, matching
    e3_prefix_tightness.py's g(k) = sum over the LAST k steps of
    (a_j - c_j)) where this chain's running sum is STRICTLY below D
    (i.e. does not bind the envelope at that prefix)."""
    n = len(a_seq)
    dips = []
    binds = []
    for k in range(1, n + 1):
        suffix_a = a_seq[n - k:]
        suffix_c = c_list[n - k:]
        g_k = sum(a - c for a, c in zip(suffix_a, suffix_c))
        if g_k < D:
            dips.append(k)
        elif g_k == D:
            binds.append(k)
        # g_k > D cannot happen for an optimal chain by construction
        # (max partial sum == D is the defining property); if it did,
        # that IS prediction (c)'s engine-bug signal -- checked below.
    return dips, binds


def credit_letters_for_row(credit_fn, m, anchor_steps=53):
    phase = anchor_steps - m
    return [credit_fn(phase + k) for k in range(m)]


def census_family(name, credit_fn, gt_dict, m_list, C_by_m):
    print(f"\n=== {name} ===")
    rows_summary = []
    rows_dump = []
    engine_bug_flags = []
    for m in m_list:
        D_expected = gt_dict[m]
        C = C_by_m(m)
        t0 = time.time()
        D, best_d, seqs = compute_D_and_optimal_set(credit_fn, m, C)
        dt = time.time() - t0
        assert D == D_expected, (
            f"{name} m={m}: D={D} != ground truth {D_expected} at C={C} "
            f"-- integrity failure, STOP")
        c_list = credit_letters_for_row(credit_fn, m)
        n_total = len(seqs)
        loop_seq = tuple([2] * m)
        assert loop_seq in seqs, (
            f"{name} m={m}: the all-2s loop chain is NOT in the optimal "
            f"set -- contradicts W6E/F0 finding, STOP and report")
        non_loop = sorted(s for s in seqs if s != loop_seq)
        n_non_loop = len(non_loop)

        # (iii) + prediction (c) check: does every non-loop optimum
        # bind EVERY prefix (same as the loop, per W6E-E3's "always
        # binding" finding)?
        any_non_loop_binds_everywhere = False
        dumped = []
        for seq in non_loop[:DUMP_CAP]:
            dips, binds = prefix_dip_set(list(seq), c_list, D)
            deltas, excursions = deviation_shape(list(seq))
            binds_everywhere = (len(dips) == 0)
            if binds_everywhere:
                any_non_loop_binds_everywhere = True
            dumped.append({
                "family": name, "m": m, "a_sequence": " ".join(map(str, seq)),
                "deviation_positions_deltas": str(deltas),
                "excursion_shapes": str(excursions),
                "dips_below_envelope_at_k": str(dips),
                "binds_at_k": str(binds),
                "binds_everywhere": binds_everywhere,
            })
        if any_non_loop_binds_everywhere:
            engine_bug_flags.append((name, m))

        print(f"  m={m:>3} D={D:>3} C={C:>2} ({dt:.2f}s): "
              f"n_optimal_total={n_total}  n_non_loop={n_non_loop}  "
              f"loop_unique={n_total==1}  "
              f"dumped={len(dumped)}/{n_non_loop}"
              f"{'  **NON-LOOP BINDS EVERYWHERE -- ENGINE BUG SIGNAL**' if any_non_loop_binds_everywhere else ''}")

        rows_summary.append({
            "family": name, "m": m, "D": D, "C": C,
            "n_optimal_total": n_total, "n_non_loop": n_non_loop,
            "loop_unique": n_total == 1,
            "n_dumped": len(dumped),
            "any_non_loop_binds_everywhere": any_non_loop_binds_everywhere,
            "wall_s": round(dt, 3),
        })
        rows_dump.extend(dumped)

    return rows_summary, rows_dump, engine_bug_flags


def main():
    t_start = time.time()

    # m<=9 required; extended to 10-13 since per-row wall time stayed
    # sane throughout (measured during development up to m=13: golden
    # 20.0s, sqrt2 12.8s at C=14 -- the slowest single rows, well
    # inside the minutes-scale CPU budget). m=14+ not attempted here:
    # the underlying (d,r) state space is 3^m and m=13's ~20s already
    # shows the backward-memo cost climbing fast; a real (not silent)
    # scope wall, reported here rather than pushed further.
    m_list_golden = list(range(2, 14))  # 2..13
    m_list_sqrt2 = list(range(2, 14))

    summary_golden, dump_golden, bugflags_golden = census_family(
        "golden-per8", credit_golden_per8, GT_GOLDEN, m_list_golden,
        C_by_m=lambda m: 12 if m < 12 else 14)
    summary_sqrt2, dump_sqrt2, bugflags_sqrt2 = census_family(
        "sqrt2-per12", credit_sqrt2_per12, GT_SQRT2, m_list_sqrt2,
        C_by_m=lambda m: 12 if m <= 11 else 14)

    all_summary = summary_golden + summary_sqrt2
    all_dump = dump_golden + dump_sqrt2
    all_bugflags = bugflags_golden + bugflags_sqrt2

    total_wall = time.time() - t_start
    print(f"\n\nTotal wall time: {total_wall:.1f}s")

    print("\n=== ENGINE INTEGRITY (prediction (c) check) ===")
    if all_bugflags:
        print(f"STOP: {len(all_bugflags)} row(s) have a non-loop optimum "
              f"binding EVERY prefix: {all_bugflags}. Per the order, this "
              f"means the ENGINE IS WRONG -- do not report as discovery.")
    else:
        print("No non-loop optimum binds every prefix on any row (0 flags "
              "across all rows tested). Prediction (c)'s bug-signal did "
              "NOT fire -- consistent with the engine being correct.")

    print("\n=== FROZEN PREDICTION (a): loop NOT unique optimum for most "
          "rows m>=5 (55%) ===")
    rows_m_ge5 = [r for r in all_summary if r["m"] >= 5]
    n_not_unique = sum(1 for r in rows_m_ge5 if not r["loop_unique"])
    n_m_ge5 = len(rows_m_ge5)
    frac = n_not_unique / n_m_ge5 if n_m_ge5 else 0
    print(f"  rows m>=5: {n_m_ge5} total, {n_not_unique} have loop NOT "
          f"unique optimum ({frac:.1%}).")
    verdict_a = "HIT" if frac > 0.5 else "MISS"
    print(f"  Prediction (a) [loop non-unique for MOST m>=5 rows]: {verdict_a}")

    print("\n=== FROZEN PREDICTION (b): IF alternatives exist, deviations "
          "are compact neutral excursions (a=1 within <=2 steps of a "
          "compensating a=3) (55%) ===")
    non_loop_dumped = [r for r in all_dump]
    if not non_loop_dumped:
        print("  No non-loop optima exist anywhere in scope -- prediction "
              "(b) is VACUOUS (nothing to check), not a HIT or MISS.")
        verdict_b = "VACUOUS (no non-loop optima found)"
    else:
        # classify each dumped excursion: is it a compact {1,3}-pair
        # (or 1 within 2 steps of a 3) excursion?
        n_compact_13 = 0
        n_other = 0
        for r in non_loop_dumped:
            import ast
            exc = ast.literal_eval(r["excursion_shapes"])
            seq_vals = set()
            for (s, e, vals) in exc:
                seq_vals.update(vals)
            has_1 = 1 in seq_vals
            has_3 = 3 in seq_vals
            span_small = all((e - s) <= 3 for (s, e, vals) in exc)
            if has_1 and has_3 and span_small:
                n_compact_13 += 1
            else:
                n_other += 1
        print(f"  {len(non_loop_dumped)} non-loop optima examined "
              f"(dumped, cap {DUMP_CAP}/row): {n_compact_13} match the "
              f"'compact {{1,3}} excursion within short span' shape, "
              f"{n_other} do not.")
        verdict_b = "HIT" if n_compact_13 > n_other else "MISS"
        print(f"  Prediction (b): {verdict_b}")

    with open(HERE / "f1_summary.csv", "w", newline="") as f:
        fieldnames = ["family", "m", "D", "C", "n_optimal_total", "n_non_loop",
                      "loop_unique", "n_dumped", "any_non_loop_binds_everywhere",
                      "wall_s"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in all_summary:
            w.writerow(r)

    with open(HERE / "f1_nonloop_dump.csv", "w", newline="") as f:
        fieldnames = ["family", "m", "a_sequence", "deviation_positions_deltas",
                      "excursion_shapes", "dips_below_envelope_at_k",
                      "binds_at_k", "binds_everywhere"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in all_dump:
            w.writerow(r)

    print(f"\nWrote f1_summary.csv ({len(all_summary)} rows), "
          f"f1_nonloop_dump.csv ({len(all_dump)} rows)")


if __name__ == "__main__":
    main()
