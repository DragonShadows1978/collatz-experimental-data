#!/usr/bin/env python3
"""
W6M-M1 -- Where the +1 bites (the strictness map), per
W6M_GLOBAL_LEMMA_MAP_ORDER.md section M1.

INSTRUMENT RULE (binding, W6K/W6L): all order-sensitive computation
goes through Path C (w6k/k0_canonical_engine.py's exact semantics,
24/24 K0-gated) or Path A (w6e/e1_walkers.py). Path B
(f1_engine_ext/bfs_Dm) is RETIRED -- not used anywhere in this script.

Scope: m=4..8, words = the two mechanical-family rows (golden-per8,
sqrt2-per12, via w6e.e1_walkers.backward_letters at anchor_steps=53,
same canonical-window convention as every L1/L3 mechanical-family use)
+ 200 random {1,2}^m words per m (seeded, canonical order: letters
given directly in consumption order, index0=nearest terminal -- for a
bare word this is left-to-right, matching k0/k1's own convention).

For each word: enumerate ALL admissible exponent sequences (canonical
order, D_free semantics -- ceiling-OFF, matching every W6K/W6L
headline result) whose max partial sum g(k) = sum_{j<=k}(a_j-c_j)
stays <= L(w)+1 throughout (L(w) = the loop's own max partial sum,
computed the same way with a_j=2 forced -- g_loop). This is an
EXHAUSTIVE enumeration (branch-and-bound: prune the instant a partial
sum exceeds L(w)+1), not a sample -- the "+1 slack" band is narrow
enough (verified below by cap-margin and count sanity) to stay small.

For every non-loop chain found (the loop itself, all a_j=2, is
excluded from the reported set but its own g_loop curve is the
reference curve throughout):
  (i)   prefix k* where the chain's own max is attained (first k
        achieving the chain's max, i.e. its own argmax)
  (ii)  residue class of the chain's ACTUAL exact residue rho at k*
        mod 3, 9, 27 (backward-walk residue, exact integers, no
        truncation -- m<=8 so 3^8=6561, tiny)
  (iii) g(k*) - g_loop(k*) (chain's own max value minus the loop's
        g at the SAME prefix k*, i.e. how far the chain's binding
        point sits above/below the loop's curve at that same index)

Frozen predictions (Fable, registered in the order):
  (a) every non-loop chain's max is attained at a prefix where its
      residue has LEFT the 1-ray at the relevant precision -- 65%.
      Operationalized: "left the 1-ray at the relevant precision" =
      rho(k*) != 1 mod 3^p for SOME precision p in {1,2,3} that is
      "relevant" -- taken here as: not IN the 1-ray at mod-3 (the
      loop's own residue is always 1 mod 3^k trivially only at k=0;
      more precisely a chain still "on the 1-ray" at prefix k means
      rho(k) == 1 mod 3^k exactly, i.e. it has tracked the terminal's
      backward orbit under a=2 every step so far). Tested exactly
      (both readings reported: mod-3 non-unit reading and the
      exact "still equals the loop's own residue trajectory" reading,
      since the order's phrasing admits both and the second is the
      operationally sharper one -- both computed, neither hidden).
  (b) g(k*) >= g_loop(k*) for ALL non-loop chains (the loop's binding
      prefix is a universal floor point) -- 55%.

Every reported witness (any chain used as an example / any crack) is
exact-integer replayed in-process via engine.backward_predecessor_exact
(the same primitive that generates it -- since this script IS the
generator, "replay" here means: independently recomputing rho at k*
via a fresh, separate application of the primitive from scratch,
rather than trusting the DFS's own running state) -- see
verify_residue_by_closed_form below. This is the independent-
recomputation discipline the W6L lesson demands: the per-step DFS
residue and the fresh from-scratch residue are two structurally
different computation passes over the same integer.
"""
from __future__ import annotations

import csv
import random
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

M_SCOPE = list(range(4, 9))  # 4..8
N_RANDOM_PER_M = 200
SEED = 20260704
A_CAP = 40  # matches k0_canonical_engine's own margin-checked default


# ---------------------------------------------------------------------
# Core: loop curve + exhaustive slack-band enumeration
# ---------------------------------------------------------------------

def loop_curve(letters):
    """g_loop(k) = sum_{j<=k}(2-c_j), canonical order, k=1..m (1-indexed
    prefixes). Returns list indexed [0..m-1] -> g_loop at prefix k=idx+1,
    plus L(w) = max of that curve (0 if never positive)."""
    running = 0
    curve = []
    for c in letters:
        running += (2 - c)
        curve.append(running)
    L = max([0] + curve)
    return curve, L


def loop_residue_curve(letters):
    """Exact backward-walk residue of the LOOP chain (all a_j=2) at
    each prefix k=1..m, via the actual engine primitive (ground truth
    for cross-check against the independent from-scratch recompute
    below)."""
    rho = 1
    curve = []
    for _ in letters:
        rho = backward_predecessor_exact(rho, 2)
        curve.append(rho)
    return curve


def enumerate_slack_band(letters, slack_bound, a_cap):
    """Exhaustive DFS, canonical order, D_free (ceiling-off) semantics:
    every admissible a-sequence (parity-forced at each step, uncapped
    except the generous a_cap margin-checked below) whose max partial
    sum over ALL prefixes stays <= slack_bound. Prunes the instant the
    running max exceeds slack_bound (sound: max is monotone
    nondecreasing along any DFS extension). Returns list of
    (a_seq, g_curve, rho_curve) for every complete admissible sequence
    found, where g_curve[k] and rho_curve[k] are the running max-so-far
    and exact residue AFTER consuming letter k+1 (0-indexed prefixes,
    i.e. rho_curve[j] is rho after prefix length j+1)."""
    m = len(letters)
    results = []

    def dfs(j, rho, running, max_so_far, a_seq, g_hist, rho_hist):
        if max_so_far > slack_bound:
            return
        if j == m:
            results.append((tuple(a_seq), tuple(g_hist), tuple(rho_hist)))
            return
        c = letters[j]
        parity = forced_parity_for_backward_step(rho)
        if parity is None:
            return
        a_min = 2 if parity == 0 else 1
        for a in range(a_min, a_min + a_cap, 2):
            running2 = running + (a - c)
            max2 = max(max_so_far, running2)
            if max2 > slack_bound:
                continue
            rho2 = backward_predecessor_exact(rho, a)
            dfs(j + 1, rho2, running2, max2, a_seq + [a],
                g_hist + [running2], rho_hist + [rho2])

    dfs(0, 1, 0, 0, [], [], [])
    return results


def cap_margin_check(letters, slack_bound, base_cap, wider_cap):
    base = enumerate_slack_band(letters, slack_bound, base_cap)
    wider = enumerate_slack_band(letters, slack_bound, wider_cap)
    return len(base) == len(wider), len(base), len(wider)


def is_still_on_loop_ray(rho_k, loop_rho_curve, k_idx):
    """Exact reading of frozen prediction (a)'s stronger operationalization:
    has the chain's residue at prefix k (0-indexed k_idx, i.e. prefix
    length k_idx+1) diverged from the LOOP's own residue at the same
    prefix length? (loop_rho_curve[k_idx] is the loop's exact rho there.)
    """
    return rho_k == loop_rho_curve[k_idx]


def mod3_unit_reading(rho_k):
    """Weaker/coarser reading of (a): rho mod 3 (the loop's own residue
    is a specific class mod 3^k at every prefix; this is the raw mod-3
    class of the chain's residue at k*, reported for completeness)."""
    return rho_k % 3


def _product12(m):
    if m == 0:
        yield ()
        return
    for rest in _product12(m - 1):
        yield (1,) + rest
        yield (2,) + rest


def build_word_list():
    words = {}
    for m in M_SCOPE:
        golden = tuple(backward_letters(credit_golden_per8, m, anchor_steps=53))
        sqrt2 = tuple(backward_letters(credit_sqrt2_per12, m, anchor_steps=53))
        words[(m, "golden-per8")] = golden
        words[(m, "sqrt2-per12")] = sqrt2
        rng = random.Random(SEED + m)
        seen = {golden, sqrt2}
        rand_words = []
        universe_size = 2 ** m
        if universe_size <= N_RANDOM_PER_M + 5:
            # m=4,5: 16,32 -- take the whole space minus the two mechanical
            # rows already counted (report actual count, not padded).
            all_words = [tuple(w) for w in _product12(m)]
            rng.shuffle(all_words)
            for w in all_words:
                if w not in seen:
                    rand_words.append(w)
                    seen.add(w)
                if len(rand_words) >= N_RANDOM_PER_M:
                    break
        else:
            attempts = 0
            while len(rand_words) < N_RANDOM_PER_M and attempts < N_RANDOM_PER_M * 50:
                w = tuple(rng.choice((1, 2)) for _ in range(m))
                attempts += 1
                if w not in seen:
                    rand_words.append(w)
                    seen.add(w)
        for i, w in enumerate(rand_words):
            words[(m, f"random{i:03d}")] = w
    return words


def main():
    t0 = time.time()
    print("=== W6M-M1: the strictness map ===\n")
    print(f"Scope: m={M_SCOPE[0]}..{M_SCOPE[-1]}, mechanical-family rows "
          f"(golden-per8, sqrt2-per12) + up to {N_RANDOM_PER_M} random {{1,2}}^m "
          f"words/m (seed={SEED})\n")

    words = build_word_list()
    print(f"Total words built: {len(words)}\n")

    print("--- Pre-run cap margin check (A_CAP=40 vs 80, on the widest-band probes) ---")
    probe_ok = True
    for m in (4, 8):
        w_probe = tuple([1] * m)
        _, L_probe = loop_curve(w_probe)
        ok, n1, n2 = cap_margin_check(w_probe, L_probe + 1, 40, 80)
        probe_ok = probe_ok and ok
        print(f"  m={m} all-1s word: slack={L_probe+1} cap40->{n1} cap80->{n2} "
              f"{'OK' if ok else '*** FAIL -- widen A_CAP ***'}")
    if not probe_ok:
        raise SystemExit("A_CAP margin check failed -- refusing to run census with an "
                          "unvalidated exponent cap.")
    print()

    rows = []              # per-chain classification rows
    per_word_summary = []  # per-word summary (loop L, chain count, etc.)
    n_residue_check_fail = 0

    for (m, label), letters in sorted(words.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        g_loop_curve, L = loop_curve(letters)
        loop_rho_curve = loop_residue_curve(letters)
        slack_bound = L + 1
        chains = enumerate_slack_band(letters, slack_bound, A_CAP)
        loop_seq = tuple([2] * m)

        n_chains_total = len(chains)
        n_non_loop = 0
        for (a_seq, g_hist, rho_hist) in chains:
            if a_seq == loop_seq:
                continue
            n_non_loop += 1
            chain_max = max(g_hist)
            k_star = g_hist.index(chain_max)  # first index achieving it (0-indexed)

            # independent residue re-derivation (the W6L exact-replay
            # discipline): recompute rho at k* fresh, from scratch
            rho_kstar_fresh = 1
            for a in a_seq[:k_star + 1]:
                rho_kstar_fresh = backward_predecessor_exact(rho_kstar_fresh, a)
            residue_ok = (rho_kstar_fresh == rho_hist[k_star])
            if not residue_ok:
                n_residue_check_fail += 1

            rho_kstar = rho_hist[k_star]
            on_loop_ray = is_still_on_loop_ray(rho_kstar, loop_rho_curve, k_star)
            mod3 = mod3_unit_reading(rho_kstar)
            mod9 = rho_kstar % 9
            mod27 = rho_kstar % 27

            g_at_kstar = g_hist[k_star]
            g_loop_at_kstar = g_loop_curve[k_star]
            diff = g_at_kstar - g_loop_at_kstar

            rows.append({
                "m": m, "word_label": label, "word": "".join(map(str, letters)),
                "a_seq": ",".join(map(str, a_seq)),
                "L": L, "slack_bound": slack_bound,
                "k_star_1indexed": k_star + 1,
                "chain_max": chain_max,
                "rho_at_kstar": rho_kstar,
                "rho_mod3": mod3, "rho_mod9": mod9, "rho_mod27": mod27,
                "left_loop_ray_exact": not on_loop_ray,
                "left_1ray_mod3_coarse": mod3 != 1,
                "g_at_kstar": g_at_kstar,
                "g_loop_at_kstar": g_loop_at_kstar,
                "diff_g_minus_gloop": diff,
                "residue_independent_check": residue_ok,
            })

        per_word_summary.append({
            "m": m, "word_label": label, "word": "".join(map(str, letters)),
            "L": L, "slack_bound": slack_bound,
            "n_chains_in_band": n_chains_total, "n_non_loop_chains": n_non_loop,
        })

    wall_enum = time.time() - t0
    print(f"Enumeration done: {len(words)} words, {sum(r['n_chains_in_band'] for r in per_word_summary)} "
          f"total admissible chains within L+1, of which {len(rows)} non-loop; wall={wall_enum:.1f}s")

    if n_residue_check_fail:
        print(f"\n*** {n_residue_check_fail} INDEPENDENT RESIDUE CHECK FAILURES -- INVESTIGATE ***")
    else:
        print(f"\nIndependent residue re-derivation: {len(rows)}/{len(rows)} PASS "
              f"(every reported rho(k*) exact-replayed from scratch)")

    # write outputs
    fieldnames = [
        "m", "word_label", "word", "a_seq", "L", "slack_bound", "k_star_1indexed",
        "chain_max", "rho_at_kstar", "rho_mod3", "rho_mod9", "rho_mod27",
        "left_loop_ray_exact", "left_1ray_mod3_coarse", "g_at_kstar",
        "g_loop_at_kstar", "diff_g_minus_gloop", "residue_independent_check"]
    out_chains = HERE / "m1_strictness_chains.csv"
    with open(out_chains, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote {out_chains.name} ({len(rows)} non-loop chain rows)")

    out_summary = HERE / "m1_word_summary.csv"
    with open(out_summary, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(per_word_summary[0].keys()))
        w.writeheader()
        for r in per_word_summary:
            w.writerow(r)
    print(f"Wrote {out_summary.name} ({len(per_word_summary)} word rows)")

    # -------------------------------------------------------------
    # Frozen prediction verdicts
    # -------------------------------------------------------------
    print("\n=== FROZEN PREDICTION VERDICTS ===")

    n_total = len(rows)
    if n_total == 0:
        print("No non-loop chains found within L+1 on any word -- predictions VACUOUS.")
        print(f"\nTotal wall: {time.time()-t0:.1f}s")
        return

    n_left_exact = sum(1 for r in rows if r["left_loop_ray_exact"])
    n_left_coarse = sum(1 for r in rows if r["left_1ray_mod3_coarse"])
    frac_exact = n_left_exact / n_total
    frac_coarse = n_left_coarse / n_total
    print(f"\n(a) 'left the 1-ray at the relevant precision' -- 65% predicted:")
    print(f"    exact reading (rho(k*) != loop's own rho at same prefix): "
          f"{n_left_exact}/{n_total} = {100*frac_exact:.1f}%")
    print(f"    coarse reading (rho(k*) mod 3 != 1): "
          f"{n_left_coarse}/{n_total} = {100*frac_coarse:.1f}%")
    verdict_a = "HIT" if round(frac_exact * 100) == 65 or abs(frac_exact - 0.65) <= 0.05 else "MISS"
    print(f"    Verdict (exact reading, tolerance +/-5pp around 65%): {verdict_a} "
          f"-- raw fraction {100*frac_exact:.1f}% is the number of record.")

    n_floor_holds = sum(1 for r in rows if r["diff_g_minus_gloop"] >= 0)
    frac_floor = n_floor_holds / n_total
    print(f"\n(b) g(k*) >= g_loop(k*) for ALL non-loop chains -- 55% predicted "
          f"(binary claim: holds universally or it does not):")
    print(f"    holds on {n_floor_holds}/{n_total} = {100*frac_floor:.2f}% of non-loop chains")
    verdict_b = "HIT" if n_floor_holds == n_total else "MISS"
    print(f"    Verdict: {verdict_b}")
    if n_floor_holds != n_total:
        violations = [r for r in rows if r["diff_g_minus_gloop"] < 0]
        print(f"    {len(violations)} VIOLATIONS found -- these locate exactly where the "
              f"global argument must NOT anchor (per the order's own framing). Sample "
              f"(up to 10):")
        for r in violations[:10]:
            print(f"      m={r['m']} word={r['word_label']} a_seq={r['a_seq']} "
                  f"k*={r['k_star_1indexed']} diff={r['diff_g_minus_gloop']}")
        out_violations = HERE / "m1_floor_violations.csv"
        with open(out_violations, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in violations:
                w.writerow(r)
        print(f"    Wrote {out_violations.name} ({len(violations)} rows)")

    print(f"\nTotal wall: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
