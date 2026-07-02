from __future__ import annotations

import argparse
import math
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from .exact import (
    analyze_orbit,
    analyze_k53_gap_exits,
    analyze_ladder_gaps,
    analyze_lock3_backward,
    analyze_lock3_census,
    analyze_k53_capacity,
    analyze_corridor_bound,
    analyze_lock2_scan,
    analyze_macro_corridors,
    analyze_macro_convergent_summary,
    analyze_post_k53_behavior,
    analyze_scaling_sweep,
    analyze_tail_law,
    phase_profile,
    scan_starters_parallel,
    scan_starters_range_parallel,
    scan_starters,
    write_gap_outputs,
    write_k53_capacity_outputs,
    write_corridor_bound_outputs,
    write_lock2_scan_outputs,
    write_lock3_backward_outputs,
    write_lock3_census_outputs,
    write_orbit_outputs,
    write_macro_outputs,
    write_macro_convergent_summary,
    write_post_k53_outputs,
    write_scaling_sweep_outputs,
    write_tail_law_outputs,
    write_phase_output,
    write_scan_outputs,
    write_scan_range_outputs,
)


DEFAULT_OUT = Path("data/runs")


def _parse_tail_range(value: str) -> tuple[int, int, Path]:
    parts = value.split(":", 2)
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("range must be START:STOP:CSV")
    try:
        start = int(parts[0])
        stop = int(parts[1])
    except ValueError as exc:
        raise argparse.ArgumentTypeError("START and STOP must be integers") from exc
    path = Path(parts[2])
    return start, stop, path


def main() -> None:
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    parser = argparse.ArgumentParser(prog="collatz-exp")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    subparsers = parser.add_subparsers(dest="command", required=True)

    orbit = subparsers.add_parser("orbit", help="analyze one odd starting value")
    orbit.add_argument("n", type=int)
    orbit.add_argument("--max-steps", type=int, default=100000)
    orbit.add_argument("--min-segment-len", type=int, default=2)

    scan = subparsers.add_parser("scan", help="scan odd starts up to a limit")
    scan.add_argument("--limit", type=int, required=True)
    scan.add_argument("--min-reserve", type=int, default=12)
    scan.add_argument("--max-steps", type=int, default=10000)

    scan_fast = subparsers.add_parser("scan-fast", help="parallel reserve scan")
    scan_fast.add_argument("--limit", type=int, required=True)
    scan_fast.add_argument("--min-reserve", type=int, default=12)
    scan_fast.add_argument("--max-steps", type=int, default=10000)
    scan_fast.add_argument("--workers", type=int, default=None)
    scan_fast.add_argument("--chunk-odds", type=int, default=100000)

    scan_range = subparsers.add_parser("scan-range-fast", help="parallel reserve scan over an inclusive odd range")
    scan_range.add_argument("--start", type=int, required=True)
    scan_range.add_argument("--stop", type=int, required=True)
    scan_range.add_argument("--min-reserve", type=int, default=23)
    scan_range.add_argument("--max-steps", type=int, default=10000)
    scan_range.add_argument("--workers", type=int, default=None)
    scan_range.add_argument("--chunk-odds", type=int, default=100000)

    phase = subparsers.add_parser("phase", help="growth-step residue profile")
    phase.add_argument("n", type=int)
    phase.add_argument("--period", type=int, default=53)
    phase.add_argument("--max-steps", type=int, default=100000)

    macro = subparsers.add_parser("macro", help="analyze macro-corridors")
    macro.add_argument("starts", type=int, nargs="+")
    macro.add_argument("--max-steps", type=int, default=100000)
    macro.add_argument("--drop-tolerance", type=int, default=2)
    macro.add_argument("--min-length", type=int, default=1)

    macro_summary = subparsers.add_parser(
        "macro-summary",
        help="summarize macro-corridor convergent mappings for many starts",
    )
    macro_summary.add_argument("starts", type=int, nargs="+")
    macro_summary.add_argument("--max-steps", type=int, default=100000)

    gap = subparsers.add_parser("gap-kill", help="quantify convergent gap bridge costs")
    gap.add_argument("starts", type=int, nargs="+")
    gap.add_argument("--max-steps", type=int, default=100000)
    gap.add_argument("--spend-per-step", type=int, default=2)
    gap.add_argument("--phase-scan", type=int, default=200000)

    post = subparsers.add_parser(
        "post-k53",
        help="measure actual exponent behavior after the k=53 macro-corridor",
    )
    post.add_argument("starts", type=int, nargs="+")
    post.add_argument("--max-steps", type=int, default=100000)
    post.add_argument("--bridge-gap", type=int, default=306)

    capacity = subparsers.add_parser(
        "k53-capacity",
        help="estimate reserve capacity and martingale scale for k=53 corridors",
    )
    capacity.add_argument("starts", type=int, nargs="+")
    capacity.add_argument("--required-reserve", type=int, action="append", default=None)
    capacity.add_argument("--max-steps", type=int, default=100000)
    capacity.add_argument("--credit-scan-limit", type=int, default=10000)

    bound = subparsers.add_parser(
        "corridor-bound",
        help="test k=53 corridor length scaling against bit length",
    )
    bound.add_argument("starts", type=int, nargs="+")
    bound.add_argument("--bit-length", type=int, action="append", default=None)
    bound.add_argument("--samples-per-bit-length", type=int, default=100)
    bound.add_argument("--max-steps", type=int, default=2000)
    bound.add_argument("--beta-threshold", type=float, default=0.01)
    bound.add_argument("--random-seed", type=int, default=8675309)

    sweep = subparsers.add_parser(
        "scaling-sweep",
        help="large random sweep for positive macro-corridor quality scaling",
    )
    sweep.add_argument("--bit-length", type=int, action="append", default=None)
    sweep.add_argument("--beta-threshold", type=float, action="append", default=None)
    sweep.add_argument("--samples-per-bit-length", type=int, default=10000)
    sweep.add_argument("--max-steps", type=int, default=50000)
    sweep.add_argument("--workers", type=int, default=None)
    sweep.add_argument("--chunk-size", type=int, default=100)
    sweep.add_argument("--random-seed", type=int, default=424242)

    tail = subparsers.add_parser(
        "tail-law",
        help="fit empirical max-reserve tail law from completed scan CSVs",
    )
    tail.add_argument(
        "--range",
        dest="ranges",
        type=_parse_tail_range,
        action="append",
        required=True,
        help="inclusive scanned range as START:STOP:CSV",
    )
    tail.add_argument("--min-threshold", type=int, default=23)
    tail.add_argument("--fit-min-threshold", type=int, action="append", default=None)
    tail.add_argument("--target-reserve", type=int, action="append", default=None)

    lock2 = subparsers.add_parser(
        "lock2-scan",
        help="exhaustively scan finite contractive words for Lock 2 margins",
    )
    lock2.add_argument("--Amax", type=int, required=True)
    lock2.add_argument("--top-n", type=int, default=200)
    lock2.add_argument(
        "--write-all",
        action="store_true",
        help="also write every contractive word row; can be very large",
    )
    lock2.add_argument(
        "--first-contractivity-only",
        action="store_true",
        help="scan only words whose final step is the first contractive prefix",
    )
    lock2.add_argument("--predict-rho-slack-min", type=int, default=None)
    lock2.add_argument("--predict-theta-candidates-min", type=int, default=None)
    lock2.add_argument("--predict-theta-over-rho-min", type=float, default=None)
    lock2.add_argument("--prediction-top-n", type=int, default=200)

    lock3 = subparsers.add_parser(
        "lock3-backward",
        help="bounded-deficit backward solver for Lock 3",
    )
    lock3.add_argument("--C", type=int, required=True)
    lock3.add_argument("--depth", type=int, required=True)
    lock3.add_argument("--mode", choices=("exact", "census"), default="exact")
    lock3.add_argument(
        "--engine",
        choices=("auto", "python", "rust"),
        default="auto",
        help="census engine; auto uses the Rust engine when available",
    )
    lock3.add_argument("--terminal-value", type=int, default=1)
    lock3.add_argument(
        "--residue-mod-power",
        type=int,
        default=8,
        help="census residue signature modulus is 3^M",
    )
    lock3.add_argument("--max-paths", type=int, default=200000)
    lock3.add_argument("--max-path-rows", type=int, default=20000)
    lock3.add_argument("--max-lift-rows", type=int, default=200000)
    lock3.add_argument(
        "--skip-terminal-checks",
        action="store_true",
        help="skip exact backward-from-terminal divisibility checks during Lock 3 scan",
    )
    lock3.add_argument(
        "--progress-every",
        type=int,
        default=0,
        help="write Lock 3 progress to stderr every N depths",
    )
    lock3.add_argument(
        "--checkpoint-path",
        type=Path,
        default=None,
        help="Rust census checkpoint file",
    )
    lock3.add_argument(
        "--checkpoint-every",
        type=int,
        default=0,
        help="write Rust census checkpoint every N depths",
    )
    lock3.add_argument(
        "--resume",
        type=Path,
        default=None,
        help="resume Rust census from a checkpoint file",
    )

    args = parser.parse_args()

    if args.command == "orbit":
        result = analyze_orbit(
            args.n,
            max_steps=args.max_steps,
            min_segment_len=args.min_segment_len,
        )
        paths = write_orbit_outputs(result, args.out_dir)
        print(
            f"n={result['start']} steps={result['total_steps']} "
            f"maxD={result['max_reserve']} segments={result['num_segments']} "
            f"growth_steps={result['num_growth_steps']}"
        )
        for segment in result["segments"][:12]:
            print(
                f"segment {segment.index:02d}: k={segment.start_k}-{segment.end_k} "
                f"L={segment.length} A={segment.A} d={segment.d_before}->{segment.d_after} "
                f"ghost={segment.ghost_num}/{segment.ghost_den} "
                f"v2_resid={segment.fixed_residual_v2}"
            )
        print(f"wrote {paths['summary']}")
        print(f"wrote {paths['segments']}")
        print(f"wrote {paths['seams']}")

    elif args.command == "scan":
        rows = scan_starters(
            args.limit,
            min_reserve=args.min_reserve,
            max_steps=args.max_steps,
        )
        path = write_scan_outputs(rows, args.out_dir, args.limit, args.min_reserve)
        print(
            f"limit={args.limit} minD={args.min_reserve} hits={len(rows)} "
            f"wrote {path}"
        )
        for row in rows[:20]:
            print(
                f"n={row['start']} maxD={row['max_reserve']} "
                f"timeMax={row['time_max']} crossing={row['crossing_time']} "
                f"segments={row['num_segments']}"
            )

    elif args.command == "scan-fast":
        rows = scan_starters_parallel(
            args.limit,
            min_reserve=args.min_reserve,
            max_steps=args.max_steps,
            workers=args.workers,
            chunk_odds=args.chunk_odds,
        )
        path = write_scan_outputs(rows, args.out_dir, args.limit, args.min_reserve)
        print(
            f"limit={args.limit} minD={args.min_reserve} hits={len(rows)} "
            f"workers={args.workers or 'auto'} wrote {path}"
        )
        for row in rows[:30]:
            print(
                f"n={row['start']} maxD={row['max_reserve']} "
                f"timeMax={row['time_max']} crossing={row['crossing_time']} "
                f"growth_steps={row['growth_steps']}"
            )

    elif args.command == "scan-range-fast":
        rows = scan_starters_range_parallel(
            args.start,
            args.stop,
            min_reserve=args.min_reserve,
            max_steps=args.max_steps,
            workers=args.workers,
            chunk_odds=args.chunk_odds,
        )
        path = write_scan_range_outputs(
            rows,
            args.out_dir,
            args.start,
            args.stop,
            args.min_reserve,
        )
        print(
            f"start={args.start} stop={args.stop} minD={args.min_reserve} "
            f"hits={len(rows)} workers={args.workers or 'auto'} wrote {path}"
        )
        for row in rows[:50]:
            print(
                f"n={row['start']} maxD={row['max_reserve']} "
                f"timeMax={row['time_max']} crossing={row['crossing_time']} "
                f"growth_steps={row['growth_steps']}"
            )

    elif args.command == "phase":
        profile = phase_profile(args.n, args.period, max_steps=args.max_steps)
        path = write_phase_output(profile, args.out_dir)
        print(
            f"n={profile['start']} period={profile['period']} "
            f"growth_steps={profile['growth_steps']} wrote {path}"
        )
        print(profile["residues"])

    elif args.command == "macro":
        rows = []
        for start in args.starts:
            orbit_rows = analyze_macro_corridors(
                start,
                max_steps=args.max_steps,
                drop_tolerance=args.drop_tolerance,
                min_length=args.min_length,
            )
            rows.extend(orbit_rows)
            print(f"\nn={start} macro_corridors={len(orbit_rows)}")
            print(
                "idx | steps | L | A | beta | conv | ghost | qual | "
                "d_entry d_exit d_peak"
            )
            for row in orbit_rows:
                ghost = (
                    f"{row.ghost_num}/{row.ghost_den}"
                    if row.ghost_num is not None
                    else "contractive"
                )
                quality = (
                    f"{row.quality_1_over_beta:.3f}"
                    if row.quality_1_over_beta is not None
                    else ""
                )
                print(
                    f"{row.corridor_index:3d} | "
                    f"{row.start_step:4d}-{row.end_step:<4d} | "
                    f"{row.length:3d} | {row.A:3d} | "
                    f"{row.beta: .6f} | {row.mapped_convergent:6d} | "
                    f"{ghost:>16} | {quality:>8} | "
                    f"{row.d_entry:7d} {row.d_exit:6d} {row.d_peak:6d}"
                )
        path = write_macro_outputs(rows, args.out_dir)
        print(f"\nwrote {path}")

    elif args.command == "macro-summary":
        rows = analyze_macro_convergent_summary(args.starts, max_steps=args.max_steps)
        path = write_macro_convergent_summary(rows, args.out_dir)
        total = len(rows)
        k53 = sum(1 for row in rows if row.has_k53_or_higher)
        k359 = sum(1 for row in rows if row.has_k359_or_higher)
        print(f"starts={total} has_k53_or_higher={k53} has_k359_or_higher={k359}")
        print("start | maxD | max_mapped | best_L | best_beta | best_map | best_peak")
        for row in rows[:80]:
            print(
                f"{row.start:10d} | {row.max_reserve:4d} | "
                f"{str(row.max_mapped_convergent):>10s} | "
                f"{str(row.best_corridor_length):>6s} | "
                f"{row.best_corridor_beta if row.best_corridor_beta is not None else '':>9} | "
                f"{str(row.best_corridor_mapped_convergent):>8s} | "
                f"{str(row.best_corridor_peak_reserve):>9s}"
            )
        print(f"\nwrote {path}")

    elif args.command == "gap-kill":
        macro_rows = []
        for start in args.starts:
            macro_rows.extend(analyze_macro_corridors(start, max_steps=args.max_steps))
        exit_rows = analyze_k53_gap_exits(
            args.starts,
            max_steps=args.max_steps,
            spend_per_step=args.spend_per_step,
        )
        ladder_rows = analyze_ladder_gaps(
            macro_rows,
            spend_per_step=args.spend_per_step,
            phase_scan=args.phase_scan,
        )
        paths = write_gap_outputs(exit_rows, ladder_rows, args.out_dir)

        print(f"assumption: non-corridor spend_per_step={args.spend_per_step}")
        print("\nK=53 exits")
        print(
            "orbit | exit | reserve | peak | remaining | gap | required | "
            "ratio | bridgeable"
        )
        for row in exit_rows:
            print(
                f"{row.orbit:9d} | {row.k53_exit_step:4d} | "
                f"{row.reserve_at_exit:7d} | {row.peak_reserve_in_corridor:4d} | "
                f"{row.steps_remaining_before_bankruptcy:9d} | {row.gap_to_359:3d} | "
                f"{row.min_reserve_to_bridge_gap:8d} | "
                f"{row.gap_to_exit_reserve_ratio:5.2f} | "
                f"{row.bridgeable_by_exit_reserve}"
            )

        print("\nConvergent ladder")
        print("n | k | gap | observed_max_reserve | required | bridgeable")
        for row in ladder_rows:
            observed = (
                str(row.max_reserve_from_riding_n)
                if row.max_reserve_from_riding_n is not None
                else ""
            )
            bridgeable = "" if row.bridgeable is None else str(row.bridgeable)
            print(
                f"{row.convergent_n:2d} | {row.convergent_k:6d} | "
                f"{row.gap_to_next:5d} | {observed:20s} | "
                f"{row.min_reserve_to_bridge_gap:8d} | {bridgeable}"
            )

        print(f"\nwrote {paths['k53_exits']}")
        print(f"wrote {paths['ladder']}")

    elif args.command == "post-k53":
        stats_rows, step_rows = analyze_post_k53_behavior(
            args.starts,
            max_steps=args.max_steps,
            bridge_gap=args.bridge_gap,
        )
        paths = write_post_k53_outputs(stats_rows, step_rows, args.out_dir)

        print("Post-k=53 actual exponent behavior")
        print(
            "orbit | exit | steps | frac_a1 | frac_a2 | frac_a>=3 | "
            "avg_a | avg_c | drain | req306 | bridgeable"
        )
        for row in stats_rows:
            print(
                f"{row.orbit:9d} | {row.k53_exit_step:4d} | "
                f"{row.post_steps:5d} | {row.frac_a1:7.3f} | "
                f"{row.frac_a2:7.3f} | {row.frac_a_ge3:9.3f} | "
                f"{row.average_a:5.3f} | {row.average_credit:5.3f} | "
                f"{row.actual_drain_per_step:6.3f} | "
                f"{row.observed_bridge_required_306:6d} | "
                f"{row.observed_bridgeable_by_exit_reserve}"
            )

        if stats_rows:
            avg_drain = sum(row.actual_drain_per_step for row in stats_rows) / len(stats_rows)
            avg_required = sum(row.observed_bridge_required_306 for row in stats_rows) / len(stats_rows)
            conservative = stats_rows[0].conservative_bridge_required_306
            conservative_drain = stats_rows[0].conservative_drain_per_step
            print("\nSummary")
            print(f"mean actual drain per step: {avg_drain:.3f}")
            print(f"conservative drain per step: {conservative_drain:.3f}")
            print(f"mean observed-model bridge reserve for {args.bridge_gap}: {avg_required:.1f}")
            print(f"conservative bridge reserve for {args.bridge_gap}: {conservative}")

        print(f"\nwrote {paths['stats']}")
        print(f"wrote {paths['steps']}")

    elif args.command == "k53-capacity":
        required = args.required_reserve or [85, 128]
        observed_rows, requirement_rows = analyze_k53_capacity(
            args.starts,
            required_reserves=required,
            max_steps=args.max_steps,
            credit_scan_limit=args.credit_scan_limit,
        )
        paths = write_k53_capacity_outputs(observed_rows, requirement_rows, args.out_dir)

        print("Observed k=53 macro-corridor capacity")
        print(
            "orbit | steps | L | gain | c2_window | best_c2 | "
            "entry_bits | max_bits | maxL_entry | maxL_max"
        )
        for row in observed_rows:
            print(
                f"{row.orbit:9d} | {row.start_step:4d}-{row.end_step:<4d} | "
                f"{row.length:3d} | {row.actual_gain_to_peak:4d} | "
                f"{row.high_credit_steps_observed_window:9d} | "
                f"{row.best_high_credit_steps_same_length_0_to_scan:7d} | "
                f"{row.entry_x_bit_length:10d} | {row.max_x_bit_length_in_corridor:8d} | "
                f"{row.max_len_from_entry_bits:10d} | {row.max_len_from_max_bits:8d}"
            )

        print("\nReserve requirements under k=53 credit density and martingale bound")
        print(
            "reserve | direct_L | instr_L | min_bits | log10(n) | log10(mu_bound) | "
            "log10(expected_starts)"
        )
        for row in requirement_rows:
            print(
                f"{row.required_reserve:7d} | "
                f"{row.direct_min_corridor_length_at_credit_density:8d} | "
                f"{row.instruction_min_corridor_length:7d} | "
                f"{row.min_starting_bit_length:8d} | "
                f"{row.approximate_integer_log10:8.1f} | "
                f"{row.martingale_log10_probability_upper_bound:15.2f} | "
                f"{row.expected_starts_log10_lower_bound:21.2f}"
            )

        print(f"\nwrote {paths['observed']}")
        print(f"wrote {paths['requirements']}")

    elif args.command == "corridor-bound":
        bit_lengths = args.bit_length or [50, 100, 200, 500, 1000]
        observed_rows, synthetic_rows, ceiling_rows = analyze_corridor_bound(
            args.starts,
            bit_lengths=bit_lengths,
            samples_per_bit_length=args.samples_per_bit_length,
            max_steps=args.max_steps,
            beta_threshold=args.beta_threshold,
            random_seed=args.random_seed,
        )
        paths = write_corridor_bound_outputs(
            observed_rows,
            synthetic_rows,
            ceiling_rows,
            args.out_dir,
        )

        print("Observed main k=53 macro-corridor ratios")
        print(
            "orbit | bits(n) | L | L/bits | entry_bits | exit_bits | "
            "consumed/L | peakD"
        )
        for row in observed_rows:
            print(
                f"{row.orbit:9d} | {row.start_bit_length:7d} | "
                f"{row.length:3d} | {row.length_over_start_bits:6.3f} | "
                f"{row.entry_x_bit_length:10d} | {row.exit_x_bit_length:9d} | "
                f"{row.bits_consumed_per_step:10.3f} | {row.peak_reserve:5d}"
            )

        print("\nSynthetic beta-quality corridor summary")
        print("bits | samples | entered | max_L | max_L/bits | maxD")
        for bit_length in bit_lengths:
            rows = [row for row in synthetic_rows if row.bit_length == bit_length]
            entered = [row for row in rows if row.entered_k53_quality]
            max_l = max(
                (row.best_corridor_length or 0 for row in rows),
                default=0,
            )
            max_ratio = max(
                (row.length_over_start_bits or 0.0 for row in rows),
                default=0.0,
            )
            max_d = max((row.max_reserve for row in rows), default=0)
            print(
                f"{bit_length:4d} | {len(rows):7d} | {len(entered):7d} | "
                f"{max_l:5d} | {max_ratio:10.3f} | {max_d:4d}"
            )

        print("\nFormal reserve ceiling")
        print("bits | max_L | max_reserve | bridge85 | bridge128")
        for row in ceiling_rows:
            print(
                f"{row.bit_length:4d} | {row.max_corridor_length:5d} | "
                f"{row.max_reserve:11d} | {row.bridge_85_possible!s:8s} | "
                f"{row.bridge_128_possible!s:9s}"
            )

        print(f"\nwrote {paths['observed']}")
        print(f"wrote {paths['synthetic']}")
        print(f"wrote {paths['ceiling']}")

    elif args.command == "scaling-sweep":
        bit_lengths = args.bit_length or [50, 100, 200, 500, 1000, 2000]
        thresholds = args.beta_threshold or [0.5, 0.1, 0.05]
        summary_rows, fit_rows, kill_rows = analyze_scaling_sweep(
            bit_lengths=bit_lengths,
            thresholds=thresholds,
            samples_per_bit_length=args.samples_per_bit_length,
            max_steps=args.max_steps,
            workers=args.workers,
            chunk_size=args.chunk_size,
            random_seed=args.random_seed,
        )
        paths = write_scaling_sweep_outputs(summary_rows, fit_rows, kill_rows, args.out_dir)

        print("Scaling sweep summary")
        print("beta | bits | samples | any_pos | quality | frac_quality | max_L | L/bits | max_gain")
        for row in summary_rows:
            print(
                f"{row.beta_threshold:4.2f} | {row.bit_length:4d} | "
                f"{row.samples:7d} | {row.positive_corridor_orbits:7d} | "
                f"{row.quality_corridor_orbits:7d} | "
                f"{row.fraction_entering_quality_corridor:12.6f} | "
                f"{row.max_length:5d} | {row.max_length_over_bits:6.3f} | "
                f"{row.max_reserve_gain:8d}"
            )

        print("\nFits")
        print("beta | model | a | b | r2")
        for row in fit_rows:
            print(
                f"{row.beta_threshold:4.2f} | {row.model:6s} | "
                f"{row.coefficient_a:10.5f} | {row.coefficient_b:10.5f} | "
                f"{row.r_squared:7.4f}"
            )

        print("\nKill scale under best fit")
        print("beta | D | model | L_req | B_req | log10 E<=1e80 | log10 E<=1e120 | log10 E<=1e500")
        for row in kill_rows:
            b_req = "inf" if row.required_bit_length == math.inf else (
                f"{row.required_bit_length:.1f}" if row.required_bit_length is not None else ""
            )
            print(
                f"{row.beta_threshold:4.2f} | {row.required_reserve:3d} | "
                f"{row.best_model:6s} | {row.required_corridor_length:5d} | "
                f"{b_req:>8s} | {row.expected_below_1e80_log10:14.2f} | "
                f"{row.expected_below_1e120_log10:15.2f} | "
                f"{row.expected_below_1e500_log10:15.2f}"
            )

        print(f"\nwrote {paths['summary']}")
        print(f"wrote {paths['fits']}")
        print(f"wrote {paths['kill']}")

    elif args.command == "tail-law":
        threshold_rows, fit_rows, projection_rows, zero_rows = analyze_tail_law(
            args.ranges,
            min_threshold=args.min_threshold,
            fit_min_thresholds=args.fit_min_threshold,
            target_reserves=args.target_reserve,
        )
        paths = write_tail_law_outputs(
            threshold_rows,
            fit_rows,
            projection_rows,
            zero_rows,
            args.out_dir,
        )

        print("Cumulative empirical reserve tail")
        print("D | count >=D | odds scanned | rate | log10(rate)")
        for row in threshold_rows:
            log_rate = (
                f"{row.log10_empirical_rate:.6f}"
                if row.log10_empirical_rate is not None
                else ""
            )
            print(
                f"{row.threshold_reserve:2d} | "
                f"{row.count_at_least_threshold:9d} | "
                f"{row.odd_starts_scanned:12d} | "
                f"{row.empirical_rate:.9e} | {log_rate}"
            )

        print("\nExponential tail fits")
        print("fit D>= | points | slope log10/D | per-D factor | R2")
        for row in fit_rows:
            print(
                f"{row.fit_min_threshold:7d} | {row.points:6d} | "
                f"{row.slope_per_reserve_log10:13.6f} | "
                f"{row.per_reserve_factor:12.4f} | {row.r_squared:6.4f}"
            )

        print("\nProjected expected odd starts")
        print("fit D>= | target D | log10 expected odds")
        for row in projection_rows:
            print(
                f"{row.fit_min_threshold:7d} | {row.target_reserve:8d} | "
                f"{row.projected_expected_odd_starts_log10:20.3f}"
            )

        print("\nZero-hit bound")
        for row in zero_rows:
            print(
                f"D>={row.threshold_reserve}: 0 hits in "
                f"{row.odd_starts_scanned} odd starts; "
                f"95% upper rate ~= {row.zero_hit_95_upper_rate:.3e}, "
                f"log10 expected odds lower bound ~= "
                f"{row.expected_odd_starts_95_lower_log10:.3f}"
            )

        print(f"\nwrote {paths['thresholds']}")
        print(f"wrote {paths['fits']}")
        print(f"wrote {paths['projections']}")
        print(f"wrote {paths['zero_bound']}")

    elif args.command == "lock2-scan":
        summary, near_rows, all_rows, prediction_rows, small_rho_rows = analyze_lock2_scan(
            Amax=args.Amax,
            top_n=args.top_n,
            include_all_rows=args.write_all,
            first_contractivity_only=args.first_contractivity_only,
            predict_rho_slack_min=args.predict_rho_slack_min,
            predict_theta_candidate_min=args.predict_theta_candidates_min,
            predict_theta_over_rho_min=args.predict_theta_over_rho_min,
            prediction_top_n=args.prediction_top_n,
        )
        paths = write_lock2_scan_outputs(
            summary,
            near_rows,
            all_rows,
            prediction_rows,
            small_rho_rows,
            args.out_dir,
            args.Amax,
        )

        print("Lock 2 exhaustive margin scan")
        print(f"Amax={summary['Amax']}")
        print(f"first_contractivity_only={summary['first_contractivity_only']}")
        print(f"contractive_words={summary['contractive_words']}")
        print(f"first_contractivity_words={summary['first_contractivity_words']}")
        print(f"all_twos_zero_margins={summary['all_twos_zero_margins']}")
        print(f"nontrivial_zero_margins={summary['nontrivial_zero_margins']}")
        print(f"negative_margins={summary['negative_margins']}")
        print(f"lock2_holds_in_scan={summary['lock2_holds_in_scan']}")

        min_margin = summary["min_nontrivial_margin"]
        min_gap = summary["min_nontrivial_relative_gap"]
        if min_margin:
            print("\nSmallest nontrivial raw margin")
            print(
                f"word=({min_margin['word']}) A={min_margin['A']} "
                f"k={min_margin['k']} rho={min_margin['rho']} "
                f"margin={min_margin['margin']} "
                f"relative_gap={min_margin['relative_gap']:.6e}"
            )
        if min_gap:
            print("\nSmallest nontrivial relative gap")
            print(
                f"word=({min_gap['word']}) A={min_gap['A']} "
                f"k={min_gap['k']} rho={min_gap['rho']} "
                f"margin={min_gap['margin']} "
                f"relative_gap={min_gap['relative_gap']:.6e}"
            )

        print("\nTheta bucket attack")
        print("candidate odd residues <= theta | count")
        for bucket, count in summary["theta_candidate_buckets"].items():
            print(f"{bucket:>28s} | {count}")
        max_bucket_row = summary["max_theta_candidate_odd_count_row"]
        if max_bucket_row:
            print(
                "max candidate odd count: "
                f"{summary['max_theta_candidate_odd_count']} "
                f"from word=({max_bucket_row['word']}) "
                f"A={max_bucket_row['A']} k={max_bucket_row['k']} "
                f"rho={max_bucket_row['rho']}"
            )

        print("\nSmall rho counts")
        for key, count in summary["rho_small_counts"].items():
            print(f"{key}: {count}")

        print("\nRho bit-slack buckets")
        print("(A+1)-bit_length(rho) | count")
        for bucket, count in summary["rho_bit_slack_buckets"].items():
            print(f"{bucket:>23s} | {count}")

        print("\nPer-A threat maxima")
        print("A | words | min_rho | max_theta/rho | max_candidate/rho_rank")
        for A_key, row in summary["by_A"].items():
            if row["contractive"] == 0:
                continue
            print(
                f"{int(A_key):2d} | {row['contractive']:7d} | "
                f"{row['min_rho']:7d} | "
                f"{row['max_theta_over_rho']:.6f} | "
                f"{row['max_candidate_to_rho_rank_ratio']:.6f}"
            )

        knobs = summary["prediction_knobs"]
        if any(
            knobs[key] is not None
            for key in ("rho_slack_min", "theta_candidate_min", "theta_over_rho_min")
        ):
            print("\nPrediction knob matches")
            print(f"knobs={knobs}")
            print(f"matches={summary['prediction_match_count']}")
            print("word | A | k | rho | theta/rho | candidates | rho_slack")
            for row in prediction_rows[:30]:
                print(
                    f"({row.word}) | {row.A:2d} | {row.k:2d} | "
                    f"{row.rho:8d} | {row.theta_over_rho:.6e} | "
                    f"{row.theta_candidate_odd_count:10d} | {row.rho_bit_slack:9d}"
                )

        print("\nTop near-failures by relative gap")
        print("word | A | k | rho | margin | relative_gap | delta2 | first_contract")
        for row in near_rows[:30]:
            print(
                f"({row.word}) | {row.A:2d} | {row.k:2d} | "
                f"{row.rho:8d} | {row.margin:12d} | "
                f"{row.relative_gap:.6e} | {row.delta_from_all_twos:6d} | "
                f"{row.first_contractivity_index}"
            )

        print(f"\nwrote {paths['summary']}")
        print(f"wrote {paths['near_failures']}")
        print(f"wrote {paths['theta_buckets']}")
        print(f"wrote {paths['small_rho']}")
        print(f"wrote {paths['by_A_threats']}")
        if "words" in paths:
            print(f"wrote {paths['words']}")
        if "predictions" in paths:
            print(f"wrote {paths['predictions']}")

    elif args.command == "lock3-backward":
        start_time = time.monotonic()

        def find_lock3_rust_engine() -> Path | None:
            env_path = os.environ.get("LOCK3_CENSUS_BIN")
            candidates = []
            if env_path:
                candidates.append(Path(env_path))
            which_path = shutil.which("lock3_census")
            if which_path:
                candidates.append(Path(which_path))
            repo_root = Path(__file__).resolve().parents[2]
            candidates.extend(
                [
                    repo_root / "target" / "release" / "lock3_census",
                    Path("/tmp/collatz-rust-target/release/lock3_census"),
                ]
            )
            for candidate in candidates:
                if candidate.is_file() and os.access(candidate, os.X_OK):
                    return candidate
            return None

        def lock3_progress(progress: dict) -> None:
            if args.progress_every <= 0:
                return
            current_depth = progress["depth"]
            if current_depth != args.depth and current_depth % args.progress_every:
                return
            elapsed = time.monotonic() - start_time
            print(
                "lock3-progress "
                f"C={progress['C']} "
                f"depth={current_depth}/{progress['target_depth']} "
                f"branches={progress['branch_count']} "
                f"budget_paths={progress['total_budget_paths']} "
                f"valid_from_1={progress['valid_backward_paths_from_1']} "
                f"residue_classes={progress['valid_backward_residue_classes']} "
                f"rho_bits={progress['largest_rho_bit_length']} "
                f"total_considered={progress['total_paths_considered']} "
                f"elapsed_sec={elapsed:.1f} "
                f"notes={progress['notes']}",
                file=sys.stderr,
                flush=True,
            )

        def lock3_census_progress(progress: dict) -> None:
            if args.progress_every <= 0:
                return
            current_depth = progress["depth"]
            if current_depth != args.depth and current_depth % args.progress_every:
                return
            elapsed = time.monotonic() - start_time
            print(
                "lock3-census-progress "
                f"C={progress['C']} "
                f"depth={current_depth}/{progress['target_depth']} "
                f"branches={progress['symbolic_branch_count']} "
                f"merged={progress['merged_state_count']} "
                f"valid1={progress['valid_from_1_count']} "
                f"compatible_signatures={progress['terminal_1_compatible_signature_count']} "
                f"valid_residues={progress['valid_residue_count']} "
                f"mod={progress['residue_modulus']} "
                f"lifts={progress['rho_lift_count']} "
                f"longest_plateau={progress['longest_plateau']} "
                f"max_bits={progress['max_rho_bit_length']} "
                f"elapsed_sec={elapsed:.1f} "
                f"notes={progress['notes']}",
                file=sys.stderr,
                flush=True,
            )

        if args.mode == "census":
            if args.engine in ("auto", "rust"):
                rust_engine = find_lock3_rust_engine()
                if rust_engine is not None:
                    command = [
                            str(rust_engine),
                            "--C",
                            str(args.C),
                            "--depth",
                            str(args.depth),
                            "--terminal-value",
                            str(args.terminal_value),
                            "--residue-mod-power",
                            str(args.residue_mod_power),
                            "--out-dir",
                            str(args.out_dir),
                            "--progress-every",
                            str(args.progress_every),
                    ]
                    if args.checkpoint_path is not None:
                        command.extend(["--checkpoint-path", str(args.checkpoint_path)])
                    if args.checkpoint_every:
                        command.extend(["--checkpoint-every", str(args.checkpoint_every)])
                    if args.resume is not None:
                        command.extend(["--resume", str(args.resume)])
                    subprocess.run(command, check=True)
                    return
                if args.engine == "rust":
                    raise SystemExit(
                        "Rust Lock 3 census engine not found. Build it with: "
                        "cargo build --release --bin lock3_census "
                        "--target-dir /tmp/collatz-rust-target"
                    )

            summary, census_rows, event_rows, witness_records = analyze_lock3_census(
                C=args.C,
                depth=args.depth,
                terminal_value=args.terminal_value,
                residue_mod_power=args.residue_mod_power,
                progress_callback=lock3_census_progress,
            )
            paths = write_lock3_census_outputs(
                summary,
                census_rows,
                event_rows,
                witness_records,
                args.out_dir,
                args.C,
            )
            print("Lock 3 bounded-deficit census")
            print(f"C={args.C}")
            print(f"depth={args.depth}")
            print(f"symbolic_branch_count={summary['symbolic_branch_count']}")
            print(f"merged_state_count={summary['merged_state_count']}")
            print(f"valid_from_1_count={summary['valid_from_1_count']}")
            print(
                "terminal_1_compatible_signature_count="
                f"{summary['terminal_1_compatible_signature_count']}"
            )
            print(f"valid_residue_count={summary['valid_residue_count']}")
            print(f"residue_modulus={summary['residue_modulus']}")
            print(f"rho_lift_count={summary['rho_lift_count']}")
            print(f"longest_plateau={summary['longest_plateau']}")
            print(f"max_rho_bit_length={summary['max_rho_bit_length']}")
            print(f"witness_count={summary['witness_count']}")
            print(f"wrote summary: {paths['summary']}")
            print(f"wrote census: {paths['census']}")
            print(f"wrote events: {paths['events']}")
            print(f"wrote witnesses: {paths['witnesses']}")
            return

        summary, survivor_rows, path_rows, lift_rows = analyze_lock3_backward(
            C=args.C,
            depth=args.depth,
            terminal_value=args.terminal_value,
            max_paths=args.max_paths,
            max_path_rows=args.max_path_rows,
            max_lift_rows=args.max_lift_rows,
            skip_terminal_checks=args.skip_terminal_checks,
            progress_callback=lock3_progress,
        )
        paths = write_lock3_backward_outputs(
            summary,
            survivor_rows,
            path_rows,
            lift_rows,
            args.out_dir,
            args.C,
            args.depth,
        )
        print("Lock 3 bounded-deficit backward solver")
        print(f"C={args.C}")
        print(f"depth={args.depth}")
        print(f"terminal_value={args.terminal_value}")
        print(f"total_paths_considered={summary['total_paths_considered']}")
        print(f"any_path_appears_extendable={summary['any_path_appears_extendable']}")
        print(f"number_of_lift_events={summary['number_of_lift_events']}")
        print(f"longest_stable_plateau={summary['longest_stable_plateau']}")
        print(f"largest_rho_bit_length={summary['largest_rho_bit_length']}")
        if survivor_rows:
            last = survivor_rows[-1]
            print(
                f"final_depth branch_count={last.branch_count} "
                f"valid_from_1={last.valid_backward_paths_from_1} "
                f"residue_classes={last.valid_backward_residue_classes}"
            )
        for name, path in paths.items():
            print(f"wrote {name}: {path}")


if __name__ == "__main__":
    main()
