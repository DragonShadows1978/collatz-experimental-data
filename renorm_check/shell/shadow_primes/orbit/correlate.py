#!/usr/bin/env python3
"""
Task 3 (continued): systematic correlation of candidate invariants vs rel_hole.
Also Task 2: correlation between orbit-measured hole and SHADOW's original
(independent-sample) hit-density deviation.
"""
import json
import math

def pearson(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / n
    vx = sum((x - mx) ** 2 for x in xs) / n
    vy = sum((y - my) ** 2 for y in ys) / n
    if vx <= 0 or vy <= 0:
        return None
    return cov / math.sqrt(vx * vy)

def main():
    inv = json.load(open("invariants.json"))
    stat = json.load(open("orbit_stationary.json"))["primes"]

    # ---- Task 2: orbit hole vs SHADOW's original independent measurement ----
    shadow_err_vs_1p = {
        5: 0.00496, 7: -0.00283, 11: -0.00954, 13: 0.01500,
        17: 0.00420, 19: -0.01499, 23: 0.00288,
    }
    common_p = sorted(shadow_err_vs_1p.keys())
    orbit_hole = [stat[str(p)]["hole"] for p in common_p]
    shadow_err = [shadow_err_vs_1p[p] for p in common_p]
    neg_shadow_err = [-e for e in shadow_err]
    r = pearson(orbit_hole, neg_shadow_err)
    print("=== Task 2: orbit hole vs SHADOW (independent sample) -hit_deviation ===")
    for p in common_p:
        print(f"  p={p:2d}  orbit_hole={stat[str(p)]['hole']:+.5f}  "
              f"-shadow_err={-shadow_err_vs_1p[p]:+.5f}  "
              f"diff={stat[str(p)]['hole']-(-shadow_err_vs_1p[p]):+.5f}")
    print(f"Pearson r (orbit_hole, -shadow_err) across {len(common_p)} shared primes = {r:.4f}")
    sign_match = sum(1 for a, b in zip(orbit_hole, neg_shadow_err) if (a > 0) == (b > 0))
    print(f"Sign agreement: {sign_match}/{len(common_p)} primes")

    print()
    print("=== Task 3: invariant correlations vs rel_hole (all 17 primes) ===")
    rel_holes = [r["rel_hole"] for r in inv]

    feat = {}
    feat["ord2"] = [r["ord2"] for r in inv]
    feat["ord3"] = [r["ord3"] for r in inv]
    feat["ord2/ord3"] = [r["ord2"] / r["ord3"] for r in inv]
    feat["ord3/ord2"] = [r["ord3"] / r["ord2"] for r in inv]
    feat["same_order(0/1)"] = [1.0 if r["same_order"] else 0.0 for r in inv]
    feat["prim2(0/1)"] = [1.0 if r["prim2"] else 0.0 for r in inv]
    feat["prim3(0/1)"] = [1.0 if r["prim3"] else 0.0 for r in inv]
    feat["in_sub3(0/1)"] = [1.0 if r["in_sub3"] else 0.0 for r in inv]
    feat["dlogh/(p-1)"] = [r["dlogh"] / (r["p"] - 1) for r in inv]
    feat["dlog2/(p-1)"] = [r["dlog2"] / (r["p"] - 1) for r in inv]
    feat["dlog3/(p-1)"] = [r["dlog3"] / (r["p"] - 1) for r in inv]
    feat["dlogh_even(0/1)"] = [1.0 if r["dlogh"] % 2 == 0 else 0.0 for r in inv]
    feat["dlogh_minus_dlog3_mod(p-1)"] = [((r["dlogh"] - r["dlog3"]) % (r["p"] - 1)) / (r["p"] - 1) for r in inv]
    feat["dlogh_minus_dlog2_mod(p-1)"] = [((r["dlogh"] - r["dlog2"]) % (r["p"] - 1)) / (r["p"] - 1) for r in inv]
    feat["p"] = [r["p"] for r in inv]
    feat["1/p"] = [1.0 / r["p"] for r in inv]

    results = {}
    for name, xs in feat.items():
        r_ = pearson(xs, rel_holes)
        results[name] = r_
        print(f"  r(rel_hole, {name:32s}) = {r_:+.4f}" if r_ is not None else f"  r(rel_hole, {name}) = n/a")

    with open("correlate.json", "w") as f:
        json.dump({"task2_r": r, "task2_sign_match": f"{sign_match}/{len(common_p)}",
                    "task3_correlations": results}, f, indent=2)

if __name__ == "__main__":
    main()
