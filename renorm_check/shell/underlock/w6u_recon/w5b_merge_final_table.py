#!/usr/bin/env python3
"""
W6U-RECON step 5b -- merge the corrected D_recon columns
(w5_corrected_table.csv, reconciled object = variant (ii)
free-endpoint range, END-anchored window validated by all six genuine
G3 gates) with the w2 game-D columns into the round's single final
deliverable table.
"""
import csv
from pathlib import Path

HERE = Path(__file__).parent

w2 = {int(r["m"]): r for r in csv.DictReader(open(HERE / "w2_comparison_table.csv"))}
w5 = {int(r["m"]): r for r in csv.DictReader(open(HERE / "w5_corrected_table.csv"))}

rows = []
for m in sorted(w5):
    r5, r2 = w5[m], w2[m]
    D = int(r5["D_recon_end"])
    mirror = int(r5["mirror_law_D_per"])
    g_end = int(r2["game_D_end_anchored"])
    g_root = int(r2["game_D_root_anchored"])
    rows.append({
        "m": m,
        "D_recon": D,                       # reconciled object (END-anchored, variant ii)
        "mirror_law_D_per": mirror,
        "game_D_root_anchored": g_root,
        "game_D_end_anchored": g_end,
        "D_recon_root_variant": int(r5["D_recon_root"]),  # root-anchored letters (fails G3, kept for the dictionary)
        "D_recon_eq_mirror": D == mirror,
        "D_recon_eq_game_end": D == g_end,
        "D_recon_eq_game_root": D == g_root,
        "witness_n0": r5["witness_end_n0"],
        "witness_a_seq": r5["witness_end"],
    })

out = HERE / "w5_final_merged_table.csv"
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    for r in rows:
        w.writerow(r)

print(f"{'m':>3} {'D_recon':>8} {'mirror':>7} {'gD_root':>8} {'gD_end':>7} "
      f"{'=mirror':>8} {'=g_end':>7} {'=g_root':>8}")
n_eq_end = 0
for r in rows:
    n_eq_end += r["D_recon_eq_game_end"]
    print(f"{r['m']:>3} {r['D_recon']:>8} {r['mirror_law_D_per']:>7} "
          f"{r['game_D_root_anchored']:>8} {r['game_D_end_anchored']:>7} "
          f"{r['D_recon_eq_mirror']!s:>8} {r['D_recon_eq_game_end']!s:>7} "
          f"{r['D_recon_eq_game_root']!s:>8}")
print(f"\nD_recon == game_D_end on {n_eq_end}/{len(rows)} rows")
print(f"D_recon == mirror on {sum(r['D_recon_eq_mirror'] for r in rows)}/{len(rows)} rows "
      f"(matches exactly m<=28; breaks at 29+)")
print(f"Wrote {out}")
