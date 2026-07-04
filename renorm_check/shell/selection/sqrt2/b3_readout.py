#!/usr/bin/env python3
"""
W6C Design B, B3 -- readout and registration, per W6C_SELECTION_ORDER.md.

Reads D_sqrt2_table.csv (written by b2_measurement.py) and laws.csv
(written by laws_table.py, frozen before any measurement), fits a
constant integer offset per candidate law on the AGREEMENT REGION
(rows m where all laws in laws.csv agree with each other -- the
work order's fitting protocol, same discipline as W6B's T4/t4_readout.py
but restricted to agreement rows as the work order specifies for B3,
not the full range), freezes those offsets, then reports:

  (a) per-row law matching across the full m range at the frozen
      offsets (T4-style, no aggregation that hides a mixed result)
  (b) the m=12 decisive-row verdict at the frozen offsets:
      7/12 (under) predicts D=6; 3/5 (over) AND the irrational law
      predict D=7 (these raw law values are read directly from
      laws.csv, offset-adjusted).

Registered predictions (frozen in W6C_SELECTION_ORDER.md, restated
verbatim, NOT re-derived or softened here):
  "Registered prediction (Fable): 6 -- R-under wins. Stated
  uncertainty: this is a mechanism hunch from golden's lag-side
  misses, not a derivation. If 7: R-coarse survives (the slope is
  already excluded as a standalone law by W6B; transfer inference
  says 7 -> R-coarse). If neither/mixed across rows: the rule is
  richer than both candidates -- report raw, no aggregation."

Usage: python3 b3_readout.py | tee b3_readout.log
"""

from __future__ import annotations

import csv
from pathlib import Path

LAW_NAMES = ["irrational", "1/2", "3/5(over)", "7/12(under)", "17/29", "41/70"]
M_DECISIVE = 12


def load_csv(path: Path, int_cols):
    rows = []
    with open(path) as f:
        for row in csv.DictReader(f):
            r = {}
            for k, v in row.items():
                if k in int_cols and v not in ("", None):
                    r[k] = int(v)
                elif v == "" or v is None:
                    r[k] = None
                else:
                    try:
                        r[k] = int(v)
                    except ValueError:
                        r[k] = v
            rows.append(r)
    return rows


def main():
    here = Path(__file__).parent
    laws_rows = load_csv(here / "laws.csv", int_cols=["m"] + LAW_NAMES)
    D_rows = load_csv(here / "D_sqrt2_table.csv",
                       int_cols=["m", "D_sqrt2", "C_final", "shell_depth", "margin", "n_attempts"])

    laws = {r["m"]: r for r in laws_rows}
    D = {r["m"]: r["D_sqrt2"] for r in D_rows}
    meta = {r["m"]: r for r in D_rows}

    ms_common = sorted(set(laws) & set(D))

    print("B3a  Agreement region: rows where ALL candidate laws in laws.csv agree")
    agreement_ms = []
    for m in ms_common:
        vals = [laws[m][name] for name in LAW_NAMES]
        if len(set(vals)) == 1:
            agreement_ms.append(m)
    print(f"    agreement rows (m): {agreement_ms}")

    print("\nB3b  Fit constant integer offset per law on the agreement region ONLY "
          "(frozen here, before comparing decisive rows m=12 etc.)")
    offsets = {}
    for name in LAW_NAMES:
        # constant offset o such that law[m] + o == D[m] for all agreement m
        candidate_offsets = set(D[m] - laws[m][name] for m in agreement_ms if D[m] is not None)
        exact_constant = len(candidate_offsets) == 1
        if exact_constant:
            offsets[name] = (next(iter(candidate_offsets)), True)
        else:
            # best-fit: minimize mismatches on agreement region, break ties toward 0
            best = None
            for o in range(-3, 4):
                n_mis = sum(1 for m in agreement_ms
                            if D[m] is not None and laws[m][name] + o != D[m])
                key = (n_mis, abs(o))
                if best is None or key < best[0]:
                    best = (key, o)
            offsets[name] = (best[1], False)
        o, exact = offsets[name]
        print(f"    {name:>14}: offset={o:+d}  exact_constant_on_agreement_region={exact}")

    print("\nB3c  Per-row law matching, full m range, at frozen offsets "
          "(no aggregation -- mixed result reported as mixed)")
    header = ["m", "D_sqrt2", "shell_depth", "margin"] + LAW_NAMES
    print("    " + "  ".join(f"{h:>14}" for h in header))
    per_row_match = {}
    for m in ms_common:
        d = D[m]
        cells = []
        matches_this_row = {}
        for name in LAW_NAMES:
            o, _ = offsets[name]
            predicted = laws[m][name] + o
            match = (d is not None) and (predicted == d)
            matches_this_row[name] = match
            cells.append(f"{predicted}{'*' if match else ''}")
        per_row_match[m] = matches_this_row
        row_meta = meta.get(m, {})
        sd = row_meta.get('shell_depth')
        mg = row_meta.get('margin')
        print(f"    {m:>14}  {str(d) if d is not None else 'None':>14}  "
              f"{str(sd) if sd is not None else '-':>14}  "
              f"{str(mg) if mg is not None else '-':>14}  "
              + "  ".join(f"{c:>14}" for c in cells))
    print("    (* marks a match at that law's frozen offset; unmarked = miss)")

    print("\nB3d  Match-count summary per law (measured rows only; unmeasured "
          "rows, e.g. a wall-hit m, are excluded from the denominator)")
    measured_ms = [m for m in ms_common if D[m] is not None]
    for name in LAW_NAMES:
        n_match = sum(1 for m in measured_ms if per_row_match[m][name])
        n_total = len(measured_ms)
        o, exact = offsets[name]
        miss_rows = [m for m in measured_ms if not per_row_match[m][name]]
        print(f"    {name:>14}: {n_match}/{n_total} rows match at offset {o:+d} "
              f"(exact_constant_on_agreement={exact})  misses at m={miss_rows}")

    print(f"\nB3e  THE DECISIVE ROW: m={M_DECISIVE}")
    print("    Registered predictions (verbatim from W6C_SELECTION_ORDER.md, "
          "restated, NOT re-derived or softened):")
    print("      \"7/12 (under) predicts D=6; 3/5 (over) AND the irrational law "
          "predict D=7.\"")
    print("      \"Registered prediction (Fable): 6 -- R-under wins. Stated "
          "uncertainty: this is a mechanism hunch from golden's lag-side "
          "misses, not a derivation. If 7: R-coarse survives (the slope is "
          "already excluded as a standalone law by W6B; transfer inference "
          "says 7 -> R-coarse). If neither/mixed across rows: the rule is "
          "richer than both candidates -- report raw, no aggregation.\"")

    if M_DECISIVE not in D or D[M_DECISIVE] is None:
        print(f"    m={M_DECISIVE} not measured or measurement is None -- "
              f"CANNOT VERDICT. Report as inconclusive.")
    else:
        d12 = D[M_DECISIVE]
        raw_irr = laws[M_DECISIVE]["irrational"]
        raw_over = laws[M_DECISIVE]["3/5(over)"]
        raw_under = laws[M_DECISIVE]["7/12(under)"]
        print(f"    Raw law values at m=12 (from laws.csv, frozen pre-measurement): "
              f"irrational={raw_irr}  3/5(over)={raw_over}  7/12(under)={raw_under}")
        o_irr, _ = offsets["irrational"]
        o_over, _ = offsets["3/5(over)"]
        o_under, _ = offsets["7/12(under)"]
        pred_irr = raw_irr + o_irr
        pred_over = raw_over + o_over
        pred_under = raw_under + o_under
        print(f"    Offset-adjusted predictions at m=12: "
              f"irrational={pred_irr} (offset {o_irr:+d})  "
              f"3/5(over)={pred_over} (offset {o_over:+d})  "
              f"7/12(under)={pred_under} (offset {o_under:+d})")
        print(f"    MEASURED D_sqrt2(12) = {d12}")

        print("\n    TWO READINGS (both reported; neither buried):")
        print(f"    (1) RAW-VALUE mapping as literally registered "
              f"(6 -> R-under; 7 -> R-coarse; other -> neither): "
              f"raw measured D_sqrt2(12) = {d12} -> "
              + ("R-UNDER" if d12 == 6 else ("R-COARSE" if d12 == 7 else "NEITHER")))
        print("    (2) FROZEN-OFFSET protocol (the work order's own fitting rule, "
              "offsets fitted on the agreement region, frozen before this row):")
        under_match = (d12 == pred_under)
        over_match = (d12 == pred_over)
        irr_match = (d12 == pred_irr)
        print(f"        7/12(under)+offset = {pred_under}  "
              f"{'MATCH' if under_match else 'miss'}")
        print(f"        3/5(over)+offset   = {pred_over}  "
              f"{'MATCH' if over_match else 'miss'}")
        print(f"        irrational+offset  = {pred_irr}  "
              f"{'MATCH' if irr_match else 'miss'}")
        if under_match and not over_match and not irr_match:
            proto = "UNDER-side law uniquely matches -> R-UNDER under the offset protocol"
        elif (over_match or irr_match) and not under_match:
            proto = "over/irrational side matches, under misses -> R-COARSE under the offset protocol"
        elif under_match and (over_match or irr_match):
            proto = "offsets collapsed the distinction -> AMBIGUOUS under the offset protocol"
        else:
            proto = "no law matches at frozen offsets -> NEITHER; rule richer than both candidates"
        print(f"        -> {proto}")
        if (d12 == 7) and under_match and not over_match:
            print("    NOTE (reported loudly, not smoothed): the two readings "
                  "CONFLICT. The registered mapping's premise -- 'with fitted "
                  "offsets, 7/12 predicts D=6; 3/5 and irrational predict D=7' "
                  "-- presupposed zero fitted offsets. The actually-fitted "
                  "offset on the agreement region is nonzero (see B3b), under "
                  "which 7/12 predicts the measured value and the others do "
                  "not. The raw value 7 is simultaneously the registered "
                  "'R-coarse' number AND the under-law's offset-adjusted "
                  "prediction. Both facts are true; integration (outside this "
                  "design's scope) must decide which reading the F5 transfer "
                  "inference should use. Raw data and per-row tables above "
                  "are the record.")


if __name__ == "__main__":
    main()
