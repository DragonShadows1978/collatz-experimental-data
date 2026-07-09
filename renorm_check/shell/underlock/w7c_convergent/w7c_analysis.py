"""
W7C: Exact CF analysis of log2(3), beta=2-log2(3), 1/beta.
All arithmetic in Fraction (for convergents/mediants) and mpmath mp.dps=60
(for the irrational CF expansion and high-precision floats feeding regressions).
"""
from fractions import Fraction
import mpmath as mp

mp.mp.dps = 60

def cf_expand(x, n_terms=30):
    """Continued fraction expansion of mpmath mpf x. Returns list of partial quotients."""
    terms = []
    x = mp.mpf(x)
    for _ in range(n_terms):
        a = mp.floor(x)
        terms.append(int(a))
        frac = x - a
        if frac == 0:
            break
        x = 1/frac
    return terms

def convergents(a_list):
    """Given partial quotients a0,a1,a2,..., return list of (k, p_k, q_k) as exact Fractions."""
    convs = []
    p_prev2, p_prev1 = 0, 1
    q_prev2, q_prev1 = 1, 0
    for k, a in enumerate(a_list):
        p_k = a*p_prev1 + p_prev2
        q_k = a*q_prev1 + q_prev2
        convs.append((k, p_k, q_k))
        p_prev2, p_prev1 = p_prev1, p_k
        q_prev2, q_prev1 = q_prev1, q_k
    return convs

log2_3 = mp.log(3)/mp.log(2)
beta = 2 - log2_3
inv_beta = 1/beta

print("="*70)
print("log2(3) =", log2_3)
print("beta = 2-log2(3) =", beta)
print("1/beta =", inv_beta)
print("log2(3)-1 =", log2_3-1)
print("="*70)

N = 25
cf_log23 = cf_expand(log2_3, N)
cf_beta = cf_expand(beta, N)
cf_invbeta = cf_expand(inv_beta, N)
cf_log23m1 = cf_expand(log2_3-1, N)

print("\nCF(log2 3) partial quotients:", cf_log23)
print("CF(beta)   partial quotients:", cf_beta)
print("CF(1/beta) partial quotients:", cf_invbeta)
print("CF(log2(3)-1) partial quotients:", cf_log23m1)

conv_log23 = convergents(cf_log23)
conv_beta = convergents(cf_beta)
conv_invbeta = convergents(cf_invbeta)
conv_log23m1 = convergents(cf_log23m1)

def print_convs(name, convs):
    print(f"\n--- Convergents of {name} ---")
    for k, p, q in convs:
        val = mp.mpf(p)/mp.mpf(q) if q != 0 else mp.mpf('inf')
        print(f"  k={k:2d}  p={p:>10d}  q={q:>10d}   p/q={val}")

print_convs("log2(3)", conv_log23)
print_convs("beta=2-log2(3)", conv_beta)
print_convs("1/beta", conv_invbeta)
print_convs("log2(3)-1", conv_log23m1)

# locate specific numbers: 53, 84, 22, 306, 665 -- as p or q in any convergent list
targets = [53, 84, 22, 306, 665]
print("\n" + "="*70)
print("SEARCHING for targets", targets, "as p or q in any convergent above")
print("="*70)
all_convs = {
    "log2(3)": conv_log23,
    "beta": conv_beta,
    "1/beta": conv_invbeta,
    "log2(3)-1": conv_log23m1,
}
for t in targets:
    hits = []
    for name, convs in all_convs.items():
        for k, p, q in convs:
            if p == t or q == t:
                hits.append((name, k, p, q, "p" if p==t else "q"))
    print(f"target {t}: {hits}")
