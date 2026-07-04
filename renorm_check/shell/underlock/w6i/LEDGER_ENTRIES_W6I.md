### W6I-I1 — Potential-function fitting (`w6i/i1_potential_fit.py`)

**Machinery validated first:** `backward_predecessor_mod` (the mod-3^k
3-lift backward residue map, reimplemented locally per the copy-don't-
edit rule) cross-checked against `w6e/engine.backward_predecessor_exact`
(genuine unbounded-integer arithmetic) on 10 explicit steps of a chain
from rho=1 — 10/10 PASS.

**FINDING (more fundamental than the registered prediction): no Phi>=0
with Phi(1-ray)=0 exists on this state graph — a structural non-
existence, not merely a lift-consistency failure.** Built the full
one-step cost graph on (delta, rho mod 3^k), delta<=8, k=4..7, edge
cost=a-2, uncapped backward exponent menu (sensitivity-checked stable
against a much larger cap, 0/2187 states differ at k=5). Bellman-Ford
from the ray (Phi(s) = min cost to reach the ray) converges cleanly (no
negative cycle at any k, 11-12 iterations) but yields Phi(delta,1) =
delta - 8 for delta<8 (i.e. NEGATIVE, not 0) at every k tested —
`ray_phi_all_zero=False`, `phi_nonneg_holds=False`, `loop_equality_ok=
False` uniformly across k=4..7. Mechanism, traced and confirmed: at
fixed k, the mod-3 class alone (which determines forced parity) cannot
distinguish the TRUE ray rho=1 from other residues rho' == 1 (mod 3)
but rho' != 1 (mod 3^k) — a cost-0 (a=2) edge from a ray state (delta,1)
legitimately lands on such an rho' (e.g. k=4: rho=28 is class-1 but
28 != 1 mod 81), and those states are cheaper to reach the BFS
"terminal" from, back-propagating negative values onto the ray itself.
This is precisely the sec 5a lift-cascade phenomenon, but it breaks the
potential-function program at a MORE BASIC level than the registered
prediction anticipated (that prediction assumed a finite Phi>=0 exists
at each fixed k and only asked about lift-consistency across k;
instead, Phi>=0 itself fails to exist, at every k, for the same
underlying reason).

**Bonus (max-Phi / "deepest hole"): STABLE, not growing — but this
finding is now subsumed by the non-existence result above** (max_phi=0
identically at k=4..7, min_phi=-8=-delta_max identically; the "depth"
never grows past the delta_max=8 cap because that cap, not k, sets the
scale here).

**Ironic technical footnote: the k -> k+1 PROJECTION check that the
prediction anchored on (part iii) is trivially, vacuously satisfied**
(0 multi-valued states, 0 mismatches across all three (k,k+1) pairs
tested) — but this is a red herring given (i)/(ii) fail outright; a
projection of an ill-posed Phi being self-consistent does not rescue
the program.

**GATE VERDICT vs registered predictions:**
- "Finite Phi exists at each k but fails lift-consistency" (60%): PARTIAL
  MISS — Phi is finite (as required, no negative cycle) but is NOT >=0
  with Phi(ray)=0, which is a stronger and earlier failure than
  "lift-consistency" addresses; the literal lift-consistency check
  itself came back TRUE (misleadingly), so the registered framing
  doesn't cleanly apply.
- "If lift-consistent, one-page dual proof, report Phi table and stop
  early": the literal lift-consistency numbers say yes, but the
  headline non-existence finding means this branch is a false
  positive, not a real early-stop condition — reported, not acted on.
- "Max-Phi grows with k" (55%): MISS — stable at 0/-8 across k=4..7 (but
  see caveat above: the deepest hole is set by delta_max, not k, here).

**PROOF-SHAPE VERDICT: DUAL-PROOF NOT VIABLE**, and for a more
fundamental reason (Phi>=0 does not exist as specified, not merely
"exists but doesn't project") than the round anticipated.

**Decisive tables:** `w6i/i1_phi_summary.csv` (4 rows, k=4..7),
`w6i/i1_lift_consistency.csv` (3 rows).

---

### W6I-I2 — Ostrowski re-coordinates for the follower-set test (`w6i/i2_ostrowski_follower.py`)

**Machinery validated first:** Ostrowski digit reconstruction
(greedy expansion w.r.t. CF convergent denominators of alpha=log2(3))
hand-checked on 10 explicit n (0,1,2,3,5,12,13,41,53,100) — exact
reconstruction + admissibility bound (d_i <= a_{i+1}) — 10/10 PASS.
**Bug caught and fixed during development:** an early draft seeded the
convergent-denominator recurrence with the NUMERATOR convention
(1,0) instead of the DENOMINATOR convention (0,1), silently computing
the p-sequence (1,2,3,8,19,...) instead of q (1,1,2,5,12,41,53,...) —
caught by cross-checking against SYNTHESIS.md's own stated 22/53
convergent and beatty/continued_fraction_analysis.py's verified
convergents(), fixed before any measurement was trusted.

**FINDING: follower sets FAIL to stabilize in Ostrowski coordinates
either.** Retried the h3->h4-type stabilization test (raw trit-space
version FAILED unambiguously per e1_stabilization.py/ledger) reindexed
via Ostrowski-block horizons (jumps of size q_1=1, q_2=2 trits, the
reachable range within the M_DENSE_MAX=13 ceiling this repo's dense-
enumeration guard allows) instead of unit-trit steps. Same (delta,
rho mod 3^m) automaton, same real Sturmian credit word, same C=12,
delta in {0,1,2}, m0 in {8,9,10} as the raw test, for direct
comparability. Type counts at j1 (levels {m0+1}) vs j2 (levels
{m0+1,m0+2}): grows by roughly 10-13x at every one of the 9 (delta,m0)
points (e.g. delta=2,m0=9: 7->78), qualitatively the SAME failure mode
as raw trit-space's roughly-2x-per-horizon growth (e.g. delta=2,m0=9:
492->1282) — no stabilization signal recovered by the coordinate
change, at this (necessarily narrow, 2-horizon) scope.

**Honest wall:** the order's full scope (m<=13, matching e1_stabilization
.py's own dense-enumeration ceiling) only permits testing 2 Ostrowski
horizons (jump sizes q_1=1, q_2=2) at m0=8,9,10 before hitting the
level-13 ceiling — an initial attempt at M_DENSE_MAX=15 (3 horizons,
jumps 1,2,5) TIMED OUT at 300s wall-clock (RSS stayed safe at ~3GB;
this was a compute-time wall from the naive per-(d,a) Python forward
pass at m=15's 9x-larger state count, not a memory wall) and was
descoped back to M_DENSE_MAX=13 to stay tractable — reported as a
genuine scope constraint, not a silent reduction.

**GATE VERDICT vs registered prediction (follower sets ALSO fail to
stabilize in Ostrowski coordinates, 55% — "the prediction I most want
to lose"): HIT.** Ostrowski re-coordinatization does not rescue the
sofic/transducer route at the tested scope; S-adic viability remains
unconfirmed here (though the 2-horizon scope is admittedly thin
evidence next to the raw test's fuller 2-5 horizon sweep).

**PROOF-SHAPE VERDICT: S-ADIC NOT VIABLE** (at this scope; genuinely
narrower evidence than I'd like, flagged honestly).

**Decisive table:** `w6i/i2_ostrowski_follower_counts.csv` (9 rows).

---

### W6I-I3 — Convergent-locking harness (`w6i/i3_convergent_locking.py`)

**Machinery validated first:** 4 exact-arithmetic strategies (quadratic-
surd isqrt, integer cube-root binary search, log2(3) bit_length exact
method cross-checked against a certified-precision mpmath method, and
a Liouville-ish alpha's exact Fraction-convergent method cross-checked
against a much-higher-index reference convergent) — 14 hand-checked
(alpha, k) cases, 14/14 PASS, including k=300 boundary cases for every
family. **Modeling correction caught before trusting results:** an
early draft computed CF/convergents of alpha itself and used a fixed
ceiling=2 in the L(w)=max sum(2-c_j) discrepancy functional; this is
WRONG for alpha not in (1,2) (sqrt5~2.236 and sqrt7~2.646 have credit
alphabet {2,3}, not {1,2}) and, more importantly, the CORRECT
convergents to test locking against are convergents of beta=ceiling-
alpha, NOT of alpha itself (verified CF(sqrt5)=[2,4,4,...] vs
CF(3-sqrt5)=[0,1,3,4,...] are genuinely different) — both fixed before
trusting any match-rate number (the alpha-CF/ceiling=2 draft gave
near-zero matches, 0-6/299, across the board; the beta-CF/per-family-
ceiling fix raised this to 8-191/299, a large, non-cosmetic effect).

**FINDING: the lock-until-next-denominator rule is a clear MISS.**
For 10 irrationals (log2(3), sqrt2, sqrt3, sqrt5, sqrt7, phi, cbrt(2),
pi-3, e-2, a Liouville-ish alpha with a designed CF entry of 10^6),
computed L(m) of the true word exactly (no floats near any floor) for
m=2..300 and matched against each family's leading beta-convergents'
closed-form laws (+1 form ceil(beta*m-1) and -1 form floor((p*m-1)/q)).
Only **24/550 transfer points** (schedule-segment boundaries, summed
across all 10 families) land within +-1 of a tabulated convergent
denominator — roughly 4%, nowhere near the 70%-confidence prediction.
Per-family match rates against ANY tabulated convergent's law at all
range from 3% (pi-3) to 64% (sqrt3); most families show NOT a clean
"convergent A owns m=[a,b], then convergent B takes over and stays"
handoff but a FRAGMENTED, oscillating pattern — the same low-q
convergent (e.g. phi's 1/2) recurring intermittently across widely
separated, non-contiguous m even after "newer" convergents have
started appearing, rather than being cleanly retired. The Liouville-
ish alpha's huge injected CF term (a_7=10^6, convergent denominator
~1.3e7) never becomes relevant within m<=300 (as expected — that
convergent's denominator dwarfs the tested range) so the "one
convergent owns a huge range" stress test is UNTESTED at this m-scope,
not confirmed or refuted; within reach, its locking behavior looks
like the other small-CF-entry families (fragmented, low-q).

**GATE VERDICT vs registered prediction (lock transfers at exactly
next convergent's denominator, refined by +-1 boundary cases, 70%):
MISS**, clearly and by a wide margin (4% hit rate on transfer points),
across every family, not just the Liouville stress case (which is
inconclusive, not a counterexample, at this m-range).

**PROOF-SHAPE VERDICT: RULE MUDDLED — the simple lock-until-denominator
picture does not describe the data; the true locking structure (to the
extent one exists) is more fragmented than a clean handoff schedule.**

**Decisive tables:** `w6i/i3_locking_summary.csv` (10 rows),
`w6i/i3_locking_<family>.csv` (299 rows each, 10 families).

---

### W6I-I4 — Lift-cascade effective branching (`w6i/i4_lift_cascade.py`, exploratory, UNGATED)

**Machinery validated first:** the "3 same-parity menu offsets give 3
distinct mod-3 successor classes, offset+6 repeats offset+0's class"
claim (DERIVATION_NOTES sec 1's mod-9 steering) hand-checked on 5
explicit steps from rho=1 — 5/5 PASS.

**Result: 19/20 tested single-step lift perturbations (offset+2 vs the
S0-greedy baseline) are "decisive" within the 20-step window, ALL at
delay=1 (the very next step).** Traced, for each backward step j=0..19
from rho==1 (mod 3^8), whether a minimal alternative lift (a_min+2
instead of a_min) at step j — followed by greedy S0 continuation —
changes the forced-parity sequence at some later step, and if so, how
many steps later.

**Honest scope caveat (flagged, not silently reported as a stronger
finding): this near-universal delay=1 is close to a TAUTOLOGY here,
not evidence about sec 5a's actual cascade claim.** The baseline chain
from rho=1 is the trivial all-2s fixed-point loop (never leaves the
ray), so perturbing step j's exponent immediately produces a
generically different residue integer, which generically differs mod
3 (hence forced parity) at the very next step too — this measures "does
perturbing the residue at all change the immediately-following mod-3
class" (near-tautologically yes on a degenerate baseline), NOT sec 5a's
actual claim, which concerns a SPECIFIC high trit (written at step j,
trit m-j-1) taking ~(m-j) further steps before it becomes the low-order
trit governing forced parity. Testing that claim properly needs a
non-degenerate baseline (one that actually visits multiple residue
classes) and tracking one specific trit's delayed influence, not
perturbed-vs-baseline forced-parity divergence on a fixed point.
Reported honestly as a narrower measurement than the order's framing
suggested going in, not reframed as confirming or refuting sec 5a.

**Deliverable (per the order, ungated, no verdict required):**
histogram = {delay=1: 19 occurrences, no-divergence-in-window: 1 (the
final step j=19, which has no room left in the 20-step window to
observe any later step — not a substantive finding)}. Effective
branching at this (degenerate) baseline and offset: 19/20 "decisive,"
1/20 untestable.

**Decisive tables:** `w6i/i4_influence_delays.csv` (20 rows),
`w6i/i4_delay_histogram.csv`.
