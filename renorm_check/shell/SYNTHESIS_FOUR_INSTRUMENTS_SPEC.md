# Cross-Instrument Synthesis — do four Collatz measures describe one object? (spec & mission)

**Origin:** David Perry, 2026-07-05. "Combine the backward basin (not
novel) with the Death Shell, Spectral Radius, and Corridor work."

**Framing (corrected by pre-check — READ THIS).** The four instruments
do NOT report the same raw constant, and they should not: they measure
different quantities. The mission is NOT "prove they give the same
number" (that would be reverse-fitting). The mission is to establish the
EXACT relationship between them — which pairs are literally the same
object (a set equality that must hold exactly), which are conversions of
each other (a derivable transform), and which are independent. Every
claimed identity is forced through a held-out / adversarial check. A
result of "these are genuinely independent, no relation" is valid and
important.

## The four instruments (all pre-existing, on disk)
1. **Backward basin** (shell/descent_rule/, BACKWARD BASIN CERTIFICATE):
   coverage density(N) of odd x certified to reach 1 within N steps ->
   1; complement c(N)=1-density decays super-exponentially (measured
   per-step ~0.93-0.95); NO hard residue floor; layers do NOT close at
   fixed modulus (description grows with depth). MERGE-SAFE (distinct x).
2. **Death shell** (shell/shell_probe.py, SYNTHESIS F6-F9): the
   ceiling-anchored DEAD residue set S(m) — states a corridor trajectory
   structurally cannot occupy; M_edge(C)=floor(53(C+1)/22); trit-locality.
3. **Spectral radius** (SPECTRAL_RADIUS_RESULTS.txt, COLLATZ_PROOF.md):
   killed-survivor graph rho=0.960647 per 53-step heartbeat (gap
   0.039353); gap-per-step base b=0.063099 ~ (53/84)^6, 84/53 = 6th
   convergent of log2(3).
4. **Corridor / capacity** (renorm_check/SYNTHESIS all rounds): edge law
   floor((C+1)/beta) exact C<=10 then a hard phase transition at C=11;
   the -6/heartbeat climb impossibility (LOCK4-B1); no-hover / no-climb.

## The joins to TEST (each with a frozen prediction, each falsifiable)

**J1 — Death shell == basin complement? (a SET equality).** The basin's
uncertified complement (odds not reaching 1 within N steps, as N->inf)
and the death shell's dead set are two constructions of "cannot descend."
Are they the SAME residue structure? Test: is the basin complement at
finite N contained in / equal to the shell dead set, on matched residue
descriptions? Frozen: they are the same object (~65%) — a set equality,
either it holds exactly or reveals a concrete difference set.

**J2 — Does the spectral rate GOVERN the basin decay? (a conversion).**
The basin complement decays per-step ~0.93-0.95; the spectral gap
decays per-step at base b~0.063; rho=0.96 per heartbeat. These are
different measures (fraction-of-starts vs survival-mass vs gap). Derive
the conversion: does the basin complement decay rate EQUAL a known
transform of rho / b (e.g. per-heartbeat rho drives per-start coverage
via the number of heartbeats to descend)? Fit the basin complement to
A*rho^(N/53), to A*b^(N/?), and to a free exponential; report which the
data prefers and whether the winning rate is rho-derived or independent.
Frozen: the basin decay is rho-GOVERNED (a derivable transform), ~55%
(genuinely uncertain — pre-check shows raw rates differ, so this needs
the conversion or it fails).

**J3 — Corridor constant == spectral convergent? (same 53).** The
corridor uses 53/22 (beta convergent); the spectral law uses 53/84
(1/alpha convergent). Both are the SAME heartbeat 53 (84/53 = 6th
convergent of log2(3)). Confirm the 53 is one object across both, and
whether the corridor's phase-transition location (C=11) relates to the
spectral exponent 6 or the heartbeat structure. Frozen: 53 is shared
(exact); C=11-transition relation to 6 is open exploration.

**J4 — Does the union CLOSE the loop the basin leaves open?** The basin
proves reachable but not rate; the corridor forbids hover/climb; the
spectral radius gives a rate; the shell names the dead set. State
PRECISELY what a proof would need and whether the four measured
properties, IF their relationships (J1-J3) hold, jointly imply "every
odd number descends to 1 at a bounded rate" — OR identify the exact gap
that remains (almost certainly: the non-closure of the residue system at
fixed modulus, which ALL FOUR instruments independently hit — basin
Gate1, spectral, corridor W6I dual-fail, transducer). Frozen: the loop
does NOT fully close — the shared obstruction (no fixed-modulus closure)
is the residual gap, and naming it precisely across all four is the
deliverable, ~75%.

## Rules
Exact arithmetic. Merge-safe (distinct x) for any basin/coverage number.
Every claimed identity (J1 set equality, J2 conversion) gets a held-out
or adversarial check — do NOT declare a match on a fit. "Independent, no
relation" and "the loop does not close, here is the exact gap" are valid,
expected verdicts. Reuse existing artifacts; do not recompute what is on
disk unless verifying. Work under renorm_check/shell/synthesis_four/.

## Output discipline (MANDATORY, LEDGER_SYNTHESIS_POLICY.md)
Process LEDGER entry to IMPLEMENTATION_LEDGER.md + SYNTHESIS entry to
SYNTHESIS.md. Chat is courtesy only. No commits.

Final message: J1 set-equality verdict (same object / difference set),
J2 conversion verdict (rho-governed / independent, with the fit
comparison), J3 shared-53 confirmation + C=11/exponent-6 note, J4 the
precise statement of what the union proves and the exact residual gap,
and confirmation LEDGER + SYNTHESIS written.
