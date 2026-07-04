#!/usr/bin/env python3
"""
W6M-M2 -- Congruence-class cost floors (the lemma's empirical form),
per W6M_GLOBAL_LEMMA_MAP_ORDER.md section M2.

INSTRUMENT RULE (binding): Path C semantics only (same exhaustive,
parity-forced backward DFS as k0_canonical_engine.canonical_D /
w6l/l1_uniqueness_recensus.canonical_D_and_optimal_set). Path B
retired, not used.

Scope: m=5..8, the two mechanical-family words (golden-per8,
sqrt2-per12, backward_letters at anchor_steps=53 -- same convention
as M1/L1/L3). For every admissible chain (parity-forced, D_free/
ceiling-off semantics) whose max partial sum stays within L+2:
compute its per-prefix residue r_k (EXACT integer, not modularly
reduced -- m<=8 so this is cheap and there is no truncation anywhere)
at every prefix k=1..m. "mod 3^min(k,6)" from the order is a precision
cap for reporting large-r values readably; since we track EXACT
integers throughout (never reduced), we report BOTH the exact r_k and
r_k mod 3^min(k,6) -- the group-by below uses the order's specified
truncated-at-depth-3 class trajectory (r_k mod 27 at each k, for
k=1..3, or fewer if m<3 -- not applicable here since m>=5).

GROUPING (order's own spec): group chains by the class trajectory
truncated at depth 3, i.e. the tuple (r_1 mod 27, r_2 mod 27, r_3 mod
27). Per group: min max-partial-sum (the cost floor for that
trajectory-class).

DEPARTURE TIME (the frozen prediction's operational object): the loop
chain (all a=2) has EXACT r_k == 1 at every prefix k (verified below,
closed form and by direct computation -- backward_predecessor_exact(1,2)
= (4*1-1)/3 = 1, a fixed point). "Departure prefix" for a given chain
= the first j in 1..m with r_j != 1 (exact integer inequality, the
sharpest possible reading -- no precision ambiguity: r_j is a genuine
integer here, never reduced mod anything internally). Chains that
NEVER depart (r_j == 1 for all j, i.e. the chain is a=2 throughout =
the loop itself) are excluded from the departure table (no departure
prefix exists) and reported separately.

Deliverable: the (departure prefix j -> min cost over ALL chains
departing exactly at j) table -- built from the SAME per-chain
enumeration as the depth-3-class grouping table (both are views of
the same underlying admissible-chain set), then cross-checked against
an INDEPENDENT second pass that recomputes the departure-floor table
purely from the materialized per-chain dump rows (structurally
separate scan, not the live dict built during enumeration) -- the two
must agree exactly.

Frozen prediction (Fable, 60%): floor(departure at prefix j) =
L + f(j), f >= 1 nonincreasing in j (leaving late is cheaper).

Every reported floor witness (the argmin chain achieving each group's
min) is exact-integer replayed independently (fresh from-scratch
recomputation of its residue trajectory and its max-partial-sum, not
reused from the DFS's own bookkeeping) before being trusted -- the
W6L lesson.
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
UNDERLOCK = HERE.parent
W6E = UNDERLOCK / "w6e"
sys.path.insert(0, str(UNDERLOCK))
sys.path.insert(0, str(W6E))

from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402
from underlock_words import credit_golden_per8, credit_sqrt2_per12  # noqa: E402
from e1_walkers import backward_letters  # noqa: E402

M_SCOPE = list(range(5, 9))  # 5..8
A_CAP = 40

MECH_WORDS = {
    "golden-per8": credit_golden_per8,
    "sqrt2-per12": credit_sqrt2_per12,
}


def loop_L(letters):
    running = 0
    best = 0
    for c in letters:
        running += (2 - c)
        best = max(best, running)
    return best


def enumerate_within_band(letters, band, a_cap):
    """Exhaustive DFS, canonical order, D_free semantics: every
    admissible a-sequence whose max partial sum stays <= band. Returns
    list of (a_seq, max_partial_sum, rho_curve) where rho_curve[k] is
    the EXACT integer residue after consuming prefix length k+1
    (0-indexed)."""
    m = len(letters)
    results = []

    def dfs(j, rho, running, max_so_far, a_seq, rho_hist):
        if max_so_far > band:
            return
        if j == m:
            results.append((tuple(a_seq), max_so_far, tuple(rho_hist)))
            return
        c = letters[j]
        parity = forced_parity_for_backward_step(rho)
        if parity is None:
            return
        a_min = 2 if parity == 0 else 1
        for a in range(a_min, a_min + a_cap, 2):
            running2 = running + (a - c)
            max2 = max(max_so_far, running2)
            if max2 > band:
                continue
            rho2 = backward_predecessor_exact(rho, a)
            dfs(j + 1, rho2, running2, max2, a_seq + [a], rho_hist + [rho2])

    dfs(0, 1, 0, 0, [], [])
    return results


def cap_margin_check(letters, band, base_cap, wider_cap):
    base = enumerate_within_band(letters, band, base_cap)
    wider = enumerate_within_band(letters, band, wider_cap)
    return len(base) == len(wider), len(base), len(wider)


def departure_prefix(rho_curve):
    """First j (1-indexed) with rho_curve[j-1] != 1, exact integer
    comparison. Returns None if the chain never departs (all-a=2, the
    loop itself)."""
    for idx, r in enumerate(rho_curve):
        if r != 1:
            return idx + 1
    return None


def independent_replay(letters, a_seq):
    """Fresh from-scratch recomputation of (max_partial_sum, rho_curve)
    for a given a_seq, structurally independent of the DFS's own
    running bookkeeping (separate function, separate loop, no shared
    state) -- the exact-replay discipline."""
    rho = 1
    running = 0
    max_so_far = 0
    rho_curve = []
    for c, a in zip(letters, a_seq):
        parity = forced_parity_for_backward_step(rho)
        assert parity is not None, "replay hit a class-0 dead end -- should be impossible"
        assert (a % 2 == 0) == (parity == 0), "replay parity mismatch -- engine bug"
        running += (a - c)
        max_so_far = max(max_so_far, running)
        rho = backward_predecessor_exact(rho, a)
        rho_curve.append(rho)
    return max_so_far, tuple(rho_curve)


def main():
    t0 = time.time()
    print("=== W6M-M2: congruence-class cost floors ===\n")

    assert backward_predecessor_exact(1, 2) == 1, "loop fixed-point check FAILED"
    print("Sanity: backward_predecessor_exact(1, 2) == 1 (loop is an exact fixed "
          "point of the backward map) -- CONFIRMED\n")

    all_group_rows = []
    all_departure_rows = []
    all_chain_dump = []
    cross_check_fails = 0
    replay_fails = 0

    for word_label, credit_fn in MECH_WORDS.items():
        for m in M_SCOPE:
            letters = backward_letters(credit_fn, m, anchor_steps=53)
            L = loop_L(letters)
            band = L + 2

            ok, n1, n2 = cap_margin_check(letters, band, A_CAP, A_CAP * 2)
            print(f"--- {word_label} m={m}: L={L}, band=L+2={band}, "
                  f"cap-margin {'OK' if ok else 'FAIL'} (cap40={n1}, cap80={n2}) ---")
            if not ok:
                raise SystemExit(f"A_CAP margin check failed for {word_label} m={m} "
                                  f"-- refusing to trust this word's census.")

            chains = enumerate_within_band(letters, band, A_CAP)
            print(f"    {len(chains)} admissible chains within band")

            groups_by_trajclass = {}   # (r1%27, r2%27, r3%27 or fewer) -> list of max_partial_sum
            floors_by_departure = {}   # departure_j -> min max_partial_sum
            n_never_depart = 0
            this_word_m_dump = []

            for (a_seq, chain_max, rho_curve) in chains:
                replay_max, replay_rho = independent_replay(letters, a_seq)
                replay_ok = (replay_max == chain_max) and (replay_rho == rho_curve)
                if not replay_ok:
                    replay_fails += 1

                dep = departure_prefix(rho_curve)
                traj_len = min(3, m)
                traj_class = tuple(rho_curve[i] % 27 for i in range(traj_len))

                groups_by_trajclass.setdefault(traj_class, []).append(chain_max)

                if dep is None:
                    n_never_depart += 1
                else:
                    prev = floors_by_departure.get(dep)
                    if prev is None or chain_max < prev:
                        floors_by_departure[dep] = chain_max

                row = {
                    "word_label": word_label, "m": m, "a_seq": ",".join(map(str, a_seq)),
                    "L": L, "band": band, "chain_max": chain_max,
                    "departure_prefix": dep if dep is not None else "",
                    "traj_class_mod27": ";".join(map(str, traj_class)),
                    "replay_ok": replay_ok,
                }
                all_chain_dump.append(row)
                this_word_m_dump.append(row)

            # independent second-pass cross-check on the materialized dump
            # rows for THIS (word_label, m) only
            recheck = {}
            for row in this_word_m_dump:
                if row["departure_prefix"] == "":
                    continue
                dep = row["departure_prefix"]
                cm = row["chain_max"]
                if dep not in recheck or cm < recheck[dep]:
                    recheck[dep] = cm
            if recheck != floors_by_departure:
                cross_check_fails += 1
                print(f"    *** CROSS-CHECK MISMATCH for {word_label} m={m}: "
                      f"{recheck} vs {floors_by_departure} ***")

            print(f"    never-departed (pure loop) chains: {n_never_depart}")
            print(f"    departure-floor table: "
                  f"{dict(sorted(floors_by_departure.items()))}")

            for dep_j, floor_cost in sorted(floors_by_departure.items()):
                all_departure_rows.append({
                    "word_label": word_label, "m": m, "L": L, "band": band,
                    "departure_prefix": dep_j, "min_cost_floor": floor_cost,
                    "f_of_j": floor_cost - L,
                })

            for traj_class, maxes in sorted(groups_by_trajclass.items()):
                all_group_rows.append({
                    "word_label": word_label, "m": m, "L": L, "band": band,
                    "traj_class_mod27": ";".join(map(str, traj_class)),
                    "n_chains_in_group": len(maxes),
                    "min_max_partial_sum": min(maxes),
                })

    print(f"\nTotal chains dumped: {len(all_chain_dump)}. Replay failures: {replay_fails}. "
          f"Cross-check failures: {cross_check_fails}.")

    out_dump = HERE / "m2_chain_dump.csv"
    with open(out_dump, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(all_chain_dump[0].keys()))
        w.writeheader()
        for r in all_chain_dump:
            w.writerow(r)
    print(f"Wrote {out_dump.name} ({len(all_chain_dump)} rows)")

    out_groups = HERE / "m2_trajclass_groups.csv"
    with open(out_groups, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(all_group_rows[0].keys()))
        w.writeheader()
        for r in all_group_rows:
            w.writerow(r)
    print(f"Wrote {out_groups.name} ({len(all_group_rows)} rows)")

    out_dep = HERE / "m2_departure_floor_table.csv"
    with open(out_dep, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(all_departure_rows[0].keys()))
        w.writeheader()
        for r in all_departure_rows:
            w.writerow(r)
    print(f"Wrote {out_dep.name} ({len(all_departure_rows)} rows) -- "
          f"THE DECISIVE TABLE (departure prefix -> min cost)")

    # -------------------------------------------------------------
    # Frozen prediction verdict: floor(dep at j) = L + f(j), f>=1
    # nonincreasing in j
    # -------------------------------------------------------------
    print("\n=== FROZEN PREDICTION VERDICT ===")
    print("floor(departure at j) = L + f(j), f(j) >= 1 nonincreasing in j "
          "(leaving late is cheaper) -- 60% predicted\n")

    by_word_m = {}
    for r in all_departure_rows:
        key = (r["word_label"], r["m"])
        by_word_m.setdefault(key, []).append(r)

    n_f_nonneg_all = True
    n_nonincreasing_all = True
    detail_lines = []
    for (word_label, m), rows in sorted(by_word_m.items()):
        rows_sorted = sorted(rows, key=lambda r: r["departure_prefix"])
        fseq = [(r["departure_prefix"], r["f_of_j"]) for r in rows_sorted]
        f_nonneg = all(f >= 1 for (_, f) in fseq)
        nonincreasing = all(fseq[i][1] >= fseq[i + 1][1] for i in range(len(fseq) - 1))
        n_f_nonneg_all = n_f_nonneg_all and f_nonneg
        n_nonincreasing_all = n_nonincreasing_all and nonincreasing
        detail_lines.append(
            f"  {word_label} m={m}: (j, f(j)) = {fseq} | f>=1 everywhere: {f_nonneg} | "
            f"nonincreasing in j: {nonincreasing}")

    for line in detail_lines:
        print(line)

    verdict = "HIT" if (n_f_nonneg_all and n_nonincreasing_all) else "MISS"
    print(f"\nf(j) >= 1 for all (word,m) rows: {n_f_nonneg_all}")
    print(f"f(j) nonincreasing in j for all (word,m) rows: {n_nonincreasing_all}")
    print(f"Verdict: {verdict}")

    print(f"\nTotal wall: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
