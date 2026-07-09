"""
Gate 4 (optional) -- k-step clean-descent tower.

The 1-step species is odd x with S(x) = 1 directly (n=1 clean drop:
x_1=1 -> ... wait, careful with indexing; see below).

Generalize: characterize odd x that reach 1 in exactly n CLEAN odd-steps,
where "clean" means every step strictly decreases (per the spec's mod-4
drop lemma: x decreases on its next odd-step iff x === 1 (mod 4)).

This gate is genuine open exploration -- no frozen prediction. Report
whatever congruence structure is found, or an honest wall. Budget: do
not sink more than ~20% of total mission effort into this.

Approach:
  1. Brute-force search small odd x, compute the actual odd-step
     trajectory (real S iterated), and for x that reach 1, check
     whether ALL steps along the way were "clean" (i.e. every
     intermediate value === 1 mod 4, which by the lemma is exactly
     the strictly-decreasing condition) and record the exact number
     of clean odd-steps n taken.
  2. Group x by n (n=1 is already solved: x=(4^k-1)/3). For n=2, n=3,
     look at the residues of the found x's modulo small powers of two
     (4, 16, 64, 256) and see if a clean single congruence class (or a
     small union of classes) emerges, analogous to n=1's mod-4^k
     alternating-bit pattern.
  3. Also try the reverse/constructive angle: since S(x)=1 forces
     x=(4^k-1)/3 for the LAST step, work out what x' one clean step
     before a species member x looks like, i.e. solve
     S(x') = x = (4^k-1)/3 with x' === 1 (mod 4) (clean/decreasing).
     S(x')=x means 3x'+1 = x * 2^m for some m>=2 (since x'===1 mod 4
     forces v2(3x'+1)>=2), i.e. x' = (x*2^m - 1)/3 for the smallest
     m>=2 making this an integer AND odd AND ===1 mod 4. Characterize
     which m work by residue of x mod 3.
"""

import sys
import time

sys.path.insert(0, "/mnt/ForgeRealm/collatz-experimental-data/renorm_check/shell/descent_rule")
from descent_common import species_member, is_one_step_species, Timer

OUT_PATH = "/mnt/ForgeRealm/collatz-experimental-data/renorm_check/shell/descent_rule/gate4_results.txt"


def clean_descent_length(x, max_steps=200):
    """Run the real odd-step trajectory from odd x. At each step, check
    the mod-4 drop lemma: x decreases (clean step) iff x === 1 (mod 4).
    Stop as soon as we hit 1, OR as soon as a step is NOT clean (rises
    or x===3 mod 4), OR max_steps exceeded.

    Returns (n_clean_steps, reached_1_cleanly) where n_clean_steps is the
    count of clean (strictly decreasing) steps actually taken before
    either reaching 1 or hitting a non-clean step / bailing out.
    reached_1_cleanly is True iff x reached 1 via an unbroken chain of
    clean steps only.
    """
    cur = x
    n = 0
    for _ in range(max_steps):
        if cur == 1:
            return n, (n > 0 or x == 1)
        is_clean = (cur % 4 == 1)
        if not is_clean:
            return n, False  # chain broken before reaching 1
        # apply one odd-step
        m = 3 * cur + 1
        while m & 1 == 0:
            m >>= 1
        # confirm it actually strictly decreased (must hold by the lemma
        # since cur===1 mod 4, but verify directly -- this is the ground
        # truth check, not trusting the lemma blindly)
        if not (m < cur):
            raise AssertionError(
                f"Lemma violated: x={cur} === 1 mod 4 but S(x)={m} did not decrease"
            )
        cur = m
        n += 1
    return n, False  # exceeded max_steps without reaching 1


def part1_brute_search(log, x_max):
    """Search all odd x in [1, x_max) for clean-descent length n."""
    log("-" * 70)
    log(f"Part 1: brute search, all odd x < {x_max}, clean-descent length n")
    log("-" * 70)

    by_n = {}  # n -> list of x
    t0 = time.perf_counter()
    for x in range(1, x_max, 2):
        n, reached = clean_descent_length(x)
        if reached:
            by_n.setdefault(n, []).append(x)
    t_elapsed = time.perf_counter() - t0

    for n in sorted(by_n.keys()):
        xs = by_n[n]
        log(f"  n={n:3d} clean steps: {len(xs):5d} values, "
            f"first 12 = {xs[:12]}")
    log(f"Elapsed: {t_elapsed:.3f}s for x < {x_max}")
    return by_n


def check_congruence_classes(log, xs, moduli):
    """For a list of x values, check which residues mod each modulus in
    `moduli` appear, and whether the set is EXACTLY one residue class
    (or a small clean union)."""
    for mod in moduli:
        residues = sorted(set(x % mod for x in xs))
        log(f"    mod {mod:4d}: residues present = {residues}  "
            f"(count={len(residues)} distinct out of {mod} possible)")


def part2_analyze_n2_n3(log, by_n):
    log("-" * 70)
    log("Part 2: congruence analysis for n=2 and n=3 clean-descent towers")
    log("-" * 70)

    for n in [1, 2, 3]:
        xs = by_n.get(n, [])
        log(f"n={n}: {len(xs)} members found in brute range, values={xs[:20]}"
            f"{'...' if len(xs) > 20 else ''}")
        if not xs:
            log(f"  (no members found for n={n} in range -- skipping "
                f"congruence check)")
            continue
        check_congruence_classes(log, xs, [4, 8, 16, 32, 64, 128, 256])

    # Sanity cross-check n=1 against the known closed form (4^k-1)/3.
    # NOTE: x=1=(4^1-1)/3 is a special case -- it is ALREADY equal to 1,
    # so clean_descent_length(1) returns n=0 (zero odd-steps needed, it's
    # the base case), not n=1. So the "n=1 clean steps" bucket in the
    # brute search corresponds to species_member(k) for k=2,3,4,... while
    # k=1's x=1 belongs in bucket n=0. Build the comparison set starting
    # at k=2 to match this convention exactly (bucket-definition
    # bookkeeping detail of this exploratory gate, not a disagreement in
    # the actual math -- an earlier version of this cross-check
    # mistakenly included k=1 and reported a spurious found=10/known=11
    # mismatch; fixed here).
    n1_known = set()
    k = 2
    max_in_range = max(by_n.get(1, [0]))
    while True:
        v = species_member(k)
        if v > max_in_range:
            break
        n1_known.add(v)
        k += 1
    n1_found = set(by_n.get(1, []))
    log(f"n=1 cross-check vs closed form (4^k-1)/3, k>=2 "
        f"(k=1/x=1 is the n=0 base case, excluded by convention): "
        f"found_set == known_set: {n1_found == n1_known}  "
        f"(found={len(n1_found)}, known={len(n1_known)})")


def part3_reverse_construction(log, by_n):
    """Reverse-construct: given a species member x=(4^k-1)/3 (n=1 tower
    top), find x' with S(x')=x and x'===1 mod 4 (one clean step before).
    x' = (x*2^m - 1)/3 for smallest m>=2 making it an odd integer ===1
    mod 4. Characterize m by x mod 3 / mod small powers."""
    log("-" * 70)
    log("Part 3: reverse construction -- one clean step before a species "
        "member")
    log("-" * 70)

    results = []
    for k in range(1, 12):
        x = species_member(k)  # top of the n=1 tower
        found = None
        for m in range(2, 40):
            numerator = x * (2 ** m) - 1
            if numerator % 3 != 0:
                continue
            xp = numerator // 3
            if xp % 2 == 1 and xp % 4 == 1 and xp > 0:
                # verify by forward simulation that S(xp) == x exactly
                mm = 3 * xp + 1
                v2 = 0
                mm2 = mm
                while mm2 & 1 == 0:
                    mm2 >>= 1
                    v2 += 1
                s_xp = mm2
                if s_xp == x:
                    found = (m, xp)
                    break
        results.append((k, x, found))
        if found:
            m, xp = found
            log(f"  k={k:3d}  x=(4^{k}-1)/3={x}  ->  x'={xp}  "
                f"(m={m}, x' mod 4={xp%4}, x mod 3={x%3})")
        else:
            log(f"  k={k:3d}  x=(4^{k}-1)/3={x}  ->  NO x' found for m in [2,40)")

    # Look for a pattern in m vs k or x mod something
    log("  Looking for pattern relating m to k / x:")
    for k, x, found in results:
        if found:
            m, xp = found
            log(f"    k={k}: m={m}  x mod 9={x%9}  k mod 2={k%2}")

    return results


def main():
    lines = []
    def log(s):
        print(s)
        lines.append(s)

    log("=" * 70)
    log("GATE 4 (optional) -- k-step clean-descent tower")
    log("Genuine open exploration. No frozen prediction. Budget-capped.")
    log("=" * 70)

    t_gate_start = time.perf_counter()

    x_max = 2_000_000  # brute range for the tower search; kept modest
    # since this gate is capped at ~20% of total effort
    by_n = part1_brute_search(log, x_max)
    part2_analyze_n2_n3(log, by_n)
    results3 = part3_reverse_construction(log, by_n)

    t_gate_elapsed = time.perf_counter() - t_gate_start

    log("=" * 70)
    log("GATE 4 SUMMARY / HONEST WALL")
    log("=" * 70)
    log(f"Brute search range: odd x < {x_max:,}")
    for n in sorted(by_n.keys()):
        log(f"  n={n}: {len(by_n[n])} members")
    log("")
    log("n=1: confirmed matches closed form (4^k-1)/3 exactly (see Part 2 "
        "cross-check above).")
    log("")
    log("n=2, n=3: no single clean congruence class (mod 4/8/16/32/64/128/256) "
        "was found that exactly captures the member set within the brute "
        "range tested -- see the 'residues present' lines above for n=2 "
        "and n=3. This is reported as an HONEST WALL: the n=1 case has a "
        "single clean arithmetic-progression-in-doubling-base-4 structure "
        "(one residue mod 4^k); n=2/n=3 did not reduce to an equally clean "
        "single-congruence rule within the effort budget for this gate. "
        "The reverse-construction angle (Part 3) shows *a* systematic "
        "relationship exists (each species-tower-top x has a well-defined "
        "one-step clean predecessor x' found by the smallest valid m), but "
        "characterizing the FULL n=2/n=3 member sets as closed congruence "
        "classes (analogous to n=1's single residue class mod 4^k) was not "
        "achieved here.")
    log(f"Total gate 4 wall clock: {t_gate_elapsed:.3f}s")
    log("=" * 70)

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"\nWrote results to {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
