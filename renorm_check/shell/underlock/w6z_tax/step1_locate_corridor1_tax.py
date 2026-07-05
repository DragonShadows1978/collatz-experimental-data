#!/usr/bin/env python3
"""
W6Z-TAX Step 1 -- locate & reproduce David's corridor-1 "-3.x% tax".

MISSION QUOTE: "In corridor 1 it's a -3.x percent tax; what was never
measured is the tax at each level."

SEARCH RESULT (documented in LEDGER_W6Z-TAX.md, cited to line):
The only -3.x% figure anywhere in the repo tied to a "corridor" and a
"per heartbeat tax" is the KILLED-SURVIVOR SPECTRAL-RADIUS contraction:

  SPECTRAL_RADIUS_RESULTS.txt:30-31
    "rho LOCKS at 0.960647 from m=10 onward (6.4M states).
     Permanent 3.94% contraction per heartbeat."
  SPECTRAL_RADIUS_RESULTS.txt:13  header: "C=3 (narrow corridor -- hard floor on rho)"
  COLLATZ_PROOF.md:484  "stabilizes at 0.03935 -- a permanent 3.94% contraction per heartbeat"
  GHOST_GEOMETRY_RELEASE.md:104   same 0.9607 / 3.94% / "per heartbeat"

What is divided by what:
  tau_spectral(C) = 1 - rho(C)
where rho(C) = spectral radius (dominant eigenvalue magnitude) of the
COMPOSED 53-step killed-survivor transition operator M(C) on the
non-terminal, non-exiting residue-automaton states at corridor width C.
rho is a per-HEARTBEAT survival-mass multiplier: |mass(after 1 heartbeat)|
~ rho * |mass(before)| along the dominant eigenvector. So 1-rho is the
fraction of surviving mass KILLED per heartbeat = the "tax".

The headline 3.94% is the C=3 *m->inf locked* value (rho=0.960647).
This is NOT the C=1 spectral radius (which is a ~97% contraction, i.e.
rho tiny), so "corridor 1" in the mission does NOT map to C=1's rho.
Two candidate readings of "corridor 1" are computed and reported; the
ledger states which one lands at -3.x% and flags the ambiguity honestly.

This script reproduces rho(C) from scratch (independent Python power
iteration on the composed operator; float64 like the Rust tool, exact
integer residue arithmetic) and confirms:
  (a) C=3 locked rho -> 0.960647, tau = 3.94%  (the headline number)
  (b) the C=1..15 spectral tax schedule tau_spectral(C) = 1 - rho(C)
      at the converged m (this is Step 4's spectral column too).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).parent

# ---------------------------------------------------------------------
# Exact Sturmian credits (bit_length, no floats) -- same as sparse_instrument
# ---------------------------------------------------------------------
def floor_k_alpha(k: int) -> int:
    if k == 0:
        return 0
    return (3 ** k).bit_length() - 1


def credit_at_step(k: int) -> int:
    return floor_k_alpha(k + 1) - floor_k_alpha(k)


HEARTBEAT = 53


def credits_53():
    return [credit_at_step(k) for k in range(HEARTBEAT)]


# ---------------------------------------------------------------------
# Killed-survivor transition operator, one step (mirrors rust/spectral_radius.rs
# build_step_matrix EXACTLY: kill terminal r==1 states; uniform 1/max_a over
# legal exponents a=1..d+c that keep the deficit in [0,C]).
# ---------------------------------------------------------------------
def pow2_inv_mod(a: int, mod: int) -> int:
    """inverse of 2^a mod 3^m (mod is a power of 3, so 2 is a unit)."""
    return pow(pow(2, a, mod), -1, mod)


def next_residue(r: int, a: int, mod: int) -> int:
    val = (3 * r + 1) % mod
    return (val * pow2_inv_mod(a, mod)) % mod


def build_step_operator(c: int, C: int, mod: int):
    """Return (index_of, transitions) where transitions is a list of
    (dst_idx, src_idx, weight). States: (d, r), d in [0,C], r in Z/mod,
    r != 1 (terminal killed). Column-stochastic-ish: each src distributes
    weight 1/max_a over its legal destinations (destinations landing on
    r==1 or leaving [0,C] are dropped -> that mass LEAKS OUT = killed)."""
    states = [(d, r) for d in range(C + 1) for r in range(mod) if r != 1]
    idx = {s: i for i, s in enumerate(states)}
    trans = []
    for (d, r) in states:
        src = idx[(d, r)]
        max_a = d + c
        if max_a < 1:
            continue
        total = float(max_a)
        for a in range(1, max_a + 1):
            d_next = d + c - a
            if d_next < 0 or d_next > C:
                continue
            r_next = next_residue(r, a, mod)
            if r_next == 1:
                continue  # killed
            dst = idx[(d_next, r_next)]
            trans.append((dst, src, 1.0 / total))
    return states, idx, trans


def compose_heartbeat_apply(v, ops):
    """Apply the composed 53-step operator to vector v (list of floats),
    one step at a time (M53 * ... * M1) * v. ops = list of 53 (n, trans)."""
    for (n, trans) in ops:
        w = [0.0] * n
        for (dst, src, wt) in trans:
            w[dst] += wt * v[src]
        v = w
    return v


def spectral_radius(C: int, m: int, max_iter: int = 20000, tol: float = 1e-13):
    """Power iteration for rho of the composed 53-step killed operator at
    (C, m). All 53 step-operators share the same state indexing (same C, m),
    so we build them once and re-apply. Returns rho (float)."""
    mod = 3 ** m
    creds = credits_53()
    # all step operators use the identical state set (fixed C, mod)
    states0, idx0, _ = build_step_operator(creds[0], C, mod)
    n = len(states0)
    # build all 53 transition lists on the shared indexing
    ops = []
    for step in range(HEARTBEAT):
        c = creds[step]
        # rebuild with same idx ordering (states identical for fixed C,mod)
        trans = []
        for (d, r) in states0:
            src = idx0[(d, r)]
            max_a = d + c
            if max_a < 1:
                continue
            total = float(max_a)
            for a in range(1, max_a + 1):
                d_next = d + c - a
                if d_next < 0 or d_next > C:
                    continue
                r_next = next_residue(r, a, mod)
                if r_next == 1:
                    continue
                trans.append((idx0[(d_next, r_next)], src, 1.0 / total))
        ops.append((n, trans))

    import math
    v = [1.0 / math.sqrt(n)] * n
    lam = 0.0
    for _ in range(max_iter):
        w = compose_heartbeat_apply(v, ops)
        nrm = math.sqrt(sum(x * x for x in w))
        if nrm < 1e-30:
            return 0.0
        v = [x / nrm for x in w]
        if abs(nrm - lam) < tol * max(nrm, 1e-15):
            return nrm
        lam = nrm
    return lam


def main():
    print("=== W6Z-TAX Step 1: reproduce David's corridor-1 -3.x% tax ===\n")
    print("Definition under test: tau_spectral(C) = 1 - rho(C), rho = spectral")
    print("radius of the composed 53-step killed-survivor operator (per-heartbeat")
    print("survival-mass multiplier). Headline archived number: C=3 locked")
    print("rho=0.960647 -> 3.94% (SPECTRAL_RADIUS_RESULTS.txt:30-31).\n")

    # (a) reproduce the headline C=3 value at increasing m (watch it lock)
    print("--- (a) C=3, sweep m (reproduce the LOCK at rho=0.960647) ---")
    print(f"{'m':>3} {'states':>10} {'rho':>14} {'gap=1-rho':>12} {'tax %':>8}")
    for m in range(1, 8):
        rho = spectral_radius(3, m)
        gap = 1.0 - rho
        print(f"{m:>3} {(3+1)*3**m - (3+1):>10} {rho:>14.9f} {gap:>12.6f} {100*gap:>7.3f}%")
    # archived C=3 lock target
    print("\n  archived C=3 lock (SPECTRAL_RADIUS_RESULTS.txt:25,30): "
          "rho=0.960647 gap=0.039353 tax=3.94%")

    # (b) the spectral tax schedule tau_spectral(C) for C=1..15 at a converged m.
    # m=6 already >12 decimal-converged in the archived C>=10 universal table
    # for the *anchor* rho; for the killed-operator rho we sweep to m where it
    # has stabilized to the precision we can afford (state count (C+1)*3^m grows,
    # keep m modest -- report the value and the m used).
    print("\n--- (b) spectral tax schedule tau_spectral(C) = 1 - rho(C), C=1..15 ---")
    print(f"{'C':>3} {'m_used':>7} {'rho':>14} {'1-rho':>12} {'tax %':>8}")
    schedule = {}
    for C in range(1, 16):
        # pick m so (C+1)*3^m stays under ~1.5e5 states (CPU-cheap); larger C -> smaller m
        m = 1
        while (C + 1) * 3 ** (m + 1) <= 120_000 and m < 7:
            m += 1
        rho = spectral_radius(C, m)
        gap = 1.0 - rho
        schedule[C] = (m, rho, gap)
        print(f"{C:>3} {m:>7} {rho:>14.9f} {gap:>12.6f} {100*gap:>7.3f}%")

    # write CSV
    import csv
    with open(HERE / "step1_spectral_tax.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["C", "m_used", "rho", "one_minus_rho", "tax_pct"])
        for C in range(1, 16):
            m, rho, gap = schedule[C]
            w.writerow([C, m, f"{rho:.12f}", f"{gap:.12f}", f"{100*gap:.4f}"])
    print(f"\nWrote {HERE / 'step1_spectral_tax.csv'}")


if __name__ == "__main__":
    main()
