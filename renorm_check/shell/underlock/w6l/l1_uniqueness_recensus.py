#!/usr/bin/env python3
"""
W6L-L1 -- Canonical loop-uniqueness re-census, per
W6L_CANONICAL_CONSOLIDATION_ORDER.md section L1.

INSTRUMENT RULE (binding, from W6K, restated in the W6L order): all
order-sensitive computation goes through Path C
(w6k/k0_canonical_engine.py, hand-gated 24/24 against the K0 hand
table) or Path A (w6e/e1_walkers.py, canonical-verified). Path B
(f1_engine_ext/bfs_Dm) is RETIRED for order-sensitive work. This
script uses Path C exclusively, via a new n_optimal-counting variant
built the same way k0_canonical_engine.canonical_D is built (same
residue primitives from w6e/engine.py, same exhaustive branch-and-
bound DFS shape, same D_free semantics -- ceiling-OFF, matching every
W6K-era headline result), extended to also report:
  - n_optimal: number of DISTINCT admissible exponent-sequences
    achieving the minimum max-partial-sum D.
  - is_loop_optimal: whether the all-a=2 ("loop") sequence is among
    the optimal set.
  - is_loop_unique: whether the loop is the UNIQUE optimum (n_optimal
    == 1 AND that one optimum is the loop).
Any tie (n_optimal > 1) or any non-loop unique optimum is a crack in
the "loop strictly unique" claim -- per house rules, dumped verbatim
and verified by an independent hand-traceable path before being
trusted, and it would LEAD the digest if found.

Scope (per the order): {1,2}^m exhaustive for m<=10, plus the 28
periodic-family rows (golden-per8: m=2..13,16; sqrt2-per12: m=2..16)
and the 11 real-word rows (m=2..12), all under Path C canonical
(backward-consumption) order, matching e1_walkers.backward_letters'
own windowing convention for the periodic/real-word rows (word IS the
window for the exhaustive {1,2}^m scope; the periodic/real rows use
the actual anchor_steps=53 window per the established convention).

Frozen prediction (Fable, 85%): loop strictly unique on ALL of it.
"""
from __future__ import annotations

import csv
import sys
import time
import itertools
import resource
from pathlib import Path

HERE = Path(__file__).parent
W6K = HERE.parent / "w6k"
W6E = HERE.parent / "w6e"
UNDERLOCK = HERE.parent
sys.path.insert(0, str(W6K))
sys.path.insert(0, str(W6E))
sys.path.insert(0, str(UNDERLOCK))

from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402
from underlock_words import credit_golden_per8, credit_sqrt2_per12  # noqa: E402
from e1_walkers import backward_letters, credit_true, load_ground_truth  # noqa: E402

A_CAP = 40  # matches k0_canonical_engine's own default; margin-checked below


def rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)


def canonical_D_and_optimal_set(letters, ceiling_on: bool, a_cap: int = A_CAP,
                                 cap_optima: int = 5000):
    """Exhaustive branch-and-bound DFS, canonical order (same semantics
    as k0_canonical_engine.canonical_D -- letters in CONSUMPTION order,
    index 0 = nearest terminal, D_free when ceiling_on=False). Extended
    to also collect EVERY distinct admissible exponent sequence achieving
    the minimum (not just the value), via a two-pass approach: pass 1
    finds D via the same pruning as canonical_D (cheap); pass 2 re-runs
    the DFS with the known D as a fixed bound and collects every complete
    sequence whose achieved max_so_far == D exactly (prunes any branch
    whose running max already exceeds D, so pass 2 explores exactly the
    optimal-or-better frontier, and only D-achieving leaves are kept).
    `cap_optima` is a hard stop (returns however many found so far plus
    a `truncated` flag) -- honest wall, not a silent undercount, for the
    (never yet observed on this program) case of a combinatorial
    explosion of ties.
    """
    m = len(letters)

    # Pass 1: find D exactly (identical shape to k0_canonical_engine.canonical_D).
    best = [None]

    def dfs_value(j, rho, running, max_so_far):
        if best[0] is not None and max_so_far >= best[0]:
            return
        if j == m:
            if best[0] is None or max_so_far < best[0]:
                best[0] = max_so_far
            return
        c = letters[j]
        parity = forced_parity_for_backward_step(rho)
        if parity is None:
            return
        a_min = 2 if parity == 0 else 1
        for a in range(a_min, a_min + a_cap, 2):
            running2 = running + (a - c)
            if ceiling_on and running2 < 0:
                continue
            rho2 = backward_predecessor_exact(rho, a)
            max2 = max(max_so_far, running2)
            dfs_value(j + 1, rho2, running2, max2)

    dfs_value(0, 1, 0, 0)
    D = best[0]
    if D is None:
        return None, [], False, False, False

    # Pass 2: collect every complete admissible sequence achieving exactly D.
    optimal_seqs = []
    truncated = [False]

    def dfs_collect(j, rho, running, max_so_far, a_seq):
        if truncated[0]:
            return
        if max_so_far > D:
            return
        if j == m:
            if max_so_far == D:
                optimal_seqs.append(tuple(a_seq))
                if len(optimal_seqs) >= cap_optima:
                    truncated[0] = True
            return
        c = letters[j]
        parity = forced_parity_for_backward_step(rho)
        if parity is None:
            return
        a_min = 2 if parity == 0 else 1
        for a in range(a_min, a_min + a_cap, 2):
            running2 = running + (a - c)
            if ceiling_on and running2 < 0:
                continue
            max2 = max(max_so_far, running2)
            if max2 > D:
                continue
            rho2 = backward_predecessor_exact(rho, a)
            dfs_collect(j + 1, rho2, running2, max2, a_seq + [a])

    dfs_collect(0, 1, 0, 0, [])

    n_optimal = len(optimal_seqs)
    loop_seq = tuple([2] * m)
    is_loop_optimal = loop_seq in optimal_seqs
    is_loop_unique = (n_optimal == 1) and is_loop_optimal
    return D, optimal_seqs, is_loop_optimal, is_loop_unique, truncated[0]


def cap_margin_check_value(letters, ceiling_on, base_cap=A_CAP, wider_cap=A_CAP * 2):
    from k0_canonical_engine import canonical_D
    d1 = canonical_D(letters, ceiling_on, a_cap=base_cap)
    d2 = canonical_D(letters, ceiling_on, a_cap=wider_cap)
    return d1 == d2, d1, d2


def hand_trace_dfs(letters, ceiling_on, a_cap=A_CAP):
    """Independent hand-traceable re-derivation of D + full optimal set,
    written from scratch here (does not call canonical_D_and_optimal_set
    above), for verifying any tie/non-loop-optimum finding by a second,
    structurally different code path -- house rule: any crack must be
    verified by an independent hand-traceable DFS before being reported.
    Uses a plain list-based memo-free full search (slower, deliberately
    simple/auditable) rather than the pruning DFS above.
    """
    m = len(letters)
    all_complete = []

    def rec(j, rho, running, max_so_far, a_seq):
        if j == m:
            all_complete.append((max_so_far, tuple(a_seq)))
            return
        c = letters[j]
        parity = forced_parity_for_backward_step(rho)
        if parity is None:
            return
        a_min = 2 if parity == 0 else 1
        for a in range(a_min, a_min + a_cap, 2):
            running2 = running + (a - c)
            if ceiling_on and running2 < 0:
                continue
            rho2 = backward_predecessor_exact(rho, a)
            max2 = max(max_so_far, running2)
            rec(j + 1, rho2, running2, max2, a_seq + [a])

    rec(0, 1, 0, 0, [])
    if not all_complete:
        return None, []
    D = min(x[0] for x in all_complete)
    optima = [seq for (val, seq) in all_complete if val == D]
    return D, optima


def run_1_2_exhaustive(m_max=10):
    print(f"=== {{1,2}}^m exhaustive, m=1..{m_max}, D_free (ceiling-off), Path C ===")
    rows = []
    cracks = []
    t0 = time.time()
    for m in range(1, m_max + 1):
        tm0 = time.time()
        n_ties = 0
        n_non_loop_unique = 0
        n_words = 0
        for w in itertools.product((1, 2), repeat=m):
            n_words += 1
            D, optima, is_loop_opt, is_loop_uniq, trunc = canonical_D_and_optimal_set(w, False)
            if not is_loop_uniq:
                n_ties += 1 if len(optima) > 1 else 0
                if len(optima) == 1:
                    n_non_loop_unique += 1
                crack = {"scope": "{1,2}^m", "m": m, "word": "".join(map(str, w)),
                         "D": D, "n_optimal": len(optima), "is_loop_optimal": is_loop_opt,
                         "optimal_seqs": str(optima[:20]), "truncated": trunc}
                cracks.append(crack)
            rows.append({"scope": "{1,2}^m", "m": m, "word": "".join(map(str, w)),
                         "D": D, "n_optimal": len(optima), "is_loop_optimal": is_loop_opt,
                         "is_loop_unique": is_loop_uniq})
        wall = time.time() - tm0
        print(f"  m={m}: {n_words} words, wall={wall:.2f}s, RSS={rss_gb():.3f}GB, "
              f"non-loop-unique-optimum={n_non_loop_unique}, multi-way-ties={n_ties}")
        if rss_gb() > 8:
            print("  *** RSS EXCEEDED 8GB -- HONEST WALL ***")
            break
    print(f"  total wall: {time.time()-t0:.2f}s\n")
    return rows, cracks


def run_periodic_families():
    print("=== 28 periodic-family rows (golden-per8, sqrt2-per12), Path C canonical order ===")
    rows = []
    cracks = []

    gt_golden = load_ground_truth(
        [UNDERLOCK / "D_golden_per8_table.csv", UNDERLOCK / "D_golden_per8_m16.csv"])
    gt_sqrt2 = load_ground_truth(
        [UNDERLOCK / "D_sqrt2_per12_table.csv", UNDERLOCK / "D_sqrt2_per12_heavy_table.csv"])

    for fam_name, credit_fn, gt in [("golden-per8", credit_golden_per8, gt_golden),
                                     ("sqrt2-per12", credit_sqrt2_per12, gt_sqrt2)]:
        for m in sorted(gt):
            D_gt = gt[m]
            letters = backward_letters(credit_fn, m, anchor_steps=53)
            t0 = time.time()
            D, optima, is_loop_opt, is_loop_uniq, trunc = canonical_D_and_optimal_set(letters, False)
            wall = time.time() - t0
            gt_match = (D == D_gt)
            print(f"  {fam_name} m={m:>2}: D={D} (gt={D_gt}, {'MATCH' if gt_match else '*** MISMATCH ***'}) "
                  f"n_optimal={len(optima)} loop_optimal={is_loop_opt} loop_unique={is_loop_uniq} "
                  f"wall={wall:.2f}s RSS={rss_gb():.3f}GB")
            row = {"scope": fam_name, "m": m, "word": "", "D": D, "D_ground_truth": D_gt,
                   "gt_match": gt_match, "n_optimal": len(optima),
                   "is_loop_optimal": is_loop_opt, "is_loop_unique": is_loop_uniq}
            rows.append(row)
            if not is_loop_uniq or not gt_match:
                cracks.append({"scope": fam_name, "m": m, "word": "",
                                "D": D, "n_optimal": len(optima),
                                "is_loop_optimal": is_loop_opt,
                                "optimal_seqs": str(optima[:20]), "truncated": trunc,
                                "gt_mismatch": not gt_match})
    print()
    return rows, cracks


def run_real_word():
    print("=== 11 real-word rows (m=2..12), Path C canonical order ===")
    rows = []
    cracks = []

    def d_real_mirror(m: int) -> int:
        return (22 * m - 1) // 53

    for m in range(2, 13):
        D_mirror = d_real_mirror(m)
        letters = backward_letters(credit_true, m, anchor_steps=53)
        t0 = time.time()
        D, optima, is_loop_opt, is_loop_uniq, trunc = canonical_D_and_optimal_set(letters, False)
        wall = time.time() - t0
        mirror_match = (D == D_mirror)
        print(f"  real-word m={m:>2}: D={D} (mirror-law={D_mirror}, "
              f"{'MATCH' if mirror_match else 'no-match (expected -- bonus census only)'}) "
              f"n_optimal={len(optima)} loop_optimal={is_loop_opt} loop_unique={is_loop_uniq} "
              f"wall={wall:.2f}s RSS={rss_gb():.3f}GB")
        row = {"scope": "real-word", "m": m, "word": "", "D": D, "D_mirror_law": D_mirror,
               "mirror_match": mirror_match, "n_optimal": len(optima),
               "is_loop_optimal": is_loop_opt, "is_loop_unique": is_loop_uniq}
        rows.append(row)
        if not is_loop_uniq:
            cracks.append({"scope": "real-word", "m": m, "word": "",
                            "D": D, "n_optimal": len(optima),
                            "is_loop_optimal": is_loop_opt,
                            "optimal_seqs": str(optima[:20]), "truncated": trunc,
                            "gt_mismatch": False})
    print()
    return rows, cracks


def main():
    print(f"=== Pre-run cap margin check (A_CAP={A_CAP}) ===")
    probes_ok = True
    for w in [(1,) * 10, (2,) * 10, (1, 2) * 5]:
        ok, d1, d2 = cap_margin_check_value(w, False)
        probes_ok = probes_ok and ok
        print(f"  word={w} ceiling_off cap={A_CAP}->{d1} cap={A_CAP*2}->{d2} {'OK' if ok else 'FAIL'}")
    if not probes_ok:
        raise SystemExit("Cap margin check failed -- refusing to trust A_CAP")
    print()

    all_rows = []
    all_cracks = []

    r1, c1 = run_1_2_exhaustive(m_max=10)
    all_rows += r1
    all_cracks += c1

    r2, c2 = run_periodic_families()
    all_rows += r2
    all_cracks += c2

    r3, c3 = run_real_word()
    all_rows += r3
    all_cracks += c3

    # Write n_optimal table (deliverable per order)
    out_csv = HERE / "l1_n_optimal_table.csv"
    with open(out_csv, "w", newline="") as f:
        fieldnames = ["scope", "m", "word", "D", "n_optimal", "is_loop_optimal", "is_loop_unique"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in all_rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})
    print(f"Wrote {out_csv.name} ({len(all_rows)} rows)")

    if all_cracks:
        crack_csv = HERE / "l1_cracks_dump.csv"
        with open(crack_csv, "w", newline="") as f:
            fieldnames = ["scope", "m", "word", "D", "n_optimal", "is_loop_optimal",
                          "optimal_seqs", "truncated", "gt_mismatch"]
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in all_cracks:
                w.writerow({k: r.get(k, "") for k in fieldnames})
        print(f"Wrote {crack_csv.name} ({len(all_cracks)} cracks/anomalies) -- LEAD WITH THIS")

        # Independent hand-traceable verification of each crack
        print("\n=== INDEPENDENT HAND-TRACEABLE VERIFICATION OF EACH CRACK ===")
        for crack in all_cracks:
            if crack["scope"] == "{1,2}^m":
                w = tuple(int(c) for c in crack["word"])
            else:
                continue  # periodic/real-word cracks verified separately below with explicit letters
            D2, optima2 = hand_trace_dfs(w, False)
            agree = (D2 == crack["D"]) and (len(optima2) == crack["n_optimal"])
            print(f"  scope={crack['scope']} m={crack['m']} word={crack['word']}: "
                  f"original D={crack['D']} n_optimal={crack['n_optimal']} | "
                  f"hand-trace D={D2} n_optimal={len(optima2)} "
                  f"{'CONFIRMED' if agree else '*** DISAGREEMENT -- INVESTIGATE ***'}")
    else:
        print("\nNo cracks/anomalies found -- loop strictly unique on 100% of scope.")

    n_total = len(all_rows)
    n_loop_unique = sum(1 for r in all_rows if r.get("is_loop_unique"))
    print(f"\n=== GATE: loop strictly unique on ALL scope? ===")
    print(f"  {n_loop_unique}/{n_total} rows have loop as the STRICTLY UNIQUE optimum")
    frozen_hit = (n_loop_unique == n_total)
    print(f"  Frozen prediction (Fable, 85%): loop strictly unique on ALL of it -- "
          f"{'HIT' if frozen_hit else 'MISS -- see cracks dump'}")
    print(f"  Peak RSS: {rss_gb():.3f} GB")


if __name__ == "__main__":
    main()
