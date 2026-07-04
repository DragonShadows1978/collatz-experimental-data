#!/usr/bin/env python3
"""
W6E-E3 -- prefix-tightness census (targets the LOWER bound), per
W6E_BOUND_PAIR_MECH_ORDER.md section E3.

For each ground-truth row, regenerate one optimal chain by exhaustive
search (engine.bfs_Dm(want_chain=True), the SAME validated engine used
in E1/verify_engine -- scalar dict path, chain extraction via parent
pointers). Tabulate the running sum g(k) = Sigma_{j<=k}(a_j - c_j),
where k indexes BACKWARD from the terminal (k=1 is the single step
closest to the terminal, k=m is the whole window) -- i.e. g(k) is
computed over the LAST k steps of the forward chain (a suffix in
forward-chain terms, a prefix in the order's backward-walk framing).
Compare against the candidate prefix bound floor((p*k+1)/q) (mirror
form floor((p*k-1)/q) for the real system, per the order).

Also runs the keystone per-prefix identity check (E3's own integrity
check, doubling as a second engine cross-validation): 2^{Sigma a over
last k steps} == S_k (mod 3^k), verified via engine.keystone_check
(already exercised in verify_engine.py on a sample; here run on EVERY
row/chain actually used by this experiment, per the order's explicit
instruction "on every chain used").

SCOPE WALL (reported honestly, not silently absorbed): chain
extraction uses the scalar Python dict BFS (needed for parent-pointer
backtracking), which is fast only up to about m=13 (3^13 states x C
depths) at CPU/minutes-scale. m=14..16 rows (sqrt2 has 3 such: 14,15,
16; golden has 1: 16) are SKIPPED for chain extraction (no optimal
chain regenerated) -- listed explicitly as skipped, not silently
dropped, per the order's own "skip and say so otherwise" clause.

Ground truth sources: same as E1 (shell/underlock/D_golden_per8_table
.csv + _m16.csv, D_sqrt2_per12_table.csv + _heavy_table.csv,
underlock_words.py). "Candidate prefix bound" p/q: golden-per8 uses
(p,q)=(3,8) (2-13/8=3/8, the toy's own exact law D_per=floor((3m+1)/8)
established in W6D-G RESULTS_D1.md); sqrt2-per12 uses (p,q)=(7,12)
(2-17/12=7/12, D_per=floor((7m+1)/12)).
"""
import csv
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import bfs_Dm, keystone_check
from underlock_words import credit_golden_per8, credit_sqrt2_per12

HERE = Path(__file__).parent
UNDERLOCK = HERE.parent

MAX_M_FOR_CHAIN = 9  # scalar dict BFS scope wall, see module docstring
# (empirically: m=9 chain extraction with parent pointers completes in
# well under a minute total across both families; m=10 alone exceeded
# a minute mid-run and the full m<=13 sweep blew the 280s budget on a
# first attempt -- capped here at the point that was ACTUALLY fast,
# rather than re-guessing; m=10..16 rows honestly reported as skipped.)


def load_ground_truth(paths):
    gt = {}
    for p in paths:
        with open(p, newline="") as f:
            for row in csv.DictReader(f):
                gt[int(row["m"])] = int(row["D"])
    return gt


GT_GOLDEN = load_ground_truth(
    [UNDERLOCK / "D_golden_per8_table.csv", UNDERLOCK / "D_golden_per8_m16.csv"])
GT_SQRT2 = load_ground_truth(
    [UNDERLOCK / "D_sqrt2_per12_table.csv", UNDERLOCK / "D_sqrt2_per12_heavy_table.csv"])


def prefix_bound(k, p, q, mirror=False):
    """floor((p*k+1)/q), or the mirror form floor((p*k-1)/q) for the
    real system (per the order: 'mirror form for the real system')."""
    if mirror:
        return (p * k - 1) // q
    return (p * k + 1) // q


def census_one_family(name, credit_fn, gt_dict, p, q, mirror=False, C_by_m=None):
    print(f"\n=== {name} (p={p}, q={q}, mirror={mirror}) ===")
    binding_k_mod_q = Counter()
    keystone_violations = []
    rows_used = []
    rows_skipped = []
    for m in sorted(gt_dict):
        if m > MAX_M_FOR_CHAIN:
            rows_skipped.append(m)
            print(f"  m={m}: SKIPPED -- exceeds scalar chain-extraction scope "
                  f"wall (m>{MAX_M_FOR_CHAIN}); no optimal chain regenerated, "
                  f"not counted in this experiment's tables.")
            continue
        D = gt_dict[m]
        C = C_by_m(m) if C_by_m else 12
        D_check, chain = bfs_Dm(credit_fn, m, C, anchor_steps=53, want_chain=True)
        if D_check != D:
            print(f"  m={m}: WARNING D_check={D_check} != ground-truth D={D} "
                  f"at C={C} -- widening C and retrying")
            C2 = C + 4
            D_check, chain = bfs_Dm(credit_fn, m, C2, anchor_steps=53, want_chain=True)
            if D_check != D:
                print(f"  m={m}: STILL mismatched at C={C2} "
                      f"(D_check={D_check}); skipping this row, flagging honestly")
                rows_skipped.append(m)
                continue

        # keystone check on this chain (every k=1..m, per the order)
        kc = keystone_check(chain, m)
        all_pass = all(v[0] for v in kc.values())
        if not all_pass:
            for k, v in kc.items():
                if not v[0]:
                    keystone_violations.append((name, m, k, v[1], v[2]))

        # g(k): running sum of (a_j - c_j) over the LAST k steps
        # (backward from terminal), k=1..m
        n = len(chain)
        a_list = [a for (c, a) in chain]
        c_list = [c for (c, a) in chain]
        g_by_k = {}
        binding_ks = []
        for k in range(1, m + 1):
            suffix_a = a_list[n - k:]
            suffix_c = c_list[n - k:]
            g_k = sum(a - c for a, c in zip(suffix_a, suffix_c))
            bound_k = prefix_bound(k, p, q, mirror=mirror)
            g_by_k[k] = (g_k, bound_k, g_k == bound_k)
            if g_k == bound_k:
                binding_ks.append(k)
                binding_k_mod_q[k % q] += 1
        rows_used.append({
            "m": m, "D": D, "chain": chain, "g_by_k": g_by_k,
            "binding_ks": binding_ks, "keystone_all_pass": all_pass,
        })
        binding_str = ",".join(str(k) for k in binding_ks) if binding_ks else "(none)"
        print(f"  m={m:>3} D={D:>3}: keystone_all_pass={all_pass}  "
              f"binding k's={binding_str}")

    return rows_used, rows_skipped, binding_k_mod_q, keystone_violations


def main():
    all_keystone_violations = []
    all_rows_used = []

    rows, skipped, bmod, viol = census_one_family(
        "golden-per8", credit_golden_per8, GT_GOLDEN, p=3, q=8,
        C_by_m=lambda m: 12 if m < 12 else 14)
    all_keystone_violations += viol
    all_rows_used += [("golden", r) for r in rows]
    golden_skipped = skipped

    rows, skipped, bmod, viol = census_one_family(
        "sqrt2-per12", credit_sqrt2_per12, GT_SQRT2, p=7, q=12,
        C_by_m=lambda m: 12 if m <= 11 else 14)
    all_keystone_violations += viol
    all_rows_used += [("sqrt2", r) for r in rows]
    sqrt2_skipped = skipped

    print("\n\n=== KEYSTONE INTEGRITY CHECK (every chain used in this experiment) ===")
    if all_keystone_violations:
        print(f"VIOLATIONS FOUND: {len(all_keystone_violations)} -- "
              "per the order, this means the ENGINE IS WRONG, not the math. "
              "STOP and do not trust downstream results.")
        for v in all_keystone_violations:
            print(f"  {v}")
    else:
        n_chains = len(all_rows_used)
        print(f"NO VIOLATIONS: keystone identity 2^Sigma_a == S_k (mod 3^k) "
              f"holds for all k=1..m on all {n_chains} chains used "
              f"(golden {len([r for f,r in all_rows_used if f=='golden'])} rows, "
              f"sqrt2 {len([r for f,r in all_rows_used if f=='sqrt2'])} rows). "
              f"Engine integrity CONFIRMED for this experiment.")

    print("\n=== BINDING-PHASE HISTOGRAM (k mod q, per family -- golden uses "
          "q=8, sqrt2 uses q=12, reported separately since pooling across "
          "different q is not meaningful) ===")

    print("\n-- golden-per8 (q=8) --")
    golden_bmod = Counter()
    for fam, r in all_rows_used:
        if fam == "golden":
            for k in r["binding_ks"]:
                golden_bmod[k % 8] += 1
    for phase in range(8):
        print(f"  k mod 8 = {phase}: {golden_bmod.get(phase, 0)} binding prefixes")
    total_golden_binding = sum(golden_bmod.values())
    print(f"  total binding prefixes (golden): {total_golden_binding}")

    print("\n-- sqrt2-per12 (q=12) --")
    sqrt2_bmod = Counter()
    for fam, r in all_rows_used:
        if fam == "sqrt2":
            for k in r["binding_ks"]:
                sqrt2_bmod[k % 12] += 1
    for phase in range(12):
        print(f"  k mod 12 = {phase}: {sqrt2_bmod.get(phase, 0)} binding prefixes")
    total_sqrt2_binding = sum(sqrt2_bmod.values())
    print(f"  total binding prefixes (sqrt2): {total_sqrt2_binding}")

    print("\n=== GATE VERDICT ===")
    def concentration_report(bmod, q, label):
        if not bmod:
            print(f"  {label}: NO binding prefixes found at all -- cannot "
                  f"assess clustering.")
            return None
        total = sum(bmod.values())
        max_phase, max_count = max(bmod.items(), key=lambda kv: kv[1])
        frac = max_count / total
        print(f"  {label}: {len(bmod)} distinct phases hit out of {q}; "
              f"peak phase={max_phase} with {max_count}/{total} "
              f"({frac:.1%}) of binding prefixes.")
        top2 = sorted(bmod.values(), reverse=True)[:2]
        top2_frac = sum(top2) / total
        print(f"    top-2 phases carry {top2_frac:.1%} of binding prefixes.")
        return frac

    frac_g = concentration_report(golden_bmod, 8, "golden-per8")
    frac_s = concentration_report(sqrt2_bmod, 12, "sqrt2-per12")

    print()
    print("Registered prediction (Fable, frozen): binding prefixes cluster "
          "at a fixed phase mod q (75% confidence) -- the Raney/cycle-lemma "
          "worst peak. Uniform scatter would weaken the P1b route.")
    for label, frac, q in [("golden-per8", frac_g, 8), ("sqrt2-per12", frac_s, 12)]:
        if frac is None:
            print(f"  {label}: inconclusive (no data).")
        elif frac >= (1.0 / q) * 2:  # peak carries at least ~2x uniform share
            print(f"  {label}: CLUSTERED (peak phase carries {frac:.1%}, "
                  f"uniform would be {1/q:.1%}) -- prediction HIT.")
        else:
            print(f"  {label}: NOT clustered beyond uniform-ish scatter "
                  f"(peak {frac:.1%} vs uniform {1/q:.1%}) -- prediction MISSED.")

    print(f"\nRows skipped (scope wall, m>{MAX_M_FOR_CHAIN}): "
          f"golden={golden_skipped}, sqrt2={sqrt2_skipped}")

    with open(HERE / "e3_binding_prefixes.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["family", "m", "D", "k", "g_k", "bound_k", "is_binding"])
        for fam, r in all_rows_used:
            for k, (g_k, bound_k, is_binding) in r["g_by_k"].items():
                w.writerow([fam, r["m"], r["D"], k, g_k, bound_k, is_binding])
    with open(HERE / "e3_binding_histogram.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["family", "phase_mod_q", "count"])
        for phase in range(8):
            w.writerow(["golden", phase, golden_bmod.get(phase, 0)])
        for phase in range(12):
            w.writerow(["sqrt2", phase, sqrt2_bmod.get(phase, 0)])
    print("\nWrote e3_binding_prefixes.csv, e3_binding_histogram.csv")


if __name__ == "__main__":
    main()
