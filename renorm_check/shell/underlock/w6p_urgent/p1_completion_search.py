#!/usr/bin/env python3
"""
W6P-URGENT -- does D=L survive at the true word's m=29 window (and
sqrt2-per12 m=24), or does universality itself break?

BACKGROUND (read fast, see ledger W6O-O1 + DERIVATION_NOTES sec 14):
O1 found that the parity/congruence-only backward DFS (D_free
semantics, no ceiling check) achieves a full m=29-length admissible
chain with max partial sum g=11, strictly below the loop's own value
L=g_loop(k*)=12 (k* here is the CURVE PEAK position, which for m=29
happens to sit at the FAR end of the window, k*=m=29 -- so O1's
"k*-prefix" DFS over the whole word already covers the entire window;
there is no separate suffix beyond it to complete WITHIN the window
itself). The open question O1 explicitly left unresolved: O1 ran
D_free (no g(k)>=0 prefix constraint enforced during search) -- is
the breach witness also D_ceil-LEGAL (g(k)>=0 at every prefix, the
house's own canonical convention per w6k/k0_canonical_engine.py), and
does the breach survive an INDEPENDENT from-scratch true-minimum
search under full D_ceil semantics (not just a post-hoc check of one
witness)?

THIS SCRIPT (independent implementation -- does NOT import or share
state with w6o/o1_lemma_exhaustive_domain.py or e1_walkers.py; only
reuses the two tiny validated residue-arithmetic primitives from
w6e/engine.py, which are pure facts about the residue map, exactly
per the W6K/W6L/W6M/W6N house discipline for cross-checks):

  1. Recompute the true-word m=29 window and sqrt2-per12 m=24 window
     from scratch (own credit-letter formula, own backward_letters
     construction), cross-checked against W6O's own word/letters for
     byte-identical agreement.
  2. Recompute the breach witness's own chain from the W6O dump and
     independently exact-replay it (fresh parity/residue walk).
  3. Check D_ceil legality of that witness (g(k)>=0 at every prefix,
     the house canonical constraint) -- own computation, not reused.
  4. INDEPENDENT branch-and-bound true minimum under FULL D_ceil
     semantics (ceiling_on=True, own DFS, own pruning argument stated
     and justified) over the WHOLE m-length window (since k*=m here,
     this IS the "search for a legal completion" the order asks for --
     there is no shorter k*<m sub-prefix to extend for these specific
     cells, a fact independently re-derived below, not assumed).
  5. Upper-bound sanity: the all-2s loop chain achieves exactly L.
  6. Verdict: D_ceil-true-min < L (universality breaks, lead with
     replayed counterexample) or D_ceil-true-min == L (D=L survives;
     report where/why the D_free-only witnesses fail ceiling
     legality, if they do -- or, if they stay ceiling-legal too,
     report that explicitly, since that would mean the breach is
     real under BOTH semantics).

Exact integer arithmetic throughout; no floats. Sound pruning: in a
DFS that tracks (max_so_far, min_so_far implicitly via ceiling_on
check inline), max_so_far is monotone nondecreasing along any
extension of a branch, so pruning any branch whose max_so_far already
equals-or-exceeds the best complete value found so far is sound
(exactly the W6K/W6N argument, re-derived here for this independent
implementation, not copy-pasted).
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
W6O = UNDERLOCK / "w6o"
sys.path.insert(0, str(W6E))

# Only the two tiny validated residue-arithmetic primitives are reused
# (pure facts about the mod-3 residue map / exact backward division,
# not part of what this independent check is testing).
from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402

A_CAP = 40
WIDER_CAP = 80
WALLCLOCK_CAP_S = 300.0
RSS_CAP_GB = 8.0


def rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)


# ---------------------------------------------------------------------
# Own, from-scratch credit-letter / window construction (independent of
# e1_walkers.py, cross-checked against it below for agreement).
# ---------------------------------------------------------------------

def credit_true_own(k: int) -> int:
    """True word: c_k = floor((k+1)log2(3)) - floor(k log2(3)), computed
    via exact bit_length on 3**k (no floats)."""
    def floor_klog2_3(kk: int) -> int:
        if kk == 0:
            return 0
        return (3 ** kk).bit_length() - 1
    return floor_klog2_3(k + 1) - floor_klog2_3(k)


def credit_sqrt2_per12_own(k: int) -> int:
    """sqrt2-per12 mechanical word: c_k = floor(17(k+1)/12) - floor(17k/12)."""
    return (17 * (k + 1)) // 12 - (17 * k) // 12


def backward_letters_own(credit_fn, m: int, anchor_steps: int = 53):
    """Own construction of the canonical, end-anchored backward-order
    letters: index 0 = letter nearest the terminal (c_{anchor_steps-1}),
    index m-1 = farthest (c_{anchor_steps-m}). Independently written,
    same convention as e1_walkers.backward_letters (cross-checked
    below, not assumed)."""
    return [credit_fn(anchor_steps - 1 - j) for j in range(m)]


# ---------------------------------------------------------------------
# Loop curve / L (own computation)
# ---------------------------------------------------------------------

def loop_curve_and_L(letters):
    running = 0
    curve = []
    for c in letters:
        running += (2 - c)
        curve.append(running)
    L = max([0] + curve)
    k_star_0idx = curve.index(max(curve)) if curve else 0
    return curve, L, k_star_0idx


# ---------------------------------------------------------------------
# Independent exact replay of a given a-sequence (parity + D_ceil check)
# ---------------------------------------------------------------------

def replay_chain(letters, a_seq):
    """Fresh, from-scratch replay: track rho exactly, verify parity
    legality at every step, compute g(k) (backward running sum) at
    every prefix k=0..m. Returns (g_sequence, final_rho, all_parity_ok)."""
    rho = 1
    running = 0
    g_seq = [0]
    for c, a in zip(letters, a_seq):
        parity = forced_parity_for_backward_step(rho)
        assert parity is not None, "replay hit class-0 dead end -- should be impossible mid-legal-sequence"
        if (a % 2 == 0) != (parity == 0):
            return g_seq, rho, False
        running += (a - c)
        g_seq.append(running)
        rho = backward_predecessor_exact(rho, a)
    return g_seq, rho, True


def d_ceil_legal(g_seq) -> bool:
    """House canonical constraint: g(k) >= 0 at every prefix k
    (w6k/k0_canonical_engine.py's ceiling_on=True)."""
    return all(g >= 0 for g in g_seq)


# ---------------------------------------------------------------------
# Independent branch-and-bound: TRUE MINIMUM over the WHOLE m-window,
# under FULL D_ceil semantics (ceiling_on=True): parity-forced a at
# every step, AND g(k) >= 0 required at every prefix k (not just
# checked post-hoc on one witness -- this is a from-scratch search).
# ---------------------------------------------------------------------

def min_full_window_d_ceil(letters, a_cap, wallclock_cap=None):
    """Branch-and-bound true minimum of max_k g(k) over ALL admissible
    (parity-forced AND g(k)>=0-at-every-prefix) length-m exponent
    sequences from rho=1. Sound pruning: max_so_far is monotone
    nondecreasing along any DFS extension of a branch, so a branch
    whose max_so_far already >= the best complete value found so far
    can never improve on it -- prune. The g(k)>=0 constraint is
    enforced INLINE (branches going negative are cut immediately, not
    just flagged) -- this is the ceiling_on=True search, independent
    of w6k/k0_canonical_engine.canonical_D (own implementation, cross-
    checked against it below on small words for agreement, not
    imported)."""
    m = len(letters)
    best = [None, None]
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
        if j == m:
            if best[0] is None or max_so_far < best[0]:
                best[0], best[1] = max_so_far, tuple(a_seq)
            return
        c = letters[j]
        parity = forced_parity_for_backward_step(rho)
        if parity is None:
            return  # genuine class-0 dead end -- this branch is infeasible, not a wall
        a_min = 2 if parity == 0 else 1
        for a in range(a_min, a_min + a_cap, 2):
            running2 = running + (a - c)
            if running2 < 0:
                continue  # D_ceil constraint: g(k)>=0 required at every prefix -- prune infeasible branch
            rho2 = backward_predecessor_exact(rho, a)
            dfs(j + 1, rho2, running2, max(max_so_far, running2), a_seq + [a])

    dfs(0, 1, 0, 0, [])
    return best[0], best[1], wall_hit[0], node_count[0]


def cap_margin_check_d_ceil(letters, base_cap, wider_cap, wallclock_cap=None):
    min1, _, w1, _ = min_full_window_d_ceil(letters, base_cap, wallclock_cap)
    min2, _, w2, _ = min_full_window_d_ceil(letters, wider_cap, wallclock_cap)
    return (min1 == min2 and not w1 and not w2), min1, min2, (w1 or w2)


# ---------------------------------------------------------------------
# Cross-check against w6k's own canonical_D on tiny words (independence
# gate: confirm this from-scratch implementation agrees with the
# house's own K0-gated reference before trusting it on m=29/24).
# ---------------------------------------------------------------------

def cross_check_against_k0():
    sys.path.insert(0, str(UNDERLOCK / "w6k"))
    from k0_canonical_engine import canonical_D  # noqa: E402
    WORDS = {
        "13": (1, 3), "31": (3, 1), "113": (1, 1, 3),
        "311": (3, 1, 1), "123": (1, 2, 3), "321": (3, 2, 1),
    }
    all_ok = True
    lines = []
    for word, canon in WORDS.items():
        for order, letters in [("canonical", canon), ("reverse", tuple(reversed(canon)))]:
            d_k0 = canonical_D(list(letters), ceiling_on=True, a_cap=40)
            d_mine, _, wall, _ = min_full_window_d_ceil(list(letters), 40, None)
            ok = (d_k0 == d_mine) and not wall
            all_ok = all_ok and ok
            lines.append(f"  word={word:4} order={order:9} k0.canonical_D(ceiling_on=True)={d_k0} "
                          f"mine={d_mine} {'OK' if ok else '*** MISMATCH ***'}")
    return all_ok, lines


# ---------------------------------------------------------------------
# Cross-check word construction against W6O's own e1_walkers letters
# ---------------------------------------------------------------------

def cross_check_letters():
    sys.path.insert(0, str(W6E))
    sys.path.insert(0, str(UNDERLOCK))
    from e1_walkers import backward_letters as bl_theirs, credit_true as ct_theirs  # noqa: E402
    from underlock_words import credit_sqrt2_per12 as cs_theirs  # noqa: E402

    ok_true = True
    ok_sqrt2 = True
    for m in [24, 29, 30, 31, 32, 33, 34, 35, 53]:
        mine = backward_letters_own(credit_true_own, m, anchor_steps=53)
        theirs = bl_theirs(ct_theirs, m, anchor_steps=53)
        if mine != theirs:
            ok_true = False
    for m in [24]:
        mine = backward_letters_own(credit_sqrt2_per12_own, m, anchor_steps=53)
        theirs = bl_theirs(cs_theirs, m, anchor_steps=53)
        if mine != theirs:
            ok_sqrt2 = False
    return ok_true, ok_sqrt2


# ---------------------------------------------------------------------
# Load W6O's breach witnesses for the target cells
# ---------------------------------------------------------------------

def load_breach_witnesses():
    witnesses = {}
    with open(W6O / "o1_breaches.csv") as f:
        for row in csv.DictReader(f):
            m = int(row["m"])
            label = row["label"]
            a_seq = tuple(int(x) for x in row["argmin_a_seq"].split(","))
            witnesses[(label, m)] = {
                "L": int(row["L"]), "min_cost": int(row["min_cost"]),
                "a_seq": a_seq, "argmin_rho_end": int(row["argmin_rho_end"]),
            }
    return witnesses


def main():
    t0 = time.time()
    out = []

    def p(s=""):
        print(s)
        out.append(s)

    p("=== W6P-URGENT: does D=L survive at true-word m=29 (and sqrt2-per12 m=24)? ===\n")

    # ------------------------------------------------------------
    # Gate 0: independence cross-checks (must pass before trusting
    # anything downstream)
    # ------------------------------------------------------------
    p("--- Gate 0a: cross-check word construction against W6O's own e1_walkers/underlock_words ---")
    ok_true, ok_sqrt2 = cross_check_letters()
    p(f"  true-word letters (m=24,29..35,53) match W6O's e1_walkers.backward_letters/credit_true: {ok_true}")
    p(f"  sqrt2-per12 letters (m=24) match W6O's underlock_words.credit_sqrt2_per12: {ok_sqrt2}")
    assert ok_true and ok_sqrt2, "GATE 0a FAIL -- word construction disagrees with W6O's own convention"

    p("\n--- Gate 0b: cross-check this D_ceil branch-and-bound against w6k's K0-gated canonical_D ---")
    ok_k0, lines = cross_check_against_k0()
    for line in lines:
        p(line)
    p(f"  ==> Gate 0b: {'PASS' if ok_k0 else 'FAIL'}")
    assert ok_k0, "GATE 0b FAIL -- independent D_ceil DFS disagrees with K0 reference on tiny words"

    # ------------------------------------------------------------
    # Load breach witnesses, sanity loop upper bound
    # ------------------------------------------------------------
    witnesses = load_breach_witnesses()
    target_cells = [
        ("true-word", 29), ("true-word", 30), ("true-word", 31), ("true-word", 32),
        ("true-word", 33), ("true-word", 34), ("true-word", 35),
        ("sqrt2-per12", 24),
    ]

    results = []
    for label, m in target_cells:
        p(f"\n=== CELL: {label} m={m} ===")
        if label == "true-word":
            letters = backward_letters_own(credit_true_own, m, anchor_steps=53)
        else:
            letters = backward_letters_own(credit_sqrt2_per12_own, m, anchor_steps=53)

        curve, L, kstar0 = loop_curve_and_L(letters)
        p(f"  window letters (backward order, idx0=nearest terminal): {''.join(map(str, letters))}")
        p(f"  loop curve g_loop(k): {curve}")
        p(f"  L = g_loop(k*) = {L}, k* (0-idx) = {kstar0} (k* 1-idx = {kstar0+1}, window length m = {m}) "
          f"-- k*==m: {kstar0+1 == m}")

        # Upper bound sanity: the all-2s loop chain achieves EXACTLY L.
        # (a=2 for every letter -> rho stays at 1 forever, the fixed point;
        # g(k) = sum_{j<=k}(2-c_j) = curve[k] by construction, so max=L
        # trivially. Confirm rho stays 1 as an explicit replay, not just
        # asserted.)
        loop_a_seq = [2] * m
        loop_g, loop_rho_end, loop_parity_ok = replay_chain(letters, loop_a_seq)
        loop_max = max(loop_g)
        p(f"  UPPER BOUND check: all-2s loop chain -- parity_ok={loop_parity_ok}, "
          f"rho_end={loop_rho_end} (fixed pt, expect 1: {loop_rho_end == 1}), "
          f"achieved max g(k)={loop_max} (expect L={L}): {'MATCH' if loop_max == L else '*** MISMATCH ***'}")
        assert loop_parity_ok and loop_rho_end == 1 and loop_max == L, \
            f"{label} m={m}: loop upper-bound sanity FAILED"

        cell = {"label": label, "m": m, "L": L, "kstar_0idx": kstar0, "kstar_eq_m": (kstar0 + 1 == m)}

        # Independent exact replay of W6O's own breach witness (if any)
        w = witnesses.get((label, m))
        if w is not None:
            g_seq, rho_end, parity_ok = replay_chain(letters, w["a_seq"])
            achieved = max(g_seq)
            ceil_legal = d_ceil_legal(g_seq)
            p(f"\n  W6O breach witness independent replay: a_seq={w['a_seq']}")
            p(f"    parity_ok={parity_ok}, rho_end={rho_end} (W6O claims {w['argmin_rho_end']}: "
              f"{rho_end == w['argmin_rho_end']})")
            p(f"    g(k) sequence: {g_seq}")
            p(f"    achieved max g(k) = {achieved} (W6O claims min_cost={w['min_cost']}: "
              f"{achieved == w['min_cost']})")
            p(f"    D_CEIL LEGAL (g(k)>=0 at every prefix, house canonical constraint): {ceil_legal}")
            assert parity_ok, f"{label} m={m}: witness replay parity FAILED"
            assert rho_end == w["argmin_rho_end"], f"{label} m={m}: witness rho_end mismatch"
            assert achieved == w["min_cost"], f"{label} m={m}: witness achieved-cost mismatch"
            cell["witness_replay_ok"] = True
            cell["witness_ceiling_legal"] = ceil_legal
            cell["witness_achieved"] = achieved
        else:
            p(f"\n  No W6O breach witness on file for this cell (extra cell, not in the original 26).")
            cell["witness_replay_ok"] = None
            cell["witness_ceiling_legal"] = None
            cell["witness_achieved"] = None

        # Independent full D_ceil branch-and-bound true minimum over the
        # WHOLE window (this IS the "legal completion" search: since
        # k*==m for every one of these cells -- verified above -- there
        # is no shorter sub-prefix to extend; the true minimum over the
        # full m-length window under FULL ceiling-on semantics is
        # exactly the object in question).
        p(f"\n  Independent D_ceil (ceiling_on=True) true-minimum branch-and-bound over full m={m} window:")
        margin_ok, min1, min2, margin_wall = cap_margin_check_d_ceil(
            letters, A_CAP, WIDER_CAP, WALLCLOCK_CAP_S)
        p(f"    cap-margin check (A_CAP={A_CAP} vs {WIDER_CAP}): min@{A_CAP}={min1}, "
          f"min@{WIDER_CAP}={min2}, margin_ok={margin_ok}, wall_hit={margin_wall}")
        if margin_wall:
            p(f"    *** HONEST WALL: wallclock cap hit during cap-margin check for {label} m={m} ***")
            cell["status"] = "WALL"
            results.append(cell)
            continue
        if not margin_ok:
            p(f"    *** A_CAP MARGIN FAIL for {label} m={m}: min1={min1} != min2={min2} -- "
              f"investigate before trusting result ***")
            cell["status"] = "MARGIN_FAIL"
            results.append(cell)
            continue

        d_ceil_true_min, argmin_a_seq, wall_hit, n_nodes = min_full_window_d_ceil(
            letters, A_CAP, WALLCLOCK_CAP_S)
        p(f"    D_ceil TRUE MINIMUM = {d_ceil_true_min} (nodes explored: {n_nodes}, wall_hit={wall_hit})")
        cell["d_ceil_true_min"] = d_ceil_true_min
        cell["d_ceil_wall_hit"] = wall_hit
        cell["d_ceil_nodes"] = n_nodes

        if wall_hit:
            p(f"    *** HONEST WALL: wallclock cap hit during production D_ceil search for {label} m={m} ***")
            cell["status"] = "WALL"
            results.append(cell)
            continue

        # Independent exact replay of the argmin found by THIS search
        # (fresh replay, separate from the DFS's own bookkeeping)
        g_seq2, rho_end2, parity_ok2 = replay_chain(letters, argmin_a_seq)
        achieved2 = max(g_seq2)
        ceil_legal2 = d_ceil_legal(g_seq2)
        p(f"    argmin a_seq = {argmin_a_seq}")
        p(f"    independent replay: parity_ok={parity_ok2}, rho_end={rho_end2}, "
          f"g(k) seq={g_seq2}")
        p(f"    replay achieved max g(k) = {achieved2} (matches DFS result {d_ceil_true_min}: "
          f"{achieved2 == d_ceil_true_min}), ceiling-legal: {ceil_legal2}")
        assert parity_ok2, f"{label} m={m}: D_ceil argmin replay parity FAILED"
        assert achieved2 == d_ceil_true_min, f"{label} m={m}: D_ceil argmin replay cost mismatch"
        assert ceil_legal2, f"{label} m={m}: D_ceil argmin replay is NOT actually ceiling-legal -- DFS BUG"

        cell["d_ceil_argmin_a_seq"] = argmin_a_seq
        cell["d_ceil_argmin_rho_end"] = rho_end2
        cell["d_ceil_replay_ok"] = True

        verdict = "D=L SURVIVES" if d_ceil_true_min >= L else "UNIVERSALITY BREAKS (D<L)"
        p(f"\n    *** VERDICT for {label} m={m}: L={L}, D_ceil true min={d_ceil_true_min} "
          f"=> {verdict} ***")
        cell["verdict"] = verdict
        cell["status"] = "OK"
        results.append(cell)

    p(f"\n\n=== SUMMARY ===")
    for cell in results:
        p(f"  {cell['label']:12} m={cell['m']:3} L={cell['L']:3} "
          f"D_ceil_true_min={cell.get('d_ceil_true_min', 'WALL/FAIL')} "
          f"witness_ceiling_legal={cell.get('witness_ceiling_legal')} "
          f"status={cell['status']} verdict={cell.get('verdict', '--')}")

    p(f"\nTotal wall: {time.time()-t0:.1f}s, peak RSS: {rss_gb():.3f} GB")

    # Write outputs
    out_csv = HERE / "p1_completion_search_results.csv"
    fieldnames = ["label", "m", "L", "kstar_0idx", "kstar_eq_m", "witness_replay_ok",
                  "witness_ceiling_legal", "witness_achieved", "d_ceil_true_min",
                  "d_ceil_wall_hit", "d_ceil_nodes", "d_ceil_argmin_a_seq",
                  "d_ceil_argmin_rho_end", "d_ceil_replay_ok", "status", "verdict"]
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for cell in results:
            row = {k: cell.get(k, "") for k in fieldnames}
            w.writerow(row)
    p(f"\nWrote {out_csv.name} ({len(results)} rows)")

    with open(HERE / "p1_run_output.log", "w") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
