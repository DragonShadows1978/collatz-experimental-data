"""
Task 2 CORRECTED: proof text (COLLATZ_PROOF.md:499-505) says the b=0.063099
fit comes from the C=10 (universal) curve, regression of ln(1-rho) vs m over
m=7..12 (six points), NOT the C=3 locked curve (that one saturates and is a
different regime -- a fixed floor, not a b^m decay to zero).

Use the C=10 table values from SPECTRAL_RADIUS_RESULTS.txt (which the proof's
own table condenses; SPECTRAL_RADIUS_RESULTS.txt gives more digits for gap
than the proof's markdown table, e.g. gap(7)=0.000464 vs proof's 4.6e-4).
"""
import mpmath as mp
from fractions import Fraction

mp.mp.dps = 50

# C=10 (universal) table from SPECTRAL_RADIUS_RESULTS.txt -- highest precision available
gap_C10 = {
    1: mp.mpf('0.998929'),
    2: mp.mpf('0.998929'),  # placeholder will overwrite below with correct values
}
# actual values from file:
gap_C10 = {
    1: mp.mpf('1.000000'),
    2: mp.mpf('0.998929'),
    3: mp.mpf('0.764556'),
    4: mp.mpf('0.219422'),
    5: mp.mpf('0.036496'),
    6: mp.mpf('0.004750'),
    7: mp.mpf('0.000464'),
    8: mp.mpf('0.000038'),
    9: mp.mpf('0.0000029'),
    10: mp.mpf('0.00000018'),
    11: mp.mpf('0.0000000094'),
    12: mp.mpf('0.00000000047'),
}

print("gap(m) for C=10 universal curve, m=7..12 (the regime the proof regresses on):")
for m in range(7,13):
    print(f"  m={m}  gap={gap_C10[m]}")

# Regression ln(gap) vs m over m=7..12 (six points) -- NOTE: these printed
# values are themselves rounded to 2 sig figs by the results file, which will
# limit our precision. Let's do the regression anyway and report residuals
# honestly, then separately check the CONSECUTIVE RATIO gap(m+1)/gap(m) which
# is less sensitive to rounding accumulation and is a direct empirical b_m.

xs = [mp.mpf(m) for m in range(7,13)]
ys = [mp.log(gap_C10[m]) for m in range(7,13)]
n = 6
mean_x = sum(xs)/n
mean_y = sum(ys)/n
Sxy = sum((x-mean_x)*(y-mean_y) for x,y in zip(xs,ys))
Sxx = sum((x-mean_x)**2 for x in xs)
slope = Sxy/Sxx
intercept = mean_y - slope*mean_x
b_fit = mp.e**slope
print(f"\nRegression (m=7..12): slope={slope}  b_fit=e^slope={b_fit}")
print(f"Published b=0.063099. Our regression b_fit={b_fit}. Rel diff = {abs(b_fit-mp.mpf('0.063099'))/mp.mpf('0.063099')}")

# residuals
print("\nResiduals of ln(gap) fit:")
resid=[]
for x,y in zip(xs,ys):
    pred = slope*x+intercept
    r = y-pred
    resid.append(r)
    print(f"  m={x}  ln(gap)={y}  pred={pred}  resid={r}")
ss_res = sum(r**2 for r in resid)
ss_tot = sum((y-mean_y)**2 for y in ys)
Rsq = 1-ss_res/ss_tot
print(f"R^2={Rsq}")

# Consecutive ratio approach (more robust to rounding: uses adjacent points only)
print("\nConsecutive ratios gap(m+1)/gap(m), m=6..11:")
for m in range(6,12):
    if gap_C10[m] == 0: continue
    ratio = gap_C10[m+1]/gap_C10[m]
    print(f"  m={m}->{m+1}: gap({m})={gap_C10[m]}  gap({m+1})={gap_C10[m+1]}  ratio={ratio}")

# Now scan (q/p)^k for log2(3) convergents (p,q), k=1..10, vs b_fit AND vs
# published 0.063099, report best matches with error
print("\n" + "="*70)
print("Scanning (q/p convergent)^k against b_fit and published b, k=1..10")
print("="*70)
conv_log23_list = [
    (0,1,1),(1,2,1),(2,3,2),(3,8,5),(4,19,12),(5,65,41),(6,84,53),(7,485,306),(8,1054,665),(9,24727,15601)
]
b_pub = mp.mpf('0.063099')
best = []
for k_idx,p,q in conv_log23_list:
    if p==0: continue
    ratio_qp = mp.mpf(q)/mp.mpf(p)
    for k in range(1,11):
        val = ratio_qp**k
        err_fit = abs(val-b_fit)/b_fit
        err_pub = abs(val-b_pub)/b_pub
        best.append((err_pub, k_idx, p, q, k, val, err_fit))
best.sort(key=lambda t: t[0])
print("\nTop 15 matches to PUBLISHED b=0.063099 (sorted by error):")
for err_pub, k_idx, p, q, k, val, err_fit in best[:15]:
    print(f"  convergent#{k_idx} (p={p},q={q}) exponent k={k}: (q/p)^k={val}  err_vs_published={err_pub}  err_vs_our_regression={err_fit}")

best2 = sorted(best, key=lambda t: t[6])
print("\nTop 15 matches to OUR REGRESSION b_fit (sorted by error):")
for err_pub, k_idx, p, q, k, val, err_fit in best2[:15]:
    print(f"  convergent#{k_idx} (p={p},q={q}) exponent k={k}: (q/p)^k={val}  err_vs_our_regression={err_fit}  err_vs_published={err_pub}")

# Is 6 = sum of partial quotients up to 84/53 convergent (index 6)?
cf_log23 = [1, 1, 1, 2, 2, 3, 1]  # a0..a6 (index up to convergent 6)
print(f"\nCF partial quotients a0..a6 for log2(3): {cf_log23}")
print(f"Sum of a0..a6 = {sum(cf_log23)}")
print(f"Sum of a1..a6 (excluding integer part a0) = {sum(cf_log23[1:])}")
print(f"Index of 84/53 convergent = k=6 (0-indexed)")
print(f"Number of partial quotients used to build it (a0..a6) = 7 terms")
