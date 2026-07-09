#!/usr/bin/env python3
"""G2 core: exact-int Collatz orbit helpers + 2-adic cylinders for exponent words."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


def v2(n: int) -> int:
    if n == 0:
        raise ValueError("v2(0)")
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    return c


def floor_k_log2_3(k: int) -> int:
    if k == 0:
        return 0
    return (3 ** k).bit_length() - 1


def odd_step(x: int) -> tuple[int, int]:
    """Odd x → (next_odd, a) with a = v2(3x+1)."""
    assert x % 2 == 1 and x > 0
    y = 3 * x + 1
    a = v2(y)
    return y >> a, a


def a_from_residue(x: int, j: int) -> int | None:
    """If a = v2(3x+1) is determined by x mod 2^j (i.e. a < j), return a else None.

    Needs y = 3x+1 known mod 2^j; valuation known exactly iff ynot≡0 mod 2^j
    or we only claim a when a < j.
    """
    if j < 1:
        return None
    mod = 1 << j
    y = (3 * (x % mod) + 1) % mod
    if y == 0:
        # divisible by 2^j — a ≥ j, not pinned below j
        return None
    a = v2(y if y else mod)  # y != 0
    # v2 of representative: if y even, count; y is in 0..mod-1
    a = 0
    yy = y
    while yy % 2 == 0:
        yy //= 2
        a += 1
    if a < j:
        return a
    return None


def predicts_a_matches(x: int, j: int) -> bool:
    """True if residue mod 2^j correctly predicts actual a whenever a < j."""
    a_true = v2(3 * x + 1)
    pred = a_from_residue(x, j)
    if a_true < j:
        return pred == a_true
    # when a >= j, prediction may be None — OK
    return True


def a1_iff_3_mod_4(x: int) -> bool:
    """Lemma: odd x has a=1 iff x ≡ 3 (mod 4)."""
    assert x % 2 == 1
    a = v2(3 * x + 1)
    return (a == 1) == (x % 4 == 3)


@dataclass
class Cylinder:
    """x ≡ residue (mod modulus); residue odd; empty if modulus==0."""

    residue: int
    modulus: int  # power of 2
    nonempty: bool
    min_positive_odd: int | None
    note: str = ""

    @property
    def mod_bits(self) -> int:
        if self.modulus <= 1:
            return 0
        return self.modulus.bit_length() - 1


def cylinder_for_word(
    word: tuple[int, ...] | list[int],
    max_bits: int = 40,
    search_bound: int = 2_000_000,
) -> Cylinder:
    """2-adic cylinder for odd positive x realizing the full exponent word.

    Semantics: a_0=v2(3x+1), x1=(3x+1)/2^{a_0}, a_1=v2(3x1+1), ...

    Method:
      1) If sum(a)+len small, full odd-scan mod 2^{need}.
      2) Else linear search for a positive odd witness, then find smallest
         2-power modulus m=2^k such that all tested lifts r+t*m realize the word.
    """
    word = tuple(int(a) for a in word)
    if not word:
        return Cylinder(1, 2, True, 1, "empty word: all odds")
    if any(a < 1 for a in word):
        return Cylinder(0, 0, False, None, "invalid a in word")

    A = sum(word)
    need_est = A + len(word) + 3

    min_x: int | None = None
    note = ""

    if need_est <= 22:
        need = max(4, need_est)
        good: list[int] = []
        for need in range(need, min(max_bits, 28) + 1):
            M = 1 << need
            good = [x for x in range(1, M, 2) if realizes_word(x, word)]
            if good:
                break
        if good:
            min_x = min(good)
            note = f"full_scan_bits={need};n={len(good)}"
    if min_x is None:
        for x in range(1, search_bound, 2):
            if realizes_word(x, word):
                min_x = x
                break
        if min_x is None:
            return Cylinder(
                0, 0, False, None, f"no witness in 1..{search_bound} (odd)"
            )
        note = f"linear_search_bound={search_bound}"

    # Smallest 2-power modulus for which the residue class of min_x realizes word
    # (sampled lifts). Then try to shrink.
    r_final, mod_final = min_x, 1 << max_bits
    for k in range(2, max_bits + 1):
        m = 1 << k
        r = min_x % m
        lifts_ok = True
        for t in range(0, 48):
            cand = r + t * m
            if cand <= 0:
                continue
            if cand % 2 == 0:
                continue
            if not realizes_word(cand, word):
                lifts_ok = False
                break
        if lifts_ok:
            r_final, mod_final = r, m
            break
    # try shrink further
    for k in range(mod_final.bit_length() - 1, 1, -1):
        m = 1 << k
        r = min_x % m
        if all(
            realizes_word(r + t * m, word)
            for t in range(0, 48)
            if r + t * m > 0 and (r + t * m) % 2 == 1
        ):
            r_final, mod_final = r, m
        else:
            break

    # true min positive in class
    cand = r_final if r_final > 0 else mod_final
    while cand % 2 == 0 or not realizes_word(cand, word):
        cand += mod_final
        if cand > mod_final * 10000:
            cand = min_x
            break
    if cand > min_x and realizes_word(min_x, word):
        # min_x may be smaller than first positive residue in reduced class
        cand = min(cand, min_x)
    return Cylinder(r_final % mod_final, mod_final, True, cand, note)


def realizes_word(x: int, word: tuple[int, ...] | list[int]) -> bool:
    if x <= 0 or x % 2 == 0:
        return False
    cur = x
    for a_exp in word:
        nxt, a = odd_step(cur)
        if a != a_exp:
            return False
        cur = nxt
    return True


def pure_a1_cylinder(L: int) -> Cylinder:
    """Closed form: first L steps a=1 iff x ≡ -1 (mod 2^{L+1}) among odds.

    Smallest positive odd: 2^{L+1} - 1.
    """
    if L < 1:
        return Cylinder(1, 2, True, 1, "L<1")
    mod = 1 << (L + 1)
    r = (mod - 1) % mod  # -1
    min_x = mod - 1
    # verify
    ok = realizes_word(min_x, tuple(1 for _ in range(L)))
    # also verify necessity on a sample of odds mod mod
    return Cylinder(r, mod, ok, min_x if ok else None, "closed_form_-1_mod_2^{L+1}")


def pure_a1_table(L_max: int = 24) -> list[dict]:
    rows = []
    for L in range(1, L_max + 1):
        c = pure_a1_cylinder(L)
        # cross-check with general engine for small L
        if L <= 12:
            g = cylinder_for_word(tuple(1 for _ in range(L)), max_bits=L + 4)
            cross = (
                g.nonempty
                and g.min_positive_odd is not None
                and realizes_word(g.min_positive_odd, tuple(1 for _ in range(L)))
            )
        else:
            cross = None
        rows.append(
            {
                "L": L,
                "modulus": c.modulus,
                "mod_bits": c.mod_bits,
                "residue": c.residue,
                "nonempty": c.nonempty,
                "min_positive_odd": c.min_positive_odd,
                "note": c.note,
                "general_engine_ok": cross,
                "log2_min_x": (
                    None
                    if c.min_positive_odd is None
                    else (c.min_positive_odd).bit_length() - 1
                ),
            }
        )
    return rows


# ---------------------------------------------------------------------------
# Orbit / climb census
# ---------------------------------------------------------------------------

HIGH_RESERVE = [
    80049391,
    120080895,
    210964383,
    219259131,
    222250543,
    246666523,
    319804831,
    77566362559,
]


def load_breach_candidates(repo_data_runs, cap: int = 200) -> list[int]:
    import json
    from pathlib import Path

    runs = Path(repo_data_runs)
    found = []
    for folder in sorted(runs.glob("lock3_C*_breach_follow")):
        for f in folder.glob("lock3_corridor_breach_follow_*.jsonl"):
            with f.open() as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    ci = obj.get("candidate_integer")
                    if isinstance(ci, int) and ci > 0 and ci % 2 == 1:
                        found.append(ci)
    seen = set()
    out = []
    for x in found:
        if x not in seen:
            seen.add(x)
            out.append(x)
        if len(out) >= cap:
            break
    return out


def walk_orbit(x0: int, max_steps: int = 8000):
    """Yield step records; also return summary lists."""
    x = x0
    if x % 2 == 0:
        while x % 2 == 0 and x > 0:
            x //= 2
    A = 0
    C_run = 0
    steps = []
    for k in range(max_steps):
        if x == 1:
            break
        nxt, a = odd_step(x)
        A += a
        d = floor_k_log2_3(k + 1) - A
        is_up = d > C_run
        if is_up:
            C_run = d
        steps.append(
            {
                "k": k,
                "x": x,
                "a": a,
                "d": d,
                "C_run": C_run,
                "upcrossing": is_up,
            }
        )
        x = nxt
    return steps


def extract_climb_runs(steps: list[dict], start_n: int, source: str) -> list[dict]:
    """climb_run = maximal consecutive a=1 steps that include ≥1 upcrossing."""
    runs = []
    i = 0
    n = len(steps)
    while i < n:
        if steps[i]["a"] != 1:
            i += 1
            continue
        j = i
        while j < n and steps[j]["a"] == 1:
            j += 1
        # [i, j) is a=1 run
        ups = [steps[t] for t in range(i, j) if steps[t]["upcrossing"]]
        if ups:
            L = j - i
            runs.append(
                {
                    "source": source,
                    "start_n": start_n,
                    "k0": steps[i]["k"],
                    "L": L,
                    "n_upcrossings": len(ups),
                    "d_before": steps[i]["d"] if i == 0 else steps[i]["d"],
                    "d_after": steps[j - 1]["d"],
                    "x_entry": steps[i]["x"],
                    "word": "1" * L,
                }
            )
        i = j
    return runs


def extract_gap_words(steps: list[dict], max_len: int = 12) -> list[tuple[int, ...]]:
    """Exponent words from one upcrossing to the next (including trailing a), len≤max_len."""
    up_idx = [i for i, s in enumerate(steps) if s["upcrossing"]]
    words = []
    if not up_idx:
        return words
    # from start to first up
    prev = 0
    for ui in up_idx:
        seg = steps[prev : ui + 1]
        w = tuple(s["a"] for s in seg)
        if 1 <= len(w) <= max_len:
            words.append(w)
        prev = ui + 1
    return words


def count_upcrossings(steps: list[dict]) -> int:
    return sum(1 for s in steps if s["upcrossing"])
