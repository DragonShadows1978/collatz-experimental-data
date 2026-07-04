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

## 4. Next concrete step

Build the finite mean-payoff game for the golden 8-block: states
(δ clipped at a working ceiling, forced parity, ρ mod 9), letters from
the period-8 mechanical word, exact value iteration. The output must
be: value per period = 3, and the phase profile reproducing
⌊(3m+1)/8⌋ row-for-row. Machine-checkable; Sonnet-shaped once this
note's game definition is frozen; the notes above are the freeze.
