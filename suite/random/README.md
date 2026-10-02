# Pseudo-random number module

This directory contains a small seedable pseudo-random number generator intended as
shared infrastructure for the BCPL demonstration suite.

The implementation uses the Park-Miller "minimal standard" generator with Schrage's
overflow-avoiding formulation.  This is deliberately chosen so that the sequence does
not depend on signed 32-bit multiplication overflow semantics.

## Interface

The module reserves GLOBAL slots 190 through 193:

- `RANDSEED:190` — set the generator state;
- `RAND:191` — return the next pseudo-random integer;
- `RANDRANGE:192` — return a pseudo-random integer in `0..N-1`;
- `RANDSTATE:193` — private persistent generator state.

`RANDSEED(N)` normalizes the seed into the valid Park-Miller state range.  A zero
seed becomes 1.  `RAND()` returns values in `1..2147483646`.  `RANDRANGE(N)` returns
0 for non-positive `N`; otherwise it returns `RAND() REM N`.

This is not a cryptographic random-number generator.  It is intended for algorithms,
demonstrations, reproducible test data, randomized search order, shuffling, and similar
suite programs.

## Demonstration

`demo.bcpl` seeds the generator, prints five raw values, reseeds it, and prints ten
values in the range 0 through 99.

Run it as a two-module BCPL program:

```sh
tools/compile-and-run --results \
    asm/icintv16.asm \
    suite/random/demo.bcpl \
    +suite/random/random.bcpl
```

For seed 1, the first five raw values should be:

```text
16807
282475249
1622650073
984943658
1144108930
```

For seed 12345, the ten `RANDRANGE(100)` results should be:

```text
15
24
16
96
31
99
20
50
40
19
```

These known sequences make the module useful as a regression test as well as a
shared facility for later demonstrations.
