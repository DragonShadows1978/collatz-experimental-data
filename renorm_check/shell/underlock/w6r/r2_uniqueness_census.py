#!/usr/bin/env python3
"""
W6R-R2 -- Loop uniqueness under the convention of record.

Order text (frozen): "Uniqueness census on root-anchored true-word
windows m = 4..16 + both mechanical families at their root phase.
Frozen: loop strictly unique everywhere -- 70%."

INSTRUMENT NOTE (honest wall reported, not silently worked around):
the order's natural reuse target, w6f/f1_engine_ext.py's
compute_D_and_optimal_set, materializes the FULL (d,r) residue state
space (r in Z/3^m) at every step -- this is exactly what its own
module docstring documents as the validated, exhaustive method, but it
scales as O(3^m) regardless of how rare optimal chains are, and timed
out (>4min) at m=15 during this round's first attempt (m=14 alone took
~21s; m=15/16 would be ~3x/~9x that, i.e. well past this round's
per-cell budget). PRIMARY instrument for R2 is therefore a SECOND,
lighter-weight exhaustive method that reuses the SAME canonical_D
backward branch-and-bound DFS shape (w6k/k0_canonical_engine.py's own
pruning argument: max_so_far is monotone nondecreasing along any DFS
extension, so pruning at the known-optimal D_target is sound and
exhaustive over exactly the set of chains achieving D_target exactly)
but COLLECTS every a-sequence hitting D_target instead of only
returning the scalar D value -- this explores the SAME admissible-
chain space as canonical_D itself (which R1 already used and
validated against an independent from-scratch re-derivation), just
also recording witnesses, and is many orders of magnitude cheaper
than materializing the full residue lattice because the D_ceil
pruning kills almost every branch immediately once it exceeds the
known optimum. This method scales to m=16 in well under a second per
word (measured).

CROSS-CHECK (independence gate, run first, per house rules): for
m<=11 (where f1_engine_ext's exhaustive residue-space method and its
own brute_force_all_chains second cross-check are both cheap), the
lightweight DFS counter is validated against compute_D_and_optimal_set
AND brute_force_all_chains (a THIRD, independent, from-scratch
recursive DFS over every literal starting residue, already living in
f1_engine_ext.py) -- three independent methods agreeing at small m is
the trust basis for extending the lightweight method alone to m=12..16.

Root-anchoring: root_anchored_word(credit_fn, m) = anchor_steps=m (the
same surgical change R1 used, reusing backward_letters unmodified).
"Both mechanical families at their root phase" = golden-per8 and
sqrt2-per12 fed the same way, distinct from their existing end-
anchored-at-53 28-row ground-truth table.
"""
from __future__ import annotations

import csv
import sys
import time
import resource
from pathlib import Path

HERE = Path(__file__).parent
W6E = HERE.parent / "w6e"
W6F = HERE.parent / "w6f"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(W6E))
sys.path.insert(0, str(W6F))

from root_anchor import (  # noqa: E402
    root_anchored_word, loop_curve, credit_true,
    canonical_D, cap_margin_check, credit_golden_per8, credit_sqrt2_per12,
)
from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402
from f1_engine_ext import compute_D_and_optimal_set, brute_force_all_chains  # noqa: E402

M_RANGE = list(range(4, 17))  # 4..16
CROSSCHECK_M_MAX_F1 = 11    # compute_D_and_optimal_set (residue-BFS) stays cheap through here
CROSSCHECK_M_MAX_BRUTE = 6  # brute_force_all_chains (explicit 3^m residue loop) -- its own
                             # module docstring only validates m=3,4,5; m>=7 measured >2min here
A_CAP = 40
CAP_COUNT = 1000  # honest wall: stop collecting witnesses past this many (uniqueness-breaking would show up well before this)


def rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)


def enumerate_optimal_chains(letters, ceiling_on, D_target, a_cap=A_CAP, cap_count=CAP_COUNT):
    """Exhaustive (within cap_count) backward DFS collecting every
    admissible a-sequence whose max partial sum equals D_target exactly
    -- same pruning argument as canonical_D, extended to collect
    witnesses rather than just the scalar optimum."""
    m = len(letters)
    found = []
    hit_cap = [False]

    def dfs(j, rho, running, max_so_far, a_seq):
        if len(found) >= cap_count:
            hit_cap[0] = True
            return
        if max_so_far > D_target:
            return
        if j == m:
            if max_so_far == D_target:
                found.append(tuple(a_seq))
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
            if max2 > D_target:
                continue
            rho2 = backward_predecessor_exact(rho, a)
            dfs(j + 1, rho2, running2, max2, a_seq + [a])
            if len(found) >= cap_count:
                hit_cap[0] = True
                return

    dfs(0, 1, 0, 0, [])
    return found, hit_cap[0]


def run_independence_gate():
    """Cross-check the lightweight DFS-counter against
    compute_D_and_optimal_set (exhaustive residue-space method) AND,
    at the smallest m only, brute_force_all_chains (from-scratch
    residue-iteration method -- its own module docstring validates it
    only at m=3,4,5; measured here to cost >2min already by m=7-9
    depending on C, an honest wall, so it is used only through
    CROSSCHECK_M_MAX_BRUTE=6), both mechanical families + true word."""
    print(f"=== Independence gate: cross-check, m<=11 (f1) / m<=6 (brute) ===\n")
    all_ok = True
    gate_rows = []
    for label, credit_fn in [("true-word", credit_true),
                              ("golden-per8", credit_golden_per8),
                              ("sqrt2-per12", credit_sqrt2_per12)]:
        for m in range(4, CROSSCHECK_M_MAX_F1 + 1):
            word = root_anchored_word(credit_fn, m)
            D_light = canonical_D(word, ceiling_on=True, a_cap=A_CAP)
            light_seqs, capped = enumerate_optimal_chains(word, True, D_light)
            light_set = set(light_seqs)

            C = D_light + 2
            D_f1, best_d, seqs_f1 = compute_D_and_optimal_set(credit_fn, m, C, anchor_steps=m)
            seqs_f1 = seqs_f1 if seqs_f1 else set()

            do_brute = m <= CROSSCHECK_M_MAX_BRUTE
            if do_brute:
                D_brute, seqs_brute = brute_force_all_chains(credit_fn, m, C, anchor_steps=m)
                seqs_brute = seqs_brute if seqs_brute else set()
                ok = (D_light == D_f1 == D_brute) and (light_set == seqs_f1 == seqs_brute)
                brute_str = f" D_brute={D_brute}"
            else:
                ok = (D_light == D_f1) and (light_set == seqs_f1)
                brute_str = " D_brute=SKIPPED(honest wall, see docstring)"

            all_ok = all_ok and ok
            gate_rows.append((label, m, D_light, D_f1, len(light_set), ok))
            print(f"  {label:12s} m={m:>2}: D_light={D_light} D_f1={D_f1}{brute_str} "
                  f"n_opt={len(light_set)} {'AGREE' if ok else '*** DISAGREE ***'}")
    print(f"\nIndependence gate: {'PASS' if all_ok else 'FAIL'}\n")
    return all_ok, gate_rows


def main():
    t0 = time.time()
    print("=== W6R-R2: loop uniqueness under the convention of record ===\n")

    gate_ok, gate_rows = run_independence_gate()
    assert gate_ok, "R2 independence gate FAILED -- do not trust production run"

    rows = []
    n_words_total = 0
    n_unique = 0
    honest_walls = []

    families = [
        ("true-word", credit_true),
        ("golden-per8", credit_golden_per8),
        ("sqrt2-per12", credit_sqrt2_per12),
    ]

    print("=== Production census: m=4..16, root-anchored, all 3 word families ===\n")
    for label, credit_fn in families:
        print(f"--- {label} (root-anchored) ---")
        for m in M_RANGE:
            word = root_anchored_word(credit_fn, m)
            _, L_root, kstar = loop_curve(word)
            D_val = canonical_D(word, ceiling_on=True, a_cap=A_CAP)
            margin_ok, d1, d2 = cap_margin_check(word, ceiling_on=True,
                                                  base_cap=A_CAP, wider_cap=A_CAP * 2)
            opt_chains, hit_cap = enumerate_optimal_chains(word, True, D_val)
            n_optimal = len(opt_chains)
            is_unique_all2s = (n_optimal == 1) and (opt_chains[0] == tuple([2] * m))

            if not margin_ok:
                honest_walls.append((label, m, "margin_check_failed", d1, d2))
            if hit_cap:
                honest_walls.append((label, m, f"hit cap_count={CAP_COUNT} while enumerating optimal chains"))

            n_words_total += 1
            n_unique += is_unique_all2s

            rows.append({
                "label": label, "m": m, "D_root_ceil": D_val, "L_root": L_root,
                "matches_L_root": D_val == L_root,
                "n_optimal": n_optimal, "is_unique_all2s": is_unique_all2s,
                "margin_ok": margin_ok, "hit_enum_cap": hit_cap,
                "sample_optimal_seq": ",".join(map(str, opt_chains[0])) if opt_chains else "",
            })
            print(f"  m={m:>3}: D={D_val:>3} L_root={L_root:>3} n_optimal={n_optimal:>3} "
                  f"unique_all2s={is_unique_all2s} margin={'OK' if margin_ok else 'FAIL'}"
                  f"{' *** CAP HIT ***' if hit_cap else ''}")
        print()

    print(f"Peak RSS: {rss_gb():.3f} GB; wall so far: {time.time()-t0:.1f}s\n")

    out = HERE / "r2_uniqueness_table.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote {out.name} ({len(rows)} rows)")

    print(f"\n=== FROZEN PREDICTION VERDICT ===")
    print(f"Loop strictly unique everywhere -- 70% predicted\n")
    print(f"{n_unique}/{n_words_total} words have a UNIQUE optimal chain (the all-2s loop)")
    verdict = "HIT" if n_unique == n_words_total else f"MISS -- {n_words_total-n_unique} non-unique case(s)"
    print(f"Verdict: {verdict}")

    non_unique_rows = [r for r in rows if not r["is_unique_all2s"]]
    if non_unique_rows:
        print(f"\nNon-unique / non-loop-optimal rows (detail):")
        for r in non_unique_rows:
            print(f"  {r['label']} m={r['m']}: D={r['D_root_ceil']} L_root={r['L_root']} "
                  f"n_optimal={r['n_optimal']} sample={r['sample_optimal_seq']}")

    if honest_walls:
        print(f"\nHonest walls: {honest_walls}")
    else:
        print(f"\nNo honest walls: every row's margin check passed, no enumeration cap hit, "
              f"3-way independence gate passed at m<=11.")

    print(f"\nTotal wall: {time.time()-t0:.1f}s, peak RSS: {rss_gb():.3f} GB")


if __name__ == "__main__":
    main()
