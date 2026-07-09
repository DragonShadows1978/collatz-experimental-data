import sys, time
import wy_core_lean as wl

def edge_of(r):
    a = [m for m, v in r['records'].items() if v['alive']]
    return max(a) if a else None

C, exp = 26, 205
t0 = time.time()
mmax = 9 * (C + 1) + 53
r = wl.find_edge_for_C(C, m_max=mmax, rss_cap_mb=8000, state_cap=4_000_000, verbose=True)
g = edge_of(r)
dt = time.time() - t0
status = 'OK' if g == exp else f'FAIL exp={exp}'
print(f"  C={C} edge={g} {status} peak_live={r['peak_live']} wall={r['wall']} t={dt:.1f}s", flush=True)
sys.exit(0 if g == exp else 1)
