# Lock 1 Rotation Window Lemma

Date: 2026-05-25

## Claim

Let:

```text
D = 2^A - 3^k > 0
```

and let `w` be a primitive necklace that survives all walls before the final
wall:

```text
M | B_w
D = Mq
```

If any cyclic rotation `rho(w)` satisfies:

```text
0 < B_rho(w) < D
```

then `w` cannot close a nontrivial loop.

## Proof

Rotation preserves divisibility by every wall. Therefore, if `w` could close
the loop, the rotated word `rho(w)` could also close it.

The loop value at that rotation would be:

```text
x_rho = B_rho(w) / D
```

But:

```text
0 < B_rho(w) < D
```

so:

```text
0 < x_rho < 1
```

This is impossible for a positive integer odd cycle.

Therefore any pre-final survivor with a rotation below the `D` window is killed
without needing a final residue calculation.

## Final-Quotient Form

Since:

```text
D = Mq
M | B_rho(w)
```

write:

```text
C_rho = B_rho(w) / M
```

Then:

```text
B_rho(w) < D
iff
C_rho < q
```

So the rotation-window test is:

```text
exists rotation rho(w) with 0 < C_rho < q
```

If true, then:

```text
q does not divide C_rho
```

and final closure is impossible.

## Implemented Measurement

Implemented inside:

```text
rust/lock1_final_wall_quotient_miner.rs
```

Current artifact:

```text
data/runs/lock1_final_wall_quotient_k8_t30
```

Summary:

```text
pre_final_classes=121
final_hit_classes=0
rotation_window_proved_necklaces=28145
rotation_window_unresolved_necklaces=64
rotation_window_unresolved_classes=9
```

So on the current surface:

```text
28145 / 28209
```

pre-final primitive necklaces are killed by the rotation-window lemma.

## Unresolved Kernel On Current Surface

The rotation-window test leaves only small-wall classes:

```text
k=3,A=5:   unresolved=2
k=4,A=7:   unresolved=5
k=5,A=8:   unresolved=7
k=5,A=9:   unresolved=10
k=6,A=10:  unresolved=6
k=6,A=11:  unresolved=14
k=7,A=12:  unresolved=2
k=7,A=13:  unresolved=3
k=8,A=13:  unresolved=15
```

Every one of these still has:

```text
C_w != 0 mod q
```

in the quotient artifact. The remaining symbolic task is to prove that these
small-wall kernels cannot persist into a general infinite family.
