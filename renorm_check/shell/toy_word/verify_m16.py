import math, time
import numpy as np

# Independent verification of W6B capstone D_toy(16) — no shared code with the repo.
def floor_kphi(k):
    return (k + math.isqrt(5*k*k)) // 2
def credit_toy(k):
    return floor_kphi(k+1) - floor_kphi(k)

def D_toy(m, C, steps=53):
    modulus = 3**m
    live = {d: np.ones(modulus, dtype=bool) for d in range(C+1)}
    perms = {}
    for a in range(1, C+3):
        r = np.arange(modulus, dtype=np.int64)
        p = ((3*r+1) % modulus) * pow(pow(2,a,modulus), -1, modulus) % modulus
        perms[a] = p.astype(np.int32)
        del r, p
    for k in range(steps):
        c = credit_toy(k)
        nxt = {d: np.zeros(modulus, dtype=bool) for d in range(C+1)}
        for d in range(C+1):
            idx = np.nonzero(live[d])[0]
            if idx.size == 0: continue
            for a in range(max(1, d+c-C), d+c+1):
                nxt[d+c-a][perms[a][idx]] = True
        live = nxt
        print(f'step {k}: live={sum(int(x.sum()) for x in live.values())}', flush=True)
    alive = [C-d for d in range(C+1) if live[d][1]]
    dead_depth = max((C-d for d in range(C+1)
                      for _ in [0] if (~live[d] & (np.arange(modulus)%3!=0)).any()), default=0)
    return (min(alive) if alive else None), dead_depth

t0 = time.time()
d13, _ = D_toy(13, 14)
print(f'CONTROL m=13 C=14: D_toy={d13} (expect 5)  [{time.time()-t0:.0f}s]', flush=True)
t0 = time.time()
d16, shell = D_toy(16, 14)
print(f'CAPSTONE m=16 C=14: D_toy={d16} shell_depth={shell}  [{time.time()-t0:.0f}s]', flush=True)
print('VERDICT:', 'CONFIRMS agent (6)' if d16 == 6 else f'DISAGREES with agent: {d16}')
