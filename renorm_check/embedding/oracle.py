"""
Big-side membership oracle: "is (d, r) live in A(C, m) after `steps` steps
of the heartbeat, starting from the fully populated initial state set?"

Dense forward enumeration is IMPOSSIBLE for the big side of this
investigation's (C, m) pairs -- e.g. C=23 (=1+22), m=59 (=6+53) already
needs 3^59 ~ 2.2e28 residues PER deficit level. No dense array can
represent this on any hardware.

Instead we use BACKWARD reachability: (d, r) is live at generation t
(starting from a FULLY populated generation 0) if and only if there
exists *some* chain of t valid forward transitions ending at (d, r) --
equivalently, if and only if there exists a t-step BACKWARD path from
(d, r) that stays in-corridor at every step (since every state at
generation 0 is live, by construction, so any valid backward chain
automatically bottoms out at a live ancestor).

Backward step: given (d', r') produced at some step with credit c_k by
exponent a from predecessor (d, r):
    d' = d + c_k - a   =>   d = d' - c_k + a
    r' = (3r+1) * (2^a)^-1 mod 3^m   =>   3r = r'*2^a - 1 (mod 3^m)
The map r -> 3r mod 3^m is NOT invertible (gcd(3, 3^m) = 3), so this
congruence has a solution for r iff (r'*2^a - 1) == 0 (mod 3), and when
it does, there are EXACTLY 3 solutions mod 3^m (kernel of size 3^(m-1)
acting on... concretely: solutions are base, base + 3^(m-1), base + 2*3^(m-1)
where base = ((r'*2^a - 1) // 3) mod 3^m, using the representative of
r'*2^a - 1 mod 3^m that is divisible by 3).

Correctness: cross-validated exhaustively against the dense forward
computation (automaton.run_heartbeat) for multiple small (C, m) -- see
validate_oracle() below and the cross-check run recorded in
validation_results.json. Zero mismatches found across all tested states.

Tractability: THIS IS THE CENTRAL HONEST LIMITATION of this investigation.
Memoized backward DFS with memo key (step_idx, d, r) does NOT blow up
predictably by (C, m) size alone -- empirically:
  - Narrow corridors (C <= ~5) resolve in milliseconds to low seconds
    regardless of m.
  - Corridor widths C >= ~6 frequently explode past 10^5 - 10^6 distinct
    memo entries for SOME target states (not all -- some resolve fast via
    early "target % 3 != 0" cutoffs, others don't).
  - The big-side corridors this conjecture requires are ALWAYS C+22 >= 23
    (since C ranges 1..15), which is deep in the explosive regime. Direct
    measurement: C=23, m=40, several random target states EXCEEDED a
    2,000,000-call budget without resolving, taking 7+ seconds each and
    climbing.
This means big-side membership queries in this investigation are answered
with a hard per-query call budget, and queries that exceed the budget are
recorded as "INCONCLUSIVE (compute-capped)", NOT as "not live". This
distinction is preserved throughout the JSON output -- an inconclusive
result must never be silently counted as a containment failure OR success.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from automaton import credit_sequence, allowed_exponents


class OracleResult:
    __slots__ = ("live", "inconclusive", "calls", "memo_size", "elapsed_sec")

    def __init__(self, live, inconclusive, calls, memo_size, elapsed_sec):
        self.live = live
        self.inconclusive = inconclusive
        self.calls = calls
        self.memo_size = memo_size
        self.elapsed_sec = elapsed_sec

    def to_dict(self):
        return {
            "live": self.live,
            "inconclusive": self.inconclusive,
            "calls": self.calls,
            "memo_size": self.memo_size,
            "elapsed_sec": self.elapsed_sec,
        }


def query_membership(C: int, m: int, d: int, r: int, steps: int = 53,
                      call_cap: int = 1_500_000, shared_memo: dict | None = None) -> OracleResult:
    """
    Answers: is (d, r) live in A(C, m) after `steps` heartbeat steps from
    the fully populated start?

    Uses memoized backward DFS with a hard call-count cap. If the cap is
    hit before resolution, returns inconclusive=True, live=None (undecided)
    -- callers MUST handle this distinctly from a definitive False.

    shared_memo: optionally pass a dict to reuse memoization across queries
    on the same (C, m, steps) -- this helps a lot when testing many
    candidate images against the same big-side automaton, since backward
    trees from nearby residues often overlap.
    """
    import time
    modulus = 3 ** m
    seq = credit_sequence(steps)
    memo = shared_memo if shared_memo is not None else {}
    step3 = modulus // 3
    call_count = [0]
    hit_cap = [False]

    t0 = time.time()

    def exists_path(step_idx, dd, rr):
        if hit_cap[0]:
            return False  # short-circuit unwind; result will be marked inconclusive
        call_count[0] += 1
        if call_count[0] > call_cap:
            hit_cap[0] = True
            return False
        if step_idx == 0:
            return True
        key = (step_idx, dd, rr)
        if key in memo:
            return memo[key]
        c_k = seq[step_idx - 1]
        found = False
        for a in range(1, C + c_k + 2):
            d_prev = dd - c_k + a
            if d_prev < 0 or d_prev > C:
                continue
            lo = max(1, d_prev + c_k - C)
            hi = d_prev + c_k
            if not (lo <= a <= hi):
                continue
            target = (rr * pow(2, a, modulus) - 1) % modulus
            if target % 3 != 0:
                continue
            base = (target // 3) % modulus
            for j in range(3):
                r_prev = (base + j * step3) % modulus
                if exists_path(step_idx - 1, d_prev, r_prev):
                    found = True
                    break
            if hit_cap[0]:
                break
            if found:
                break
        if not hit_cap[0]:
            memo[key] = found
        return found

    result = exists_path(steps, d, r)
    elapsed = time.time() - t0

    if hit_cap[0]:
        return OracleResult(live=None, inconclusive=True, calls=call_count[0],
                             memo_size=len(memo), elapsed_sec=elapsed)
    return OracleResult(live=result, inconclusive=False, calls=call_count[0],
                         memo_size=len(memo), elapsed_sec=elapsed)


def validate_oracle_against_dense(C, m, steps=53):
    """Cross-check: for ALL (d,r) in a small automaton, the oracle's answer
    must match the dense forward computation exactly. Returns (total, mismatches)."""
    from automaton import run_heartbeat
    live_by_d, hist = run_heartbeat(C, m, steps=steps)
    modulus = 3 ** m
    total = 0
    mismatches = []
    for d in range(C + 1):
        for r in range(modulus):
            dense_live = bool(live_by_d[d][r])
            res = query_membership(C, m, d, r, steps=steps, call_cap=10_000_000)
            total += 1
            if res.inconclusive:
                mismatches.append((d, r, "inconclusive", dense_live))
                continue
            if res.live != dense_live:
                mismatches.append((d, r, res.live, dense_live))
    return total, mismatches


if __name__ == "__main__":
    # Quick self-test when run directly.
    for C, m in [(1, 3), (2, 4), (3, 3)]:
        total, mismatches = validate_oracle_against_dense(C, m, steps=25)
        print(f"C={C} m={m}: total={total} mismatches={len(mismatches)}")
        if mismatches:
            print("  sample mismatches:", mismatches[:5])
