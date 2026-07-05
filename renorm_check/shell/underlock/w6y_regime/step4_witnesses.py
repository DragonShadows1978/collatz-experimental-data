#!/usr/bin/env python3
"""
W6Y-REGIME -- Step 4: witness discipline.

For each new edge found in step2 (C=16..26), exact-replay a witness:
backward exact-rho reconstruction from rho=1, TRUE forward Collatz
replay (exact division at every step), deficit-range check against C --
reusing mx_core.verify_witness_exact (validated already, not
reimplemented). Reports the n0 (slow-descender start integer) at each
edge and tabulates the n0-vs-depth (edge m) relation.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "w6x_multi"))
import mx_core as mx  # noqa: E402

HERE = Path(__file__).parent


def main():
    data = json.loads((HERE / "step2_measurement_full.json").read_text())
    results = data["results"]

    ladder = []
    print(f"{'C':>3} {'edge':>5} {'n0':>10} {'backward_ok':>12} {'collatz_ok':>11} "
          f"{'range':>6} {'deficit_ok':>11} {'all_ok':>7}")
    for r in results:
        C, edge = r["C"], r["edge"]
        if edge is None:
            continue
        w = mx.sparse_survival_multi(edge, C, reading="B", want_witness=True)
        if not w["alive"] or w["witness"] is None:
            print(f"{C:>3} {edge:>5}  -- witness reconstruction FAILED (unexpected) --")
            continue
        letters = mx.letters_for(edge, "B")
        v = mx.verify_witness_exact(w["witness"], C, letters)
        ladder.append({"C": C, "edge": edge, "n0": v["start_integer"],
                        "backward_ok": v["backward_ok"], "collatz_ok": v["collatz_replay_ok"],
                        "range": v["range"], "deficit_ok": v["deficit_ok"], "all_ok": v["all_ok"]})
        print(f"{C:>3} {edge:>5} {v['start_integer']:>10} {v['backward_ok']!s:>12} "
              f"{v['collatz_replay_ok']!s:>11} {v['range']:>6} {v['deficit_ok']!s:>11} {v['all_ok']!s:>7}")

    (HERE / "step4_witness_ladder.json").write_text(json.dumps(ladder, indent=2))

    print("\n=== n0-vs-depth ladder (sorted by edge m) ===")
    for row in sorted(ladder, key=lambda x: x["edge"]):
        print(f"  m={row['edge']:>4} (C={row['C']:>2}): n0={row['n0']}")

    all_ok = all(row["all_ok"] for row in ladder)
    print(f"\n=== All witnesses verified: {all_ok} ===")


if __name__ == "__main__":
    main()
