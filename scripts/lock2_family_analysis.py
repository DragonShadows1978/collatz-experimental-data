#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from collatz_experimental_data.exact import odd_syracuse_step


A54 = (
    1, 1, 1, 1, 1, 4, 1, 2, 1, 1, 2, 1, 1, 1, 2, 3, 1,
    1, 2, 1, 2, 1, 1, 1, 1, 1, 3, 1, 1, 1, 4, 2, 2, 4,
)
A59 = (
    1, 2, 1, 1, 1, 1, 2, 2, 1, 2, 1, 1, 2, 1, 1, 1, 2, 3, 1,
    1, 2, 1, 2, 1, 1, 1, 1, 1, 3, 1, 1, 1, 4, 2, 2, 4, 3,
)


@dataclass(frozen=True)
class Hit:
    word: tuple[int, ...]
    a_sum: int
    k: int
    rho: int
    score: Fraction
    comparison: str
    verified: bool


def word_text(word: tuple[int, ...] | list[int]) -> str:
    return "(" + ",".join(str(x) for x in word) + ")"


def parse_word(text: str) -> tuple[int, ...]:
    text = text.strip()
    if not text:
        return ()
    return tuple(int(part) for part in text.split(",") if part)


def affine_prefix_rows(word: tuple[int, ...]) -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    a_prefix = 0
    b_prefix = 0
    for j, exponent in enumerate(word, start=1):
        b_prefix = 3 * b_prefix + (1 << a_prefix)
        a_prefix += exponent
        pow3 = 3**j
        pow2 = 1 << a_prefix
        deficit = pow3.bit_length() - 1 - a_prefix
        contractive = pow2 > pow3
        if contractive:
            den = pow2 - pow3
            threat = Fraction(b_prefix, den)
            threat_text = f"{threat.numerator}/{threat.denominator}"
            threat_float = f"{float(threat):.15f}"
        else:
            threat_text = "N/A"
            threat_float = "N/A"
        rows.append(
            {
                "j": j,
                "a_j": exponent,
                "A_j": a_prefix,
                "k_j": j,
                "deficit_j": deficit,
                "B_j": b_prefix,
                "status": "contractive" if contractive else "solvent",
                "partial_threat": threat_text,
                "partial_threat_float": threat_float,
            }
        )
    return rows


def write_prefix_csv(path: Path, word: tuple[int, ...]) -> None:
    rows = affine_prefix_rows(word)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def common_prefix(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    out = []
    for lhs, rhs in zip(a, b):
        if lhs != rhs:
            break
        out.append(lhs)
    return tuple(out)


def common_suffix(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    out = []
    for lhs, rhs in zip(reversed(a), reversed(b)):
        if lhs != rhs:
            break
        out.append(lhs)
    return tuple(reversed(out))


def longest_common_contiguous(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, int, tuple[int, ...]]:
    best_i = 0
    best_j = 0
    best_len = 0
    for i in range(len(a)):
        for j in range(len(b)):
            length = 0
            while i + length < len(a) and j + length < len(b) and a[i + length] == b[j + length]:
                length += 1
            if length > best_len:
                best_i = i
                best_j = j
                best_len = length
    return best_i, best_j, a[best_i : best_i + best_len]


def is_subsequence(needle: tuple[int, ...], haystack: tuple[int, ...]) -> bool:
    idx = 0
    for item in haystack:
        if idx < len(needle) and item == needle[idx]:
            idx += 1
    return idx == len(needle)


def blocks(word: tuple[int, ...]) -> list[tuple[str, tuple[int, ...]]]:
    out: list[tuple[str, tuple[int, ...]]] = []
    i = 0
    while i < len(word):
        value = word[i]
        j = i + 1
        while j < len(word) and word[j] == value:
            j += 1
        run = word[i:j]
        if value == 2 and len(run) == 2:
            label = "pair(2,2)"
        elif len(run) > 1:
            label = f"run-of-{value}s({len(run)})"
        elif value >= 3:
            label = f"isolated-{value}"
        else:
            label = f"single-{value}"
        out.append((label, run))
        i = j
    return out


def orbit(start: int, steps: int) -> tuple[list[int], list[int]]:
    values = [start]
    exponents = []
    x = start
    for _ in range(steps):
        x, exponent = odd_syracuse_step(x)
        exponents.append(exponent)
        values.append(x)
    return exponents, values


def agreement(a: tuple[int, ...], b: list[int]) -> int:
    count = 0
    for lhs, rhs in zip(a, b):
        if lhs != rhs:
            break
        count += 1
    return count


def read_hits(path: Path) -> list[Hit]:
    hits: list[Hit] = []
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            hits.append(
                Hit(
                    word=parse_word(row["word"]),
                    a_sum=int(row["A"]),
                    k=int(row["k"]),
                    rho=int(row["rho"]),
                    score=Fraction(int(row["score_num"]), int(row["score_den"])),
                    comparison=row["comparison"],
                    verified=row["verified"].lower() == "true",
                )
            )
    return hits


def score_bucket(score: Fraction) -> str:
    if score >= Fraction(3, 4):
        return "[0.75,1.0]"
    if score >= Fraction(1, 2):
        return "[0.5,0.75)"
    if score >= Fraction(2, 5):
        return "[0.4,0.5)"
    if score >= Fraction(3, 10):
        return "[0.3,0.4)"
    if score >= Fraction(1, 4):
        return "[0.25,0.3)"
    if score >= Fraction(1, 5):
        return "[0.2,0.25)"
    return "<0.2"


def suffix_key(word: tuple[int, ...], length: int = 4) -> tuple[int, ...]:
    return word[-length:] if len(word) >= length else word


def write_report(path: Path, hits: list[Hit]) -> None:
    prefix = common_prefix(A54, A59)
    suffix = common_suffix(A54, A59)
    a54_core = A54[len(prefix) : len(A54) - len(suffix)]
    a59_core = A59[len(prefix) : len(A59) - len(suffix)]
    core_i, core_j, core = longest_common_contiguous(A54, A59)
    orbit63_exp, orbit63_vals = orbit(63, 40)
    orbit27_exp, orbit27_vals = orbit(27, 45)
    a54_agreement = agreement(A54, orbit63_exp)
    a59_agreement = agreement(A59, orbit27_exp)
    a54_blocks = blocks(A54)
    a59_blocks = blocks(A59)

    by_rho: dict[int, list[Hit]] = defaultdict(list)
    by_suffix: dict[tuple[int, ...], list[Hit]] = defaultdict(list)
    for hit in hits:
        by_rho[hit.rho].append(hit)
        by_suffix[suffix_key(hit.word)].append(hit)

    histogram = Counter(score_bucket(hit.score) for hit in hits)
    a54_suffix = (4, 2, 2, 4)
    a54_suffix_hits = [hit for hit in hits if hit.word[-4:] == a54_suffix]

    lines = [
        "# Lock 2 A54/A59 Family Alignment",
        "",
        "## Common Prefix And Suffix",
        "",
        f"Longest common prefix length: {len(prefix)}",
        f"Longest common prefix: {word_text(prefix)}",
        f"Longest common suffix length: {len(suffix)}",
        f"Longest common suffix: {word_text(suffix)}",
        "",
        f"A54: {word_text(prefix)} {word_text(a54_core)} {word_text(suffix)}",
        f"A59: {word_text(prefix)} {word_text(a59_core)} {word_text(suffix)}",
        "",
        f"A59 prepends to A54: {A59[-len(A54):] == A54}",
        f"A59 appends to A54: {A59[:len(A54)] == A54}",
        f"A54 is contiguous inside A59: {contains_contiguous(A54, A59)}",
        f"A54 is subsequence inside A59: {is_subsequence(A54, A59)}",
        f"A59 is rotation of A54: {len(A54) == len(A59) and contains_contiguous(A54, A54 + A54)}",
        f"Exponent-count A54: {dict(sorted(Counter(A54).items()))}",
        f"Exponent-count A59: {dict(sorted(Counter(A59).items()))}",
        "",
        "## Longest Shared Core",
        "",
        f"Longest common contiguous block length: {len(core)}",
        f"A54 offset: {core_i}",
        f"A59 offset: {core_j}",
        f"Core: {word_text(core)}",
        "",
        "## Actual Orbit Comparison",
        "",
        f"rho=63 first 40 exponents: {word_text(tuple(orbit63_exp))}",
        f"rho=63 agrees with A54 for {a54_agreement}/{len(A54)} steps",
        f"rho=63 image after A54 word: {orbit63_vals[len(A54)]}",
        f"rho=63 next six odd values after A54 word: {orbit63_vals[len(A54):len(A54)+7]}",
        f"rho=63 continues descending after word end: {orbit63_vals[len(A54)] < 63}",
        "",
        f"rho=27 first 45 exponents: {word_text(tuple(orbit27_exp))}",
        f"rho=27 agrees with A59 for {a59_agreement}/{len(A59)} steps",
        f"rho=27 image after A59 word: {orbit27_vals[len(A59)]}",
        f"rho=27 next six odd values after A59 word: {orbit27_vals[len(A59):len(A59)+7]}",
        f"rho=27 continues descending after word end: {orbit27_vals[len(A59)] < 27}",
        "",
        f"27 appears in rho=63 orbit prefix: {27 in orbit63_vals}",
        f"63 appears in rho=27 orbit prefix: {63 in orbit27_vals}",
        f"27 is immediate successor of 63: {len(orbit63_vals) > 1 and orbit63_vals[1] == 27}",
        f"63 is immediate successor of 27: {len(orbit27_vals) > 1 and orbit27_vals[1] == 63}",
        "",
        "## Block Decomposition",
        "",
        "| index | A54 block | A59 block |",
        "| ---: | :--- | :--- |",
    ]
    for idx in range(max(len(a54_blocks), len(a59_blocks))):
        lhs = block_text(a54_blocks[idx]) if idx < len(a54_blocks) else ""
        rhs = block_text(a59_blocks[idx]) if idx < len(a59_blocks) else ""
        lines.append(f"| {idx} | {lhs} | {rhs} |")

    lines.extend(
        [
            "",
            "## Family Search Above 0.2 Through Amax 100",
            "",
            f"Total hits: {len(hits)}",
            f"Verified hits: {sum(hit.verified for hit in hits)}",
            "",
            "| score bucket | count |",
            "| :--- | ---: |",
        ]
    )
    for bucket in ["[0.75,1.0]", "[0.5,0.75)", "[0.4,0.5)", "[0.3,0.4)", "[0.25,0.3)", "[0.2,0.25)"]:
        lines.append(f"| `{bucket}` | {histogram.get(bucket, 0)} |")

    lines.extend(["", "### Hits By Score", "", "| word | A | k | rho | score | suffix4 |", "| :--- | ---: | ---: | ---: | ---: | :--- |"])
    for hit in sorted(hits, key=lambda item: item.score, reverse=True):
        lines.append(
            f"| `{word_text(hit.word)}` | {hit.a_sum} | {hit.k} | {hit.rho} | {float(hit.score):.15f} | `{word_text(suffix_key(hit.word))}` |"
        )

    lines.extend(["", "### Grouped By Rho", ""])
    for rho, rows in sorted(by_rho.items()):
        labels = ", ".join(f"A={hit.a_sum},k={hit.k},score={float(hit.score):.6f}" for hit in sorted(rows, key=lambda item: item.score, reverse=True))
        lines.append(f"- rho={rho}: {labels}")

    lines.extend(["", "### Grouped By Common Suffix4", ""])
    for suffix4, rows in sorted(by_suffix.items(), key=lambda item: (-len(item[1]), item[0])):
        labels = ", ".join(f"A={hit.a_sum},k={hit.k},rho={hit.rho},score={float(hit.score):.6f}" for hit in sorted(rows, key=lambda item: item.score, reverse=True))
        lines.append(f"- {word_text(suffix4)}: {labels}")

    lines.extend(
        [
            "",
            "## Relationship Determination",
            "",
            f"Hits ending in A54 suffix {word_text(a54_suffix)}: {len(a54_suffix_hits)}",
            f"A54 suffix appears in: {', '.join(f'A={hit.a_sum},k={hit.k},rho={hit.rho}' for hit in a54_suffix_hits)}",
            "",
            "A59 is not a prepend, append, rotation, or permutation-extension of A54.",
            "The real shared structure is a long aligned suffix/core. A59 has a different head and one extra terminal 3 after the A54-family suffix.",
            "The above-0.2 family through Amax=100 is small: A51, A54, A59, old A7, and the trivial all-2 case.",
            "A51 and A54 share the exact suffix (4,2,2,4). A59 extends that suffix to (4,2,2,4,3).",
            "This looks more like a suffix/core family than a monotone score-improving chain: A51 score 0.204686, A54 score 0.572331, A59 score 0.323160.",
        ]
    )

    path.write_text("\n".join(lines) + "\n")


def contains_contiguous(needle: tuple[int, ...], haystack: tuple[int, ...]) -> bool:
    if not needle:
        return True
    return any(haystack[i : i + len(needle)] == needle for i in range(len(haystack) - len(needle) + 1))


def block_text(block: tuple[str, tuple[int, ...]]) -> str:
    label, run = block
    return f"{label} `{word_text(run)}`"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("data/runs"))
    parser.add_argument(
        "--hits",
        type=Path,
        default=Path("data/runs/lock2_reverse_barrier_hits_Amax100_20260523T_lock2_reverse_barrier_family_search_Amax100.csv"),
    )
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_prefix_csv(args.out_dir / "lock2_prefix_analysis_A54.csv", A54)
    write_prefix_csv(args.out_dir / "lock2_prefix_analysis_A59.csv", A59)
    hits = read_hits(args.hits)
    write_report(args.out_dir / "lock2_family_alignment.md", hits)

    print(f"wrote {args.out_dir / 'lock2_prefix_analysis_A54.csv'}")
    print(f"wrote {args.out_dir / 'lock2_prefix_analysis_A59.csv'}")
    print(f"wrote {args.out_dir / 'lock2_family_alignment.md'}")


if __name__ == "__main__":
    main()
