"""
Follow-up: the order file's claimed jump set {4,5,6,8,11,13,15,17} was fit to
floor(9n/4)+2 "+-1". Let's check that fit literally (inverse direction: does
n=floor(9k/4)+2 approx predict jump_ns[k-1] to within 1?), and separately ask
what happens if we define "jump" empirically (top deltas) instead of taking
the order file's list on faith, since n=18 (delta=55, the single BIGGEST jump
in the entire C=11..28 table) was excluded from the claimed set despite being
larger than every claimed jump's delta.
"""
from fractions import Fraction

jump_ns = [4,5,6,8,11,13,15,17]
# check |floor(9k/4)+2 - jump_ns[k-1]| <= 1
print("Literal +-1 check of floor(9k/4)+2 against claimed jump_ns:")
ok = True
for k in range(1,9):
    pred = (9*k)//4 + 2
    actual = jump_ns[k-1]
    diff = pred-actual
    within1 = abs(diff)<=1
    ok = ok and within1
    print(f"  k={k}: pred={pred} actual={actual} diff={diff} within_1={within1}")
print(f"All within +-1: {ok}")

# Empirical "top-8 deltas by size" among n=1..18 (excluding n=1 which is
# corridor-transition boundary artifact, not a heartbeat jump)
delta_by_n = {1:31,2:6,3:5,4:3,5:8,6:14,7:15,8:2,9:20,10:2,11:7,12:18,13:6,14:25,15:4,16:13,17:3,18:55}
print("\nAll deltas n=1..18 sorted by size (descending):")
for n,d in sorted(delta_by_n.items(), key=lambda kv:-kv[1]):
    print(f"  n={n:2d} delta={d}")

print("\nTop 8 by size (excluding n=1 boundary): ", sorted([n for n in delta_by_n if n!=1], key=lambda n:-delta_by_n[n])[:8])

# rate of TOP-delta n's (empirical jumps) vs k
top_ns_excl_n1 = sorted([n for n in delta_by_n if n!=1], key=lambda n:-delta_by_n[n])[:8]
top_ns_sorted = sorted(top_ns_excl_n1)
print(f"Empirical top-8 jump n's (sorted ascending): {top_ns_sorted}")
for k,n in enumerate(top_ns_sorted, start=1):
    r = Fraction(n,k)
    print(f"  k={k} n={n} n/k={r}={float(r):.4f}")

# Given the ambiguity, the DEFENSIBLE quantitative claim is just the
# n_k/k drift of the ORDER FILE's OWN claimed set, computed above:
# 4.0, 2.5, 2.0, 2.0, 2.2, 2.167, 2.143, 2.125
# This is NOT monotonically approaching 2.409 from below; after k=3 it rises
# slightly (2.0->2.2) then DECREASES again toward ~2.1-2.125, i.e. it's
# oscillating/settling, and settling BELOW 9/4=2.25, trending away from
# 53/22=2.409, not toward it.
seq = [4.0, 2.5, 2.0, 2.0, 2.2, 2.1666666666666665, 2.142857142857143, 2.125]
print(f"\nn_k/k sequence: {seq}")
print("Differences from 9/4=2.25:", [round(x-2.25,4) for x in seq])
print("Differences from 53/22=2.4091:", [round(x-53/22,4) for x in seq])
print("Trend (k=5..8 only, post-transient): ", seq[4:])
print("-> monotonically DECREASING from 2.2 to 2.125, moving AWAY from both")
print("   9/4 and 53/22, not converging to either from this data span.")
