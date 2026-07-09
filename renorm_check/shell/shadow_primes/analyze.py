#!/usr/bin/env python3
"""
Analyze results.json from harness.py and produce all numbers needed for
SHADOW_FINDINGS.md: density table, v2-correlation, co-occurrence, descent-
position trend, and residue-class / forbidden-prime check.
"""
import json
import math

PRIMES = [2, 5, 7, 11, 13, 17, 19, 23]

def wilson_ci(k, n, z=1.96):
    """Wilson score interval for a binomial proportion, returns (phat, lo, hi)."""
    if n == 0:
        return (0.0, 0.0, 0.0)
    phat = k / n
    denom = 1 + z*z/n
    center = (phat + z*z/(2*n)) / denom
    half = (z * math.sqrt(phat*(1-phat)/n + z*z/(4*n*n))) / denom
    return phat, center - half, center + half

def main():
    r = json.load(open("results.json"))
    n_steps = r["n_steps_total"]
    support_n = r["support_steps"]
    drop_n = r["drop_steps"]

    print("="*100)
    print(f"SAMPLE: {r['n_trajectories']} trajectories, {n_steps} total odd-steps, "
          f"{r['n_failed']} failed, max_traj_len={r['max_traj_len']}")
    print(f"support(v2=1) steps = {support_n} ({support_n/n_steps:.4f}), "
          f"drop(v2>=2) steps = {drop_n} ({drop_n/n_steps:.4f})")
    print("="*100)

    # ---------------- TASK 1: density table ----------------
    print("\n--- TASK 1: hit-density table, p, measured P(v_p>=1), Wilson 95% CI, 1/(p-1), 1/p, err vs 1/(p-1) ---")
    task1_rows = []
    for p in PRIMES:
        k = r["hits"][str(p)]
        phat, lo, hi = wilson_ci(k, n_steps)
        pred_pm1 = 1.0/(p-1)
        pred_p = 1.0/p
        err_pm1 = phat - pred_pm1
        err_p = phat - pred_p
        mean_vp = r["sumv"][str(p)] / n_steps
        # expected mean_vp under geometric-with-stop model: sum_{k=1}^inf k * (1/p)^k*(1-1/p) roughly
        # if hit density h = 1/(p-1) matches sum over v_p>=1 (P(v_p=j)= (p-1)/p^j for j>=1 scaled)
        row = dict(p=p, k=k, phat=phat, lo=lo, hi=hi, pred_pm1=pred_pm1, pred_p=pred_p,
                   err_pm1=err_pm1, err_p=err_p, mean_vp=mean_vp)
        task1_rows.append(row)
        print(f"p={p:2d}  hits={k:7d}  P(v_p>=1)={phat:.5f}  CI=[{lo:.5f},{hi:.5f}]  "
              f"1/(p-1)={pred_pm1:.5f}  1/p={pred_p:.5f}  err_vs_1/(p-1)={err_pm1:+.5f}  "
              f"mean_vp={mean_vp:.5f}")

    # ---------------- TASK 2: v2 correlation ----------------
    print("\n--- TASK 2: P(v_p>=1 | v2=1 support) vs P(v_p>=1 | v2>=2 drop), diff, and correlation coefficients ---")
    task2_rows = []
    for p in PRIMES:
        hs = r["hits_given_support"][str(p)]
        hd = r["hits_given_drop"][str(p)]
        p_supp, lo_s, hi_s = wilson_ci(hs, support_n)
        p_drop, lo_d, hi_d = wilson_ci(hd, drop_n)
        diff = p_supp - p_drop
        # pooled z-test for difference of two proportions
        p_pool = (hs + hd) / (support_n + drop_n)
        se = math.sqrt(p_pool*(1-p_pool)*(1/support_n + 1/drop_n))
        z = diff / se if se > 0 else 0.0
        corr_mag = r["corr_magnitude"][str(p)]
        corr_bin = r["corr_binary"][str(p)]
        row = dict(p=p, p_supp=p_supp, ci_s=(lo_s,hi_s), p_drop=p_drop, ci_d=(lo_d,hi_d),
                   diff=diff, z=z, corr_mag=corr_mag, corr_bin=corr_bin)
        task2_rows.append(row)
        print(f"p={p:2d}  P(hit|support)={p_supp:.5f} [{lo_s:.5f},{hi_s:.5f}]  "
              f"P(hit|drop)={p_drop:.5f} [{lo_d:.5f},{hi_d:.5f}]  diff={diff:+.5f}  z={z:+.2f}  "
              f"corr(v2,v_p)={corr_mag:+.4f}  corr(isdrop,hit_p)={corr_bin:+.4f}")

    # ---------------- TASK 3: co-occurrence matrix ----------------
    print("\n--- TASK 3: co-occurrence matrix (observed count both p,q hit) vs independent-expected, ratio ---")
    cooc = r["cooc"]
    hits = {p: r["hits"][str(p)] for p in PRIMES}
    print("Pairwise (p,q) p<q: observed, expected=hits_p*hits_q/n_steps, ratio=obs/exp, excess=obs-exp")
    task3_rows = []
    for i, p in enumerate(PRIMES):
        for q in PRIMES[i+1:]:
            obs = cooc[str(p)][str(q)]
            exp = hits[p] * hits[q] / n_steps
            ratio = obs / exp if exp > 0 else float('nan')
            excess = obs - exp
            # z-score approx using Poisson-ish sqrt(exp) as sigma (rough)
            z = excess / math.sqrt(exp) if exp > 0 else float('nan')
            task3_rows.append(dict(p=p,q=q,obs=obs,exp=exp,ratio=ratio,excess=excess,z=z))
            print(f"({p:2d},{q:2d})  obs={obs:6d}  exp={exp:9.2f}  ratio={ratio:.4f}  "
                  f"excess={excess:+8.2f}  z~={z:+.2f}")

    # ---------------- TASK 4: descent-position density ----------------
    print("\n--- TASK 4: density vs fractional descent-position bin (0=near n0 start, 9=near 1) ---")
    NBINS = 10
    bin_steps = r["bin_steps"]
    bin_hits = r["bin_hits"]
    task4_rows = []
    for p in PRIMES:
        row = []
        for b in range(NBINS):
            k = bin_hits[str(p)][b]
            n = bin_steps[b]
            phat, lo, hi = wilson_ci(k, n)
            row.append((phat, lo, hi, n))
        task4_rows.append((p, row))
        vals = " ".join(f"{v[0]:.4f}" for v in row)
        print(f"p={p:2d}  bins(0->9): {vals}")
    print("bin_steps (n per bin):", bin_steps)

    # ---------------- TASK 5: residue-class / forbidden-prime check ----------------
    print("\n--- TASK 5: residue class distribution of m=3x+1 mod p (raw, unconditioned), chi-square vs uniform-over-all-residues ---")
    residue_counts = r["residue_counts"]
    task5_rows = []
    for p in PRIMES:
        counts = {int(k): v for k, v in residue_counts[str(p)].items()}
        total = sum(counts.values())
        # expected uniform over p residues
        exp_uniform = total / p
        chi2 = 0.0
        detail = []
        for res in range(p):
            obs = counts.get(res, 0)
            chi2 += (obs - exp_uniform)**2 / exp_uniform
            detail.append((res, obs, obs/total))
        # degrees of freedom = p-1
        task5_rows.append(dict(p=p, total=total, chi2=chi2, dof=p-1, detail=detail))
        detail_str = ", ".join(f"r{res}:{obs}({obs/total:.4f})" for res,obs,_ in detail)
        print(f"p={p:2d}  total={total}  chi2={chi2:.2f} (dof={p-1})  residues: {detail_str}")

    # Save consolidated summary as JSON for reference
    summary = dict(
        n_trajectories=r['n_trajectories'], n_steps=n_steps, support_n=support_n, drop_n=drop_n,
        task1=task1_rows, task2=task2_rows, task3=task3_rows, task4_bins=bin_steps, task5=task5_rows,
    )
    with open("summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print("\nWrote summary.json")

if __name__ == "__main__":
    main()
