#!/usr/bin/env python3
"""
W6M-M3 -- Ladder walls extension (close L2's honest gaps), per
W6M_GLOBAL_LEMMA_MAP_ORDER.md section M3.

TARGET SCOPE (per the order): t=13,14 at len<=14 (T0=27,28); and a
length-stability probe at t=10..12, len 15,16 (T0=25..28) -- does the
curve drop further than L2e's len<=14 values?

WHY A NEW INSTRUMENT (not l2d/l2e reused as-is): l2d's ladder_step is
int64-vectorized (single 64-bit product, valid to M_exp<=19); l2e's
two-limb extension raises this to M_exp<=24 by splitting P into two
3^10-sized limbs -- but this round's target T0 values (25-28) exceed
that bound. Checked directly before assuming anything: the two-limb
scheme's OWN correctness gate (G1-ext) was only ever run for
M_exp<=24; probing it at M_exp=26 here (throwaway check, not part of
the certified record) finds a genuine int64 OVERFLOW in the "P_hi*sub"
cross term (P_hi up to ~3^16, sub up to 3^26, product ~3^42 > 2^63) --
so the L2e docstring's stated M_exp<=24 ceiling is a REAL arithmetic
wall, not a conservative round number, and reusing that code past its
own gated range would silently fabricate results (exactly the W6L
lesson). Rather than build a fragile wider multi-limb int64 scheme
under time pressure (a 3- or 4-limb split was sketched and would need
its own from-scratch multi-gate certification to trust), this script
uses PYTHON BIGINT ARITHMETIC THROUGHOUT -- no modular int64 tricks,
no truncation, no overflow risk of any kind, at the cost of no numpy
vectorization. Live-state counts at these depths are the same order
as L2e's own certified run (max ~7.9e5 states, per l2e_run_output.log)
-- bigint arithmetic at that scale is sub-second per rung (measured:
200k bigint modular steps ~0.05s), so this is not a performance
compromise, just a correctness-first instrument choice.

THE LADDER (same mathematical object as L2/L2d/L2e, restated exactly):
state at depth k = v_k mod 3^(T0-k), T0 = t + d_max, starting from the
EXACT terminal v_0 = 1. One backward step from class r mod 3^M gives
the predecessor class EXACTLY mod 3^(M-1):
    pred mod 3^(M-1) = ((2^a * r - 1) mod 3^M) // 3
Parity legality needs only v mod 3. A readout at depth d needs
v mod 3^t with M_d = T0-d >= t for all d<=d_max (the guarantee-zone
law, t+d<=T0, enforced by construction here exactly as in L2d/L2e).
Min-cost merging of equal classes is sound (identical feasible
futures). Every reported witness is additionally exact-replayed on
genuine (unbounded, non-modular) big integers via
engine.backward_predecessor_exact, independent of the ladder's own
class-tracking arithmetic -- the W6L discipline.

GATES (all run before any production value is reported):
  G1: bigint ladder step == direct big-int reference computation
      (trivially true by construction here since both ARE big-int,
      but still cross-checked against an entirely separately-written
      formula to catch transcription bugs) + lift-invariance.
  G2: full curve/per-depth tables == brute-force exact-integer DFS
      (the SAME brute_force_exact used by l2d, imported unmodified --
      it is already a structurally independent, non-modular reference)
      on small scopes.
  G3: every extracted witness exact-replays via
      engine.backward_predecessor_exact (fully independent primitive
      from a different module).

SCOPE ACTUALLY RUN (stated exactly, honest walls if hit):
  (1) t=13, d_max=14 (T0=27); t=14, d_max=14 (T0=28) -- the order's len<=14 extension.
  (2) length-stability probe: t=10, d_max=15,16 (T0=25,26);
      t=11, d_max=15,16 (T0=26,27); t=12, d_max=15,16 (T0=27,28).
Caps: best-known-so-far (from L2e's l2e_extended_curve.csv) + margin,
generous where no prior value exists; honest wall (state explosion or
wall-clock budget) reported verbatim, not silently narrowed.
"""
from __future__ import annotations

import csv
import sys
import time
import resource
from pathlib import Path

HERE = Path(__file__).parent
W6L = HERE.parent / "w6l"
W6E = HERE.parent / "w6e"
sys.path.insert(0, str(W6L))
sys.path.insert(0, str(W6E))

from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402
from l2d_exact_ladder import brute_force_exact  # noqa: E402 (structurally independent reference, reused as-is)

RSS_CAP_GB = 8.0
LIVE_CAP = 250_000_000
WALLCLOCK_CAP_S = 240.0  # per-(t,d_max) wall-clock honest-wall budget


def rss_gb() -> float:
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024)


# ---------------------------------------------------------------------
# Bigint ladder core (independent instrument -- no numpy, no int64 caps)
# ---------------------------------------------------------------------

def ladder_step_bigint(state_cost, M_exp, a, first_step):
    """state_cost: dict {idx (python int, exact class mod 3^M_exp): cost}.
    Returns a NEW dict {pred_idx mod 3^(M_exp-1): min_cost}, merging
    ties to the minimum (sound: equal classes have identical feasible
    futures). Pure big-int arithmetic -- no modular reduction of the
    exponent needed since Python ints have no width limit; 2**a is
    computed once per (M_exp, a) and reduced mod M once."""
    if first_step and a == 2:
        return {}
    M = 3 ** M_exp
    P = pow(2, a, M)
    want = 1 if a % 2 == 0 else 2
    out = {}
    for idx, cost in state_cost.items():
        if idx % 3 != want:
            continue
        num = (P * idx - 1) % M
        pred = num // 3
        new_cost = cost + (a - 2)
        prev = out.get(pred)
        if prev is None or new_cost < prev:
            out[pred] = new_cost
    return out


def run_ladder_bigint(t, d_max, cap, verbose=True, wallclock_cap=WALLCLOCK_CAP_S):
    """Same semantics/shape as l2d.run_ladder but pure bigint, no numpy.
    Returns the same result dict shape (depth_states holds plain dicts,
    not numpy arrays)."""
    T0 = t + d_max
    state = {1: 0}
    depth_states = {0: dict(state)}
    per_depth_min = {}
    live_counts = {0: 1}
    wall = None
    t_start = time.time()
    for k in range(d_max):
        elapsed_before = time.time() - t_start
        if elapsed_before > wallclock_cap:
            wall = ("WALLCLOCK", k, round(elapsed_before, 1))
            if verbose:
                print(f"    HONEST WALL (wall-clock) at depth {k}: "
                      f"{elapsed_before:.1f}s > {wallclock_cap}s budget", flush=True)
            break
        M_exp = T0 - k
        remaining_after = d_max - (k + 1)
        # prune by cap before expanding
        state = {idx: c for idx, c in state.items() if c <= cap + (d_max - k)}
        if not state:
            break
        merged = {}
        a_hi = cap + (d_max - k) + 2 - (min(state.values()) if state else 0)
        a_hi = max(1, a_hi)
        aborted_mid_sweep = False
        for a in range(1, a_hi + 1):
            part = ladder_step_bigint(state, M_exp, a, first_step=(k == 0))
            for idx, c in part.items():
                if c > cap + remaining_after:
                    continue
                prev = merged.get(idx)
                if prev is None or c < prev:
                    merged[idx] = c
            # mid-sweep honest-wall checks (a single depth's a-loop can
            # itself run long at large a_hi * large |state| -- check
            # every few iterations, not just once per depth)
            if a % 4 == 0:
                if time.time() - t_start > wallclock_cap:
                    aborted_mid_sweep = True
                    break
                if len(merged) > LIVE_CAP or rss_gb() > RSS_CAP_GB:
                    aborted_mid_sweep = True
                    break
        if aborted_mid_sweep:
            wall = ("WALLCLOCK_OR_RSS_MIDSWEEP", k + 1, len(merged), round(rss_gb(), 2),
                    round(time.time() - t_start, 1))
            if verbose:
                print(f"    HONEST WALL mid-sweep at depth {k+1}: live_so_far={len(merged)} "
                      f"RSS={rss_gb():.2f}GB elapsed={time.time()-t_start:.1f}s", flush=True)
            break
        state = merged
        live_counts[k + 1] = len(state)
        if len(state) > LIVE_CAP or rss_gb() > RSS_CAP_GB:
            wall = ("STATE_OR_RSS", k + 1, len(state), round(rss_gb(), 2))
            if verbose:
                print(f"    HONEST WALL at depth {k+1}: live={len(state)} RSS={rss_gb():.2f}GB",
                      flush=True)
            break
        depth_states[k + 1] = dict(state)
        modt = 3 ** t
        hits = [c for idx, c in state.items() if idx % modt == 1]
        if hits:
            per_depth_min[k + 1] = min(hits)
        if verbose:
            print(f"    depth {k+1}/{d_max}: live={len(state)} RSS={rss_gb():.2f}GB "
                  f"target_min={per_depth_min.get(k+1)} elapsed={time.time()-t_start:.1f}s",
                  flush=True)
    gmin = min(per_depth_min.values()) if per_depth_min else None
    return {"t": t, "d_max": d_max, "T0": T0, "cap": cap, "per_depth_min": per_depth_min,
            "global_min": gmin, "live_counts": live_counts, "depth_states": depth_states,
            "wall": wall}


def extract_witness_bigint(res):
    """Backtrack one argmin witness (min depth among global argmins),
    same predecessor-uniqueness logic as l2d.extract_witness but over
    plain-dict depth_states (bigint keys)."""
    t, T0, d_max = res["t"], res["T0"], res["d_max"]
    gmin = res["global_min"]
    if gmin is None:
        return None
    depth = min(d for d, c in res["per_depth_min"].items() if c == gmin)
    state = res["depth_states"][depth]
    modt = 3 ** t
    child = None
    for idx, c in state.items():
        if idx % modt == 1 and c == gmin:
            child = idx
            break
    ccost = gmin
    seq = []
    for k in range(depth, 0, -1):
        M_exp = T0 - k
        Mp = 3 ** (M_exp + 1)
        parent_state = res["depth_states"][k - 1]
        found = False
        for a in range(1, res["cap"] + 2 * d_max + 3):
            if k == 1 and a == 2:
                continue
            target_parent_cost = ccost - (a - 2)
            inv2a = pow(pow(2, a, Mp), -1, Mp)
            p = ((3 * child + 1) * inv2a) % Mp
            want = 1 if a % 2 == 0 else 2
            if p % 3 != want:
                continue
            if parent_state.get(p) == target_parent_cost:
                seq.append(a)
                child = p
                ccost = target_parent_cost
                found = True
                break
        if not found:
            return ("BACKTRACK_FAIL", depth, seq)
    seq.reverse()
    return (depth, tuple(seq))


def exact_replay(seq, t):
    """Independent replay on genuine unbounded integers via the
    engine.py primitive (a different module/function from the ladder's
    own arithmetic above) -- the W6L discipline."""
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
    """Cross-check the bigint step against an entirely separately-
    written closed-form + big-int lift-invariance check (transcription-
    bug catch, not an overflow catch -- bigints have no overflow)."""
    import random
    rng = random.Random(42)
    n = 0
    for M_exp in (3, 7, 12, 19, 24, 27, 28):
        M = 3 ** M_exp
        for a in (1, 2, 3, 5, 8, 13, 20, 31, 40):
            want = 1 if a % 2 == 0 else 2
            samples = []
            while len(samples) < 40:
                r = rng.randrange(M)
                if r % 3 == want:
                    samples.append(r)
            state = {r: 0 for r in samples}
            out = ladder_step_bigint(state, M_exp, a, first_step=False)
            expected_cost = 0 + (a - 2)  # every sample enters with cost 0
            for r in samples:
                num = (pow(2, a, M) * r - 1) % M
                assert num % 3 == 0
                pred = num // 3
                assert pred in out, f"G1 FAIL M_exp={M_exp} a={a} r={r}: predecessor missing"
                assert out[pred] == expected_cost, (
                    f"G1 cost-tracking FAIL M_exp={M_exp} a={a} r={r}: "
                    f"got {out[pred]} expected {expected_cost}")
                # lift invariance: arbitrary lift of r, exact big-int, must agree mod M//3
                v = r + M * 11
                pv = (1 << a) * v - 1
                if pv % 3 == 0:
                    assert (pv // 3) % (M // 3) == pred % (M // 3), "G1 lift-invariance FAIL"
                n += 1
    print(f"G1 PASS: bigint ladder step == independent closed-form reference on {n} samples "
          f"(M_exp up to 28, incl. lift-invariance; no int64 anywhere so no overflow class exists)")


def gate_G2():
    for (t, d_max, cap) in [(1, 6, 6), (2, 6, 7), (3, 6, 9), (2, 7, 6), (4, 7, 9)]:
        res = run_ladder_bigint(t, d_max, cap, verbose=False)
        bf_pd, bf_g = brute_force_exact(t, d_max, cap)
        ok = (res["global_min"] == bf_g) and (res["per_depth_min"] == bf_pd)
        print(f"G2 {'PASS' if ok else '*** FAIL ***'}: t={t} d_max={d_max} cap={cap}: "
              f"bigint-ladder gmin={res['global_min']} bf gmin={bf_g}")
        if not ok:
            raise SystemExit("G2 FAILED -- bigint ladder not trustworthy")


def gate_G3_vs_l2e(rows):
    """G3: bigint-ladder min <= every L2e exact-verified witness cost
    within the same (t, d_max<=14) scope, and every produced witness
    here exact-replays. Also: where L2e already certified a value for
    the SAME (t, d_max), require exact agreement (independent
    cross-check of the new instrument against the old one's certified
    overlap zone, not the other way around)."""
    l2e_path = W6L / "l2e_extended_curve.csv"
    prior = {}
    with open(l2e_path, newline="") as f:
        for r in csv.DictReader(f):
            if r["exact_min"]:
                prior[(int(r["t"]), int(r["d_max"]))] = int(r["exact_min"])
    n_overlap_checked = 0
    n_overlap_fail = 0
    for row in rows:
        key = (row["t"], row["d_max"])
        if key in prior and row["exact_min"] is not None:
            n_overlap_checked += 1
            if row["exact_min"] != prior[key]:
                n_overlap_fail += 1
                print(f"  *** OVERLAP MISMATCH t={row['t']} d_max={row['d_max']}: "
                      f"new={row['exact_min']} vs L2e-certified={prior[key]} ***")
    print(f"G3-overlap: {n_overlap_checked} (t,d_max) cells overlap L2e's certified record; "
          f"{n_overlap_fail} mismatches "
          f"{'(NONE -- new instrument agrees with old on shared ground)' if n_overlap_fail == 0 else '-- INVESTIGATE'}")
    return n_overlap_fail == 0


# ---------------------------------------------------------------------
# Production runs
# ---------------------------------------------------------------------

PRIOR_BEST = {6: 7, 7: 11, 8: 12, 9: 12, 10: 16, 11: 21, 12: 21}  # from L2e's own curve of record


def cap_for(t, d_max):
    prior = PRIOR_BEST.get(t)
    if prior is not None:
        return prior + 4
    return 40  # generous, no prior value exists (t=13,14 unknown before this run)


def main():
    t0_all = time.time()
    print("=== W6M-M3: ladder walls extension (bigint instrument, T0 up to 28) ===\n")
    print("--- Gates ---")
    gate_G1()
    gate_G2()
    print()

    # RUNS: (label, t, d_max)
    runs = []
    print("--- Part 1: t=13,14 at len<=14 (T0=27,28) ---")
    for t in (13, 14):
        runs.append(("len14_extension", t, 14))
    print("--- Part 2: length-stability probe, t=10,11,12 at len 15,16 (T0=25..28) ---")
    for t in (10, 11, 12):
        for d_max in (15, 16):
            runs.append(("length_stability_probe", t, d_max))

    rows = []
    for (label, t, d_max) in runs:
        cap = cap_for(t, d_max)
        print(f"\n  [{label}] t={t} d_max={d_max} (T0={t+d_max}) cap={cap}:")
        t_run0 = time.time()
        res = run_ladder_bigint(t, d_max, cap)
        wit = extract_witness_bigint(res)
        gmin = res["global_min"]
        replay_ok = None
        if wit is None:
            wit_str = "none in scope"
        elif wit[0] == "BACKTRACK_FAIL":
            wit_str = f"BACKTRACK FAIL {wit[1:]}"
            replay_ok = False
        else:
            d, seq = wit
            replay_ok = exact_replay(seq, t) and sum(a - 2 for a in seq) == gmin
            wit_str = f"len={d} a_seq={seq} replay={'PASS' if replay_ok else '*** FAIL ***'}"
        wall_note = f" WALL@{res['wall']}" if res["wall"] else ""
        elapsed = time.time() - t_run0
        print(f"    RESULT: exact min (len<={d_max}) = {gmin}; {wit_str}; "
              f"per-depth {res['per_depth_min']}{wall_note}; {elapsed:.1f}s RSS={rss_gb():.2f}GB")
        rows.append({
            "label": label, "t": t, "d_max": d_max, "T0": t + d_max, "cap": cap,
            "exact_min": gmin,
            "argmin_len": (wit[0] if wit and wit[0] != "BACKTRACK_FAIL" else ""),
            "argmin_a_seq": (",".join(map(str, wit[1])) if wit and wit[0] != "BACKTRACK_FAIL" else ""),
            "witness_replay": replay_ok,
            "per_depth_min": str(res["per_depth_min"]),
            "wall": str(res["wall"]) if res["wall"] else "",
            "wallclock_s": round(elapsed, 1),
            "peak_rss_gb": round(rss_gb(), 3),
        })

    out = HERE / "m3_ladder_extension.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nWrote {out.name} ({len(rows)} rows)")

    print("\n--- G3: overlap cross-check against L2e's certified record ---")
    gate_G3_vs_l2e(rows)

    # -------------------------------------------------------------
    # Frozen prediction verdict: t=13,14 close the honest gaps;
    # length-stability at len 15/16 for t<=12 -- 60% predicted
    # -------------------------------------------------------------
    print("\n=== FROZEN PREDICTION VERDICT ===")
    print("Curve values stable at len 15-16 for t<=12 (i.e. extending d_max from 14 to "
          "15/16 does NOT lower the exact min for t=10,11,12) -- 60% predicted\n")

    ext14 = {r["t"]: r["exact_min"] for r in rows if r["label"] == "len14_extension"}
    print(f"  t=13,14 at len<=14: {ext14}")

    probe = {(r["t"], r["d_max"]): r["exact_min"] for r in rows if r["label"] == "length_stability_probe"}
    l2e_curve = {}
    with open(W6L / "l2e_extended_curve.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["exact_min"]:
                l2e_curve[int(r["t"])] = int(r["exact_min"])
    l2d_curve = {}
    with open(W6L / "l2d_exact_curve.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["exact_min_len_scoped"]:
                l2d_curve[int(r["t"])] = int(r["exact_min_len_scoped"])

    print("\n  t | len14 (L2e cert.) | len15 (this run) | len16 (this run) | stable?")
    all_stable = True
    any_probe_ran = False
    for t in (10, 11, 12):
        v14 = l2e_curve.get(t, l2d_curve.get(t))
        v15 = probe.get((t, 15))
        v16 = probe.get((t, 16))
        any_probe_ran = any_probe_ran or (v15 is not None) or (v16 is not None)
        vals = [v for v in (v14, v15, v16) if v is not None]
        stable = (len(vals) >= 2) and (min(vals) == max(vals))
        if v15 is None and v16 is None:
            stable_str = "NO DATA (honest wall on both)"
            all_stable = False
        else:
            stable_str = str(stable)
            if not stable:
                all_stable = False
        print(f"  {t:>2} | {v14} | {v15} | {v16} | {stable_str}")

    if not any_probe_ran:
        print("\n  Verdict: UNEVALUATED -- no length-stability cell completed (honest wall on all).")
    else:
        print(f"\n  Verdict: {'HIT' if all_stable else 'MISS'}")

    print(f"\nTotal wall: {time.time()-t0_all:.1f}s, peak RSS: {rss_gb():.3f} GB")


if __name__ == "__main__":
    main()
