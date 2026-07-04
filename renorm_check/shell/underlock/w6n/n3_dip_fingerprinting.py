#!/usr/bin/env python3
"""
W6N-N3 -- Dip fingerprinting (the boundary term's positions), per
W6N_FLOOR_MECHANISM_ORDER.md section N3.

M2 (W6M) built the departure-prefix -> min-cost-floor table for the two
mechanical-family words (golden-per8, sqrt2-per12) at m=5..8, within
L+2, and found f(j) = floor - L >= 1 always, but NOT nonincreasing in
j -- the real shape is a flat ceiling (mostly f(j)=2, i.e. chains ride
the full L+2 slack) with SPARSE single-departure-prefix "dips" down to
f(j)=1. This round: (i) rerun the SAME departure-floor computation
(identical semantics -- Path C, D_free, band = L+1 per THIS order's
own text: "within L+1", narrower than M2's L+2) extended to every
mechanical-family row m<=9 (m=5..9, five rows per family instead of
M2's four, 5..8); (ii) catalog every dip position (f(j)==1, the
minimum possible value on this order's tighter L+1 band -- see NOTE
below on the band-narrowing consequence); (iii) for each dip: record
the word's local structure at that position.

BAND NOTE (honest, load-bearing): M2 used band=L+2 (giving room for
f(j) in {1,2}); this order specifies "within L+1" for N3's extension.
On an L+1 band the ONLY possible values of f(j) are 1 (the tightest
possible: departing at j costs exactly one more than the loop) or the
departure not appearing in-band at all (any chain departing at j that
would need more than L+1 to complete is simply absent from an L+1-band
census, not present-with-a-higher-floor as it would be at L+2). So
"dip to f=1" and "floor value at all" become the SAME event at this
band -- every departure-prefix that appears in an L+1-band census is,
BY THE BAND's OWN CONSTRUCTION, a dip (f=1). This is reported exactly
as it is: the L+1 band cannot distinguish "flat ceiling at f=2" from
"absent" the way M2's L+2 band could, so N3's "dip catalog" here is
really "every departure prefix reachable at all within L+1" -- a
strictly smaller, band-narrowed version of M2's departure set (a
SUBSET of M2's own dip+ceiling departures, specifically the ones that
happen to cost exactly L+1). This is the correct reading of "within
L+1" as literally specified; the M2 comparison (which departures
persisted at L+2 with f=2 vs collapsed out of the L+1 census) is
reported alongside for continuity where m overlaps (5..8).

LOCAL STRUCTURE recorded per dip position j (canonical order, index 1
= nearest terminal, per backward_letters convention):
  - letter at j (c_j in {1,2})
  - distance to nearest SUPPORT letter (c=1, DERIVATION_NOTES sec 1's
    term) at or after position j in the window (0 if c_j itself is a
    support letter) -- well-defined for these pure periodic mechanical
    words.
  - "correction letter" (the true-word-vs-periodic-word deviation
    concept from W6G's g4_true_word_round.py): NOT APPLICABLE to this
    experiment's word class -- golden-per8/sqrt2-per12 ARE the
    periodic mechanical words themselves (not compared against a true
    Sturmian word here), so there is no periodic-vs-true divergence to
    measure a distance to. Reported as N/A explicitly rather than
    silently omitted (the order's own phrasing bundles "support/
    correction letter" as a pair; only the support-letter half is a
    well-defined quantity for this word class).
  - phase mod q (q = 8 for golden-per8, 12 for sqrt2-per12): the
    window-absolute forward step index mod the word's own period,
    i.e. which cyclic position of the periodic block position j
    corresponds to.

Frozen prediction (Fable, 55%): dips occur exactly at positions where
the word's suffix from j is a maximal-credit run (the chain can afford
one late unit because the remaining letters over-credit).
OPERATIONALIZED: "maximal-credit run" = the suffix window (from
position j to the end of the m-window) has the HIGHEST support-letter
(c=1) density among all same-length suffixes of this word's window --
i.e. j is (one of) the position(s) where suffix_support_count(j) is
maximized. Tested exactly below (both a strict-max reading and a
top-quartile reading, reported honestly).

INSTRUMENT RULE (binding): Path C only (parity-forced backward DFS,
D_free semantics), same core loop as w6m/m2_departure_floor.py,
independently re-derived here (not imported) at the order's own L+1
band and m<=9 extension. Every departure-floor witness is
independently re-derived (fresh from-scratch residue/cost replay, not
reused DFS state) before being trusted -- the W6L/W6M discipline.
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

M_SCOPE = list(range(5, 10))  # 5..9 (extends M2's 5..8 by one row)
A_CAP = 40
BAND_EXTRA = 1  # "within L+1" per the order's own text (narrower than M2's L+2)

MECH_WORDS = {
    "golden-per8": (credit_golden_per8, 8),
    "sqrt2-per12": (credit_sqrt2_per12, 12),
}


def loop_L(letters):
    running = 0
    best = 0
    for c in letters:
        running = running + (2 - c)
        best = max(best, running)
    return best


def enumerate_within_band(letters, band, a_cap):
    """Exhaustive DFS, canonical order, D_free semantics (identical
    core to w6m/m2_departure_floor.enumerate_within_band, independently
    re-derived here): every admissible a-sequence whose max partial sum
    stays <= band. Returns list of (a_seq, max_partial_sum, rho_curve)."""
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
    the DFS's own bookkeeping -- the W6L/W6M exact-replay discipline."""
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
    """Distance (in steps) from position j (1-indexed, canonical
    consumption order) to the nearest SUPPORT letter (c==1) at or
    after j in the window. 0 if letters[j-1]==1 itself. None if no
    support letter exists at or after j (word tail is all-2s from j
    on)."""
    m = len(letters)
    for d in range(0, m - (j_1idx - 1)):
        pos = (j_1idx - 1) + d
        if letters[pos] == 1:
            return d
    return None


def suffix_support_density(letters, j_1idx):
    """Number of support letters (c==1) in the suffix window
    [j-1 .. m-1] (0-indexed), i.e. from position j to the end,
    inclusive -- used to test the "maximal-credit run" frozen
    prediction (higher density = more over-credit available in the
    remaining window)."""
    m = len(letters)
    return sum(1 for pos in range(j_1idx - 1, m) if letters[pos] == 1)


def main():
    t0 = time.time()
    print("=== W6N-N3: dip fingerprinting (boundary term positions) ===\n")
    print(f"Scope: m={M_SCOPE[0]}..{M_SCOPE[-1]}, mechanical-family words, "
          f"band=L+{BAND_EXTRA} (per the order's 'within L+1' text)\n")

    assert backward_predecessor_exact(1, 2) == 1, "loop fixed-point check FAILED"

    all_dip_rows = []
    all_chain_dump = []
    replay_fails = 0

    for word_label, (credit_fn, period_q) in MECH_WORDS.items():
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
            print(f"    {len(chains)} admissible chains within band")

            floors_by_departure = {}
            n_never_depart = 0
            for (a_seq, chain_max, rho_curve) in chains:
                replay_max, replay_rho = independent_replay(letters, a_seq)
                if not (replay_max == chain_max and replay_rho == rho_curve):
                    replay_fails += 1
                dep = departure_prefix(rho_curve)
                if dep is None:
                    n_never_depart += 1
                    continue
                prev = floors_by_departure.get(dep)
                if prev is None or chain_max < prev:
                    floors_by_departure[dep] = chain_max
                all_chain_dump.append({
                    "word_label": word_label, "m": m, "a_seq": ",".join(map(str, a_seq)),
                    "L": L, "band": band, "chain_max": chain_max,
                    "departure_prefix": dep,
                })

            print(f"    never-departed (loop) chains: {n_never_depart}")
            print(f"    departure-floor table (this band): "
                  f"{dict(sorted(floors_by_departure.items()))}")

            # window-absolute anchor: canonical order index j (1..m,
            # nearest-terminal-first) corresponds to absolute forward
            # step (53 - j) [backward_letters: index0 = c_{52}, i.e.
            # letters[idx] = credit_fn(53-1-idx); j=idx+1 -> absolute
            # step = 53-j]. Phase mod q of that absolute step.
            for dep_j, floor_cost in sorted(floors_by_departure.items()):
                f_of_j = floor_cost - L
                is_dip = (f_of_j == 1)  # the ONLY possible in-band value at L+1
                letter_at_j = letters[dep_j - 1]
                dist_support = distance_to_nearest_support(letters, dep_j)
                suffix_density = suffix_support_density(letters, dep_j)
                abs_step = 53 - dep_j
                phase = abs_step % period_q
                all_dip_rows.append({
                    "word_label": word_label, "m": m, "period_q": period_q,
                    "L": L, "band": band, "departure_prefix_j": dep_j,
                    "f_of_j": f_of_j, "is_dip_f1": is_dip,
                    "letter_at_j": letter_at_j,
                    "dist_to_nearest_support_at_or_after_j": dist_support,
                    "correction_letter_distance": "N/A (pure periodic word, no true-word comparison)",
                    "abs_forward_step": abs_step, "phase_mod_q": phase,
                    "suffix_support_density_from_j": suffix_density,
                })

    print(f"\nTotal chains dumped: {len(all_chain_dump)}. Replay failures: {replay_fails}.")

    out_dump = HERE / "n3_chain_dump.csv"
    with open(out_dump, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(all_chain_dump[0].keys()))
        w.writeheader()
        for r in all_chain_dump:
            w.writerow(r)
    print(f"Wrote {out_dump.name} ({len(all_chain_dump)} rows)")

    out_dips = HERE / "n3_dip_catalog.csv"
    with open(out_dips, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(all_dip_rows[0].keys()))
        w.writeheader()
        for r in all_dip_rows:
            w.writerow(r)
    print(f"Wrote {out_dips.name} ({len(all_dip_rows)} rows) -- THE DIP CATALOG")

    # -------------------------------------------------------------
    # Frozen prediction: dips occur where suffix-from-j is a
    # maximal-credit run (55%)
    # -------------------------------------------------------------
    print("\n=== FROZEN PREDICTION VERDICT ===")
    print("Dips occur exactly at positions where suffix-from-j is a "
          "maximal-credit (max support-density) run -- 55% predicted\n")

    dips = [r for r in all_dip_rows if r["is_dip_f1"]]
    print(f"Dip rows (f(j)=1, the only in-band value at L+1): {len(dips)}/{len(all_dip_rows)}")

    # Group by (word_label, m): for each, compute max suffix_support_density
    # over ALL positions j=1..m (not just departure positions) to test
    # whether dip positions coincide with the window-wide maximum.
    n_strict_max_hit = 0
    n_top_quartile_hit = 0
    n_tested = 0
    detail = []
    for word_label, (credit_fn, period_q) in MECH_WORDS.items():
        for m in M_SCOPE:
            letters = backward_letters(credit_fn, m, anchor_steps=53)
            all_densities = [suffix_support_density(letters, j) for j in range(1, m + 1)]
            max_density = max(all_densities)
            sorted_densities = sorted(all_densities, reverse=True)
            quartile_cut = sorted_densities[max(0, len(sorted_densities) // 4 - 1)] if len(sorted_densities) >= 4 else max_density
            these_dips = [r for r in dips if r["word_label"] == word_label and r["m"] == m]
            for r in these_dips:
                n_tested += 1
                d = r["suffix_support_density_from_j"]
                strict_hit = (d == max_density)
                topq_hit = (d >= quartile_cut)
                n_strict_max_hit += strict_hit
                n_top_quartile_hit += topq_hit
                detail.append(f"  {word_label} m={m} j={r['departure_prefix_j']} "
                              f"suffix_density={d} (window max={max_density}, "
                              f"top-quartile-cut={quartile_cut}) "
                              f"strict_max={strict_hit} top_quartile={topq_hit}")

    for line in detail:
        print(line)

    if n_tested == 0:
        print("\nNo dip rows to test against -- VACUOUS (no in-band departures found "
              "at this band width; see honest-wall note below if applicable).")
        verdict = "VACUOUS"
    else:
        frac_strict = n_strict_max_hit / n_tested
        frac_topq = n_top_quartile_hit / n_tested
        print(f"\nStrict-max reading: {n_strict_max_hit}/{n_tested} = {100*frac_strict:.1f}% "
              f"of dips sit at the window's own suffix-support-density maximum")
        print(f"Top-quartile reading: {n_top_quartile_hit}/{n_tested} = {100*frac_topq:.1f}% "
              f"of dips sit in the top quartile of suffix-support-density")
        verdict = "HIT" if frac_strict >= 0.5 or frac_topq >= 0.75 else "MISS"
    print(f"\nVerdict: {verdict}")

    print(f"\nTotal wall: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
