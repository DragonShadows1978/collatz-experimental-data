#!/usr/bin/env python3
"""
Structure analysis of rho(C): first differences, autocorrelation, lag tests
at 22/53/75, mod-22 grouping, monotonicity.

Reads a sweep CSV produced by run_rho_sweep.sh (columns:
m,C,states,nnz_per_step,spectral_radius,gap,mode,time_sec)
and writes a JSON report + CSV table alongside it.

Usage: analyze_rho_structure.py <sweep_csv> <out_prefix> [--min-c N] [--max-c N]
"""
import csv
import json
import sys
import math


def load_sweep(path):
    rows = {}
    with open(path) as f:
        r = csv.DictReader(f)
        for row in r:
            if row.get("spectral_radius") in (None, "", "ERROR"):
                continue
            try:
                c = int(row["C"])
                rho = float(row["spectral_radius"])
            except (ValueError, KeyError):
                continue
            rows[c] = rho
    return rows


def first_differences(c_sorted, rho):
    diffs = []
    for i in range(1, len(c_sorted)):
        c0, c1 = c_sorted[i - 1], c_sorted[i]
        if c1 - c0 == 1:
            diffs.append((c1, rho[c1] - rho[c0]))
    return diffs


def autocorrelation(values, max_lag):
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    if var == 0:
        return {lag: None for lag in range(1, max_lag + 1)}
    out = {}
    for lag in range(1, max_lag + 1):
        if lag >= n:
            out[lag] = None
            continue
        s = sum((values[i] - mean) * (values[i + lag] - mean) for i in range(n - lag))
        out[lag] = (s / (n - lag)) / var
    return out


def mod_group_stats(c_sorted, rho, modulus):
    groups = {}
    for c in c_sorted:
        k = c % modulus
        groups.setdefault(k, []).append(rho[c])
    stats = {}
    for k, vals in sorted(groups.items()):
        mean = sum(vals) / len(vals)
        var = sum((v - mean) ** 2 for v in vals) / len(vals) if len(vals) > 1 else 0.0
        stats[k] = {"n": len(vals), "mean": mean, "var": var, "min": min(vals), "max": max(vals)}
    return stats


def monotonicity_report(c_sorted, rho):
    increases = decreases = flats = 0
    violations = []
    for i in range(1, len(c_sorted)):
        c0, c1 = c_sorted[i - 1], c_sorted[i]
        if c1 - c0 != 1:
            continue
        d = rho[c1] - rho[c0]
        if d > 1e-12:
            increases += 1
        elif d < -1e-12:
            decreases += 1
            violations.append((c0, c1, d))
        else:
            flats += 1
    return {
        "increases": increases,
        "decreases": decreases,
        "flats": flats,
        "decrease_events": violations[:50],
        "num_decrease_events": len(violations),
    }


def lag_alignment_test(c_sorted, rho, lag):
    """
    For each C, compare rho(C) to rho(C+lag) where both are present.
    Reports mean abs diff, max abs diff, and whether the diffs look like
    exact matches (candidate periodicity) vs a smooth trend (no special
    alignment at this lag beyond overall convergence).
    """
    pairs = []
    cset = set(c_sorted)
    for c in c_sorted:
        if (c + lag) in cset:
            pairs.append((c, rho[c], rho[c + lag], rho[c + lag] - rho[c]))
    if not pairs:
        return {"lag": lag, "n_pairs": 0}
    diffs = [p[3] for p in pairs]
    mean_abs = sum(abs(d) for d in diffs) / len(diffs)
    max_abs = max(abs(d) for d in diffs)
    exact_matches = sum(1 for d in diffs if abs(d) < 1e-9)
    return {
        "lag": lag,
        "n_pairs": len(pairs),
        "mean_abs_diff": mean_abs,
        "max_abs_diff": max_abs,
        "exact_matches_lt_1e-9": exact_matches,
        "sample_first5": pairs[:5],
    }


def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)
    sweep_csv = args[0]
    out_prefix = args[1]

    rho = load_sweep(sweep_csv)
    c_sorted = sorted(rho.keys())
    if not c_sorted:
        print("No valid rows found.", file=sys.stderr)
        sys.exit(1)

    # Full table CSV
    table_path = out_prefix + "_table.csv"
    with open(table_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["C", "rho", "C_mod_22", "C_mod_53", "C_mod_75"])
        for c in c_sorted:
            w.writerow([c, f"{rho[c]:.12e}", c % 22, c % 53, c % 75])

    diffs = first_differences(c_sorted, rho)
    values_in_order = [rho[c] for c in c_sorted]  # assumes contiguous-ish; ok for reporting
    acf = autocorrelation(values_in_order, max_lag=min(80, len(values_in_order) - 1))

    mono = monotonicity_report(c_sorted, rho)

    mod22 = mod_group_stats(c_sorted, rho, 22)
    mod53 = mod_group_stats(c_sorted, rho, 53) if max(c_sorted) >= 53 else {}
    mod75 = mod_group_stats(c_sorted, rho, 75) if max(c_sorted) >= 75 else {}

    lag_tests = {
        lag: lag_alignment_test(c_sorted, rho, lag) for lag in (22, 53, 75)
    }

    report = {
        "source_csv": sweep_csv,
        "n_points": len(c_sorted),
        "c_min": min(c_sorted),
        "c_max": max(c_sorted),
        "rho_min": min(rho.values()),
        "rho_max": max(rho.values()),
        "rho_range": max(rho.values()) - min(rho.values()),
        "first_differences_sample": diffs[:20],
        "first_differences_max_abs": max((abs(d[1]) for d in diffs), default=None),
        "first_differences_mean": (sum(d[1] for d in diffs) / len(diffs)) if diffs else None,
        "monotonicity": mono,
        "autocorrelation_lag1_10": {k: acf[k] for k in range(1, min(11, len(acf) + 1))},
        "autocorrelation_at_22_53_75": {
            str(lag): acf.get(lag) for lag in (22, 53, 75) if lag in acf
        },
        "mod22_group_stats": mod22,
        "mod53_group_stats": mod53,
        "mod75_group_stats": mod75,
        "lag_alignment_tests": lag_tests,
        "interpretation_note": (
            "If rho(C) converges to (or is already at) a constant for the C range "
            "covered, first differences ~0, autocorrelation undefined/degenerate "
            "(zero variance), and lag tests will trivially show near-zero diffs "
            "everywhere -- this indicates rho is C-INDEPENDENT in this regime, "
            "not that it has periodic structure at these specific lags. "
            "Only a nonzero-variance regime (e.g. small-C transient) can "
            "distinguish genuine 22/53/75 alignment from generic convergence."
        ),
    }

    report_path = out_prefix + "_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"table: {table_path}")
    print(f"report: {report_path}")
    print(f"n_points={len(c_sorted)} c_range=[{min(c_sorted)},{max(c_sorted)}]")
    print(f"rho_min={min(rho.values()):.12f} rho_max={max(rho.values()):.12f} range={report['rho_range']:.3e}")
    print(f"monotonicity: +{mono['increases']} -{mono['decreases']} ={mono['flats']}")


if __name__ == "__main__":
    main()
