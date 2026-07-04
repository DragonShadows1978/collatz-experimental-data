#!/usr/bin/env python3
"""
W6L-L3 -- J4 residual structure (the third-structure hunt), per
W6L_CANONICAL_CONSOLIDATION_ORDER.md section L3.

PREMISE CORRECTION (load-bearing, verified twice before this script
and re-verified below): the ORDER states "The model overpredicted
95.7% -- something makes real chains CHEAPER than ray-descent +
ray-riding." The dump says the opposite: 95.7% of mismatch rows have
model_prediction < D_actual (the model UNDERpredicts the true cost;
real chains are MORE EXPENSIVE than the ray decomposition), and only
4.3% are overpredictions. The order's number (95.7) matches the
dump's negative-diff share exactly, so the direction label in the
order is inverted relative to its own source data. Consequence for
the hypothesis menu: (i) mixed itineraries and (ii) entry-segment
credits are CHEAPENING mechanisms -- they can only address the 4.3%
minority. The 95.7% majority needs a cost-INCREASING mechanism; the
natural candidate is the composition coupling just measured in L4
(ray-riding + entry does not compose additively; the entry's parity
pattern taxes the join).

INSTRUMENTS:
  - Classification: pure data analysis of w6j dumps (order-immune
    inputs per SYNTHESIS's W6J-J4 annotation).
  - Chain extraction: h2_two_ray_model.bfs_Dm_target_chain_with_
    residues -- Path-B-derived machinery, used ONLY on the J4 input
    class whose order-immunity SYNTHESIS certifies ("W6J-J4: STANDS
    ... (order-immune inputs)"; mechanical words are reversal-closed
    families per the K0 scope annotation). Per the instrument rule's
    escape clause this use is declared, and it is additionally gated
    here: every extracted chain's D must equal the dump's D_actual
    for that key, and a small-m Path-C cross-check (canonical
    anchored DFS) is run at m=3..4 to document which canonical
    variant the ground truth corresponds to.
  - Third-structure hunt: pure residue arithmetic (order-free).

Frozen prediction (Fable, 65%): (ii) + (i) explain >= 90% of
residuals; no third ray exists.
"""
from __future__ import annotations

import csv
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
W6H = HERE.parent / "w6h"
W6J = HERE.parent / "w6j"
W6E = HERE.parent / "w6e"
sys.path.insert(0, str(W6E))
sys.path.insert(0, str(W6H))
sys.path.insert(0, str(HERE.parent / "w6f"))

from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402
from h2_two_ray_model import FAMILIES, bfs_Dm_target_chain_with_residues  # noqa: E402
from e1_walkers import backward_letters  # noqa: E402

C_PROXY = 12


def prox(r, target, mod_exp_max):
    """3-adic proximity: max t <= mod_exp_max with r == target mod 3^t."""
    t = 0
    while t < mod_exp_max and (r - target) % (3 ** (t + 1)) == 0:
        t += 1
    return t


def cycle_shadows(k):
    """Residue shadows mod 3^k of the known non-positive 3x+1 cycles:
    {1} (a=2), {-1} (a=1), {-5,-7} (2-cycle), {-17,-25,-37,-55,-41}
    (5-cycle)."""
    M = 3 ** k
    return {
        "+1": [1 % M], "-1": [(-1) % M],
        "-5/-7": [(-5) % M, (-7) % M],
        "-17cyc": [(-17) % M, (-25) % M, (-37) % M, (-55) % M, (-41) % M],
    }


def main():
    t0 = time.time()

    # ------------------------------------------------------------------
    # 0. Premise re-verification (from the dump itself)
    # ------------------------------------------------------------------
    dump = list(csv.DictReader(open(W6J / "j4_residual_mismatches_dump.csv")))
    fit = list(csv.DictReader(open(W6J / "j4_repaired_fit.csv")))
    n_over = sum(1 for r in dump if int(r["model_prediction"]) > int(r["D_actual"]))
    n_under = sum(1 for r in dump if int(r["model_prediction"]) < int(r["D_actual"]))
    print("=== 0. PREMISE RE-VERIFICATION ===")
    print(f"mismatch rows: {len(dump)}; model OVERpredicts (model>actual): {n_over} "
          f"({100*n_over/len(dump):.1f}%); model UNDERpredicts (model<actual): {n_under} "
          f"({100*n_under/len(dump):.1f}%)")
    print("The order's '95.7% overpredicted / real chains CHEAPER' is INVERTED vs its "
          "own source: 95.7% are UNDERpredictions -- real chains are MORE EXPENSIVE "
          "than ray-descent + ray-riding.\n")

    # dedupe (the dump repeats keys across the mod-27/mod-81 sweeps)
    keys = {}
    for r in dump:
        k = (r["family"], int(r["m"]), int(r["target_r"]))
        if k not in keys:
            keys[k] = {"D_actual": int(r["D_actual"]),
                       "model": int(r["model_prediction"]),
                       "best_ray": r["best_ray"], "entry_len": int(r["entry_len"]),
                       "entry_cost": int(r["entry_cost"]), "ray_cost": int(r["ray_cost"]),
                       "mult": 0}
        keys[k]["mult"] += 1
    print(f"deduped residual keys: {len(keys)} (from {len(dump)} rows)")

    controls = set()
    for r in fit:
        if r["match"] == "True":
            controls.add((r["family"], int(r["m"]), int(r["target_r"])))
    print(f"control keys (model exact): {len(controls)}\n")

    # ------------------------------------------------------------------
    # 1. Classification
    # ------------------------------------------------------------------
    print("=== 1. RESIDUAL CLASSIFICATION ===")
    rows_out = []
    for (fam, m, tr), info in sorted(keys.items()):
        diff = info["model"] - info["D_actual"]
        kmax = min(m, 4)
        shadows = cycle_shadows(kmax)
        prox_map = {name: max(prox(tr, s, kmax) for s in vals)
                    for name, vals in shadows.items()}
        rows_out.append({
            "family": fam, "m": m, "target_r": tr, "D_actual": info["D_actual"],
            "model": info["model"], "diff": diff, "sign": "over" if diff > 0 else "under",
            "r_mod9": tr % 9, "r_mod27": tr % 27,
            "prox_+1": prox_map["+1"], "prox_-1": prox_map["-1"],
            "prox_-5/-7": prox_map["-5/-7"], "prox_-17cyc": prox_map["-17cyc"],
            "mult": info["mult"],
        })
    with open(HERE / "l3_residual_classification.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        w.writeheader()
        for r in rows_out:
            w.writerow(r)
    print(f"Wrote l3_residual_classification.csv ({len(rows_out)} deduped keys)")

    print("\n  diff distribution (deduped):",
          dict(sorted(Counter(r['diff'] for r in rows_out).items())))
    print("  r mod 9 distribution (residuals):",
          dict(sorted(Counter(r['r_mod9'] for r in rows_out).items())))
    ctrl_mod9 = Counter(k[2] % 9 for k in controls)
    print("  r mod 9 distribution (controls): ", dict(sorted(ctrl_mod9.items())))

    print("\n  3-adic proximity to cycle shadows (mean, residuals vs controls):")
    for name in ("+1", "-1", "-5/-7", "-17cyc"):
        res_p = [r[f"prox_{name}"] for r in rows_out]
        ctl_p = []
        for (fam, m, tr) in controls:
            kmax = min(m, 4)
            vals = cycle_shadows(kmax)[name]
            ctl_p.append(max(prox(tr, s, kmax) for s in vals))
        mr = sum(res_p) / len(res_p)
        mc = sum(ctl_p) / len(ctl_p) if ctl_p else float("nan")
        print(f"    {name:>8}: residual mean {mr:.3f} vs control mean {mc:.3f} "
              f"(residual max {max(res_p)}, control max {max(ctl_p) if ctl_p else '-'})")

    # ------------------------------------------------------------------
    # 2. (iii) third-structure enumeration: 1-step and 2-step fixed points
    # ------------------------------------------------------------------
    print("\n=== 2. (iii) FIXED-POINT ENUMERATION mod 27 / 81 ===")
    for k in (3, 4):
        M = 3 ** k
        fps1 = {}
        for a in range(1, 7):
            den = (3 - pow(2, a, M)) % M     # always a unit mod 3^k
            fps1[a] = (-pow(den, -1, M)) % M
        print(f"  mod {M}: 1-step fixed points r_a = -1/(3-2^a): {fps1}")
        fps2 = {}
        for a1 in range(1, 5):
            for a2 in range(1, 5):
                den = (9 - pow(2, a1 + a2, M)) % M
                num = (-(3 + pow(2, a1, M))) % M
                fps2[(a1, a2)] = (num * pow(den, -1, M)) % M
        print(f"  mod {M}: 2-step fixed points (a1,a2) in 1..4^2 -> distinct residues "
              f"{sorted(set(fps2.values()))}")
        print(f"    (-5={(-5) % M}, -7={(-7) % M} mod {M}; the (1,2)/(2,1) fixed points "
              f"{fps2[(1, 2)]}, {fps2[(2, 1)]} are the -5/-7 negative-cycle shadow)")

    fp_set27 = set()
    M = 27
    for a in range(1, 7):
        den = (3 - pow(2, a, M)) % M
        fp_set27.add((-pow(den, -1, M)) % M)
    for a1 in range(1, 5):
        for a2 in range(1, 5):
            den = (9 - pow(2, a1 + a2, M)) % M
            num = (-(3 + pow(2, a1, M))) % M
            fp_set27.add((num * pow(den, -1, M)) % M)
    n_res_on = sum(1 for r in rows_out if (r["target_r"] % 27) in fp_set27)
    n_ctl_on = sum(1 for kk in controls if (kk[2] % 27) in fp_set27)
    print(f"\n  keys ON a 1/2-step fixed-point class mod 27 ({len(fp_set27)} classes: "
          f"{sorted(fp_set27)}):")
    print(f"    residuals: {n_res_on}/{len(rows_out)} ({100*n_res_on/len(rows_out):.1f}%) | "
          f"controls: {n_ctl_on}/{len(controls)} ({100*n_ctl_on/len(controls):.1f}%) | "
          f"uniform expectation ~{100*len(fp_set27)/27:.1f}%")

    # ------------------------------------------------------------------
    # 3. Mechanism tests on extracted true chains
    # ------------------------------------------------------------------
    print("\n=== 3. MECHANISM TESTS (true optimal chains, sampled keys) ===")
    sample = []
    per_fam_m = Counter()
    for (fam, m, tr), info in sorted(keys.items()):
        if m <= 6:
            sample.append((fam, m, tr, info))
        elif m in (7, 8) and per_fam_m[(fam, m)] < 6:
            sample.append((fam, m, tr, info))
            per_fam_m[(fam, m)] += 1
    print(f"  sample: {len(sample)} keys (all m<=6 + up to 6 per family at m=7,8)")

    mech_rows = []
    n_gate_fail = 0
    for (fam, m, tr, info) in sample:
        fn = FAMILIES[fam]
        D_chain, chain, residues = bfs_Dm_target_chain_with_residues(
            fn, m, C_PROXY, target_r=tr, anchor_steps=53, family_name=fam)
        if D_chain != info["D_actual"]:
            n_gate_fail += 1
            continue
        Mm = 3 ** m
        ray_p, ray_m = 1 % Mm, Mm - 1
        n57 = {(-5) % Mm, (-7) % Mm}
        touches = []
        for i, r in enumerate(residues):
            if r == ray_p:
                touches.append((i, "+1"))
            elif r == ray_m:
                touches.append((i, "-1"))
            elif r in n57:
                touches.append((i, "-5/-7"))
        distinct = sorted(set(t[1] for t in touches))
        if not touches:
            mech = "D_no_ray_contact"
        elif "-5/-7" in distinct:
            mech = "C_third_shadow_touch"
        elif len([x for x in distinct if x in ("+1", "-1")]) > 1:
            mech = "A_mixed_itinerary"
        elif distinct == ["+1"]:
            mech = ("B_rides+1_costlier_than_model" if info["model"] < info["D_actual"]
                    else "B_rides+1_cheaper_than_model")
        else:
            mech = ("E_rides-1_costlier" if info["model"] < info["D_actual"]
                    else "E_rides-1_cheaper")
        mech_rows.append({"family": fam, "m": m, "target_r": tr,
                          "D_actual": info["D_actual"], "model": info["model"],
                          "diff": info["model"] - info["D_actual"], "mechanism": mech,
                          "ray_touches": ";".join(f"{i}:{t}" for i, t in touches[:8]),
                          "chain": ";".join(f"{c},{a}" for c, a in chain)})
    print(f"  extraction gate: {len(mech_rows)} chains reproduce D_actual exactly, "
          f"{n_gate_fail} FAILED the gate{' -- INVESTIGATE' if n_gate_fail else ''}")
    with open(HERE / "l3_mechanism_sample.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(mech_rows[0].keys()))
        w.writeheader()
        for r in mech_rows:
            w.writerow(r)
    print(f"  Wrote l3_mechanism_sample.csv ({len(mech_rows)} rows)")
    print("  (touch classification is EXACT-residue contact mod 3^m -- conservative; "
          "coarse mod-27 proximity is in section 1's table)")

    mc = Counter(r["mechanism"] for r in mech_rows)
    print("\n  mechanism distribution (sampled true chains):")
    for k2, v in mc.most_common():
        print(f"    {k2:<36} {v:>4}  ({100*v/len(mech_rows):.1f}%)")
    by_sign = defaultdict(Counter)
    for r in mech_rows:
        by_sign["under" if r["diff"] < 0 else "over"][r["mechanism"]] += 1
    for sign, cnt in by_sign.items():
        print(f"  {sign}-prediction keys: {dict(cnt)}")

    # ------------------------------------------------------------------
    # 4. Path-C small-m cross-check (m=3..4)
    # ------------------------------------------------------------------
    print("\n=== 4. Path-C cross-check (m=3..4, canonical anchored DFS) ===")

    def anchored_D(anchor_int, letters, ceiling_on, a_cap=40):
        m2 = len(letters)
        best = [None]

        def dfs(j, rho, running, mx):
            if best[0] is not None and mx >= best[0]:
                return
            if j == m2:
                if best[0] is None or mx < best[0]:
                    best[0] = mx
                return
            c = letters[j]
            par = forced_parity_for_backward_step(rho)
            if par is None:
                return
            a_min = 2 if par == 0 else 1
            for a in range(a_min, a_min + a_cap, 2):
                run2 = running + (a - c)
                if ceiling_on and run2 < 0:
                    continue
                dfs(j + 1, backward_predecessor_exact(rho, a), run2, max(mx, run2))

        dfs(0, anchor_int, 0, 0)
        return best[0]

    n_ok = {"free": 0, "ceil": 0}
    n_tot = 0
    for (fam, m, tr, info) in sample:
        if m > 4:
            continue
        n_tot += 1
        letters = backward_letters(FAMILIES[fam], m, anchor_steps=53)
        anchor = tr % (3 ** m)
        if anchor % 3 == 0:
            continue  # class-0 anchor: no backward move at all
        for variant, con in (("free", False), ("ceil", True)):
            got = anchored_D(anchor, letters, con)
            if got == info["D_actual"]:
                n_ok[variant] += 1
    print(f"  {n_tot} keys at m<=4: Path-C anchored-DFS == D_actual: "
          f"ceiling-off {n_ok['free']}/{n_tot}, ceiling-on {n_ok['ceil']}/{n_tot}")
    print("  (documents which canonical variant the Path-B ground truth corresponds to "
          "on this input class)")

    # ------------------------------------------------------------------
    # 5. Frozen prediction verdict
    # ------------------------------------------------------------------
    print("\n=== 5. FROZEN PREDICTION VERDICT ===")
    n_under_s = sum(1 for r in mech_rows if r["diff"] < 0)
    n_i_ii = sum(1 for r in mech_rows
                 if r["mechanism"] in ("A_mixed_itinerary", "B_rides+1_cheaper_than_model",
                                        "E_rides-1_cheaper"))
    print(f"  (i)+(ii)-class (cheapening) mechanisms cover {n_i_ii}/{len(mech_rows)} sampled "
          f"residuals ({100*n_i_ii/len(mech_rows):.1f}%).")
    print(f"  Prediction requires >= 90%: {'HIT' if n_i_ii >= 0.9 * len(mech_rows) else 'MISS'} "
          f"-- structurally forced by the premise inversion: {n_under_s}/{len(mech_rows)} "
          f"sampled residuals are UNDERpredictions (real chains costlier), which no "
          f"cheapening mechanism can explain.")
    third = mc.get("C_third_shadow_touch", 0)
    print(f"  'No third ray exists' half: sampled chains touching -5/-7 shadows exactly: "
          f"{third}; fixed-point-class enrichment vs controls: section 2.")
    print(f"\nTotal wall: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
