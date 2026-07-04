#!/usr/bin/env python3
"""
W6P-URGENT sanity check: validate the forward depth recursion
d_k = d_{k-1} + c_k - a_k (k=1..m, forward-order chain, d in [0,C])
against engine.bfs_Dm's OWN validated chain extraction, on small m
where full BFS is tractable. This pins down, before using it on the
m=29 breach witness, that "does there exist d_0 in [0,C] making the
whole forward walk ceiling-legal" is the RIGHT and ONLY extra check
beyond parity/congruence -- by confirming it holds (as it must) for
bfs_Dm's own certified-optimal chain.
"""
import sys
from pathlib import Path

HERE = Path(__file__).parent
UNDERLOCK = HERE.parent
sys.path.insert(0, str(UNDERLOCK))
sys.path.insert(0, str(UNDERLOCK / "w6e"))

from engine import bfs_Dm  # noqa: E402
from e1_walkers import credit_true  # noqa: E402


def ceiling_legal_exists(chain, C):
    """Sweep d_0 in [0,C]; return (exists_legal, d0_list_that_work)."""
    good = []
    for d0 in range(0, C + 1):
        d = d0
        ok = True
        for (c, a) in chain:
            d = d + c - a
            if d < 0 or d > C:
                ok = False
                break
        if ok:
            good.append(d0)
    return (len(good) > 0), good


def main():
    for m in [5, 8]:
        C = 20
        D, chain = bfs_Dm(credit_true, m, C=C, anchor_steps=53, want_chain=True)
        print(f"m={m} D={D} chain(forward order, (c,a) pairs)={chain}")
        exists, good_d0 = ceiling_legal_exists(chain, C)
        print(f"  ceiling-legal d0 in [0,{C}] exists: {exists}, "
              f"good d0 values: {good_d0[:5]}{'...' if len(good_d0) > 5 else ''}")
        # Also confirm: max cumulative (a-c) over the chain == D (the
        # achieved value), independent check of the extraction itself.
        running = 0
        maxrun = 0
        for (c, a) in chain:
            running += (a - c)
            maxrun = max(maxrun, running)
        print(f"  max cumulative (a-c) over extracted chain = {maxrun} "
              f"(should equal D={D}): {'MATCH' if maxrun == D else 'MISMATCH -- investigate'}")
        assert exists, f"m={m}: bfs_Dm's own optimal chain has NO ceiling-legal d0 -- relation is WRONG"
        assert maxrun == D, f"m={m}: max(a-c) cumulative != D -- relation direction is WRONG"
    print("\nSANITY PASSED: forward recursion d_k=d_{k-1}+c_k-a_k, ceiling-legal-d0-exists check, "
          "and max-cumulative(a-c)==D all agree with bfs_Dm's certified chain on m=5,8.")


if __name__ == "__main__":
    main()
