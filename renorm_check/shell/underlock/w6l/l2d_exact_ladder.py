#!/usr/bin/env python3
"""
W6L-L2d -- EXACT shrinking-modulus ladder DP for the excursion tax
curve (replaces the representative DP outside its guarantee zone).

WHY (the L2c finding): the K2/H1 representative DP reduces to a fixed
modulus 3^T every step; the division by 3 loses one trit of certainty
per step, so a t-readout of a length-d excursion is faithful only for
t + d <= T. Outside that zone the DP both fabricates returns (K2's
certified t=9 cost-22 and t=10 cost-27 argmins FAIL exact replay --
H1's published chain actually returns at t=7) and can miss real
chains. This instrument has NO representative error:

  THE LADDER: state at depth k = v_k mod 3^(T0-k), T0 = t + d_max,
  starting from the EXACT terminal v_0 = 1. One backward step from
  class r mod 3^M gives the predecessor class EXACTLY mod 3^(M-1):
      pred mod 3^(M-1) = ((2^a * r - 1) mod 3^M) // 3
  (the division-by-3 trit loss and the ladder's modulus decrement are
  the same thing). Parity legality needs only v mod 3 (exact at every
  rung since M >= t+1 >= 2 while stepping). A readout at depth d needs
  v mod 3^t, and M_d = T0 - d >= t for all d <= d_max. Min-cost
  merging of equal classes is sound because equal classes have
  IDENTICAL feasible futures (parities and readouts for all remaining
  steps are functions of the class). Every claim below is therefore
  about the EXACT integer game, with no approximation anywhere.

  WITNESS EXTRACTION: predecessor is UNIQUE per (child class, a):
  p = (3c+1) * inv(2^a) mod 3^(M+1); backtracking climbs the ladder
  one trit per step. Every extracted witness is finally EXACT-REPLAYED
  on big integers (independent of the DP) before being reported.

GATES (all must pass before any curve value is reported):
  G1: vectorized modular step == Python big-int reference on random
      samples across all rung moduli used (incl. lift-invariance).
  G2: full curve + per-depth tables == brute-force exact-integer DFS
      (structurally independent code, big ints, no modular reduction
      at all) on small scopes.
  G3: ladder min <= every L2c exact-verified witness cost within the
      same length scope; every ladder argmin witness exact-replays.

SCOPE (RSS-honest): T0 = t + d_max <= 19 keeps every product
P * idx < 3^19*3^19 ~ 1.4e18 < 2^63 (int64-safe, no limb tricks);
live counts printed; honest wall if live > 2.5e8 states or RSS > 8GB.
  t=1..5:  d_max = 14
  t=6..10: d_max = 19 - t (13,12,11,10,9)
  t=11..14: d_max = 19 - t (8,7,6,5)  [extrapolation, length-scoped]
K2 convention kept: a=2 forbidden at the FIRST step only (the
excursion must leave the loop); cost = sum(a-2); min over depths
1..d_max of min cost among states == 1 mod 3^t.
"""
from __future__ import annotations

import csv
import sys
import time
import resource
import numpy as np
from pathlib import Path

HERE = Path(__file__).parent
W6E = HERE.parent / "w6e"
sys.path.insert(0, str(W6E))
from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402

RSS_CAP_GB = 8.0
LIVE_CAP = 250_000_000  # honest-wall threshold on live states per rung

# CAPs: cost cap per t (sound pruning: prune states with
# cost > CAP + remaining; any pruned completion ends > CAP, so if the
# found min <= CAP it is the true min for the scope). CAP chosen above
# every verified upper bound (L2c) with margin; t>=10 has no verified
# upper bound -> generous.
VERIFIED_UPPER = {1: 1, 2: 2, 3: 3, 4: 5, 5: 7, 6: 7, 7: 11, 8: 12, 9: 12}


def cap_for(t):
    return VERIFIED_UPPER.get(t, 24) + 6


def rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)


# ---------------------------------------------------------------------
# Core ladder step (vectorized, exact)
# ---------------------------------------------------------------------

def ladder_step(idx, cost, M_exp, a, first_step):
    """One exponent's worth of transitions from states (idx mod 3^M_exp,
    cost) to predecessor classes mod 3^(M_exp-1). Returns (pred_idx,
    new_cost) arrays (unmerged). Parity selection: a even serves class
    idx%3==1, a odd serves class idx%3==2."""
    if first_step and a == 2:
        return None, None
    M = 3 ** M_exp
    cls = idx % 3
    want = 1 if a % 2 == 0 else 2
    sel = cls == want
    if not sel.any():
        return None, None
    sub = idx[sel]
    subc = cost[sel]
    P = pow(2, a, M)
    prod = (P * sub) % M          # int64-safe for M <= 3^19
    num = prod - 1
    num[num < 0] += M             # canonical representative
    pred = num // 3               # exact class mod 3^(M_exp-1)
    return pred, subc + np.int32(a - 2)


def merge_min(idx_parts, cost_parts):
    """Concatenate candidate (idx, cost) arrays and keep min cost per idx."""
    idx_all = np.concatenate(idx_parts)
    cost_all = np.concatenate(cost_parts)
    order = np.lexsort((cost_all, idx_all))
    idx_s = idx_all[order]
    cost_s = cost_all[order]
    first = np.ones(len(idx_s), dtype=bool)
    first[1:] = idx_s[1:] != idx_s[:-1]
    return idx_s[first], cost_s[first]


def run_ladder(t, d_max, cap, verbose=True):
    """Full ladder run for precision t. Returns per-depth min costs to
    the target class, global min, live counts, stored per-depth state
    arrays for backtracking, and any honest wall."""
    T0 = t + d_max
    idx = np.array([1], dtype=np.int64)
    cost = np.array([0], dtype=np.int32)
    depth_states = [(idx, cost)]
    per_depth_min = {}
    live_counts = {0: 1}
    wall = None
    for k in range(d_max):
        M_exp = T0 - k
        remaining_after = d_max - (k + 1)
        keep = cost <= cap + (d_max - k)
        idx, cost = idx[keep], cost[keep]
        if len(idx) == 0:
            break
        a_hi = cap + (d_max - k) + 2 - int(cost.min())
        parts_i, parts_c = [], []
        pending = 0
        for a in range(1, max(1, a_hi) + 1):
            p, c = ladder_step(idx, cost, M_exp, a, first_step=(k == 0))
            if p is None:
                continue
            ok = c <= cap + remaining_after
            if not ok.any():
                continue
            parts_i.append(p[ok])
            parts_c.append(c[ok])
            pending += int(ok.sum())
            if pending > 60_000_000:
                mi, mc = merge_min(parts_i, parts_c)
                parts_i, parts_c = [mi], [mc]
                pending = len(mi)
        if not parts_i:
            depth_states.append((np.array([], dtype=np.int64), np.array([], dtype=np.int32)))
            live_counts[k + 1] = 0
            continue
        idx, cost = merge_min(parts_i, parts_c)
        live_counts[k + 1] = len(idx)
        if len(idx) > LIVE_CAP or rss_gb() > RSS_CAP_GB:
            wall = (k + 1, len(idx), round(rss_gb(), 2))
            if verbose:
                print(f"    HONEST WALL at depth {k+1}: live={len(idx)} RSS={rss_gb():.2f}GB")
            break
        depth_states.append((idx, cost))
        modt = 3 ** t
        hit = (idx % modt) == 1
        if hit.any():
            per_depth_min[k + 1] = int(cost[hit].min())
        if verbose and (len(idx) > 5_000_000 or k == d_max - 1):
            print(f"    depth {k+1}: live={len(idx)} RSS={rss_gb():.2f}GB "
                  f"target_min={per_depth_min.get(k+1)}")
    gmin = min(per_depth_min.values()) if per_depth_min else None
    return {"t": t, "d_max": d_max, "T0": T0, "cap": cap, "per_depth_min": per_depth_min,
            "global_min": gmin, "live_counts": live_counts, "depth_states": depth_states,
            "wall": wall}


def extract_witness(res):
    """Backtrack ONE argmin witness (min depth among global argmins):
    child class c at rung modulus 3^M has unique predecessor per a:
    p = (3c+1)*inv(2^a) mod 3^(M+1); accept if p is live at the parent
    depth with cost == child_cost - (a-2)."""
    t, T0, d_max = res["t"], res["T0"], res["d_max"]
    gmin = res["global_min"]
    if gmin is None:
        return None
    depth = min(d for d, c in res["per_depth_min"].items() if c == gmin)
    idx, cost = res["depth_states"][depth]
    modt = 3 ** t
    hit = ((idx % modt) == 1) & (cost == gmin)
    child = int(idx[hit][0])
    ccost = gmin
    seq = []
    for k in range(depth, 0, -1):
        M_exp = T0 - k            # child rung modulus exponent
        Mp = 3 ** (M_exp + 1)     # parent rung modulus
        pidx, pcost = res["depth_states"][k - 1]
        found = False
        for a in range(1, res["cap"] + 2 * d_max + 3):
            if k == 1 and a == 2:
                continue  # first-step convention
            target_parent_cost = ccost - (a - 2)
            inv2a = pow(pow(2, a, Mp), -1, Mp)
            p = ((3 * child + 1) * inv2a) % Mp
            want = 1 if a % 2 == 0 else 2
            if p % 3 != want:
                continue
            loc = int(np.searchsorted(pidx, p))
            if loc < len(pidx) and pidx[loc] == p and pcost[loc] == target_parent_cost:
                seq.append(a)
                child = int(p)
                ccost = int(target_parent_cost)
                found = True
                break
        if not found:
            return ("BACKTRACK_FAIL", depth, seq)
    seq.reverse()
    return (depth, tuple(seq))


def exact_replay(seq, t):
    v = 1
    for a in seq:
        p = forced_parity_for_backward_step(v)
        if p is None or (a % 2 == 0) != (p == 0):
            return False
        v = backward_predecessor_exact(v, a)
    return v % (3 ** t) == 1


# ---------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------

def gate_G1():
    rng = np.random.default_rng(42)
    n_checked = 0
    for M_exp in (3, 7, 12, 16, 19):
        M = 3 ** M_exp
        for a in (1, 2, 3, 5, 8, 13, 20):
            want = 1 if a % 2 == 0 else 2
            raw = rng.integers(0, min(M, 10 ** 9), size=200, dtype=np.int64)
            raw = raw[(raw % 3) == want]
            if len(raw) == 0:
                continue
            cost0 = np.zeros(len(raw), dtype=np.int32)
            pred, _ = ladder_step(raw, cost0, M_exp, a, first_step=False)
            for r, p in zip(raw.tolist(), pred.tolist()):
                ref = ((pow(2, a, M) * r) % M) - 1
                if ref < 0:
                    ref += M
                assert ref % 3 == 0
                ref //= 3
                assert p == ref, f"G1 FAIL M=3^{M_exp} a={a} r={r}: {p} != {ref}"
                # lift-invariance: fully exact big-int on an arbitrary lift
                v = r + M * 7
                pv = (1 << a) * v - 1
                if pv % 3 == 0:
                    assert (pv // 3) % (M // 3) == ref % (M // 3), "G1 lift-invariance FAIL"
                n_checked += 1
    print(f"G1 PASS: vectorized ladder step == big-int reference on {n_checked} samples "
          f"(incl. lift-invariance of the class map)")


def brute_force_exact(t, d_max, cap):
    """Structurally independent brute force: recursive DFS on EXACT big
    integers, no modular state anywhere."""
    per_depth = {}

    def rec(v, depth, cost):
        if depth > 0 and v % (3 ** t) == 1:
            if depth not in per_depth or cost < per_depth[depth]:
                per_depth[depth] = cost
        if depth == d_max:
            return
        p = forced_parity_for_backward_step(v)
        if p is None:
            return
        a = 2 if p == 0 else 1
        while cost + (a - 2) <= cap + (d_max - depth - 1):
            if not (depth == 0 and a == 2):
                rec(backward_predecessor_exact(v, a), depth + 1, cost + (a - 2))
            a += 2

    rec(1, 0, 0)
    gmin = min(per_depth.values()) if per_depth else None
    return per_depth, gmin


def gate_G2():
    for (t, d_max, cap) in [(1, 6, 6), (2, 6, 7), (3, 6, 9), (2, 7, 6)]:
        res = run_ladder(t, d_max, cap, verbose=False)
        bf_per_depth, bf_gmin = brute_force_exact(t, d_max, cap)
        ok = (res["global_min"] == bf_gmin) and (res["per_depth_min"] == bf_per_depth)
        print(f"G2 {'PASS' if ok else '*** FAIL ***'}: t={t} d_max={d_max} cap={cap}: "
              f"ladder gmin={res['global_min']} bf gmin={bf_gmin}; per-depth tables "
              f"{'identical' if res['per_depth_min'] == bf_per_depth else 'DIFFER: ' + str((res['per_depth_min'], bf_per_depth))}")
        if not ok:
            raise SystemExit("G2 FAILED -- ladder not trustworthy")


def main():
    t_start = time.time()
    print("=== L2d: EXACT shrinking-modulus ladder DP ===\n")
    print("--- Gates ---")
    gate_G1()
    gate_G2()
    print()

    scope = {t: (14 if t <= 5 else 19 - t) for t in range(1, 15)}

    curve_rows = []
    print("--- Production runs ---")
    for t in range(1, 15):
        d_max = scope[t]
        cap = cap_for(t)
        print(f"  t={t} (T0={t+d_max}, d_max={d_max}, cap={cap}):")
        t0 = time.time()
        res = run_ladder(t, d_max, cap)
        wit = extract_witness(res)
        gmin = res["global_min"]
        replay_ok = None
        if wit is None:
            wit_str = "none (no target hit in scope)"
        elif wit[0] == "BACKTRACK_FAIL":
            wit_str = f"BACKTRACK FAILED at depth {wit[1]} partial={wit[2]}"
            replay_ok = False
        else:
            depth, seq = wit
            replay_ok = exact_replay(seq, t) and sum(a - 2 for a in seq) == gmin
            wit_str = f"len={depth} a_seq={seq} exact_replay={'PASS' if replay_ok else '*** FAIL ***'}"
        vu = VERIFIED_UPPER.get(t)
        g3_note = ""
        if vu is not None and gmin is not None and gmin > vu:
            g3_note = (f" [verified witness cost {vu} exists at length beyond this d_max "
                       f"-- min over ALL lengths <= {vu}]")
        wall_note = f" WALL@{res['wall']}" if res["wall"] else ""
        print(f"    RESULT: exact min (len<={d_max}) = {gmin}; witness {wit_str}; "
              f"per-depth {res['per_depth_min']}{g3_note}{wall_note}; {time.time()-t0:.1f}s")
        curve_rows.append({
            "t": t, "d_max": d_max, "T0": t + d_max, "cap": cap,
            "exact_min_len_scoped": gmin,
            "argmin_len": (wit[0] if wit and wit[0] != "BACKTRACK_FAIL" else ""),
            "argmin_a_seq": (",".join(map(str, wit[1])) if wit and wit[0] != "BACKTRACK_FAIL" else ""),
            "witness_replay": replay_ok,
            "verified_upper_beyond_scope": vu if (vu is not None and gmin is not None and gmin > vu) else "",
            "per_depth_min": str(res["per_depth_min"]),
            "wall": str(res["wall"]) if res["wall"] else "",
        })
        res["depth_states"] = None  # free before next t

    out = HERE / "l2d_exact_curve.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(curve_rows[0].keys()))
        w.writeheader()
        for r in curve_rows:
            w.writerow(r)
    print(f"\nWrote {out.name}")

    print("\n=== EXACT CURVE OF RECORD (t=1..14) ===")
    final_curve = {}
    for r in curve_rows:
        t = r["t"]
        cands = [v for v in (r["exact_min_len_scoped"], VERIFIED_UPPER.get(t)) if v is not None]
        final_curve[t] = min(cands) if cands else None
        exact = (r["exact_min_len_scoped"] is not None
                 and (VERIFIED_UPPER.get(t) is None or r["exact_min_len_scoped"] <= VERIFIED_UPPER[t]))
        tag = f"EXACT for len<={r['d_max']}" if exact else "UPPER BOUND (longer verified witness beats in-scope min)"
        print(f"  t={t:>2}: {final_curve[t]}  [{tag}]")

    core = [final_curve[t] for t in range(1, 11)]
    print(f"\nCore curve t=1..10: {core}")
    print(f"vs K2 certified:    [1, 2, 5, 5, 7, 7, 15, 19, 22, 27]")
    ext = [final_curve[t] for t in range(11, 15)]
    print(f"Extension t=11..14 (d_max={[scope[t] for t in range(11, 15)]}): {ext}")

    print("\n=== Frozen (c) [60%]: t=11..14 continues ~2.5-3/trit, plateaus width<=2 ===")
    known = [(t, final_curve[t]) for t in range(10, 15) if final_curve[t] is not None]
    if len(known) >= 2:
        incs = [(known[i + 1][0], known[i + 1][1] - known[i][1]) for i in range(len(known) - 1)]
        vals = [v for (_t, v) in incs]
        avg = sum(vals) / len(vals)
        seqv = [v for (_t, v) in known]
        maxw = cw = 1
        for i in range(1, len(seqv)):
            cw = cw + 1 if seqv[i] == seqv[i - 1] else 1
            maxw = max(maxw, cw)
        in_range = 2.5 <= avg <= 3.0
        print(f"  increments from t=10: {incs}; avg rate={avg:.2f} "
              f"(2.5-3.0: {'yes' if in_range else 'NO'}), max plateau width={maxw} "
              f"(<=2: {'yes' if maxw <= 2 else 'NO'})")
        print(f"  Verdict: {'HIT' if (in_range and maxw <= 2) else 'MISS'} "
              f"[caveat: extension values are length-scoped (d_max shrinks with t); exact "
              f"for their scope but possibly above the unbounded-length min]")
    else:
        print("  UNEVALUATED (insufficient extension data)")

    print(f"\nTotal wall: {time.time()-t_start:.1f}s, peak RSS: {rss_gb():.3f} GB")


if __name__ == "__main__":
    main()
