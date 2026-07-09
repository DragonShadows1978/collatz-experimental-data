#!/usr/bin/env python3
"""
Task 3, corrected: the discrete-log-based features in invariants.py/correlate.py
are basis-dependent artifacts (verified: dlog differences range over nearly
the full [0,1] interval depending on choice of primitive root g -- see
basis_check.txt). Discarding those. This script computes ONLY genuinely
basis-independent (intrinsic, group-theoretic) invariants of (p, h_p, 2, 3)
and correlates them against rel_hole.
"""
import json
import math
from sympy import isprime, jacobi_symbol

def mult_order(a, p):
    a = a % p
    if a == 0:
        return None
    x = a
    k = 1
    while x != 1:
        x = (x * a) % p
        k += 1
    return k

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
    stat = json.load(open("orbit_stationary.json"))["primes"]
    rows = []
    for p_str, rec in stat.items():
        p = int(p_str)
        h = rec["trig_res"]
        ord2 = mult_order(2, p)
        ord3 = mult_order(3, p)
        ordh = mult_order(h, p)
        is_qr_h = jacobi_symbol(h, p) == 1  # QR test (p prime, so Jacobi=Legendre)
        is_qr_2 = jacobi_symbol(2, p) == 1
        is_qr_3 = jacobi_symbol(3, p) == 1
        g_ord2_ord3 = math.gcd(ord2, ord3)
        row = dict(
            p=p, h=h, ord2=ord2, ord3=ord3, ordh=ordh,
            ord2_eq_ord3=(ord2 == ord3),
            prim2=(ord2 == p - 1), prim3=(ord3 == p - 1), primh=(ordh == p - 1),
            is_qr_h=is_qr_h, is_qr_2=is_qr_2, is_qr_3=is_qr_3,
            gcd_ord2_ord3=g_ord2_ord3,
            ordh_over_p1=ordh / (p - 1),
            h_over_p=h / p,
            twoh_mod_p=(2 * h) % p,
            threeh_mod_p=(3 * h) % p,
            rel_hole=rec["hole"] / rec["pred_1_over_p"],
            hole=rec["hole"],
        )
        rows.append(row)

    print(f"{'p':>3} {'h':>3} {'ord2':>4} {'ord3':>4} {'ordh':>4} {'o2=o3':>5} {'prim2':>5} "
          f"{'prim3':>5} {'primh':>5} {'QR(h)':>5} {'QR(2)':>5} {'QR(3)':>5} {'rel_hole':>9}")
    for r in rows:
        print(f"{r['p']:3d} {r['h']:3d} {r['ord2']:4d} {r['ord3']:4d} {r['ordh']:4d} "
              f"{str(r['ord2_eq_ord3']):>5} {str(r['prim2']):>5} {str(r['prim3']):>5} "
              f"{str(r['primh']):>5} {str(r['is_qr_h']):>5} {str(r['is_qr_2']):>5} {str(r['is_qr_3']):>5} "
              f"{r['rel_hole']:+.4f}")

    rel_holes = [r["rel_hole"] for r in rows]
    feat = {}
    feat["ord2"] = [r["ord2"] for r in rows]
    feat["ord3"] = [r["ord3"] for r in rows]
    feat["ordh"] = [r["ordh"] for r in rows]
    feat["ordh/(p-1)"] = [r["ordh_over_p1"] for r in rows]
    feat["ord2/ord3"] = [r["ord2"] / r["ord3"] for r in rows]
    feat["ord2_eq_ord3(0/1)"] = [1.0 if r["ord2_eq_ord3"] else 0.0 for r in rows]
    feat["prim2(0/1)"] = [1.0 if r["prim2"] else 0.0 for r in rows]
    feat["prim3(0/1)"] = [1.0 if r["prim3"] else 0.0 for r in rows]
    feat["primh(0/1)"] = [1.0 if r["primh"] else 0.0 for r in rows]
    feat["is_qr_h(0/1)"] = [1.0 if r["is_qr_h"] else 0.0 for r in rows]
    feat["is_qr_2(0/1)"] = [1.0 if r["is_qr_2"] else 0.0 for r in rows]
    feat["is_qr_3(0/1)"] = [1.0 if r["is_qr_3"] else 0.0 for r in rows]
    feat["gcd(ord2,ord3)"] = [r["gcd_ord2_ord3"] for r in rows]
    feat["gcd(ord2,ord3)/(p-1)"] = [r["gcd_ord2_ord3"] / (r["p"] - 1) for r in rows]
    feat["h/p"] = [r["h_over_p"] for r in rows]
    feat["p"] = [r["p"] for r in rows]

    print()
    print("=== corrected (basis-independent-only) correlations vs rel_hole ===")
    results = {}
    for name, xs in feat.items():
        r_ = pearson(xs, rel_holes)
        results[name] = r_
        print(f"  r(rel_hole, {name:24s}) = {r_:+.4f}")

    with open("invariants2.json", "w") as f:
        json.dump({"rows": rows, "correlations": results}, f, indent=2, default=str)

if __name__ == "__main__":
    main()
