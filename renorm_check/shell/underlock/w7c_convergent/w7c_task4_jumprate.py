"""
Task 4: jump-rate drift. Edge list M(C) for C=1..28 (order file + confirmed
new edges C=27,28 from w7a_new_edges.txt -- matches order file exactly).
Jump positions among C=11..28 at word-index n = {4,5,6,8,11,13,15,17}
(these n are indices into the C=11..28 sequence, n=1 is C=11, so n=k -> C=10+k).
Fit floor(9n/4)+2 per the order file. Test whether the RATE (spacing between
jump n's, or n vs jump-count) drifts toward 53/22=2.409 or stays at 9/4=2.25.
"""
from fractions import Fraction
import mpmath as mp
mp.mp.dps = 50

edges_1_10 = {1:4,2:7,3:9,4:12,5:14,6:16,7:19,8:21,9:24,10:26}
edges_11_28 = {11:57,12:63,13:68,14:71,15:79,16:93,17:108,18:110,19:130,20:132,
               21:139,22:157,23:163,24:188,25:192,26:205,27:208,28:263}

all_edges = {**edges_1_10, **edges_11_28}
Cs = sorted(all_edges.keys())
print("Full edge table C: M(C):")
for C in Cs:
    print(f"  C={C:3d}  M(C)={all_edges[C]:4d}")

# check exact formula for C<=10: M(C)=floor((C+1)/beta)
beta = 2-mp.log(3)/mp.log(2)
print("\nCheck M(C)=floor((C+1)/beta) for C=1..10:")
for C in range(1,11):
    pred = int(mp.floor((C+1)/beta))
    actual = edges_1_10[C]
    print(f"  C={C}: predicted={pred}  actual={actual}  match={pred==actual}")

# "jump" = big increment among the M(C) sequence C=11..28.
# compute deltas
print("\nDeltas M(C)-M(C-1) for C=11..28:")
deltas = {}
prev = edges_1_10[10]
for C in range(11,29):
    d = all_edges[C]-prev
    deltas[C]=d
    print(f"  C={C}: M={all_edges[C]}  delta={d}")
    prev = all_edges[C]

# word-index n: order file says n=1..18 corresponds to C=11..28 (n = C-10)
# "BIG-increment (jump) positions ... at word-index n={4,5,6,8,11,13,15,17}"
print("\nWord-index n = C-10, mapping deltas by n:")
delta_by_n = {}
for C,d in deltas.items():
    n = C-10
    delta_by_n[n]=d
    print(f"  n={n:2d} (C={C})  delta={d}")

jump_ns = [4,5,6,8,11,13,15,17]
print(f"\nClaimed jump n's: {jump_ns}")
print("Deltas at those n (should be the large ones):")
sorted_deltas = sorted(delta_by_n.items(), key=lambda kv: -kv[1])
print("All (n,delta) sorted descending by delta size:")
for n,d in sorted_deltas:
    marker = " <-- claimed jump" if n in jump_ns else ""
    print(f"  n={n:2d}  delta={d:3d}{marker}")

# test floor(9n/4)+2 fit
print("\nTest floor(9n/4)+2 against jump_ns (are these the PREDICTED jump positions,")
print("i.e., does n_k = floor(9k/4)+2 for k=1,2,3...?):")
for k in range(1,9):
    pred_n = int(mp.floor(mp.mpf(9*k)/4))+2
    print(f"  k={k}: floor(9k/4)+2 = {pred_n}   actual jump_ns[{k-1}]={jump_ns[k-1] if k-1<len(jump_ns) else 'N/A'}")

# Now: the RATE. Compute spacing between consecutive jump n's.
print("\nSpacings between consecutive claimed jump n's:")
spacings = [jump_ns[i+1]-jump_ns[i] for i in range(len(jump_ns)-1)]
print(f"  jump_ns={jump_ns}")
print(f"  spacings={spacings}")
print(f"  mean spacing = {sum(spacings)/len(spacings)} = {Fraction(sum(spacings),len(spacings))}")

# also compute n_k / k as k grows (rate = n_k/k), see if -> 9/4 or drifts to 53/22
print("\nn_k / k for k=1..8 (rate estimate from ANCHOR positions):")
for k,n in enumerate(jump_ns, start=1):
    rate = Fraction(n,k)
    print(f"  k={k}: n_k={n}  n_k/k = {rate} = {float(rate)}")

print(f"\n9/4 = {9/4} = 2.25")
print(f"53/22 = {53/22} = {float(Fraction(53,22))}")

# The real test: using MORE data (C=27,28 confirmed, no C=29+ yet), does the
# jump rate (extrapolated) drift toward 53/22 or stay flat at 9/4?
# Since we only have deltas through C=28 (n=18) and the claimed jump set only
# goes to n=17, let's check if C=27,28 (n=17,18) show a NEW jump or continue
# the same pattern, i.e. is n=18 a jump too?
print(f"\ndelta at n=17 (C=27): {delta_by_n.get(17)}")
print(f"delta at n=18 (C=28): {delta_by_n.get(18)}")
print("(n=17 was claimed as a jump n; check if n=18 continues pattern predicted by floor(9k/4)+2 for k=9:")
k=9
pred_n9 = int(mp.floor(mp.mpf(9*k)/4))+2
print(f"  floor(9*9/4)+2 = {pred_n9}  (we only have data to n=18, C=28)")

# Linear regression of n_k vs k over the 8 known jump anchors --- exact slope
# via least squares in Fraction arithmetic where possible, else mpmath.
ks = [mp.mpf(k) for k in range(1,9)]
ns = [mp.mpf(n) for n in jump_ns]
nn=8
mean_k=sum(ks)/nn; mean_n=sum(ns)/nn
Skn=sum((k-mean_k)*(n-mean_n) for k,n in zip(ks,ns))
Skk=sum((k-mean_k)**2 for k in ks)
slope=Skn/Skk
intercept=mean_n-slope*mean_k
print(f"\nLinear regression n_k = slope*k + intercept over 8 anchors:")
print(f"  slope={slope}  intercept={intercept}")
print(f"  slope as rate estimate = {slope}  vs 9/4=2.25  vs 53/22={float(Fraction(53,22))}")

# residuals
print("Residuals:")
for k,n in zip(ks,ns):
    pred = slope*k+intercept
    print(f"  k={k}  n={n}  pred={pred}  resid={n-pred}")
