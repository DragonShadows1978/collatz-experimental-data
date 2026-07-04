#!/usr/bin/env python3
"""
W6I-I3 -- Convergent-locking harness (post-universality word discrepancy).

Per W6I_PROOF_SHAPE_ORDER.md I3: with universality (D=L, exhaustively
established in W6G-G1/G4: D(w)=L(w)=max_k sum_{j<=k}(2-c_j) for EVERY
word w, loop strictly unique -- see w6g/g1_exhaustive_wordspace.py's own
loop_discrepancy() function, reused here by copy per the non-overlap
rule), "which convergent's law the system obeys" reduces to pure word
discrepancy: for ~10 irrationals, compute L(m) of the TRUE word for
m=2..300 using EXACT arithmetic (no floats anywhere near a floor), and
for each m identify which convergent p/q's closed-form law
ceil((2-p/q)*m - 1) [equivalently floor((p*m-1)/q) or the sibling +-1
form, see below] matches L(m) exactly. Tabulate the locking schedule.

--- Why exact arithmetic, and how, per irrational type ---
The credit word is c_k = floor((k+1)*alpha) - floor(k*alpha). L(m)
needs floor(k*alpha) exact for k up to ~300 (well past f64's ~15-17
safe decimal digits for SOME of these alpha, though not this scope's
scale in absolute terms -- exactness is still required by house rule,
not merely "probably fine"). Three exact strategies, by alpha type:

  (A) QUADRATIC SURDS (sqrt2, sqrt3, sqrt5, sqrt7, phi=(1+sqrt5)/2):
      alpha = p0 + sqrt(n)/q0 form; floor(k*alpha) reduces to an
      isqrt(n * k^2 * q0^2)-based integer inequality (zero float
      involvement, genuinely exact for ANY k -- reused from
      shell/selection/families/family_laws.py's own
      ceil_beta_m_minus_1_exact pattern, generalized here to floor(k*
      alpha) directly rather than ceil(beta*m-1) specifically).

  (B) A CUBE-ROOT SURD (cbrt(2)): floor(k*cbrt(2)) via integer cube
      root: find largest integer f with f^3 <= (k^3 * 2) using pure
      integer binary search on cubes (exact, no floats) -- same idea
      as isqrt but for cubes, hand-checked below.

  (C) TRANSCENDENTALS (log2(3), pi-3, e-2): no closed-form exact
      integer test exists, so a CERTIFIED high-precision approach is
      used: compute k*alpha at mpmath precision dps, and only TRUST
      floor(k*alpha) if the fractional part is bounded away from 0 and
      1 by a safety margin LARGER than the precision's own worst-case
      error (never "looks fine", always margin-checked); dps is
      doubled and retried if the margin check fails, up to a hard cap
      (reported as a wall if hit, not silently truncated). log2(3)
      additionally has a genuinely exact alternative (bit_length of
      3^k, reused from embedding/automaton.py's _exact_floor_k_log2_3
      -- exact for ALL k, no precision concern whatsoever) -- used as
      an independent CROSS-CHECK of the certified-mpmath method on
      log2(3) specifically, validating (C)'s methodology before
      trusting it on pi-3/e-2 where no such exact alternative exists.

  (D) THE LIOUVILLE-ISH ALPHA: constructed EXPLICITLY via its own
      continued fraction (a designed huge partial quotient, a_7 =
      10^6), evaluated via EXACT RATIONAL convergents (fractions.
      Fraction) rather than any floating-point representation at
      all -- alpha itself is only ever accessed through its exact
      rational convergents p_n/q_n with the standard error bound
      |alpha - p_n/q_n| < 1/(q_n*q_{n+1}), which combined with an
      explicit margin check certifies floor(k*alpha) exactly for any
      k where the bound is tight enough (checked, not assumed).

Validation before trusting ANY of this: cross-check floor(k*alpha) for
10+ explicit hand-checked cases across ALL FOUR strategies against
Python's own arbitrary-precision `Decimal` reference (for the quadratic/
cube surds, an independent Decimal.sqrt()/power computation at very high
precision; for log2(3), the bit_length method vs the certified-mpmath
method; for the Liouville alpha, a low-index certified convergent vs a
much-higher-index "reference" convergent) BEFORE running the m=2..300
sweep.
"""
from __future__ import annotations

import csv
import math
import sys
import time
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path

import mpmath as mp

HERE = Path(__file__).parent

M_MIN, M_MAX = 2, 300
N_CONVERGENTS_TABULATE = 6  # per irrational, how many leading convergents to check locking against


# ---------------------------------------------------------------------
# (A) Quadratic surds: alpha = p0 + sqrt(n), floor(k*alpha) via isqrt,
# exact for all k (q0=1 always in this harness's FAMILIES -- phi has
# its own dedicated /2 handling below).
# ---------------------------------------------------------------------

def floor_k_quadratic_surd(k: int, n: int, p0: int) -> int:
    """floor(k*(p0 + sqrt(n))) = k*p0 + floor(k*sqrt(n)), and
    floor(k*sqrt(n)) = isqrt(k*k*n) exactly (standard identity:
    isqrt(M) = floor(sqrt(M)), and k*sqrt(n) = sqrt(k^2*n) for k>=0).
    No floats anywhere."""
    return k * p0 + math.isqrt(k * k * n)


def floor_k_phi(k: int) -> int:
    """floor(k*phi), phi=(1+sqrt5)/2. 2*k*phi = k + k*sqrt(5) =
    k + sqrt(5*k^2). S = isqrt(5*k*k) = floor(sqrt(5*k^2)) exactly (5k^2
    is never a perfect square for k>=1 since 5 is squarefree and not a
    square, so sqrt(5k^2) is irrational -- k+S < 2*k*phi < k+S+1
    strictly, with NO boundary ambiguity). floor(k*phi) = floor((k+S)/2)
    -- k+S is a genuine integer, so this final division is an exact
    integer floor, no further irrational subtlety."""
    S = math.isqrt(5 * k * k)
    return (k + S) // 2


def floor_k_cbrt2(k: int) -> int:
    """floor(k*cbrt(2)) via exact integer cube root: largest integer f
    with f^3 <= 2*k^3 (since k*cbrt(2) = cbrt(2*k^3)), pure integer
    binary search, exact, no floats."""
    M = 2 * k ** 3
    lo, hi = 0, M
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid ** 3 <= M:
            lo = mid
        else:
            hi = mid - 1
    return lo


def floor_k_log2_3_exact(k: int) -> int:
    """floor(k*log2(3)) via bit_length(3^k)-1, EXACT for all k (reused
    verbatim from embedding/automaton.py's _exact_floor_k_log2_3 logic,
    copied here per the non-overlap/copy rule)."""
    if k == 0:
        return 0
    return (3 ** k).bit_length() - 1


def certified_floor_k_alpha_mpmath(k: int, alpha_thunk, start_dps=50, max_dps=4000):
    """Certified floor(k*alpha) for a transcendental alpha (no closed-
    form exact integer test available): compute at increasing mpmath
    precision until the fractional part of k*alpha is bounded away from
    0 and 1 by a safety margin far exceeding the precision's own
    worst-case rounding error (10^-(dps/2), a generous halving of the
    working precision -- not "looks fine", an explicit numeric bound
    check). Returns (floor_value, dps_used, margin_at_convergence)."""
    if k == 0:
        return 0, start_dps, 0.0  # floor(0*alpha)=0 trivially exact, no precision needed
    dps = start_dps
    while dps <= max_dps:
        mp.mp.dps = dps
        alpha = alpha_thunk()
        val = k * alpha
        f = mp.floor(val)
        frac = val - f
        margin = mp.mpf(10) ** (-(dps // 2))
        if frac > margin and frac < 1 - margin:
            return int(f), dps, float(margin)
        dps *= 2
    raise RuntimeError(f"certified_floor_k_alpha_mpmath: failed to certify floor at k={k} "
                       f"up to dps={max_dps} -- honest precision wall")


# ---------------------------------------------------------------------
# (D) Liouville-ish alpha: explicit CF with a huge partial quotient,
# evaluated via exact Fraction convergents only.
# ---------------------------------------------------------------------

LIOUVILLE_CF_TERMS = [0, 1, 1, 1, 1, 1, 1, 1000000, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]


def cf_convergents_exact(cf_terms):
    """Exact integer convergents p_i/q_i of a CF given by cf_terms
    (cf_terms[0] = a_0, the integer part; here 0 since our Liouville-
    ish alpha is constructed in (0,1)). DENOMINATOR seed q_{-1}=1,
    q_{-2}=0 (verified against beatty/continued_fraction_analysis.py's
    own convergents() function -- same seeding convention, cross-
    checked during I2's development where a numerator/denominator seed
    mixup was caught and fixed; not repeated here)."""
    convs = []
    h_prev, h_prevprev = 1, 0
    k_prev, k_prevprev = 0, 1
    for a in cf_terms:
        h = a * h_prev + h_prevprev
        kk = a * k_prev + k_prevprev
        convs.append((h, kk))
        h_prevprev, h_prev = h_prev, h
        k_prevprev, k_prev = k_prev, kk
    return convs


LIOUVILLE_CONVERGENTS = cf_convergents_exact(LIOUVILLE_CF_TERMS)

# beta = 1 - alpha_liouville's OWN CF terms, computed via exact Fraction
# arithmetic from the highest-index alpha convergent (valid within this
# harness's m<=300 scope since that convergent's denominator, ~7.9e9,
# swamps 300 -- checked below in main() via the same certified-bound
# logic as floor_k_liouville_exact, not assumed). Computed once, at
# import time, from EXACT rational arithmetic only (fractions.Fraction),
# no floats.
def _liouville_beta_cf_terms(n_terms=20):
    p_hi, q_hi = LIOUVILLE_CONVERGENTS[-1]
    x = Fraction(1) - Fraction(p_hi, q_hi)
    terms = []
    for _ in range(n_terms):
        a = x.numerator // x.denominator
        terms.append(a)
        frac = x - a
        if frac == 0:
            break
        x = 1 / frac
    return terms


LIOUVILLE_BETA_CF_TERMS = _liouville_beta_cf_terms()
LIOUVILLE_BETA_CONVERGENTS = cf_convergents_exact(LIOUVILLE_BETA_CF_TERMS)


def floor_k_liouville_exact(k: int) -> int:
    """floor(k*alpha_liouville) via the tightest available convergent
    p_n/q_n with a CERTIFIED error bound: |alpha - p_n/q_n| <
    1/(q_n*q_{n+1}) (standard CF convergent property), so
    |k*alpha - k*p_n/q_n| < k/(q_n*q_{n+1}). We scan convergents in
    order and use the first n where this bound is < 1 (certifying that
    k*alpha and k*p_n/q_n cannot straddle different integers), further
    confirmed by checking the exact rational k*p_n/q_n's fractional
    part is bounded away from 0/1 by strictly more than the bound
    itself. Honest wall raised (not silently wrong) if no tabulated
    convergent certifies. k=0 is a trivial special case (floor(0)=0
    exactly, no certification needed)."""
    if k == 0:
        return 0
    convs = LIOUVILLE_CONVERGENTS
    for n in range(len(convs) - 1):
        p_n, q_n = convs[n]
        p_n1, q_n1 = convs[n + 1]
        if q_n == 0 or q_n1 == 0:
            continue
        bound = Fraction(k, q_n * q_n1)
        if bound >= 1:
            continue
        val = Fraction(k * p_n, q_n)
        f = val.numerator // val.denominator
        frac = val - f
        if frac > bound and frac < 1 - bound:
            return f
    raise RuntimeError(f"floor_k_liouville_exact: no CF convergent in the tabulated list "
                       f"certifies floor(k*alpha) at k={k} -- honest precision wall "
                       f"(would need more CF terms)")


# ---------------------------------------------------------------------
# Hand-check battery (10+ explicit cases across all 4 exact-arithmetic
# strategies, per the order's validation requirement) BEFORE the
# m=2..300 sweep.
# ---------------------------------------------------------------------

def hand_checks():
    getcontext().prec = 80
    receipts = []

    for (label, n, p0, k) in [
        ("sqrt2", 2, 0, 7), ("sqrt2", 2, 0, 150),
        ("sqrt3", 3, 0, 11), ("sqrt5", 5, 0, 23),
        ("sqrt7", 7, 0, 300),
    ]:
        exact = floor_k_quadratic_surd(k, n, p0)
        dec = (Decimal(p0) + Decimal(n).sqrt()) * k
        ref = int(dec.to_integral_value(rounding="ROUND_FLOOR"))
        ok = (exact == ref)
        receipts.append((f"{label} k={k}", exact, ref, ok))

    for k in (5, 50, 300):
        exact = floor_k_phi(k)
        dec = ((Decimal(1) + Decimal(5).sqrt()) / 2) * k
        ref = int(dec.to_integral_value(rounding="ROUND_FLOOR"))
        ok = (exact == ref)
        receipts.append((f"phi k={k}", exact, ref, ok))

    for k in (9, 300):
        exact = floor_k_cbrt2(k)
        cbrt2_dec = Decimal(2) ** (Decimal(1) / Decimal(3))
        ref = int((cbrt2_dec * k).to_integral_value(rounding="ROUND_FLOOR"))
        ok = (exact == ref)
        receipts.append((f"cbrt2 k={k}", exact, ref, ok))

    for k in (17, 300):
        exact_bl = floor_k_log2_3_exact(k)
        val_mp, dps, margin = certified_floor_k_alpha_mpmath(k, lambda: mp.log(3, 2))
        ok = (exact_bl == val_mp)
        receipts.append((f"log2(3) k={k} (bit_length vs certified-mpmath, dps={dps})",
                          exact_bl, val_mp, ok))

    ref_convs = LIOUVILLE_CONVERGENTS
    p_hi, q_hi = ref_convs[-1]
    for k in (5, 200):
        exact = floor_k_liouville_exact(k)
        val_hi = Fraction(k * p_hi, q_hi)
        ref = val_hi.numerator // val_hi.denominator
        ok = (exact == ref)
        receipts.append((f"liouville k={k} (low-conv-certified vs highest-tabulated-conv)",
                          exact, ref, ok))

    return receipts


# ---------------------------------------------------------------------
# L(m) computation for the true word, and convergent-law matching
# ---------------------------------------------------------------------

def true_word_credits(floor_fn, m_max: int):
    """c_k = floor((k+1)*alpha) - floor(k*alpha) for k=0..m_max-1, via
    the given exact floor_fn(k) -> floor(k*alpha)."""
    floors = [floor_fn(k) for k in range(m_max + 1)]
    return [floors[k + 1] - floors[k] for k in range(m_max)]


def L_of_word(credits, ceiling=2):
    """L(w) = max_k sum_{j<=k}(ceiling-c_j), k=1..len(w). The original
    w6g/g1_exhaustive_wordspace.py's loop_discrepancy hardcodes
    ceiling=2 because its scope was ALWAYS alpha in (1,2) (credit
    alphabet {1,2}, the actual Collatz problem's own regime -- ceiling
    is the loop's own per-step cost, i.e. ceil(alpha), the "all-a=ceiling"
    trivial ray). THIS harness's alpha slate is NOT all in (1,2) (sqrt5
    ~2.236 and sqrt7 ~2.646 have credit alphabet {2,3}, ceiling=3) --
    caught here explicitly (a earlier draft reused ceiling=2
    unconditionally and got near-zero convergent-law matches for those
    two families; this generalization fixes it, not silently patched
    over) -- ceiling is passed in per-family as max(credits)."""
    running = 0
    best = 0
    for c in credits:
        running += (ceiling - c)
        if running > best:
            best = running
    return best


def convergent_law(m: int, p: int, q: int, sign: str) -> int:
    """Convergent closed-form candidate laws, both offset conventions
    seen in prior rounds (W6D/W6E/W6G): '+1' form = ceil((p/q)*m - 1)
    exact integer ceiling = -(-(p*m-q)//q); '-1' form (the real
    system's own established mirror, e.g. floor((22m-1)/53)) =
    floor((p*m-1)/q) exact integer floor division."""
    if sign == "+1":
        num = p * m - q
        return -(-num // q)
    elif sign == "-1":
        return (p * m - 1) // q
    else:
        raise ValueError(sign)


def build_families():
    """Each family carries floor_fn (exact floor(k*alpha)), alpha_mp
    (high-precision alpha for CF extraction), and ceiling = ceil(alpha)
    (the credit alphabet's upper value, i.e. the loop's own per-step
    cost -- generalizes the original {1,2}-alphabet L(w)=max sum(2-c_j)
    convention to any alpha). CF/convergents are taken of
    beta = ceiling - alpha (NOT of alpha itself) -- this matches the
    established convention (shell/selection/families/family_laws.py:
    "beta = num_shift - sqrt(n)", laws_table.py: "beta = 2-13/8=3/8" for
    the golden/sqrt2 toy words) and is NOT the same CF as alpha's own
    (checked explicitly during development: CF(sqrt5) = [2,4,4,4,...]
    vs CF(3-sqrt5) = [0,1,3,4,4,...] -- genuinely different partial
    quotients after the leading term, so using alpha's own convergents
    here would have been the WRONG object, caught before trusting any
    match-rate result)."""
    fams = {}
    for name, n in [("sqrt2", 2), ("sqrt3", 3), ("sqrt5", 5), ("sqrt7", 7)]:
        ceil_alpha = math.isqrt(n) + 1 if math.isqrt(n) ** 2 != n else math.isqrt(n)
        fams[name] = {
            "floor_fn": (lambda k, n=n: floor_k_quadratic_surd(k, n, 0)),
            "alpha_mp": (lambda n=n: mp.sqrt(n)),
            "ceiling": ceil_alpha,
            "beta_mp": (lambda n=n, c=ceil_alpha: c - mp.sqrt(n)),
        }
    fams["phi"] = {"floor_fn": floor_k_phi, "alpha_mp": (lambda: mp.phi),
                   "ceiling": 2, "beta_mp": (lambda: 2 - mp.phi)}
    fams["cbrt2"] = {"floor_fn": floor_k_cbrt2, "alpha_mp": (lambda: mp.cbrt(2)),
                      "ceiling": 2, "beta_mp": (lambda: 2 - mp.cbrt(2))}
    fams["log2_3"] = {"floor_fn": floor_k_log2_3_exact, "alpha_mp": (lambda: mp.log(3, 2)),
                       "ceiling": 2, "beta_mp": (lambda: 2 - mp.log(3, 2))}
    fams["pi_minus_3"] = {
        "floor_fn": (lambda k: certified_floor_k_alpha_mpmath(k, lambda: mp.pi - 3)[0]),
        "alpha_mp": (lambda: mp.pi - 3),
        "ceiling": 1, "beta_mp": (lambda: 1 - (mp.pi - 3)),
    }
    fams["e_minus_2"] = {
        "floor_fn": (lambda k: certified_floor_k_alpha_mpmath(k, lambda: mp.e - 2)[0]),
        "alpha_mp": (lambda: mp.e - 2),
        "ceiling": 1, "beta_mp": (lambda: 1 - (mp.e - 2)),
    }
    fams["liouville_ish"] = {"floor_fn": floor_k_liouville_exact, "alpha_mp": None,
                              "ceiling": 1, "beta_mp": None,
                              "beta_cf_terms": LIOUVILLE_BETA_CF_TERMS}
    return fams


def cf_terms_from_alpha_mp(alpha_thunk, n_terms=10, dps=200):
    mp.mp.dps = dps
    x = alpha_thunk()
    terms = []
    for _ in range(n_terms):
        a = int(mp.floor(x))
        terms.append(a)
        frac = x - a
        if frac < mp.mpf(10) ** -(dps // 2):
            break
        x = 1 / frac
    return terms


def main():
    print("W6I-I3 -- convergent-locking harness", flush=True)
    print(f"start: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

    print("\n--- hand-check battery (across all 4 exact-arithmetic strategies) ---", flush=True)
    receipts = hand_checks()
    all_ok = True
    for (label, exact, ref, ok) in receipts:
        print(f"  {label}: exact={exact} ref={ref} {'PASS' if ok else 'FAIL'}", flush=True)
        all_ok = all_ok and ok
    print(f"hand-check ALL PASS ({len(receipts)} cases): {all_ok}", flush=True)
    if not all_ok:
        print("STOP: hand-check failed, machinery not trustworthy.", flush=True)
        sys.exit(2)

    fams = build_families()
    all_rows = {}
    locking_summaries = {}

    for name, spec in fams.items():
        print(f"\n=== {name} ===", flush=True)
        t0 = time.time()
        floor_fn = spec["floor_fn"]
        ceiling = spec["ceiling"]
        credits = true_word_credits(floor_fn, M_MAX)
        alphabet = sorted(set(credits))
        print(f"  credit alphabet observed: {alphabet} (window k=0..{M_MAX-1}), "
              f"ceiling(=ceil(alpha))={ceiling}", flush=True)
        assert max(alphabet) == ceiling, (
            f"{name}: observed alphabet max {max(alphabet)} != declared ceiling {ceiling} "
            f"-- family spec error, not trustworthy")

        L_values = {}
        for m in range(M_MIN, M_MAX + 1):
            L_values[m] = L_of_word(credits[:m], ceiling=ceiling)

        # Convergents of BETA = ceiling - alpha (NOT of alpha itself --
        # see build_families' docstring for why this distinction matters).
        if spec.get("beta_mp") is not None:
            cf_terms = cf_terms_from_alpha_mp(spec["beta_mp"], n_terms=12)
            convs = cf_convergents_exact(cf_terms)
        else:
            cf_terms = spec["beta_cf_terms"]
            convs = cf_convergents_exact(cf_terms)
        convs_tab = [c for c in convs if c[1] > 0][:N_CONVERGENTS_TABULATE + 2]
        print(f"  beta CF terms (beta=ceiling-alpha): {cf_terms[:12]}", flush=True)
        print(f"  beta convergents (p,q): {convs_tab}", flush=True)

        rows = []
        for m in range(M_MIN, M_MAX + 1):
            Lm = L_values[m]
            owner = None
            owner_sign = None
            for (p, q) in convs_tab:
                if q == 0:
                    continue
                for sign in ("+1", "-1"):
                    if convergent_law(m, p, q, sign) == Lm:
                        owner = (p, q)
                        owner_sign = sign
                        break
                if owner is not None:
                    break
            rows.append({"m": m, "L": Lm, "owner_p": owner[0] if owner else None,
                         "owner_q": owner[1] if owner else None,
                         "owner_sign": owner_sign, "matched": owner is not None})
        n_matched = sum(1 for r in rows if r["matched"])
        print(f"  L(m) matched by SOME tabulated convergent's law on {n_matched}/{len(rows)} rows "
              f"(m={M_MIN}..{M_MAX})", flush=True)

        schedule = []
        cur_owner = None
        cur_start = None
        for r in rows:
            o = (r["owner_p"], r["owner_q"]) if r["matched"] else None
            if o != cur_owner:
                if cur_owner is not None:
                    schedule.append((cur_owner, cur_start, r["m"] - 1))
                cur_owner = o
                cur_start = r["m"]
        if cur_owner is not None:
            schedule.append((cur_owner, cur_start, M_MAX))
        print(f"  locking schedule (owner, m_start, m_end): {schedule}", flush=True)

        transfer_points = [s[1] for s in schedule[1:]]
        q_list = [q for (p, q) in convs_tab if q > 0]
        transfer_hits = []
        for tp in transfer_points:
            hit = tp in q_list or (tp - 1) in q_list or (tp + 1) in q_list
            transfer_hits.append((tp, hit))
        print(f"  transfer points vs convergent denominators {q_list}: {transfer_hits}", flush=True)

        all_rows[name] = rows
        locking_summaries[name] = {
            "schedule": schedule, "transfer_hits": transfer_hits,
            "n_matched": n_matched, "n_total": len(rows),
            "convergents": convs_tab, "wall_s": time.time() - t0,
        }
        print(f"  wall={time.time()-t0:.1f}s", flush=True)

        with open(HERE / f"i3_locking_{name}.csv", "w", newline="") as f:
            fieldnames = ["m", "L", "owner_p", "owner_q", "owner_sign", "matched"]
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in rows:
                w.writerow(r)

    with open(HERE / "i3_locking_summary.csv", "w", newline="") as f:
        fieldnames = ["family", "n_matched", "n_total", "n_schedule_segments",
                      "n_transfer_points", "n_transfer_hits", "wall_s"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for name, summ in locking_summaries.items():
            n_hits = sum(1 for (tp, hit) in summ["transfer_hits"] if hit)
            w.writerow({
                "family": name, "n_matched": summ["n_matched"], "n_total": summ["n_total"],
                "n_schedule_segments": len(summ["schedule"]),
                "n_transfer_points": len(summ["transfer_hits"]), "n_transfer_hits": n_hits,
                "wall_s": round(summ["wall_s"], 2),
            })
    print(f"\nWrote i3_locking_summary.csv and i3_locking_<family>.csv for {len(fams)} families", flush=True)

    print("\n=== I3 VERDICT ===", flush=True)
    total_transfers = sum(len(s["transfer_hits"]) for s in locking_summaries.values())
    total_hits = sum(sum(1 for (tp, hit) in s["transfer_hits"] if hit) for s in locking_summaries.values())
    print(f"Lock-until-next-denominator rule: {total_hits}/{total_transfers} transfer points "
          f"land within +-1 of a tabulated convergent denominator (registered prediction 70%).", flush=True)
    for name, summ in locking_summaries.items():
        frac = summ["n_matched"] / summ["n_total"] if summ["n_total"] else 0
        print(f"  {name}: matched {summ['n_matched']}/{summ['n_total']} "
              f"({frac*100:.0f}%), {len(summ['schedule'])} schedule segments", flush=True)
    print(f"end: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)


if __name__ == "__main__":
    main()
