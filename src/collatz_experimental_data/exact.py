from __future__ import annotations

import csv
import heapq
import json
import math
import os
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from fractions import Fraction
from multiprocessing import Pool
from pathlib import Path
from typing import Callable, Iterable


ALPHA = math.log2(3)
KNOWN_CF_CONVERGENTS = (1, 2, 7, 12, 53, 359, 665, 16266, 31867, 111202)


def v2(n: int) -> int:
    if n == 0:
        raise ValueError("v2(0) is undefined")
    n = abs(n)
    return (n & -n).bit_length() - 1


def odd_syracuse_step(x: int) -> tuple[int, int]:
    if x <= 0 or x % 2 == 0:
        raise ValueError("x must be a positive odd integer")
    y = 3 * x + 1
    a = v2(y)
    return y >> a, a


@dataclass(frozen=True)
class Step:
    k: int
    x: int
    a: int
    A_before: int
    A_after: int
    d_before: int
    d_after: int
    c: int
    growing: bool


@dataclass(frozen=True)
class Segment:
    index: int
    start_idx: int
    end_idx: int
    start_k: int
    end_k: int
    length: int
    A: int
    B: int
    entry_x: int
    exit_x: int
    d_before: int
    d_after: int
    max_d_before: int
    max_d_after: int
    multiplier_num: int
    multiplier_den: int
    ghost_num: int | None
    ghost_den: int | None
    ghost_real: float | None
    fixed_residual_v2: int | None
    fixed_residual_bits: int | None
    beta_length: float
    beta_start: float
    beta_end: float


@dataclass(frozen=True)
class Seam:
    index: int
    previous_segment: int
    next_segment: int
    start_idx: int
    end_idx: int
    length: int
    A: int
    d_start: int
    d_end: int
    min_d: int
    max_d: int
    max_a: int
    total_a: int
    word: str


@dataclass(frozen=True)
class MacroCorridor:
    orbit: int
    corridor_index: int
    start_step: int
    end_step: int
    length: int
    A: int
    B: int
    beta: float
    positive_action: bool
    mapped_convergent: int
    mapped_convergent_beta: float
    mapped_by: str
    ghost_num: int | None
    ghost_den: int | None
    ghost_real: float | None
    quality_1_over_beta: float | None
    d_entry: int
    d_exit: int
    d_peak: int
    d_min: int
    word: str


@dataclass(frozen=True)
class GapExitRow:
    orbit: int
    k53_corridor_index: int
    k53_start_step: int
    k53_exit_step: int
    k53_length: int
    reserve_at_exit: int
    peak_reserve_in_corridor: int
    bankruptcy_step: int
    steps_remaining_before_bankruptcy: int
    gap_to_359: int
    min_reserve_to_bridge_gap: int
    gap_to_exit_reserve_ratio: float
    bridgeable_by_exit_reserve: bool


@dataclass(frozen=True)
class LadderGapRow:
    convergent_n: int
    convergent_k: int
    gap_to_next: int
    max_reserve_from_riding_n: int | None
    min_reserve_to_bridge_gap: int
    bridgeable: bool | None


@dataclass(frozen=True)
class PostK53StepRow:
    orbit: int
    phase_index: int
    step_k: int
    a: int
    c: int
    d_before: int
    d_after: int
    delta_d: int
    is_a1: bool


@dataclass(frozen=True)
class PostK53StatsRow:
    orbit: int
    k53_exit_step: int
    bankruptcy_step: int
    post_steps: int
    count_a1: int
    count_a2: int
    count_a_ge3: int
    frac_a1: float
    frac_a2: float
    frac_a_ge3: float
    average_a: float
    average_credit: float
    actual_drain_per_step: float
    conservative_drain_per_step: float
    observed_bridge_required_306: int
    conservative_bridge_required_306: int
    observed_bridgeable_by_exit_reserve: bool
    exit_reserve: int


@dataclass(frozen=True)
class K53CapacityObservedRow:
    orbit: int
    corridor_index: int
    start_step: int
    end_step: int
    length: int
    A: int
    entry_reserve: int
    exit_reserve: int
    peak_reserve: int
    actual_gain_to_peak: int
    high_credit_steps_observed_window: int
    high_credit_density_observed_window: float
    best_high_credit_steps_same_length_0_to_scan: int
    entry_x_bit_length: int
    max_x_bit_length_in_corridor: int
    max_len_from_entry_bits: int
    max_len_from_max_bits: int
    possible_gain_from_entry_bits: int
    possible_gain_from_max_bits: int


@dataclass(frozen=True)
class K53CapacityRequirementRow:
    required_reserve: int
    direct_min_corridor_length_at_credit_density: int
    high_credit_gain_events_needed: int
    instruction_min_corridor_length: int
    min_starting_bit_length: int
    approximate_integer_log10: float
    martingale_probability_upper_bound: float
    martingale_log10_probability_upper_bound: float
    expected_starts_lower_bound: float
    expected_starts_log10_lower_bound: float


@dataclass(frozen=True)
class CorridorBoundObservedRow:
    orbit: int
    start_bit_length: int
    corridor_index: int
    start_step: int
    end_step: int
    length: int
    length_over_start_bits: float
    entry_x_bit_length: int
    exit_x_bit_length: int
    bits_consumed_entry_minus_exit: int
    bits_consumed_per_step: float
    peak_reserve: int


@dataclass(frozen=True)
class CorridorBoundSyntheticRow:
    bit_length: int
    sample_index: int
    start: int
    max_reserve: int
    entered_k53_quality: bool
    best_corridor_length: int | None
    best_corridor_beta_distance: float | None
    best_corridor_start_step: int | None
    best_corridor_end_step: int | None
    length_over_start_bits: float | None


@dataclass(frozen=True)
class CorridorBoundCeilingRow:
    bit_length: int
    max_corridor_length: int
    max_reserve: int
    bridge_85_possible: bool
    bridge_128_possible: bool
    martingale_mu_H85_upper_bound: float
    martingale_mu_H128_upper_bound: float


@dataclass(frozen=True)
class ScalingSweepSummaryRow:
    beta_threshold: float
    bit_length: int
    samples: int
    positive_corridor_orbits: int
    quality_corridor_orbits: int
    fraction_entering_positive_corridor: float
    fraction_entering_quality_corridor: float
    max_length: int
    max_length_over_bits: float
    max_reserve_gain: int
    max_gain_per_step: float


@dataclass(frozen=True)
class ScalingSweepFitRow:
    beta_threshold: float
    model: str
    coefficient_a: float
    coefficient_b: float
    r_squared: float


@dataclass(frozen=True)
class ScalingSweepKillRow:
    beta_threshold: float
    required_reserve: int
    best_model: str
    best_model_r_squared: float
    observed_gain_per_step: float
    required_corridor_length: int
    required_bit_length: float | None
    expected_below_1e80_log10: float
    expected_below_1e120_log10: float
    expected_below_1e500_log10: float


@dataclass(frozen=True)
class MacroConvergentSummaryRow:
    start: int
    max_reserve: int
    time_max: int
    crossing_time: int
    macro_corridors: int
    positive_macro_corridors: int
    max_mapped_convergent: int | None
    has_k53_or_higher: bool
    has_k359_or_higher: bool
    best_corridor_index: int | None
    best_corridor_start: int | None
    best_corridor_end: int | None
    best_corridor_length: int | None
    best_corridor_A: int | None
    best_corridor_beta: float | None
    best_corridor_mapped_convergent: int | None
    best_corridor_peak_reserve: int | None


@dataclass(frozen=True)
class TailThresholdRow:
    threshold_reserve: int
    count_at_least_threshold: int
    odd_starts_scanned: int
    empirical_rate: float
    log10_empirical_rate: float | None


@dataclass(frozen=True)
class TailFitRow:
    fit_min_threshold: int
    fit_max_threshold: int
    points: int
    intercept_log10: float
    slope_per_reserve_log10: float
    per_reserve_factor: float
    r_squared: float


@dataclass(frozen=True)
class TailProjectionRow:
    fit_min_threshold: int
    target_reserve: int
    projected_log10_rate: float
    projected_expected_odd_starts_log10: float


@dataclass(frozen=True)
class TailZeroBoundRow:
    threshold_reserve: int
    odd_starts_scanned: int
    zero_hit_95_upper_rate: float
    zero_hit_95_upper_rate_log10: float
    expected_odd_starts_95_lower_log10: float


@dataclass(frozen=True)
class Lock2WordRow:
    word: str
    k: int
    A: int
    B: int
    rho: int
    theta_num: int
    theta_den: int
    theta_float: float
    margin: int
    threshold_gap_float: float
    relative_gap: float
    normalized_margin: float
    log2_margin_plus_1_over_k: float
    theta_candidate_odd_count: int
    rho_rank: int
    theta_over_rho: float
    candidate_to_rho_rank_ratio: float
    rho_bit_slack: int
    is_all_twos: bool
    first_contractivity_index: int | None
    delta_from_all_twos: int
    count_ones: int
    count_twos: int
    count_ge3: int
    max_run_1: int
    max_run_2: int
    max_run_ge3: int
    primitive_period: int
    primitive_repetitions: int


@dataclass(frozen=True)
class Lock3SurvivorDepthRow:
    C: int
    depth: int
    total_budget_paths: int
    valid_backward_paths_from_1: int
    valid_backward_residue_classes: int
    min_positive_ancestor: int | None
    max_positive_ancestor: int | None
    branch_count: int
    notes: str


@dataclass(frozen=True)
class Lock3BackwardPathRow:
    C: int
    depth: int
    deficit_path_encoded: str
    exponent_word: str
    terminal_value: int
    ancestor_value: int | None
    valid_all_steps: bool
    first_failure_depth: int | None
    failure_reason: str
    final_modulus: int
    residue_class: int


@dataclass(frozen=True)
class Lock3ResidueLiftRow:
    C: int
    depth: int
    A_k: int
    modulus: int
    rho_k: int
    bit_length_rho: int
    rho_changed: bool
    lift_amount: int
    deficit_state: int
    exponent: int


@dataclass(frozen=True)
class Lock3SearchState:
    deficits: tuple[int, ...]
    word: tuple[int, ...]
    A: int
    B: int
    pow3: int
    previous_rho: int | None
    lift_count: int
    current_plateau: int
    longest_plateau: int


@dataclass(frozen=True)
class Lock3CensusWitnessState:
    deficits: tuple[int, ...]
    word: tuple[int, ...]
    A: int
    B: int
    pow3: int
    previous_rho: int | None
    lift_count: int
    current_plateau: int
    longest_plateau: int


@dataclass(frozen=True)
class Lock3CensusRow:
    C: int
    depth: int
    residue_mod_power: int
    residue_modulus: int
    terminal_residue_signature: int
    symbolic_branch_count: int
    merged_state_count: int
    valid_from_1_count: int
    terminal_1_compatible_signature_count: int
    valid_residue_count: int
    residue_class_count: int
    rho_stable_count: int
    rho_lift_count: int
    longest_plateau: int
    max_rho_bit_length: int
    max_branch_multiplicity: int
    compression_ratio: str
    valid_fraction: str
    stable_fraction: str
    truncated: bool
    notes: str


@dataclass(frozen=True)
class Lock3CensusEventRow:
    C: int
    depth: int
    event_type: str
    value: str
    branch_id_or_state_id: str
    deficit_state: int | None
    exponent: int | None
    summary: str


def simulate_orbit(n: int, max_steps: int = 100000) -> list[Step]:
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be a positive odd integer")

    steps: list[Step] = []
    x = n
    A = 0

    for k in range(max_steps):
        d_before = math.floor(k * ALPHA) - A
        x_next, a = odd_syracuse_step(x)
        A_after = A + a
        c = math.floor((k + 1) * ALPHA) - math.floor(k * ALPHA)
        d_after = math.floor((k + 1) * ALPHA) - A_after
        steps.append(
            Step(
                k=k,
                x=x,
                a=a,
                A_before=A,
                A_after=A_after,
                d_before=d_before,
                d_after=d_after,
                c=c,
                growing=d_after > d_before,
            )
        )
        x = x_next
        A = A_after
        if d_after < 0:
            break

    return steps


def affine_for_word(word: Iterable[int]) -> tuple[int, int, int]:
    length = 0
    A = 0
    B = 0
    for a in word:
        B = 3 * B + (1 << A)
        A += a
        length += 1
    return length, A, B


def find_growth_segments(steps: list[Step], min_len: int = 2) -> list[tuple[int, int]]:
    segments: list[tuple[int, int]] = []
    in_growth = False
    start = 0

    for i, step in enumerate(steps):
        if step.growing and not in_growth:
            in_growth = True
            start = i
        elif not step.growing and in_growth:
            in_growth = False
            if i - start >= min_len:
                segments.append((start, i - 1))

    if in_growth and len(steps) - start >= min_len:
        segments.append((start, len(steps) - 1))

    return segments


def _frac_parts(k: int) -> float:
    return k * ALPHA - math.floor(k * ALPHA)


def analyze_segment(steps: list[Step], index: int, start: int, end: int) -> Segment:
    word = [s.a for s in steps[start : end + 1]]
    length, A, B = affine_for_word(word)
    entry_x = steps[start].x
    exit_x = _advance_by_word(entry_x, word)
    D = 3**length - (1 << A)
    ghost: Fraction | None = None
    fixed_v: int | None = None
    residual_bits: int | None = None

    if D > 0:
        ghost = Fraction(-B, D)
        residual = D * entry_x + B
        fixed_v = v2(residual) if residual else 10**9
        residual_bits = abs(residual).bit_length()

    return Segment(
        index=index,
        start_idx=start,
        end_idx=end,
        start_k=steps[start].k,
        end_k=steps[end].k,
        length=length,
        A=A,
        B=B,
        entry_x=entry_x,
        exit_x=exit_x,
        d_before=steps[start].d_before,
        d_after=steps[end].d_after,
        max_d_before=max(s.d_before for s in steps[start : end + 1]),
        max_d_after=max(s.d_after for s in steps[start : end + 1]),
        multiplier_num=3**length,
        multiplier_den=1 << A,
        ghost_num=ghost.numerator if ghost is not None else None,
        ghost_den=ghost.denominator if ghost is not None else None,
        ghost_real=float(ghost) if ghost is not None else None,
        fixed_residual_v2=fixed_v,
        fixed_residual_bits=residual_bits,
        beta_length=_frac_parts(length),
        beta_start=_frac_parts(steps[start].k),
        beta_end=_frac_parts(steps[end].k),
    )


def _advance_by_word(x: int, word: Iterable[int]) -> int:
    for a in word:
        y = 3 * x + 1
        if v2(y) != a:
            raise AssertionError("orbit word does not match entry value")
        x = y >> a
    return x


def analyze_seams(steps: list[Step], segments: list[tuple[int, int]]) -> list[Seam]:
    seams: list[Seam] = []
    for idx, ((_, prev_end), (next_start, _)) in enumerate(zip(segments, segments[1:])):
        start = prev_end + 1
        end = next_start - 1
        if start > end:
            word: list[int] = []
            d_start = steps[prev_end].d_after
            d_end = steps[next_start].d_before
            min_d = min(d_start, d_end)
            max_d = max(d_start, d_end)
        else:
            word = [s.a for s in steps[start : end + 1]]
            d_start = steps[start].d_before
            d_end = steps[end].d_after
            values = [s.d_before for s in steps[start : end + 1]]
            values.extend(s.d_after for s in steps[start : end + 1])
            min_d = min(values)
            max_d = max(values)

        _, A, _ = affine_for_word(word)
        seams.append(
            Seam(
                index=idx,
                previous_segment=idx,
                next_segment=idx + 1,
                start_idx=start,
                end_idx=end,
                length=len(word),
                A=A,
                d_start=d_start,
                d_end=d_end,
                min_d=min_d,
                max_d=max_d,
                max_a=max(word) if word else 0,
                total_a=sum(word),
                word=",".join(str(a) for a in word),
            )
        )
    return seams


def analyze_orbit(n: int, max_steps: int = 100000, min_segment_len: int = 2) -> dict:
    steps = simulate_orbit(n, max_steps=max_steps)
    raw_segments = find_growth_segments(steps, min_len=min_segment_len)
    segments = [
        analyze_segment(steps, idx, start, end)
        for idx, (start, end) in enumerate(raw_segments)
    ]
    seams = analyze_seams(steps, raw_segments)
    max_reserve = max([0, *(s.d_before for s in steps), *(s.d_after for s in steps)])
    time_max = next(
        (
            s.k + 1
            for s in steps
            if s.d_after == max_reserve
        ),
        0,
    )
    return {
        "start": n,
        "total_steps": len(steps),
        "crossing_time": len(steps) if steps and steps[-1].d_after < 0 else -1,
        "max_reserve": max_reserve,
        "time_max": time_max,
        "num_growth_steps": sum(1 for s in steps if s.growing),
        "num_segments": len(segments),
        "steps": steps,
        "segments": segments,
        "seams": seams,
    }


def reserve_values(steps: list[Step]) -> list[int]:
    if not steps:
        return []
    return [steps[0].d_before, *(step.d_after for step in steps)]


def find_macro_corridor_ranges(
    d_values: list[int],
    drop_tolerance: int = 2,
    min_length: int = 1,
) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    if len(d_values) < 2:
        return ranges

    start = 0
    running_max = d_values[0]
    for idx in range(1, len(d_values)):
        d = d_values[idx]
        if d > running_max:
            running_max = d
        if running_max - d > drop_tolerance:
            end = idx - 1
            if end - start >= min_length:
                ranges.append((start, end))
            start = idx
            running_max = d

    end = len(d_values) - 1
    if end - start >= min_length:
        ranges.append((start, end))
    return ranges


def convergent_beta(k: int) -> float:
    value = k * ALPHA
    return abs(value - round(value))


def map_to_convergent(length: int, beta: float) -> tuple[int, float, str]:
    nearest_length = min(KNOWN_CF_CONVERGENTS, key=lambda k: abs(k - length))
    nearest_beta = min(KNOWN_CF_CONVERGENTS, key=lambda k: abs(convergent_beta(k) - abs(beta)))
    if nearest_length == nearest_beta:
        return nearest_length, convergent_beta(nearest_length), "length_and_beta"
    return nearest_length, convergent_beta(nearest_length), "length"


def analyze_macro_corridors(
    n: int,
    max_steps: int = 100000,
    drop_tolerance: int = 2,
    min_length: int = 1,
) -> list[MacroCorridor]:
    steps = simulate_orbit(n, max_steps=max_steps)
    d_values = reserve_values(steps)
    ranges = find_macro_corridor_ranges(
        d_values,
        drop_tolerance=drop_tolerance,
        min_length=min_length,
    )
    rows: list[MacroCorridor] = []

    for index, (start, end) in enumerate(ranges):
        word = [step.a for step in steps[start:end]]
        length, A, B = affine_for_word(word)
        if length != end - start:
            raise AssertionError("macro-corridor word length mismatch")

        beta = length * ALPHA - A
        positive = 3**length > (1 << A)
        ghost: Fraction | None = None
        quality: float | None = None
        if positive:
            ghost = Fraction(-B, 3**length - (1 << A))
        if beta > 0:
            quality = 1.0 / beta

        mapped, mapped_beta, mapped_by = map_to_convergent(length, beta)
        segment_d = d_values[start : end + 1]
        rows.append(
            MacroCorridor(
                orbit=n,
                corridor_index=index,
                start_step=start,
                end_step=end,
                length=length,
                A=A,
                B=B,
                beta=beta,
                positive_action=positive,
                mapped_convergent=mapped,
                mapped_convergent_beta=mapped_beta,
                mapped_by=mapped_by,
                ghost_num=ghost.numerator if ghost is not None else None,
                ghost_den=ghost.denominator if ghost is not None else None,
                ghost_real=float(ghost) if ghost is not None else None,
                quality_1_over_beta=quality,
                d_entry=d_values[start],
                d_exit=d_values[end],
                d_peak=max(segment_d),
                d_min=min(segment_d),
                word=",".join(str(a) for a in word),
            )
        )

    return rows


def required_reserve_for_gap(
    gap: int,
    spend_per_step: int = 2,
    start_step: int | None = None,
    phase_scan: int = 200000,
) -> int:
    if gap < 0:
        raise ValueError("gap must be non-negative")
    if spend_per_step < 1:
        raise ValueError("spend_per_step must be at least 1")

    if start_step is None:
        return max(
            0,
            max(
                spend_per_step * prefix - math.floor(prefix * ALPHA)
                for prefix in range(gap + 1)
            ),
        )

    starts = [start_step] if start_step is not None else range(phase_scan)
    worst_required = 0
    for start in starts:
        loss = 0
        required = 0
        for offset in range(gap):
            k = start + offset
            c = math.floor((k + 1) * ALPHA) - math.floor(k * ALPHA)
            loss += spend_per_step - c
            if loss > required:
                required = loss
        if required > worst_required:
            worst_required = required
    return worst_required


def analyze_k53_gap_exits(
    starts: Iterable[int],
    max_steps: int = 100000,
    gap_to_359: int = 306,
    spend_per_step: int = 2,
) -> list[GapExitRow]:
    rows: list[GapExitRow] = []
    for start in starts:
        orbit = analyze_orbit(start, max_steps=max_steps)
        macros = analyze_macro_corridors(start, max_steps=max_steps)
        k53_rows = [
            row
            for row in macros
            if row.mapped_convergent == 53 and row.positive_action
        ]
        if not k53_rows:
            continue

        main = max(k53_rows, key=lambda row: (row.d_peak, row.length))
        required = required_reserve_for_gap(
            gap_to_359,
            spend_per_step=spend_per_step,
            start_step=main.end_step,
        )
        rows.append(
            GapExitRow(
                orbit=start,
                k53_corridor_index=main.corridor_index,
                k53_start_step=main.start_step,
                k53_exit_step=main.end_step,
                k53_length=main.length,
                reserve_at_exit=main.d_exit,
                peak_reserve_in_corridor=main.d_peak,
                bankruptcy_step=orbit["crossing_time"],
                steps_remaining_before_bankruptcy=orbit["crossing_time"] - main.end_step,
                gap_to_359=gap_to_359,
                min_reserve_to_bridge_gap=required,
                gap_to_exit_reserve_ratio=gap_to_359 / max(1, main.d_exit),
                bridgeable_by_exit_reserve=main.d_exit >= required,
            )
        )
    return rows


def analyze_ladder_gaps(
    macro_rows: Iterable[MacroCorridor],
    spend_per_step: int = 2,
    phase_scan: int = 200000,
) -> list[LadderGapRow]:
    convergents = [1, 2, 7, 12, 53, 359, 665, 16266, 31867, 111202]
    gaps = [1, 5, 5, 41, 306, 306, 15601, 15601, 79335]
    observed_reserve: dict[int, int] = {}
    for row in macro_rows:
        current = observed_reserve.get(row.mapped_convergent)
        if current is None or row.d_peak > current:
            observed_reserve[row.mapped_convergent] = row.d_peak

    rows: list[LadderGapRow] = []
    for idx, (k, gap) in enumerate(zip(convergents, gaps)):
        required = required_reserve_for_gap(
            gap,
            spend_per_step=spend_per_step,
            phase_scan=phase_scan,
        )
        max_reserve = observed_reserve.get(k)
        bridgeable = None if max_reserve is None else max_reserve >= required
        rows.append(
            LadderGapRow(
                convergent_n=idx,
                convergent_k=k,
                gap_to_next=gap,
                max_reserve_from_riding_n=max_reserve,
                min_reserve_to_bridge_gap=required,
                bridgeable=bridgeable,
            )
        )
    return rows


def analyze_post_k53_behavior(
    starts: Iterable[int],
    max_steps: int = 100000,
    bridge_gap: int = 306,
) -> tuple[list[PostK53StatsRow], list[PostK53StepRow]]:
    stats_rows: list[PostK53StatsRow] = []
    step_rows: list[PostK53StepRow] = []
    conservative_required = required_reserve_for_gap(bridge_gap, spend_per_step=2)
    conservative_drain = ALPHA - 2.0

    for start in starts:
        steps = simulate_orbit(start, max_steps=max_steps)
        d_values = reserve_values(steps)
        macros = analyze_macro_corridors(start, max_steps=max_steps)
        k53_rows = [
            row
            for row in macros
            if row.mapped_convergent == 53 and row.positive_action
        ]
        if not k53_rows:
            continue

        main = max(k53_rows, key=lambda row: (row.d_peak, row.length))
        phase_steps = steps[main.end_step :]
        if not phase_steps:
            continue

        count = len(phase_steps)
        count_a1 = sum(1 for step in phase_steps if step.a == 1)
        count_a2 = sum(1 for step in phase_steps if step.a == 2)
        count_a_ge3 = sum(1 for step in phase_steps if step.a >= 3)
        average_a = sum(step.a for step in phase_steps) / count
        average_credit = sum(step.c for step in phase_steps) / count
        actual_delta = sum(step.d_after - step.d_before for step in phase_steps) / count
        observed_required = max(0, math.ceil(bridge_gap * max(0.0, average_a - ALPHA)))

        stats_rows.append(
            PostK53StatsRow(
                orbit=start,
                k53_exit_step=main.end_step,
                bankruptcy_step=len(steps) if steps and steps[-1].d_after < 0 else -1,
                post_steps=count,
                count_a1=count_a1,
                count_a2=count_a2,
                count_a_ge3=count_a_ge3,
                frac_a1=count_a1 / count,
                frac_a2=count_a2 / count,
                frac_a_ge3=count_a_ge3 / count,
                average_a=average_a,
                average_credit=average_credit,
                actual_drain_per_step=actual_delta,
                conservative_drain_per_step=conservative_drain,
                observed_bridge_required_306=observed_required,
                conservative_bridge_required_306=conservative_required,
                observed_bridgeable_by_exit_reserve=d_values[main.end_step] >= observed_required,
                exit_reserve=d_values[main.end_step],
            )
        )

        for phase_index, step in enumerate(phase_steps):
            step_rows.append(
                PostK53StepRow(
                    orbit=start,
                    phase_index=phase_index,
                    step_k=step.k,
                    a=step.a,
                    c=step.c,
                    d_before=step.d_before,
                    d_after=step.d_after,
                    delta_d=step.d_after - step.d_before,
                    is_a1=step.a == 1,
                )
            )

    return stats_rows, step_rows


def credit_at_step(k: int) -> int:
    return math.floor((k + 1) * ALPHA) - math.floor(k * ALPHA)


def count_high_credit_steps(start: int, length: int) -> int:
    return sum(1 for k in range(start, start + length) if credit_at_step(k) == 2)


def max_high_credit_steps(length: int, scan_limit: int = 10000) -> int:
    if length <= 0:
        return 0
    best = 0
    current = count_high_credit_steps(0, length)
    best = current
    for start in range(1, scan_limit + 1):
        if credit_at_step(start - 1) == 2:
            current -= 1
        if credit_at_step(start + length - 1) == 2:
            current += 1
        if current > best:
            best = current
    return best


def k53_length_from_bits(bit_length: int) -> int:
    return math.floor(bit_length * 53 / 84)


def analyze_k53_capacity(
    starts: Iterable[int],
    required_reserves: Iterable[int] = (85, 128),
    max_steps: int = 100000,
    credit_scan_limit: int = 10000,
) -> tuple[list[K53CapacityObservedRow], list[K53CapacityRequirementRow]]:
    observed_rows: list[K53CapacityObservedRow] = []
    for start in starts:
        steps = simulate_orbit(start, max_steps=max_steps)
        macros = analyze_macro_corridors(start, max_steps=max_steps)
        k53_rows = [
            row
            for row in macros
            if row.mapped_convergent == 53 and row.positive_action
        ]
        if not k53_rows:
            continue
        main = max(k53_rows, key=lambda row: (row.d_peak, row.length))
        corridor_steps = steps[main.start_step : main.end_step]
        entry_bits = steps[main.start_step].x.bit_length() if corridor_steps else start.bit_length()
        max_bits = max((step.x.bit_length() for step in corridor_steps), default=entry_bits)
        max_len_entry = k53_length_from_bits(entry_bits)
        max_len_max = k53_length_from_bits(max_bits)
        observed_high_credit = count_high_credit_steps(main.start_step, main.length)

        observed_rows.append(
            K53CapacityObservedRow(
                orbit=start,
                corridor_index=main.corridor_index,
                start_step=main.start_step,
                end_step=main.end_step,
                length=main.length,
                A=main.A,
                entry_reserve=main.d_entry,
                exit_reserve=main.d_exit,
                peak_reserve=main.d_peak,
                actual_gain_to_peak=main.d_peak - main.d_entry,
                high_credit_steps_observed_window=observed_high_credit,
                high_credit_density_observed_window=observed_high_credit / main.length,
                best_high_credit_steps_same_length_0_to_scan=max_high_credit_steps(
                    main.length,
                    scan_limit=credit_scan_limit,
                ),
                entry_x_bit_length=entry_bits,
                max_x_bit_length_in_corridor=max_bits,
                max_len_from_entry_bits=max_len_entry,
                max_len_from_max_bits=max_len_max,
                possible_gain_from_entry_bits=max_high_credit_steps(
                    max_len_entry,
                    scan_limit=credit_scan_limit,
                ),
                possible_gain_from_max_bits=max_high_credit_steps(
                    max_len_max,
                    scan_limit=credit_scan_limit,
                ),
            )
        )

    requirement_rows: list[K53CapacityRequirementRow] = []
    high_credit_density = ALPHA - 1.0
    for reserve in required_reserves:
        direct_min_length = math.ceil(reserve / high_credit_density)
        gain_events_needed = direct_min_length
        instruction_min_length = math.ceil(gain_events_needed / high_credit_density)
        min_bits = math.ceil(instruction_min_length * 84 / 53)
        log10_probability = -reserve * math.log10(2)
        log10_expected = reserve * math.log10(2)
        requirement_rows.append(
            K53CapacityRequirementRow(
                required_reserve=reserve,
                direct_min_corridor_length_at_credit_density=direct_min_length,
                high_credit_gain_events_needed=gain_events_needed,
                instruction_min_corridor_length=instruction_min_length,
                min_starting_bit_length=min_bits,
                approximate_integer_log10=min_bits * math.log10(2),
                martingale_probability_upper_bound=2.0 ** (-reserve),
                martingale_log10_probability_upper_bound=log10_probability,
                expected_starts_lower_bound=2.0 ** reserve,
                expected_starts_log10_lower_bound=log10_expected,
            )
        )

    return observed_rows, requirement_rows


def _orbit_value_at_reserve_index(steps: list[Step], reserve_index: int) -> int:
    if not steps:
        raise ValueError("no orbit steps")
    if reserve_index < len(steps):
        return steps[reserve_index].x
    if reserve_index == len(steps):
        last = steps[-1]
        return (3 * last.x + 1) >> last.a
    raise ValueError("reserve index is beyond simulated orbit")


def _beta_distance_to_integer(beta: float) -> float:
    return abs(beta - round(beta))


def _random_odd_with_bit_length(bit_length: int, rng: random.Random) -> int:
    if bit_length < 2:
        raise ValueError("bit_length must be at least 2")
    middle_bits = rng.getrandbits(bit_length - 2)
    return (1 << (bit_length - 1)) | (middle_bits << 1) | 1


def analyze_corridor_bound(
    starts: Iterable[int],
    bit_lengths: Iterable[int] = (50, 100, 200, 500, 1000),
    samples_per_bit_length: int = 100,
    max_steps: int = 2000,
    beta_threshold: float = 0.01,
    random_seed: int = 8675309,
) -> tuple[
    list[CorridorBoundObservedRow],
    list[CorridorBoundSyntheticRow],
    list[CorridorBoundCeilingRow],
]:
    observed_rows: list[CorridorBoundObservedRow] = []
    for start in starts:
        steps = simulate_orbit(start, max_steps=max_steps)
        macros = analyze_macro_corridors(start, max_steps=max_steps)
        k53_rows = [
            row
            for row in macros
            if row.mapped_convergent == 53 and row.positive_action
        ]
        if not k53_rows:
            continue
        main = max(k53_rows, key=lambda row: (row.d_peak, row.length))
        entry_x = _orbit_value_at_reserve_index(steps, main.start_step)
        exit_x = _orbit_value_at_reserve_index(steps, main.end_step)
        consumed = entry_x.bit_length() - exit_x.bit_length()
        observed_rows.append(
            CorridorBoundObservedRow(
                orbit=start,
                start_bit_length=start.bit_length(),
                corridor_index=main.corridor_index,
                start_step=main.start_step,
                end_step=main.end_step,
                length=main.length,
                length_over_start_bits=main.length / start.bit_length(),
                entry_x_bit_length=entry_x.bit_length(),
                exit_x_bit_length=exit_x.bit_length(),
                bits_consumed_entry_minus_exit=consumed,
                bits_consumed_per_step=consumed / main.length,
                peak_reserve=main.d_peak,
            )
        )

    rng = random.Random(random_seed)
    synthetic_rows: list[CorridorBoundSyntheticRow] = []
    for bit_length in bit_lengths:
        for sample_index in range(samples_per_bit_length):
            start = _random_odd_with_bit_length(bit_length, rng)
            orbit = analyze_orbit(start, max_steps=max_steps)
            macros = analyze_macro_corridors(start, max_steps=max_steps)
            quality_rows = [
                row
                for row in macros
                if _beta_distance_to_integer(row.beta) < beta_threshold
            ]
            best = max(quality_rows, key=lambda row: row.length, default=None)
            synthetic_rows.append(
                CorridorBoundSyntheticRow(
                    bit_length=bit_length,
                    sample_index=sample_index,
                    start=start,
                    max_reserve=orbit["max_reserve"],
                    entered_k53_quality=best is not None,
                    best_corridor_length=best.length if best is not None else None,
                    best_corridor_beta_distance=(
                        _beta_distance_to_integer(best.beta)
                        if best is not None
                        else None
                    ),
                    best_corridor_start_step=best.start_step if best is not None else None,
                    best_corridor_end_step=best.end_step if best is not None else None,
                    length_over_start_bits=(
                        best.length / bit_length
                        if best is not None
                        else None
                    ),
                )
            )

    ceiling_rows: list[CorridorBoundCeilingRow] = []
    for bit_length in bit_lengths:
        max_length = math.floor(bit_length * 53 / 84)
        max_reserve = math.floor((ALPHA - 1.0) * max_length)
        ceiling_rows.append(
            CorridorBoundCeilingRow(
                bit_length=bit_length,
                max_corridor_length=max_length,
                max_reserve=max_reserve,
                bridge_85_possible=max_reserve >= 85,
                bridge_128_possible=max_reserve >= 128,
                martingale_mu_H85_upper_bound=2.0 ** -85,
                martingale_mu_H128_upper_bound=2.0 ** -128,
            )
        )

    return observed_rows, synthetic_rows, ceiling_rows


def _empty_scaling_chunk(
    bit_lengths: Iterable[int],
    thresholds: Iterable[float],
) -> dict:
    return {
        "samples": {bit_length: 0 for bit_length in bit_lengths},
        "positive": {bit_length: 0 for bit_length in bit_lengths},
        "thresholds": {
            (bit_length, threshold): {
                "quality_count": 0,
                "max_length": 0,
                "max_gain": 0,
            }
            for bit_length in bit_lengths
            for threshold in thresholds
        },
    }


def _merge_scaling_chunks(target: dict, source: dict) -> None:
    for bit_length, value in source["samples"].items():
        target["samples"][bit_length] = target["samples"].get(bit_length, 0) + value
    for bit_length, value in source["positive"].items():
        target["positive"][bit_length] = target["positive"].get(bit_length, 0) + value
    for key, value in source["thresholds"].items():
        slot = target["thresholds"].setdefault(
            key,
            {"quality_count": 0, "max_length": 0, "max_gain": 0},
        )
        slot["quality_count"] += value["quality_count"]
        slot["max_length"] = max(slot["max_length"], value["max_length"])
        slot["max_gain"] = max(slot["max_gain"], value["max_gain"])


def _scaling_worker(args: tuple[int, int, int, int, tuple[float, ...], int, int, int]) -> dict:
    bit_length, sample_start, sample_count, max_steps, thresholds, drop_tolerance, min_length, seed = args
    rng = random.Random(seed)
    chunk = _empty_scaling_chunk([bit_length], thresholds)
    for _ in range(sample_count):
        n = _random_odd_with_bit_length(bit_length, rng)
        steps = simulate_orbit(n, max_steps=max_steps)
        d_values = reserve_values(steps)
        ranges = find_macro_corridor_ranges(
            d_values,
            drop_tolerance=drop_tolerance,
            min_length=min_length,
        )
        chunk["samples"][bit_length] += 1
        any_positive = False
        per_threshold_hit = {threshold: False for threshold in thresholds}

        for start, end in ranges:
            length = end - start
            if length <= 0:
                continue
            A = sum(step.a for step in steps[start:end])
            beta = length * ALPHA - A
            if beta <= 0:
                continue
            any_positive = True
            reserve_gain = max(d_values[start : end + 1]) - d_values[start]
            for threshold in thresholds:
                if beta < threshold:
                    per_threshold_hit[threshold] = True
                    slot = chunk["thresholds"][(bit_length, threshold)]
                    if length > slot["max_length"]:
                        slot["max_length"] = length
                    if reserve_gain > slot["max_gain"]:
                        slot["max_gain"] = reserve_gain

        if any_positive:
            chunk["positive"][bit_length] += 1
        for threshold, hit in per_threshold_hit.items():
            if hit:
                chunk["thresholds"][(bit_length, threshold)]["quality_count"] += 1

    return chunk


def _linear_fit(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    n = len(xs)
    if n == 0:
        return 0.0, 0.0, 0.0
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    sxx = sum((x - mean_x) ** 2 for x in xs)
    if sxx == 0:
        return 0.0, mean_y, 0.0
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    a = sxy / sxx
    b = mean_y - a * mean_x
    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    ss_res = sum((y - (a * x + b)) ** 2 for x, y in zip(xs, ys))
    r2 = 1.0 if ss_tot == 0 and ss_res == 0 else 1.0 - ss_res / ss_tot if ss_tot else 0.0
    return a, b, r2


def _invert_fit(model: str, a: float, b: float, target_y: float) -> float | None:
    if a <= 0:
        return None
    z = (target_y - b) / a
    if model == "linear":
        return max(0.0, z)
    if model == "log":
        if z > 700:
            return math.inf
        return math.exp(z)
    if model == "sqrt":
        return max(0.0, z) ** 2
    return None


def analyze_scaling_sweep(
    bit_lengths: Iterable[int] = (50, 100, 200, 500, 1000, 2000),
    thresholds: Iterable[float] = (0.5, 0.1, 0.05),
    samples_per_bit_length: int = 10000,
    max_steps: int = 50000,
    workers: int | None = None,
    chunk_size: int = 100,
    random_seed: int = 424242,
    drop_tolerance: int = 2,
    min_length: int = 1,
    required_reserves: Iterable[int] = (85, 128),
) -> tuple[list[ScalingSweepSummaryRow], list[ScalingSweepFitRow], list[ScalingSweepKillRow]]:
    bit_lengths = tuple(bit_lengths)
    thresholds = tuple(thresholds)
    aggregate = _empty_scaling_chunk(bit_lengths, thresholds)
    tasks = []
    for bit_length in bit_lengths:
        for sample_start in range(0, samples_per_bit_length, chunk_size):
            sample_count = min(chunk_size, samples_per_bit_length - sample_start)
            seed = random_seed + bit_length * 1_000_003 + sample_start
            tasks.append(
                (
                    bit_length,
                    sample_start,
                    sample_count,
                    max_steps,
                    thresholds,
                    drop_tolerance,
                    min_length,
                    seed,
                )
            )

    workers = workers or max(1, (os.cpu_count() or 2) - 1)
    with Pool(processes=workers) as pool:
        for chunk in pool.imap_unordered(_scaling_worker, tasks):
            _merge_scaling_chunks(aggregate, chunk)

    summary_rows: list[ScalingSweepSummaryRow] = []
    for threshold in thresholds:
        for bit_length in bit_lengths:
            samples = aggregate["samples"][bit_length]
            positive = aggregate["positive"][bit_length]
            slot = aggregate["thresholds"][(bit_length, threshold)]
            max_length = slot["max_length"]
            max_gain = slot["max_gain"]
            summary_rows.append(
                ScalingSweepSummaryRow(
                    beta_threshold=threshold,
                    bit_length=bit_length,
                    samples=samples,
                    positive_corridor_orbits=positive,
                    quality_corridor_orbits=slot["quality_count"],
                    fraction_entering_positive_corridor=positive / samples if samples else 0.0,
                    fraction_entering_quality_corridor=slot["quality_count"] / samples if samples else 0.0,
                    max_length=max_length,
                    max_length_over_bits=max_length / bit_length if bit_length else 0.0,
                    max_reserve_gain=max_gain,
                    max_gain_per_step=max_gain / max_length if max_length else 0.0,
                )
            )

    fit_rows: list[ScalingSweepFitRow] = []
    kill_rows: list[ScalingSweepKillRow] = []
    for threshold in thresholds:
        rows = [row for row in summary_rows if row.beta_threshold == threshold]
        xs = [float(row.bit_length) for row in rows]
        ys = [float(row.max_length) for row in rows]
        candidates = [
            ("linear", xs),
            ("log", [math.log(x) for x in xs]),
            ("sqrt", [math.sqrt(x) for x in xs]),
        ]
        threshold_fit_rows = []
        for model, transformed_xs in candidates:
            a, b, r2 = _linear_fit(transformed_xs, ys)
            row = ScalingSweepFitRow(
                beta_threshold=threshold,
                model=model,
                coefficient_a=a,
                coefficient_b=b,
                r_squared=r2,
            )
            fit_rows.append(row)
            threshold_fit_rows.append(row)

        best_fit = max(threshold_fit_rows, key=lambda row: row.r_squared)
        observed_gain_per_step = max((row.max_gain_per_step for row in rows), default=0.0)
        if observed_gain_per_step <= 0:
            observed_gain_per_step = ALPHA - 1.0
        for reserve in required_reserves:
            required_length = math.ceil(reserve / observed_gain_per_step)
            required_bits = _invert_fit(
                best_fit.model,
                best_fit.coefficient_a,
                best_fit.coefficient_b,
                required_length,
            )
            log10_mu = -reserve * math.log10(2)
            kill_rows.append(
                ScalingSweepKillRow(
                    beta_threshold=threshold,
                    required_reserve=reserve,
                    best_model=best_fit.model,
                    best_model_r_squared=best_fit.r_squared,
                    observed_gain_per_step=observed_gain_per_step,
                    required_corridor_length=required_length,
                    required_bit_length=required_bits,
                    expected_below_1e80_log10=80 + log10_mu,
                    expected_below_1e120_log10=120 + log10_mu,
                    expected_below_1e500_log10=500 + log10_mu,
                )
            )

    return summary_rows, fit_rows, kill_rows


def analyze_macro_convergent_summary(
    starts: Iterable[int],
    max_steps: int = 100000,
) -> list[MacroConvergentSummaryRow]:
    rows: list[MacroConvergentSummaryRow] = []
    for start in starts:
        orbit = analyze_orbit(start, max_steps=max_steps)
        macros = analyze_macro_corridors(start, max_steps=max_steps)
        positive = [row for row in macros if row.positive_action]
        max_mapped = max((row.mapped_convergent for row in positive), default=None)
        best = max(
            positive,
            key=lambda row: (row.d_peak, row.length, row.mapped_convergent),
            default=None,
        )
        rows.append(
            MacroConvergentSummaryRow(
                start=start,
                max_reserve=orbit["max_reserve"],
                time_max=orbit["time_max"],
                crossing_time=orbit["crossing_time"],
                macro_corridors=len(macros),
                positive_macro_corridors=len(positive),
                max_mapped_convergent=max_mapped,
                has_k53_or_higher=max_mapped is not None and max_mapped >= 53,
                has_k359_or_higher=max_mapped is not None and max_mapped >= 359,
                best_corridor_index=best.corridor_index if best is not None else None,
                best_corridor_start=best.start_step if best is not None else None,
                best_corridor_end=best.end_step if best is not None else None,
                best_corridor_length=best.length if best is not None else None,
                best_corridor_A=best.A if best is not None else None,
                best_corridor_beta=best.beta if best is not None else None,
                best_corridor_mapped_convergent=(
                    best.mapped_convergent if best is not None else None
                ),
                best_corridor_peak_reserve=best.d_peak if best is not None else None,
            )
        )
    rows.sort(key=lambda row: (row.max_reserve, -row.start), reverse=True)
    return rows


def scan_starters(limit: int, min_reserve: int, max_steps: int = 10000) -> list[dict]:
    hits: list[dict] = []
    for n in range(3, limit + 1, 2):
        result = analyze_orbit(n, max_steps=max_steps)
        if result["max_reserve"] >= min_reserve:
            hits.append(
                {
                    "start": n,
                    "max_reserve": result["max_reserve"],
                    "time_max": result["time_max"],
                    "crossing_time": result["crossing_time"],
                    "num_growth_steps": result["num_growth_steps"],
                    "num_segments": result["num_segments"],
                }
            )
    hits.sort(key=lambda row: (row["max_reserve"], -row["start"]), reverse=True)
    return hits


def reserve_profile(n: int, max_steps: int = 10000) -> dict:
    if n <= 0 or n % 2 == 0:
        raise ValueError("n must be a positive odd integer")

    x = n
    A = 0
    max_reserve = 0
    time_max = 0
    growth_steps = 0

    for k in range(max_steps):
        d_before = math.floor(k * ALPHA) - A
        x, a = odd_syracuse_step(x)
        A += a
        d_after = math.floor((k + 1) * ALPHA) - A
        if d_after > d_before:
            growth_steps += 1
        if d_after > max_reserve:
            max_reserve = d_after
            time_max = k + 1
        if d_after < 0:
            return {
                "start": n,
                "max_reserve": max_reserve,
                "time_max": time_max,
                "crossing_time": k + 1,
                "growth_steps": growth_steps,
            }

    return {
        "start": n,
        "max_reserve": max_reserve,
        "time_max": time_max,
        "crossing_time": -1,
        "growth_steps": growth_steps,
    }


def _scan_range_worker(args: tuple[int, int, int, int]) -> list[dict]:
    start, stop, min_reserve, max_steps = args
    rows = []
    for n in range(start, stop, 2):
        row = reserve_profile(n, max_steps=max_steps)
        if row["max_reserve"] >= min_reserve:
            rows.append(row)
    return rows


def scan_starters_range_parallel(
    start: int,
    stop: int,
    min_reserve: int,
    max_steps: int = 10000,
    workers: int | None = None,
    chunk_odds: int = 100000,
) -> list[dict]:
    if start % 2 == 0:
        start += 1
    if stop % 2 == 0:
        stop -= 1
    if stop < start:
        return []

    workers = workers or max(1, (os.cpu_count() or 2) - 1)
    chunk_width = chunk_odds * 2
    tasks = []
    chunk_start = start
    while chunk_start <= stop:
        chunk_stop = min(stop + 1, chunk_start + chunk_width)
        if chunk_stop % 2 == 0:
            chunk_stop += 1
        tasks.append((chunk_start, chunk_stop, min_reserve, max_steps))
        chunk_start = chunk_stop

    rows: list[dict] = []
    with Pool(processes=workers) as pool:
        for chunk_rows in pool.imap_unordered(_scan_range_worker, tasks):
            rows.extend(chunk_rows)

    rows.sort(key=lambda row: (row["max_reserve"], -row["start"]), reverse=True)
    return rows


def scan_starters_parallel(
    limit: int,
    min_reserve: int,
    max_steps: int = 10000,
    workers: int | None = None,
    chunk_odds: int = 100000,
) -> list[dict]:
    workers = workers or max(1, (os.cpu_count() or 2) - 1)
    chunk_width = chunk_odds * 2
    tasks = []
    start = 3
    while start <= limit:
        stop = min(limit + 1, start + chunk_width)
        if stop % 2 == 0:
            stop += 1
        tasks.append((start, stop, min_reserve, max_steps))
        start = stop

    rows: list[dict] = []
    with Pool(processes=workers) as pool:
        for chunk_rows in pool.imap_unordered(_scan_range_worker, tasks):
            rows.extend(chunk_rows)

    rows.sort(key=lambda row: (row["max_reserve"], -row["start"]), reverse=True)
    return rows


def phase_profile(n: int, period: int, max_steps: int = 100000) -> dict:
    steps = simulate_orbit(n, max_steps=max_steps)
    growth_steps = [s for s in steps if s.growing]
    residues: dict[int, int] = {}
    for step in growth_steps:
        residue = step.k % period
        residues[residue] = residues.get(residue, 0) + 1
    return {
        "start": n,
        "period": period,
        "total_steps": len(steps),
        "growth_steps": len(growth_steps),
        "residues": dict(sorted(residues.items())),
        "growth_k": [s.k for s in growth_steps],
    }


def write_orbit_outputs(result: dict, out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    start = result["start"]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    prefix = out_dir / f"orbit_{start}_{stamp}"

    summary_path = prefix.with_suffix(".summary.json")
    segments_path = prefix.with_suffix(".segments.csv")
    seams_path = prefix.with_suffix(".seams.csv")

    summary = {
        key: value
        for key, value in result.items()
        if key not in {"steps", "segments", "seams"}
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    _write_csv(segments_path, (asdict(s) for s in result["segments"]))
    _write_csv(seams_path, (asdict(s) for s in result["seams"]))
    return {"summary": summary_path, "segments": segments_path, "seams": seams_path}


def write_scan_outputs(rows: list[dict], out_dir: Path, limit: int, min_reserve: int) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"scan_limit{limit}_D{min_reserve}_{stamp}.csv"
    _write_csv(path, rows)
    return path


def write_scan_range_outputs(
    rows: list[dict],
    out_dir: Path,
    start: int,
    stop: int,
    min_reserve: int,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"scan_range_{start}_{stop}_D{min_reserve}_{stamp}.csv"
    _write_csv(path, rows)
    return path


def odd_count_inclusive(start: int, stop: int) -> int:
    if stop < start:
        return 0
    return ((stop + 1) // 2) - (start // 2)


def _fit_tail_line(points: list[tuple[int, float]]) -> tuple[float, float, float]:
    n = len(points)
    if n < 2:
        raise ValueError("at least two nonzero threshold points are required")
    sx = sum(d for d, _ in points)
    sy = sum(y for _, y in points)
    sxx = sum(d * d for d, _ in points)
    sxy = sum(d * y for d, y in points)
    denom = n * sxx - sx * sx
    if denom == 0:
        raise ValueError("fit thresholds must not all be equal")
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    mean_y = sy / n
    ss_res = sum((y - (intercept + slope * d)) ** 2 for d, y in points)
    ss_tot = sum((y - mean_y) ** 2 for _, y in points)
    r_squared = 1.0 if ss_tot == 0 else 1.0 - ss_res / ss_tot
    return intercept, slope, r_squared


def _read_scan_reserve_counts(path: Path) -> dict[int, int]:
    counts: dict[int, int] = {}
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames or "max_reserve" not in reader.fieldnames:
            raise ValueError(f"{path} is missing a max_reserve column")
        for row in reader:
            reserve = int(row["max_reserve"])
            counts[reserve] = counts.get(reserve, 0) + 1
    return counts


def analyze_tail_law(
    scanned_ranges: list[tuple[int, int, Path]],
    min_threshold: int = 23,
    fit_min_thresholds: list[int] | None = None,
    target_reserves: list[int] | None = None,
) -> tuple[
    list[TailThresholdRow],
    list[TailFitRow],
    list[TailProjectionRow],
    list[TailZeroBoundRow],
]:
    total_odds = 0
    exact_counts: dict[int, int] = {}
    for start, stop, path in scanned_ranges:
        total_odds += odd_count_inclusive(start, stop)
        for reserve, count in _read_scan_reserve_counts(path).items():
            exact_counts[reserve] = exact_counts.get(reserve, 0) + count

    if total_odds <= 0:
        raise ValueError("scanned ranges contain no odd starts")

    max_observed = max(exact_counts, default=min_threshold - 1)
    max_threshold = max(max_observed, min_threshold)
    threshold_rows: list[TailThresholdRow] = []
    fit_points: dict[int, float] = {}
    for threshold in range(min_threshold, max_threshold + 1):
        count = sum(c for reserve, c in exact_counts.items() if reserve >= threshold)
        rate = count / total_odds
        log_rate = math.log10(rate) if count else None
        if log_rate is not None:
            fit_points[threshold] = log_rate
        threshold_rows.append(
            TailThresholdRow(
                threshold_reserve=threshold,
                count_at_least_threshold=count,
                odd_starts_scanned=total_odds,
                empirical_rate=rate,
                log10_empirical_rate=log_rate,
            )
        )

    fit_min_thresholds = fit_min_thresholds or list(
        range(min_threshold, max_threshold)
    )
    target_reserves = target_reserves or [32, 40, 53, 85, 128]

    fit_rows: list[TailFitRow] = []
    projection_rows: list[TailProjectionRow] = []
    for fit_min in fit_min_thresholds:
        points = [(d, y) for d, y in sorted(fit_points.items()) if d >= fit_min]
        if len(points) < 2:
            continue
        intercept, slope, r_squared = _fit_tail_line(points)
        fit_max = max(d for d, _ in points)
        fit_rows.append(
            TailFitRow(
                fit_min_threshold=fit_min,
                fit_max_threshold=fit_max,
                points=len(points),
                intercept_log10=intercept,
                slope_per_reserve_log10=slope,
                per_reserve_factor=10**slope,
                r_squared=r_squared,
            )
        )
        for target in target_reserves:
            projected_log_rate = intercept + slope * target
            projection_rows.append(
                TailProjectionRow(
                    fit_min_threshold=fit_min,
                    target_reserve=target,
                    projected_log10_rate=projected_log_rate,
                    projected_expected_odd_starts_log10=-projected_log_rate,
                )
            )

    zero_threshold = max_observed + 1
    upper_rate = 3.0 / total_odds
    zero_rows = [
        TailZeroBoundRow(
            threshold_reserve=zero_threshold,
            odd_starts_scanned=total_odds,
            zero_hit_95_upper_rate=upper_rate,
            zero_hit_95_upper_rate_log10=math.log10(upper_rate),
            expected_odd_starts_95_lower_log10=math.log10(total_odds / 3.0),
        )
    ]
    return threshold_rows, fit_rows, projection_rows, zero_rows


def write_tail_law_outputs(
    threshold_rows: list[TailThresholdRow],
    fit_rows: list[TailFitRow],
    projection_rows: list[TailProjectionRow],
    zero_rows: list[TailZeroBoundRow],
    out_dir: Path,
    label: str = "tail_law",
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    thresholds_path = out_dir / f"{label}_thresholds_{stamp}.csv"
    fits_path = out_dir / f"{label}_fits_{stamp}.csv"
    projections_path = out_dir / f"{label}_projections_{stamp}.csv"
    zero_path = out_dir / f"{label}_zero_bound_{stamp}.csv"
    _write_csv(thresholds_path, (asdict(row) for row in threshold_rows))
    _write_csv(fits_path, (asdict(row) for row in fit_rows))
    _write_csv(projections_path, (asdict(row) for row in projection_rows))
    _write_csv(zero_path, (asdict(row) for row in zero_rows))
    return {
        "thresholds": thresholds_path,
        "fits": fits_path,
        "projections": projections_path,
        "zero_bound": zero_path,
    }


def _compositions_fixed_length(total: int, length: int) -> Iterable[tuple[int, ...]]:
    if length <= 0:
        return
    if length == 1:
        if total >= 1:
            yield (total,)
        return
    max_first = total - length + 1
    for first in range(1, max_first + 1):
        for suffix in _compositions_fixed_length(total - first, length - 1):
            yield (first, *suffix)


def _first_contractivity_words_up_to(
    Amax: int,
) -> Iterable[tuple[tuple[int, ...], int]]:
    powers2 = [1 << i for i in range(Amax + 1)]
    powers3 = [1]
    for _ in range(Amax):
        powers3.append(powers3[-1] * 3)
    max_solvent_sum = [value.bit_length() - 1 for value in powers3]

    def rec(prefix: list[int], prefix_sum: int, prefix_B: int) -> Iterable[tuple[tuple[int, ...], int]]:
        prefix_len = len(prefix)
        final_len = prefix_len + 1
        if final_len <= Amax:
            min_final_A = max(prefix_sum + 1, max_solvent_sum[final_len] + 1)
            for final_A in range(min_final_A, Amax + 1):
                final_a = final_A - prefix_sum
                word = (*prefix, final_a)
                B = 3 * prefix_B + powers2[prefix_sum]
                yield word, B

        next_len = prefix_len + 1
        if next_len >= Amax:
            return
        max_a = min(Amax - 1 - prefix_sum, max_solvent_sum[next_len] - prefix_sum)
        for a in range(1, max_a + 1):
            next_sum = prefix_sum + a
            next_B = 3 * prefix_B + powers2[prefix_sum]
            prefix.append(a)
            yield from rec(prefix, next_sum, next_B)
            prefix.pop()

    yield from rec([], 0, 0)


def _max_run_by_predicate(word: tuple[int, ...], predicate) -> int:
    best = 0
    current = 0
    for value in word:
        if predicate(value):
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def _primitive_period(word: tuple[int, ...]) -> tuple[int, int]:
    k = len(word)
    for period in range(1, k + 1):
        if k % period != 0:
            continue
        block = word[:period]
        if all(word[i : i + period] == block for i in range(0, k, period)):
            return period, k // period
    return k, 1


def _theta_candidate_bucket(candidate_odd_count: int) -> str:
    if candidate_odd_count <= 5:
        return str(candidate_odd_count)
    if candidate_odd_count <= 10:
        return "6-10"
    if candidate_odd_count <= 100:
        return "11-100"
    if candidate_odd_count <= 1000:
        return "101-1000"
    return ">1000"


def _rho_bit_slack_bucket(slack: int) -> str:
    if slack <= 4:
        return str(slack)
    if slack <= 8:
        return "5-8"
    if slack <= 16:
        return "9-16"
    return ">16"


def word_affine_B(word: tuple[int, ...]) -> int:
    k = len(word)
    A_prefix = 0
    B = 0
    for j, a in enumerate(word):
        B += (3 ** (k - 1 - j)) * (2**A_prefix)
        A_prefix += a
    return B


def lock2_rho_for_word(word: tuple[int, ...], B: int | None = None) -> int:
    A = sum(word)
    k = len(word)
    B = word_affine_B(word) if B is None else B
    modulus = 1 << (A + 1)
    rho = (((1 << A) - B) * pow(3**k, -1, modulus)) % modulus
    if rho == 0:
        return modulus
    return rho


def first_contractivity_index_for_word(word: tuple[int, ...]) -> int | None:
    A_prefix = 0
    for idx, a in enumerate(word, start=1):
        A_prefix += a
        if (1 << A_prefix) > 3**idx:
            return idx
    return None


def exponent_prefix_from_start(n: int, length: int) -> tuple[int, ...]:
    x = n
    word = []
    for _ in range(length):
        x, a = odd_syracuse_step(x)
        word.append(a)
    return tuple(word)


def lock3_inverse_step(x_next: int, a: int) -> int | None:
    if x_next <= 0 or x_next % 2 == 0:
        raise ValueError("x_next must be a positive odd integer")
    if a < 1:
        raise ValueError("a must be positive")
    numerator = (1 << a) * x_next - 1
    if numerator <= 0 or numerator % 3:
        return None
    x_prev = numerator // 3
    if x_prev <= 0 or x_prev % 2 == 0:
        return None
    return x_prev


def lock3_mod3_gate_residue(a: int) -> int:
    if a < 1:
        raise ValueError("a must be positive")
    return 1 if a % 2 == 0 else 2


def lock3_critical_word(depth: int) -> tuple[int, ...]:
    if depth < 0:
        raise ValueError("depth must be non-negative")
    return tuple(credit_at_step(k) for k in range(depth))


def lock3_deficit_path(word: tuple[int, ...], initial_deficit: int = 0) -> tuple[int, ...]:
    deficits = [initial_deficit]
    d = initial_deficit
    for k, a in enumerate(word):
        d = d + credit_at_step(k) - a
        deficits.append(d)
    return tuple(deficits)


def lock3_rho_for_prefix(word: tuple[int, ...], B: int | None = None) -> int:
    return lock2_rho_for_word(word, B=B)


def _lock3_rho_from_affine(A: int, B: int, pow3: int) -> int:
    modulus = 1 << (A + 1)
    rho = (((1 << A) - B) * pow(pow3 % modulus, -1, modulus)) % modulus
    if rho == 0:
        return modulus
    return rho


def _lock3_lift_rho(
    previous_rho: int | None,
    previous_A: int,
    A: int,
    B: int,
    pow3: int,
) -> int:
    if previous_rho is None:
        return _lock3_rho_from_affine(A, B, pow3)
    old_modulus = 1 << (previous_A + 1)
    modulus = 1 << (A + 1)
    target = ((1 << A) - B) % modulus
    coefficient = pow3 & (modulus - 1)
    for lift_digit in range(1 << (A - previous_A)):
        candidate = previous_rho + lift_digit * old_modulus
        if (coefficient * candidate) % modulus == target:
            return modulus if candidate == 0 else candidate
    return _lock3_rho_from_affine(A, B, pow3)


def lock3_backward_from_terminal(
    word: tuple[int, ...],
    terminal_value: int = 1,
) -> tuple[bool, int | None, int | None, str]:
    x = terminal_value
    for backward_depth, a in enumerate(reversed(word), start=1):
        previous = lock3_inverse_step(x, a)
        if previous is None:
            return False, None, backward_depth, "inverse_divisibility_failed"
        x = previous
    return True, x, None, ""


def lock3_terminal_residue_class(word: tuple[int, ...], B: int | None = None) -> tuple[int, int]:
    depth = len(word)
    A = sum(word)
    B = word_affine_B(word) if B is None else B
    modulus = 3**depth
    return _lock3_terminal_residue_class_from_affine(A, B, modulus)


def _lock3_terminal_residue_class_from_affine(A: int, B: int, pow3: int) -> tuple[int, int]:
    modulus = pow3
    if modulus == 1:
        return 1, 0
    residue = (B * pow(pow(2, A, modulus), -1, modulus)) % modulus
    return modulus, residue


def _encode_ints(values: tuple[int, ...]) -> str:
    return ",".join(str(value) for value in values)


def _lock3_terminal_check_from_affine(
    A: int,
    B: int,
    pow3: int,
    terminal_value: int,
) -> tuple[bool, int | None]:
    numerator = (1 << A) * terminal_value - B
    if numerator <= 0 or numerator % pow3:
        return False, None
    ancestor = numerator // pow3
    if ancestor <= 0 or ancestor % 2 == 0:
        return False, None
    return True, ancestor


def _lock3_path_row(
    C: int,
    deficits: tuple[int, ...],
    word: tuple[int, ...],
    terminal_value: int,
) -> Lock3BackwardPathRow:
    valid, ancestor, failure_depth, reason = lock3_backward_from_terminal(word, terminal_value)
    modulus, residue = lock3_terminal_residue_class(word)
    return Lock3BackwardPathRow(
        C=C,
        depth=len(word),
        deficit_path_encoded=_encode_ints(deficits),
        exponent_word=_encode_ints(word),
        terminal_value=terminal_value,
        ancestor_value=ancestor,
        valid_all_steps=valid,
        first_failure_depth=failure_depth,
        failure_reason=reason,
        final_modulus=modulus,
        residue_class=residue,
    )


def _lock3_path_row_from_state(
    C: int,
    state: Lock3SearchState,
    terminal_value: int,
) -> Lock3BackwardPathRow:
    valid, ancestor, failure_depth, reason = lock3_backward_from_terminal(
        state.word,
        terminal_value,
    )
    modulus, residue = _lock3_terminal_residue_class_from_affine(
        state.A,
        state.B,
        state.pow3,
    )
    return Lock3BackwardPathRow(
        C=C,
        depth=len(state.word),
        deficit_path_encoded=_encode_ints(state.deficits),
        exponent_word=_encode_ints(state.word),
        terminal_value=terminal_value,
        ancestor_value=ancestor,
        valid_all_steps=valid,
        first_failure_depth=failure_depth,
        failure_reason=reason,
        final_modulus=modulus,
        residue_class=residue,
    )


def _format_ratio(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0"
    return f"{numerator / denominator:.12g}"


def _update_lock3_census_witness(
    state: Lock3CensusWitnessState,
    d_next: int,
    a: int,
) -> Lock3CensusWitnessState:
    next_A = state.A + a
    next_B = 3 * state.B + (1 << state.A)
    next_pow3 = state.pow3 * 3
    rho = _lock3_lift_rho(
        state.previous_rho,
        state.A,
        next_A,
        next_B,
        next_pow3,
    )
    rho_changed = state.previous_rho is None or rho != state.previous_rho
    next_lift_count = state.lift_count + int(
        rho_changed and state.previous_rho is not None
    )
    next_plateau = 0 if rho_changed else state.current_plateau + 1
    next_longest_plateau = max(state.longest_plateau, next_plateau)
    return Lock3CensusWitnessState(
        deficits=(*state.deficits, d_next),
        word=(*state.word, a),
        A=next_A,
        B=next_B,
        pow3=next_pow3,
        previous_rho=rho,
        lift_count=next_lift_count,
        current_plateau=next_plateau,
        longest_plateau=next_longest_plateau,
    )


def _lock3_witness_record(
    C: int,
    depth: int,
    witness_type: str,
    state: Lock3CensusWitnessState,
    notes: str,
) -> dict:
    rho = state.previous_rho
    return {
        "C": C,
        "depth": depth,
        "witness_type": witness_type,
        "deficit_path": _encode_ints(state.deficits),
        "exponent_word": _encode_ints(state.word),
        "A_k": state.A,
        "rho_k": rho,
        "modulus_bits": state.A + 1,
        "lift_count": state.lift_count,
        "plateau_length": state.current_plateau,
        "longest_plateau": state.longest_plateau,
        "notes": notes,
    }


def _lock3_residue_modulus(depth: int, residue_mod_power: int) -> int:
    if residue_mod_power <= 0:
        return 1
    return 3 ** min(depth, residue_mod_power)


def _lock3_next_terminal_residue_signature(
    residue: int,
    exponent: int,
    modulus: int,
) -> int:
    if modulus == 1:
        return 0
    inv = pow(pow(2, exponent, modulus), -1, modulus)
    return ((3 * residue + 1) * inv) % modulus


def analyze_lock3_census(
    C: int,
    depth: int,
    terminal_value: int = 1,
    residue_mod_power: int = 8,
    progress_callback: Callable[[dict], None] | None = None,
) -> tuple[dict, list[Lock3CensusRow], list[Lock3CensusEventRow], list[dict]]:
    if C < 0:
        raise ValueError("C must be non-negative")
    if depth < 0:
        raise ValueError("depth must be non-negative")
    if terminal_value <= 0 or terminal_value % 2 == 0:
        raise ValueError("terminal_value must be a positive odd integer")
    if residue_mod_power < 0:
        raise ValueError("residue_mod_power must be non-negative")

    initial = Lock3CensusWitnessState(
        deficits=(0,),
        word=(),
        A=0,
        B=0,
        pow3=1,
        previous_rho=None,
        lift_count=0,
        current_plateau=0,
        longest_plateau=0,
    )
    counts: dict[tuple[int, int], int] = {(0, 0): 1}
    witnesses: dict[tuple[int, int], Lock3CensusWitnessState] = {(0, 0): initial}
    rows: list[Lock3CensusRow] = []
    events: list[Lock3CensusEventRow] = []
    witness_records: list[dict] = []
    max_symbolic_branch_count = 0
    max_merged_state_count = 0
    max_longest_plateau = 0
    max_rho_bit_length = 0
    max_valid_from_1_count = 0
    near_returns: list[int] = []

    for next_depth in range(1, depth + 1):
        c = credit_at_step(next_depth - 1)
        residue_modulus = _lock3_residue_modulus(next_depth, residue_mod_power)
        terminal_residue_signature = terminal_value % residue_modulus
        next_counts: dict[tuple[int, int], int] = {}
        next_witnesses: dict[tuple[int, int], Lock3CensusWitnessState] = {}
        next_exponents: dict[tuple[int, int], int] = {}

        for (d, residue), multiplicity in counts.items():
            witness = witnesses[(d, residue)]
            for d_next in range(C + 1):
                a = d + c - d_next
                if a < 1:
                    continue
                next_residue = _lock3_next_terminal_residue_signature(
                    residue,
                    a,
                    residue_modulus,
                )
                key = (d_next, next_residue)
                next_counts[key] = next_counts.get(key, 0) + multiplicity
                if key not in next_witnesses:
                    next_witnesses[key] = _update_lock3_census_witness(
                        witness,
                        d_next,
                        a,
                    )
                    next_exponents[key] = a

        counts = next_counts
        witnesses = next_witnesses
        symbolic_branch_count = sum(counts.values())
        merged_state_count = len(counts)
        max_branch_multiplicity = max(counts.values(), default=0)
        residue_signatures = {residue for _, residue in counts}
        valid_residue_count = len(residue_signatures)
        terminal_compatible_items = [
            (key, multiplicity)
            for key, multiplicity in counts.items()
            if key[1] == terminal_residue_signature
        ]
        terminal_1_compatible_signature_count = len(terminal_compatible_items)
        valid_from_1_count = sum(
            multiplicity for _, multiplicity in terminal_compatible_items
        )
        rho_stable_count = sum(
            1 for state in witnesses.values() if state.current_plateau > 0
        )
        rho_lift_count = max((state.lift_count for state in witnesses.values()), default=0)
        longest_plateau = max(
            (state.longest_plateau for state in witnesses.values()),
            default=0,
        )
        row_max_rho_bit_length = max(
            (
                state.previous_rho.bit_length()
                for state in witnesses.values()
                if state.previous_rho is not None
            ),
            default=0,
        )
        notes = (
            "census_by_deficit_and_terminal_residue_signature;"
            "rho_metrics_on_representative_witnesses;"
            f"terminal_compatibility_mod_3^{min(next_depth, residue_mod_power)}"
        )
        row = Lock3CensusRow(
            C=C,
            depth=next_depth,
            residue_mod_power=residue_mod_power,
            residue_modulus=residue_modulus,
            terminal_residue_signature=terminal_residue_signature,
            symbolic_branch_count=symbolic_branch_count,
            merged_state_count=merged_state_count,
            valid_from_1_count=valid_from_1_count,
            terminal_1_compatible_signature_count=terminal_1_compatible_signature_count,
            valid_residue_count=valid_residue_count,
            residue_class_count=valid_residue_count,
            rho_stable_count=rho_stable_count,
            rho_lift_count=rho_lift_count,
            longest_plateau=longest_plateau,
            max_rho_bit_length=row_max_rho_bit_length,
            max_branch_multiplicity=max_branch_multiplicity,
            compression_ratio=_format_ratio(symbolic_branch_count, merged_state_count),
            valid_fraction=_format_ratio(valid_from_1_count, symbolic_branch_count),
            stable_fraction=_format_ratio(rho_stable_count, merged_state_count),
            truncated=False,
            notes=notes,
        )
        rows.append(row)

        if symbolic_branch_count > max_symbolic_branch_count:
            max_symbolic_branch_count = symbolic_branch_count
            events.append(
                Lock3CensusEventRow(
                    C=C,
                    depth=next_depth,
                    event_type="new_max_branch_count",
                    value=str(symbolic_branch_count),
                    branch_id_or_state_id="deficit_census",
                    deficit_state=None,
                    exponent=None,
                    summary=f"symbolic branch count reached {symbolic_branch_count}",
                )
            )
        if merged_state_count > max_merged_state_count:
            max_merged_state_count = merged_state_count
            events.append(
                Lock3CensusEventRow(
                    C=C,
                    depth=next_depth,
                    event_type="new_max_merged_state_count",
                    value=str(merged_state_count),
                    branch_id_or_state_id="deficit_census",
                    deficit_state=None,
                    exponent=None,
                    summary=f"merged deficit states reached {merged_state_count}",
                )
            )
        if valid_from_1_count > max_valid_from_1_count:
            max_valid_from_1_count = valid_from_1_count
            events.append(
                Lock3CensusEventRow(
                    C=C,
                    depth=next_depth,
                    event_type="new_max_terminal_1_compatible_count",
                    value=str(valid_from_1_count),
                    branch_id_or_state_id=f"residue={terminal_residue_signature}",
                    deficit_state=None,
                    exponent=None,
                    summary=(
                        f"{valid_from_1_count} branches compatible with terminal "
                        f"{terminal_value} modulo {residue_modulus}"
                    ),
                )
            )
        if terminal_compatible_items:
            events.append(
                Lock3CensusEventRow(
                    C=C,
                    depth=next_depth,
                    event_type="terminal_1_compatible_signatures",
                    value=str(terminal_1_compatible_signature_count),
                    branch_id_or_state_id=f"residue={terminal_residue_signature}",
                    deficit_state=None,
                    exponent=None,
                    summary=(
                        f"{terminal_1_compatible_signature_count} merged signatures "
                        f"carry {valid_from_1_count} branches compatible with terminal "
                        f"{terminal_value} modulo {residue_modulus}"
                    ),
                )
            )
            for (deficit_state, residue_signature), multiplicity in terminal_compatible_items:
                witness_records.append(
                    _lock3_witness_record(
                        C,
                        next_depth,
                        "terminal_1_compatible_residue_signature",
                        witnesses[(deficit_state, residue_signature)],
                        (
                            f"multiplicity={multiplicity};"
                            f"residue_modulus={residue_modulus};"
                            f"terminal_residue_signature={terminal_residue_signature};"
                            f"deficit={deficit_state}"
                        ),
                    )
                )
        if longest_plateau > max_longest_plateau:
            max_longest_plateau = longest_plateau
            witness_key, witness = max(
                witnesses.items(),
                key=lambda item: item[1].longest_plateau,
            )
            deficit_state, residue_signature = witness_key
            events.append(
                Lock3CensusEventRow(
                    C=C,
                    depth=next_depth,
                    event_type="new_longest_rho_plateau",
                    value=str(longest_plateau),
                    branch_id_or_state_id=f"deficit={deficit_state};residue={residue_signature}",
                    deficit_state=deficit_state,
                    exponent=next_exponents.get(witness_key),
                    summary=f"representative plateau reached {longest_plateau}",
                )
            )
            witness_records.append(
                _lock3_witness_record(
                    C,
                    next_depth,
                    "longest_rho_plateau",
                    witness,
                    "representative witness for merged deficit state",
                )
            )
        if row_max_rho_bit_length > max_rho_bit_length:
            max_rho_bit_length = row_max_rho_bit_length
            witness_key, witness = max(
                witnesses.items(),
                key=lambda item: item[1].previous_rho.bit_length()
                if item[1].previous_rho is not None
                else 0,
            )
            deficit_state, residue_signature = witness_key
            events.append(
                Lock3CensusEventRow(
                    C=C,
                    depth=next_depth,
                    event_type="new_max_rho_bit_length",
                    value=str(row_max_rho_bit_length),
                    branch_id_or_state_id=f"deficit={deficit_state};residue={residue_signature}",
                    deficit_state=deficit_state,
                    exponent=next_exponents.get(witness_key),
                    summary=f"representative rho bit length reached {row_max_rho_bit_length}",
                )
            )
        if next_depth in KNOWN_CF_CONVERGENTS:
            near_returns.append(next_depth)
            for (deficit_state, residue_signature), witness in witnesses.items():
                witness_records.append(
                    _lock3_witness_record(
                        C,
                        next_depth,
                        "near_return_depth",
                        witness,
                        (
                            f"near-return depth {next_depth}; representative for "
                            f"deficit {deficit_state}; terminal residue signature {residue_signature}"
                        ),
                    )
                )

        if progress_callback is not None:
            progress_callback(
                {
                    "C": C,
                    "depth": next_depth,
                    "target_depth": depth,
                    "symbolic_branch_count": symbolic_branch_count,
                    "merged_state_count": merged_state_count,
                    "valid_from_1_count": valid_from_1_count,
                    "terminal_1_compatible_signature_count": terminal_1_compatible_signature_count,
                    "valid_residue_count": valid_residue_count,
                    "residue_modulus": residue_modulus,
                    "rho_lift_count": rho_lift_count,
                    "longest_plateau": longest_plateau,
                    "max_rho_bit_length": row_max_rho_bit_length,
                    "notes": notes,
                }
            )

    summary = {
        "C": C,
        "mode": "census",
        "max_depth": depth,
        "terminal_value": terminal_value,
        "residue_mod_power": residue_mod_power,
        "residue_modulus": rows[-1].residue_modulus if rows else 1,
        "terminal_residue_signature": rows[-1].terminal_residue_signature
        if rows
        else terminal_value % 1,
        "merge_strategy": "deficit_state_and_terminal_residue_signature",
        "symbolic_branch_count": rows[-1].symbolic_branch_count if rows else 1,
        "merged_state_count": rows[-1].merged_state_count if rows else 1,
        "valid_from_1_tracked": True,
        "valid_from_1_is_modular_compatibility": True,
        "valid_from_1_count": rows[-1].valid_from_1_count if rows else 0,
        "terminal_1_compatible_signature_count": rows[
            -1
        ].terminal_1_compatible_signature_count
        if rows
        else 0,
        "valid_residue_count": rows[-1].valid_residue_count if rows else 0,
        "residue_class_count": rows[-1].residue_class_count if rows else 0,
        "residue_class_count_is_proxy": False,
        "rho_metrics_are_representative": True,
        "rho_lift_count": rows[-1].rho_lift_count if rows else 0,
        "longest_plateau": rows[-1].longest_plateau if rows else 0,
        "max_rho_bit_length": rows[-1].max_rho_bit_length if rows else 0,
        "max_branch_multiplicity": rows[-1].max_branch_multiplicity if rows else 1,
        "truncated_depths": [],
        "near_return_times_encountered": near_returns,
        "event_count": len(events),
        "witness_count": len(witness_records),
    }
    return summary, rows, events, witness_records


def _analyze_lock3_c0_census(
    depth: int,
    terminal_value: int,
    max_paths: int,
    progress_callback: Callable[[dict], None] | None,
) -> tuple[dict, list[Lock3SurvivorDepthRow], list[Lock3BackwardPathRow], list[Lock3ResidueLiftRow]]:
    A = 0
    pow3 = 1
    previous_rho: int | None = None
    carry_q = 0
    lift_count = 0
    current_plateau = 0
    longest_plateau = 0
    largest_rho_bit_length = 0
    near_returns: list[int] = []
    survivor_rows: list[Lock3SurvivorDepthRow] = []

    for next_depth in range(1, depth + 1):
        old_A = A
        a = credit_at_step(next_depth - 1)
        A += a
        pow3 *= 3
        if previous_rho is None:
            rho = 3
            B = 1
            carry_q = (pow3 * rho - ((1 << A) - B)) >> (A + 1)
        else:
            lift_modulus = 1 << a
            carry_offset = 1 if a == 1 else 0
            lift_digit = (
                -((3 * carry_q + carry_offset) % lift_modulus)
                * pow(pow3 % lift_modulus, -1, lift_modulus)
            ) % lift_modulus
            rho = previous_rho + lift_digit * (1 << (old_A + 1))
            carry_q = (3 * carry_q + carry_offset + pow3 * lift_digit) >> a

        rho_changed = previous_rho is None or rho != previous_rho
        if previous_rho is not None and rho_changed:
            lift_count += 1
        current_plateau = 0 if rho_changed else current_plateau + 1
        longest_plateau = max(longest_plateau, current_plateau)
        largest_rho_bit_length = max(largest_rho_bit_length, rho.bit_length())
        previous_rho = rho

        row = Lock3SurvivorDepthRow(
            C=0,
            depth=next_depth,
            total_budget_paths=1,
            valid_backward_paths_from_1=0,
            valid_backward_residue_classes=1,
            min_positive_ancestor=None,
            max_positive_ancestor=None,
            branch_count=1,
            notes="terminal_checks_skipped",
        )
        survivor_rows.append(row)
        if next_depth in KNOWN_CF_CONVERGENTS:
            near_returns.append(next_depth)
        if progress_callback is not None:
            progress_callback(
                {
                    "C": 0,
                    "depth": next_depth,
                    "target_depth": depth,
                    "total_budget_paths": 1,
                    "total_paths_considered": next_depth,
                    "branch_count": 1,
                    "valid_backward_paths_from_1": 0,
                    "valid_backward_residue_classes": 1,
                    "largest_rho_bit_length": largest_rho_bit_length,
                    "notes": row.notes,
                }
            )

    summary = {
        "C": 0,
        "max_depth": depth,
        "terminal_value": terminal_value,
        "max_paths": max_paths,
        "total_paths_considered": depth,
        "survivor_counts": {
            str(row.depth): row.valid_backward_paths_from_1
            for row in survivor_rows
        },
        "branch_counts": {
            str(row.depth): row.branch_count
            for row in survivor_rows
        },
        "any_path_appears_extendable": depth > 0,
        "rho_representatives_stabilize": False,
        "longest_stable_plateau": longest_plateau,
        "number_of_lift_events": lift_count,
        "largest_rho_bit_length": largest_rho_bit_length,
        "near_return_times_encountered": near_returns,
        "truncated_depths": [],
        "terminal_checks_skipped": True,
    }
    return summary, survivor_rows, [], []


def analyze_lock3_backward(
    C: int,
    depth: int,
    terminal_value: int = 1,
    max_paths: int = 200000,
    max_path_rows: int = 20000,
    max_lift_rows: int = 200000,
    skip_terminal_checks: bool = False,
    progress_callback: Callable[[dict], None] | None = None,
) -> tuple[dict, list[Lock3SurvivorDepthRow], list[Lock3BackwardPathRow], list[Lock3ResidueLiftRow]]:
    if C < 0:
        raise ValueError("C must be non-negative")
    if depth < 0:
        raise ValueError("depth must be non-negative")
    if terminal_value <= 0 or terminal_value % 2 == 0:
        raise ValueError("terminal_value must be a positive odd integer")
    if C == 0 and skip_terminal_checks and max_path_rows == 0 and max_lift_rows == 0:
        return _analyze_lock3_c0_census(
            depth,
            terminal_value,
            max_paths,
            progress_callback,
        )

    states: list[Lock3SearchState] = [
        Lock3SearchState(
            deficits=(0,),
            word=(),
            A=0,
            B=0,
            pow3=1,
            previous_rho=None,
            lift_count=0,
            current_plateau=0,
            longest_plateau=0,
        )
    ]
    survivor_rows: list[Lock3SurvivorDepthRow] = []
    path_rows: list[Lock3BackwardPathRow] = []
    lift_rows: list[Lock3ResidueLiftRow] = []
    total_paths_considered = 0
    truncated_depths: list[int] = []
    largest_rho_bit_length = 0
    near_returns: list[int] = []

    for next_depth in range(1, depth + 1):
        new_states: list[Lock3SearchState] = []
        total_budget_paths = 0
        c = credit_at_step(next_depth - 1)
        for state in states:
            d = state.deficits[-1]
            for d_next in range(C + 1):
                a = d + c - d_next
                if a < 1:
                    continue
                total_budget_paths += 1
                if len(new_states) >= max_paths:
                    continue
                next_A = state.A + a
                next_B = 3 * state.B + (1 << state.A)
                next_pow3 = state.pow3 * 3
                rho = _lock3_lift_rho(
                    state.previous_rho,
                    state.A,
                    next_A,
                    next_B,
                    next_pow3,
                )
                rho_changed = state.previous_rho is None or rho != state.previous_rho
                next_lift_count = state.lift_count + int(
                    rho_changed and state.previous_rho is not None
                )
                next_plateau = 0 if rho_changed else state.current_plateau + 1
                next_longest_plateau = max(state.longest_plateau, next_plateau)
                largest_rho_bit_length = max(largest_rho_bit_length, rho.bit_length())
                if len(lift_rows) < max_lift_rows:
                    lift_rows.append(
                        Lock3ResidueLiftRow(
                            C=C,
                            depth=next_depth,
                            A_k=next_A,
                            modulus=1 << (next_A + 1),
                            rho_k=rho,
                            bit_length_rho=rho.bit_length(),
                            rho_changed=rho_changed,
                            lift_amount=0
                            if state.previous_rho is None
                            else rho - state.previous_rho,
                            deficit_state=d_next,
                            exponent=a,
                        )
                    )
                new_states.append(
                    Lock3SearchState(
                        deficits=(*state.deficits, d_next),
                        word=(*state.word, a),
                        A=next_A,
                        B=next_B,
                        pow3=next_pow3,
                        previous_rho=rho,
                        lift_count=next_lift_count,
                        current_plateau=next_plateau,
                        longest_plateau=next_longest_plateau,
                    )
                )

        total_paths_considered += total_budget_paths
        if total_budget_paths > len(new_states):
            truncated_depths.append(next_depth)

        valid_path_count = 0
        residues = set()
        residue_count = 1 if C == 0 and new_states else 0
        ancestors = []
        for state in new_states:
            if len(path_rows) < max_path_rows and next_depth == depth:
                path_rows.append(_lock3_path_row_from_state(C, state, terminal_value))
            if C != 0:
                residues.add(
                    _lock3_terminal_residue_class_from_affine(
                        state.A,
                        state.B,
                        state.pow3,
                    )
                )
            if not skip_terminal_checks:
                valid, ancestor = _lock3_terminal_check_from_affine(
                    state.A,
                    state.B,
                    state.pow3,
                    terminal_value,
                )
                if valid:
                    valid_path_count += 1
                    if ancestor is not None:
                        ancestors.append(ancestor)
        if C != 0:
            residue_count = len(residues)

        note = "ok"
        if next_depth in truncated_depths:
            note = f"truncated_at_max_paths_{max_paths}"
        row = Lock3SurvivorDepthRow(
                C=C,
                depth=next_depth,
                total_budget_paths=total_budget_paths,
                valid_backward_paths_from_1=valid_path_count,
                valid_backward_residue_classes=residue_count,
            min_positive_ancestor=min(ancestors) if ancestors else None,
            max_positive_ancestor=max(ancestors) if ancestors else None,
            branch_count=len(new_states),
            notes=note,
        )
        survivor_rows.append(row)
        if progress_callback is not None:
            progress_callback(
                {
                    "C": C,
                    "depth": next_depth,
                    "target_depth": depth,
                    "total_budget_paths": total_budget_paths,
                    "total_paths_considered": total_paths_considered,
                    "branch_count": row.branch_count,
                    "valid_backward_paths_from_1": row.valid_backward_paths_from_1,
                    "valid_backward_residue_classes": row.valid_backward_residue_classes,
                    "largest_rho_bit_length": largest_rho_bit_length,
                    "notes": note,
                }
            )
        if next_depth in KNOWN_CF_CONVERGENTS:
            near_returns.append(next_depth)
        states = new_states
        if not states:
            break

    max_lift_count = max((state.lift_count for state in states), default=0)
    longest_plateau = max((state.longest_plateau for state in states), default=0)
    summary = {
        "C": C,
        "max_depth": depth,
        "terminal_value": terminal_value,
        "max_paths": max_paths,
        "total_paths_considered": total_paths_considered,
        "survivor_counts": {
            str(row.depth): row.valid_backward_paths_from_1
            for row in survivor_rows
        },
        "branch_counts": {
            str(row.depth): row.branch_count
            for row in survivor_rows
        },
        "any_path_appears_extendable": bool(states),
        "rho_representatives_stabilize": bool(states) and max_lift_count == 0 and depth > 0,
        "longest_stable_plateau": longest_plateau,
        "number_of_lift_events": max_lift_count,
        "largest_rho_bit_length": largest_rho_bit_length,
        "near_return_times_encountered": near_returns,
        "truncated_depths": truncated_depths,
    }
    return summary, survivor_rows, path_rows, lift_rows


def lock2_word_row(word: tuple[int, ...], B: int | None = None) -> Lock2WordRow:
    k = len(word)
    A = sum(word)
    B = word_affine_B(word) if B is None else B
    den = (1 << A) - 3**k
    if den <= 0:
        raise ValueError("word is not contractive")
    rho = lock2_rho_for_word(word, B=B)
    margin = den * rho - B
    theta = B / den
    gap = rho - theta
    floor_theta = B // den
    theta_candidate_odd_count = (floor_theta + 1) // 2
    rho_rank = (rho + 1) // 2
    period, repetitions = _primitive_period(word)
    return Lock2WordRow(
        word=",".join(str(a) for a in word),
        k=k,
        A=A,
        B=B,
        rho=rho,
        theta_num=B,
        theta_den=den,
        theta_float=theta,
        margin=margin,
        threshold_gap_float=gap,
        relative_gap=gap / rho,
        normalized_margin=margin / den,
        log2_margin_plus_1_over_k=math.log2(margin + 1) / k if margin >= 0 else math.nan,
        theta_candidate_odd_count=theta_candidate_odd_count,
        rho_rank=rho_rank,
        theta_over_rho=theta / rho,
        candidate_to_rho_rank_ratio=(
            theta_candidate_odd_count / rho_rank if rho_rank else 0.0
        ),
        rho_bit_slack=(A + 1) - rho.bit_length(),
        is_all_twos=all(a == 2 for a in word),
        first_contractivity_index=first_contractivity_index_for_word(word),
        delta_from_all_twos=sum(abs(a - 2) for a in word),
        count_ones=sum(1 for a in word if a == 1),
        count_twos=sum(1 for a in word if a == 2),
        count_ge3=sum(1 for a in word if a >= 3),
        max_run_1=_max_run_by_predicate(word, lambda a: a == 1),
        max_run_2=_max_run_by_predicate(word, lambda a: a == 2),
        max_run_ge3=_max_run_by_predicate(word, lambda a: a >= 3),
        primitive_period=period,
        primitive_repetitions=repetitions,
    )


def analyze_lock2_scan(
    Amax: int,
    top_n: int = 200,
    include_all_rows: bool = False,
    first_contractivity_only: bool = False,
    predict_rho_slack_min: int | None = None,
    predict_theta_candidate_min: int | None = None,
    predict_theta_over_rho_min: float | None = None,
    prediction_top_n: int = 200,
) -> tuple[
    dict,
    list[Lock2WordRow],
    list[Lock2WordRow],
    list[Lock2WordRow],
    list[Lock2WordRow],
]:
    if Amax < 1:
        raise ValueError("Amax must be positive")

    total_words = 0
    contractive_words = 0
    all_twos_zero_margins = 0
    nontrivial_zero_margins = 0
    negative_margins = 0
    first_contractivity_words = 0
    by_A: dict[int, dict[str, int]] = {}
    all_rows: list[Lock2WordRow] = []
    small_rho_rows: list[Lock2WordRow] = []
    near_heap: list[tuple[tuple[float, int, int, int, int], Lock2WordRow]] = []
    prediction_heap: list[tuple[tuple[float, int, int, int, int], Lock2WordRow]] = []
    near_counter = 0
    prediction_counter = 0
    prediction_match_count = 0
    min_nontrivial_margin: Lock2WordRow | None = None
    min_nontrivial_relative_gap: Lock2WordRow | None = None
    theta_candidate_buckets: dict[str, int] = {}
    max_theta_candidate_count = 0
    max_theta_candidate_count_row: Lock2WordRow | None = None
    rho_small_counts: dict[str, int] = {
        "rho_le_3": 0,
        "rho_le_5": 0,
        "rho_le_7": 0,
        "rho_le_15": 0,
        "rho_le_31": 0,
        "rho_le_63": 0,
        "rho_le_127": 0,
        "rho_le_255": 0,
        "rho_le_511": 0,
        "rho_le_1023": 0,
    }
    rho_bit_slack_buckets: dict[str, int] = {}

    for A in range(1, Amax + 1):
        by_A[A] = {
            "contractive": 0,
            "first_contractivity": 0,
            "min_rho": 0,
            "min_rho_word": "",
            "max_theta_candidate_count": 0,
            "max_theta_candidate_word": "",
            "max_theta_over_rho": 0.0,
            "max_theta_over_rho_word": "",
            "max_candidate_to_rho_rank_ratio": 0.0,
            "max_candidate_to_rho_rank_word": "",
        }

    if first_contractivity_only:
        row_iter = (
            (word, B)
            for word, B in _first_contractivity_words_up_to(Amax)
        )
    else:
        def broad_rows() -> Iterable[tuple[tuple[int, ...], int | None]]:
            for A in range(1, Amax + 1):
                words_by_k = []
                max_k = 0
                for k in range(1, A + 1):
                    if (1 << A) > 3**k:
                        max_k = k
                    else:
                        break
                for k in range(1, max_k + 1):
                    words_by_k.append(_compositions_fixed_length(A, k))
                for words in words_by_k:
                    for word in words:
                        yield word, None

        row_iter = broad_rows()

    for word, precomputed_B in row_iter:
        A = sum(word)
        if A > Amax:
            continue

        total_words += 1
        row = lock2_word_row(word, B=precomputed_B)
        is_first_contractivity = row.first_contractivity_index == row.k
        if first_contractivity_only and not is_first_contractivity:
            continue
        contractive_words += 1
        by_A[A]["contractive"] += 1
        if is_first_contractivity:
            first_contractivity_words += 1
            by_A[A]["first_contractivity"] += 1

        if row.margin < 0:
            negative_margins += 1
        elif row.margin == 0:
            if row.is_all_twos:
                all_twos_zero_margins += 1
            else:
                nontrivial_zero_margins += 1

        if include_all_rows:
            all_rows.append(row)

        bucket = _theta_candidate_bucket(row.theta_candidate_odd_count)
        theta_candidate_buckets[bucket] = theta_candidate_buckets.get(bucket, 0) + 1
        if row.theta_candidate_odd_count > max_theta_candidate_count:
            max_theta_candidate_count = row.theta_candidate_odd_count
            max_theta_candidate_count_row = row
        rho_slack_bucket = _rho_bit_slack_bucket(row.rho_bit_slack)
        rho_bit_slack_buckets[rho_slack_bucket] = (
            rho_bit_slack_buckets.get(rho_slack_bucket, 0) + 1
        )
        by_A_row = by_A[A]
        if by_A_row["min_rho"] == 0 or row.rho < by_A_row["min_rho"]:
            by_A_row["min_rho"] = row.rho
            by_A_row["min_rho_word"] = row.word
        if row.theta_candidate_odd_count > by_A_row["max_theta_candidate_count"]:
            by_A_row["max_theta_candidate_count"] = row.theta_candidate_odd_count
            by_A_row["max_theta_candidate_word"] = row.word
        if row.theta_over_rho > by_A_row["max_theta_over_rho"]:
            by_A_row["max_theta_over_rho"] = row.theta_over_rho
            by_A_row["max_theta_over_rho_word"] = row.word
        if row.candidate_to_rho_rank_ratio > by_A_row["max_candidate_to_rho_rank_ratio"]:
            by_A_row["max_candidate_to_rho_rank_ratio"] = row.candidate_to_rho_rank_ratio
            by_A_row["max_candidate_to_rho_rank_word"] = row.word
        for key in rho_small_counts:
            limit = int(key.rsplit("_", 1)[1])
            if row.rho <= limit:
                rho_small_counts[key] += 1
        if row.rho <= 1023:
            small_rho_rows.append(row)

        if not row.is_all_twos:
            if (
                min_nontrivial_margin is None
                or row.margin < min_nontrivial_margin.margin
            ):
                min_nontrivial_margin = row
            if (
                min_nontrivial_relative_gap is None
                or row.relative_gap < min_nontrivial_relative_gap.relative_gap
            ):
                min_nontrivial_relative_gap = row
            if top_n > 0:
                near_counter += 1
                heap_key = (
                    -row.relative_gap,
                    -row.margin,
                    -row.A,
                    -row.k,
                    -near_counter,
                )
                if len(near_heap) < top_n:
                    heapq.heappush(near_heap, (heap_key, row))
                elif heap_key > near_heap[0][0]:
                    heapq.heapreplace(near_heap, (heap_key, row))

        prediction_match = True
        if (
            predict_rho_slack_min is not None
            and row.rho_bit_slack < predict_rho_slack_min
        ):
            prediction_match = False
        if (
            predict_theta_candidate_min is not None
            and row.theta_candidate_odd_count < predict_theta_candidate_min
        ):
            prediction_match = False
        if (
            predict_theta_over_rho_min is not None
            and row.theta_over_rho < predict_theta_over_rho_min
        ):
            prediction_match = False
        if prediction_match and any(
            value is not None
            for value in (
                predict_rho_slack_min,
                predict_theta_candidate_min,
                predict_theta_over_rho_min,
            )
        ):
            prediction_match_count += 1
            if prediction_top_n > 0:
                prediction_counter += 1
                prediction_key = (
                    row.theta_over_rho,
                    row.candidate_to_rho_rank_ratio,
                    row.rho_bit_slack,
                    row.theta_candidate_odd_count,
                    prediction_counter,
                )
                if len(prediction_heap) < prediction_top_n:
                    heapq.heappush(prediction_heap, (prediction_key, row))
                elif prediction_key > prediction_heap[0][0]:
                    heapq.heapreplace(prediction_heap, (prediction_key, row))

    near_rows = [row for _, row in near_heap]
    near_rows.sort(key=lambda r: (r.relative_gap, r.margin, r.A, r.k))
    prediction_rows = [row for _, row in prediction_heap]
    prediction_rows.sort(
        key=lambda r: (
            -r.theta_over_rho,
            -r.candidate_to_rho_rank_ratio,
            -r.rho_bit_slack,
            -r.theta_candidate_odd_count,
        )
    )

    summary = {
        "Amax": Amax,
        "first_contractivity_only": first_contractivity_only,
        "total_generated_contractivity_candidates": total_words,
        "contractive_words": contractive_words,
        "first_contractivity_words": first_contractivity_words,
        "all_twos_zero_margins": all_twos_zero_margins,
        "nontrivial_zero_margins": nontrivial_zero_margins,
        "negative_margins": negative_margins,
        "lock2_holds_in_scan": negative_margins == 0 and nontrivial_zero_margins == 0,
        "min_nontrivial_margin": asdict(min_nontrivial_margin)
        if min_nontrivial_margin is not None
        else None,
        "min_nontrivial_relative_gap": asdict(min_nontrivial_relative_gap)
        if min_nontrivial_relative_gap is not None
        else None,
        "theta_candidate_buckets": dict(sorted(theta_candidate_buckets.items())),
        "max_theta_candidate_odd_count": max_theta_candidate_count,
        "max_theta_candidate_odd_count_row": asdict(max_theta_candidate_count_row)
        if max_theta_candidate_count_row is not None
        else None,
        "rho_small_counts": rho_small_counts,
        "rho_bit_slack_buckets": dict(sorted(rho_bit_slack_buckets.items())),
        "prediction_knobs": {
            "rho_slack_min": predict_rho_slack_min,
            "theta_candidate_min": predict_theta_candidate_min,
            "theta_over_rho_min": predict_theta_over_rho_min,
            "prediction_top_n": prediction_top_n,
        },
        "prediction_match_count": prediction_match_count,
        "by_A": by_A,
    }
    small_rho_rows.sort(key=lambda r: (r.rho, r.A, r.k, r.word))
    return summary, near_rows, all_rows, prediction_rows, small_rho_rows


def write_lock2_scan_outputs(
    summary: dict,
    near_rows: list[Lock2WordRow],
    all_rows: list[Lock2WordRow],
    prediction_rows: list[Lock2WordRow],
    small_rho_rows: list[Lock2WordRow],
    out_dir: Path,
    Amax: int,
    label: str = "lock2",
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    summary_path = out_dir / f"{label}_summary_Amax{Amax}_{stamp}.json"
    near_path = out_dir / f"{label}_near_failures_Amax{Amax}_{stamp}.csv"
    theta_path = out_dir / f"{label}_theta_buckets_Amax{Amax}_{stamp}.csv"
    small_rho_path = out_dir / f"{label}_small_rho_Amax{Amax}_{stamp}.csv"
    by_A_path = out_dir / f"{label}_by_A_threats_Amax{Amax}_{stamp}.csv"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    _write_csv(near_path, (asdict(row) for row in near_rows))
    _write_csv(
        theta_path,
        (
            {"candidate_odd_count_bucket": bucket, "words": count}
            for bucket, count in summary["theta_candidate_buckets"].items()
        ),
    )
    def small_rho_dicts() -> Iterable[dict]:
        for row in small_rho_rows:
            materialized = asdict(row)
            word = tuple(int(part) for part in row.word.split(",")) if row.word else ()
            orbit_word = exponent_prefix_from_start(row.rho, row.k)
            image_num = (3**row.k) * row.rho + row.B
            image_den = 1 << row.A
            materialized["rho_orbit_prefix"] = ",".join(str(a) for a in orbit_word)
            materialized["rho_follows_word"] = orbit_word == word
            materialized["congruence_valid"] = (
                ((3**row.k) * row.rho + row.B - (1 << row.A))
                % (1 << (row.A + 1))
            ) == 0
            materialized["image_at_rho"] = image_num // image_den
            materialized["image_at_rho_is_odd"] = (
                image_num % image_den == 0 and ((image_num // image_den) % 2 == 1)
            )
            materialized["image_at_rho_below_rho"] = (
                image_num % image_den == 0 and (image_num // image_den) < row.rho
            )
            return_row = materialized
            yield return_row

    _write_csv(small_rho_path, small_rho_dicts())
    _write_csv(
        by_A_path,
        (
            {"A": int(A), **row}
            for A, row in sorted(summary["by_A"].items(), key=lambda item: int(item[0]))
        ),
    )
    paths = {
        "summary": summary_path,
        "near_failures": near_path,
        "theta_buckets": theta_path,
        "small_rho": small_rho_path,
        "by_A_threats": by_A_path,
    }
    if all_rows:
        words_path = out_dir / f"{label}_words_Amax{Amax}_{stamp}.csv"
        _write_csv(words_path, (asdict(row) for row in all_rows))
        paths["words"] = words_path
    if prediction_rows:
        prediction_path = out_dir / f"{label}_predictions_Amax{Amax}_{stamp}.csv"
        _write_csv(prediction_path, (asdict(row) for row in prediction_rows))
        paths["predictions"] = prediction_path
    return paths


def write_lock3_backward_outputs(
    summary: dict,
    survivor_rows: list[Lock3SurvivorDepthRow],
    path_rows: list[Lock3BackwardPathRow],
    lift_rows: list[Lock3ResidueLiftRow],
    out_dir: Path,
    C: int,
    depth: int,
    label: str = "lock3",
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / f"{label}_summary_C{C}.json"
    survivors_path = out_dir / f"survivors_by_depth_C{C}.csv"
    paths_path = out_dir / f"valid_backward_paths_C{C}_N{depth}.csv"
    lifts_path = out_dir / f"{label}_residue_lifts_C{C}.csv"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    _write_csv(survivors_path, (asdict(row) for row in survivor_rows))
    _write_csv(paths_path, (asdict(row) for row in path_rows))
    _write_csv(lifts_path, (asdict(row) for row in lift_rows))
    return {
        "summary": summary_path,
        "survivors": survivors_path,
        "paths": paths_path,
        "residue_lifts": lifts_path,
    }


def write_lock3_census_outputs(
    summary: dict,
    census_rows: list[Lock3CensusRow],
    event_rows: list[Lock3CensusEventRow],
    witness_records: list[dict],
    out_dir: Path,
    C: int,
    label: str = "lock3",
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = out_dir / f"{label}_summary_C{C}.json"
    census_path = out_dir / f"{label}_census_C{C}.csv"
    events_path = out_dir / f"{label}_events_C{C}.csv"
    witnesses_path = out_dir / f"{label}_witnesses_C{C}.jsonl"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    _write_csv(census_path, (asdict(row) for row in census_rows))
    _write_csv(events_path, (asdict(row) for row in event_rows))
    with witnesses_path.open("w") as fh:
        for record in witness_records:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
    return {
        "summary": summary_path,
        "census": census_path,
        "events": events_path,
        "witnesses": witnesses_path,
    }


def write_phase_output(profile: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"phase_{profile['start']}_mod{profile['period']}_{stamp}.json"
    path.write_text(json.dumps(profile, indent=2, sort_keys=True) + "\n")
    return path


def write_macro_outputs(
    rows: list[MacroCorridor],
    out_dir: Path,
    label: str = "macro_corridors",
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"{label}_{stamp}.csv"
    _write_csv(path, (asdict(row) for row in rows))
    return path


def write_gap_outputs(
    exit_rows: list[GapExitRow],
    ladder_rows: list[LadderGapRow],
    out_dir: Path,
    label: str = "gap_kill",
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    exit_path = out_dir / f"{label}_k53_exits_{stamp}.csv"
    ladder_path = out_dir / f"{label}_ladder_{stamp}.csv"
    _write_csv(exit_path, (asdict(row) for row in exit_rows))
    _write_csv(ladder_path, (asdict(row) for row in ladder_rows))
    return {"k53_exits": exit_path, "ladder": ladder_path}


def write_post_k53_outputs(
    stats_rows: list[PostK53StatsRow],
    step_rows: list[PostK53StepRow],
    out_dir: Path,
    label: str = "post_k53",
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stats_path = out_dir / f"{label}_stats_{stamp}.csv"
    steps_path = out_dir / f"{label}_steps_{stamp}.csv"
    _write_csv(stats_path, (asdict(row) for row in stats_rows))
    _write_csv(steps_path, (asdict(row) for row in step_rows))
    return {"stats": stats_path, "steps": steps_path}


def write_k53_capacity_outputs(
    observed_rows: list[K53CapacityObservedRow],
    requirement_rows: list[K53CapacityRequirementRow],
    out_dir: Path,
    label: str = "k53_capacity",
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    observed_path = out_dir / f"{label}_observed_{stamp}.csv"
    requirements_path = out_dir / f"{label}_requirements_{stamp}.csv"
    _write_csv(observed_path, (asdict(row) for row in observed_rows))
    _write_csv(requirements_path, (asdict(row) for row in requirement_rows))
    return {"observed": observed_path, "requirements": requirements_path}


def write_corridor_bound_outputs(
    observed_rows: list[CorridorBoundObservedRow],
    synthetic_rows: list[CorridorBoundSyntheticRow],
    ceiling_rows: list[CorridorBoundCeilingRow],
    out_dir: Path,
    label: str = "corridor_bound",
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    observed_path = out_dir / f"{label}_observed_{stamp}.csv"
    synthetic_path = out_dir / f"{label}_synthetic_{stamp}.csv"
    ceiling_path = out_dir / f"{label}_ceiling_{stamp}.csv"
    _write_csv(observed_path, (asdict(row) for row in observed_rows))
    _write_csv(synthetic_path, (asdict(row) for row in synthetic_rows))
    _write_csv(ceiling_path, (asdict(row) for row in ceiling_rows))
    return {
        "observed": observed_path,
        "synthetic": synthetic_path,
        "ceiling": ceiling_path,
    }


def write_scaling_sweep_outputs(
    summary_rows: list[ScalingSweepSummaryRow],
    fit_rows: list[ScalingSweepFitRow],
    kill_rows: list[ScalingSweepKillRow],
    out_dir: Path,
    label: str = "scaling_sweep",
) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    summary_path = out_dir / f"{label}_summary_{stamp}.csv"
    fits_path = out_dir / f"{label}_fits_{stamp}.csv"
    kill_path = out_dir / f"{label}_kill_{stamp}.csv"
    _write_csv(summary_path, (asdict(row) for row in summary_rows))
    _write_csv(fits_path, (asdict(row) for row in fit_rows))
    _write_csv(kill_path, (asdict(row) for row in kill_rows))
    return {"summary": summary_path, "fits": fits_path, "kill": kill_path}


def write_macro_convergent_summary(
    rows: list[MacroConvergentSummaryRow],
    out_dir: Path,
    label: str = "macro_convergent_summary",
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"{label}_{stamp}.csv"
    _write_csv(path, (asdict(row) for row in rows))
    return path


def _write_csv(path: Path, rows: Iterable[dict]) -> None:
    materialized = list(rows)
    if not materialized:
        path.write_text("")
        return
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(materialized[0].keys()))
        writer.writeheader()
        writer.writerows(materialized)
