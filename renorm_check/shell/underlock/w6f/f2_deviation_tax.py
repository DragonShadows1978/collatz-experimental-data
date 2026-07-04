#!/usr/bin/env python3
"""
W6F-F2 -- deviation tax table, per W6F_OPTIMAL_SET_ORDER.md section F2.

For each row m<=8: enumerate ALL admissible chains with max partial sum
<= D(m)+2, using f1_engine_ext's validated primitives (REUSED, not
re-derived): forward_live_fast (boolean-array forward pass, identical
mechanics to engine.bfs_Dm_fast) + distinct_optimal_a_sequences
(memoized backward enumeration, validated against an independent
brute force in f1_validate.py).

Key fact used (verified directly, not assumed): a chain from d0=C
ending at depth d_target at step m has max partial sum EXACTLY
C - d_target (this is the same C-d_survivor identity engine.bfs_Dm
uses for D itself -- see engine.py docstring). So "all chains with max
partial sum <= D+2" = the union, over delta in {0,1,2}, of all chains
ending at terminal depth (best_d - delta), each queried via the SAME
distinct_optimal_a_sequences call used for F1 (just pointed at a
different terminal depth) -- no new engine logic, only a different
terminal-depth argument to an already-validated function.

For each chain, classify its deviation pattern vs the all-2s loop
(multiset of (position, a_j-2) deltas, compressed into excursion
shapes -- reusing f1_census.deviation_shape) and record
Delta = (its exact max partial sum) - D(m) (which equals `delta` by
construction above, but computed independently per chain from its own
a-sequence and the credit word, as a sanity cross-check).

Deliverable: tax histogram by excursion shape, plus the MINIMUM tax
over all chains containing >=1 step with a=1, per row.

Frozen prediction (Fable): if F1 shows the loop unique at D (IT DOES,
see f1_summary.csv: 24/24 rows loop-unique), then min tax of any
a=1-containing chain = +1 exactly, for every row -- 60%.
"""
import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "w6e"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from f1_engine_ext import forward_live_fast, distinct_optimal_a_sequences
from f1_census import deviation_shape
from underlock_words import credit_golden_per8, credit_sqrt2_per12

HERE = Path(__file__).parent
UNDERLOCK = HERE.parent


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


def credit_letters_for_row(credit_fn, m, anchor_steps=53):
    phase = anchor_steps - m
    return [credit_fn(phase + k) for k in range(m)]


def exact_max_partial_sum(a_seq, c_list):
    """Independent cross-check of a chain's max partial sum, computed
    directly from its own a-sequence and credit word (running sum over
    the FULL forward chain from step 0), rather than trusting the
    terminal-depth identity blindly."""
    running = 0
    best = 0
    for a, c in zip(a_seq, c_list):
        running += (a - c)
        best = max(best, running)
    return best


def excursion_shape_label(a_seq):
    """Compact label for a deviation pattern: tuple of (length, values)
    per excursion, e.g. ((1,(1,)),) for a lone a=1, or ((2,(1,3)),) for
    an adjacent {1,3} pair."""
    _, excursions = deviation_shape(list(a_seq))
    labels = tuple((e - s + 1, vals) for (s, e, vals) in excursions)
    return labels


def census_row(name, credit_fn, m, D_expected, C):
    letters, history = forward_live_fast(credit_fn, m, C)
    modulus = 3 ** m
    target_r = 1 % modulus
    final_live = history[m]
    survivors = [d for d in range(C + 1) if final_live[d][target_r]]
    best_d = max(survivors)
    D = C - best_d
    assert D == D_expected, (
        f"{name} m={m}: D={D} != ground truth {D_expected} at C={C} -- "
        f"integrity failure, STOP")
    c_list = credit_letters_for_row(credit_fn, m)

    chains_by_delta = {}
    for delta in [0, 1, 2]:
        d_target = best_d - delta
        if d_target < 0:
            chains_by_delta[delta] = set()
            continue
        seqs = distinct_optimal_a_sequences(letters, history, m, C, modulus,
                                             d_target, target_r=1)
        # cross-check: every seq's OWN max partial sum equals D+delta exactly
        for s in seqs:
            mps = exact_max_partial_sum(s, c_list)
            assert mps == D + delta, (
                f"{name} m={m}: chain {s} claimed at delta={delta} but its "
                f"own max partial sum is {mps} (expected {D+delta}) -- "
                f"terminal-depth identity violated, STOP")
        chains_by_delta[delta] = seqs

    return D, chains_by_delta, c_list


def main():
    all_tax_rows = []
    all_min_tax_a1 = []
    shape_histogram = {}  # (delta, shape_label) -> count

    for fam, credit_fn, gt in [("golden", credit_golden_per8, GT_GOLDEN),
                                ("sqrt2", credit_sqrt2_per12, GT_SQRT2)]:
        print(f"\n=== {fam}-per{'8' if fam=='golden' else '12'} (m<=8) ===")
        for m in sorted(k for k in gt if k <= 8):
            D_expected = gt[m]
            C = 12
            t0 = time.time()
            D, chains_by_delta, c_list = census_row(fam, credit_fn, m, D_expected, C)
            dt = time.time() - t0

            loop_seq = tuple([2] * m)
            n0, n1, n2 = (len(chains_by_delta[0]), len(chains_by_delta[1]),
                           len(chains_by_delta[2]))
            print(f"  m={m} D={D} ({dt:.2f}s): |delta=0|={n0} |delta=1|={n1} "
                  f"|delta=2|={n2}")

            min_tax_a1 = None
            for delta in [0, 1, 2]:
                for seq in chains_by_delta[delta]:
                    has_a1 = 1 in seq
                    shape = excursion_shape_label(seq)
                    is_loop = (seq == loop_seq)
                    key = (fam, delta, shape)
                    shape_histogram[key] = shape_histogram.get(key, 0) + 1
                    all_tax_rows.append({
                        "family": fam, "m": m, "D": D, "delta_tax": delta,
                        "a_sequence": " ".join(map(str, seq)),
                        "is_loop": is_loop, "has_a1": has_a1,
                        "excursion_shape": str(shape),
                    })
                    if has_a1 and (min_tax_a1 is None or delta < min_tax_a1):
                        min_tax_a1 = delta

            print(f"    min tax over any a=1-containing chain (within "
                  f"delta<=2 scope): {min_tax_a1 if min_tax_a1 is not None else 'NONE FOUND (scope wall: no a=1 chain within +2)'}")
            all_min_tax_a1.append({
                "family": fam, "m": m, "D": D,
                "min_tax_a1_within_scope": min_tax_a1,
            })

    print("\n\n=== TAX HISTOGRAM BY EXCURSION SHAPE (family, delta, shape) -> count ===")
    for (fam, delta, shape), count in sorted(shape_histogram.items(),
                                              key=lambda kv: (kv[0][0], kv[0][1])):
        print(f"  {fam} delta=+{delta} shape={shape}: {count}")

    print("\n=== FROZEN PREDICTION: IF F1 shows loop unique at D (IT DOES -- "
          "24/24 rows m=2..13 both families, f1_summary.csv), min tax of "
          "any a=1-containing chain = +1 exactly, for every row (60%) ===")
    n_rows = len(all_min_tax_a1)
    n_hit = 0
    n_no_a1_in_scope = 0
    for r in all_min_tax_a1:
        mt = r["min_tax_a1_within_scope"]
        if mt is None:
            n_no_a1_in_scope += 1
            print(f"  {r['family']} m={r['m']}: NO a=1-containing chain found "
                  f"within delta<=2 scope -- cannot evaluate prediction for "
                  f"this row (scope wall, not a miss).")
        elif mt == 1:
            n_hit += 1
            print(f"  {r['family']} m={r['m']}: min_tax_a1={mt} -- matches "
                  f"prediction exactly.")
        else:
            print(f"  {r['family']} m={r['m']}: min_tax_a1={mt} -- prediction "
                  f"said exactly 1, got {mt}.")
    n_evaluable = n_rows - n_no_a1_in_scope
    print(f"\n  Evaluable rows: {n_evaluable}/{n_rows} ({n_no_a1_in_scope} hit "
          f"the delta<=2 scope wall with no a=1 chain found at all).")
    if n_evaluable == 0:
        print("  VERDICT: INCONCLUSIVE -- no row had an a=1-containing chain "
              "within the delta<=2 scope to test the prediction against.")
    elif n_hit == n_evaluable:
        print(f"  VERDICT: HIT -- min tax is exactly +1 on all {n_hit} "
              f"evaluable rows.")
    else:
        print(f"  VERDICT: MISS -- min tax is +1 on only {n_hit}/{n_evaluable} "
              f"evaluable rows.")

    with open(HERE / "f2_tax_table.csv", "w", newline="") as f:
        fieldnames = ["family", "m", "D", "delta_tax", "a_sequence", "is_loop",
                      "has_a1", "excursion_shape"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in all_tax_rows:
            w.writerow(r)

    with open(HERE / "f2_min_tax_a1.csv", "w", newline="") as f:
        fieldnames = ["family", "m", "D", "min_tax_a1_within_scope"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in all_min_tax_a1:
            w.writerow(r)

    with open(HERE / "f2_shape_histogram.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["family", "delta_tax", "excursion_shape", "count"])
        for (fam, delta, shape), count in sorted(shape_histogram.items(),
                                                   key=lambda kv: (kv[0][0], kv[0][1])):
            w.writerow([fam, delta, str(shape), count])

    print(f"\nWrote f2_tax_table.csv ({len(all_tax_rows)} rows), "
          f"f2_min_tax_a1.csv ({len(all_min_tax_a1)} rows), "
          f"f2_shape_histogram.csv ({len(shape_histogram)} rows)")


if __name__ == "__main__":
    main()
