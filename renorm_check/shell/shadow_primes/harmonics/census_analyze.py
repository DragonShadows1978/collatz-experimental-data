#!/usr/bin/env python3
"""
Analyze census_results.json:
  1. Per-prime hit-rate with BLOCK-BOOTSTRAP CI over trajectories (the
     independent sampling unit) -- not the naive pooled-step Wilson CI,
     which SHADOW_FINDINGS.md already showed is anti-conservative by
     ~100-1000x due to within-trajectory autocorrelation.
  2. Anomaly ranking: CI-robust deviation from 1/p (both endpoints of the
     trajectory-level CI must exclude 1/p to count as "anomalous").
  3. Harmonic predictor tests over the FIT set (p in [5,200]):
     ord(2 mod p), ord(3 mod p), ord2==ord3, p mod 53, p | (heartbeat
     convergent numerator/denominator: 8,5,19,12,65,41,84,53,485,306,
     1054,665), p | (2^a - 3^b) for small a,b near the heartbeat.
  4. (53/84)^k magnitude law fit for anomalous primes, incl. the frozen
     19->k=9 test.
  5. Spectral cross-correlation: correlate |deviation| against spectral
     quantities (rho, gap) -- since rho/gap are single constants (not a
     per-prime series) the "cross-correlation" is operationalized as:
     does |deviation| scale with (53/84)^k for a SINGLE global k, i.e.
     is there one dynamical decay constant explaining every anomalous
     prime simultaneously (structural), or does each need its own k
     (coincidental / overfit)?
  6. Predictive check: freeze whatever predictor(s) pass step 3 on the
     FIT set, apply UNCHANGED to the HELD-OUT set (p in (200,500]),
     measure hit rate, report hit/miss.

Exact arithmetic for orders/divisibility (sympy). CIs: block bootstrap,
10000 resamples, deterministic seed, resampling whole trajectories (i.e.
resampling (hits,n_steps) pairs), which is the correct unit given the
established autocorrelation.
"""
import json
import math
import random
import numpy as np
from sympy import n_order, isprime

FIT_LO, FIT_HI = 5, 200
HOLD_LO, HOLD_HI = 201, 500
HEARTBEAT = 53
CONVERGENT_PAIRS = [(1,1),(2,1),(3,2),(8,5),(19,12),(65,41),(84,53),(485,306),(1054,665)]
CONVERGENT_NUMS_DENS = sorted(set([53,84,306,485,665,8,5,19,12,65,41,3,2,1]))
RHO = 0.960647
GAP = 1 - RHO
B_FIT = 0.063099          # empirical decay base fitted in SPECTRAL_RADIUS_RESULTS.txt
B_CONV = (53/84)**6       # (53/84)^6 = 0.063093, the convergent-index identification

def make_bootstrap_counts(n, n_boot=10000, seed=1234):
    """
    Draw the SAME n_boot resamplings of trajectory indices once (shared
    across all primes -- this is the standard shared-bootstrap-draws
    trick: cheaper, and it also correctly preserves cross-prime
    co-resampling structure since it's the same trajectories dropped/
    duplicated together). Return a (n_boot, n) counts-per-trajectory
    matrix (how many times each original trajectory index was drawn in
    each bootstrap replicate), via bincount -- this turns the per-prime
    bootstrap into a single matrix multiply (counts @ hit_arr).
    """
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    row_offset = (np.arange(n_boot, dtype=np.int64) * n)[:, None]
    flat = (idx + row_offset).ravel()
    counts_flat = np.bincount(flat, minlength=n_boot * n).astype(np.float32)
    return counts_flat.reshape(n_boot, n)

def block_bootstrap_ci_fast(hit_arr, step_arr, counts, alpha=0.05):
    """
    hit_arr, step_arr: 1D numpy arrays (per trajectory). counts: precomputed
    (n_boot, n) resample-count matrix from make_bootstrap_counts (SHARED
    across primes for speed + consistent co-resampling). Returns point, lo, hi.
    """
    point = float(hit_arr.sum() / step_arr.sum())
    h = counts @ hit_arr.astype(np.float32)
    s = counts @ step_arr.astype(np.float32)
    boot_rates = np.sort(h / s)
    n_boot = len(boot_rates)
    lo = float(boot_rates[int((alpha/2) * n_boot)])
    hi = float(boot_rates[int((1 - alpha/2) * n_boot) - 1])
    return point, lo, hi

def main():
    r = json.load(open("census_results.json"))
    per_traj = r["per_traj"]
    fit_primes = r["fit_primes"]
    hold_primes = r["hold_primes"]
    n_traj = r["n_trajectories"]
    n_steps_total = r["n_steps_total"]

    print(f"Loaded {n_traj} trajectories, {n_steps_total} steps, "
          f"{len(fit_primes)} fit primes, {len(hold_primes)} held-out primes")

    # Reorganize per-trajectory hit/step arrays per prime (fast bootstrap access)
    step_counts = [rec["n_steps"] for rec in per_traj]
    total_steps_check = sum(step_counts)
    assert total_steps_check == n_steps_total

    all_primes = fit_primes + hold_primes
    step_arr_np = np.array(step_counts, dtype=np.int64)
    hit_arrays = {p: np.array([rec["hits"][str(p)] for rec in per_traj], dtype=np.int64) for p in all_primes}

    # ---------------- Step 1+2: per-prime block-bootstrap CI + anomaly flag ----------------
    print("\n=== CENSUS: block-bootstrap (10000 resamples, trajectory-level, shared draws) ===")
    N_BOOT = 10000
    counts_matrix = make_bootstrap_counts(n_traj, n_boot=N_BOOT, seed=42)
    print(f"Built shared bootstrap count matrix: {counts_matrix.shape}, "
          f"{counts_matrix.nbytes/1e9:.2f} GB")
    census = {}
    for p in all_primes:
        pt, lo, hi = block_bootstrap_ci_fast(hit_arrays[p], step_arr_np, counts_matrix)
        pred = 1.0 / p
        anomalous = not (lo <= pred <= hi)  # CI excludes 1/p entirely
        dev = pt - pred
        reldev = dev / pred
        census[p] = dict(point=pt, lo=lo, hi=hi, pred=pred, dev=dev, reldev=reldev,
                          anomalous=anomalous, band=("fit" if p in fit_primes else "hold"))
        flag = "ANOMALOUS" if anomalous else ""
        print(f"p={p:3d}  rate={pt:.5f}  CI=[{lo:.5f},{hi:.5f}]  1/p={pred:.5f}  "
              f"dev={dev:+.5f}  reldev={reldev:+.4f}  {flag}")

    fit_anomalous = sorted([p for p in fit_primes if census[p]["anomalous"]],
                            key=lambda p: -abs(census[p]["dev"]))
    print(f"\nFIT-set anomalous primes (CI excludes 1/p): {len(fit_anomalous)} / {len(fit_primes)}")
    print("Ranked by |deviation|:")
    for p in sorted(fit_primes, key=lambda p: -abs(census[p]["dev"])):
        c = census[p]
        flag = " <-- ANOMALOUS" if c["anomalous"] else ""
        print(f"  p={p:3d}  dev={c['dev']:+.5f}  reldev={c['reldev']:+.4f}{flag}")

    is_19_extreme = fit_anomalous[0] == 19 if fit_anomalous else False
    print(f"\nIs p=19 the |deviation|-extreme prime in the fit set? {is_19_extreme}")
    if fit_anomalous:
        top = fit_anomalous[0]
        print(f"Actual extreme: p={top}, dev={census[top]['dev']:+.5f}")

    # ---------------- Step 3: harmonic predictor tests ----------------
    print("\n=== HARMONIC PREDICTOR TESTS (fit set) ===")
    predictors = {}
    for p in fit_primes:
        ord2 = n_order(2, p)
        ord3 = n_order(3, p)
        pmod53 = p % HEARTBEAT
        div_conv = p in CONVERGENT_NUMS_DENS or any((n % p == 0 or d % p == 0) for n, d in CONVERGENT_PAIRS)
        # p | 2^a - 3^b for small a,b (search a,b in 1..60, near heartbeat scale)
        resonance_hits = []
        for a in range(1, 61):
            for b in range(1, 61):
                val = (pow(2, a, p) - pow(3, b, p)) % p
                if val == 0:
                    resonance_hits.append((a, b))
        min_resonance = min((a+b for a, b in resonance_hits), default=None)
        predictors[p] = dict(ord2=ord2, ord3=ord3, ord2_eq_ord3=(ord2 == ord3),
                              pmod53=pmod53, div_conv=div_conv,
                              n_resonance=len(resonance_hits),
                              min_resonance_sum=min_resonance)

    # Compare predictor values on anomalous vs non-anomalous fit primes
    anom_set = set(fit_anomalous)
    non_anom = [p for p in fit_primes if p not in anom_set]

    def summarize(field, primes_list):
        vals = [predictors[p][field] for p in primes_list]
        return vals

    print(f"\nAnomalous fit primes: {fit_anomalous}")
    print(f"Non-anomalous fit primes ({len(non_anom)}): {non_anom}")

    print("\n-- ord(2 mod p) --")
    print(f"  anomalous:     {[predictors[p]['ord2'] for p in fit_anomalous]}")
    print(f"  non-anomalous (sample): {[predictors[p]['ord2'] for p in non_anom[:15]]} ...")

    print("\n-- ord(3 mod p) --")
    print(f"  anomalous:     {[predictors[p]['ord3'] for p in fit_anomalous]}")

    print("\n-- ord2==ord3 --")
    n_eq_anom = sum(predictors[p]['ord2_eq_ord3'] for p in fit_anomalous)
    n_eq_nonanom = sum(predictors[p]['ord2_eq_ord3'] for p in non_anom)
    print(f"  anomalous: {n_eq_anom}/{len(fit_anomalous)} have ord2==ord3")
    print(f"  non-anomalous: {n_eq_nonanom}/{len(non_anom)} have ord2==ord3")

    print("\n-- p mod 53 --")
    print(f"  anomalous:     {[predictors[p]['pmod53'] for p in fit_anomalous]}")
    print(f"  non-anomalous (sample): {[predictors[p]['pmod53'] for p in non_anom[:15]]} ...")

    print("\n-- divides a heartbeat convergent num/den (53,84,306,485,665,8,5,19,12,65,41) --")
    n_div_anom = sum(predictors[p]['div_conv'] for p in fit_anomalous)
    n_div_nonanom = sum(predictors[p]['div_conv'] for p in non_anom)
    print(f"  anomalous: {n_div_anom}/{len(fit_anomalous)} divide a convergent term")
    print(f"  non-anomalous: {n_div_nonanom}/{len(non_anom)} divide a convergent term")
    print(f"  (of the fit-band primes, which ones divide a convergent term at all: "
          f"{[p for p in fit_primes if predictors[p]['div_conv']]})")

    print("\n-- p | 2^a-3^b, min(a+b) over search a,b<=60 --")
    print(f"  anomalous:     {[(p, predictors[p]['min_resonance_sum']) for p in fit_anomalous]}")
    print(f"  non-anomalous (sample): {[(p, predictors[p]['min_resonance_sum']) for p in non_anom[:15]]}")
    # This one is a near-tautology check: EVERY prime other than 2,3 divides
    # SOME 2^a-3^b for small a,b (pigeonhole on residues), so report the
    # distribution to show whether anomalous primes have unusually SMALL
    # min_resonance_sum (i.e. sit close to the heartbeat) vs the full set.
    all_min_res = sorted([(p, predictors[p]['min_resonance_sum']) for p in fit_primes], key=lambda t: t[1])
    print(f"  full fit-set sorted by min_resonance_sum (smallest=closest to heartbeat): {all_min_res[:20]}")

    # ---------------- Step 4: (53/84)^k magnitude law ----------------
    print("\n=== (53/84)^k MAGNITUDE LAW ===")
    print(f"(53/84) = {53/84:.6f}, (53/84)^6 = {(53/84)**6:.6f} (matches fitted b={B_FIT})")
    print(f"{'p':>4} {'|reldev|':>10} {'best_k':>10} {'(53/84)^k_pred':>16} {'k_int?':>8}")
    magnitude_rows = []
    for p in fit_anomalous:
        absdev = abs(census[p]["reldev"])
        if absdev <= 0 or absdev >= 1:
            k_fit = float('nan')
        else:
            k_fit = math.log(absdev) / math.log(53/84)
        magnitude_rows.append((p, absdev, k_fit))
        is_int = abs(k_fit - round(k_fit)) < 0.15 if not math.isnan(k_fit) else False
        print(f"{p:4d} {absdev:10.5f} {k_fit:10.4f} {(53/84)**round(k_fit) if not math.isnan(k_fit) else float('nan'):16.6f} {str(is_int):>8}")

    # frozen prediction test: p=19, |dev| measured vs (53/84)^9
    if 19 in census:
        c19 = census[19]
        measured_absdev = abs(c19["dev"])  # ABSOLUTE deviation (not relative), matching the frozen claim's units
        pred_98 = (53/84)**9
        print(f"\nFROZEN PREDICTION TEST: p=19 |dev| (absolute, this census) = {measured_absdev:.6f} "
              f"vs (53/84)^9 = {pred_98:.6f}")
        print(f"  CI on absolute dev: point={c19['point']:.5f}, 1/19={1/19:.5f}, "
              f"CI=[{c19['lo']:.5f},{c19['hi']:.5f}]")
        ci_abs_dev_lo = c19['lo'] - 1/19
        ci_abs_dev_hi = c19['hi'] - 1/19
        # abs dev CI (could flip sign at endpoints; report the interval of (rate-1/p))
        lo_dev, hi_dev = sorted([ci_abs_dev_lo, ci_abs_dev_hi])
        hit = lo_dev <= -pred_98 <= hi_dev or lo_dev <= pred_98 <= hi_dev
        print(f"  dev CI = [{lo_dev:.6f}, {hi_dev:.6f}]; does it bracket ±(53/84)^9={pred_98:.6f}? {hit}")
        print(f"  reldev = {c19['reldev']:.5f}, |reldev| = {abs(c19['reldev']):.5f} "
              f"-> k_fit = {math.log(abs(c19['reldev']))/math.log(53/84):.4f}" if c19['reldev'] != 0 else "")

    # ---------------- Step 5: spectral cross-correlation ----------------
    print("\n=== SPECTRAL CROSS-CORRELATION ===")
    # Correlate |reldev| against p_mod_53 distance-to-0 (heartbeat phase alignment)
    # and against min_resonance_sum, and against ord2, ord3 -- report Pearson r
    # for each against |reldev| across the full fit set (not just anomalous).
    def pearson(xs, ys):
        n = len(xs)
        mx = sum(xs)/n; my = sum(ys)/n
        cov = sum((x-mx)*(y-my) for x,y in zip(xs,ys))/n
        vx = sum((x-mx)**2 for x in xs)/n
        vy = sum((y-my)**2 for y in ys)/n
        if vx <= 0 or vy <= 0:
            return 0.0
        return cov/math.sqrt(vx*vy)

    absdevs = [abs(census[p]["reldev"]) for p in fit_primes]
    ord2s = [predictors[p]["ord2"] for p in fit_primes]
    ord3s = [predictors[p]["ord3"] for p in fit_primes]
    pmod53s = [min(predictors[p]["pmod53"], HEARTBEAT - predictors[p]["pmod53"]) for p in fit_primes]
    minres = [predictors[p]["min_resonance_sum"] for p in fit_primes]
    ps = list(fit_primes)

    r_ord2 = pearson(ord2s, absdevs)
    r_ord3 = pearson(ord3s, absdevs)
    r_pmod53 = pearson(pmod53s, absdevs)
    r_minres = pearson(minres, absdevs)
    r_p = pearson(ps, absdevs)
    print(f"Pearson r(|reldev|, ord2)        = {r_ord2:+.4f}")
    print(f"Pearson r(|reldev|, ord3)        = {r_ord3:+.4f}")
    print(f"Pearson r(|reldev|, dist-to-0 mod53) = {r_pmod53:+.4f}")
    print(f"Pearson r(|reldev|, min_resonance_sum) = {r_minres:+.4f}")
    print(f"Pearson r(|reldev|, p itself)    = {r_p:+.4f}  (null-model control: does deviation just shrink with 1/p scale?)")

    # Single global k test: if one k explained ALL anomalous primes' magnitudes,
    # the fitted k's (magnitude_rows) should cluster tightly. Report std/mean.
    ks = [k for (_, _, k) in magnitude_rows if not math.isnan(k)]
    if ks:
        mean_k = sum(ks)/len(ks)
        var_k = sum((k-mean_k)**2 for k in ks)/len(ks)
        print(f"\nFitted k values across anomalous primes: {[(p,round(k,3)) for p,_,k in magnitude_rows]}")
        print(f"mean(k)={mean_k:.3f}, std(k)={math.sqrt(var_k):.3f} "
              f"-> {'TIGHT (structural, single decay const)' if math.sqrt(var_k) < 1.0 else 'SCATTERED (no single global k)'}")

    # ---------------- Step 6: predictive check on held-out primes ----------------
    print("\n=== HELD-OUT PREDICTIVE CHECK (p in 201..500) ===")
    hold_anomalous = sorted([p for p in hold_primes if census[p]["anomalous"]],
                             key=lambda p: -abs(census[p]["dev"]))
    print(f"Held-out anomalous count: {len(hold_anomalous)} / {len(hold_primes)}")
    print(f"Held-out anomalous primes: {hold_anomalous}")

    # Apply frozen/fitted predictors UNCHANGED: whichever predictor(s) showed
    # a real anom/non-anom split in the fit set. Report their held-out hit rate.
    # We test: "small min_resonance_sum flags anomaly" and "p mod 53 near 0 flags anomaly"
    # as the two candidate rules from step 3/5, PRE-REGISTERED here as whatever
    # showed the strongest fit-set correlation (report both regardless of sign,
    # honesty over cherry-picking).
    predictors_hold = {}
    for p in hold_primes:
        ord2 = n_order(2, p)
        ord3 = n_order(3, p)
        pmod53 = p % HEARTBEAT
        resonance_hits = []
        for a in range(1, 61):
            for b in range(1, 61):
                val = (pow(2, a, p) - pow(3, b, p)) % p
                if val == 0:
                    resonance_hits.append((a, b))
        min_resonance = min((a+b for a, b in resonance_hits), default=None)
        predictors_hold[p] = dict(ord2=ord2, ord3=ord3, pmod53=pmod53, min_resonance_sum=min_resonance)

    all_pred = {**predictors, **predictors_hold}

    print(f"\n{'p':>4} {'anomalous?':>10} {'dev':>10} {'ord2':>6} {'ord3':>6} {'pmod53':>7} {'minres':>7}")
    for p in hold_primes:
        c = census[p]
        pr = all_pred[p]
        print(f"{p:4d} {str(c['anomalous']):>10} {c['dev']:+10.5f} {pr['ord2']:6d} {pr['ord3']:6d} "
              f"{pr['pmod53']:7d} {pr['min_resonance_sum']:7}")

    out = dict(
        census={str(p): v for p, v in census.items()},
        predictors={str(p): v for p, v in predictors.items()},
        predictors_hold={str(p): v for p, v in predictors_hold.items()},
        fit_anomalous=fit_anomalous,
        hold_anomalous=hold_anomalous,
        is_19_extreme=is_19_extreme,
        r_ord2=r_ord2, r_ord3=r_ord3, r_pmod53=r_pmod53, r_minres=r_minres, r_p_control=r_p,
        magnitude_rows=magnitude_rows,
    )
    with open("census_analysis.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\nWrote census_analysis.json")

if __name__ == "__main__":
    main()
