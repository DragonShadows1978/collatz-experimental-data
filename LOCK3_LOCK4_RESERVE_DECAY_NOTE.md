# Lock 3 / Lock 4 Reserve-Decay Mechanism

Status: working mechanism note, preserved from the C6-C50 `m=1` cutoff data.

## Core Mechanism

`3x + 1` creates apparent reserve, but the forced divisions by 2 spend that
reserve faster than it can become durable.

In corridor language:

```text
3x+1 creates reserve
/2 consumes reserve
residue precision debt grows
net reserve decays
```

The wider the corridor `C`, the faster the effective cutoff falls behind the
naive `3C` expectation.

```text
cutoff(C) = 3C - decay(C)
```

The measured `m=1` line shows `decay(C)` increasing with `C`:

```text
C6  cutoff 17  = 3C - 1
C10 cutoff 27  = 3C - 3
C20 cutoff 51  = 3C - 9
C30 cutoff 75  = 3C - 15
C40 cutoff 99  = 3C - 21
C50 cutoff 123 = 3C - 27
```

So corridor width has diminishing returns. A wider corridor does not buy stable
survival budget. It buys less relative reserve as `C` grows.

## Lock 4 Consequence

Lock 4 asks whether an orbit can build enough reserve to bridge the next
continued-fraction gap.

Lock 3 now explains why that reserve cannot be accumulated inside a finite
corridor:

```text
more width needed -> faster precision decay -> more reserve needed
```

That feedback is the source of the exponential reserve wall.

The orbit tries to widen the corridor to carry enough reserve, but widening the
corridor increases the precision debt. The debt consumes the reserve before the
Lock 4 bridge can be reached.

## Compact Statement

Lock 3 and Lock 4 are the same obstruction viewed at different scales:

```text
Lock 3: no bounded corridor can preserve reserve forever.
Lock 4: no bridge can accumulate enough reserve to cross the next gap.
```

The reason is not merely that `3C + 1` fails as a local cutoff slogan. The
stronger mechanism is that the cutoff decays faster as corridor width grows:

```text
forced /2 payments outpace apparent 3x+1 reserve
```

That is the reserve-decay wall.
