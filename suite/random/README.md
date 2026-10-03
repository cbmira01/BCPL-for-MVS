# Pseudo-random number demonstration

This directory demonstrates the reusable pseudo-random number implementation now maintained in `library/random.bcpl`.

The library uses the Park-Miller "minimal standard" generator with Schrage's overflow-avoiding formulation, so the sequence does not depend on signed 32-bit multiplication overflow semantics.

The public interface is:

```text
SRAND(N)
RAND()
RANDRANGE(N)
RANDSEED(N)   compatibility spelling for SRAND
```

Run the demonstration from the repository root with:

```sh
tools/compile-and-run --results \
    "$(tools/current-icint)" \
    suite/random/demo.bcpl \
    +library/random.bcpl
```

For seed 1, the first five raw values are expected to be:

```text
16807
282475249
1622650073
984943658
1144108930
```

For seed 12345, the ten `RANDRANGE(100)` results are expected to be:

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

The corresponding exact-output regression is part of the `standard-library` regression-panel category.
