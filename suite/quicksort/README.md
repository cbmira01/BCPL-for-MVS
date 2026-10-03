# Quicksort

Sorts a small vector with recursive quicksort. Pivot selection uses the shared seedable pseudo-random number generator in `library/random.bcpl`.

Run from the repository root using the currently promoted ICINT baseline:

```sh
tools/compile-and-run --results \
    "$(tools/current-icint)" \
    suite/quicksort/quicksort.bcpl \
    +library/random.bcpl
```

The demo-suite runner uses the same library module:

```sh
run_demo "quicksort" \
    "$COMPILE" --results \
    "$ICINT" \
    "$SUITE/quicksort/quicksort.bcpl" \
    +library/random.bcpl
```
