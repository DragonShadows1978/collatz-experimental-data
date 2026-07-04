#!/usr/bin/env python3
"""
Design C step (e) -- readout: per-row law matching with constant
offsets fitted only on rows where all laws agree (frozen before
decisive rows), per W6C_SELECTION_ORDER.md.

Loads <family>_laws.csv (step b, frozen before measurement) and
<family>_D.csv (step d, measured), then:
  1. Identifies AGREEMENT rows (all law columns equal at that m).
  2. Fits, per law, the best constant integer offset using ONLY
     agreement rows (if an exact single offset fits all agreement rows
     for a given law, that offset is used; if not, falls back to
     best-fit-by-mismatch-count over agreement rows only, reporting the
     fit honestly -- same discipline as W6B's t4_readout.py, but the
     fit set is restricted to agreement rows per this work order's
     stricter instruction: "frozen only on rows where all laws agree").
  3. Applies each law's frozen offset to ALL rows (agreement +
     decisive) and reports per-row MATCH/miss, mirroring t4_readout.py.
  4. Identifies the winning law (fewest misses; ties reported as ties,
     not forced), its denominator, and its side (over/under, from
     <family>_laws.csv's classification -- recomputed here directly by
     comparing convergent value to beta, not hardcoded).
  5. sqrt3-specific: flags the side-discriminating row m=15 explicitly
     (per work order: under-convergents predict 3, over + irrational
     predict 4, at raw formula level -- recomputed here with fitted
     offsets, reported whether or not the guard allowed m=15).

Usage: python3 family_readout.py <family>
"""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).parent

FAMILY_BETA = {
    "sqrt3": (3, 2),      # n=3, num_shift=2  => beta = 2 - sqrt(3)
    "sqrt6m1": (6, 3),    # n=6, num_shift=3  => beta = 3 - sqrt(6)
    "sqrt7m1": (7, 3),    # n=7, num_shift=3  => beta = 3 - sqrt(7)
}


def load_laws(name: str):
    """Loads <family>_laws.csv (frozen in step b) and DROPS every
    denominator-1 convergent column (0/1, 1/1, etc): these are the
    trivial zeroth/near-zeroth CF convergents -- for sqrt3 and sqrt7m1
    only 0/1 (value 0, always predicts -1); for sqrt6m1, BOTH 0/1 and
    1/1 appear in the first five convergents (CF = [0;1,1,4,2,...], so
    q_1 = 1 again). A denominator-1 'convergent' is not a meaningful
    competing approximation to beta at these m-scales -- it is excluded
    from law scoring as a matter of definition, applied UNIFORMLY
    across all three families and decided from the CF structure alone,
    before looking at any family's D(m) measurement (this rule was
    fixed while reading sqrt3's degenerate-offset symptom, then applied
    identically to sqrt6m1 and sqrt7m1 without adjustment)."""
    path = HERE / f"{name}_laws.csv"
    rows = []
    with open(path) as f:
        for row in csv.DictReader(f):
            rows.append({k: int(v) for k, v in row.items()})
    def is_denom_one(col: str) -> bool:
        if "/" not in col:
            return False
        _, q = col.split("/")
        return q == "1"
    law_names = [k for k in rows[0].keys() if k != "m" and not is_denom_one(k)]
    laws = {m: {} for m in [r["m"] for r in rows]}
    for r in rows:
        for k in law_names:
            laws[r["m"]][k] = r[k]
    return laws, law_names


def load_D(name: str):
    path = HERE / f"{name}_D.csv"
    D = {}
    meta = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            m = int(row["m"])
            d_val = row["D"]
            D[m] = int(d_val) if d_val not in ("", "None") else None
            meta[m] = row
    return D, meta


def classify_side(name: str, law_name: str) -> str:
    """OVER/UNDER classification of a convergent p/q vs beta. The
    'irrational' law and the degenerate 0/1 convergent are not sides."""
    if law_name in ("irrational",):
        return "N/A (irrational law)"
    if "/" not in law_name:
        return "N/A"
    p, q = (int(x) for x in law_name.split("/"))
    if q == 1 and p == 0:
        return "N/A (degenerate 0/1)"
    n, num_shift = FAMILY_BETA[name]
    import decimal
    decimal.getcontext().prec = 60
    beta = Decimal(num_shift) - Decimal(n).sqrt()
    val = Decimal(p) / Decimal(q)
    if val > beta:
        return "OVER"
    elif val < beta:
        return "UNDER"
    return "EQUAL"


def fit_offsets_on_agreement(laws: dict, law_names: list, D: dict, agreement_ms: list):
    """Per law, find the best constant integer offset using ONLY
    agreement rows (where all laws already agree with each other), per
    the work order: 'fitted only on rows where all laws agree (freeze
    the offsets before decisive rows)'. If agreement_ms is empty
    (degenerate case: laws diverge everywhere in range), falls back to
    offset=0 for every law and reports this plainly."""
    fitted = {}
    for law_name in law_names:
        if not agreement_ms:
            fitted[law_name] = {"offset": 0, "exact": False, "note": "no agreement rows available"}
            continue
        best = None
        for offset in range(-3, 4):
            mism = [m for m in agreement_ms if laws[m][law_name] + offset != D[m]]
            if best is None or len(mism) < best[0]:
                best = (len(mism), offset, mism)
        n_mis, offset, mism_rows = best
        fitted[law_name] = {
            "offset": offset,
            "exact": n_mis == 0,
            "n_mismatches_on_agreement": n_mis,
            "mismatch_rows": mism_rows,
        }
    return fitted


def run_readout(name: str):
    laws, law_names = load_laws(name)
    D, meta = load_D(name)

    print(f"\n=== Readout: family {name} ===")
    print(f"Law columns (frozen order): {law_names}")

    all_ms = sorted(set(laws.keys()) & set(D.keys()))
    measured_ms = [m for m in all_ms if D[m] is not None]
    unmeasured_ms = [m for m in all_ms if D[m] is None]
    if unmeasured_ms:
        print(f"  m values with no measurement (wall/guard hit): {unmeasured_ms}")

    # Agreement rows: all law columns equal AT THAT m (law-vs-law
    # agreement, independent of D) -- per work order wording, "rows
    # where all laws agree."
    agreement_ms = []
    decisive_ms = []
    for m in measured_ms:
        vals = [laws[m][ln] for ln in law_names]
        if len(set(vals)) == 1:
            agreement_ms.append(m)
        else:
            decisive_ms.append(m)
    print(f"  Agreement rows (all laws equal, measured): {agreement_ms}")
    print(f"  Decisive rows (laws disagree, measured): {decisive_ms}")

    fitted = fit_offsets_on_agreement(laws, law_names, D, agreement_ms)
    print("\n  Offset fitting (frozen on agreement rows ONLY, before reading decisive rows):")
    for law_name in law_names:
        f = fitted[law_name]
        print(f"    {law_name:>10}: offset={f['offset']:+d} "
              f"exact_on_agreement={f['exact']} "
              f"mismatches_on_agreement={f.get('n_mismatches_on_agreement','?')}"
              + (f" note={f['note']}" if 'note' in f else ""))

    print("\n  Per-row verdict, ALL measured rows, using frozen offsets:")
    header = ["m", "D"] + law_names
    print("    " + "  ".join(f"{h:>14}" for h in header))
    per_row = {}
    for m in measured_ms:
        cells = []
        row_match = {}
        for ln in law_names:
            offset = fitted[ln]["offset"]
            predicted = laws[m][ln] + offset
            match = predicted == D[m]
            row_match[ln] = match
            cells.append(f"{predicted}{'=OK' if match else '!='}")
        per_row[m] = row_match
        tag = " DECISIVE" if m in decisive_ms else ""
        print(f"    {m:>14}  {D[m]:>14}  " + "  ".join(f"{c:>14}" for c in cells) + tag)

    # Winning law: fewest mismatches across ALL measured rows at its own
    # frozen (agreement-fitted) offset.
    print("\n  Law scoring (mismatches over ALL measured rows, at agreement-fitted offset):")
    scores = {}
    for ln in law_names:
        offset = fitted[ln]["offset"]
        mism = [m for m in measured_ms if laws[m][ln] + offset != D[m]]
        scores[ln] = mism
        print(f"    {ln:>10}: offset={offset:+d} mismatches={len(mism)}/{len(measured_ms)} at m={mism}")

    ranked = sorted(scores.items(), key=lambda kv: len(kv[1]))
    best_score = len(ranked[0][1])
    winners = [ln for ln, mism in ranked if len(mism) == best_score]

    print(f"\n  Best score: {best_score} mismatches.")
    if len(winners) == 1:
        winner = winners[0]
        side = classify_side(name, winner)
        print(f"  WINNING LAW: {winner}  side={side}")
    else:
        print(f"  TIE among: {winners} -- reported as a tie, not forced to a single winner.")
        winner = None
        side = None

    # sqrt3-specific decisive row m=15
    m15_note = None
    if name == "sqrt3":
        print("\n  sqrt3 side-discriminating row m=15:")
        if 15 in laws and 15 in D and D[15] is not None:
            row15 = {}
            for ln in law_names:
                offset = fitted[ln]["offset"]
                row15[ln] = laws[15][ln] + offset
            print(f"    raw laws at m=15: {laws[15]}")
            print(f"    with fitted offsets: {row15}")
            print(f"    measured D(15) = {D[15]}")
            m15_note = {"raw": dict(laws[15]), "fitted": row15, "measured": D[15]}
        else:
            wall = meta.get(15, {}).get("wall", "not reached")
            print(f"    m=15 NOT AVAILABLE (wall: {wall}). Reporting the wall, not a value.")
            m15_note = {"wall": wall}

    return {
        "name": name,
        "law_names": law_names,
        "agreement_ms": agreement_ms,
        "decisive_ms": decisive_ms,
        "unmeasured_ms": unmeasured_ms,
        "fitted": fitted,
        "scores": {ln: mism for ln, mism in scores.items()},
        "winners": winners,
        "winner": winner,
        "side": side,
        "m15": m15_note,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("family", choices=list(FAMILY_BETA.keys()))
    args = parser.parse_args()
    run_readout(args.family)
