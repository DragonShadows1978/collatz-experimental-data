import sys, time
import wy_core_lean as wl

def edge_of(r):
    a = [m for m, v in r['records'].items() if v['alive']]
    return max(a) if a else None

KNOWN = {16: 93, 23: 163, 26: 205}
print("=== VALIDATION GATE (lean wy_core) ===", flush=True)
ok = True
for C, exp in KNOWN.items():
    t0 = time.time()
    mmax = 9 * (C + 1) + 53
    r = wl.find_edge_for_C(C, m_max=mmax, rss_cap_mb=8000, state_cap=4_000_000, verbose=False)
    g = edge_of(r)
    dt = time.time() - t0
    status = 'OK' if g == exp else f'FAIL exp={exp}'
    print(f"  C={C} edge={g} {status} peak_live={r['peak_live']} wall={r['wall']} t={dt:.1f}s", flush=True)
    if g != exp:
        ok = False
print("GATE PASS" if ok else "GATE FAILED", flush=True)
sys.exit(0 if ok else 1)
