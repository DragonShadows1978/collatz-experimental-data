#!/usr/bin/env python3
"""
J2 -- Does the spectral rate GOVERN the basin complement decay?

Fits complement_density(N) (renorm_check/shell/descent_rule/gate2_density_table.csv,
N=0..200, basin ODD-STEPS, not automaton/heartbeat steps) against:
  (a) A * rho^(N/53)         rho = 0.960647  (one rho-power per heartbeat; N is
                              basin odd-steps, 53 odd-steps = 1 heartbeat)
  (b) A * b^(N/k)            b = 0.063099 (~ (53/84)^6, the C>=10 universal
                              gap-decay base); try k=53 (one b-power per
                              heartbeat, matching rho's natural unit) as the
                              only principled choice -- k is the SAME
                              heartbeat length for both curves since both
                              rho and b are properties of the same 53-step
                              operator.
  (c) A * r^N                free per-step geometric rate, unconstrained
                              log-linear least squares fit, no relation to
                              rho or b assumed.

All three are fit via log-linear least squares: log(complement_density(N))
~ log(A) + N * log(rate_unit), where "rate_unit" for (a) is rho^(1/53), for
(b) is b^(1/53), and for (c) is a free r solved directly.

Fit separately over:
  - FULL range N=0..200 (includes early sigmoid-rise region, unfair to pure
    geometric decay per the spec's own warning)
  - TAIL range N=150..200 (post-saturation, the fair test region)
  - EARLY range N=0..20 (diagnostic only, to show why full-range fits are
    contaminated)

Report R^2 (on log-complement, i.e. how well a straight line explains
log(complement_density) vs N) and residual sum of squares (RSS) for each.
Also compare empirical per-step ratios complement_density(N)/complement_density(N-1)
in the tail against the PREDICTED per-step ratios rho^(1/53) and b^(1/53).
"""
import csv
import math
from pathlib import Path

HERE = Path(__file__).parent
CSV_PATH = HERE.parent.parent / "shell" / "descent_rule" / "gate2_density_table.csv"

RHO = 0.960647
B = 0.063099
HEARTBEAT = 53


def load_csv():
    rows = []
    with open(CSV_PATH) as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append((int(row["N"]), float(row["complement_density"])))
    return rows


def log_linear_fit(xs, ys):
    """Least squares fit of log(y) = a + b*x. Returns (a, b, R2, RSS_on_log)."""
    n = len(xs)
    mean_x = sum(xs) / n
    logys = [math.log(y) for y in ys]
    mean_logy = sum(logys) / n
    sxx = sum((x - mean_x) ** 2 for x in xs)
    sxy = sum((x - mean_x) * (ly - mean_logy) for x, ly in zip(xs, logys))
    b = sxy / sxx
    a = mean_logy - b * mean_x
    pred = [a + b * x for x in xs]
    ss_res = sum((ly - p) ** 2 for ly, p in zip(logys, pred))
    ss_tot = sum((ly - mean_logy) ** 2 for ly in logys)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return a, b, r2, ss_res


def fixed_rate_fit(xs, ys, rate_per_step):
    """Fit y = A * rate_per_step^x (only A free -- rate is FIXED from theory,
    not fit). A = exp(mean(log y - x*log rate)). Returns (A, R2, RSS_on_log)
    where R2/RSS measure how well the FIXED-SLOPE line explains log(y),
    i.e. a strictly harder/more honest test than letting slope float."""
    logr = math.log(rate_per_step)
    n = len(xs)
    logys = [math.log(y) for y in ys]
    logA_vals = [ly - x * logr for x, ly in zip(xs, logys)]
    logA = sum(logA_vals) / n
    mean_logy = sum(logys) / n
    pred = [logA + x * logr for x in xs]
    ss_res = sum((ly - p) ** 2 for ly, p in zip(logys, pred))
    ss_tot = sum((ly - mean_logy) ** 2 for ly in logys)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return math.exp(logA), r2, ss_res


def main():
    data = load_csv()
    out = []
    out.append("=" * 78)
    out.append("J2 -- basin complement_density(N) vs rho/b/free-rate fits")
    out.append("=" * 78)
    out.append(f"\nData source: {CSV_PATH}")
    out.append(f"Rows loaded: {len(data)} (N=0..200)")
    out.append(f"RHO = {RHO} (C=3 spectral lock, per 53-step heartbeat)")
    out.append(f"B   = {B} (C>=10 universal gap-decay base b ~ (53/84)^6, per m -- "
                "NOTE: b is a per-INCREMENT-OF-m rate in the spectral data, where m "
                "indexes precision level, NOT heartbeat count directly; using it here "
                "as a per-53-step rate is the spec's proposed analogy, tested honestly "
                "below and flagged if it requires a strained unit assumption)")

    rho_per_step = RHO ** (1.0 / HEARTBEAT)
    b_per_step = B ** (1.0 / HEARTBEAT)
    out.append(f"\nDerived per-odd-step rates (assuming N counts basin ODD-STEPS and "
                f"53 odd-steps = 1 heartbeat, so per-step rate = (per-heartbeat rate)^(1/53)):")
    out.append(f"  rho^(1/53) = {rho_per_step:.8f}")
    out.append(f"  b^(1/53)   = {b_per_step:.8f}")

    ranges = {
        "FULL (N=0..200)": [(n, c) for n, c in data],
        "EARLY (N=0..20, diagnostic -- sigmoid rise contaminates)":
            [(n, c) for n, c in data if n <= 20],
        "TAIL (N=150..200, fair geometric-decay test)":
            [(n, c) for n, c in data if 150 <= n <= 200],
        "DEEP TAIL (N=170..200, held-out adversarial check)":
            [(n, c) for n, c in data if 170 <= n <= 200],
    }

    for label, rows in ranges.items():
        xs = [n for n, c in rows]
        ys = [c for n, c in rows]
        out.append(f"\n--- Range: {label}  (n={len(xs)} points) ---")

        # (a) rho-governed, fixed rate
        A_rho, r2_rho, rss_rho = fixed_rate_fit(xs, ys, rho_per_step)
        out.append(f"  (a) A*rho^(N/53)  [rho^(1/53)={rho_per_step:.6f} FIXED]: "
                    f"A={A_rho:.6e}  R2={r2_rho:.6f}  RSS(log)={rss_rho:.6f}")

        # (b) b-governed, fixed rate
        A_b, r2_b, rss_b = fixed_rate_fit(xs, ys, b_per_step)
        out.append(f"  (b) A*b^(N/53)    [b^(1/53)={b_per_step:.6f} FIXED]:   "
                    f"A={A_b:.6e}  R2={r2_b:.6f}  RSS(log)={rss_b:.6f}")

        # (c) free rate, log-linear regression (slope free)
        a_free, slope_free, r2_free, rss_free = log_linear_fit(xs, ys)
        r_free = math.exp(slope_free)
        out.append(f"  (c) A*r^N         [free per-step r fit by OLS]:        "
                    f"r={r_free:.6f}  A={math.exp(a_free):.6e}  R2={r2_free:.6f}  "
                    f"RSS(log)={rss_free:.6f}")

        out.append(f"      free-fit rate r={r_free:.6f}  vs rho^(1/53)={rho_per_step:.6f}"
                    f"  (ratio {r_free/rho_per_step:.4f})"
                    f"  vs b^(1/53)={b_per_step:.6f}  (ratio {r_free/b_per_step:.4f})")

    # ---- Per-step empirical ratio table in the tail, vs predicted rates ----
    out.append("\n--- Empirical per-step ratios complement_density(N)/complement_density(N-1) "
                "in the tail, vs FIXED predicted per-step rates ---")
    tail_pts = [(n, c) for n, c in data if n >= 145]
    tail_dict = dict(data)
    out.append(f"  {'N':>4} {'compl_density':>16} {'empirical_ratio':>16} "
                f"{'rho^(1/53)':>12} {'b^(1/53)':>12}")
    prev_n, prev_c = None, None
    for n, c in tail_pts:
        if prev_n is not None and (n - prev_n) == 1 and prev_c > 0:
            ratio = c / prev_c
            out.append(f"  {n:>4} {c:>16.9f} {ratio:>16.6f} "
                        f"{rho_per_step:>12.6f} {b_per_step:>12.6f}")
        prev_n, prev_c = n, c

    # also compute avg empirical per-step ratio in deep tail via geometric mean
    deep_tail = [(n, c) for n, c in data if 170 <= n <= 200]
    ratios = []
    for i in range(1, len(deep_tail)):
        n0, c0 = deep_tail[i - 1]
        n1, c1 = deep_tail[i]
        if n1 - n0 == 5 and c0 > 0:  # csv steps by 5 in this region
            ratios.append((c1 / c0) ** (1.0 / (n1 - n0)))
    if ratios:
        geo_mean_ratio = math.exp(sum(math.log(r) for r in ratios) / len(ratios))
        out.append(f"\n  Geometric-mean empirical per-step ratio over N=170..200 "
                    f"(5-step chunks, deannualized to per-step): {geo_mean_ratio:.6f}")
        out.append(f"  vs rho^(1/53) = {rho_per_step:.6f}  "
                    f"(diff {geo_mean_ratio - rho_per_step:+.6f}, "
                    f"{100*(geo_mean_ratio/rho_per_step - 1):+.3f}%)")
        out.append(f"  vs b^(1/53)   = {b_per_step:.6f}  "
                    f"(diff {geo_mean_ratio - b_per_step:+.6f}, "
                    f"{100*(geo_mean_ratio/b_per_step - 1):+.3f}%)")

    # ---- Adversarial: does free-rate fit on FIRST HALF of tail predict SECOND HALF? ----
    out.append("\n--- Adversarial held-out check: fit free rate on N=150..175, "
                "predict N=180..200 ---")
    fit_rows = [(n, c) for n, c in data if 150 <= n <= 175]
    test_rows = [(n, c) for n, c in data if 180 <= n <= 200]
    xs_fit = [n for n, c in fit_rows]
    ys_fit = [c for n, c in fit_rows]
    a_h, slope_h, r2_h, _ = log_linear_fit(xs_fit, ys_fit)
    out.append(f"  fit on N=150..175: r={math.exp(slope_h):.6f}  A={math.exp(a_h):.6e}  "
                f"R2(in-sample)={r2_h:.6f}")
    out.append(f"  {'N':>4} {'actual':>14} {'predicted':>14} {'rel_err%':>10}")
    for n, c in test_rows:
        pred = math.exp(a_h + slope_h * n)
        rel_err = 100 * (pred - c) / c
        out.append(f"  {n:>4} {c:>14.8f} {pred:>14.8f} {rel_err:>10.2f}")

    text = "\n".join(out)
    print(text)
    (HERE / "j2_output.txt").write_text(text + "\n")


if __name__ == "__main__":
    main()
