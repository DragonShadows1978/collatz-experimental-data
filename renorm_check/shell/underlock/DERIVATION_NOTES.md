# W6D Derivation Notes — The Depth Minimax (Fable, started 2026-07-04)

Working notes for P1 (exact periodic law ⌊(pm+1)/q⌋) and P3 (true-word
bonus schedule). Ground truth: shell/underlock/ tables (28/28 periodic,
the ±1 bonus structure, the real system's mirror form 11/11).

## 1. Reduction to a one-dimensional game (done)

Coordinates: ceiling-distance δ = C − d, wide corridor (floor ignored;
justified for D(m) by the margin rule in all measurements). Backward
step from depth δ at credit letter c: exponent menu a ∈ [1, δ + c],
predecessor depth δ_prev = δ + c − a. Residue side (F6): the parity of
a is FORCED by the current residue's class mod 3 (class 1 ⟹ even,
class 2 ⟹ odd; class 0 = no legal move). The three same-parity menu
entries {a, a+2, a+4} land the predecessor residue in the three
distinct classes mod 3 (mod-9 steering), so the walker chooses its
NEXT forced parity when the menu is rich enough, at exponent cost
0 / 2 / 4 above parity-minimal.

Kill condition (unique): δ = 0, support letter (c = 1), even parity
forced — the even menu {2, 4, …} ∩ [1, 1] is empty. Odd-forced steps
can never kill (a = 1 always legal).

Trit-locality: only the last m backward steps from the terminal carry
residue constraints; the remaining prefix is a free deficit walk,
always satisfiable (choose a = c). Hence D(m) is exactly the value of
the m-step constrained game.

## 2. The conservation identity (done)

Depth after k backward steps: δ_k = δ_T − Σ_{j≤k} (a_j − c_j).
Feasibility (δ_k ≥ 0 for all k) ⟺ δ_T ≥ max_k Σ_{j≤k} (a_j − c_j).

**D(m) = min over admissible exponent processes of
max_k Σ_{j≤k} (a_j − c_j).**

"Admissible" = parity forced by the residue trajectory, lifts free,
steering as in §1. This is an integer minimax of the exponent process
against the credit word — the capacity law is its value.

Drift: Σc over an m-window = ⌊αm⌋ + O(1) (credits sum telescopes);
the measured laws all have slope β = 2 − α, which forces
Σa = 2m + O(1) at optimum — optimal constrained play realizes the
generic 2-adic valuation mean E[a] = 2 (P(a = k) = 2^−k for the free
backward chain; the classic 3x+1 heuristic constant appears as the
game value). NOTE: this is currently read OFF the data through the
identity, not derived; deriving Σa = 2m + O(1) for optimal play is
obligation P1a below.

## 3. What remains

- **P1a (the value):** prove the m-step game value has drift exactly
  E[a] = 2 — i.e., neither player can move the mean: the walker
  cannot cheapen below 2 (residue classes punish greedy a = p₀ play
  through forced-even runs), the word cannot extract more (steering
  caps the damage). Candidate route: potential/martingale argument on
  (δ, ρ mod 9) with the explicit steering table; the periodic case is
  a finite mean-payoff game on ≤ 18 states per letter — SOLVABLE
  EXACTLY by value iteration, mechanically, for the 8-block. Do the
  8-block first; the answer should be value = p per period = 3.
- **P1b (the constant):** the max-partial-sum boundary term. For a
  periodic word, which cyclic phase of the block maximizes the
  running sum determines the +1 in ⌊(pm+1)/q⌋ (Raney/cycle-lemma
  structure). The over/under mirror (real system's −1 form) should
  fall out of the phase of the worst peak relative to the window's
  end anchor.
- **P3′ (the bonus):** with P1a/P1b, the true-word law is the same
  minimax over the Sturmian window; balance (each length-ℓ factor
  carries ⌊ℓβ⌋ or ⌈ℓβ⌉ supports) bounds the value difference to
  {0, +1} against the convergent word — matching the measured bonus —
  and the bonus schedule = which windows carry the extra support,
  PROVIDED the phase-absorption question (the honest gap in W6D-M) is
  settled by the P1b analysis.
- **Phase pinning for F5:** the real measurement at m = 359 runs
  371 = 7·53 steps; the constrained window is end-anchored (letters
  ~12..370). The exact-counting argument (149 vs 150 supports) was
  computed on the 0..358 window — REDO on the end-anchored window
  with the phase convention from P1b before any F5 claim. The
  correction letter at 358 is inside either window; only the boundary
  constant can differ.

## 4. Next concrete step (SUPERSEDED by §5 — kept for the record)

Build the finite mean-payoff game for the golden 8-block: states
(δ clipped at a working ceiling, forced parity, ρ mod 9), letters from
the period-8 mechanical word, exact value iteration. The output must
be: value per period = 3, and the phase profile reproducing
⌊(3m+1)/8⌋ row-for-row.

## 5. Session-2 findings (Fable, 2026-07-04)

**5a. The (δ, parity, ρ mod 9) abstraction LEAKS — the game is not
finite-state in those coordinates.** The mod-9 steering table needs
ρ mod 27 to predict the successor's mod-9 class, mod 81 for the next,
and so on: nothing closes at any fixed level. Worse, the lift chosen
at backward step j sits at trit (m−j−1) and cascades down one trit
per step, reaching mod-9 relevance only ~(m−j) steps later — lift
choices are long-range investments, not local dice. A finite
mean-payoff game in these coordinates would be an APPROXIMATION, and
this program does not prove theorems from approximations. Value
iteration on the exact game is just dense enumeration — which is what
the measured tables already are. The derivation must be theory:
matching upper and lower BOUNDS.

**5b. The keystone identity (exact, one line of algebra).** Composing
m forward steps: 2^{Σa}·ρ_end = 3^m·ρ_start + S with
S = Σ_{i=0}^{m−1} 3^{m−1−i}·2^{A_i}, A_i = a_1+…+a_i (the standard
cycle-equation composition). With the terminal anchor ρ_end = 1:

**2^{Σa} ≡ S (mod 3^m).**

This is the SAME identity as the cycle equation's offset arithmetic —
the capacity law and the +1-offset cycle rigidity are one identity
read in two directions. It is the natural engine for the LOWER bound:
Σa (hence the depth budget, via §2's conservation) cannot be small,
because 2^{Σa} must hit the residue class of a structured sum S whose
terms are pinned by the exponent pattern itself. Quantifying "cannot
be small" into Σ_{j≤k}(a_j − c_j) ≥ ⌊(pk+1)/q⌋-type partial-sum
bounds is the remaining number theory — Baker-free, purely 3-adic,
because the congruence is exact.

**5c. Bound-pair program (replaces §4):**
- UPPER: exhibit an explicit walker strategy achieving max partial
  sum ≤ ⌊(pm+1)/q⌋ for the periodic word (constructive; the strategy
  from the steering table with lift pre-commitment; verify
  mechanically against all 28 ground-truth rows first, then prove).
- LOWER: from 5b, show any admissible chain from ρ_end = 1 has
  max_k Σ_{j≤k}(a_j − c_j) ≥ ⌊(pm+1)/q⌋. Candidate route: reduce
  2^{Σa} ≡ S mod 3^m per prefix — the identity holds at every
  intermediate precision (project mod 3^k for the last k steps), so
  each prefix inherits its own rigidity; the partial-sum bound should
  fall out prefix-by-prefix.
The over/under mirror and the true-word bonus (P1b/P3′) then ride on
which side of the congruence the word's credit sum sits — the same
±1 that decides F5.

## 6. Session-3 findings (W6E mechanical phase, 2026-07-04)

**6a. UPPER BOUND IS THE TRIVIAL LOOP.** From ρ_end = 1, greedy plays
a = 2 forever and stays at ρ = 1 (backward image of 4-2-1). Matches D
exactly on 39/39 ground-truth rows (28 periodic + 11 real-mirror).
So the constructive object for the upper bound is NOT a clever
steering strategy — it is the fixed point, and
D_per(m) ≤ max_k Σ_{j≤k}(2 − c_j), pure mechanical-word discrepancy.
Remaining upper-side work: the offset/anchoring bookkeeping that
turns max_k(2k − Σc) into ⌊(pm+1)/q⌋ and the mirror −1 form
(elementary; the E2 lesson says be exact about end-anchoring).

**6b. ZERO-SLACK ENVELOPE.** Searched-optimal chains bind the prefix
bound at EVERY k (16 chains, keystone verified, no violations). The
lower bound must therefore be an equality-grade induction: each
prefix inherits full rigidity, no slack to give away. Route stands:
project 2^{Σa} ≡ S (mod 3^m) to mod 3^k per suffix; show any
deviation from the loop (harvesting a = 1 at class-2 positions)
costs at least what it saves in max-partial-sum terms. The lift
cascade (§5a) is exclusively THIS side's terrain now.

**6c. E2 ANCHORING CORRECTION — F5 conditional flips to 358.** The
149-vs-150 support differential at m = 359 was a start-anchoring
artifact; end-anchored (the real measurement's frame) both words
count 149. Under the support-cost mechanism the prediction becomes
D_true = D_per at m = 359 → edge = 358, the Architect's formula
exact. §3 "Phase pinning for F5" obligation: DISCHARGED (answer:
differential does not survive). Fable's F5 lean: 358 at ~60/40,
decisive instrument = this derivation's boundary constant.

## 7. Session-4 findings (W6F optimal-set census, 2026-07-04)

**7a. THE LOOP IS STRICTLY UNIQUE.** Exhaustive enumeration
(independently validated), m = 2..13 both families: n_optimal = 1 on
all 24 rows, and it is the all-2s chain. The lower bound obligation
is therefore a STRICT statement: every admissible non-loop chain has
max partial sum ≥ D + 1. Nothing ties. Rigidity is total.

**7b. Tax law (measured).** Min tax of a=1-containing chains: +1 on
8/9 evaluable rows; +2 at sqrt2 m=8 (only compound (1,3,1)+(3,4)
excursions exist there; the +1 bucket provably empty). Never 0.
Local shape to formalize: exiting ρ = 1 costs a − 2 ≥ +2 upfront
(even-forced menu at class 1); measured recoveries never refund more
than net −1. Candidate lemma: EXIT COST 2, MAX REFUND 1 — strict tax
≥ 1 for any excursion, composable across disjoint excursions.

**7c. P1b sharpened: the ±1 constant is a SIDE function.** F3:
end-anchored D = the +1 law 12/12 both families; start-anchoring is
an additive ≈+1 shift (vanishing at word-aligned m — golden m = 5,
8, 13, Fibonacci flush), and the −1-mirror "matches" under any
anchoring are boundary-residue coincidences. So the real system's
−1 mirror form must be carried by 22/53 being the OVER-side
convergent — derive the constant from the side of the convergent,
with anchoring as a separate, now-measured shift. This is the
constant that decides F5.

## 8. Session-5 findings (W6G break-it + the F5 computation, 2026-07-04)

**8a. UNIVERSAL DISCREPANCY (empirical theorem, exhaustive to
m=10).** For EVERY word w ∈ {1,2}^m: D(w) = L(w) = max_k Σ(2 − c_j),
loop strictly unique — 2,044/2,044. The entire derivation now
reduces to ONE lemma: **loop optimality/uniqueness** (any excursion
off ρ≡1 pays exit ≥ +2, refunds ≤ +1, strict tax ≥ 1). Everything
else is classical word combinatorics.

**8b. Two fixed rays = the two trivial cycles of 3x+1 on ℤ.**
ρ≡+1: a=2 forever, cost 2/step (positive 4-2-1 loop shadow).
ρ≡−1: a=1 forever, cost 1/step ((2(−1)−1)/3 = −1; negative −1-loop
shadow) — the CHEAP ray, discovered when the h(r) ≥ 0 conjecture
broke (80/144 anchors easier than 1). The real problem's terminal
is the EXPENSIVE ray; positivity forces it. Lower-bound lemma
restated with the right geometry: among chains anchored at ρ_end=1,
the +1-ray is optimal BECAUSE the −1-ray is unreachable-without-
overpaying from anchor 1 (excursions toward the cheap ray cost more
than they harvest before returning — this is what "exit 2, refund
≤ 1" must actually prove).

**8c. F5 COMPUTED (conditional on 8a's lemma): edge = 358.** In the
physical frame (C=148 run = 371 = 7·53 steps, window end ≡ 52 mod
53; frame validated on C=1..5 edges + 11 ground-truth rows):
L(358) = 148, L(359) = 149, both anchorings agree at 359. Shadow-
depth sweep: the rational form ⌊53(C+1)/22⌋ is exact at ALL seven
catalogued divergence points through C=275 — the corridor's 53-
quantized run lengths phase-lock every decisive window to the
convergent grid; the frame carries the rationality. Open cheap
check: mid-range-C run-length rule vs archived corridor step counts.

## 9. Session-6 findings (W6I proof-shape recon, 2026-07-04)

Three doors closed: (i) state-potential dual NOT viable in raw
(δ, ρ mod 3^k) coordinates — Φ boundary condition unposable, cost-0
leakage off-ray = the §5a cascade as potential leakage (smarter
duals via keystone certificates NOT excluded, merely unfound);
(ii) Ostrowski/S-adic follower sets grow 10-13×/horizon — sofic
route dead in both coordinate systems; (iii) no clean convergent-
locking schedule (ownership fragments/oscillates; and the relevant
convergents are those of β = ceiling − α, per-family ceiling —
banked modeling lesson). CONSEQUENCE: the keystone prefix-rigidity
route (§5b, §8) is the only live analytical path. All further proof
effort goes at 2^Σa ≡ S (mod 3^m) directly: excursion tax via the
congruence, composability, then the ±1 boundary term.

## 10. Session-7 findings (W6H lemma core, 2026-07-04)

**10a. Interior/boundary decomposition of the lemma.** Exact-return
excursions (ρ≡1 mod 3^{ℓ+2}) up to length 8 cost ≥ 27 — the
congruence makes true return brutally expensive. The measured +1
minimum taxes (F2) come from WINDOW-END deviations where
trit-locality shrinks required return precision. Proof shape:
(i) interior rigidity — cheap and provable from the order-gap
(ord(2, 3^k) = 2·3^{k−1} dwarfs the feasible Σa window, pinning σ);
(ii) boundary term — finite arithmetic at the window end, the same
±1 that decides each family's constant. W6J measures the
return-precision cost curve to quantify (i)/(ii)'s crossover.

**10b. Universality's boundary = the loop's own rate.** D = L
requires loop increments 2 − c ≥ 0 (alphabet ≤ 2); letters ≥ 3
engage the corridor CEILING and break the identity both directions
(H3, verified by hand on "31"). The real word ({1,2}, α < 2) is
intrinsically inside the safe region. Conjecture to prove with the
lemma: D = L ⟺ min_k g_loop(k) ≥ 0.

**10c. Cheap-ray confirmation.** D(anchor ≡ −1 mod 3^m) = 0 exactly
(18/18) for min-letter-≥1 words — the negative trivial cycle is the
game's zero-cost seat, as §8b predicted. Two-ray D(r) model needs an
exit-cost term (repair queued).

**10d. Frame rule receipt-complete.** M_edge(C) = ⌊53(C+1)/22⌋
exact at C = 3..50 dense (48 archived countdown ladders) + both
53-boundary crossings. Combined with W6G: the formula is exact
everywhere it has ever been measured.

## 11. Session-8 findings (W6K convention pinning, 2026-07-04)

**11a. UNIVERSALITY IS TOTAL (canonical instruments).** D_free(w) =
max_k Σ(2−c_j) for every word over {1,2}, {0,1,2}, {1,2,3},
{0,1,2,3} — the H3 "alphabet boundary" was entirely an order bug
(census engine consumed reversed words; pinned to
f1_engine_ext.py:101-106/254-255). §10b's ceiling mechanism:
REFUTED outright (K3, both variants). The proof target is now
word-independent with no scope fence: the ceiling-free game IS the
discrepancy functional. (Ceiling-ON variant differs on 39% of
c≥3 words — irrelevant to the real word's {1,2} letters; noted for
theoretical completeness only.)

**11b. Interior tax curve (corrected, trustworthy):**
min excursion cost vs required return precision t:
[1,2,5,5,7,7,15,19,22,27], t=1..10, ~2.7/trit with plateaus at
(3,4) and (5,6). Per-trit tax + J3's order-gap pinning + K2's
monotonicity = the quantitative skeleton of the interior-rigidity
induction. Open derivation questions: why plateaus of width 2
(mod-9 steering granularity?); the exact per-trit increment law.

**11c. Proof program, final shape:** (P-I) universal loop
optimality — prove D_free = L for arbitrary credit words (the
keystone/order-gap route; word-independence suggests the proof
never needs word structure, only the residue game); (P-II) the
interior tax law (per-trit cost of return fidelity); (P-III) the
window-end boundary term (family constants, F5's ±1). All three
now have certified empirical tables to prove INTO.

## 12. Session-9 findings (W6L, 2026-07-04 night) — the strategy pivot

**12a. Composition is dead; the argument must be global.** L4:
excursion taxes are never additive (0/246; super-additive +5..+67).
The exact mechanism is the derivation's most important new fact:
a pinned letter-block admits entry from exactly ONE class mod
3^len, unlock exponents spaced ord(2, 3^len) — the order gap
appears as BOTH the global Σa-pinning (J3) and the local coupling
that forbids cut-and-paste. So P-I/P-II merge into a single global
statement: over the whole m-window, the congruence 2^Σa ≡ S
(mod 3^m) + the order gap force max partial sum ≥ L(w). No
excursion decomposition exists or is needed.

**12b. Curve of record (exact ladder, len ≤ 14):**
t=1..12 → [1,2,3,5,7,7,11,12,12,16,21,21], ~1.75-2.5/trit,
plateaus (5,6),(8,9),(11,12) = single chains serving both t's.
Supersedes §11b's numbers (H1's 27 was a t=7 event mislabeled
t=10 — architect-replayed). Increment sequence
[1,1,2,2,0,4,1,0,4,5,0] awaits a law; candidate: Ostrowski/steering
granularity, unproven.

**12c. Generic anchors are ray-free (83.6%), the two-ray model
underpredicts (junction pays the 12a coupling), no third invariant
structure exists mod 27/81. The anchor-1 problem is special —
which is fine: it is the only anchor the real corridor has.**

**12d. Proof obligation, final form (replaces the bound-pair
assembly): ONE lemma — for every word w and every admissible chain
from ρ_end = 1 over the m-window, max_k Σ(a_j − c_j) ≥ L(w), with
equality iff the chain is the loop. Route: prefix-projected
keystone + order gap, argued over the whole window. All supporting
tables now exist and are certified: pinning (J3), tax curve (12b),
uniqueness (L1), coupling (12a).**

## 13. Session-10 findings (W6M, 2026-07-04 night)

**13a. THE FLOOR-POINT LAW (empirical, exceptionless): at the
loop's binding prefix k* = argmax g_loop, every admissible chain
satisfies g(k*) ≥ g_loop(k*)** — 519/519 within L+1, 442 words.
This is the global argument's anchor: prove this single-prefix
inequality from the prefix-projected keystone at k*, and strict
uniqueness + the +1 follow from equality analysis at one point.
Candidate mechanism (untested): at prefix k*, the congruence class
of any chain that stayed cheaper than the loop is forced off the
residue set that the remaining window can absorb — check whether
the mod-3^{k*} constraint ALONE reproduces the floor (next round).

**13b. Strictness is departure-independent (f(j) ≥ 1 always), but
NOT monotone in j — flat ceiling with sparse single-prefix
undercuts to f=1. The undercut positions are the boundary term
showing through; fingerprint them against three-distance/correction
structure.**

**13c. Tax curve status: t ≤ 10 solid; t ≥ 11 length-capped upper
envelopes (21 → 19 at len 15; convergence open). t=13: 31, t=14: 32
(len ≤ 14). True asymptotic per-trit rate: OPEN — do not quote
2.5/trit as final.**

## 14. Session-11: THE ONE-POINT LEMMA (W6N, 2026-07-04 night)

**14a. Lemma (empirical, 40/40 + N1's 2,956-chain floor + architect
hand-check): for every word w with binding prefix k*, every
parity-legal k*-step backward walk from ρ = 1 satisfies
g(k*) ≥ g_loop(k*) = L(w) — from the mod-3^k* constraints ALONE.**
Since max_k g(k) ≥ g(k*) for any chain, D ≥ L follows immediately;
with the loop's upper bound, D = L; equality analysis at k* gives
uniqueness. THIS is the single statement left to prove. It is
finite per (k*, prefix-word), purely 3-adic, and the order-gap
(ord(2, 3^k) = 2·3^{k-1}) is the natural engine.

**14b. Boundary fingerprint: dips (f = 1 undercuts) are
support-adjacent (9/9 within 1 step of a support letter).**

**14c. Tax curve (converged cells): t=11,12,13 → 19; t=10 ≤ 15
open; t=14 ∈ [25, 32]. Four-trit plateau witness lands ≡ 1 mod
3^13; +6 cliff after. Shape = flats + cliffs; suspect Ostrowski
scales. METHOD LAW: consecutive-length agreement is NOT a
convergence certificate (a width-4 plateau broke at len 18).**
