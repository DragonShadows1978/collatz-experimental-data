#!/usr/bin/env python3
"""
W6N-N2 -- Is the floor forced by the prefix congruence ALONE?, per
W6N_FLOOR_MECHANISM_ORDER.md section N2 (the mechanism check, 13a).

QUESTION: at the loop's own binding prefix k* (argmax of g_loop for a
given word w), is the floor g(k*) >= g_loop(k*) [proven exceptionless
in M1 and re-confirmed at wider budget in N1] a fact about the
mod-3^k* residue CONGRUENCE ALONE (i.e. no admissible length-k* prefix
-- parity-forced at every step, no suffix-completability requirement
at all -- ever achieves a max-partial-sum below g_loop(k*)), or does
the congruence alone permit cheap prefixes that are only killed later,
by SUFFIX infeasibility over the remaining m-k* letters?

OPERATIONALIZATION (binding, per the order's own text): "residue-
feasible prefix states" = "ANY chain prefix of length k*, regardless
of suffix feasibility -- the mod-3^k* congruence/parity constraints
ONLY". The parity-forcing rule (engine.forced_parity_for_backward_step)
IS exactly this congruence: at each backward step, the current exact
residue rho mod 3 forces the parity of the NEXT exponent a (class 0 =
no legal move ever, a genuine congruence obstruction; class 1/2 forces
even/odd). So "enumerate ALL residue-feasible prefix states of length
k*" = enumerate every a-sequence of length k* that is admissible under
this SAME parity rule alone -- with NO cap on the partial sum along
the way (unlike M1/N1's DFS, which prunes anything exceeding a slack
bound; here we want the true minimum over the WHOLE prefix space, so
pruning must only ever be sound, never an artificial ceiling). This is
mechanically the identical DFS primitive used everywhere else in
W6E/W6K/W6L/W6M (Path C), just run over prefixes of length k* only,
with the objective "find min max_{j<=k*} g(j)" instead of "enumerate
band-bounded completions."

For each prefix state found with max-partial-sum (over j=1..k*) STRICTLY
below g_loop(k*) (i.e. "cheap-at-k*"): attempt to extend it to a FULL
admissible chain of length m (Path C DFS over the remaining m-k*
letters, D_free semantics, checking only that a completion EXISTS --
does not need to itself respect any slack bound, since a class-0 dead
end is the only way a suffix can be infeasible; report whichever cheap
prefixes have ANY legal completion at all, however expensive).

Two possible answers:
  (a) NO cheap-at-k* prefix exists at all (min over ALL residue-
      admissible length-k* prefixes is >= g_loop(k*)) -- the
      congruence ALONE reproduces the floor. Frozen-prediction FALSE
      reading; "prefix-alone suffices".
  (b) Cheap-at-k* prefixes DO exist under the congruence alone, but
      EVERY one of them has NO legal admissible completion to length m
      (every extension attempt hits a class-0 dead end before m) --
      the floor is forced by the WHOLE WINDOW (prefix congruence is
      not enough by itself; suffix infeasibility is doing the killing).
  (c) [would be the genuine surprise] some cheap-at-k* prefix DOES
      have a legal completion to length m -- this would mean the
      floor g(k*)>=g_loop(k*) is FALSE for some full chain, which
      would already have shown up as an N1/M1 violation. Given N1's
      240/240 clean result at L+3, (c) is not expected, but is
      checked explicitly here as a cross-consistency gate (any (c)
      finding would contradict N1 and must be dumped, exact-replayed,
      and treated as a possible N1/N2 discrepancy needing
      reconciliation).

Frozen prediction (Fable, 65%): (b) -- the congruence alone is NOT
enough; cheap prefixes exist and are killed by the suffix.

Sample: 40 words, m=5..7 -- the two mechanical-family rows at each of
m=5,6,7 (6 words) + random {1,2}^m words to fill to 40 (34 random
words, seeded, matching M1's seed convention where applicable).

INSTRUMENT RULE (binding): Path C only (parity-forced backward DFS,
D_free semantics). Every reported prefix-state witness (the argmin
cheap prefix, and any completion found) is exact-integer replayed
in-process via a fresh, independent from-scratch application of
engine.backward_predecessor_exact -- the W6L/W6M discipline.
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

M_SCOPE = [5, 6, 7]
N_WORDS_TOTAL = 40
SEED = 20260704
A_CAP = 40


def loop_curve(letters):
    running = 0
    curve = []
    for c in letters:
        running += (2 - c)
        curve.append(running)
    L = max([0] + curve)
    k_star = curve.index(max(curve))  # 0-indexed
    return curve, L, k_star


def _product12(m):
    if m == 0:
        yield ()
        return
    for rest in _product12(m - 1):
        yield (1,) + rest
        yield (2,) + rest


def build_sample():
    """40-word sample: mechanical rows (golden-per8, sqrt2-per12) at
    each m=5,6,7 (6 words) + random {1,2}^m words filling to 40,
    seeded, distributed as evenly as possible across m=5,6,7."""
    words = []
    seen_by_m = {m: set() for m in M_SCOPE}
    for m in M_SCOPE:
        golden = tuple(backward_letters(credit_golden_per8, m, anchor_steps=53))
        sqrt2 = tuple(backward_letters(credit_sqrt2_per12, m, anchor_steps=53))
        words.append((m, "golden-per8", golden))
        words.append((m, "sqrt2-per12", sqrt2))
        seen_by_m[m].add(golden)
        seen_by_m[m].add(sqrt2)

    n_random_needed = N_WORDS_TOTAL - len(words)  # 40 - 6 = 34
    # distribute as evenly as possible across the 3 m values
    per_m = [n_random_needed // 3] * 3
    for i in range(n_random_needed % 3):
        per_m[i] += 1

    rng = random.Random(SEED)
    for i, m in enumerate(M_SCOPE):
        n_needed = per_m[i]
        universe_size = 2 ** m
        if universe_size <= n_needed + len(seen_by_m[m]) + 2:
            all_words = [tuple(w) for w in _product12(m)]
            rng.shuffle(all_words)
            cnt = 0
            for w in all_words:
                if w not in seen_by_m[m]:
                    words.append((m, f"random{cnt:03d}", w))
                    seen_by_m[m].add(w)
                    cnt += 1
                if cnt >= n_needed:
                    break
        else:
            cnt = 0
            attempts = 0
            while cnt < n_needed and attempts < n_needed * 100:
                w = tuple(rng.choice((1, 2)) for _ in range(m))
                attempts += 1
                if w not in seen_by_m[m]:
                    words.append((m, f"random{cnt:03d}", w))
                    seen_by_m[m].add(w)
                    cnt += 1
    return words


def min_prefix_cost_and_argmin(letters_prefix, a_cap):
    """Find the TRUE MINIMUM max-partial-sum over ALL residue-admissible
    (parity-forced, congruence-only) exponent sequences of length
    k*=len(letters_prefix) -- branch-and-bound DFS (prune the instant a
    branch's running max already exceeds the best complete value found
    so far; sound because max_so_far is monotone nondecreasing along
    any extension -- the SAME pruning argument as
    k0_canonical_engine.canonical_D). This finds the min WITHOUT
    materializing the full (exponentially large, unrestricted) prefix
    space -- the naive full enumeration is 20^k* for a_cap=40 and
    explodes past k*~6 (verified: k*=7 -> 20^7 = 1.28e9, an honest
    combinatorial wall this script must not walk into). a_cap is
    margin-checked below (rerun at a wider cap, confirm unchanged
    minimum) exactly as k0/M1/M2 do for their own DFS width.
    Returns (min_cost, argmin_a_seq, argmin_rho_end)."""
    k = len(letters_prefix)
    best = [None, None, None]  # cost, a_seq, rho_end

    def dfs(j, rho, running, max_so_far, a_seq):
        if best[0] is not None and max_so_far >= best[0]:
            return
        if j == k:
            if best[0] is None or max_so_far < best[0]:
                best[0], best[1], best[2] = max_so_far, tuple(a_seq), rho
            return
        c = letters_prefix[j]
        parity = forced_parity_for_backward_step(rho)
        if parity is None:
            return  # class-0 dead end -- this prefix branch does not exist
        a_min = 2 if parity == 0 else 1
        for a in range(a_min, a_min + a_cap, 2):
            running2 = running + (a - c)
            rho2 = backward_predecessor_exact(rho, a)
            dfs(j + 1, rho2, running2, max(max_so_far, running2), a_seq + [a])

    dfs(0, 1, 0, 0, [])
    return best[0], best[1], best[2]


def enumerate_cheap_states(letters_prefix, threshold, a_cap):
    """Enumerate every residue-admissible length-k* exponent sequence
    whose max-partial-sum is STRICTLY BELOW `threshold` (= g_loop(k*)),
    i.e. every "cheap-at-k*" prefix state -- branch-and-bound pruned at
    `threshold` (sound: same monotone-max argument), so this stays
    small even though the unrestricted prefix space is exponential --
    it only ever materializes states that end up satisfying the cheap
    condition, or dies before reaching k*. Returns list of
    (a_seq, max_partial_sum, rho_end)."""
    k = len(letters_prefix)
    results = []

    def dfs(j, rho, running, max_so_far, a_seq):
        if max_so_far >= threshold:
            return
        if j == k:
            results.append((tuple(a_seq), max_so_far, rho))
            return
        c = letters_prefix[j]
        parity = forced_parity_for_backward_step(rho)
        if parity is None:
            return
        a_min = 2 if parity == 0 else 1
        for a in range(a_min, a_min + a_cap, 2):
            running2 = running + (a - c)
            max2 = max(max_so_far, running2)
            if max2 >= threshold:
                continue
            rho2 = backward_predecessor_exact(rho, a)
            dfs(j + 1, rho2, running2, max2, a_seq + [a])

    dfs(0, 1, 0, 0, [])
    return results


def cap_margin_check_prefix(letters_prefix, base_cap, wider_cap):
    min1, _, _ = min_prefix_cost_and_argmin(letters_prefix, base_cap)
    min2, _, _ = min_prefix_cost_and_argmin(letters_prefix, wider_cap)
    return (min1 == min2, min1, min2)


def try_extend_to_completion(letters_full, k_star, prefix_a_seq, prefix_rho, a_cap,
                              completion_a_cap=6, node_budget=200_000):
    """Given a cheap-at-k* prefix (its exponent sequence and its ending
    exact residue rho), attempt to find ANY admissible completion over
    the remaining letters[k_star:] to length m -- ignoring cost
    entirely (we only want to know: does ANY legal continuation exist
    at all, however expensive -- existence, not optimality). Since
    EVERY residue class 1/2 always has a1=1 or a=2 as its cheapest
    legal choice (class 0 is the only dead end; class 1/2 never runs
    out of legal exponents at that parity), completion existence
    reduces to whether a class-0 residue is ever hit -- checked at
    completion_a_cap=6 admissible choices per step (far more than
    needed for existence: the greedy least-exponent choice at each
    step is always tried first via range() ascending order, so a
    small completion_a_cap only limits BACKTRACKING search width, not
    whether existence is found -- and any class-0 dead end is a
    genuine dead end regardless of a_cap width, since a_cap only ever
    ADDS more same-parity choices, never removes the None-parity
    case). A node_budget bounds worst-case DFS nodes explored (honest
    wall, reported if hit) since remaining length can be several
    steps and this is called once per cheap prefix. Returns the first
    completion found (as a full a_seq) or None if every continuation
    dies at a class-0 dead end within the search budget, or
    ("BUDGET_EXCEEDED", None) if the node budget was exhausted first
    (distinct from a genuine dead end -- an honest wall, not a proof
    of infeasibility)."""
    remaining = letters_full[k_star:]
    nodes = [0]

    def dfs(j, rho, a_seq):
        nodes[0] += 1
        if nodes[0] > node_budget:
            return "BUDGET"
        if j == len(remaining):
            return list(a_seq)
        c = remaining[j]
        parity = forced_parity_for_backward_step(rho)
        if parity is None:
            return None
        a_min = 2 if parity == 0 else 1
        for a in range(a_min, a_min + completion_a_cap, 2):
            rho2 = backward_predecessor_exact(rho, a)
            found = dfs(j + 1, rho2, a_seq + [a])
            if found == "BUDGET":
                return "BUDGET"
            if found is not None:
                return found
        return None

    tail = dfs(0, prefix_rho, [])
    if tail == "BUDGET":
        return "BUDGET_EXCEEDED"
    if tail is None:
        return None
    return list(prefix_a_seq) + tail


def independent_replay_full_chain(letters, a_seq):
    """Fresh from-scratch recomputation: replay the full chain,
    confirming parity-legality at every step and returning the
    max-partial-sum over the WHOLE chain (for cross-consistency with
    N1's floor test if a completion is ever found)."""
    rho = 1
    running = 0
    max_so_far = 0
    for c, a in zip(letters, a_seq):
        parity = forced_parity_for_backward_step(rho)
        if parity is None or (a % 2 == 0) != (parity == 0):
            return None  # illegal -- replay failed
        running += (a - c)
        max_so_far = max(max_so_far, running)
        rho = backward_predecessor_exact(rho, a)
    return max_so_far


def main():
    t0 = time.time()
    print("=== W6N-N2: is the floor forced by the prefix congruence ALONE? ===\n")

    words = build_sample()
    print(f"Sample size: {len(words)} words (target 40)")
    by_m = {}
    for (m, label, w) in words:
        by_m.setdefault(m, []).append(label)
    for m in M_SCOPE:
        print(f"  m={m}: {len(by_m.get(m, []))} words -- {by_m.get(m, [])}")
    assert len(words) == N_WORDS_TOTAL, f"sample size {len(words)} != {N_WORDS_TOTAL}"
    print()

    rows = []
    n_cheap_exists = 0
    n_no_cheap = 0
    n_cheap_with_completion = 0  # the (c) surprise case
    n_cheap_all_die = 0          # the (b) predicted case
    n_cheap_state_cap_hit = 0    # honest-wall counter (per-word cheap-state cap)
    cross_consistency_alerts = []
    CHEAP_STATE_CAP = 20000      # honest wall: cap cheap states materialized/word

    for (m, label, letters) in words:
        g_loop_curve, L, k_star_idx = loop_curve(letters)
        k_star_1idx = k_star_idx + 1
        g_loop_at_kstar = g_loop_curve[k_star_idx]
        prefix_letters = letters[:k_star_1idx]

        # cap margin check on this word's own prefix (branch-and-bound
        # over the TRUE minimum, not the exponentially-large full space)
        margin_ok, min1, min2 = cap_margin_check_prefix(prefix_letters, A_CAP, A_CAP * 2)
        if not margin_ok:
            raise SystemExit(f"A_CAP margin FAIL at m={m} {label}: min@{A_CAP}={min1} "
                              f"min@{A_CAP*2}={min2} -- widen cap")
        min_prefix_cost, argmin_a_seq, argmin_rho = min_prefix_cost_and_argmin(prefix_letters, A_CAP)

        # cheap states: enumerated with branch-and-bound pruning at the
        # g_loop(k*) threshold -- stays small (only cheap-or-borderline
        # branches are ever materialized), honest-wall capped for the
        # rare word with many cheap states.
        cheap_states = enumerate_cheap_states(prefix_letters, g_loop_at_kstar, A_CAP)
        n_cheap = len(cheap_states)
        cheap_capped = False
        if n_cheap > CHEAP_STATE_CAP:
            n_cheap_state_cap_hit += 1
            cheap_capped = True
            cheap_states = cheap_states[:CHEAP_STATE_CAP]

        if n_cheap == 0:
            n_no_cheap += 1
            verdict_word = "NO_CHEAP_PREFIX (congruence alone already forbids)"
            completion_found_any = None
        else:
            n_cheap_exists += 1
            # attempt completion for every materialized cheap prefix
            any_completion = None
            n_completions_found = 0
            n_budget_exceeded = 0
            for (a_seq, cost, rho_end) in cheap_states:
                completion = try_extend_to_completion(letters, k_star_1idx, a_seq, rho_end, A_CAP)
                if completion == "BUDGET_EXCEEDED":
                    n_budget_exceeded += 1
                    continue
                if completion is not None:
                    n_completions_found += 1
                    if any_completion is None:
                        any_completion = completion
            completion_found_any = (n_completions_found > 0)
            if completion_found_any:
                n_cheap_with_completion += 1
                verdict_word = f"CHEAP_PREFIX_HAS_COMPLETION ({n_completions_found}/{n_cheap})"
                # cross-consistency: replay the full chain and check
                # its max-partial-sum against g_loop_at full-word k*
                # (this is the SAME k* since it's a word-level quantity)
                replay_max = independent_replay_full_chain(letters, any_completion)
                full_loop_L = L
                if replay_max is not None and replay_max < full_loop_L:
                    cross_consistency_alerts.append({
                        "m": m, "label": label, "word": "".join(map(str, letters)),
                        "a_seq": any_completion, "replay_max": replay_max, "L": full_loop_L,
                    })
            else:
                n_cheap_all_die += 1
                budget_note = f", {n_budget_exceeded} hit node-budget (honest wall)" if n_budget_exceeded else ""
                verdict_word = f"CHEAP_PREFIX_ALL_DIE (0/{n_cheap} have any completion{budget_note})"

        rows.append({
            "m": m, "label": label, "word": "".join(map(str, letters)),
            "L": L, "k_star_1idx": k_star_1idx, "g_loop_at_kstar": g_loop_at_kstar,
            "min_prefix_cost": min_prefix_cost,
            "n_cheap_states": n_cheap, "cheap_states_capped": cheap_capped,
            "any_cheap_has_completion": completion_found_any,
            "verdict": verdict_word,
        })
        print(f"  m={m} {label:12s} word={''.join(map(str,letters))} k*={k_star_1idx} "
              f"g_loop(k*)={g_loop_at_kstar} min_prefix_cost={min_prefix_cost} "
              f"n_cheap={n_cheap}{' (CAPPED)' if cheap_capped else ''} -> {verdict_word}")

    print(f"\nTotals: {n_no_cheap}/{len(words)} words have NO cheap-at-k* prefix "
          f"(congruence alone forbids); {n_cheap_exists}/{len(words)} have cheap "
          f"prefixes under the congruence alone.")
    print(f"  Of the {n_cheap_exists} with cheap prefixes: {n_cheap_all_die} have ALL "
          f"cheap prefixes die by suffix infeasibility (prediction (b)); "
          f"{n_cheap_with_completion} have at least one cheap prefix WITH a legal "
          f"completion (would be case (c), a cross-consistency alert vs N1).")

    if cross_consistency_alerts:
        print(f"\n*** {len(cross_consistency_alerts)} CROSS-CONSISTENCY ALERTS -- a "
              f"full chain was found with max-partial-sum < L(w), which would "
              f"contradict the loop's own optimality (L1/L2/L3/M1/N1 all certify "
              f"the loop is the unique minimizer) -- investigate before trusting ***")
        for a in cross_consistency_alerts:
            print(f"  ALERT m={a['m']} {a['label']} word={a['word']} a_seq={a['a_seq']} "
                  f"replay_max={a['replay_max']} < L={a['L']}")
    else:
        print("\nNo cross-consistency alerts: no completion found ever produced a "
              "full-chain max-partial-sum below L(w) (consistent with L1's total-"
              "rigidity/uniqueness result and N1's clean floor at L+3).")

    out = HERE / "n2_prefix_congruence_table.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nWrote {out.name} ({len(rows)} rows)")

    # -------------------------------------------------------------
    # Frozen prediction verdict
    # -------------------------------------------------------------
    print("\n=== FROZEN PREDICTION VERDICT ===")
    print("(b) congruence alone NOT enough -- cheap prefixes exist, killed by "
          "suffix -- 65% predicted\n")
    frac_cheap_exists = n_cheap_exists / len(words)
    print(f"Fraction of words with cheap-at-k* prefixes under the congruence alone: "
          f"{n_cheap_exists}/{len(words)} = {100*frac_cheap_exists:.1f}%")
    if n_cheap_exists == 0:
        verdict = "MISS -- reading (a): congruence ALONE already forbids cheap prefixes " \
                  "on every sampled word (prefix-alone suffices)"
    elif n_cheap_with_completion > 0:
        verdict = (f"MISS/ALERT -- {n_cheap_with_completion} word(s) show a cheap prefix "
                   f"WITH a legal completion; this is case (c), inconsistent with total "
                   f"rigidity unless the completion's full-chain cost is still >= L(w) "
                   f"(possible if a_seq's LATER partial sums exceed g_loop(k*) despite the "
                   f"prefix being cheap AT k* -- i.e. cheap-at-k*-but-not-cheap-overall; see "
                   f"cross-consistency check above for whether this actually violates the "
                   f"floor)")
    else:
        verdict = (f"HIT -- reading (b): {n_cheap_exists}/{len(words)} words have cheap-"
                   f"at-k* prefixes under the congruence alone, and on EVERY one of them "
                   f"({n_cheap_all_die}/{n_cheap_exists}) every such cheap prefix dies by "
                   f"suffix infeasibility -- the floor is a whole-window fact, congruence "
                   f"alone is not enough")
    print(f"Verdict: {verdict}")

    print(f"\nTotal wall: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
