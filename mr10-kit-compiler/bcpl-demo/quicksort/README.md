# Quicksort demo

Sorts a vector using recursive quicksort. It uses `library/random.bcpl` for pivot selection.

```sh
tools/compile-and-run --results \
  "$(tools/current-icint)" \
  mr10-kit-compiler/bcpl-demo/quicksort/quicksort.bcpl \
  +mr10-kit-compiler/library/random.bcpl
```

The full demo suite is `tools/run-mr10kit-demo-suite`.
