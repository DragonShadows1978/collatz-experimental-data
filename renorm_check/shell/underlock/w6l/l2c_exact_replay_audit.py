#!/usr/bin/env python3
"""
W6L-L2c -- Exact-integer replay audit of every excursion witness in
play: K2's own certified CSV argmins (t=1..10, len<=10), the L2
K2-replica catalog (len<=10, all argmin states), and the L2 len-14
extension catalog. Motivated by the L2 length-extension finding plus
the trit-cascade analysis of the representative DP:

  backward_step_mod reduces to the working modulus 3^T each step; the
  division by 3 makes residues exact only in the low T-d trits after
  d steps (pred_true - pred_repr = k*2^a*3^(T-1) mod 3^T for lift k).
  Therefore a t-precision readout of a length-d excursion is
  GUARANTEED faithful only when t + d <= T. K2's own certified
  argmins (e.g. t=10 at length 8, T=10) live OUTSIDE this zone --
  their validity as upper bounds rests on exact replay, which this
  script performs; their MINIMALITY is re-certified separately by the
  exact ladder DP (l2d).

Replay = from exact integer v=1, apply backward_predecessor_exact
(w6e/engine.py, Path-A/C shared primitive, exact big-int arithmetic),
enforcing the parity legality at every step, then check v == 1
(mod 3^t) and cost == claimed. PASS = the chain is a genuine
excursion of the exact game at the claimed cost (valid upper bound).
FAIL = representative-DP artifact (the claimed value is unsupported).
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

HERE = Path(__file__).parent
W6K = HERE.parent / "w6k"
W6E = HERE.parent / "w6e"
sys.path.insert(0, str(W6K))
sys.path.insert(0, str(W6E))

from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402
from k2_precision_cost_curve_redo import shared_layered_dp  # noqa: E402
from l2_per_trit_tax import all_argmin_excursions  # noqa: E402


def exact_replay(seq, t):
    """Replay a-seq on exact integers from v=1. Returns (ok, reason)."""
    v = 1
    for j, a in enumerate(seq):
        p = forced_parity_for_backward_step(v)
        if p is None:
            return False, f"class-0 dead at step {j}"
        if (a % 2 == 0) != (p == 0):
            return False, f"parity violation at step {j} (a={a}, forced={'even' if p==0 else 'odd'})"
        v = backward_predecessor_exact(v, a)
    if v % (3 ** t) != 1:
        return False, f"final v !== 1 mod 3^{t} (v mod = {v % 3**t})"
    return True, "exact"


def audit(label, entries):
    """entries: list of (t, claimed_cost, seq). Returns n_pass, n_fail, fails."""
    print(f"\n--- {label} ---")
    n_pass = n_fail = 0
    fails = []
    for (t, cost, seq) in entries:
        ok, reason = exact_replay(seq, t)
        cost_ok = sum(a - 2 for a in seq) == cost
        verdict = ok and cost_ok
        if verdict:
            n_pass += 1
        else:
            n_fail += 1
            fails.append((t, cost, seq, reason if not ok else "cost mismatch"))
        zone = "IN guarantee zone" if (t + len(seq) <= 10) else f"OUTSIDE zone (t+d={t+len(seq)}>10)"
        print(f"  t={t:>2} cost={cost:>3} len={len(seq):>2} [{zone}]: "
              f"{'EXACT-VERIFIED' if verdict else '*** ARTIFACT: ' + (reason if not ok else 'cost mismatch') + ' ***'}")
    return n_pass, n_fail, fails


def main():
    # 1. K2's own certified CSV argmins
    k2_entries = []
    with open(W6K / "k2_precision_cost_curve.csv", newline="") as f:
        for row in csv.DictReader(f):
            seq = tuple(int(x) for x in row["argmin_a_seq"].split(","))
            k2_entries.append((int(row["t"]), int(row["min_cost"]), seq))
    p1, f1, fails1 = audit("K2 certified CSV argmins (t=1..10, len<=10, mod 3^10)", k2_entries)

    # 2. L2 K2-replica full catalog (len<=10) -- re-derived (not saved as CSV by l2 core)
    hist10 = shared_layered_dp(3 ** 10, 10, 150)
    replica_entries = []
    for t in range(1, 11):
        cost, cat = all_argmin_excursions(hist10, t, 10)
        for (d, seq, _) in cat:
            replica_entries.append((t, cost, seq))
    p2, f2, fails2 = audit("L2 K2-replica catalog (len<=10, ALL argmin states)", replica_entries)

    # 3. L2 len-14 extension catalog (from CSV)
    ext_entries = []
    with open(HERE / "l2_argmin_catalog.csv", newline="") as f:
        for row in csv.DictReader(f):
            seq = tuple(int(x) for x in row["a_seq"].split(","))
            ext_entries.append((int(row["t"]), int(row["min_cost"]), seq))
    p3, f3, fails3 = audit("L2 len-14 extension catalog (mod 3^10 DP pushed past its envelope)", ext_entries)

    print(f"\n=== AUDIT SUMMARY ===")
    print(f"K2 certified argmins:  {p1} verified, {f1} artifacts")
    print(f"L2 replica catalog:    {p2} verified, {f2} artifacts")
    print(f"L2 len-14 catalog:     {p3} verified, {f3} artifacts")
    all_fails = fails1 + fails2 + fails3
    if all_fails:
        print("\nARTIFACT LIST (claims REJECTED, not usable even as upper bounds):")
        for (t, cost, seq, reason) in all_fails:
            print(f"  t={t} cost={cost} seq={seq}: {reason}")
    print("\nInterpretation: EXACT-VERIFIED rows are genuine upper bounds on the exact "
          "excursion game. Minimality of any value outside the t+d<=10 guarantee zone "
          "requires the exact ladder DP (l2d).")


if __name__ == "__main__":
    main()
