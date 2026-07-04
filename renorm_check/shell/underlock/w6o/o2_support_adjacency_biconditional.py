#!/usr/bin/env python3
"""
W6O-O2 -- Support-adjacency biconditional (N3's law, tested properly),
per W6O_LEMMA_SCALE_ORDER.md section O2.

BACKGROUND (W6N-N3, SYNTHESIS.md): N3 catalogued dips (f(j)=1 departure
positions, at band L+1 -- see BAND NOTE below, inherited verbatim from
N3 since this order also specifies "band L+1") on mechanical-family
rows m=5..9 and found 9/9 dips support-adjacent (dist_to_nearest_
support <= 1). That is the FORWARD direction only (dips => support-
adjacent), tested on a small catalog. This round tests the actual
BICONDITIONAL: is EVERY dip support-adjacent, AND is EVERY support-
adjacent position (within the relevant range) a dip?

SCOPE (per the order's exact text): "all mechanical rows m<=11 both
families + true-word windows m<=11, band L+1". This is a genuine
scope widening over N3 (which went to m=9 for mechanical families
only, no true-word rows at all) -- the biconditional's REVERSE
direction (support-adjacent => dip) requires knowing, for every
support-adjacent position, whether the band-L+1 census reaches it at
all -- exactly what N3's own band-narrowing note already flagged:
"dip" and "reachable within L+1" are the SAME event at this band (an
L+1 band cannot represent f(j)=2; a departure either appears at f=1
or doesn't appear in-band at all). This is carried forward from N3
as-is (not silently resolved) since it directly controls how the 2x2
table's cells are populated: "support-adjacent but NOT a dip"
literally means "support-adjacent position that the L+1 band census
does not reach" -- reported exactly as such.

THE 2x2 TABLE (per position j, 1<=j<=m, across all rows in scope):
  - "dip": position j is a departure-prefix reachable within band L+1
    (equivalently: SOME admissible chain within L+1 departs from the
    loop exactly at prefix j -- f(j)=1 is a fact ABOUT THE WORD, at
    THIS band; not every j is even a candidate departure point for
    EVERY word -- see below).
  - "support-adjacent": dist_to_nearest_support(j) <= 1, i.e. letters[j]
    itself is a support letter (c=1, dist=0) OR the letter immediately
    following it in the window is (dist=1) -- SAME operational
    definition as N3's distance_to_nearest_support (distance to the
    NEAREST support letter AT OR AFTER j).
  cells: (dip, adjacent), (dip, not-adjacent), (not-dip, adjacent),
  (not-dip, not-adjacent) -- counted over ALL positions j=1..m for
  every word in scope (not just observed dip positions), since the
  biconditional's reverse direction needs the full population of
  support-adjacent positions, dip or not.

Frozen prediction (Fable): forward direction survives (dips => support-
adjacent) -- 70%; reverse fails (adjacency is necessary, not
sufficient) -- 70%. Deliverable: the 2x2 table + the exact extra
condition that separates dip from non-dip among support-adjacent
positions, if visible.

BAND NOTE (inherited from N3, restated because it changes what "dip"
means operationally): band = L+1 (order's own text, both N3 and O2).
At this band, f(j) can only ever be 1 (present) or absent (no
admissible chain within L+1 departs at j at all) -- so "is position j
a dip" is exactly "does the L+1-band exhaustive DFS produce at least
one admissible chain whose departure-prefix is j".

INSTRUMENT RULE (binding): Path C only (parity-forced backward DFS,
D_free semantics), same core primitive as N3's
enumerate_within_band / departure_prefix, independently re-derived
here (not imported) at THIS order's own scope (m<=11, both mechanical
families + true-word windows -- N3 had no true-word rows and stopped
at m=9). Every departure-floor witness independently re-derived
(fresh from-scratch residue/cost replay) before being trusted, per
the W6L/W6M/W6N discipline.

NOTE ON REUSE (deliberate, per the order's own instruction to reuse/
extend w6n machinery): loop_L, cap_margin_check, independent_replay
below intentionally reuse the same shapes as w6o/o1's and w6n/n3's
own primitives -- these are the fixed house-standard operations, not
accidental duplication.
"""
from __future__ import annotations

import csv
import sys
import time
import resource
from pathlib import Path

HERE = Path(__file__).parent
UNDERLOCK = HERE.parent
W6E = UNDERLOCK / "w6e"
sys.path.insert(0, str(UNDERLOCK))
sys.path.insert(0, str(W6E))

from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402
from underlock_words import credit_golden_per8, credit_sqrt2_per12  # noqa: E402
from e1_walkers import backward_letters, credit_true  # noqa: E402

M_SCOPE = list(range(2, 12))  # m<=11 (start at 2: m=1 has no meaningful window)
A_CAP = 40
BAND_EXTRA = 1  # "band L+1" per the order's own text (same as N3)
RSS_CAP_GB = 8.0

WORD_SOURCES = {
    "golden-per8": credit_golden_per8,
    "sqrt2-per12": credit_sqrt2_per12,
    "true-word": credit_true,
}


def rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)


def loop_L(letters):
    running = 0
    best = 0
    for c in letters:
        running = running + (2 - c)
        best = max(best, running)
    return best


def enumerate_within_band(letters, band, a_cap):
    """Exhaustive DFS, canonical order, D_free semantics (independently
    re-derived here): every admissible a-sequence whose max partial
    sum stays <= band. Returns list of (a_seq, max_partial_sum,
    rho_hist)."""
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
    for idx, r in enumerate(rho_curve):
        if r != 1:
            return idx + 1
    return None


def independent_replay(letters, a_seq):
    """Fresh from-scratch recomputation, structurally independent of
    the DFS's own bookkeeping -- the W6L/W6M/W6N exact-replay
    discipline."""
    rho = 1
    running = 0
    max_so_far = 0
    rho_curve = []
    for c, a in zip(letters, a_seq):
        parity = forced_parity_for_backward_step(rho)
        assert parity is not None
        assert (a % 2 == 0) == (parity == 0)
        running += (a - c)
        max_so_far = max(max_so_far, running)
        rho = backward_predecessor_exact(rho, a)
        rho_curve.append(rho)
    return max_so_far, tuple(rho_curve)


def distance_to_nearest_support(letters, j_1idx):
    """Distance from position j (1-indexed, canonical order) to the
    nearest support letter (c==1) AT OR AFTER j in the window. 0 if
    letters[j-1]==1 itself. None if no support letter exists at or
    after j (SAME definition as N3's distance_to_nearest_support)."""
    m = len(letters)
    for d in range(0, m - (j_1idx - 1)):
        pos = (j_1idx - 1) + d
        if letters[pos] == 1:
            return d
    return None


def is_support_adjacent(letters, j_1idx):
    d = distance_to_nearest_support(letters, j_1idx)
    return d is not None and d <= 1


def main():
    t0 = time.time()
    print("=== W6O-O2: support-adjacency biconditional ===\n")
    print(f"Scope: m={M_SCOPE[0]}..{M_SCOPE[-1]}, mechanical families + true-word, "
          f"band=L+{BAND_EXTRA}\n")

    assert backward_predecessor_exact(1, 2) == 1, "loop fixed-point check FAILED"

    all_position_rows = []
    all_chain_dump = []
    replay_fails = 0

    for word_label, credit_fn in WORD_SOURCES.items():
        for m in M_SCOPE:
            letters = backward_letters(credit_fn, m, anchor_steps=53)
            L = loop_L(letters)
            band = L + BAND_EXTRA

            ok, n1, n2 = cap_margin_check(letters, band, A_CAP, A_CAP * 2)
            print(f"--- {word_label} m={m}: L={L} band=L+{BAND_EXTRA}={band} "
                  f"cap-margin {'OK' if ok else 'FAIL'} (cap40={n1} cap80={n2}) ---")
            if not ok:
                raise SystemExit(f"A_CAP margin check FAILED for {word_label} m={m}")

            chains = enumerate_within_band(letters, band, A_CAP)

            dip_positions = set()
            n_never_depart = 0
            for (a_seq, chain_max, rho_curve) in chains:
                replay_max, replay_rho = independent_replay(letters, a_seq)
                if not (replay_max == chain_max and replay_rho == rho_curve):
                    replay_fails += 1
                dep = departure_prefix(rho_curve)
                if dep is None:
                    n_never_depart += 1
                    continue
                dip_positions.add(dep)
                all_chain_dump.append({
                    "word_label": word_label, "m": m, "a_seq": ",".join(map(str, a_seq)),
                    "L": L, "band": band, "chain_max": chain_max,
                    "departure_prefix": dep,
                })

            print(f"    {len(chains)} admissible chains within band; "
                  f"{len(dip_positions)} distinct dip positions: {sorted(dip_positions)}")

            # 2x2 table population: every position j=1..m
            for j in range(1, m + 1):
                is_dip = j in dip_positions
                adj = is_support_adjacent(letters, j)
                dist = distance_to_nearest_support(letters, j)
                letter_at_j = letters[j - 1]
                all_position_rows.append({
                    "word_label": word_label, "m": m, "L": L, "band": band,
                    "position_j": j, "is_dip": is_dip, "is_support_adjacent": adj,
                    "dist_to_nearest_support": dist, "letter_at_j": letter_at_j,
                })

    print(f"\nTotal chains dumped: {len(all_chain_dump)}. Replay failures: {replay_fails}.")

    out_dump = HERE / "o2_chain_dump.csv"
    with open(out_dump, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(all_chain_dump[0].keys()))
        w.writeheader()
        for r in all_chain_dump:
            w.writerow(r)
    print(f"Wrote {out_dump.name} ({len(all_chain_dump)} rows)")

    out_positions = HERE / "o2_position_table.csv"
    with open(out_positions, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(all_position_rows[0].keys()))
        w.writeheader()
        for r in all_position_rows:
            w.writerow(r)
    print(f"Wrote {out_positions.name} ({len(all_position_rows)} rows)")

    # -------------------------------------------------------------
    # The 2x2 table
    # -------------------------------------------------------------
    n_dip_adj = sum(1 for r in all_position_rows if r["is_dip"] and r["is_support_adjacent"])
    n_dip_nonadj = sum(1 for r in all_position_rows if r["is_dip"] and not r["is_support_adjacent"])
    n_nondip_adj = sum(1 for r in all_position_rows if not r["is_dip"] and r["is_support_adjacent"])
    n_nondip_nonadj = sum(1 for r in all_position_rows if not r["is_dip"] and not r["is_support_adjacent"])
    n_dip_total = n_dip_adj + n_dip_nonadj
    n_adj_total = n_dip_adj + n_nondip_adj

    print("\n=== THE 2x2 TABLE ===")
    print(f"                 support-adjacent   NOT adjacent      row-total")
    print(f"  dip            {n_dip_adj:>10d}       {n_dip_nonadj:>10d}      {n_dip_total:>10d}")
    print(f"  NOT dip        {n_nondip_adj:>10d}       {n_nondip_nonadj:>10d}      {n_nondip_nonadj+n_nondip_adj:>10d}")
    print(f"  col-total      {n_adj_total:>10d}       {n_dip_nonadj+n_nondip_nonadj:>10d}      {len(all_position_rows):>10d}")

    frac_forward = n_dip_adj / n_dip_total if n_dip_total else float("nan")
    frac_reverse = n_dip_adj / n_adj_total if n_adj_total else float("nan")
    print(f"\nFORWARD (dip => adjacent): {n_dip_adj}/{n_dip_total} = "
          f"{100*frac_forward:.1f}% of dips are support-adjacent")
    print(f"REVERSE (adjacent => dip): {n_dip_adj}/{n_adj_total} = "
          f"{100*frac_reverse:.1f}% of support-adjacent positions are dips")

    # -------------------------------------------------------------
    # The extra condition separating dip from non-dip among
    # support-adjacent positions (if visible): look at dist=0 vs
    # dist=1 breakdown, and any other structural feature available
    # (letter at j, band-tightness L vs L+1 usage).
    # -------------------------------------------------------------
    print("\n=== SEPARATING CONDITION AMONG SUPPORT-ADJACENT POSITIONS ===")
    adj_rows = [r for r in all_position_rows if r["is_support_adjacent"]]
    for dist_val in (0, 1):
        subset = [r for r in adj_rows if r["dist_to_nearest_support"] == dist_val]
        if subset:
            n_dip_sub = sum(1 for r in subset if r["is_dip"])
            print(f"  dist={dist_val}: {n_dip_sub}/{len(subset)} are dips "
                  f"({100*n_dip_sub/len(subset):.1f}%)")
        else:
            print(f"  dist={dist_val}: no rows")
    for letter_val in (1, 2):
        subset = [r for r in adj_rows if r["letter_at_j"] == letter_val]
        if subset:
            n_dip_sub = sum(1 for r in subset if r["is_dip"])
            print(f"  letter_at_j={letter_val}: {n_dip_sub}/{len(subset)} are dips "
                  f"({100*n_dip_sub/len(subset):.1f}%)")
        else:
            print(f"  letter_at_j={letter_val}: no rows")

    # -------------------------------------------------------------
    # Frozen prediction verdict
    # -------------------------------------------------------------
    print("\n=== FROZEN PREDICTION VERDICT ===")
    print("Forward (dips => support-adjacent) survives -- 70% predicted")
    print("Reverse (adjacency => dip) FAILS -- 70% predicted (necessary, not sufficient)\n")

    forward_verdict = "HIT" if frac_forward == 1.0 else (
        "PARTIAL" if frac_forward >= 0.9 else "MISS")
    reverse_verdict = "HIT" if frac_reverse < 1.0 else "MISS"

    print(f"Forward: {forward_verdict} ({100*frac_forward:.2f}% of {n_dip_total} dips adjacent)")
    reverse_note = ("adjacency is NOT sufficient, as predicted" if frac_reverse < 1.0
                     else "every adjacent position IS a dip -- reverse HOLDS, contradicting prediction")
    print(f"Reverse: {reverse_verdict} ({100*frac_reverse:.2f}% of {n_adj_total} "
          f"adjacent positions are dips -- {reverse_note})")

    print(f"\nTotal wall: {time.time()-t0:.1f}s, peak RSS: {rss_gb():.3f} GB")


if __name__ == "__main__":
    main()
