# Quicksort demo

Sorts a vector using recursive quicksort. It uses `library/random.bcpl` for pivot selection.

```sh
tools/mr10/compile-and-run --results \
  "$(tools/mr10/current-icint)" \
  mr10-kit-compiler/bcpl-demo/quicksort/quicksort.bcpl \
  +mr10-kit-compiler/library/random.bcpl
```

The full demo suite is `tools/mr10/run-demo-suite`.
