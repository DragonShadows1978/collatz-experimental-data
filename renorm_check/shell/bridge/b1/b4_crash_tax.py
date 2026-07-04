#!/usr/bin/env python3
"""
LOCK4-B1.4 -- Crash tax (exploratory, gated lightly).

Takes B1.2's argmax witnesses (the actual exponent sequences achieving
the best residue-legal climb found for each scope/launch), then
CONTINUES each witness chain for 20-50 more letters using the S0 greedy
strategy (smallest legal exponent of the forced parity every step,
matching w6e/e1_walkers.py's S0 convention exactly -- dies only on a
genuine class-0 dead end), and measures the forced net descent (change
in running climb) over that continuation. This directly operationalizes
"the forced net descent over the steps immediately following a maximal
climb segment" (LOCK4_BRIDGE_NOTES sec 1's CRASH TAX definition).

Witness re-extraction: re-runs the SAME gated DFS from b2 with
witness-tracking added (records the full a-sequence achieving the
best value), for the SPECIFIC (k, launch) cells identified as best by
b2's completed run (read from b2_max_climb_by_launch.csv) -- avoids
re-running all 18 launches x 4 scopes; only the argmax cells actually
needed for this experiment.

Every witness (climb segment + crash continuation) is exact-replayed
independently (big-integer forward Collatz-residue check from the
launch class, not merely trusted from the DFS's own bookkeeping).
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
W6E = HERE.parent.parent / "underlock" / "w6e"
sys.path.insert(0, str(W6E))
from engine import forced_parity_for_backward_step, backward_predecessor_exact  # noqa: E402


def floor_k_alpha(k: int) -> int:
    if k == 0:
        return 0
    return (3 ** k).bit_length() - 1


def credit_true(k: int) -> int:
    return floor_k_alpha(k + 1) - floor_k_alpha(k)


def backward_letters_window(k_end: int, m: int):
    return [credit_true(k_end - 1 - j) for j in range(m)]


def suffix_ub_table(letters):
    """Admissible bound (c-1 per step) -- see b2's docstring for why
    this (not B1.1's blanket phase-relaxed cap) is the sound choice
    for the residue-legal game."""
    m = len(letters)
    tbl = [0] * (m + 1)
    for j in range(m - 1, -1, -1):
        c = letters[j]
        tbl[j] = tbl[j + 1] + (c - 1)
    return tbl


def dfs_max_climb_witness(letters, rho0: int, a_cap: int, time_budget: float,
                           node_check_interval: int = 500_000):
    """Same gated DFS as b2, but records the a-sequence and terminal
    residue for the best value found (a valid witness even under a
    time-limited/walled run: whatever complete path is found is a
    real, replayable residue-legal chain)."""
    m = len(letters)
    ub_tbl = suffix_ub_table(letters)
    best = [-10 ** 9]
    best_seq = [None]
    best_rho = [None]
    t0 = time.time()
    nodes = [0]

    def rec(j, rho, running, seq):
        nodes[0] += 1
        if nodes[0] % node_check_interval == 0 and time.time() - t0 > time_budget:
            raise TimeoutError()
        if running + ub_tbl[j] <= best[0]:
            return
        if j == m:
            if running > best[0]:
                best[0] = running
                best_seq[0] = list(seq)
                best_rho[0] = rho
            return
        c = letters[j]
        p = forced_parity_for_backward_step(rho)
        if p is None:
            return
        a_min = 2 if p == 0 else 1
        for a in range(a_min, a_min + a_cap + 1, 2):
            rho2 = backward_predecessor_exact(rho, a)
            seq.append(a)
            rec(j + 1, rho2, running + (c - a), seq)
            seq.pop()

    try:
        rec(0, rho0, 0, [])
        return best[0], best_seq[0], best_rho[0], nodes[0], False
    except TimeoutError:
        return best[0], best_seq[0], best_rho[0], nodes[0], True


def exact_replay(rho0: int, letters, a_seq) -> tuple[bool, int, int]:
    """Independent exact-integer replay of the witness: re-walk from
    rho0 applying a_seq, verify parity legality at every step, and
    return (all_legal, final_residue, computed_climb)."""
    rho = rho0
    climb = 0
    for c, a in zip(letters, a_seq):
        p = forced_parity_for_backward_step(rho)
        want_parity = 0 if a % 2 == 0 else 1
        if p is None or p != want_parity:
            return False, rho, climb
        rho = backward_predecessor_exact(rho, a)
        climb += (c - a)
    return True, rho, climb


def continue_s0(rho0: int, letters_continuation):
    """S0 greedy continuation: smallest legal exponent of the forced
    parity every step (matches w6e/e1_walkers.py's S0 exactly). Returns
    the running climb trajectory and whether/where it died."""
    rho = rho0
    climb = 0
    trajectory = []
    for j, c in enumerate(letters_continuation):
        p = forced_parity_for_backward_step(rho)
        if p is None:
            return trajectory, j, "DIED(class-0)"
        a = 2 if p == 0 else 1
        rho = backward_predecessor_exact(rho, a)
        climb += (c - a)
        trajectory.append(climb)
    return trajectory, None, "SURVIVED"


def main():
    print("=== LOCK4-B1.4: crash tax ===\n")
    b2_csv = HERE / "b2_max_climb_by_launch.csv"
    if not b2_csv.exists():
        raise SystemExit(f"B1.4 requires {b2_csv.name} from a completed B1.2 run")

    with open(b2_csv, newline="") as f:
        b2_rows = list(csv.DictReader(f))

    # find best launch per k (max_climb_or_lower_bound, over rows with a real value)
    best_by_k = {}
    for row in b2_rows:
        if not row["max_climb_or_lower_bound"]:
            continue
        k = int(row["k"])
        val = int(row["max_climb_or_lower_bound"])
        if k not in best_by_k or val > best_by_k[k][1]:
            best_by_k[k] = (int(row["launch_class_mod27"]), val)

    print("Best (argmax) launch per scope, from completed B1.2 run:")
    for k in sorted(best_by_k):
        rho0, val = best_by_k[k]
        print(f"  k={k}: launch_class={rho0} value={val}")
    print()

    # NOTE: backward_letters_window is END-anchored at k_end; to get a CONTINUATION past the
    # original 306-letter window (which was end-anchored at 306), we need letters BEYOND that
    # anchor -- i.e., letters at absolute steps 306..355 (the "next" 50 letters chronologically
    # forward from where the backward-306 window's k_end sits). Since backward-consumption
    # order index 0 = closest to anchor (index 306-1=305 = absolute step 305), continuing
    # requires letters at absolute steps 306, 307, ... (forward continuation of the SAME
    # absolute-step credit sequence used throughout this window).
    continuation_letters = [credit_true(306 + i) for i in range(50)]

    rows = []
    A_CAP = 4
    for k in sorted(best_by_k):
        rho0_launch, reported_val = best_by_k[k]
        sub = backward_letters_window(306, k)
        print(f"--- k={k}, launch_class={rho0_launch} (reported value {reported_val}) ---")
        t0 = time.time()
        val, seq, terminal_rho, nodes, timedout = dfs_max_climb_witness(
            sub, rho0_launch, A_CAP, time_budget=60)
        if seq is None:
            print(f"  no witness found within budget (val={val}) -- skipping crash-tax measurement")
            continue
        ok, replay_rho, replay_climb = exact_replay(rho0_launch, sub, seq)
        print(f"  re-extracted witness: value={val} (vs reported {reported_val}), "
              f"nodes={nodes}, timedout={timedout}")
        print(f"  exact replay: legal={ok}, replay_climb={replay_climb} "
              f"{'MATCH' if replay_climb == val else '*** MISMATCH ***'}, "
              f"terminal_rho consistent={replay_rho == terminal_rho}")

        for cont_len in (20, 50):
            traj, died_at, status = continue_s0(terminal_rho, continuation_letters[:cont_len])
            final_climb_delta = traj[-1] if traj else 0
            crash_tax = -final_climb_delta  # positive tax = net descent
            print(f"  continuation {cont_len} letters: status={status} "
                  f"died_at={died_at} net_climb_change={final_climb_delta} "
                  f"crash_tax={crash_tax} "
                  f"({'crash confirmed (tax>0)' if crash_tax > 0 else 'NO CRASH (tax<=0)'})")
            rows.append({
                "k": k, "launch_class": rho0_launch, "witness_value": val,
                "replay_ok": ok, "continuation_len": cont_len,
                "continuation_status": status, "died_at": died_at,
                "net_climb_change_over_continuation": final_climb_delta,
                "crash_tax": crash_tax,
            })
        print()

    out = HERE / "b4_crash_tax_table.csv"
    with open(out, "w", newline="") as f:
        fieldnames = ["k", "launch_class", "witness_value", "replay_ok", "continuation_len",
                      "continuation_status", "died_at", "net_climb_change_over_continuation",
                      "crash_tax"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote {out.name} ({len(rows)} rows)")

    if rows:
        all_positive = all(r["crash_tax"] > 0 for r in rows)
        print(f"\n=== Frozen prediction (crash tax > 0 for every maximal-climb witness, 70%): "
              f"{'HIT' if all_positive else 'MISS'} "
              f"(taxes: {[r['crash_tax'] for r in rows]}) ===")


if __name__ == "__main__":
    main()
