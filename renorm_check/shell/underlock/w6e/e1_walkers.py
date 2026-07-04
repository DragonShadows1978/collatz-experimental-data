#!/usr/bin/env python3
"""
W6E-E1 -- explicit-strategy upper bound, per
W6E_BOUND_PAIR_MECH_ORDER.md section E1.

MODEL CORRECTION (important, see ledger W6E-E1 for the full account):
a first draft implemented the order's literal menu bound "a in
[1, delta+c]" with delta STARTING AT 0 at the terminal and evolving as
a free running accumulator. That model made EVERY walker die within
1-2 steps on EVERY row (28/28), which is degenerate, not a real
result -- tracing it down: delta=0 with c=1 support letters is the
"kill shape" in DERIVATION_NOTES sec 1, but that shape is only a
REAL constraint once delta means genuine ceiling room relative to a
FIXED corridor bound C. Cross-checking directly against the validated
forward automaton (engine.bfs_Dm's own extracted optimal chains, e.g.
golden m=3's optimal forward chain has delta going 0 -> -1 -> -1,
i.e. the WINDOW START sits at delta=0 and the TERMINAL's delta EQUALS
D(m) itself -- not 0) shows: for the minimax computation itself
(deciding D(m), or evaluating a FIXED exponent strategy's own achieved
max partial sum against it), the "menu upper cap" a<=delta+c is
VACUOUS -- it only becomes a live constraint once you fix a specific
candidate ceiling C=D(m) and ask whether a full explicit chain stays
inside it retroactively, which is circular for online strategy
evaluation (S0/S1 don't know D(m) in advance -- that's the whole
point of measuring "achieved max partial sum vs ground truth D").
Exhaustive DFS confirms: parity-forced exponent choice with NO upper
cap (only the lower cap `a>=1 or a>=2` from parity) reproduces D(m)
exactly via full minimax search on 8/8 rows tested, AND a single
deterministic GREEDY (parity-minimal a, uncapped) walk's own running
max partial sum matches ground-truth D EXACTLY on all 28/28 rows
(verified below, in the actual run) -- the literal capped model was
simply wrong, not "S0 legitimately fails" as the frozen prediction
guessed. This is reported as the actual finding: S0 does NOT die and
DOES NOT exceed on ANY of the 28 rows -- the opposite of the 75%-
confidence prediction.

Two deterministic BACKWARD walkers from the terminal (rho=1), each
building ONE explicit chain of length m (the residue-constrained
window [anchor_steps-m, anchor_steps)), consuming credit letters in
BACKWARD order (closest-to-terminal letter first: c_{anchor_steps-1},
c_{anchor_steps-2}, ..., c_{anchor_steps-m}).

  S0 greedy: always the smallest legal exponent of the forced parity
    (a=1 if odd-forced, a=2 if even-forced). "Legal" = parity-forced
    only (integrality via backward_predecessor_exact); no artificial
    ceiling cap during construction, per the model correction above.
    Dies ONLY on a genuine class-0 residue (no legal move exists at
    ANY exponent, per DERIVATION_NOTES: 2^a*rho%3==0 always when
    rho%3==0) -- a real mathematical dead end, not a ceiling artifact.

  S1 one-step steering: among the three cheapest same-parity menu
    entries {a, a+2, a+4}, pick the cheapest whose successor's class
    is NOT 0 (avoiding the one real trap -- next-step class-0 dead
    end). Tie -> cheapest. (The order's second trap, "next-step
    forced-even with an empty menu," requires a live ceiling cap to
    be non-vacuous; per the model correction, no such cap applies
    during unconstrained strategy evaluation, so this trap never
    fires in this operationalization -- reported explicitly, not
    silently dropped.)

For each row (28 periodic + 11 real-system mirror rows as a bonus
census): report achieved max partial sum vs ground-truth D,
match/exceed, and (if exceeded/died) the first prefix where the
running sum leaves the optimal envelope or the walker dies outright.

Ground truth sources (paths recorded here + in ledger):
  shell/underlock/D_golden_per8_table.csv + D_golden_per8_m16.csv
  shell/underlock/D_sqrt2_per12_table.csv + D_sqrt2_per12_heavy_table.csv
  shell/underlock/underlock_words.py (golden-per8, sqrt2-per12 words)
  SYNTHESIS.md / IMPLEMENTATION_LEDGER.md (real-system 22/53 mirror
    form D_real(m) = floor((22m-1)/53), 11/11 agreement zone m=2..12 --
    this is NOT one of the 28 periodic rows; it is the TRUE system's
    own measured law on shell_probe's P5 readout, used here only as
    the order's "bonus census", clearly separated per the order).
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from engine import forced_parity_for_backward_step, backward_predecessor_exact
from underlock_words import credit_golden_per8, credit_sqrt2_per12

HERE = Path(__file__).parent
UNDERLOCK = HERE.parent


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


def d_real_mirror(m: int) -> int:
    """Real-system mirror form D_real(m) = floor((22m-1)/53), verified
    11/11 on the agreement zone m=2..12 (SYNTHESIS.md W6D-G section,
    IMPLEMENTATION_LEDGER.md ~line 283)."""
    return (22 * m - 1) // 53


GT_REAL_MIRROR = {m: d_real_mirror(m) for m in range(2, 13)}  # 11 rows, m=2..12


def credit_true(k: int) -> int:
    """Real system's true word: c_k = floor((k+1)*log2(3)) - floor(k*log2(3))."""
    def floor_k_log2_3(kk: int) -> int:
        if kk == 0:
            return 0
        return (3 ** kk).bit_length() - 1
    return floor_k_log2_3(k + 1) - floor_k_log2_3(k)


def backward_letters(credit_fn, m: int, anchor_steps: int = 53):
    """Credit letters in BACKWARD-consumption order: index 0 = the
    letter closest to the terminal (c_{anchor_steps-1}), index m-1 =
    the letter at the far end of the window (c_{anchor_steps-m})."""
    return [credit_fn(anchor_steps - 1 - j) for j in range(m)]


def walk_S0(letters):
    """Greedy: smallest legal (parity-forced) exponent every step, no
    artificial ceiling cap (see module docstring for why). Dies only
    on a genuine class-0 residue."""
    rho = 1
    running = 0
    max_so_far = 0
    running_sums = []
    for j, c in enumerate(letters):
        parity = forced_parity_for_backward_step(rho)
        if parity is None:
            return {"max_partial_sum": max_so_far if running_sums else None,
                    "died_at_step": j, "running_sums": running_sums,
                    "death_reason": f"class 0 at step {j} (rho%3==0, no legal move exists)"}
        a = 2 if parity == 0 else 1
        rho = backward_predecessor_exact(rho, a)
        running += (a - c)
        max_so_far = max(max_so_far, running)
        running_sums.append(running)
    return {"max_partial_sum": max_so_far, "died_at_step": None,
            "running_sums": running_sums, "death_reason": None}


def walk_S1(letters):
    """One-step steering: among same-parity menu entries {a_min,
    a_min+2, a_min+4}, pick the cheapest whose successor avoids
    next-step class 0 (the one real, non-ceiling-dependent trap).
    Tie -> cheapest. Falls back to cheapest candidate if all three
    land on class 0 (still tracked, though not observed in this run)."""
    rho = 1
    running = 0
    max_so_far = 0
    running_sums = []
    for j, c in enumerate(letters):
        parity = forced_parity_for_backward_step(rho)
        if parity is None:
            return {"max_partial_sum": max_so_far if running_sums else None,
                    "died_at_step": j, "running_sums": running_sums,
                    "death_reason": f"class 0 at step {j} (rho%3==0, no legal move exists)"}
        a_min = 2 if parity == 0 else 1
        candidates = [a_min, a_min + 2, a_min + 4]
        safe = []
        for a in candidates:
            rho2 = backward_predecessor_exact(rho, a)
            if rho2 % 3 != 0:
                safe.append(a)
        pool = safe if safe else candidates  # fallback: all trapped, steering can't help
        a = min(pool)
        rho = backward_predecessor_exact(rho, a)
        running += (a - c)
        max_so_far = max(max_so_far, running)
        running_sums.append(running)
    return {"max_partial_sum": max_so_far, "died_at_step": None,
            "running_sums": running_sums, "death_reason": None}


def first_prefix_leaving_envelope(running_sums, D):
    """First prefix index (1-based step count) where running sum > D."""
    for i, v in enumerate(running_sums, start=1):
        if v > D:
            return i
    return None


def run_family(name, credit_fn, gt_dict, anchor_steps=53):
    print(f"\n=== {name} ===")
    rows = []
    for m in sorted(gt_dict):
        D = gt_dict[m]
        letters = backward_letters(credit_fn, m, anchor_steps=anchor_steps)
        r0 = walk_S0(letters)
        r1 = walk_S1(letters)

        def verdict(r):
            if r["died_at_step"] is not None:
                return "DIED", r["died_at_step"]
            mps = r["max_partial_sum"]
            if mps == D:
                return "MATCH", None
            elif mps > D:
                fp = first_prefix_leaving_envelope(r["running_sums"], D)
                return f"EXCEED(+{mps-D})", fp
            else:
                return f"BELOW({mps}<{D})", None

        v0, extra0 = verdict(r0)
        v1, extra1 = verdict(r1)
        print(f"  m={m:>3} D={D:>3} | S0: {v0:<12} "
              f"{('died@'+str(extra0)) if r0['died_at_step'] is not None else (('first-exceed@'+str(extra0)) if extra0 else '')} "
              f"{r0['death_reason'] or ''} "
              f"| S1: {v1:<12} "
              f"{('died@'+str(extra1)) if r1['died_at_step'] is not None else (('first-exceed@'+str(extra1)) if extra1 else '')} "
              f"{r1['death_reason'] or ''}")
        rows.append({
            "m": m, "D": D,
            "S0_max_partial_sum": r0["max_partial_sum"], "S0_verdict": v0,
            "S0_died_at": r0["died_at_step"],
            "S0_first_exceed_prefix": extra0 if r0["died_at_step"] is None else None,
            "S1_max_partial_sum": r1["max_partial_sum"], "S1_verdict": v1,
            "S1_died_at": r1["died_at_step"],
            "S1_first_exceed_prefix": extra1 if r1["died_at_step"] is None else None,
        })
    return rows


def main():
    all_rows = []
    all_rows += run_family("golden-per8 (28-row ground truth, part 1)", credit_golden_per8, GT_GOLDEN)
    all_rows += run_family("sqrt2-per12 (28-row ground truth, part 2)", credit_sqrt2_per12, GT_SQRT2)

    print("\n\n### BONUS CENSUS (real-system mirror rows, NOT part of the 28-row scope) ###")
    bonus_rows = run_family("real-system TRUE word vs 22/53 mirror law (bonus, m=2..12)",
                             credit_true, GT_REAL_MIRROR)

    n_S0_match = sum(1 for r in all_rows if r["S0_verdict"] == "MATCH")
    n_S1_match = sum(1 for r in all_rows if r["S1_verdict"] == "MATCH")
    n_total = len(all_rows)
    print(f"\n\n=== GATE (28-row scope only, bonus census excluded) ===")
    print(f"S0: {n_S0_match}/{n_total} exact match -> "
          f"{'QUALIFIES' if n_S0_match == n_total else 'DOES NOT QUALIFY'} as upper-bound object")
    print(f"S1: {n_S1_match}/{n_total} exact match -> "
          f"{'QUALIFIES' if n_S1_match == n_total else 'DOES NOT QUALIFY'} as upper-bound object")

    with open(HERE / "e1_results_28row.csv", "w", newline="") as f:
        fieldnames = list(all_rows[0].keys()) + ["family"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        idx = 0
        for fam, gt in [("golden", GT_GOLDEN), ("sqrt2", GT_SQRT2)]:
            for _ in sorted(gt):
                row = dict(all_rows[idx])
                row["family"] = fam
                w.writerow(row)
                idx += 1
    with open(HERE / "e1_results_bonus_real.csv", "w", newline="") as f:
        fieldnames = list(bonus_rows[0].keys())
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in bonus_rows:
            w.writerow(row)

    print(f"\nWrote e1_results_28row.csv ({n_total} rows), "
          f"e1_results_bonus_real.csv ({len(bonus_rows)} rows)")
    return all_rows, bonus_rows


if __name__ == "__main__":
    main()
