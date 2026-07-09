"""
Task 2: re-derive b from the rho(m) data (C=3 locked curve is the one that
matches the 53/84 heartbeat claim in COLLATZ_PROOF.md -- C>=10 curve saturates
to rho->1, gap->0 super fast, not a clean geometric decay in the same regime).
We use the C=3 table (which the proof explicitly cites for the b~0.063 fit)
since the C>=10 curve's gap collapses combinatorially fast (not the locked
heartbeat regime -- it's pre-lock transient). Re-check both to be safe.
"""
import mpmath as mp
from fractions import Fraction

mp.mp.dps = 50

# C=3 table, m: gap=1-rho
C3 = {
    1: mp.mpf('1.000000'),
    2: mp.mpf('0.999005'),
    3: mp.mpf('0.775210'),
    4: mp.mpf('0.250120'),
    5: mp.mpf('0.073780'),
    6: mp.mpf('0.043640'),
    7: mp.mpf('0.039770'),
    8: mp.mpf('0.039390'),
    9: mp.mpf('0.039353'),
    10: mp.mpf('0.039353'),
    11: mp.mpf('0.039353'),
    12: mp.mpf('0.039353'),
    13: mp.mpf('0.039353'),
}

# This is the published rounded table. But note: m=9..13 all print IDENTICAL
# 0.039353 -- that's a LOCK not a decay. A pure geometric ~b^m decay would
# keep shrinking; it wouldn't lock to a constant. So gap "decaying as c*b^m"
# must refer to the APPROACH to the lock (m=3->9), not m>=9 itself.
# Let's regress ln(gap - gap_inf) vs m using gap_inf = 0.039353 (locked value)
# on the transient region m=3..9 (before lock), which is the only region where
# gap is actually changing.

gap_inf = C3[13]  # locked asymptote from data (m>=9 identical to 6 dp)
print("Locked asymptote gap_inf =", gap_inf)

# transient residual: e(m) = gap(m) - gap_inf, should go to 0 like b^m if pure exp
print("\nm, gap(m), e(m)=gap(m)-gap_inf")
ms = []
es = []
for m in range(3, 9):
    e = C3[m] - gap_inf
    ms.append(m)
    es.append(e)
    print(f"  m={m}  gap={C3[m]}  e={e}")

# ln(e) vs m linear regression (exact-ish, using mpmath) over the region
# where e is well-resolved by the 6dp table (m=3..8; m>=9 e is below/at
# table precision so unusable)
import math
xs = [mp.mpf(m) for m in ms]
ys = [mp.log(e) for e in es]
n = len(xs)
mean_x = sum(xs)/n
mean_y = sum(ys)/n
Sxy = sum((x-mean_x)*(y-mean_y) for x,y in zip(xs,ys))
Sxx = sum((x-mean_x)**2 for x in xs)
slope = Sxy/Sxx
intercept = mean_y - slope*mean_x
b_fit = mp.e**slope
print(f"\nRegression ln(e) = {slope}*m + {intercept}")
print(f"=> b_fit (full m=3..8) = {b_fit}")

# residuals
print("\nResiduals (ln(e) - fit):")
resid = []
for x,y in zip(xs,ys):
    pred = slope*x+intercept
    r = y-pred
    resid.append(r)
    print(f"  m={x}  actual_ln={y}  pred_ln={pred}  resid={r}")
ss_res = sum(r**2 for r in resid)
ss_tot = sum((y-mean_y)**2 for y in ys)
Rsq = 1 - ss_res/ss_tot
print(f"R^2 = {Rsq}")

# Try restricting to the most "converged-looking" asymptotic tail m=6,7,8
# (closer to true exponential regime, away from initial transient m=3,4,5
# which are dominated by other eigenvalues)
print("\n--- Restricted regression on m=6,7,8 only (closer to asymptotic single-mode decay) ---")
xs2 = [mp.mpf(m) for m in [6,7,8]]
ys2 = [mp.log(C3[m]-gap_inf) for m in [6,7,8]]
n2=3
mean_x2 = sum(xs2)/n2
mean_y2 = sum(ys2)/n2
Sxy2 = sum((x-mean_x2)*(y-mean_y2) for x,y in zip(xs2,ys2))
Sxx2 = sum((x-mean_x2)**2 for x in xs2)
slope2 = Sxy2/Sxx2
b_fit2 = mp.e**slope2
print(f"slope={slope2}  b_fit(m=6,7,8)={b_fit2}")

# also try consecutive-ratio approach: b_m = e(m+1)/e(m), see if it converges
print("\n--- Consecutive ratios e(m+1)/e(m) (should -> b if single-mode exponential) ---")
for m in range(3,8):
    e1 = C3[m]-gap_inf
    e2 = C3[m+1]-gap_inf
    ratio = e2/e1
    print(f"  m={m}->{m+1}: e({m})={e1}  e({m+1})={e2}  ratio={ratio}")

# compare all fits to (53/84)^6 and (53/84)^k for various k, and neighbor convergents
print("\n" + "="*70)
print("Comparing b candidates to (q/p)^k for convergent (p,q) pairs and k=1..10")
print("="*70)

candidates = {
    "(84/53)^-1 form i.e. (53/84)": (Fraction(53,84)),
    "(22/53)": (Fraction(22,53)),   # beta convergent 5
    "(127/306) neighbor": Fraction(127,306),
    "(65/41) neighbor (log2(3) k=5)": Fraction(65,41),
    "(19/12) neighbor (log2(3) k=4)": Fraction(19,12),
}

target_bs = {
    "b_fit_m3-8": b_fit,
    "b_fit_m6-8": b_fit2,
    "ratio_m7->8 (best resolved consecutive)": C3[8]-gap_inf if False else None,
}

# convergents of log2(3): k=0..8 as (p,q)
conv_log23_list = [
    (0,1,1),(1,2,1),(2,3,2),(3,8,5),(4,19,12),(5,65,41),(6,84,53),(7,485,306),(8,1054,665)
]
print("\nFor b_fit (m=3..8 regression):", b_fit)
print("For b_fit (m=6..8 regression):", b_fit2)
print("Published/table b = 0.063099 (from proof, matches (53/84)^6=0.063093 to 0.01%)")

target_b_published = mp.mpf('0.063099')
print(f"\n(53/84)^6 = {(mp.mpf(53)/84)**6}")
print(f"target_b_published = {target_b_published}")
print(f"relative error = {abs((mp.mpf(53)/84)**6 - target_b_published)/target_b_published}")

print("\nScan (q/p convergent ratio)^k for k=1..10, all log2(3) convergent neighbor pairs:")
for k_idx,p,q in conv_log23_list:
    if p==0: continue
    ratio_qp = mp.mpf(q)/mp.mpf(p)  # this is q/p, e.g. 53/84
    for k in range(1,11):
        val = ratio_qp**k
        # compare to b_fit2 (best regression) and to published 0.063099
        err_vs_fit2 = abs(val-b_fit2)/b_fit2
        err_vs_pub = abs(val-target_b_published)/target_b_published
        if err_vs_pub < 0.02 or err_vs_fit2 < 0.02:
            print(f"  convergent k_idx={k_idx} (p={p},q={q})  (q/p)^{k}={val}  err_vs_regression(m6-8)={err_vs_fit2}  err_vs_published={err_vs_pub}")
