#!/usr/bin/env python3
"""
IME reframe of J2/J4 (2026-07-05, second round, per architect course-correction
relayed by a peer session -- see IME-primer.md).

Original J2 treated "basin decay rate != spectral rate" as FALSIFICATION of a
rho-governs-basin hypothesis. Under IME the raw-rate mismatch is not a failure
signature -- it is the EXPECTED signature of two incommensurable measurement
geometries forced to interact. The test changes from "do the rates match" to
"do the four instruments' CHARACTERISTIC DEPTHS form an ordered hierarchy whose
tier BOUNDARIES land on the log2(3) convergent ladder (53, 84, 306, 485, 665,
1054, 24727, ...), or is the ordering arbitrary."

STEP 0 -- PRE-REGISTRATION (must happen BEFORE any numeric comparison, or the
match is a reverse-fit by construction, exactly the failure mode already
caught twice in this program's history -- 9/4 and prime-19).

Natural/principled instrument -> characteristic-depth pairing, fixed BEFORE
computing which convergent-ladder value is numerically closest:

  1. BASIN: per-odd-step decay rate ~0.93-0.95 (J2 round 1, free-rate fit,
     tail region). Characteristic depth = e-folding depth = -1/ln(rate)
     (steps for the complement to shrink by factor 1/e). This is a BASIN
     (odd-step) native unit.
  2. DEATH SHELL: characteristic m-depth is P5's D(m) growth / the m=359
     first-divergence point (the shell's own natively-reported deep
     structural scale) -- but for a same-footing "characteristic depth"
     comparison we use M_edge(C) at the shell's own edge C values, which
     is already reported in HEARTBEAT units (53-step blocks), matching
     the corridor's own units natively (heartbeat-native instrument).
  3. SPECTRAL RADIUS: e-folding depth of the gap (1-rho), = -1/ln(b) in
     m-UNITS (b is a per-m-increment rate, i.e. per PRECISION LEVEL, not
     per heartbeat) -- this is the spectral instrument's own native unit,
     kept separate rather than silently converted to heartbeats (that
     conversion was the exact unit-conflation flagged as a caveat in
     round 1's J2 entry).
  4. CORRIDOR: M_edge(C) growth is exact and heartbeat-native by
     construction (M_edge(C)=floor(53(C+1)/22), a HEARTBEAT-per-corridor-
     unit law); the post-C=11 growth law measured empirically at ~x1.83
     per unit C (SYNTHESIS.md "Growth curve" W6X, live-set peak growth,
     NOT M_edge growth -- registering this distinctly so as not to
     conflate two different corridor quantities).

Pre-registered PAIRING for the convergent-ladder test (fixed before any
number is compared against the ladder): the corridor and spectral
instruments are ALREADY heartbeat-native (53 appears by construction in
both, verified exactly in round-1 J3) -- so the ladder test is applied
to the BASIN and DEATH SHELL characteristic depths, converted to
heartbeat units (divide by 53), since those two are the instruments
whose native units are NOT already locked to 53 by construction (testing
corridor/spectral against the ladder they're built from would be
circular).

Ladder values fixed IN ADVANCE by log2(3)'s own continued fraction
(verified exactly in round-1 J3, reused verbatim, NOT recomputed here to
avoid any appearance of re-deriving to fit): 53, 84, 306, 485, 665,
1054, 15601, 24727, 31867, ...
"""
import math
from pathlib import Path

HERE = Path(__file__).parent

# ---- Ladder, taken verbatim from round-1 J3's j3_output.txt convergents ----
# CF(log2 3) convergents (p,q): (1,1)(2,1)(3,2)(8,5)(19,12)(65,41)(84,53)
#   (485,306)(1054,665)(24727,15601)(50508,31867)...
# CF(2-log2 3) convergents (p,q): (0,1)(1,2)(2,5)(5,12)(17,41)(22,53)
#   (127,306)(276,665)(6475,15601)...
LADDER_DENOMS = [1, 1, 2, 5, 12, 41, 53, 306, 665, 15601, 31867, 79335, 111202, 190537]
LADDER_NAMED = {
    "53 (alpha k=6, beta k=5)": 53,
    "306 (alpha k=7 numerator=485; beta k=6 denom=306)": 306,
    "665 (alpha k=8 denom)": 665,
    "1054 (alpha k=8 numerator)": 1054,
    "15601 (alpha k=9 denom)": 15601,
    "24727 (alpha k=9 numerator)": 24727,
}

HEARTBEAT = 53
SUPPORT_COUNT = 22


def M_edge(C):
    return (HEARTBEAT * (C + 1)) // SUPPORT_COUNT


def main():
    out = []
    out.append("=" * 78)
    out.append("IME-reframed J2/J4 -- characteristic-depth hierarchy vs convergent ladder")
    out.append("=" * 78)

    out.append("\n--- STEP 0: pre-registered pairing (fixed before any ladder lookup) ---")
    out.append("Corridor and spectral are ALREADY heartbeat-native (53 built in by "
               "construction, per round-1 J3). Ladder test applies to BASIN and DEATH "
               "SHELL characteristic depths only, converted to heartbeat units.")

    # ---- 1. BASIN characteristic depth ----
    out.append("\n--- 1. BASIN characteristic (e-folding) depth ---")
    out.append("Using round-1 J2's free-rate tail fits (already computed, not re-derived "
               "to fit here): DEEP TAIL (N=170-200) r=0.935710; TAIL (N=150-200) "
               "r=0.932844; FULL r=0.943803.")
    basin_rates = {"DEEP_TAIL_170_200": 0.935710, "TAIL_150_200": 0.932844, "FULL_0_200": 0.943803}
    basin_efold = {}
    for label, r in basin_rates.items():
        efold_steps = -1 / math.log(r)  # odd-steps for complement to shrink by 1/e
        efold_heartbeats = efold_steps / HEARTBEAT
        basin_efold[label] = (efold_steps, efold_heartbeats)
        out.append(f"  {label}: rate={r}  e-fold depth = {efold_steps:.4f} odd-steps "
                   f"= {efold_heartbeats:.4f} heartbeats")

    # ---- 2/4. Corridor M_edge and growth ----
    out.append("\n--- 2/4. CORRIDOR M_edge(C) (exact, heartbeat-native by construction) ---")
    for C in [1, 5, 10, 11, 12, 15, 20]:
        out.append(f"  M_edge({C:>2}) = {M_edge(C):>4}  (heartbeats)")
    out.append("  Post-C=11 live-set growth rate ~x1.83/C (SYNTHESIS.md W6X 'Growth "
               "curve', a DIFFERENT quantity from M_edge -- state count growth, not "
               "heartbeat-depth growth; kept separate, not converted into a depth here.")

    # ---- 3. Spectral e-folding depth in m-units ----
    out.append("\n--- 3. SPECTRAL RADIUS characteristic (e-folding) depth, m-units ---")
    B = 0.063099
    RHO_C3 = 0.960647
    m_efold_b = -1 / math.log(B)
    out.append(f"  b={B} (C>=10 universal gap-decay base, per m/precision-level): "
               f"e-fold depth = {m_efold_b:.4f} m-levels")
    out.append(f"  NOTE: this is in PRECISION-LEVEL (m) units, native to the spectral "
               f"instrument, NOT heartbeat units -- no conversion applied (m and "
               f"heartbeat-count are different axes; the spectral m-axis is corridor "
               f"PRECISION depth, not heartbeat repetitions of a fixed corridor).")
    out.append(f"  C=3 hard-floor lock value rho={RHO_C3}, gap={1-RHO_C3:.6f} -- this "
               f"is a FIXED per-heartbeat contraction at the narrow C=3 corridor, "
               f"already in heartbeat-native units by construction (1 heartbeat = "
               f"53 steps, the unit the whole instrument is built on).")

    # ---- 4. Death shell characteristic depth (D(m) / m=359 divergence) ----
    out.append("\n--- 4. DEATH SHELL characteristic depth ---")
    out.append("The shell's own natively-reported DEEP structural scale is the D(m) "
               "first-divergence point m=359 (P5, shell_probe.py) -- a PRECISION-level "
               "(m) quantity, same axis as the spectral radius's m (both instruments "
               "index depth by 3^m residue precision, not by heartbeat count).")
    out.append(f"  m=359 first divergence (D_rat=149 vs D_irr=148, an exact one-trit "
               f"difference) -- this is the shell's own m-axis deep scale, computed "
               f"and verified in the shell's OWN prior work (P5), NOT re-derived here.")

    # ---- Convergent-ladder test: basin heartbeat-depth vs ladder ----
    out.append("\n--- STEP 1: is BASIN's heartbeat-depth near a convergent-ladder value? ---")
    out.append(f"Ladder (heartbeat-axis candidates, since basin's native unit converts "
               f"to heartbeats): {LADDER_DENOMS}")
    for label, (steps, hbs) in basin_efold.items():
        nearest = min(LADDER_DENOMS, key=lambda v: abs(v - hbs))
        rel_err = abs(nearest - hbs) / nearest
        out.append(f"  {label}: {hbs:.4f} heartbeats.  Nearest ladder value: {nearest}  "
                   f"(relative error {100*rel_err:.1f}%)")
    out.append("\n  ADVERSARIAL NULL CHECK: basin e-fold depths are ~14.4-17.3 RAW "
               "odd-steps -- i.e. only ~0.27-0.33 of a SINGLE heartbeat (53 steps). "
               "The basin's complement decays to 1/e within a THIRD of one heartbeat; "
               "it never accumulates to even the ladder's SMALLEST nontrivial tier "
               "(53). The nearest ladder value (1, the trivial first convergent) is "
               "still 3x too large relative to the basin's own sub-heartbeat e-fold "
               "scale, and the next real tier (53) is off by ~160x. There is no "
               "regime in which the basin's characteristic depth lands on ANY "
               "ladder tier -- report exact relative errors, do not round to 'close'.")

    # ---- Null-model comparison: would ANY random rate in the plausible basin range hit the ladder? ----
    out.append("\n--- Adversarial null model: how often would an ARBITRARY rate in the "
               "empirically-plausible basin range (0.90-0.97/step, the full spread seen "
               "across N-ranges and the per-step ratio scatter) land within 10% of ANY "
               "ladder value, purely by chance? ---")
    ladder_set = sorted(set(LADDER_DENOMS))
    hits = 0
    total = 0
    r = 0.90
    while r <= 0.97:
        efold = -1 / math.log(r)
        hb = efold / HEARTBEAT
        nearest = min(ladder_set, key=lambda v: abs(v - hb))
        rel_err = abs(nearest - hb) / nearest
        total += 1
        if rel_err < 0.10:
            hits += 1
        r += 0.001
    out.append(f"  Sweeping r=0.900..0.970 in steps of 0.001 ({total} points): "
               f"{hits} land within 10% of SOME ladder value ({100*hits/total:.1f}%).")
    out.append("  If this fraction is already large, a 10%-tolerance 'match' anywhere "
               "in the plausible basin-rate range is not evidence of ladder alignment "
               "-- it's just how densely the small ladder values (1,1,2,5,12,41,53) "
               "are packed relative to the tiny heartbeat-depth range (14-17) that "
               "ANY basin decay rate in this whole plausible interval maps to.")

    # ---- Held-out prediction ----
    out.append("\n--- MANDATORY held-out prediction ---")
    out.append("Registered BEFORE checking: IF the basin's heartbeat-depth were "
               "ladder-governed, the corridor's own M_edge(C) at the SAME heartbeat-"
               "depth (~15.3-15.6) should mark a structurally distinguished corridor "
               "width C -- since M_edge(C)=floor(53(C+1)/22), solve for C at "
               "M_edge(C)=15-16 heartbeats and check whether that C is anywhere "
               "flagged as structurally special in the corridor's OWN prior work "
               "(independent of this fit).")
    for target_hb in [15, 16]:
        # M_edge(C) = floor(53(C+1)/22) = target_hb  =>  C+1 ~= target_hb*22/53
        C_est = target_hb * SUPPORT_COUNT / HEARTBEAT - 1
        out.append(f"  M_edge(C)={target_hb} heartbeats => C ~ {C_est:.2f}  "
                   f"(nearest integer C={round(C_est)}, M_edge({round(C_est)})="
                   f"{M_edge(round(C_est))})")
    out.append("  C~5-6 is NOT the corridor's flagged special width anywhere in prior "
               "work (the flagged special widths are C=11, the phase transition, and "
               "C=148, the F1 divergence) -- the held-out prediction FAILS: the basin's "
               "heartbeat-depth does not point at a corridor-flagged structural width.")

    # ---- Overall hierarchy shape check (geometric bulk / heavy tail?) ----
    out.append("\n--- Is there a GHOST_PRECISION-shaped hierarchy (bulk/tail), or just "
               "different numbers? ---")
    out.append("Basin: single geometric-ish decay rate in the tail (NOT a clean bulk/"
               "tail split into two regimes -- round-1 J2's held-out check showed the "
               "SAME tail region (N=150-200) does not extrapolate to N=180-200 cleanly, "
               "meaning the basin does not even have ONE stable geometric rate, let "
               "alone a two-regime bulk/tail split with a sharp percentage boundary "
               "like GHOST_PRECISION's 50%@1bit / 77-89%@2bit.")
    out.append("Death shell: P1 shows dead-mass GROWING with m (not a fixed bulk "
               "fraction) -- no stable 'X% resolve shallow, Y% need deep' split "
               "reported anywhere in the shell's own P1-P6 measurements.")
    out.append("Spectral: the C=3 vs C>=10 split IS a genuine two-regime structure "
               "(narrow corridor locks at a fixed floor; wide corridor's gap -> 0) -- "
               "but this is a FIXED-C-vs-VARIABLE-C dichotomy, not a population split "
               "of interactions/orbits into bulk-fraction and tail-fraction the way "
               "GHOST_PRECISION's bit-depth histogram is. Structurally different kind "
               "of two-regime-ness.")
    out.append("Corridor: F1's C<=147 exact-agreement / C>=148 divergence is the "
               "closest analog to a bulk/tail SPLIT WITH A SHARP BOUNDARY -- but it is "
               "a single width threshold in one growing constant (M_edge formula "
               "agreement), not a population fraction split (there is no '86% of "
               "corridor widths behave like X').")
    out.append("VERDICT: none of the four instruments' own native structure is "
               "actually shaped like GHOST_PRECISION's bulk/tail population-fraction "
               "histogram. Each has SOME two-regime or growing/decaying structure, but "
               "not the SAME shape (a fixed population percentage stabilizing at a "
               "fixed low resource level). Calling this 'the same IME shape' would be "
               "describing four different growth/decay/threshold phenomena with one "
               "borrowed label, not demonstrating a shared underlying mechanism.")

    text = "\n".join(out)
    print(text)
    (HERE / "j2j4_ime_output.txt").write_text(text + "\n")


if __name__ == "__main__":
    main()
