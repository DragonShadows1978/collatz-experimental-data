"""
gate0_gate1.py -- Backward Basin Certificate mission (BASIN_CERTIFICATE_SPEC.md)

Gate 0: reproduce layer-0 species closed form + the mod-3 predecessor-
existence rule, by direct construction.

Gate 1: derive LAYER 1, LAYER 2, LAYER 3 by exhaustive enumeration + fit
congruence classes (or report honestly why they don't reduce cleanly).

Exact integer arithmetic throughout. No floats in any decision logic.
"""

import sys
from descent_common import (
    species_member, one_odd_step, is_power_of_two, is_one_step_species, Timer,
)

sys.set_int_max_str_digits(2_000_000)

OUT = []
def log(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    OUT.append(s)


# ---------------------------------------------------------------------------
# GATE 0a: layer-0 species closed form, first ~30 members, confirm S(x)=1
# ---------------------------------------------------------------------------
log("=" * 78)
log("GATE 0a -- layer-0 species (4^k-1)/3, k=1..30, confirm S(x)=1")
log("=" * 78)

layer0_members = []
gate0a_pass = True
for k in range(1, 31):
    x = species_member(k)
    sx = one_odd_step(x)
    mod4 = x % 4
    ok = (sx == 1) and (mod4 == 1)
    if not ok:
        gate0a_pass = False
    layer0_members.append(x)
    log(f"k={k:2d}  x={x:>10d}  S(x)={sx}  x mod 4={mod4}  ok={ok}")

log(f"GATE 0a RESULT: all 30 members reach 1 in one odd-step and are "
    f"===1 (mod 4): {gate0a_pass}")
assert gate0a_pass, "GATE 0a FAILED -- harness bug, stop and diagnose"


# ---------------------------------------------------------------------------
# GATE 0b: mod-3 predecessor existence rule, direct construction
# ---------------------------------------------------------------------------
log("")
log("=" * 78)
log("GATE 0b -- mod-3 predecessor existence rule: x=(t*2^j-1)/3, j=1..20")
log("=" * 78)
log("Rule under test: t===1 (mod3) -> predecessors at EVEN j only;")
log("                 t===2 (mod3) -> predecessors at ODD j only;")
log("                 t===0 (mod3) -> NO predecessors at any j.")
log("")

def predecessors_of(t, jmax=20):
    """For odd t, return dict j -> x for all j in [1,jmax] where
    x=(t*2^j-1)/3 is an odd positive integer. Direct construction, no
    shortcuts -- tests integrality and oddness explicitly for every j."""
    hits = {}
    for j in range(1, jmax + 1):
        num = t * (2 ** j) - 1
        if num % 3 != 0:
            continue
        x = num // 3
        if x <= 0:
            continue
        if x % 2 == 1:
            hits[j] = x
    return hits

# Pick a handful of t values in each residue class mod 3 (odd t only,
# since predecessors of odd t are what the backward map cares about).
test_ts = {
    0: [3, 9, 15, 21, 33, 51],       # t === 0 mod 3 (odd multiples of 3)
    1: [1, 7, 13, 19, 31, 37],       # t === 1 mod 3
    2: [5, 11, 17, 23, 29, 41],      # t === 2 mod 3
}

gate0b_pass = True
for resclass, ts in test_ts.items():
    log(f"--- t === {resclass} (mod 3) ---")
    for t in ts:
        assert t % 3 == resclass and t % 2 == 1
        hits = predecessors_of(t, jmax=20)
        js = sorted(hits.keys())
        if resclass == 0:
            ok = (len(js) == 0)
            log(f"  t={t:3d}: predecessor j's found = {js}  "
                f"(expect NONE)  ok={ok}")
        elif resclass == 1:
            ok = all(j % 2 == 0 for j in js) and len(js) > 0
            log(f"  t={t:3d}: predecessor j's found = {js}  "
                f"(expect all EVEN, nonempty)  ok={ok}")
        else:  # resclass == 2
            ok = all(j % 2 == 1 for j in js) and len(js) > 0
            log(f"  t={t:3d}: predecessor j's found = {js}  "
                f"(expect all ODD, nonempty)  ok={ok}")
        # cross-check: for each found predecessor x, confirm S(x)==t
        for j, x in hits.items():
            sx = one_odd_step(x)
            xcheck = (sx == t)
            if not xcheck:
                ok = False
                log(f"    CROSS-CHECK FAIL: S({x}) = {sx} != t={t} at j={j}")
        if not ok:
            gate0b_pass = False

log("")
log(f"GATE 0b RESULT: mod-3 predecessor-existence rule confirmed across "
    f"{sum(len(v) for v in test_ts.values())} t values, j=1..20: {gate0b_pass}")
assert gate0b_pass, "GATE 0b FAILED -- harness bug, stop and diagnose"

log("")
log("GATE 0: PASS (0a and 0b both exact, zero exceptions).")


# ---------------------------------------------------------------------------
# GATE 1: derive LAYER 1, LAYER 2, LAYER 3 -- exhaustive enumeration first,
# then attempt congruence-class fit.
# ---------------------------------------------------------------------------
log("")
log("=" * 78)
log("GATE 1 -- closed-form the layers")
log("=" * 78)

LAYER0 = set(layer0_members)  # first 30 members: 1,5,21,85,341,...
log(f"LAYER 0 (first 30 members): smallest 8 = {sorted(LAYER0)[:8]}")

# Which layer-0 members are ===0 mod 3? (those contribute NO predecessors)
log("")
log("LAYER 0 members mod 3 (determines which contribute to LAYER 1):")
for x in sorted(LAYER0)[:12]:
    log(f"  x={x:>7d}  x mod 3 = {x % 3}")

# ---- Enumerate LAYER 1 exhaustively within a census bound, via TWO
# independent methods, cross-checked against each other:
#  Method A (backward): for each t in LAYER 0, each admissible j (by t
#    mod 3), compute x=(t*2^j-1)/3, keep if x odd positive and < BOUND.
#  Method B (forward, ground truth): for every odd x < BOUND, check if
#    S(x) is in LAYER 0 (species closed-form test via is_one_step_species
#    on S(x) directly, since species membership is a closed-form
#    trajectory-free-from-S(x) test) -- confirm x in LAYER 1 iff caught
#    by method A.
BOUND = 2_000_000  # keep layer-1 census generous; layer sizes grow, so
                    # deeper layers use a separate smaller/targeted bound.

def species_test(t):
    """Is odd t itself a layer-0 (species) member? Closed form: t=(4^k-1)/3
    iff 3t+1 is a power of 2 with even exponent. Reuses is_one_step_species
    machinery: t is species iff S(t)==1 in one step... NO -- careful: layer-0
    IS the species (reaches 1 in ONE step), so "t in LAYER0" is EXACTLY
    is_one_step_species(t) when t>1, and t=1 is also layer-0 (k=... actually
    1 itself: is 1 = (4^k-1)/3 for k=0? spec says k>=1 giving x=1 at k=1:
    (4^1-1)/3 = 1. So x=1 IS species member k=1. is_one_step_species(1):
    n=3*1+1=4=2^2, power of two, j=2 even -> (True, 1). Consistent."""
    ok, k = is_one_step_species(t)
    return ok

# sanity: species_test agrees with LAYER0 set on the first 30 members
for x in LAYER0:
    assert species_test(x), f"species_test disagrees with LAYER0 on x={x}"

log("")
log(f"Enumerating LAYER 1 via backward construction from LAYER 0 members "
    f"(t < {BOUND} needed to keep predecessors x < {BOUND} in range;"
    f" using all 30 constructed layer-0 members as t-source, j up to 40):")

def backward_layer(prior_layer_members, bound, jmax=40):
    """Given the (finite, truncated) member list of the prior layer, compute
    all odd positive x < bound such that S(x) is in prior_layer_members, by
    direct backward construction x=(t*2^j-1)/3 over admissible j (by t mod 3)
    for each t in prior_layer_members. Returns a set of x values < bound.
    NOTE: this is only complete up to `bound` and up to the finite t-list
    given -- deeper/larger t's could in principle produce small x too for
    large j, but j*t grows, so for t already >= bound the smallest predecessor
    (smallest admissible j) alone may still be < bound; the finite t-list
    from LAYER 0's own truncation (30 members, largest ~4^30) makes this
    negligible for BOUND=2*10^6. Cross-checked against forward enumeration
    below regardless."""
    found = set()
    for t in prior_layer_members:
        if t % 3 == 0:
            continue  # no predecessors, ever
        start_j = 2 if t % 3 == 1 else 1  # even j's start at 2, odd at 1
        for j in range(start_j, jmax + 1, 2):
            num = t * (2 ** j) - 1
            if num % 3 != 0:
                continue
            x = num // 3
            if x <= 0 or x >= bound:
                continue
            if x % 2 == 1:
                found.add(x)
    return found

layer1_backward = backward_layer(LAYER0, BOUND, jmax=40)
log(f"  backward construction: {len(layer1_backward)} members < {BOUND}")

log("")
log(f"Cross-checking via FORWARD enumeration (ground truth): every odd x "
    f"< {BOUND}, test whether S(x) is a layer-0 (species) member:")

layer1_forward = set()
for x in range(1, BOUND, 2):
    sx = one_odd_step(x)
    if species_test(sx) and x not in LAYER0:
        # x's own single step lands on species -> x is layer-1 (unless x is
        # itself already layer-0, which we exclude since layers are meant to
        # be the NEW members added, matching "LAYER n = odd x such that
        # S(x) in LAYER(n-1)" -- note this does NOT exclude x that are
        # ALSO layer-0 by the spec's literal wording, so record both views)
        layer1_forward.add(x)

# Also compute the literal-spec version (no exclusion of layer-0 overlap)
layer1_forward_literal = set()
for x in range(1, BOUND, 2):
    sx = one_odd_step(x)
    if species_test(sx):
        layer1_forward_literal.add(x)

overlap_with_layer0 = layer1_forward_literal & LAYER0
log(f"  forward enumeration (literal spec, S(x) in LAYER0): "
    f"{len(layer1_forward_literal)} members < {BOUND}")
log(f"  of which also themselves LAYER 0 members (overlap): "
    f"{sorted(overlap_with_layer0)}")
log(f"  forward enumeration EXCLUDING layer-0 overlap (the 'new' members): "
    f"{len(layer1_forward)} members < {BOUND}")

match = (layer1_backward == layer1_forward)
log(f"  backward-construction set == forward-enumeration(excl. overlap) set: "
    f"{match}")
if not match:
    only_b = layer1_backward - layer1_forward
    only_f = layer1_forward - layer1_backward
    log(f"    ONLY in backward: {sorted(only_b)[:20]} (showing up to 20)")
    log(f"    ONLY in forward:  {sorted(only_f)[:20]} (showing up to 20)")

LAYER1 = layer1_forward_literal  # use the literal-spec forward set as ground truth
log(f"LAYER 1 (literal spec, includes any layer0 overlap) size < {BOUND}: "
    f"{len(LAYER1)}")
log(f"  smallest 15 members: {sorted(LAYER1)[:15]}")


# ---------------------------------------------------------------------------
# Fit congruence classes to LAYER 1: check mod 2,4,8,16,32,64 residues
# ---------------------------------------------------------------------------
def residues_mod(members, m):
    """Return sorted set of distinct residues mod m present in members."""
    return sorted(set(x % m for x in members))

def fit_report(members, label, moduli=(2,4,8,16,32,64,128,256,512,1024)):
    log(f"  congruence-class fit for {label} (n={len(members)} members):")
    prev_res = None
    for m in moduli:
        res = residues_mod(members, m)
        frac = len(res) / m
        log(f"    mod {m:5d}: {len(res)} distinct residues out of {m} "
            f"possible ({frac:.4f} of classes populated): {res if len(res)<=20 else str(res[:20])+' ...'}")

fit_report(LAYER1, "LAYER 1")

# Check specifically: is LAYER1 == a single class mod some power of 2, or a
# union of a SMALL number of classes mod 2^n? Test the natural guess x===3
# (mod 4) [since layer0 was x===1 mod 4] and other small guesses.
log("")
log("Targeted checks on LAYER 1:")
mod4_res = residues_mod(LAYER1, 4)
log(f"  LAYER1 mod 4 residues: {mod4_res}")
mod8_res = residues_mod(LAYER1, 8)
log(f"  LAYER1 mod 8 residues: {mod8_res}")
mod3_res = residues_mod(LAYER1, 3)
log(f"  LAYER1 mod 3 residues: {mod3_res}")


# ---------------------------------------------------------------------------
# LAYER 2: forward-enumerate (ground truth: S(S(x)) in LAYER0, i.e. two odd
# steps land on species) within a smaller bound (deeper layers are sparser
# per unit range near the bottom but the SMALLEST members can still be
# large, so we also do a backward construction pass to catch small members
# a plain forward-range scan might miss if the range is too small -- use
# backward construction as primary generator, forward scan as cross-check
# over the SAME bound).
# ---------------------------------------------------------------------------
log("")
log("=" * 78)
log("LAYER 2 -- odd x such that S(x) in LAYER 1")
log("=" * 78)

BOUND2 = 2_000_000

def species_after_n_steps(x, n, cap=None):
    """Forward ground truth: apply the odd-map n times to x, return True iff
    the n-th iterate lands in the species (layer 0), i.e. x is a member of
    LAYER (n-1) under the literal spec definition unrolled n times. cap is
    an optional extra safety iteration cap (unused here, n is small)."""
    cur = x
    for _ in range(n):
        cur = one_odd_step(cur)
    return species_test(cur)

layer2_forward = set()
for x in range(1, BOUND2, 2):
    if species_after_n_steps(x, 2):
        layer2_forward.add(x)

log(f"LAYER 2 forward enumeration (S(S(x)) in LAYER0), x < {BOUND2}: "
    f"{len(layer2_forward)} members")
log(f"  smallest 15: {sorted(layer2_forward)[:15]}")

# backward construction cross-check: predecessors of LAYER1 members (using
# the SAME finite LAYER1 set already enumerated < BOUND, as t-source)
layer2_backward = backward_layer(LAYER1, BOUND2, jmax=40)
log(f"LAYER 2 backward construction from (finite) LAYER1 set < {BOUND}, "
    f"result < {BOUND2}: {len(layer2_backward)} members")

match2 = (layer2_forward == layer2_backward)
log(f"  forward set == backward set: {match2}  "
    f"(mismatch expected ONLY if LAYER1's own truncation at {BOUND} "
    f"missed t-values needed to generate small LAYER2 members)")
if not match2:
    only_f2 = layer2_forward - layer2_backward
    only_b2 = layer2_backward - layer2_forward
    log(f"    ONLY in forward: {len(only_f2)} members, e.g. {sorted(only_f2)[:10]}")
    log(f"    ONLY in backward: {len(only_b2)} members, e.g. {sorted(only_b2)[:10]}")

LAYER2 = layer2_forward
fit_report(LAYER2, "LAYER 2")

mod4_res2 = residues_mod(LAYER2, 4)
mod8_res2 = residues_mod(LAYER2, 8)
mod16_res2 = residues_mod(LAYER2, 16)
log(f"  LAYER2 mod 4: {mod4_res2}")
log(f"  LAYER2 mod 8: {mod8_res2}")
log(f"  LAYER2 mod 16: {mod16_res2}")


# ---------------------------------------------------------------------------
# LAYER 3: same treatment, if tractable within the bound.
# ---------------------------------------------------------------------------
log("")
log("=" * 78)
log("LAYER 3 -- odd x such that S(x) in LAYER 2 (i.e. S^3(x) in LAYER0)")
log("=" * 78)

BOUND3 = 2_000_000

layer3_forward = set()
for x in range(1, BOUND3, 2):
    if species_after_n_steps(x, 3):
        layer3_forward.add(x)

log(f"LAYER 3 forward enumeration (S^3(x) in LAYER0), x < {BOUND3}: "
    f"{len(layer3_forward)} members")
log(f"  smallest 15: {sorted(layer3_forward)[:15]}")

LAYER3 = layer3_forward
fit_report(LAYER3, "LAYER 3")

mod4_res3 = residues_mod(LAYER3, 4)
mod8_res3 = residues_mod(LAYER3, 8)
mod16_res3 = residues_mod(LAYER3, 16)
mod32_res3 = residues_mod(LAYER3, 32)
log(f"  LAYER3 mod 4: {mod4_res3}")
log(f"  LAYER3 mod 8: {mod8_res3}")
log(f"  LAYER3 mod 16: {mod16_res3}")
log(f"  LAYER3 mod 32: {mod32_res3}")


# ---------------------------------------------------------------------------
# Modulus-growth summary: does the "distinct residues populated" count grow
# as a clean power of 2 per layer, or explode?
# ---------------------------------------------------------------------------
log("")
log("=" * 78)
log("MODULUS / CLASS-COUNT GROWTH SUMMARY")
log("=" * 78)
log(f"LAYER 0 (species): closed form x=(4^k-1)/3 -- a SINGLE residue class "
    f"mod 4^k for a GIVEN k (x===1 mod4, but more precisely the k-th member "
    f"is the unique solution mod 4^k -- it is a discrete recurrence, not a "
    f"fixed-modulus class covering a whole layer at once).")
for label, members in [("LAYER 1", LAYER1), ("LAYER 2", LAYER2), ("LAYER 3", LAYER3)]:
    for m in (4, 8, 16, 32, 64, 128, 256):
        res = residues_mod(members, m)
        log(f"  {label}: mod {m:4d} -> {len(res):4d} distinct residues "
            f"({len(res)/m:.4f} of all classes)")

log("")
log("Gate 0/1 script complete.")

with open("gate0_gate1_results.txt", "w") as f:
    f.write("\n".join(OUT) + "\n")
