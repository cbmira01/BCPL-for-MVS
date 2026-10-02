# Quicksort

Sorts a small vector with recursive quicksort. Pivot selection uses the shared seedable pseudo-random number generator in `suite/random/random.bcpl`.

Run from the repository root:

```sh
tools/compile-and-run --results \
    asm/icintv16.asm \
    suite/quicksort/quicksort.bcpl \
    +suite/random/random.bcpl
```
