#!/usr/bin/env python3
"""
W6O-O1 -- The one-point lemma (W6N-N2/N4c's N2 finding, DERIVATION_NOTES
sec 14a) exhaustively over the REAL domain, per W6O_LEMMA_SCALE_ORDER.md
section O1.

LEMMA UNDER TEST (DERIVATION_NOTES 14a, N2's exact form): for a word w
with binding prefix k* (the loop's own argmax index), every
parity-legal k*-step backward walk from rho=1 satisfies
g(k*) >= g_loop(k*) = L(w) -- FROM THE MOD-3^k* CONGRUENCE ALONE (no
suffix-completability check; N2 already showed the congruence-only
prefix space's minimum equals g_loop(k*) exactly, on 40/40 sampled
words). THIS round scales the empirical base from "40 sampled words"
to the domain that actually matters for the proof:

  (i)   every k*-PREFIX of the TRUE word's OWN windows, m=2..53
        (canonical order, end-anchored at absolute step 53, matching
        e1_walkers.backward_letters/credit_true exactly -- the real
        system's actual measured object, not a sample of it);
  (ii)  every k*-prefix of BOTH mechanical families (golden-per8,
        sqrt2-per12), m=2..2q (q=8 for golden -> m=2..16; q=12 for
        sqrt2 -> m=2..24) -- one full period beyond the 28-row
        ground-truth table, so k* itself can cross a period boundary
        at least once per family;
  (iii) ALL {1,2}^m words, m<=12, EXHAUSTIVE, each word played AS ITS
        OWN k*-prefix directly (i.e. k*=m, the word's own full length
        -- "exhaustive" here subsumes N2's random sampling entirely:
        every {1,2} word up to length 12 is tested, not a sample of
        them). This is the domain that dominates cost (2^12=4096 words
        at length 12) and is run separately from (i)/(ii) for clarity.

For EACH prefix tested: compute g_loop(k*) = L(prefix) (all-2s
running-sum max over the prefix itself, since the prefix here IS
the k*-window whose own loop value is being tested against), then
branch-and-bound the TRUE MINIMUM of max_{j<=k*} g(j) over ALL
parity-legal (mod-3^k*, congruence-only, no suffix-feasibility check)
k*-step exponent sequences from rho=1 -- this reuses and extends the
w6n/n2_prefix_congruence_mechanism.py branch-and-bound primitive (same
DFS: prune the instant running max-so-far reaches or exceeds the best
complete value found; sound because max_so_far is monotone
nondecreasing along any extension). Cap-margin checked (A_CAP=40 vs
80) on every prefix, exactly as N2/K0/M1 all do for their own DFS
width.

IMPORTANT SCOPING NOTE on (i)/(ii)'s "prefix": the order says "every
BINDING prefix of the true word's windows ... for m=2..53" -- read
literally, per word-length m, there is exactly ONE binding prefix (the
loop's own argmax k* for that m-window), so (i) is 52 tests (m=2..53)
and (ii) is 2 families x (2q-1) tests each = 15+23=38 tests, not an
enumeration of every possible sub-prefix length. This matches N2's own
per-word convention (one k* per word) and is stated explicitly to
avoid silently inflating or shrinking scope.

HONEST WALL NOTE (stated up front, per the order's own text pointing at
n2's "killed 20^k* brute force" note): the TRUE MINIMUM search here is
NOT full 20^k* materialization (that was N2's own already-abandoned
naive approach, killed explicitly in its docstring past k*~7); it is
the SAME branch-and-bound used throughout W6K/W6L/W6M/W6N (prune the
moment a branch cannot possibly improve on the best complete answer
found so far). This stays fast because g_loop(k*) is usually a tight
bound the DFS converges towards quickly; a per-prefix wall-clock
budget is still enforced and any k* that walls is reported as an
honest partial, not silently skipped.

Frozen prediction (Fable): min = g_loop(k*) on 100% - 85%. Any breach:
exact-replay, dump, lead the digest -- an O1 breach would falsify the
lemma BEFORE any proof effort is spent, which is the entire point of
this round (see order's own text, verbatim).

INSTRUMENT RULE (binding, W6K/W6L/W6M/W6N house convention): Path C
only (parity-forced backward DFS, D_free/ceiling-off semantics,
canonical order, index 0 = nearest terminal). Every reported minimum's
argmin exponent sequence is independently exact-replayed in-process
(fresh from-scratch application of engine.backward_predecessor_exact,
not reusing the generating DFS's own bookkeeping) before being
trusted, per the W6L/W6M/W6N discipline.

NOTE ON REUSE (deliberate, per the order's instruction to "reuse/
extend w6n/n2 machinery"): the DFS core below is intentionally close
in shape to n2_prefix_congruence_mechanism.min_prefix_cost_and_argmin
-- this is the specified extension target, not an accidental
duplication.
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
W6N = UNDERLOCK / "w6n"
sys.path.insert(0, str(UNDERLOCK))
sys.path.insert(0, str(W6E))
sys.path.insert(0, str(W6N))

from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402
from underlock_words import credit_golden_per8, credit_sqrt2_per12  # noqa: E402
from e1_walkers import backward_letters, credit_true  # noqa: E402

A_CAP = 40
WIDER_CAP = 80
RSS_CAP_GB = 8.0
PER_PREFIX_WALLCLOCK_CAP_S = 60.0  # honest-wall per prefix (branch-and-bound, expected sub-second)


def rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)


def loop_curve_and_L(letters):
    """g_loop(k) for k=1..len(letters) (canonical order, all-2s chain).
    L = max of the curve (this IS g_loop(k*) since k* is the argmax)."""
    running = 0
    curve = []
    for c in letters:
        running += (2 - c)
        curve.append(running)
    L = max([0] + curve)
    k_star_0idx = curve.index(max(curve)) if curve else 0
    return curve, L, k_star_0idx


def min_prefix_cost_and_argmin(letters_prefix, a_cap, wallclock_cap=None):
    """TRUE MINIMUM of max_{j<=k} g(j) over ALL parity-legal (mod-3^k
    congruence only) k=len(letters_prefix)-step exponent sequences from
    rho=1. Branch-and-bound DFS: prune the instant a branch's running
    max-so-far reaches or exceeds the best COMPLETE value found so far
    (sound: max_so_far is monotone nondecreasing along any extension of
    that branch, so it can never beat an already-found complete
    answer). Returns (min_cost, argmin_a_seq, argmin_rho_end,
    wall_hit)."""
    k = len(letters_prefix)
    best = [None, None, None]
    t0 = time.time()
    node_count = [0]
    wall_hit = [False]

    def dfs(j, rho, running, max_so_far, a_seq):
        if wall_hit[0]:
            return
        node_count[0] += 1
        if wallclock_cap is not None and (node_count[0] & 0xFFF) == 0 and time.time() - t0 > wallclock_cap:
            wall_hit[0] = True
            return
        if best[0] is not None and max_so_far >= best[0]:
            return
        if j == k:
            if best[0] is None or max_so_far < best[0]:
                best[0], best[1], best[2] = max_so_far, tuple(a_seq), rho
            return
        c = letters_prefix[j]
        parity = forced_parity_for_backward_step(rho)
        if parity is None:
            return
        a_min = 2 if parity == 0 else 1
        for a in range(a_min, a_min + a_cap, 2):
            running2 = running + (a - c)
            rho2 = backward_predecessor_exact(rho, a)
            dfs(j + 1, rho2, running2, max(max_so_far, running2), a_seq + [a])

    dfs(0, 1, 0, 0, [])
    return best[0], best[1], best[2], wall_hit[0]


def cap_margin_check(letters_prefix, base_cap, wider_cap, wallclock_cap=None):
    min1, _, _, w1 = min_prefix_cost_and_argmin(letters_prefix, base_cap, wallclock_cap)
    min2, _, _, w2 = min_prefix_cost_and_argmin(letters_prefix, wider_cap, wallclock_cap)
    return (min1 == min2 and not w1 and not w2), min1, min2, (w1 or w2)


def independent_replay(letters_prefix, a_seq):
    """Fresh from-scratch recomputation, structurally independent of
    the generating DFS (separate loop, no shared state) -- the
    W6L/W6M/W6N exact-replay discipline."""
    rho = 1
    running = 0
    max_so_far = 0
    for c, a in zip(letters_prefix, a_seq):
        parity = forced_parity_for_backward_step(rho)
        assert parity is not None, "replay hit class-0 dead end -- should be impossible mid-legal-sequence"
        assert (a % 2 == 0) == (parity == 0), "replay parity mismatch -- engine bug"
        running += (a - c)
        max_so_far = max(max_so_far, running)
        rho = backward_predecessor_exact(rho, a)
    return max_so_far, rho


def _product12(m):
    if m == 0:
        yield ()
        return
    for rest in _product12(m - 1):
        yield (1,) + rest
        yield (2,) + rest


def test_one_prefix(letters, label, rows, breaches, wall_rows, do_replay=True):
    """Core test for a single prefix `letters` (this prefix IS the
    k*-window: k*=len(letters)). Returns True if this prefix hit a
    per-prefix wall (honest partial)."""
    m = len(letters)
    _, L, k_star0 = loop_curve_and_L(letters)
    g_loop_kstar = L  # since k*=argmax, g_loop(k*)=L by construction

    margin_ok, min1, min2, margin_wall = cap_margin_check(
        letters, A_CAP, WIDER_CAP, PER_PREFIX_WALLCLOCK_CAP_S)

    if margin_wall:
        wall_rows.append({"label": label, "m": m, "reason": "cap-margin wallclock cap hit"})
        rows.append({"label": label, "m": m, "L": L, "min_cost": "", "hit_loop": "",
                     "cap_margin_ok": "WALL", "status": "WALL"})
        return True

    if not margin_ok:
        raise SystemExit(f"A_CAP margin FAIL for {label} m={m}: min@40={min1} min@80={min2}")

    min_cost, argmin_a_seq, argmin_rho, wall_hit = min_prefix_cost_and_argmin(
        letters, A_CAP, PER_PREFIX_WALLCLOCK_CAP_S)

    if wall_hit:
        wall_rows.append({"label": label, "m": m, "reason": "production wallclock cap hit"})
        rows.append({"label": label, "m": m, "L": L, "min_cost": "", "hit_loop": "",
                     "cap_margin_ok": True, "status": "WALL"})
        return True

    hit_loop = (min_cost == g_loop_kstar)
    breach = min_cost < g_loop_kstar
    over = min_cost > g_loop_kstar  # should be impossible: loop itself is always admissible

    replay_ok = None
    if do_replay:
        replay_cost, replay_rho = independent_replay(letters, argmin_a_seq)
        replay_ok = (replay_cost == min_cost and replay_rho == argmin_rho)

    if breach:
        breaches.append({
            "label": label, "m": m, "word": "".join(map(str, letters)),
            "L": L, "min_cost": min_cost, "argmin_a_seq": argmin_a_seq,
            "argmin_rho_end": argmin_rho, "replay_ok": replay_ok,
        })

    rows.append({
        "label": label, "m": m, "word": "".join(map(str, letters)) if m <= 16 else f"<{m} letters>",
        "L": L, "min_cost": min_cost, "hit_loop": hit_loop, "breach": breach,
        "over_loop_impossible_check": over, "cap_margin_ok": margin_ok,
        "replay_ok": replay_ok, "status": "OK",
    })
    return False


def main():
    t0 = time.time()
    print("=== W6O-O1: the one-point lemma exhaustively over the real domain ===\n")
    print("Sanity: loop fixed point --", backward_predecessor_exact(1, 2) == 1)
    assert backward_predecessor_exact(1, 2) == 1

    rows = []
    breaches = []
    wall_rows = []

    # ------------------------------------------------------------------
    # (i) True word's own windows, m=2..53 (canonical, end-anchored)
    # ------------------------------------------------------------------
    print("--- (i) True word windows, m=2..53 (end-anchored at absolute step 53) ---")
    for m in range(2, 54):
        letters = backward_letters(credit_true, m, anchor_steps=53)
        walled = test_one_prefix(letters, "true-word", rows, breaches, wall_rows)
        status = "WALL" if walled else "ok"
        if m % 10 == 0 or m in (2, 53) or walled:
            print(f"  m={m:2d} true-word: {status}")
    print(f"  done: m=2..53 ({53-2+1} prefixes)\n")

    # ------------------------------------------------------------------
    # (ii) Both mechanical families, m=2..2q
    # ------------------------------------------------------------------
    print("--- (ii) Mechanical families, m=2..2q ---")
    families = [
        ("golden-per8", credit_golden_per8, 8),
        ("sqrt2-per12", credit_sqrt2_per12, 12),
    ]
    for fam_label, credit_fn, q in families:
        m_max = 2 * q
        print(f"  {fam_label}: m=2..{m_max}")
        for m in range(2, m_max + 1):
            letters = backward_letters(credit_fn, m, anchor_steps=53)
            walled = test_one_prefix(letters, fam_label, rows, breaches, wall_rows)
            if walled:
                print(f"    m={m}: WALL")
        print(f"  done: {fam_label} m=2..{m_max} ({m_max-2+1} prefixes)")
    print()

    # ------------------------------------------------------------------
    # (iii) ALL {1,2}^m words, m<=12, exhaustive, each as its own
    # k*-prefix (k*=m)
    # ------------------------------------------------------------------
    print("--- (iii) ALL {1,2}^m words, m<=12, exhaustive (each word = its own k*-prefix) ---")
    n_words_total = sum(2 ** m for m in range(1, 13))
    print(f"  total word count (m=1..12): {n_words_total}")
    n_done = 0
    n_walled = 0
    rss_cap_hit = False
    for m in range(1, 13):
        if rss_cap_hit:
            break
        n_this_m = 0
        for w in _product12(m):
            walled = test_one_prefix(list(w), f"exhaustive-m{m}", rows, breaches, wall_rows,
                                      do_replay=True)
            n_done += 1
            n_this_m += 1
            if walled:
                n_walled += 1
            if rss_gb() > RSS_CAP_GB:
                print(f"  *** RSS CAP HIT at m={m}, word #{n_this_m}: {rss_gb():.2f}GB "
                      f"-- honest wall, stopping further words ***")
                rss_cap_hit = True
                break
        print(f"  m={m:2d}: {n_this_m} words done" + (" (RSS-capped mid-m)" if rss_cap_hit else ""))
    print(f"  exhaustive scope: {n_done}/{n_words_total} words tested, {n_walled} per-word walls, "
          f"RSS-cap-hit={rss_cap_hit}\n")

    # ------------------------------------------------------------------
    # Any breach: exact-replay + dump + lead (per order's binding text)
    # ------------------------------------------------------------------
    n_breach_replay_fail = 0
    if breaches:
        print(f"\n*** {len(breaches)} BREACHES FOUND -- min_prefix_cost < g_loop(k*) ***")
        for b in breaches:
            print(f"  BREACH label={b['label']} m={b['m']} word={b['word']} "
                  f"L={b['L']} min_cost={b['min_cost']} argmin={b['argmin_a_seq']} "
                  f"replay_ok={b['replay_ok']}")
            if not b["replay_ok"]:
                n_breach_replay_fail += 1
    else:
        print("No breaches: min_prefix_cost == g_loop(k*) on every prefix tested "
              "(modulo any honest walls reported above).")

    n_total = len(rows)
    n_wall = len(wall_rows)
    n_ok = sum(1 for r in rows if r["status"] == "OK")
    n_hit = sum(1 for r in rows if r["status"] == "OK" and r["hit_loop"])
    n_over = sum(1 for r in rows if r["status"] == "OK" and r.get("over_loop_impossible_check"))

    print(f"\nTotals: {n_total} prefixes attempted, {n_ok} completed, {n_wall} honest walls, "
          f"{len(breaches)} breaches.")
    if n_over:
        print(f"*** {n_over} prefixes show min_cost > g_loop(k*) -- SHOULD BE IMPOSSIBLE "
              f"(the all-2s loop chain is always itself admissible, so min <= g_loop(k*) "
              f"always) -- this would indicate an engine bug, investigate ***")

    # write outputs
    out_main = HERE / "o1_lemma_scale_domain.csv"
    fieldnames = ["label", "m", "word", "L", "min_cost", "hit_loop", "breach",
                  "over_loop_impossible_check", "cap_margin_ok", "replay_ok", "status"]
    with open(out_main, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            row = {k: r.get(k, "") for k in fieldnames}
            w.writerow(row)
    print(f"\nWrote {out_main.name} ({len(rows)} rows)")

    if breaches:
        out_breach = HERE / "o1_breaches.csv"
        breach_fields = ["label", "m", "word", "L", "min_cost", "argmin_a_seq",
                          "argmin_rho_end", "replay_ok"]
        with open(out_breach, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=breach_fields)
            w.writeheader()
            for b in breaches:
                row = dict(b)
                row["argmin_a_seq"] = ",".join(map(str, row["argmin_a_seq"]))
                w.writerow(row)
        print(f"Wrote {out_breach.name} ({len(breaches)} rows)")

    if wall_rows:
        out_wall = HERE / "o1_honest_walls.csv"
        with open(out_wall, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["label", "m", "reason"])
            w.writeheader()
            for r in wall_rows:
                w.writerow(r)
        print(f"Wrote {out_wall.name} ({len(wall_rows)} rows)")

    # -------------------------------------------------------------
    # Frozen prediction verdict
    # -------------------------------------------------------------
    print("\n=== FROZEN PREDICTION VERDICT ===")
    print("min = g_loop(k*) on 100% -- 85% predicted\n")
    frac_hit = n_hit / n_ok if n_ok else 0.0
    print(f"Fraction hitting g_loop(k*) exactly (of {n_ok} completed, non-walled prefixes): "
          f"{n_hit}/{n_ok} = {100*frac_hit:.4f}%")
    if breaches and n_breach_replay_fail == 0:
        verdict = f"BREACH CONFIRMED -- {len(breaches)} exact-replayed breach(es), LEMMA FALSIFIED at scale"
    elif breaches and n_breach_replay_fail > 0:
        verdict = (f"BREACH CANDIDATE(S) FOUND BUT {n_breach_replay_fail} FAILED REPLAY -- "
                   f"instrument bug suspected, NOT a confirmed falsification; investigate")
    elif frac_hit == 1.0:
        verdict = "HIT -- 100% exact, exceeding the 85% frozen prediction"
    else:
        verdict = f"MISS -- {100*frac_hit:.4f}% (below 100%, no breach found -- see status column for cause)"
    print(f"Verdict: {verdict}")

    print(f"\nTotal wall: {time.time()-t0:.1f}s, peak RSS: {rss_gb():.3f} GB")


if __name__ == "__main__":
    main()
