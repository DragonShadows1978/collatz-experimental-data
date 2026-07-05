#!/usr/bin/env python3
"""
W6U-RECON step 5 -- G3 definitional-variant probe + the corrected
D_recon table.

W4 established (two independent implementations agreeing, plus the
brute-force confirmation below): the ROOT-PINNED variant (V1: d_0 = 0
at the root, valid1 at depth m, full-precision residues) is INFEASIBLE
at every C <= 40 for the gate rows -- no residue-legal a-sequence of
length 9/12/14 keeps its forward deficit walk >= 0 from a pinned
d_0 = 0 (the E[a]=2 backward drift makes the forward prefix sums of
(c - a) go negative immediately). Plain "valid1 at exactly depth m
from the root" is NOT the object the genuine M_edge data measures.

Per the round order, the definitional variants are probed and the one
that hits the genuine 9/12/14 edges (positive AND negative directions)
is named the reconciled object.

VARIANT (ii) -- birth-anchored / free-endpoint (census lineage
semantics, and EXACTLY the archived validation automaton's frame):
renorm_check/embedding/automaton.py (the from-scratch reimplementation
whose validate.py reproduces the genuine LOCK3 cutoffs) initializes
FULLY POPULATED -- "all states (d, r), d in {0..C}, r in Z/3^m"
(COLLATZ_PROOF.md Lemma 4 / Section 8.3, quoted in automaton.py's
docstring) -- runs ONE 53-step heartbeat (credits c_0..c_52), and
tests whether any terminal-compatible state (r == 1 mod 3^m) is live
at the end. Deficit endpoints are FREE (any d in [0,C] at start and
end); the residue constraint is applied at the heartbeat's END, so by
trit-locality (DERIVATION_NOTES sec 1) only the LAST m steps carry
residue constraints -- the residue-constrained window is END-ANCHORED
at absolute credit index 53 -- and the first 53-m steps are a free
deficit walk (always satisfiable inside [0,C]: a=c holds position,
c=2/a=1 climbs, both always legal -- w1's degeneracy diagnosis, now
load-bearing in the right place).

Hence the candidate reconciled object:

  D_recon_v2(m) = min over residue-admissible backward chains from
  rho = 1 (m steps, parity-forced, exact integers) of the RANGE
  (max_j s_j - min_j s_j) of the deficit partial-sum walk
  s_j = sum(c - a), endpoints free.

  = min C such that an m-step residue-legal chain fits inside a
  deficit corridor of width C at SOME vertical offset.

Both anchorings of the credit window are computed (end-anchored
[53-m, 53) -- the measurement frame; root-anchored [0, m) -- the
census's per-trajectory convention): the genuine C<=5 gates decide
which (or both, if they coincide there -- the known convention-
coincidence zone; then m=29..32 is where they separate and the gates
cannot arbitrate -- reported honestly if so).

Cross-checks: (A) exact-integer DFS with failure memo; (B) layered
modular BFS (no big ints) -- same two independent engines as w4,
acceptance changed to free-endpoint; (C) the archived automaton
itself (embedding/automaton.py, imported READ-ONLY, no files written
there) as the genuine-frame oracle at the gate rows.
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
EMBEDDING = HERE.parent.parent.parent / "embedding"  # renorm_check/embedding
sys.path.insert(0, str(UNDERLOCK))
sys.path.insert(0, str(W6E))
sys.path.insert(0, str(HERE))

from w1_census_port import credit_at_step  # noqa: E402
from w4_census_residue_recon import (  # noqa: E402
    parity_forced, backward_pred, backward_walk_legal,
)


def rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)


def letters_end(m: int, anchor: int = 53):
    """Backward-consumption order, END-anchored window [anchor-m, anchor)."""
    return [credit_at_step(anchor - 1 - j) for j in range(m)]


def letters_root(m: int):
    """Backward-consumption order, ROOT-anchored window [0, m)."""
    return [credit_at_step(m - 1 - j) for j in range(m)]


def mirror_law(m: int) -> int:
    return (22 * m - 1) // 53


# ---------------------------------------------------------------------
# Engine A': exact-integer DFS, free endpoints (range semantics)
# ---------------------------------------------------------------------

def exists_range_at_C(letters, C: int, memo_cap: int = 30_000_000):
    """Does an m-step residue-legal backward chain from rho=1 exist
    whose deficit partial-sum walk has range <= C? Free endpoints:
    acceptance at j = m is unconditional (all constraints enforced en
    route). Returns (witness a_forward or None, stats)."""
    m = len(letters)
    pow3 = [3 ** i for i in range(m + 1)]
    memo = set()
    stats = {"nodes": 0, "memo_capped": False}
    sys.setrecursionlimit(10000)

    def dfs(j, rho, s, min_s, max_s, acc):
        stats["nodes"] += 1
        if max_s - min_s > C:
            return None
        if j == m:
            return list(acc)  # free endpoints: any complete chain fits
        key = (j, rho % pow3[m - j], s - min_s, max_s - s)
        if key in memo:
            return None
        c = letters[j]
        p = parity_forced(rho)
        if p is not None:
            a_min = 2 if p == 0 else 1
            a_hi = c + C - (max_s - s)  # keep s' >= max_s - C
            a = a_min
            while a <= a_hi:
                s2 = s + c - a
                acc.append(a)
                res = dfs(j + 1, backward_pred(rho, a), s2,
                          min(min_s, s2), max(max_s, s2), acc)
                acc.pop()
                if res is not None:
                    return res
                a += 2
        if len(memo) < memo_cap:
            memo.add(key)
        else:
            stats["memo_capped"] = True
        return None

    wit_backward = dfs(0, 1, 0, 0, 0, [])
    if wit_backward is None:
        return None, stats
    return list(reversed(wit_backward)), stats


def D_range(letters, C_max: int = 40):
    for C in range(0, C_max + 1):
        wit, stats = exists_range_at_C(letters, C)
        if stats["memo_capped"]:
            return None, None, "memo_capped"
        if wit is not None:
            return C, wit, None
    return None, None, "C_max_exhausted"


# ---------------------------------------------------------------------
# Engine B': layered modular BFS, free endpoints
# ---------------------------------------------------------------------

def exists_range_at_C_bfs(letters, C: int, state_cap: int = 20_000_000):
    """Modular-residue BFS analogue (no big integers). Acceptance at
    layer m: any surviving state."""
    m = len(letters)
    pow3 = [3 ** i for i in range(m + 1)]
    stats = {"state_capped": False, "peak_layer": 0}
    start = (1 % pow3[m], 0, 0)  # (R, u = s - min_s, v = max_s - s)
    frontier = {start: None}
    layers = [frontier]
    for j in range(m):
        c = letters[j]
        mod_next = pow3[m - j - 1]
        nxt = {}
        for (R, u, v), _parent in frontier.items():
            p = parity_forced(R % 3)
            if p is None:
                continue
            a_min = 2 if p == 0 else 1
            a_hi = c + C - v
            a = a_min
            while a <= a_hi:
                s_rel = c - a
                new_min_rel = min(-u, s_rel)
                new_max_rel = max(v, s_rel)
                if new_max_rel - new_min_rel <= C:
                    u2 = s_rel - new_min_rel
                    v2 = new_max_rel - s_rel
                    R2 = (((R << a) - 1) // 3) % mod_next if mod_next > 1 else 0
                    key2 = (R2, u2, v2)
                    if key2 not in nxt:
                        nxt[key2] = ((R, u, v), a)
                a += 2
        if len(nxt) > state_cap:
            stats["state_capped"] = True
            return None, stats
        frontier = nxt
        layers.append(frontier)
        stats["peak_layer"] = max(stats["peak_layer"], len(frontier))
        if not frontier:
            return None, stats
    goal = next(iter(frontier), None)
    if goal is None:
        return None, stats
    a_bw = []
    cur = goal
    for j in range(m, 0, -1):
        parent, a = layers[j][cur]
        a_bw.append(a)
        cur = parent
    a_bw.reverse()
    return list(reversed(a_bw)), stats


def D_range_bfs(letters, C_max: int = 40):
    for C in range(0, C_max + 1):
        wit, stats = exists_range_at_C_bfs(letters, C)
        if stats["state_capped"]:
            return None, None, "state_capped"
        if wit is not None:
            return C, wit, None
    return None, None, "C_max_exhausted"


# ---------------------------------------------------------------------
# Witness verification (free-endpoint variant)
# ---------------------------------------------------------------------

def verify_witness_range(a_forward, C, letters):
    """(i) residue: backward exact reconstruction from 1 must succeed
    and yield an odd integer n0; (ii) TRUE forward Collatz replay from
    n0 must reach 1 in exactly m odd steps with these exponents (exact
    integers, odd value at every step, exact division); (iii) deficit:
    the partial-sum walk over the given letters must have range <= C
    (then d_start = -min_s places it in [0, C])."""
    bk_ok, n0 = backward_walk_legal(a_forward)
    collatz_ok = False
    if bk_ok:
        cur = n0
        ok = True
        for a in a_forward:
            if cur % 2 != 1:
                ok = False
                break
            t = 3 * cur + 1
            if t % (2 ** a) != 0:
                ok = False
                break
            cur = t // (2 ** a)
        collatz_ok = ok and cur == 1
    # deficit walk over the window letters (letters are in backward-
    # consumption order; forward order is reversed)
    fwd_credits = list(reversed(letters))
    s = 0
    s_walk = [0]
    for c, a in zip(fwd_credits, a_forward):
        s += c - a
        s_walk.append(s)
    rng = max(s_walk) - min(s_walk)
    range_ok = rng <= C
    d_start = -min(s_walk)
    d_walk = [d_start + x for x in s_walk]
    deficit_ok = range_ok and all(0 <= d <= C for d in d_walk)
    return {
        "backward_ok": bk_ok, "start_integer": n0,
        "collatz_replay_ok": collatz_ok, "range": rng,
        "deficit_ok": deficit_ok, "d_walk": d_walk,
        "all_ok": bk_ok and collatz_ok and deficit_ok,
    }


# ---------------------------------------------------------------------
# V1 brute-force confirmation (root-pinned infeasibility is real)
# ---------------------------------------------------------------------

def v1_brute_force(m: int, a_cap: int = 8):
    """Exhaustively enumerate ALL residue-legal backward chains from
    rho=1 (root-anchored letters, a <= a_cap) and count how many are
    floor-legal from a pinned d_0 = 0 (s_m >= max_s). Independent of
    both w4 engines (no memo, no C, no range prune -- pure census of
    the acceptance condition)."""
    lets = letters_root(m)
    count_all = [0]
    count_floor = [0]
    best_peak = [None]

    def dfs(j, rho, s, min_s, max_s):
        if j == m:
            count_all[0] += 1
            if s >= max_s:
                count_floor[0] += 1
                peak = s - min_s
                if best_peak[0] is None or peak < best_peak[0]:
                    best_peak[0] = peak
            return
        c = lets[j]
        p = parity_forced(rho)
        if p is None:
            return
        a_min = 2 if p == 0 else 1
        for a in range(a_min, a_cap + 1, 2):
            s2 = s + c - a
            dfs(j + 1, backward_pred(rho, a), s2, min(min_s, s2), max(max_s, s2))

    dfs(0, 1, 0, 0, 0)
    return count_all[0], count_floor[0], best_peak[0]


def main():
    out_lines = []

    def p(s=""):
        print(s)
        out_lines.append(s)

    t0 = time.time()
    p("=== W6U-RECON W5: G3 variant probe + corrected D_recon table ===\n")

    # ---------- V1 brute-force confirmation ----------
    p("[V1 confirm] root-pinned variant, exhaustive over ALL residue-legal chains (a<=8):")
    for m in range(5, 11):
        n_all, n_floor, best = v1_brute_force(m)
        p(f"  m={m}: residue-legal chains={n_all}, floor-legal(d_0=0 pinned)={n_floor}, "
          f"min peak={best}")
    p("  (root-pinned floor-legality dies out -- confirms w4's A+B verdict independently)")

    # ---------- G3 oracle: archived automaton (genuine frame) ----------
    p("\n[G3 oracle] archived embedding/automaton.py (fully-populated start, one 53-step")
    p("heartbeat, terminal-compatible set at precision m) -- read-only import:")
    sys.path.insert(0, str(EMBEDDING))
    from automaton import terminal_compatible_set  # noqa: E402
    oracle_ok = True
    for C, m, expect_nonempty in [(3, 9, True), (3, 10, False),
                                  (4, 12, True), (4, 13, False),
                                  (5, 14, True), (5, 15, False)]:
        terminal, _hist = terminal_compatible_set(C, m)
        nonempty = len(terminal) > 0
        ok = (nonempty == expect_nonempty)
        oracle_ok = oracle_ok and ok
        p(f"  C={C}, m={m}: terminal set {'NON-EMPTY' if nonempty else 'EMPTY'} "
          f"(expected {'NON-EMPTY' if expect_nonempty else 'EMPTY'}) {'OK' if ok else 'FAIL'}")
    p(f"  Oracle frame reproduces genuine edges: {'PASS' if oracle_ok else 'FAIL'}")

    # ---------- G3 on variant (ii), both anchorings ----------
    p("\n[GATE G3 / variant (ii) free-endpoint range] both anchorings:")
    g3_end_ok = True
    g3_root_ok = True
    for m, expect in [(9, 3), (12, 4), (14, 5)]:
        De, wite, we = D_range(letters_end(m))
        Dr, witr, wr = D_range(letters_root(m))
        hit_e = (De == expect)
        hit_r = (Dr == expect)
        g3_end_ok = g3_end_ok and hit_e
        g3_root_ok = g3_root_ok and hit_r
        p(f"  m={m}: D_range_END={De} ({'MATCH' if hit_e else 'MISS'})  "
          f"D_range_ROOT={Dr} ({'MATCH' if hit_r else 'MISS'})  [expected {expect}]")
    p("  Negative directions:")
    for m_over, C_edge in [(10, 3), (13, 4), (15, 5)]:
        wit_e, _ = exists_range_at_C(letters_end(m_over), C_edge)
        wit_r, _ = exists_range_at_C(letters_root(m_over), C_edge)
        inf_e = wit_e is None
        inf_r = wit_r is None
        g3_end_ok = g3_end_ok and inf_e
        g3_root_ok = g3_root_ok and inf_r
        p(f"  length-{m_over} at C={C_edge}: END {'INFEASIBLE (correct)' if inf_e else 'FEASIBLE (miss)'}, "
          f"ROOT {'INFEASIBLE (correct)' if inf_r else 'FEASIBLE (miss)'}")
    p(f"  GATE G3: END-anchored {'PASS' if g3_end_ok else 'FAIL'}; "
      f"ROOT-anchored {'PASS' if g3_root_ok else 'FAIL'}")

    # ---------- G2 under variant (ii): the 839 chain ----------
    A839 = [1, 1, 2, 2, 1, 1, 2, 1, 4, 2, 1, 2, 1, 2, 2, 2, 1, 1, 1, 6,
            1, 2, 2, 4, 1, 1, 2, 3, 4]
    v_end = verify_witness_range(A839, 11, letters_end(29))
    v_root = verify_witness_range(A839, 11, letters_root(29))
    p(f"\n[G2 / variant (ii)] 839 chain deficit RANGE: end-anchored={v_end['range']}, "
      f"root-anchored={v_root['range']} (fits C=11 end-anchored: {v_end['range'] <= 11}; "
      f"root: {v_root['range'] <= 11})")

    # ---------- Full table m=2..32 ----------
    p("\n[Table] m=2..32, variant (ii) free-endpoint range, both anchorings,")
    p("A' (exact DFS+memo) cross-checked by B' (modular BFS) on every cell:\n")
    rows = []
    honest_walls = []
    p(f"{'m':>3} {'D_end':>6} {'D_root':>7} {'mirror':>7} {'AB_end':>7} {'AB_root':>8} "
      f"{'wit_end_ok':>11} {'wit_root_ok':>12} {'t(s)':>6}")
    for m in range(2, 33):
        tm = time.time()
        le = letters_end(m)
        lr = letters_root(m)
        De, wite, we = D_range(le)
        De_b, wite_b, we_b = D_range_bfs(le)
        Dr, witr, wr = D_range(lr)
        Dr_b, witr_b, wr_b = D_range_bfs(lr)
        ab_e = (De == De_b)
        ab_r = (Dr == Dr_b)
        if we or we_b or wr or wr_b:
            honest_walls.append((m, we, we_b, wr, wr_b))
        ve = verify_witness_range(wite, De, le) if wite else {"all_ok": None}
        vr = verify_witness_range(witr, Dr, lr) if witr else {"all_ok": None}
        rows.append({
            "m": m, "D_recon_end": De, "D_recon_root": Dr,
            "mirror_law_D_per": mirror_law(m),
            "AB_crosscheck_end": ab_e, "AB_crosscheck_root": ab_r,
            "witness_end_ok": ve["all_ok"], "witness_root_ok": vr["all_ok"],
            "witness_end": ",".join(map(str, wite)) if wite else "",
            "witness_root": ",".join(map(str, witr)) if witr else "",
            "witness_end_n0": ve.get("start_integer"),
            "witness_root_n0": vr.get("start_integer"),
        })
        p(f"{m:>3} {De!s:>6} {Dr!s:>7} {mirror_law(m):>7} {ab_e!s:>7} {ab_r!s:>8} "
          f"{ve['all_ok']!s:>11} {vr['all_ok']!s:>12} {time.time()-tm:>6.1f}")

    out_csv = HERE / "w5_corrected_table.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    p(f"\nWrote {out_csv}")
    p(f"Honest walls: {honest_walls if honest_walls else 'none'}")
    p(f"Wall: {time.time()-t0:.1f}s, peak RSS: {rss_gb():.3f} GB")

    (HERE / "w5_output.log").write_text("\n".join(out_lines) + "\n")
    p(f"Wrote {HERE / 'w5_output.log'}")


if __name__ == "__main__":
    main()
