#!/usr/bin/env python3
"""
W6L-L2e -- Ladder extension to T0 <= 24 via a two-limb modular
multiply (the l2d instrument was int64-limited to T0 <= 19 because it
computes (2^a mod M) * idx directly; at M = 3^20 that product can
exceed 2^63). The two-limb form splits P = P_hi*3^10 + P_lo:
    P*idx mod M = ((P_lo*idx) mod M + 3^10*((P_hi*idx) mod 3^(Mexp-10))) mod M
with every intermediate product < 3^38 < 2^63 for Mexp <= 24
(P_lo < 3^10, idx < 3^Mexp <= 3^24; P_hi < 3^(Mexp-10)).

INSTRUMENT SWAP, EXPLICIT: this script replaces l2d.ladder_step with
the two-limb version and RE-RUNS ALL GATES on the swapped instrument
(G1 extended to Mexp up to 24 vs Python big-int reference incl.
lift-invariance; G2 brute-force cross-checks; plus every witness
exact-replayed as before). Nothing from l2d's runs is reused except
code; all numbers below are freshly computed under the new step.

Scope closed here (the l2d honest walls):
  t=6..10: d_max=14 (T0=20..24)
  t=11: d_max=13; t=12: d_max=12; t=13: d_max=11; t=14: d_max=10 (T0=24)
Caps: current best + 1 where a value/witness exists (sound: pruned
completions end above cap; finding anything <= cap-1 beats it, and
reproducing the known value certifies it as the scoped min). For
t=12..14 (unknown): cap 36, honest wall if live states explode.
"""
from __future__ import annotations

import csv
import sys
import time
import numpy as np
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import l2d_exact_ladder as l2d  # noqa: E402
from l2d_exact_ladder import (  # noqa: E402
    extract_witness, exact_replay, brute_force_exact, rss_gb,
)

LIMB = 3 ** 10


def ladder_step_two_limb(idx, cost, M_exp, a, first_step):
    """Two-limb exact ladder step, valid for M_exp <= 24 (all
    intermediate products < 3^38 < 2^63). Same semantics as
    l2d.ladder_step, verified by the gates below."""
    if first_step and a == 2:
        return None, None
    assert M_exp <= 24, "two-limb bound exceeded"
    M = 3 ** M_exp
    cls = idx % 3
    want = 1 if a % 2 == 0 else 2
    sel = cls == want
    if not sel.any():
        return None, None
    sub = idx[sel]
    subc = cost[sel]
    P = pow(2, a, M)
    if M_exp <= 19:
        prod = (P * sub) % M
    else:
        P_hi, P_lo = divmod(P, LIMB)
        M_hi = 3 ** (M_exp - 10)
        term1 = (P_lo * sub) % M
        term2 = ((P_hi * sub) % M_hi) * LIMB
        prod = (term1 + term2) % M
    num = prod - 1
    num[num < 0] += M
    pred = num // 3
    return pred, subc + np.int32(a - 2)


# EXPLICIT instrument swap (documented in module docstring):
l2d.ladder_step = ladder_step_two_limb


def gate_G1_extended():
    rng = np.random.default_rng(7)
    n = 0
    for M_exp in (3, 10, 15, 19, 20, 22, 24):
        M = 3 ** M_exp
        for a in (1, 2, 3, 5, 8, 13, 20, 31):
            want = 1 if a % 2 == 0 else 2
            raw = rng.integers(0, M, size=300, dtype=np.int64)
            raw = raw[(raw % 3) == want]
            if len(raw) == 0:
                continue
            pred, _ = ladder_step_two_limb(raw, np.zeros(len(raw), dtype=np.int32),
                                            M_exp, a, first_step=False)
            for r, p in zip(raw.tolist(), pred.tolist()):
                ref = (pow(2, a, M) * r - 1) % M   # Python big-int, no overflow possible
                assert ref % 3 == 0
                ref //= 3
                assert p == ref, f"G1-ext FAIL M=3^{M_exp} a={a} r={r}: {p} != {ref}"
                v = r + M * 5  # lift-invariance
                pv = (1 << a) * v - 1
                if pv % 3 == 0:
                    assert (pv // 3) % (M // 3) == ref % (M // 3), "lift-invariance FAIL"
                n += 1
    print(f"G1-ext PASS: two-limb step == big-int reference on {n} samples "
          f"(Mexp up to 24, incl. lift-invariance)")


def gate_G2_rerun():
    for (t, d_max, cap) in [(1, 6, 6), (2, 6, 7), (3, 6, 9), (2, 7, 6), (4, 7, 9)]:
        res = l2d.run_ladder(t, d_max, cap, verbose=False)
        bf_pd, bf_g = brute_force_exact(t, d_max, cap)
        ok = (res["global_min"] == bf_g) and (res["per_depth_min"] == bf_pd)
        print(f"G2 {'PASS' if ok else '*** FAIL ***'} (two-limb): t={t} d_max={d_max} "
              f"cap={cap}: gmin {res['global_min']} vs bf {bf_g}")
        if not ok:
            raise SystemExit("G2 FAILED on the two-limb instrument")


RUNS = [
    # (t, d_max, cap) -- caps = best-known + 1 where known
    (6, 14, 8),
    (7, 14, 12),
    (8, 14, 13),
    (9, 14, 13),
    (10, 14, 29),
    (11, 13, 30),
    (12, 12, 36),
    (13, 11, 36),
    (14, 10, 36),
]

PRIOR_BEST = {6: 7, 7: 11, 8: 12, 9: 12, 10: 28, 11: 29}  # exact-verified values in play


def main():
    t0_all = time.time()
    print("=== L2e: ladder extension (two-limb, T0<=24) ===\n--- Gates on swapped instrument ---")
    gate_G1_extended()
    gate_G2_rerun()
    print()

    rows = []
    for (t, d_max, cap) in RUNS:
        print(f"  t={t} (T0={t+d_max}, d_max={d_max}, cap={cap}):")
        t0 = time.time()
        res = l2d.run_ladder(t, d_max, cap)
        wit = extract_witness(res)
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
        prior = PRIOR_BEST.get(t)
        note = ""
        if prior is not None and gmin is not None:
            if gmin < prior:
                note = f" [NEW MINIMUM, beats prior {prior}]"
            elif gmin == prior:
                note = f" [confirms prior {prior} as the len<={d_max} min]"
            else:
                note = f" [in-scope min above prior verified {prior} -- INVESTIGATE]"
        wall_note = f" WALL@{res['wall']}" if res["wall"] else ""
        print(f"    RESULT: exact min (len<={d_max}) = {gmin}; {wit_str}; "
              f"per-depth {res['per_depth_min']}{note}{wall_note}; "
              f"{time.time()-t0:.1f}s RSS={rss_gb():.2f}GB")
        rows.append({"t": t, "d_max": d_max, "T0": t + d_max, "cap": cap,
                     "exact_min": gmin,
                     "argmin_len": (wit[0] if wit and wit[0] != "BACKTRACK_FAIL" else ""),
                     "argmin_a_seq": (",".join(map(str, wit[1])) if wit and wit[0] != "BACKTRACK_FAIL" else ""),
                     "witness_replay": replay_ok,
                     "per_depth_min": str(res["per_depth_min"]),
                     "wall": str(res["wall"]) if res["wall"] else ""})
        res["depth_states"] = None

    out = HERE / "l2e_extended_curve.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nWrote {out.name}")
    print(f"Total wall: {time.time()-t0_all:.1f}s, peak RSS: {rss_gb():.3f} GB")


if __name__ == "__main__":
    main()
