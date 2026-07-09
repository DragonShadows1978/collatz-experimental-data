"""
Task 3: Is 9/4 a convergent, mediant, or semiconvergent of log2(3), beta,
1/beta, log2(3)-1, or 1/(2-log2 3) [note: 1/(2-log2 3) == 1/beta, already listed
-- same object]?
"""
from fractions import Fraction
import mpmath as mp
mp.mp.dps = 50

target = Fraction(9,4)
print(f"Target: 9/4 = {float(target)}")

log23 = mp.log(3)/mp.log(2)
beta = 2-log23
inv_beta = 1/beta
log23m1 = log23-1
print(f"log2(3)={log23}\nbeta={beta}\n1/beta={inv_beta}\nlog2(3)-1={log23m1}")
print("Note: 1/(2-log2 3) = 1/beta -- identical to already-listed quantity.")

def cf_expand(x, n_terms=15):
    terms = []
    x = mp.mpf(x)
    for _ in range(n_terms):
        a = mp.floor(x)
        terms.append(int(a))
        frac = x-a
        if frac==0: break
        x = 1/frac
    return terms

def convergents(a_list):
    convs=[]
    p2,p1=0,1
    q2,q1=1,0
    for k,a in enumerate(a_list):
        p=a*p1+p2; q=a*q1+q2
        convs.append((k,p,q))
        p2,p1=p1,p
        q2,q1=q1,q
    return convs

def semiconvergents(a_list):
    """Semiconvergents (intermediate fractions) between convergent k-1 and k:
    p = i*p_{k-1} + p_{k-2}, q = i*q_{k-1} + q_{k-2}, for i=1..a_k."""
    semis=[]
    p2,p1=0,1
    q2,q1=1,0
    for k,a in enumerate(a_list):
        for i in range(1,a+1):
            p = i*p1+p2
            q = i*q1+q2
            semis.append((k,i,p,q))
        p2,p1=p1,a*p1+p2
        q2,q1=q1,a*q1+q2
    return semis

quantities = {
    "log2(3)": log23,
    "beta=2-log2(3)": beta,
    "1/beta": inv_beta,
    "log2(3)-1": log23m1,
}

for name, val in quantities.items():
    print(f"\n{'='*60}\n{name}\n{'='*60}")
    cf = cf_expand(val, 15)
    convs = convergents(cf)
    print("Convergents p/q:")
    for k,p,q in convs:
        if q==0: continue
        print(f"  k={k} p={p} q={q}  p/q={float(mp.mpf(p)/mp.mpf(q)) if q else 'inf'}")
        if p==9 and q==4:
            print("    *** EXACT MATCH TO 9/4 ***")
    print("Semiconvergents (k, i, p, q) -- intermediate Stern-Brocot fractions:")
    semis = semiconvergents(cf)
    matches=[]
    for k,i,p,q in semis:
        if p==9 and q==4:
            matches.append((k,i,p,q))
        if q!=0:
            pass
    if matches:
        print(f"    *** 9/4 FOUND as semiconvergent: {matches} ***")
    else:
        print("    9/4 not found exactly among semiconvergents computed.")
    # find CLOSEST semiconvergent/convergent to 9/4 by |p/q - 9/4| and by
    # simplicity (small q)
    all_frac = [(p,q,'conv',k) for k,p,q in convs if q!=0] + [(p,q,'semi',(k,i)) for k,i,p,q in semis if q!=0]
    best = None
    for p,q,kind,idx in all_frac:
        err = abs(Fraction(p,q) - target)
        if best is None or err < best[0]:
            best = (err, p, q, kind, idx)
    print(f"CLOSEST fraction to 9/4 among convergents+semiconvergents: p/q={best[1]}/{best[2]} ({best[3]} idx={best[4]}), |diff|={float(best[0])}")

    # Also: is 9/4 close to any LOW-q convergent/semiconvergent by relative error?
    close_hits = [(p,q,kind,idx,float(abs(Fraction(p,q)-target))) for p,q,kind,idx in all_frac if q<=100]
    close_hits.sort(key=lambda t:t[4])
    print("Best 5 low-denominator (q<=100) hits:")
    for p,q,kind,idx,err in close_hits[:5]:
        print(f"    p/q={p}/{q} ({kind} idx={idx})  |diff from 9/4|={err}  rel_err={err/2.25}")

# Mediant check: mediant of two convergents p1/q1, p2/q2 is (p1+p2)/(q1+q2).
# Check mediants of ADJACENT convergents of log2(3) (and beta) for 9/4.
print("\n" + "="*60)
print("Mediant check: adjacent convergents of log2(3), does any mediant = 9/4?")
print("="*60)
cf = cf_expand(log23, 12)
convs = convergents(cf)
for i in range(len(convs)-1):
    k1,p1,q1 = convs[i]
    k2,p2,q2 = convs[i+1]
    mp_, mq_ = p1+p2, q1+q2
    print(f"  mediant of k={k1}({p1}/{q1}) and k={k2}({p2}/{q2}) = {mp_}/{mq_} = {float(mp_/mq_) if mq_ else 'inf'}", "  *** = 9/4 ***" if (mp_,mq_)==(9,4) else "")

# direct: is 9/4 close to log2(3)-related simple combos, e.g. beta*... or
# just report: since target 2.25 lives near 1/beta=2.409 region (both >2 <3),
# compare gap
print(f"\n9/4 = 2.25 exactly.")
print(f"1/beta = {float(inv_beta)}  (nearest 'natural' home for a ~2.4 number)")
print(f"|9/4 - 1/beta| = {float(abs(mp.mpf(9)/4 - inv_beta))}")
print(f"9/4 as convergent of 1/beta's CF? convergents printed above for 1/beta -- check p=9,q=4 there specifically")
