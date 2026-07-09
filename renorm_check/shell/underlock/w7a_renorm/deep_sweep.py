import sys, math, time
BASE='/mnt/ForgeRealm/collatz-experimental-data/renorm_check/shell/underlock'
sys.path.insert(0, BASE+'/w6y_regime')
import wy_core as wy
def edge_of(r):
    a=[m for m,v in r['records'].items() if v['alive']]
    return max(a) if a else None
KNOWN={16:93,23:163,26:205}
print("=== GATE ===", flush=True); ok=True
for C,exp in KNOWN.items():
    g=edge_of(wy.find_edge_for_C(C, m_max=min(9*(C+1)+53,300), verbose=False))
    print(f"  C={C} edge={g} {'OK' if g==exp else 'FAIL exp='+str(exp)}", flush=True)
    if g!=exp: ok=False
if not ok: print("GATE FAILED"); sys.exit(1)
print("GATE PASS\n=== DEEP SWEEP C=27..40 ===", flush=True)
out=open(BASE+'/w7a_renorm/w7a_new_edges.txt','w')
for C in range(27,41):
    t0=time.time(); mmax=9*(C+1)+53
    e=edge_of(wy.find_edge_for_C(C, m_max=mmax, verbose=False)); dt=time.time()-t0
    print(f"  C={C} edge={e} t={dt:.0f}s mmax={mmax}", flush=True)
    out.write(f"{C} {e}\n"); out.flush()
    if dt>1200: print(f"  wall at C={C}",flush=True); break
out.close(); print("DONE", flush=True)
