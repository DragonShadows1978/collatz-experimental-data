#!/usr/bin/env python3
"""
Beatty / mechanical-word / Sturmian search for an exact representation of

    M_edge(C) = floor(53*(C+1)/22)

Tasks (per mission spec):
  1. Confirm exact periodicity M_edge(C+22) - M_edge(C) = 53 (rational formula; trivial
     algebraic fact, done here for completeness — real "measured" verification is a
     separate, repo-data-grounded task, not done in this script).
  2. Hunt for exact Beatty / mechanical-word / first-passage representations, fit against
     C = 1..200, report exact-match verdicts. Test BOTH the rational slope 22/53 and the
     irrational slope log2(3).
  3. Report first C (up to 10^6) where floor(53(C+1)/22) diverges from the irrational-slope
     analogues found to match in task 2.

All outputs are written as JSON/CSV into the same directory as this script.
"""
import json
import math
from fractions import Fraction
from pathlib import Path

OUTDIR = Path(__file__).resolve().parent

LOG2_3 = math.log2(3)  # irrational slope, ~1.5849625007211562
ALPHA = LOG2_3         # "heartbeat" slope used elsewhere in the proof (drop/support ratio context)

RATIONAL_SLOPE = Fraction(22, 53)   # 22 support out of 53 heartbeat steps
IRRATIONAL_SLOPE = LOG2_3 - 1       # ~0.5849625007211562  (31/53 approx this; support fraction complement)

# ---------------------------------------------------------------------------
# Reference (ground truth) formula
# ---------------------------------------------------------------------------

def M_edge_rational(C: int) -> int:
    """floor(53*(C+1)/22) using exact integer arithmetic."""
    return (53 * (C + 1)) // 22


# ---------------------------------------------------------------------------
# Task 1: periodicity of the rational formula (exact, algebraic — sanity check)
# ---------------------------------------------------------------------------

def check_periodicity(max_C: int = 2000):
    violations = []
    for C in range(1, max_C - 22 + 1):
        d = M_edge_rational(C + 22) - M_edge_rational(C)
        if d != 53:
            violations.append({"C": C, "delta": d})
    return {
        "range_checked": [1, max_C],
        "expected_delta": 53,
        "period": 22,
        "num_violations": len(violations),
        "violations": violations[:50],
        "exact_periodicity_holds": len(violations) == 0,
        "note": (
            "This is an algebraic property of floor(53*(C+1)/22): since 53 and 22 are "
            "exact integers, floor(53*(C+22+1)/22) = floor(53*(C+1)/22 + 53) = M_edge(C)+53 "
            "identically, for ALL integer C, not just empirically. This function verifies it "
            "computationally over a wide range as a sanity check; it does not by itself say "
            "anything about whether the MEASURED automaton capacities are periodic — that must "
            "be checked against the repo's raw measured data separately (see companion report)."
        ),
    }


# ---------------------------------------------------------------------------
# Task 2: candidate exact representations
# ---------------------------------------------------------------------------

def frac(x: float) -> float:
    return x - math.floor(x)


def family_a_beatty_rational(C: int) -> int:
    """
    (a) M_edge(C) = #{ m>=1 : frac(m*22/53) in [0, (C+1)*22/53 mod 1) }
    Exact rational arithmetic version using Fraction, tested over m=1..UPPER.
    We must choose a search window for m. Because frac(m*22/53) is periodic in m with
    period 53 (since gcd(22,53)=1, m*22/53 mod 1 cycles through all 53 residues/53 as m
    ranges over a period-53 block), the natural window is m = 1..53*ceil((C+1)/22) — i.e.
    one full heartbeat block per unit "budget" of 22 support-phases. We instead directly
    use the closed-form combinatorial identity: for slope p/q in lowest terms, the count
    #{1<=m<=N : frac(m*p/q) < theta} has a known sawtooth closed form. Here we just brute
    force count over the natural periodic domain m=1..N with N scaled to C, since q=53 is
    small.
    """
    p, q = 22, 53
    theta = frac((C + 1) * p / q)  # threshold in [0,1)
    # natural window size: one period of the rational rotation is q=53 steps, and the
    # "budget" grows by p=22 per unit C+1amount -> so window N = q * something. We scan
    # m = 1..q*(C+1) capped, but that's not bounded well; instead the correct Beatty-style
    # count for a first-return problem uses N = q (one full period) times multiplicity.
    # We test the single-period definition (m=1..q) scaled by the natural "layer" count.
    N = q
    count = sum(1 for m in range(1, N + 1) if frac(m * p / q) < theta)
    return count


def family_a_variants(C: int, upper_bound_C: int):
    """
    Several concrete variants of family (a), each a genuine function of C alone,
    evaluated exactly with Fraction arithmetic (rational slope 22/53).
    Returns dict variant_name -> value.
    """
    p, q = 22, 53
    out = {}

    # Variant A1: three-distance / Beatty count with N = (C+1), threshold = p/q
    #   #{1<=m<=C+1 : frac(m*p/q) < p/q}  -- a natural "how many of the first C+1 rotations
    #   land in the support arc" count.
    N = C + 1
    theta = Fraction(p, q)
    cnt = sum(1 for m in range(1, N + 1) if Fraction(m * p, q) - Fraction(m * p, q).__floor__() < theta)
    out["A1_N=C+1_theta=p/q"] = cnt

    # Variant A2: Beatty sequence value itself: floor((C+1)*q/p) style (dual slope)
    out["A2_floor((C+1)*q/p)"] = math.floor(Fraction(C + 1) * Fraction(q, p))

    # Variant A3: the actual target rearranged as a pure Beatty sequence term:
    #   floor(53(C+1)/22) = floor((C+1) / (22/53)) = Beatty sequence with modulus 22/53
    out["A3_floor((C+1)/(p/q))_==target_by_construction"] = math.floor(Fraction(C + 1) / Fraction(p, q))

    return out


def family_b_mechanical_word(C: int, heartbeat: list) -> dict:
    """
    (b) mechanical-word letter counts: S(k) = #{j<=k : heartbeat_j == support(1)}.
    heartbeat is the 53-length 0/1 word (1=support, 0=drop) reconstructed from the
    thin_phase_mod_53 list in Lock3_support_cell_audit/lock3_support_cell_summary.json.
    We test threshold-style windows f(C) and report S(f(C)) against target.
    """
    q = len(heartbeat)
    assert q == 53
    # prefix sum of the heartbeat word
    prefix = [0] * (q + 1)
    for i, b in enumerate(heartbeat):
        prefix[i + 1] = prefix[i] + b

    def S(k):
        """support-letter count in first k symbols of the (period-53) word."""
        full_periods, rem = divmod(k, q)
        return full_periods * prefix[q] + prefix[rem]

    out = {}
    # Variant B1: window length f(C) = 53*(C+1)/22 rounded down to nearest heartbeat step
    #   i.e. count support letters in the first floor(53(C+1)/22) steps -- circular by
    #   construction (uses the target as the window), included only as a consistency check,
    #   NOT a genuine independent derivation.
    target = M_edge_rational(C)

    # Variant B2: window f(C) = 53 * ceil((C+1)/22)  (heartbeat-aligned window covering budget)
    f2 = 53 * math.ceil((C + 1) / 22)
    out["B2_S(53*ceil((C+1)/22))"] = S(f2)

    # Variant B3: first-passage — smallest k such that S(k) >= C+1 (see family c; duplicated
    # here as a mechanical-word framing for cross-check)
    k = 0
    while S(k) < C + 1:
        k += 1
        if k > q * (C + 2):
            k = None
            break
    out["B3_first_passage_S(k)>=C+1_report_k_minus_1"] = (k - 1) if k is not None else None

    return out


def family_c_first_passage(C: int, heartbeat: list) -> dict:
    """
    (c) capacity as first passage of the Sturmian counting function.
    S(m) = #{j<=m : heartbeat_j == support}.
    Candidate: M_edge(C) = largest m such that 22*m <= 53*(C+1)  <=> the *drop*-count
    interpretation, OR the smallest m such that the m-th partial sum of the heartbeat
    word crosses a C-dependent threshold, per spec:
      "smallest m such that the m-th partial sum of the heartbeat word crosses a
       C-dependent threshold" — here "m-th partial sum" is over the *heartbeat repeated
       m times* (m = full heartbeats, not steps), i.e. total phase-height cells used
       vs. total support constraints imposed, matching the proof's own accounting:
       22*m <= 53*(C+1).
    """
    out = {}
    # C1: largest integer m with 22*m <= 53*(C+1)  -- this IS the theorem's own derivation,
    # i.e. M_edge(C) = floor(53*(C+1)/22) exactly by definition. Included as the transparent
    # "first passage of linear capacity constraint" baseline (algebraically identical to target,
    # not an independent representation).
    out["C1_largest_m_22m<=53(C+1)"] = (53 * (C + 1)) // 22

    # C2: first-passage of the actual support-letter partial-sum function against threshold
    # C+1, i.e. smallest total heartbeat-STEP count m such that the number of support-phase
    # steps encountered so far (cycling through the 53-word) reaches ceil(22*(C+1)/22)... this
    # collapses to variant B3 above; keep for completeness under family C naming.
    q = len(heartbeat)
    prefix = [0] * (q + 1)
    for i, b in enumerate(heartbeat):
        prefix[i + 1] = prefix[i] + b

    def S(k):
        full_periods, rem = divmod(k, q)
        return full_periods * prefix[q] + prefix[rem]

    k = 0
    threshold = C + 1
    while S(k) < threshold:
        k += 1
        if k > q * (C + 2):
            k = None
            break
    out["C2_first_passage_step_count(support>=C+1)"] = k
    # convert step count to "heartbeats" (divide by 53) for comparison to M_edge scale
    out["C2_as_heartbeats_k/53"] = (k / 53) if k is not None else None

    return out


# ---------------------------------------------------------------------------
# Irrational-slope analogues (using true log2(3), not the 22/53 convergent)
# ---------------------------------------------------------------------------

## IMPORTANT -- slope bookkeeping, verified numerically before use:
##   support fraction  22/53 = 0.415094...   <-> irrational analogue  2 - log2(3) = 0.415037...
##   drop    fraction  31/53 = 0.584906...   <-> irrational analogue  log2(3) - 1 = 0.584963...
## i.e. 22/53 is a rational convergent of (2 - log2(3)), NOT of (log2(3) - 1).
## The formula under test, M_edge(C) = floor(53(C+1)/22) = floor((C+1)/(22/53)), so its
## genuine irrational-slope analogue replaces the denominator 22/53 with its irrational
## target (2 - log2(3)), giving v1/v4 below. An earlier draft of this script also tried a
## "(log2(3)-1)" denominator and a "log2(3)/(log2(3)-1)" scale factor; both used the WRONG
## ratio (target ratio is 53/22 = 2.4091..., not log2(3)/(log2(3)-1) = 2.7095...) and produced
## a spurious "diverges at C=1" artifact from a mislabeled analogue, not a real finding. They
## have been removed to avoid reporting a false mismatch.

def M_edge_irrational_v1(C: int) -> int:
    """floor((C+1) / (2 - log2(3))): true irrational analogue of floor((C+1)/(22/53))."""
    denom = 2 - LOG2_3
    return math.floor((C + 1) / denom)


def M_edge_irrational_v4(C: int) -> int:
    """Same value as v1, expressed in the proof's own 53-scaled form:
    floor(53*(C+1) / (53*(2-log2(3)))). Kept as an independent code path (different
    floating-point operation order) as a numerical-robustness cross-check on v1."""
    return math.floor(53 * (C + 1) / (53 * (2 - LOG2_3)))


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main():
    results = {}

    # --- Task 1 ---
    results["task1_periodicity_rational_formula"] = check_periodicity(max_C=5000)

    # --- Load heartbeat word from repo data (22 support phases mod 53) ---
    summary_path = Path(
        "/mnt/ForgeRealm/collatz-experimental-data/Lock3_support_cell_audit/lock3_support_cell_summary.json"
    )
    heartbeat_source = None
    heartbeat = [0] * 53
    if summary_path.exists():
        with open(summary_path) as f:
            summary = json.load(f)
        thin_phases = summary["thin_phases_mod_53"]
        for ph in thin_phases:
            heartbeat[ph] = 1
        heartbeat_source = str(summary_path)
        assert sum(heartbeat) == 22, f"expected 22 support phases, got {sum(heartbeat)}"
    else:
        raise SystemExit(f"required heartbeat source not found: {summary_path}")

    results["heartbeat_word"] = {
        "source": heartbeat_source,
        "support_phase_count": sum(heartbeat),
        "drop_phase_count": len(heartbeat) - sum(heartbeat),
        "word": "".join(str(b) for b in heartbeat),
    }

    # --- Task 2: fit families over C = 1..200 (rational slope) ---
    C_LO, C_HI = 1, 200
    per_C_rows = []
    family_a_exact = {}
    family_b_exact = {}
    family_c_exact = {}

    for C in range(C_LO, C_HI + 1):
        target = M_edge_rational(C)
        row = {"C": C, "target_M_edge": target}

        a_vals = family_a_variants(C, C_HI)
        for k, v in a_vals.items():
            row[f"a.{k}"] = v

        b_vals = family_b_mechanical_word(C, heartbeat)
        for k, v in b_vals.items():
            row[f"b.{k}"] = v

        c_vals = family_c_first_passage(C, heartbeat)
        for k, v in c_vals.items():
            row[f"c.{k}"] = v

        per_C_rows.append(row)

        for k, v in a_vals.items():
            family_a_exact.setdefault(k, True)
            if v != target:
                family_a_exact[k] = False
        for k, v in b_vals.items():
            family_b_exact.setdefault(k, True)
            if v != target:
                family_b_exact[k] = False
        for k, v in c_vals.items():
            family_c_exact.setdefault(k, True)
            if v != target:
                family_c_exact[k] = False

    results["task2_fit_range"] = [C_LO, C_HI]
    results["task2_family_a_beatty_rational"] = family_a_exact
    results["task2_family_b_mechanical_word"] = family_b_exact
    results["task2_family_c_first_passage"] = family_c_exact

    # --- Task 2 continued: irrational-slope versions, same fit range ---
    irr_variants = {
        "v1_floor((C+1)/(2-log2_3))": M_edge_irrational_v1,
        "v4_floor(53(C+1)/(53(2-log2_3)))": M_edge_irrational_v4,
    }
    irr_exact_in_range = {}
    irr_first_mismatch_in_range = {}
    for name, fn in irr_variants.items():
        exact = True
        first_mismatch = None
        for C in range(C_LO, C_HI + 1):
            t = M_edge_rational(C)
            v = fn(C)
            if v != t:
                exact = False
                if first_mismatch is None:
                    first_mismatch = {"C": C, "target": t, "irrational_value": v, "diff": v - t}
        irr_exact_in_range[name] = exact
        irr_first_mismatch_in_range[name] = first_mismatch

    results["task2_irrational_slope_variants_exact_over_1_200"] = irr_exact_in_range
    results["task2_irrational_slope_variants_first_mismatch_over_1_200"] = irr_first_mismatch_in_range

    # --- Task 3: search C = 1..10^6 for first divergence between rational formula and
    #     each irrational-slope variant ---
    LIMIT = 1_000_000
    divergence_report = {}
    for name, fn in irr_variants.items():
        first_c = None
        # direct O(N) scan; each fn call is O(1) float floor, fast enough for 1e6
        for C in range(1, LIMIT + 1):
            t = M_edge_rational(C)
            v = fn(C)
            if v != t:
                first_c = {"C": C, "target_rational": t, "irrational_value": v, "diff": v - t}
                break
        divergence_report[name] = {
            "first_divergence_C_up_to_1e6": first_c,
            "searched_up_to": LIMIT,
        }

    results["task3_first_divergence_search"] = divergence_report

    # --- write outputs ---
    with open(OUTDIR / "beatty_search_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # per-C CSV for the C=1..200 fit
    import csv

    if per_C_rows:
        fieldnames = list(per_C_rows[0].keys())
        with open(OUTDIR / "fit_C1_200.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for row in per_C_rows:
                w.writerow(row)

    print(json.dumps(results, indent=2)[:4000])
    print("...")
    print("Full results written to:", OUTDIR / "beatty_search_results.json")
    print("Per-C fit table written to:", OUTDIR / "fit_C1_200.csv")


if __name__ == "__main__":
    main()
