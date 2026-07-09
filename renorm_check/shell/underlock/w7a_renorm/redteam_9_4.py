"""
RED TEAM: is the claimed 9/4 Beatty-fit for H-positions real or a reverse-fit
artifact?  Exact integer arithmetic throughout (Fraction for all k
candidates; residuals/SSE are always integers since M(C), positions, c are
all integers -- only k is rational).

Data source: M(C), C=1..28, exactly as given in REDTEAM_9_4_ORDER.md /
W7A_FINDINGS.md / W7C_FINDINGS.md. w7a_new_edges.txt contributes only
C=27->208, C=28->263 -- ALREADY included in this table (verified identical
to the order file). deep_sweep.log contains a STALE/INCONSISTENT run (its
C=27..40 "edge" values decrease monotonically and do NOT match
w7a_new_edges.txt or the order file at C=27,28 -- e.g. log says C=27 edge=36
but the validated file + order file both say C=27 -> M=208) -- excluded as
untrustworthy. No genuine C>=29 data exists. N is fixed at 18 increments
(C=11..28), exactly as given.

Speed note: k-grid search is restricted to RATIONAL candidates p/q with
q<=40 (a generous "simple rational" menu, well beyond 9/4=q4) rather than a
blind 0.0001 float sweep -- this is both faster (exact breakpoints, no
wasted evaluations) AND the methodologically correct test, since the claim
under audit is specifically "fits a SIMPLE rational", not "fits some real
number to 4 decimal places".
"""
import itertools, random, time
from fractions import Fraction as F

M = {1:4,2:7,3:9,4:12,5:14,6:16,7:19,8:21,9:24,10:26,11:57,12:63,13:68,14:71,
     15:79,16:93,17:108,18:110,19:130,20:132,21:139,22:157,23:163,24:188,
     25:192,26:205,27:208,28:263}
Cs = sorted(M)
assert Cs == list(range(1,29))

deltas = {C: M[C]-M[C-1] for C in range(2,29)}
d = {C-10: deltas[C] for C in range(11,29)}  # n = C-10, n=1..18

expected = [31,6,5,3,8,14,15,2,20,2,7,18,6,25,4,13,3,55]
actual = [d[n] for n in range(1,19)]
print("Increment table match with order file:", actual == expected)
print("n: ", list(range(1,19)))
print("d: ", actual)

# ---- fast exact rational-k fit ----
def gen_rational_menu(q_max=40, k_lo=F(13,10), k_hi=F(4,1)):
    s = set()
    for q in range(1, q_max+1):
        for p in range(int(k_lo*q), int(k_hi*q)+2):
            r = F(p,q)
            if k_lo <= r <= k_hi:
                s.add(r)
    return sorted(s)

RATIONAL_MENU = gen_rational_menu(q_max=20)
print(f"\nRational menu size (q<=20, k in [1.3,4.0]): {len(RATIONAL_MENU)}")
# precompute (num,den) pairs once as plain ints for fast floor-div in hot loops
MENU_ND = [(k.numerator, k.denominator) for k in RATIONAL_MENU]

def best_fit_over_menu(hpos_n, menu_nd=MENU_ND, menu=RATIONAL_MENU):
    """hpos_n: 1-indexed rank list of H positions (values = C-index n).
    For each k in menu, the OPTIMAL integer c for minimizing SSE against a
    fixed floor(k*j) shape is c* = round(mean(hp_i - floor(k*i))) -- SSE is
    a quadratic in c, minimized at the (integer-rounded) mean residual, so
    we compute it directly instead of looping over a c_range (13x speedup,
    exact, no approximation: SSE(c) = SSE(0) - 2c*sum(resid0) + n*c^2 is
    exactly quadratic in integer c, so checking floor(mean) and ceil(mean)
    suffices)."""
    best = None
    n = len(hpos_n)
    for (num,den),k in zip(menu_nd, menu):
        resid0 = [hp - (num*j)//den for j,hp in enumerate(hpos_n, start=1)]
        s0 = sum(resid0)
        # SSE(c) = sum((r0_i - c)^2) = sum(r0_i^2) - 2c*s0 + n*c^2
        # minimized at c = s0/n (real); check both integer neighbors
        mean_c = s0 / n
        for c_try in {int(mean_c), int(mean_c)+1, int(mean_c)-1}:
            sse = sum((r0-c_try)**2 for r0 in resid0)
            if best is None or sse < best[0]:
                resid = tuple(r0-c_try for r0 in resid0)
                best = (sse, k, c_try, resid)
    return best  # (sse, k, c, resid)

print()
print("="*70)
print("TASK 1: THRESHOLD SENSITIVITY SWEEP")
print("="*70)

def word_for_threshold(T):
    return {n: ('H' if d[n] > T else 'L') for n in range(1,19)}

threshold_results = {}
t0=time.time()
for T in range(2, 30):
    w = word_for_threshold(T)
    hpos_n = [n for n in range(1,19) if w[n]=='H']
    if len(hpos_n) < 3 or len(hpos_n) > 15:
        continue
    sse,k,c,resid = best_fit_over_menu(hpos_n)
    threshold_results[T] = (hpos_n, k, c, sse, resid)
print(f"(fit search took {time.time()-t0:.1f}s)\n")

print(f"{'T':>4} {'nH':>4} {'H-positions(n)':32} {'best k':>10} {'c':>3} {'SSE':>5} {'SSE/pt':>7}")
for T,(hp,k,c,sse,resid) in threshold_results.items():
    flag = "  <-- k==9/4" if k == F(9,4) else ""
    print(f"{T:4d} {len(hp):4d} {str(hp):32} {str(k):>10} {c:3d} {sse:5d} {sse/len(hp):7.3f}{flag}")

exact_94 = [T for T,(hp,k,c,sse,resid) in threshold_results.items() if k==F(9,4)]
near_94 = [T for T,(hp,k,c,sse,resid) in threshold_results.items() if abs(float(k)-2.25)<0.02]
print(f"\nThresholds tested: {len(threshold_results)}  (T=2..29, all splits giving 3-15 H points)")
print(f"Thresholds where 9/4 is the EXACT best-fit k: {exact_94}  ({len(exact_94)}/{len(threshold_results)})")
print(f"Thresholds where best-fit k is within 0.02 of 2.25: {near_94}  ({len(near_94)}/{len(threshold_results)})")

print()
print("="*70)
print("TASK 2: FITS WITH/WITHOUT THE EXCLUDED +55 (n=18, C=28)")
print("="*70)

T=10
w_full = word_for_threshold(T)
hpos_T10 = [n for n in range(1,19) if w_full[n]=='H']
print("T=10 word (n=1..18):", ''.join(w_full[n] for n in range(1,19)))
print("T=10 H-positions (n):", hpos_T10, " n=18(C=28,+55) included:", 18 in hpos_T10)

sse,k,c,resid = best_fit_over_menu(hpos_T10)
print(f"\n[A] Full T=10 H-set, ALL {len(hpos_T10)} points, +55 INCLUDED, n=1 INCLUDED (no drops at all):")
print(f"    best k={k} ({float(k):.4f}) c={c} SSE={sse} SSE/pt={sse/len(hpos_T10):.3f}  resid={resid}")

claimed_set = [6,7,9,12,14,16]  # order-file claimed set, n=1 AND n=18 both dropped
sse2,k2,c2,resid2 = best_fit_over_menu(claimed_set)
print(f"\n[B] Claimed set {claimed_set} (n=1 dropped as 'transient', n=18/+55 never included):")
print(f"    best k={k2} ({float(k2):.4f}) c={c2} SSE={sse2} SSE/pt={sse2/len(claimed_set):.3f}  resid={resid2}")

claimed_plus55 = sorted(claimed_set + [18])
sse3,k3,c3,resid3 = best_fit_over_menu(claimed_plus55)
print(f"\n[C] Claimed set WITH +55 added back {claimed_plus55} (n=1 still dropped, n=18 restored):")
print(f"    best k={k3} ({float(k3):.4f}) c={c3} SSE={sse3} SSE/pt={sse3/len(claimed_plus55):.3f}  resid={resid3}")
print(f"    SSE degradation vs [B]: {sse2} -> {sse3}  (x{sse3/max(1,sse2):.1f})")
print(f"    Is 9/4 still the best k with +55 restored? {k3 == F(9,4)}")

full_all18 = list(range(1,19))
sse4,k4,c4,resid4 = best_fit_over_menu(hpos_T10)  # same as [A], restated for clarity
print(f"\n[D] (=A restated) No exclusions whatsoever (T=10 fixed threshold, keep every H): SSE/pt={sse4/len(hpos_T10):.3f}, k={k4}")

print()
print("="*70)
print("TASK 3: MONTE CARLO LOOK-ELSEWHERE NULL TEST")
print("="*70)
random.seed(20260705)
N=18
n_H = len(hpos_T10)
print(f"Observed: N={N} word length, nH={n_H} H-symbols (T=10), menu={len(RATIONAL_MENU)} rational candidates")

obs_sse, obs_k, obs_c, _ = best_fit_over_menu(hpos_T10)
obs_ssept = obs_sse/n_H
print(f"Observed full-{n_H}-point (no drops) best-over-menu: SSE={obs_sse} SSE/pt={obs_ssept:.4f} k={obs_k}")

obs_sse_c, obs_k_c, _, _ = best_fit_over_menu(claimed_set)
obs_ssept_c = obs_sse_c/len(claimed_set)
print(f"Observed CLAIMED 6-point (cherry-picked, dropped n=1 AND n=18) best-over-menu: SSE={obs_sse_c} SSE/pt={obs_ssept_c:.4f} k={obs_k_c}")

def random_hpos(nH, N, rng):
    return sorted(rng.sample(range(1,N+1), nH))

# Null A: fixed-size (nH=8) random word, no cherry-picking after the fact --
# fair comparison to [A]/[D] (full set, no drops).
rng = random.Random(20260705)
trials = 20000
hits_full = 0
t0=time.time()
for _ in range(trials):
    hp = random_hpos(n_H, N, rng)
    sse,k,c,_ = best_fit_over_menu(hp)
    if sse/n_H <= obs_ssept + 1e-9:
        hits_full += 1
frac_full = hits_full/trials
print(f"\n[Null A: fixed nH={n_H}, no cherry-picking, {trials} trials, {time.time()-t0:.1f}s]")
print(f"  fraction of random words fitting SOME simple rational at SSE/pt <= {obs_ssept:.4f}: {frac_full:.4f} ({hits_full}/{trials})")

# Null B: the REAL move that produced the claim -- start from an nH=8 (or
# 7, T=10-on-C11..26) random word, allow dropping exactly 1-2 points
# (the analysis dropped n=1 as "transient" AND never included n=18 to begin
# with -- effectively a 2-point drop from 8 candidates down to 6), take the
# best subset of size 6 from whatever nH the random word has (capped),
# and ask how often that beats the claimed SSE/pt.
print(f"\n[Null B: allowed to drop down to the best 6-of-{n_H} subset -- mimics the actual analysis move]")
trials2 = 800
hits_cherry = 0
t0=time.time()
def best_k_subset(hpos_full, subset_size, menu_nd=MENU_ND, menu=RATIONAL_MENU):
    best=None
    for combo in itertools.combinations(hpos_full, subset_size):
        sse,k,c,_ = best_fit_over_menu(list(combo), menu_nd, menu)
        if best is None or sse<best[0]:
            best=(sse,k,c,combo)
    return best

for _ in range(trials2):
    hp = random_hpos(n_H, N, rng)
    best = best_k_subset(hp, 6)
    if best[0]/6 <= obs_ssept_c + 1e-9:
        hits_cherry += 1
frac_cherry = hits_cherry/trials2
print(f"  fraction of random {n_H}-point words whose best 6-point subset fits this well (SSE/pt <= {obs_ssept_c:.4f}): {frac_cherry:.4f} ({hits_cherry}/{trials2}, {time.time()-t0:.1f}s)")

print()
print("="*70)
print("TASK 4: FREE-PARAMETER COUNT")
print("="*70)
params = {
    "k (rational rate)": 1,
    "c (integer offset)": 1,
    "H/L split threshold T": 1,
    "drop n=1 (C=11) as 'transient'": 1,
    "exclude n=18 (C=28, +55) from candidate set": 1,
}
total_params = sum(params.values())
n_data_claimed = 6
n_data_full = len(hpos_T10)
print("Choices spent to reach the claimed 9/4, c=3, SSE=1 result:")
for kk,v in params.items():
    print(f"  {v}  {kk}")
print(f"  TOTAL free choices = {total_params}")
print(f"  data points 'explained' by the claimed fit = {n_data_claimed}")
print(f"  ratio (choices : points) = {total_params}:{n_data_claimed} = {total_params/n_data_claimed:.2f}")
print(f"\n  For comparison, honest no-drop fit (T fixed, k+c only, no point exclusions):")
print(f"  params = 2 (k,c) [T is pre-registered at the variance-minimizing gap, not tuned to the Beatty fit]")
print(f"  points = {n_data_full}")
print(f"  ratio = 2:{n_data_full} = {2/n_data_full:.2f}")
print(f"  --> the claimed-fit ratio is {(total_params/n_data_claimed)/(2/n_data_full):.1f}x more parameter-dense than the honest no-drop fit")

print()
print("="*70)
print("TASK 5: PROVENANCE (from this session's own written record)")
print("="*70)
print("""W7A_FINDINGS.md sec 4, verbatim sequence:
  1. Grid search floor(n*k)+c over ALL 7 post-T=10 H-positions
     {1,6,7,9,12,14,16} (C=11..26 window) => best k=2.2, c=1, SSE=5.
     (2.2, not 9/4 -- the *global* best fit on the full available set at
     that time was NOT the claimed constant.)
  2. n=1 (C=11) was then dropped, described as "the break's transient",
     because it is also the single largest delta in that window (d=31)
     and adjacent to the known C<=10 base-law boundary.
  3. Refitting the remaining 6 points landed on k=9/4=2.25 EXACTLY, SSE=1.
  4. Later, C=27,28 were added (n=17,18) but n=18's d=55 -- the single
     LARGEST delta in the ENTIRE 18-point series, exceeding even the n=1
     transient's d=31 -- was never folded into the claimed set at all.
This is a reverse-fit signature: free k search with no external target,
discard the point that hurts the fit most, re-run, land exactly on a
"nice" fraction, name the fraction the finding. W7C (same session cluster)
independently swept the ENTIRE continued-fraction convergent lattice of
log2(3), beta=2-log2(3), 1/beta, and log2(3)-1 (convergents, semiconvergents,
mediants) and found NO match for 9/4 anywhere in that structure -- closest
hit was 3.7% relative error (convergent-quality matches in that same table
run 10^-3 to 10^-10). 9/4 has no independent theoretical anchor; it exists
only as the residue of two data-driven exclusions (n=1, and n=18/+55).
""")
