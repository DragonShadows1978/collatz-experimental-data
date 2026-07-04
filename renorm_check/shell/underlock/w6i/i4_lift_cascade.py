#!/usr/bin/env python3
"""
W6I-I4 -- Lift-cascade effective branching (exploratory, UNGATED).

Per W6I_PROOF_SHAPE_ORDER.md I4: for 20-step backward chains from
rho == 1 (mod 3^8 working precision), trace each lift choice's
influence: at which later step does a lift made at step j first
change the forced parity of the chain? Build the histogram of
influence delays and the effective branching factor per step (how
many lift choices are ever decisive vs pre-cancelled).

--- Setup, reusing w6e/engine.py's validated primitives (copied here
per the non-overlap rule) ---
A backward chain from the terminal rho_0 = 1 (mod 3^8) proceeds for
steps j=0..19: at step j, current residue rho_j has a FORCED parity
(class 1 mod 3 -> a even, class 2 -> a odd, class 0 -> dead, per
engine.forced_parity_for_backward_step). Given the forced parity, the
LIFT CHOICE is which same-parity menu entry to use: a in {a_min,
a_min+2, a_min+4, ...} (a_min=2 if even-forced, 1 if odd-forced) --
per DERIVATION_NOTES sec 1, "the three same-parity menu entries {a,
a+2, a+4} land the predecessor residue in the three distinct classes
mod 3 (mod-9 steering)" -- i.e. exactly 3 DISTINCT lift choices are
ever locally decisive for the IMMEDIATE next step's forced parity
(steering among 3 classes); larger lifts (a_min+6, a_min+8, ...)
cycle back through the same 3 classes mod 9 (period 3 in the lift
index, since stepping by 2 in `a` cycles the predecessor's mod-9
residue through a fixed 3-cycle -- verified empirically below, not
assumed).

--- Definition of "when a lift's influence is FELT" ---
Fix a baseline chain: greedy S0 (a_min every step, matching w6e/
e1_walkers.py's own S0 walker exactly). For each step j = 0..19 and
an ALTERNATIVE lift choice at step j (a_min+2 instead of a_min, i.e.
the next steering option -- the minimal, most local perturbation),
build a PERTURBED chain: identical to baseline for steps 0..j-1, use
the alternative lift at step j, then continue the perturbed chain
with S0's OWN greedy rule (a_min of whatever parity is now forced)
for steps j+1..19. Compare the perturbed chain's forced-parity
sequence (parity_j+1, parity_j+2, ...) against the baseline's, step by
step (both continuing under the SAME greedy continuation rule from
their respective post-step-j residues) -- the "influence delay" is
the smallest k>=1 such that parity at step j+k differs between the
two chains (i.e., first step where the lift's effect resurfaces as a
DIFFERENT forced constraint), or "never" if no divergence occurs
within the 20-step window (a genuinely pre-cancelled / non-decisive
lift, reported as such, not as an unbounded delay).

Cross-checked (house rule, small-scale hand-check before trusting):
the "3 lifts cycle mod 9 with period 3" claim, and the forced-parity/
backward-predecessor mechanics themselves (both borrowed unmodified
from w6e/engine.py, already validated there against ground truth --
re-verified here on 5 explicit steps for this specific chain before
trusting the full histogram).
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent / "w6e"))

from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402

HERE = Path(__file__).parent

WORKING_PRECISION_K = 8  # rho == 1 (mod 3^8), per the order
N_STEPS = 20
MODULUS = 3 ** WORKING_PRECISION_K


def greedy_step(rho: int):
    """S0 greedy backward step (matches w6e/e1_walkers.py's walk_S0
    exactly): a_min of the forced parity (2 if even-forced, 1 if
    odd-forced); dies (returns None) on class 0."""
    parity = forced_parity_for_backward_step(rho % MODULUS if rho % MODULUS != 0 else rho)
    if parity is None:
        return None, None
    a = 2 if parity == 0 else 1
    rho2 = backward_predecessor_exact(rho, a)
    return rho2, a


def alt_step(rho: int, lift_offset: int):
    """Alternative lift at the CURRENT step: a_min + lift_offset (must
    stay the same parity, so lift_offset must be even; lift_offset=2
    is the minimal/most local perturbation, matching DERIVATION_NOTES'
    own '3 same-parity menu entries' framing with offsets {0,2,4})."""
    parity = forced_parity_for_backward_step(rho % MODULUS if rho % MODULUS != 0 else rho)
    if parity is None:
        return None, None
    a_min = 2 if parity == 0 else 1
    a = a_min + lift_offset
    rho2 = backward_predecessor_exact(rho, a)
    return rho2, a


def build_greedy_chain(rho0: int, n_steps: int):
    """Baseline S0 greedy chain from rho0, n_steps backward steps.
    Returns (rho_sequence, a_sequence, parity_sequence, died_at)."""
    rhos = [rho0]
    a_seq = []
    parities = []
    died_at = None
    rho = rho0
    for j in range(n_steps):
        parity = forced_parity_for_backward_step(rho % MODULUS if rho % MODULUS != 0 else rho)
        parities.append(parity)
        if parity is None:
            died_at = j
            break
        rho, a = greedy_step(rho)
        a_seq.append(a)
        rhos.append(rho)
    return rhos, a_seq, parities, died_at


def hand_check_mod9_cycle(rho0: int, n_checks: int = 5):
    """Validate the 'lift offsets cycle mod 9 with period 3' claim:
    for a handful of explicit residues, confirm that the predecessor's
    class mod 3 under a_min, a_min+2, a_min+4 are the 3 DISTINCT
    classes {0,1,2} (mod-9 steering), and that a_min+6 repeats
    a_min's own successor class (period-3 cycle in the lift index)."""
    receipts = []
    rho = rho0
    checked = 0
    tries = 0
    while checked < n_checks and tries < 500:
        tries += 1
        parity = forced_parity_for_backward_step(rho % MODULUS if rho % MODULUS != 0 else rho)
        if parity is None:
            rho = 4 * rho + 1
            continue
        a_min = 2 if parity == 0 else 1
        classes = []
        for offset in (0, 2, 4, 6):
            a = a_min + offset
            pred = backward_predecessor_exact(rho, a)
            classes.append(pred % 3)
        distinct_first3 = len(set(classes[:3])) == 3
        period3 = (classes[3] == classes[0])
        receipts.append((rho, a_min, classes, distinct_first3, period3))
        checked += 1
        rho, _ = greedy_step(rho)
        if rho is None:
            break
    return receipts


def trace_influence_delay(rho0: int, n_steps: int, lift_offset: int = 2):
    """For each step j=0..n_steps-1 where the baseline chain is alive
    and has a legal alternative lift (same parity, offset=lift_offset,
    landing on a non-dead class), build the perturbed chain (identical
    up to j-1, alternative lift at j, greedy S0 continuation after)
    and find the first k>=1 with differing forced parity at step j+k
    vs the baseline. Returns list of (j, delay_or_None, note)."""
    base_rhos, base_a, base_parities, base_died = build_greedy_chain(rho0, n_steps)
    results = []
    for j in range(len(base_a)):
        rho_before_j = base_rhos[j]
        rho_after_alt, a_alt = alt_step(rho_before_j, lift_offset)
        if rho_after_alt is None:
            results.append({"j": j, "delay": None, "note": "alt lift lands on class-0 immediately (dead)"})
            continue
        pert_parities = []
        rho = rho_after_alt
        pert_died = None
        for k in range(n_steps - j - 1):
            parity = forced_parity_for_backward_step(rho % MODULUS if rho % MODULUS != 0 else rho)
            pert_parities.append(parity)
            if parity is None:
                pert_died = k
                break
            rho, _ = greedy_step(rho)
        delay = None
        for k in range(len(pert_parities)):
            base_idx = j + 1 + k
            if base_idx >= len(base_parities):
                break
            if pert_parities[k] != base_parities[base_idx]:
                delay = k + 1
                break
        note = ""
        if pert_died is not None and delay is None:
            note = f"perturbed chain died at relative step {pert_died} (baseline survived that far)"
        results.append({"j": j, "delay": delay, "note": note})
    return results, base_died


def main():
    print("W6I-I4 -- lift-cascade effective branching (exploratory, ungated)", flush=True)
    print(f"start: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print(f"working precision k={WORKING_PRECISION_K} (modulus 3^{WORKING_PRECISION_K}={MODULUS}), "
          f"n_steps={N_STEPS}, rho0=1", flush=True)

    print("\n--- hand-check: lift offsets {0,2,4} give 3 distinct mod-3 successor "
          "classes (mod-9 steering), offset 6 repeats offset 0's class (period-3 cycle) ---", flush=True)
    checks = hand_check_mod9_cycle(1, n_checks=5)
    all_ok = True
    for (rho, a_min, classes, distinct_first3, period3) in checks:
        ok = distinct_first3 and period3
        print(f"  rho={rho} a_min={a_min} successor-classes(offsets 0,2,4,6)={classes} "
              f"distinct_first3={distinct_first3} period3_repeat={period3} {'PASS' if ok else 'FAIL'}", flush=True)
        all_ok = all_ok and ok
    print(f"hand-check ALL PASS: {all_ok}", flush=True)
    if not all_ok:
        print("STOP: hand-check failed, machinery not trustworthy.", flush=True)
        sys.exit(2)

    print(f"\n--- baseline S0 greedy chain from rho0=1, {N_STEPS} steps ---", flush=True)
    base_rhos, base_a, base_parities, base_died = build_greedy_chain(1, N_STEPS)
    print(f"  a-sequence: {base_a}", flush=True)
    print(f"  parity-sequence (0=even-forced,1=odd-forced,None=dead): {base_parities}", flush=True)
    print(f"  died_at: {base_died}", flush=True)

    print(f"\n--- tracing influence delay for each step j's alternative lift "
          f"(offset=+2, the minimal steering perturbation) ---", flush=True)
    results, _ = trace_influence_delay(1, N_STEPS, lift_offset=2)
    for r in results:
        print(f"  j={r['j']:>2}: delay={r['delay']} {r['note']}", flush=True)

    delays = [r["delay"] for r in results if r["delay"] is not None]
    n_never = sum(1 for r in results if r["delay"] is None and not r["note"])
    n_immediately_dead = sum(1 for r in results if r["delay"] is None and "class-0" in r["note"])
    n_pert_died_no_diverge = sum(1 for r in results if r["delay"] is None and "perturbed chain died" in r["note"])

    print(f"\n--- histogram of influence delays (steps after the lift where forced "
          f"parity first differs) ---", flush=True)
    hist = Counter(delays)
    for delay in sorted(hist):
        print(f"  delay={delay}: {hist[delay]} occurrence(s)", flush=True)
    print(f"  never diverges within window (pre-cancelled / non-decisive): {n_never}", flush=True)
    print(f"  alternative lift immediately illegal (class-0): {n_immediately_dead}", flush=True)
    print(f"  perturbed chain died before any divergence observed: {n_pert_died_no_diverge}", flush=True)

    n_decisive = len(delays)
    n_total = len(results)
    print(f"\neffective branching: {n_decisive}/{n_total} lift choices (one alternative "
          f"tested per step, offset+2) are EVER decisive (cause a later forced-parity "
          f"change) within the {N_STEPS}-step window; "
          f"{n_total - n_decisive}/{n_total} are pre-cancelled or untestable "
          f"(dead / chain-terminated before divergence).", flush=True)

    with open(HERE / "i4_influence_delays.csv", "w", newline="") as f:
        fieldnames = ["j", "delay", "note"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in results:
            w.writerow(r)
    with open(HERE / "i4_delay_histogram.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["delay", "count"])
        for delay in sorted(hist):
            w.writerow([delay, hist[delay]])
        w.writerow(["never_or_dead", n_never + n_immediately_dead + n_pert_died_no_diverge])
    print(f"\nWrote i4_influence_delays.csv ({len(results)} rows), i4_delay_histogram.csv", flush=True)

    print("\n=== I4 HONEST READING (ungated, exploratory) ===", flush=True)
    if delays:
        all_delay_one = all(d == 1 for d in delays)
        print(f"Where a lift IS decisive, the observed delays are {sorted(set(delays))} "
              f"(min={min(delays)}, max={max(delays)}, mean={sum(delays)/len(delays):.1f}).", flush=True)
        if all_delay_one:
            print("SCOPE CAVEAT (important, not papered over): delay=1 on EVERY decisive case here "
                  "is close to a TAUTOLOGY for this specific measurement, not evidence of short-range "
                  "influence in DERIVATION_NOTES sec 5a's sense. The baseline chain from rho=1 is the "
                  "trivial all-2s loop (rho stays at 1 every step -- the greedy walker never leaves the "
                  "ray), so perturbing step j's exponent by +2 changes rho to a GENERICALLY DIFFERENT "
                  "integer immediately; since forced parity depends only on rho mod 3, a generic "
                  "perturbation almost always changes rho mod 3 at the very next step too -- this "
                  "measures 'does changing the residue at all change the very next mod-3 class' (near-"
                  "tautologically yes), NOT sec 5a's actual claim, which is about a SPECIFIC HIGH TRIT "
                  "(the one written at backward step j, trit m-j-1) taking ~(m-j) further steps before "
                  "it becomes the LOW-order trit that governs forced parity. Testing that claim properly "
                  "would require a non-degenerate baseline (one that actually visits multiple residue "
                  "classes, not the fixed point) and tracking a SPECIFIC trit's influence through the "
                  "cascade, not just whether perturbed-vs-baseline forced parity first differs -- this "
                  "run's design does not do that, and the near-universal delay=1 here should NOT be read "
                  "as contradicting or confirming sec 5a's cascade claim. Reported honestly as a narrower, "
                  "less informative measurement than intended, not silently reframed as a stronger result.")
        print(f"{n_total - n_decisive}/{n_total} of the tested "
              f"single-offset perturbations never surface as a forced-parity change within the "
              f"{N_STEPS}-step window (the j=19 case: no room left in the window to observe any "
              f"later step at all, not a substantive finding either).", flush=True)
    else:
        print("No tested lift was ever decisive within the window at this scale -- all "
              "perturbations were either immediately illegal or pre-cancelled before any "
              "divergence could be observed. Honest reading: either the greedy-S0 continuation "
              "is unusually good at self-correcting, or the window (20 steps at k=8 working "
              "precision) is too short to see the cascade this program's derivation notes "
              "describe -- reported as an open question, not resolved either way.", flush=True)
    print(f"end: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)


if __name__ == "__main__":
    main()
