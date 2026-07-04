#!/usr/bin/env python3
"""
W6L-L2 (CORE) -- Per-trit tax decomposition, per
W6L_CANONICAL_CONSOLIDATION_ORDER.md section L2.

RELAUNCH NOTE (honest record): a first draft of this script ran the
dict DP directly at mod 3^14/len 14/cap 200 -- pure-Python state
space ~81x K2's, killed by its own 280s timeout with zero output
(exit 124). This restructured version separates:
  CORE (this script, dict DP, minutes): K2-exact-replica run
    (mod 3^10, len 10, cap 150 -- the certified instrument at its
    certified parameters) for the argmin catalogs, increments,
    plateau test; PLUS a length-extension check (len 14 at mod 3^10)
    -- K2's own argmin lengths reach 9 with a len-10 wall, so the
    certified curve had an unexamined length-boundary risk; this
    closes it cheaply.
  EXTENSION (l2b_extension.py, vectorized, gated): t=11..14 curve.

INSTRUMENT: w6k/k2_precision_cost_curve_redo.py's shared_layered_dp +
validation, imported verbatim (K0/K2-gated: reproduces H1's published
t=10 answer exactly; nesting assertion structural). This DP consumes
NO word letters -- it enumerates all admissible exponent processes
from the fixed terminal rho=1 -- so the W6K direction seam cannot
apply to it (nothing exists to consume in the wrong order); it is not
Path B and was never retired.

Catalog semantics (exact, per the order's "ALL argmin excursions ...
from K2's corrected DP"): the DP keeps ONE min-cost parent per
(depth, high-precision residue) state -- within-state equal-cost
path ties are collapsed by its `<` update rule. "ALL argmins"
therefore means: all (depth, terminal high-precision residue) pairs
achieving the global min for each t, each with its DP witness chain.
That is everything K2's corrected DP defines; stated, not hidden.

Frozen predictions (Fable):
  (a) plateau shapes are literally identical chains serving both t
      values -- 70%.
  (b) every jump t->t+1 coincides with minimum excursion LENGTH
      increasing -- 55%.
  (c) t=11..14 continues at ~2.5-3/trit with width<=2 plateaus --
      60% (evaluated in l2b_extension.py).
"""
from __future__ import annotations

import csv
import sys
import time
import resource
from pathlib import Path

HERE = Path(__file__).parent
W6K = HERE.parent / "w6k"
W6E = HERE.parent / "w6e"
sys.path.insert(0, str(W6K))
sys.path.insert(0, str(W6E))

from k2_precision_cost_curve_redo import (  # noqa: E402
    validate_against_exact, shared_layered_dp,
)

K2_CERTIFIED_CURVE = [1, 2, 5, 5, 7, 7, 15, 19, 22, 27]  # t=1..10, k2_precision_cost_curve.csv
MAX_T = 10
COST_CAP = 150   # K2's own
RSS_CAP_GB = 8.0


def rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)


def all_argmin_excursions(history, t: int, max_len: int):
    """ALL (depth, terminal residue) pairs achieving the GLOBAL min
    cost for return-precision t, with the DP's witness chain each --
    deliverable (i). Returns (min_cost, [(depth, a_seq, touched_early)])."""
    modt = 3 ** t
    best_cost = None
    per_depth_best = {}
    for d in range(1, max_len + 1):
        cands = [cost for rho, (cost, _, _) in history[d].items() if rho % modt == 1]
        if not cands:
            continue
        dcost = min(cands)
        per_depth_best[d] = dcost
        if best_cost is None or dcost < best_cost:
            best_cost = dcost
    if best_cost is None:
        return None, []
    catalog = []
    for d in range(1, max_len + 1):
        if per_depth_best.get(d) != best_cost:
            continue
        for rho, (cost, _, _) in history[d].items():
            if rho % modt == 1 and cost == best_cost:
                seq = []
                node = rho
                depth = d
                touched_early = False
                while depth > 0:
                    _, parent, a = history[depth][node]
                    seq.append(a)
                    node = parent
                    depth -= 1
                    if depth > 0 and node % modt == 1:
                        touched_early = True
                seq.reverse()
                catalog.append((d, tuple(seq), touched_early))
    return best_cost, catalog


def shape_class(a_seq):
    """Coarse shape descriptor: (length, n_exponents>2, max exponent,
    sum a). Used for the increment analysis's 'shape class' question."""
    return (len(a_seq), sum(1 for a in a_seq if a > 2), max(a_seq), sum(a_seq))


def main():
    high_mod = 3 ** MAX_T
    print(f"=== CORE run: K2-exact-replica (mod=3^{MAX_T}, len 10, cap {COST_CAP}) "
          f"+ length-extension check (len 14) ===")
    print("Pre-run validation (K2's own house checks):")
    for c in validate_against_exact(high_mod):
        print(" ", c)
    print("All validation checks PASS.\n")

    # --- Run 1: K2's exact parameters ---
    t0 = time.time()
    hist10 = shared_layered_dp(high_mod, 10, COST_CAP)
    print(f"K2-replica DP (len 10): {time.time()-t0:.2f}s, RSS={rss_gb():.3f}GB")

    curve10 = {}
    catalogs10 = {}
    for t in range(1, MAX_T + 1):
        cost, cat = all_argmin_excursions(hist10, t, 10)
        curve10[t] = cost
        catalogs10[t] = cat
    got = [curve10[t] for t in range(1, MAX_T + 1)]
    if got != K2_CERTIFIED_CURVE:
        raise SystemExit(f"STOP: K2-replica curve {got} != certified {K2_CERTIFIED_CURVE}")
    print(f"Gate: replica curve == K2 certified curve {K2_CERTIFIED_CURVE} -- PASS")
    h1_present = any(seq == (4, 3, 8, 3, 9, 8, 7, 1) for (_, seq, _) in catalogs10[10])
    print(f"Gate: H1's published t=10 chain present in catalog -- {'PASS' if h1_present else 'FAIL'}")
    if not h1_present:
        raise SystemExit("STOP: H1 chain missing from t=10 catalog")

    # --- Run 2: length-extension check (len 14, same modulus/cap) ---
    t0 = time.time()
    hist14 = shared_layered_dp(high_mod, 14, COST_CAP)
    print(f"\nLength-extension DP (len 14): {time.time()-t0:.2f}s, RSS={rss_gb():.3f}GB")
    if rss_gb() > RSS_CAP_GB:
        raise SystemExit(137)
    curve14 = {}
    catalogs14 = {}
    length_wall_findings = []
    for t in range(1, MAX_T + 1):
        cost, cat = all_argmin_excursions(hist14, t, 14)
        curve14[t] = cost
        catalogs14[t] = cat
        if cost != curve10[t]:
            length_wall_findings.append((t, curve10[t], cost))
    if length_wall_findings:
        print("*** LENGTH WALL FINDING: len-14 search LOWERS the certified curve at: "
              f"{length_wall_findings} (t, len10_cost, len14_cost) -- K2's curve was "
              f"length-limited; the len-14 values supersede for the tax law ***")
    else:
        print("Length-extension check: len-14 min costs IDENTICAL to len-10 on all t=1..10 "
              "-- K2's certified curve has no length wall (new negative result, banked).")

    # The catalog of record: len-14 run (superset search; identical costs unless wall found)
    curve = curve14
    catalogs = catalogs14

    # --- (i) Argmin catalog dump ---
    print("\n=== (i) ARGMIN CATALOG (all (depth, terminal-residue) argmins per t, len<=14) ===")
    catalog_rows = []
    for t in range(1, MAX_T + 1):
        cat = catalogs[t]
        lens = sorted(set(x[0] for x in cat))
        print(f"  t={t:>2}: min_cost={curve[t]}, n_argmin_states={len(cat)}, lengths={lens}")
        for (length, seq, touched) in sorted(cat):
            print(f"      len={length} a_seq={seq} touched_early={touched}")
            catalog_rows.append({"t": t, "min_cost": curve[t], "length": length,
                                  "a_seq": ",".join(map(str, seq)),
                                  "touched_target_early": touched})
    out_csv = HERE / "l2_argmin_catalog.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["t", "min_cost", "length", "a_seq", "touched_target_early"])
        w.writeheader()
        for r in catalog_rows:
            w.writerow(r)
    print(f"Wrote {out_csv.name} ({len(catalog_rows)} rows)")

    # --- (ii) Increment analysis ---
    print("\n=== (ii) INCREMENT ANALYSIS (t -> t+1: WHAT changed) ===")
    increment_rows = []
    for t in range(1, MAX_T):
        t1 = t + 1
        cost_t, cost_t1 = curve[t], curve[t1]
        jump = cost_t1 - cost_t
        cat_t, cat_t1 = catalogs[t], catalogs[t1]
        min_len_t = min(x[0] for x in cat_t)
        min_len_t1 = min(x[0] for x in cat_t1)
        seqs_t = set(x[1] for x in cat_t)
        seqs_t1 = set(x[1] for x in cat_t1)
        shared = seqs_t & seqs_t1
        classes_t = sorted(set(shape_class(s) for s in seqs_t))
        classes_t1 = sorted(set(shape_class(s) for s in seqs_t1))
        length_increased = min_len_t1 > min_len_t
        is_plateau = (jump == 0)
        print(f"  t={t}->{t1}: cost {cost_t}->{cost_t1} (jump {jump}"
              f"{', PLATEAU' if is_plateau else ''}) | min_len {min_len_t}->{min_len_t1} "
              f"(incr={length_increased}) | shared exact chains: {len(shared)} | "
              f"shape classes (len,n>2,max_a,sum_a): {classes_t} -> {classes_t1}")
        increment_rows.append({
            "t": t, "t_next": t1, "cost": cost_t, "cost_next": cost_t1, "jump": jump,
            "is_plateau": is_plateau, "min_len": min_len_t, "min_len_next": min_len_t1,
            "length_increased": length_increased, "n_shared_exact_chains": len(shared),
            "shape_classes_t": str(classes_t), "shape_classes_next": str(classes_t1),
        })
    out2 = HERE / "l2_increment_analysis.csv"
    with open(out2, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(increment_rows[0].keys()))
        w.writeheader()
        for r in increment_rows:
            w.writerow(r)
    print(f"Wrote {out2.name}")

    # --- (iii) Plateau hypothesis ---
    print("\n=== (iii) PLATEAU HYPOTHESIS (one chain serves both t values) ===")
    print("Note (structural): by precision nesting, any (t+1)-argmin at equal cost IS a "
          "t-argmin, so a shared chain EXISTS whenever cost(t)==cost(t+1). The empirical "
          "content measured here is the STRONGER identity: is the t-argmin SET equal to "
          "the (t+1)-argmin set (one shape owns both trits), or strictly larger?")
    plateau_rows = [r for r in increment_rows if r["is_plateau"]]
    verdicts = []
    for r in plateau_rows:
        t, t1 = r["t"], r["t_next"]
        seqs_t = set(x[1] for x in catalogs[t])
        seqs_t1 = set(x[1] for x in catalogs[t1])
        shared_exists = len(seqs_t & seqs_t1) > 0
        sets_identical = seqs_t == seqs_t1
        print(f"  plateau ({t},{t1}) cost={r['cost']}: n_argmins {len(seqs_t)} vs {len(seqs_t1)}; "
              f"shared chain exists: {shared_exists}; argmin SETS identical: {sets_identical}")
        verdicts.append((shared_exists, sets_identical))
    pred_a_hit = len(verdicts) > 0 and all(v[0] for v in verdicts)
    print(f"\nFrozen (a) [70%] plateau shapes literally identical chains serving both t: "
          f"{'HIT' if pred_a_hit else 'MISS'} "
          f"(shared-chain: {sum(1 for v in verdicts if v[0])}/{len(verdicts)}; "
          f"full set identity: {sum(1 for v in verdicts if v[1])}/{len(verdicts)})")

    # --- (b) jumps vs min-length increase ---
    print("\n=== Frozen (b) [55%]: every jump coincides with min excursion length increase ===")
    nonplateau = [r for r in increment_rows if not r["is_plateau"]]
    for r in nonplateau:
        print(f"  t={r['t']}->{r['t_next']} jump={r['jump']}: min_len {r['min_len']}->"
              f"{r['min_len_next']} increased={r['length_increased']}")
    n_incr = sum(1 for r in nonplateau if r["length_increased"])
    b_hit = n_incr == len(nonplateau)
    print(f"Verdict: {'HIT' if b_hit else 'MISS'} ({n_incr}/{len(nonplateau)} jumps with "
          f"min-length increase)")

    print(f"\nCurve of record (t=1..10, len<=14): {[curve[t] for t in range(1, 11)]}")
    print(f"Peak RSS: {rss_gb():.3f} GB")
    print("Prediction (c) t=11..14: deferred to l2b_extension.py (vectorized, gated).")


if __name__ == "__main__":
    main()
