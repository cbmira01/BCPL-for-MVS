# Random-number demo

The reusable implementation is in `mr10-kit-compiler/library/random.bcpl`.

| Call | Use |
| --- | --- |
| `SRAND(N)` | Set the seed |
| `RAND()` | Next random number |
| `RANDRANGE(N)` | Number from 0 through N-1 |
| `RANDSEED(N)` | Alias for SRAND |

This is a repeatable Park-Miller sequence, not a security-grade generator. With seed 1 the first five raw values are `16807`, `282475249`, `1622650073`, `984943658`, and `1144108930`.

The `standard-library` regression tests check these results.
