"""
Is exponent 6 structurally special, or just "whichever k best fits THIS b"?
Test candidate derivations of 6 from the CF data of log2(3):
  - CF partial quotients up to convergent index 6 (84/53): [1,1,1,2,2,3,1]  (a0..a6, 7 terms, k=6 is index)
  - a6 itself = 1 (not 6)
  - index k=6 IS the convergent index -- trivially "6" because that's which convergent we picked
  - sum of some subset of partial quotients?
  - Is there a convergent whose OWN index features "6" more essentially (e.g. a_k=6 somewhere)?
"""
import mpmath as mp
mp.mp.dps = 50

cf_log23 = [1, 1, 1, 2, 2, 3, 1, 5, 2, 23, 2, 2, 1, 1, 55, 1, 4, 3, 1, 1, 15, 1, 9, 2, 5]
print("CF(log2 3) =", cf_log23)
print("Partial quotient values, indexed a0..a24:")
for i,a in enumerate(cf_log23):
    print(f"  a{i} = {a}")

print("\nNotice: NONE of the partial quotients up to a6 equal 6.")
print("a5 = 3 (the largest quotient in that prefix). Sum a0..a6 = 11. Sum a1..a6=10.")
print("So exponent 6 is NOT explained as 'a partial quotient value' or a natural")
print("sum in the prefix. It coincides only with the INDEX of the convergent")
print("(84/53 is the k=6 convergent, 0-indexed) -- but that's circular: we chose")
print("that convergent BECAUSE 53 is the heartbeat length, not because index=6")
print("explains the exponent independently.")

# Test: total CF-expansion "cost" (sum of first k+1 terms) needed to reach
# denominator 53 via the Stern-Brocot tree (number of L/R steps) -- this is
# actually sum(a0..a6) = 11, not 6.
print("\nStern-Brocot path length (sum of all partial quotients to reach 53/84) = 11")

# Test whether 6 = number of DISTINCT convergents needed (k+1 where k=6 -> 7 convergents)
print("Number of convergents 0..6 inclusive = 7 (not 6 either)")

# Test: is 6 possibly just log2(3)-related via floor(some function)?
log23 = mp.log(3)/mp.log(2)
print(f"\nlog2(3) = {log23}")
print(f"floor(3*log2(3)) = {mp.floor(3*log23)}")
print(f"round(2*e) time-wasting check, floor(2/beta)... just enumerate simple candidates:")
beta = 2-log23
print(f"1/beta = {1/beta}, floor={mp.floor(1/beta)}")
print(f"floor(53/84 denominator stuff)... 53 mod something")

# The honest empirical answer: scan which EXPONENT k (not tied to any formula)
# gives the tightest fit for EACH convergent, independently, and see if 6 is
# a repeat winner (suggesting it's convergent-dependent, not fundamental) or
# if only 84/53 gives 6 as its best-fit exponent (suggesting some deeper tie).
gap_C10 = {
    7: mp.mpf('0.000464'), 8: mp.mpf('0.000038'), 9: mp.mpf('0.0000029'),
    10: mp.mpf('0.00000018'), 11: mp.mpf('0.0000000094'), 12: mp.mpf('0.00000000047'),
}
xs = [mp.mpf(m) for m in range(7,13)]
ys = [mp.log(gap_C10[m]) for m in range(7,13)]
n=6
mean_x=sum(xs)/n; mean_y=sum(ys)/n
Sxy=sum((x-mean_x)*(y-mean_y) for x,y in zip(xs,ys))
Sxx=sum((x-mean_x)**2 for x in xs)
slope=Sxy/Sxx
b_fit = mp.e**slope

conv_log23_list = [(0,1,1),(1,2,1),(2,3,2),(3,8,5),(4,19,12),(5,65,41),(6,84,53),(7,485,306),(8,1054,665)]
print(f"\nFor EACH convergent (p,q), find the best-fit REAL exponent k* = ln(b_fit)/ln(q/p):")
for k_idx,p,q in conv_log23_list:
    if p==0 or q==p: continue
    ratio = mp.mpf(q)/mp.mpf(p)
    if ratio<=0 or ratio==1: continue
    k_star = mp.log(b_fit)/mp.log(ratio)
    print(f"  convergent#{k_idx} (p={p},q={q}, q/p={float(ratio):.6f}): best-fit continuous k* = {k_star}")
