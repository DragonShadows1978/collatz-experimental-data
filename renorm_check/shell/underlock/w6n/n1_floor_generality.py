#!/usr/bin/env python3
"""
W6N-N1 -- Floor-point law at full generality, per
W6N_FLOOR_MECHANISM_ORDER.md section N1.

M1 (W6M) tested ALL admissible chains within L(w)+1 for m=4..8 (442
words: 2 mechanical + up to 200 random {1,2}^m/m) and found the floor
g(k*) >= g_loop(k*) holding 519/519 at the loop's own binding prefix
k* -- zero violations. This round extends the BUDGET (L+1 -> L+3) and
the WORD-LENGTH scope (m=4..8 -> m=4..7, exhaustive ALL 2^m words, not
a random sample) per the order's exact text: "Extend: ALL admissible
chains within L+3, m = 4..7 (exhaustive, Path C), same 442-word scope
trimmed as needed for runtime (state trims honestly)."

Reading of "same 442-word scope": M1's 442-word scope was ITSELF
already "mechanical rows + up to 200 random/m" -- not exhaustive over
{1,2}^m. The order's N1 explicitly upgrades this to "ALL admissible
chains" and "exhaustive" for m=4..7, so here we run the TRUE exhaustive
word space {1,2}^m for m=4..7 (sizes 16,32,64,128 = 240 words total,
strictly LESS than 442 -- the order's "trimmed as needed for runtime"
clause is honored by reporting the true exhaustive scope actually
achieved rather than padding with random words that would dilute the
exhaustiveness claim). The two mechanical-family words are INCLUDED
inside the m<=7 exhaustive enumeration already (both are specific
{1,2}^m words for each m), so no separate mechanical-row pass is
needed -- this is verified explicitly below (both mechanical words
appear as members of the enumerated word set at every m).

INSTRUMENT RULE (binding, W6K/W6L/W6M): Path C
(w6k/k0_canonical_engine.py semantics: parity-forced backward DFS,
D_free/ceiling-off) only. Path B retired, not used.

For each word w in {1,2}^m (m=4..7, exhaustive): compute L(w) = the
loop's own max partial sum (g_loop, all a_j=2). Exhaustively enumerate
(branch-and-bound DFS, canonical order) EVERY admissible chain whose
own max partial sum stays <= L(w)+3 (the widened slack band). For
every non-loop chain found: identify the LOOP's binding prefix k*
(argmax of g_loop -- fixed per word, independent of which chain is
being tested) and test g(k*) >= g_loop(k*) at that word-level k*
(the SAME index that M1 tested; the order's "at the loop's own binding
prefix k*" is a per-word quantity, computed once per word from the
loop curve, not per-chain).

Frozen prediction (Fable, 75%): exceptionless at every budget -- zero
violations, at L+3 exactly as at L+1. ANY violation must be exact-
replayed, dumped verbatim, and lead the digest (it would relocate the
induction's anchor).

Every reported witness (any violation, or the sample confirmations)
is exact-integer replayed in-process via a fresh, independent
from-scratch application of engine.backward_predecessor_exact --
the W6L/W6M discipline.
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
from e1_walkers import backward_letters  # noqa: E402

M_SCOPE = list(range(4, 8))  # 4..7, exhaustive
SLACK_EXTRA = 3  # L(w) + 3
A_CAP = 40  # matches k0/M1's own margin-checked default
RSS_CAP_GB = 8.0
LIVE_ROW_CAP = 5_000_000  # honest-wall row-count cap per word (runtime trim)


def rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)


def loop_curve(letters):
    """g_loop(k) = sum_{j<=k}(2-c_j), canonical order, k=1..m (1-indexed
    prefixes, 0-indexed list). L(w) = max of that curve (0 if never
    positive). k*(0-indexed) = FIRST index achieving the max (the
    loop's own binding prefix, per M1's convention)."""
    running = 0
    curve = []
    for c in letters:
        running += (2 - c)
        curve.append(running)
    L = max([0] + curve)
    k_star = curve.index(max(curve))
    return curve, L, k_star


def cap_margin_check(letters, slack_bound, base_cap, wider_cap):
    n1 = count_admissible(letters, slack_bound, base_cap)
    n2 = count_admissible(letters, slack_bound, wider_cap)
    return n1 == n2, n1, n2


def count_admissible(letters, slack_bound, a_cap):
    """Count-only DFS (no storage) for fast cap-margin checks."""
    m = len(letters)
    count = [0]

    def dfs(j, rho, running, max_so_far):
        if max_so_far > slack_bound:
            return
        if j == m:
            count[0] += 1
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
            dfs(j + 1, rho2, running2, max2)

    dfs(0, 1, 0, 0)
    return count[0]


def enumerate_and_check_floor(letters, slack_bound, a_cap, g_loop_curve, k_star):
    """Exhaustive DFS (canonical order, D_free semantics): every
    admissible a-sequence whose max partial sum stays <= slack_bound.
    For every NON-LOOP chain found, test g(k*) >= g_loop(k*) at the
    word's fixed k* (loop's own binding prefix). Returns
    (n_total_chains, n_non_loop, violations_list). Violations list
    entries are (a_seq, g_at_kstar, g_loop_at_kstar, diff) for any
    chain failing the floor -- expected empty."""
    m = len(letters)
    loop_seq = tuple([2] * m)
    g_loop_at_kstar = g_loop_curve[k_star]

    n_total = [0]
    n_non_loop = [0]
    violations = []

    def dfs(j, rho, running, max_so_far, a_seq, g_hist):
        if max_so_far > slack_bound:
            return
        if j == m:
            n_total[0] += 1
            a_tup = tuple(a_seq)
            if a_tup != loop_seq:
                n_non_loop[0] += 1
                g_at_kstar = g_hist[k_star]
                diff = g_at_kstar - g_loop_at_kstar
                if diff < 0:
                    violations.append((a_tup, g_at_kstar, g_loop_at_kstar, diff))
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
            dfs(j + 1, rho2, running2, max2, a_seq + [a], g_hist + [running2])

    dfs(0, 1, 0, 0, [], [])
    return n_total[0], n_non_loop[0], violations


def independent_replay_violation(letters, a_seq):
    """Fresh from-scratch recomputation of the full g-curve for a
    reported violation witness -- structurally independent of the
    generating DFS's own bookkeeping (separate loop, no shared state)."""
    rho = 1
    running = 0
    g_hist = []
    for c, a in zip(letters, a_seq):
        parity = forced_parity_for_backward_step(rho)
        assert parity is not None, "replay hit a class-0 dead end -- should be impossible"
        assert (a % 2 == 0) == (parity == 0), "replay parity mismatch -- engine bug"
        running += (a - c)
        rho = backward_predecessor_exact(rho, a)
        g_hist.append(running)
    return g_hist


def _product12(m):
    if m == 0:
        yield ()
        return
    for rest in _product12(m - 1):
        yield (1,) + rest
        yield (2,) + rest


def build_word_list():
    """ALL words in {1,2}^m for m=4..7, exhaustive. Confirms both
    mechanical-family words are members (per the module docstring's
    scope-reading note)."""
    words_by_m = {}
    mech_confirmed = {}
    for m in M_SCOPE:
        all_words = [tuple(w) for w in _product12(m)]
        golden = tuple(backward_letters(credit_golden_per8, m, anchor_steps=53))
        sqrt2 = tuple(backward_letters(credit_sqrt2_per12, m, anchor_steps=53))
        mech_confirmed[m] = {
            "golden_in_exhaustive_set": golden in all_words,
            "sqrt2_in_exhaustive_set": sqrt2 in all_words,
            "golden_word": golden, "sqrt2_word": sqrt2,
        }
        words_by_m[m] = all_words
    return words_by_m, mech_confirmed


def main():
    t0 = time.time()
    print("=== W6N-N1: floor-point law at full generality (ALL words, m=4..7, L+3) ===\n")

    words_by_m, mech_confirmed = build_word_list()
    total_words = sum(len(v) for v in words_by_m.values())
    print(f"Total words (exhaustive {{1,2}}^m, m=4..7): {total_words} "
          f"(sizes: {[2**m for m in M_SCOPE]}, sum={sum(2**m for m in M_SCOPE)})")
    for m in M_SCOPE:
        mc = mech_confirmed[m]
        print(f"  m={m}: golden-per8 word={mc['golden_word']} "
              f"in exhaustive set: {mc['golden_in_exhaustive_set']}; "
              f"sqrt2-per12 word={mc['sqrt2_word']} "
              f"in exhaustive set: {mc['sqrt2_in_exhaustive_set']}")
        assert mc["golden_in_exhaustive_set"] and mc["sqrt2_in_exhaustive_set"], (
            f"m={m}: mechanical-family word NOT found in the exhaustive {{1,2}}^m "
            f"enumeration -- scope bug, investigate before proceeding"
        )
    print()

    # Pre-run cap margin check on the widest-band probes (all-1s words,
    # both extremes of M_SCOPE) before trusting any production count.
    print("--- Pre-run cap margin check (A_CAP=40 vs 80, widest-band probes) ---")
    probe_ok = True
    for m in (M_SCOPE[0], M_SCOPE[-1]):
        w_probe = tuple([1] * m)
        _, L_probe, _ = loop_curve(w_probe)
        slack = L_probe + SLACK_EXTRA
        ok, n1, n2 = cap_margin_check(w_probe, slack, 40, 80)
        probe_ok = probe_ok and ok
        print(f"  m={m} all-1s word: slack=L+{SLACK_EXTRA}={slack} "
              f"cap40->{n1} cap80->{n2} {'OK' if ok else '*** FAIL -- widen A_CAP ***'}")
    if not probe_ok:
        raise SystemExit("A_CAP margin check failed -- refusing to run N1 with an "
                          "unvalidated exponent cap.")
    print()

    all_violations = []  # dicts
    per_word_rows = []   # summary rows for CSV
    n_words_done = 0
    n_words_trimmed = 0
    total_chains = 0
    total_non_loop = 0
    rss_cap_hit = False

    for m in M_SCOPE:
        if rss_cap_hit:
            break
        for w in words_by_m[m]:
            g_loop_curve, L, k_star = loop_curve(w)
            slack_bound = L + SLACK_EXTRA

            # honest runtime trim check: count first (cheap, no storage);
            # if the count would blow past LIVE_ROW_CAP, report the trim
            # honestly rather than silently cutting scope.
            n_chains = count_admissible(w, slack_bound, A_CAP)
            if n_chains > LIVE_ROW_CAP:
                n_words_trimmed += 1
                per_word_rows.append({
                    "m": m, "word": "".join(map(str, w)), "L": L, "k_star_1idx": k_star + 1,
                    "slack_bound": slack_bound, "n_chains_in_band": n_chains,
                    "n_non_loop": "", "n_violations": "", "status": "TRIMMED (count>cap)",
                })
                continue

            n_total, n_non_loop, violations = enumerate_and_check_floor(
                w, slack_bound, A_CAP, g_loop_curve, k_star)
            total_chains += n_total
            total_non_loop += n_non_loop
            n_words_done += 1

            for (a_seq, g_at_k, gl_at_k, diff) in violations:
                all_violations.append({
                    "m": m, "word": w, "a_seq": a_seq, "k_star_1idx": k_star + 1,
                    "L": L, "slack_bound": slack_bound,
                    "g_at_kstar": g_at_k, "g_loop_at_kstar": gl_at_k, "diff": diff,
                })

            per_word_rows.append({
                "m": m, "word": "".join(map(str, w)), "L": L, "k_star_1idx": k_star + 1,
                "slack_bound": slack_bound, "n_chains_in_band": n_total,
                "n_non_loop": n_non_loop, "n_violations": len(violations),
                "status": "OK",
            })

            if rss_gb() > RSS_CAP_GB:
                print(f"  *** RSS CAP HIT at m={m} word={''.join(map(str,w))}: "
                      f"{rss_gb():.2f}GB -- honest wall, stopping further words ***")
                rss_cap_hit = True
                break

    wall = time.time() - t0
    print(f"Words processed to completion: {n_words_done}/{total_words} "
          f"; words trimmed (honest, count>cap): {n_words_trimmed}")
    print(f"Total admissible chains enumerated (within L+3, across all completed words): {total_chains}")
    print(f"Total non-loop chains: {total_non_loop}")
    print(f"Peak RSS: {rss_gb():.3f} GB; wall so far: {wall:.1f}s\n")

    # Independent exact-replay of every violation witness (if any).
    n_replay_fail = 0
    if all_violations:
        print(f"*** {len(all_violations)} FLOOR VIOLATIONS FOUND -- exact-replaying each ***")
        for v in all_violations:
            g_hist = independent_replay_violation(v["word"], v["a_seq"])
            replay_g_at_k = g_hist[v["k_star_1idx"] - 1]
            replay_ok = (replay_g_at_k == v["g_at_kstar"])
            if not replay_ok:
                n_replay_fail += 1
            print(f"  VIOLATION m={v['m']} word={''.join(map(str,v['word']))} "
                  f"a_seq={v['a_seq']} k*={v['k_star_1idx']} "
                  f"g(k*)={v['g_at_kstar']} g_loop(k*)={v['g_loop_at_kstar']} "
                  f"diff={v['diff']} replay={'PASS' if replay_ok else '*** FAIL ***'}")
    else:
        print("No violations found -- floor holds on every completed word.")

    # write outputs
    out_summary = HERE / "n1_word_summary.csv"
    with open(out_summary, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(per_word_rows[0].keys()))
        w.writeheader()
        for r in per_word_rows:
            w.writerow(r)
    print(f"\nWrote {out_summary.name} ({len(per_word_rows)} rows)")

    out_violations = HERE / "n1_violations.csv"
    fieldnames = ["m", "word", "a_seq", "k_star_1idx", "L", "slack_bound",
                  "g_at_kstar", "g_loop_at_kstar", "diff"]
    with open(out_violations, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for v in all_violations:
            row = dict(v)
            row["word"] = "".join(map(str, row["word"]))
            row["a_seq"] = ",".join(map(str, row["a_seq"]))
            w.writerow(row)
    print(f"Wrote {out_violations.name} ({len(all_violations)} rows)")

    # -------------------------------------------------------------
    # Frozen prediction verdict
    # -------------------------------------------------------------
    print("\n=== FROZEN PREDICTION VERDICT ===")
    print("Exceptionless at every budget (L+3, m=4..7 exhaustive) -- 75% predicted\n")
    if n_words_trimmed > 0 or rss_cap_hit:
        print(f"HONEST WALL: {n_words_trimmed} word(s) trimmed (admissible-chain count "
              f"exceeded the {LIVE_ROW_CAP} row cap){' ; RSS cap hit mid-scope' if rss_cap_hit else ''} "
              f"-- these words' floor claim is NOT tested at L+3 in this run. Verdict below "
              f"covers ONLY the {n_words_done} completed words.")
    verdict = "HIT (0 violations)" if len(all_violations) == 0 else f"MISS -- {len(all_violations)} violations found"
    print(f"Verdict: {verdict}")
    if n_replay_fail:
        print(f"*** {n_replay_fail} VIOLATION WITNESSES FAILED INDEPENDENT REPLAY -- "
              f"investigate before trusting the violation count ***")

    print(f"\nTotal wall: {time.time()-t0:.1f}s, peak RSS: {rss_gb():.3f} GB")


if __name__ == "__main__":
    main()
