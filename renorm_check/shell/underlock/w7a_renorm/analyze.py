import math, csv, json
alpha = math.log2(3); beta = 2 - alpha
# edges through C=26 (measured, exact, cross-checked); extend cells arrive from the sweep.
edges = {1:4,2:7,3:9,4:12,5:14,6:16,7:19,8:21,9:24,10:26,11:57,12:63,13:68,14:71,15:79,
         16:93,17:108,18:110,19:130,20:132,21:139,22:157,23:163,24:188,25:192,26:205}

def load_extra():
    try:
        for line in open('../w7a_renorm/new_edges.txt'):
            C,e = line.split(); edges[int(C)] = int(e)
    except FileNotFoundError: pass
load_extra()

# --- THE THREE-WAY FORK ---
# base law exact C<=10. residual r(C) = edge - floor((C+1)/beta).
# H1 renormalization: r(C) snaps to a clean law at denominator 306 (second convergent 485/306).
# H2 Beatty: increments form a Sturmian word (aperiodic, 2 symbols) -> characterize the word.
# H3 smooth: r(C)/C -> constant (a linear correction I mis-read as jumps).
rows=[]
for C in sorted(edges):
    e=edges[C]; base=math.floor((C+1)/beta); r=e-base
    rows.append((C,e,base,r, r/53, r/306*22, e*22/(C+1), e*beta/(C+1)))
print("C  edge base  r    r/53   r*22/306  e*22/(C+1)  e*beta/(C+1)")
for C,e,b,r,r53,r306,ratio,eb in rows:
    print(f"{C:2d}  {e:3d}  {b:3d}  {r:4d}  {r53:.3f}  {r306:.4f}   {ratio:.3f}     {eb:.4f}")

# H3 test: is r/C converging?
print("\n[H3 smooth] r(C)/(C+1) for C>=11 (constant => smooth linear correction):")
xs=[C for C in sorted(edges) if C>=11]
print("  ", [round(edges[C]-math.floor((C+1)/beta),0)/(C+1) for C in xs])

# H2 test: increment word past C=10, classify small vs big
print("\n[H2 Beatty] edge increments C>=11, symbol L(<=4)/H(>=5):")
prev=None; word=[]
for C in sorted(edges):
    if prev is not None and C>=11:
        d=edges[C]-edges[prev]; word.append('L' if d<=4 else 'H')
    prev=C
print("  ", ''.join(word), f"  ({word.count('H')}H/{word.count('L')}L)")
# density of H should approach an algebraic constant if Sturmian
if word:
    print(f"   H-density={word.count('H')/len(word):.4f}  (compare beta={beta:.4f}, 1-beta={1-beta:.4f}, 2beta-... )")

# H1 test: does floor((C+1)*q2/(q2*beta)) with q2=306 improve? i.e. use the 306-convergent rational for beta
# 485/306 approximates alpha; beta ~ (2*306-485)/306 = 127/306
p2,q2=485,306; beta306=(2*q2-p2)/q2
print(f"\n[H1 renorm] beta via 306-convergent = 127/306 = {beta306:.6f} vs true {beta:.6f}")
print("  edge_pred306 = floor((C+1)*306/127), residual:")
bad=0
for C in sorted(edges):
    pred=math.floor((C+1)*q2/(2*q2-p2)); r=edges[C]-pred
    tag = '' if abs(r)<=1 else ' <-- off'
    if abs(r)>1: bad+=1
    print(f"   C={C:2d} edge={edges[C]:3d} pred306={pred:4d} r={r:+d}{tag}")
print(f"  306-law cells within +-1: {len(edges)-bad}/{len(edges)}")
