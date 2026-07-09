#!/usr/bin/env python3
"""Gate 0: verify v3(3x+1) = 0 identically, on 1000 odd trajectories."""

def vp(m, p):
    v = 0
    while m % p == 0:
        m //= p
        v += 1
    return v

def collatz_odd_trajectory(n0, cap=100000):
    """Return list of m=3x+1 values encountered at each odd step, and whether it reached 1."""
    x = n0
    ms = []
    steps = 0
    while x != 1:
        m = 3 * x + 1
        ms.append(m)
        # divide out all factors of 2
        v2 = 0
        y = m
        while y % 2 == 0:
            y //= 2
            v2 += 1
        x = y
        steps += 1
        if steps > cap:
            return ms, False
    return ms, True

exceptions = 0
total_steps = 0
n_traj = 0
for n0 in range(1, 2001):  # odd numbers 1..2001 -> take first 1000 odd
    if n0 % 2 == 0:
        continue
    if n_traj >= 1000:
        break
    ms, ok = collatz_odd_trajectory(n0)
    if not ok:
        print(f"WARNING: trajectory {n0} did not converge within cap")
        continue
    n_traj += 1
    for m in ms:
        total_steps += 1
        if vp(m, 3) != 0:
            exceptions += 1
            print(f"EXCEPTION at n0={n0}, m={m}, v3={vp(m,3)}")

print(f"Gate 0 result: {n_traj} trajectories, {total_steps} total odd-steps, {exceptions} exceptions to v3=0")
