"""
gate2_gate3_census.py -- Backward Basin Certificate mission
(BASIN_CERTIFICATE_SPEC.md), Gate 2 (coverage census) + Gate 3
(uncoverable-class question).

METHODOLOGY (MERGE-SAFE, read before touching this file):
For each DISTINCT odd x in [1, CENSUS_BOUND), run ONE forward simulation
of the odd-map S, checking AT EACH ODD-STEP whether the current iterate
is a layer-0 (species) member via the closed-form, trajectory-free test
is_one_step_species(cur) (3*cur+1 is a power of two with even exponent).
Record hit_step(x) = the smallest n>=0 such that the n-th iterate (x
itself counts as the 0th iterate) is in the species, i.e. hit_step(x)=0
means x itself is a layer-0 member, hit_step(x)=1 means x is a layer-1
member (S(x) in species) etc. matching the spec's "LAYER n = odd x with
S(x) in LAYER(n-1)" recursion (LAYER n members have hit_step = n).
If the cap (MAX_STEPS) is reached with no hit, record hit_step(x) = None
("not within cap").

density(N) = (# distinct odd x with hit_step(x) <= N) / (total distinct
odd x in range). Exactly ONE membership determination per distinct x --
each x is simulated once, its own first-hit step recorded once, and
counted in the numerator for every N >= its own hit_step. This is
merge-safe by construction: we are not sampling/counting VISITS to nodes
across many trajectories (which would overcount shared merge points);
we are recording, once per DISTINCT starting x, that single x's own
first-hit step. Memoization (see below) is used ONLY as a speed
optimization on top of this -- it still credits each distinct x exactly
once to the numerator/denominator logic, based on that x's own first-hit
step (which may be resolved instantly via a memo of an already-visited
downstream value, but the credited x is still the original starting x,
counted once).

Exact integer arithmetic throughout (Python native ints). No floats in
decision logic -- floats appear ONLY when computing final density
percentages for reporting after all counts are exact integers.
"""

import sys
import time
import resource
from descent_common import is_power_of_two, is_one_step_species, Timer

sys.set_int_max_str_digits(2_000_000)

OUT = []
def log(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUT.append(s)


CENSUS_BOUND = 10_000_000   # odd x in [1, CENSUS_BOUND)
MAX_STEPS = 200             # simulate up to this many odd-steps per start
MEMO_CAP_VALUE = 5_000_000  # only memoize hit-step results for values that
                             # themselves fall inside the census range as
                             # odd starts (keeps the memo dict bounded and
                             # meaningful -- values outside this range are
                             # still followed correctly, just not cached)

log("=" * 78)
log("GATE 2 -- coverage census: density(N) for N=1..%d over odd x < %d"
    % (MAX_STEPS, CENSUS_BOUND))
log("=" * 78)
log("")
log("METHODOLOGY (merge-safe): exactly ONE forward simulation per DISTINCT")
log("odd x in [1, %d). At each odd-step, test the current iterate for" % CENSUS_BOUND)
log("species (layer-0) membership via closed-form is_one_step_species()")
log("(3*cur+1 power-of-two with even exponent) -- NO trajectory simulation")
log("inside the membership test itself, only in walking x's OWN orbit.")
log("hit_step(x) = first n>=0 with S^n(x) in species (x itself counts as")
log("n=0). Each distinct x contributes exactly ONE hit_step value to the")
log("dataset; density(N) = count(hit_step(x) <= N) / total distinct x.")
log("Memoization (memo dict keyed on odd values seen during any walk) is")
log("used purely for SPEED -- if a later value's forward orbit hits a")
log("value already resolved by an earlier start's walk, we reuse that")
log("resolved hit-step-from-that-value instead of recomputing -- but the")
log("credit (the entry in the numerator/denominator) is always for the")
log("ORIGINAL starting x, added exactly once, using ITS OWN first-hit")
log("step (= steps-to-reach-memoized-value + memoized value's own hit")
log("step). This does not overcount merged nodes: it is a call-count")
log("speedup on top of a per-distinct-x accounting scheme, not a change")
log("to what is being counted.")
log("")

# hit_step_memo: odd value -> resolved hit_step (int) or None (exceeded
# a step cap during ITS OWN resolution -- see note below on cap handling
# for memoized sub-walks).
hit_step_memo = {}

def resolve_hit_step(start_x, max_steps):
    """Walk the odd-map orbit of start_x up to max_steps odd-steps,
    checking species membership at each iterate (including the 0th,
    start_x itself). Uses hit_step_memo to short-circuit if a later
    iterate has already been resolved by a previous call (memo values
    are stored as absolute hit_step FROM THAT VALUE, i.e. how many
    MORE steps from that value until species, so combining is just
    addition: total = steps_taken_so_far + memoized_value).

    Returns (hit_step or None, path) where path is the list of odd
    values visited starting from start_x (in case the walk needs to
    backfill the memo for each visited node -- see caller).
    """
    path = []
    cur = start_x
    steps = 0
    while True:
        if cur in hit_step_memo:
            memo_val = hit_step_memo[cur]
            # CRITICAL: the memo shortcut must not bypass the max_steps
            # cap. memo_val is the exact remaining-steps-to-species FROM
            # cur (unbounded by any particular caller's budget -- it is
            # a fact about cur's own orbit, computed once). Combined with
            # `steps` (how far the CURRENT walk already travelled to
            # reach cur), the total steps-from-start_x is steps+memo_val
            # -- but this total is only a valid (in-cap) hit_step if it
            # does not exceed max_steps. If it does, start_x's own
            # capped walk would have stopped before ever seeing species,
            # so the correct answer for start_x under THIS max_steps is
            # None, not a step count larger than the cap.
            if memo_val is None or steps + memo_val > max_steps:
                return None, path
            return steps + memo_val, path
        # test species membership directly on cur (closed form, no
        # trajectory run -- this is the "checking at each odd-step" test)
        if is_power_of_two(3 * cur + 1):
            n = (3 * cur + 1).bit_length() - 1
            if n % 2 == 0:
                # cur itself is species -> hit_step from cur is 0
                return steps, path
        path.append(cur)
        if steps >= max_steps:
            return None, path
        # advance one odd-step
        nxt = 3 * cur + 1
        while nxt & 1 == 0:
            nxt >>= 1
        cur = nxt
        steps += 1

def backfill_memo(path, resolved_from_path_end, max_steps):
    """After resolving a walk starting at path[0], we know: for each
    index i in path, hit_step(path[i]) = resolved_from_path_end - i
    (i.e. path[i] is (len(path)-i) ... ) -- more precisely: if the walk
    took `steps` total odd-steps from path[0] to reach either species or
    the cap, then for path[i] (the i-th visited value, 0-indexed, i=0 is
    start_x itself), the number of REMAINING steps from path[i] to the
    same resolution is (original_total_steps - i). We only backfill
    values that are within MEMO_CAP_VALUE (bounded memo) to keep memory
    sane, and only if resolved_from_path_end is not None (a cap-out from
    position 0 doesn't necessarily mean every suffix also caps out under
    a SHORTER budget from its own start -- but since we always call with
    the SAME max_steps ceiling and steps remaining only shrinks moving
    along the path, a cap-out for the full path implies cap-out for
    every suffix too under the same absolute step budget from x's own
    start -- careful reasoning below in the caller comment)."""
    total = len(path)
    for i, val in enumerate(path):
        if val > MEMO_CAP_VALUE:
            continue
        if resolved_from_path_end is None:
            # the ORIGINAL start x hit the cap at max_steps total steps.
            # path[i] took i steps to be reached from path[0], so path[i]
            # itself, walking the SAME remaining trajectory, would need
            # (max_steps - i) more steps to reach the same point where the
            # cap triggered -- but path[i]'s own resolve_hit_step call
            # uses max_steps as ITS OWN full budget (not max_steps - i).
            # Since path[i]'s trajectory is a SUFFIX of a walk that did not
            # reach species within (max_steps - i) further steps (that's
            # how far we got: the ORIGINAL call ran out of budget with
            # (max_steps - i) steps left from path[i]), we can only safely
            # memoize "no species found within (max_steps - i) steps" for
            # path[i], not a full max_steps-budget None. To keep the memo
            # exact and not silently reuse a SHORTER-budget None as if it
            # were a full-budget None, we do NOT memoize None entries here
            # at all -- only successful (non-None) resolutions, which are
            # exact regardless of how much budget was left when found.
            continue
        remaining = resolved_from_path_end - i
        # remaining is the exact hit_step FROM val (species-relative steps
        # from val itself), valid regardless of budget, since it's a
        # concrete integer count derived from an actual completed walk.
        if val not in hit_step_memo:
            hit_step_memo[val] = remaining


log("Running census (this walks 5,000,000 distinct odd starts)...")
total_odds = 0
hit_steps = []  # hit_steps[i] corresponds to odd x = 2*i+1
none_count = 0

t0 = time.perf_counter()
CHECKPOINT = 1_000_000
for x in range(1, CENSUS_BOUND, 2):
    total_odds += 1
    result, path = resolve_hit_step(x, MAX_STEPS)
    backfill_memo(path, result, MAX_STEPS)
    hit_steps.append(result)
    if result is None:
        none_count += 1
    if total_odds % CHECKPOINT == 0:
        elapsed = time.perf_counter() - t0
        log(f"  ... {total_odds:,} distinct odd x processed, "
            f"{elapsed:.2f}s elapsed, memo size={len(hit_step_memo):,}, "
            f"none-so-far={none_count:,}")

t1 = time.perf_counter()
peak_rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
log("")
log(f"Census walk complete: {total_odds:,} distinct odd x in [1, {CENSUS_BOUND})")
log(f"Wall clock: {t1-t0:.3f}s ({total_odds/(t1-t0):,.0f} x/sec)")
log(f"Peak RSS: {peak_rss_mb:.2f} MB")
log(f"Final memo size: {len(hit_step_memo):,}")
log(f"Count with hit_step=None (not within {MAX_STEPS} steps): {none_count:,}")

assert total_odds == (CENSUS_BOUND // 2), \
    f"census count mismatch: {total_odds} != {CENSUS_BOUND//2}"

# ---------------------------------------------------------------------------
# density(N) table
# ---------------------------------------------------------------------------
log("")
log("=" * 78)
log("DENSITY(N) TABLE")
log("=" * 78)
log(f"{'N':>4}  {'count(hit<=N)':>14}  {'density':>12}  {'complement_count':>17}  {'complement_density':>18}")

max_hit = max(h for h in hit_steps if h is not None)
log(f"(max observed finite hit_step across all {total_odds:,} starts: {max_hit})")
log("")

density_rows = []
# cumulative count by N: for each N from 0..MAX_STEPS, count hit_step<=N
counts_at_N = [0] * (MAX_STEPS + 1)
for h in hit_steps:
    if h is not None:
        # increments all N >= h -- do this via a difference array for speed
        counts_at_N[h] += 1
# prefix sum to get count(hit_step <= N) for each N
running = 0
cum_counts = []
for n in range(MAX_STEPS + 1):
    running += counts_at_N[n]
    cum_counts.append(running)

for n in range(0, MAX_STEPS + 1):
    c = cum_counts[n]
    dens = c / total_odds
    comp = total_odds - c
    comp_dens = comp / total_odds
    density_rows.append((n, c, dens, comp, comp_dens))
    if n <= 20 or n % 5 == 0 or n == MAX_STEPS:
        log(f"{n:>4}  {c:>14,}  {dens:>12.9f}  {comp:>17,}  {comp_dens:>18.9f}")

log("")
log(f"density({MAX_STEPS}) = {cum_counts[MAX_STEPS]/total_odds:.9f}  "
    f"(complement = {total_odds - cum_counts[MAX_STEPS]:,} / {total_odds:,} "
    f"= {(total_odds - cum_counts[MAX_STEPS])/total_odds:.9f})")

# write CSV
csv_path = "gate2_density_table.csv"
with open(csv_path, "w") as f:
    f.write("N,count_covered,density,complement_count,complement_density\n")
    for row in density_rows:
        f.write(f"{row[0]},{row[1]},{row[2]:.12f},{row[3]},{row[4]:.12f}\n")
log(f"Full density(N) table (N=0..{MAX_STEPS}) written to {csv_path}")

# ---------------------------------------------------------------------------
# Convergence check: does density(N) plateau, keep climbing, or hit 1.0?
# ---------------------------------------------------------------------------
log("")
log("Convergence check -- density(N) deltas over the tail:")
for n in range(MAX_STEPS - 10, MAX_STEPS + 1):
    if n <= 0:
        continue
    delta = cum_counts[n] - cum_counts[n-1]
    log(f"  N={n}: new covered = {delta:,}  cum density = {cum_counts[n]/total_odds:.9f}")

log("")
log(f"GATE 2 VERDICT: density({MAX_STEPS}) = "
    f"{cum_counts[MAX_STEPS]/total_odds:.9f}. "
    f"Reaches exactly 1.0: {cum_counts[MAX_STEPS] == total_odds}. "
    f"Frozen conjecture was density(N) -> 1 as N grows (~70% confidence).")


# ---------------------------------------------------------------------------
# GATE 3 -- uncoverable-class question
# ---------------------------------------------------------------------------
log("")
log("=" * 78)
log("GATE 3 -- uncoverable-class question")
log("=" * 78)

remaining_x = [2*i+1 for i, h in enumerate(hit_steps) if h is None]
log(f"Odd x with hit_step=None (not within {MAX_STEPS} steps) at census end: "
    f"{len(remaining_x):,}")
if remaining_x:
    log(f"  smallest 20: {remaining_x[:20]}")
    log(f"  largest 20: {remaining_x[-20:]}")

# Check mod-3: does every x===0 mod 3's FIRST step land in the basin quickly?
log("")
log("Check: x === 0 (mod 3) -- these can never be WAYPOINTS (no predecessors)")
log("but CAN be starts. Does their own first step land in the basin quickly?")
mod3_0_hitsteps = []
for i, h in enumerate(hit_steps):
    x = 2*i + 1
    if x % 3 == 0:
        mod3_0_hitsteps.append(h)
mod3_0_none = sum(1 for h in mod3_0_hitsteps if h is None)
mod3_0_max = max((h for h in mod3_0_hitsteps if h is not None), default=None)
log(f"  odd x===0 mod3 count: {len(mod3_0_hitsteps):,}, "
    f"none-count: {mod3_0_none:,}, max finite hit_step: {mod3_0_max}")

# Residue-class structural check: for mod m in {2,3,4,8,9,16,32}, does any
# residue class show a hit_step distribution that keeps GROWING (no finite
# cap) as opposed to one that's simply bounded but needs larger N?
# Efficiency note: for each modulus m, bucket ALL residues in a SINGLE pass
# over hit_steps (accumulating count/none_count/max_finite per residue in
# one sweep), rather than re-scanning the full 5,000,000-entry list once
# per residue (m separate O(total) passes collapsed into 1 per modulus).
# This changes only the WALL-CLOCK cost of this reporting step, not the
# per-distinct-x accounting: every x is still counted in exactly one
# residue bucket for a given m, using its own already-resolved hit_step.
log("")
log("Per-residue-class max finite hit_step and None-count (mod 2,3,4,8,9,16,32):")
for m in (2, 3, 4, 8, 9, 16, 32):
    log(f"  --- mod {m} ---")
    counts = [0] * m
    none_counts = [0] * m
    max_finite = [None] * m
    for i, h in enumerate(hit_steps):
        x = 2 * i + 1
        r = x % m
        counts[r] += 1
        if h is None:
            none_counts[r] += 1
        else:
            if max_finite[r] is None or h > max_finite[r]:
                max_finite[r] = h
    for r in range(m):
        if counts[r] == 0:
            continue
        log(f"    x==={r:3d} (mod{m:3d}): n={counts[r]:>9,}  "
            f"none_count={none_counts[r]:>7,}  max_finite_hit={max_finite[r]}")

# ---------------------------------------------------------------------------
# Trend of complement as N grows -- decay rate check (does complement shrink
# geometrically, polynomially, or plateau at a positive floor?)
# ---------------------------------------------------------------------------
log("")
log("Complement decay trend (complement_count at selected N, ratio to prior):")
checkpoints = [1,2,3,5,8,13,21,34,55,89,MAX_STEPS]
prev = None
for n in checkpoints:
    if n > MAX_STEPS:
        continue
    comp = total_odds - cum_counts[n]
    ratio = (comp / prev) if (prev is not None and prev > 0) else None
    log(f"  N={n:>4}: complement={comp:>10,}  "
        f"(ratio to previous checkpoint: {ratio if ratio is None else f'{ratio:.4f}'})")
    prev = comp

log("")
log("GATE 3 VERDICT:")
if len(remaining_x) == 0:
    log("  Complement is EMPTY at N=%d -- full coverage achieved within cap. "
        "No uncoverable class." % MAX_STEPS)
else:
    frac_remaining = len(remaining_x) / total_odds
    log(f"  Complement at N={MAX_STEPS}: {len(remaining_x):,} / {total_odds:,} "
        f"= {frac_remaining:.9f} of census.")
    log("  See per-residue-class table above for whether any class shows a "
        "GROWING (unbounded) max_finite_hit alongside nonzero none_count "
        "(suggesting 'just needs larger N') vs a hard floor.")

with open("gate2_gate3_results.txt", "w") as f:
    f.write("\n".join(OUT) + "\n")

log("")
log("Gate 2/3 script complete.")
