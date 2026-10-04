# BCPL demonstration suite

`suite/` contains readable BCPL programs intended to show the hosted compiler/runtime doing ordinary work. They are broader and more human-facing than the exact-output regression panel under `tests/00-regression-panel/`.

Run all 17 general demonstrations with:

```sh
tools/run-demo-suite.sh
```

The runner uses the promoted interpreter from `config/CURRENT`. Override it for a candidate interpreter with `--icint PATH`.

## General demonstrations

| Directory | What it demonstrates |
| --- | --- |
| `richards-factorial` | compact recursive factorial program retained from early bootstrap work |
| `queens` | recursive eight-queens backtracking |
| `knight` | 5x5 knight's tour using Warnsdorff's heuristic |
| `hanoi` | recursive Towers of Hanoi |
| `sieve` | Sieve of Eratosthenes over a BCPL vector |
| `gcd` | Euclid's algorithm and LCM |
| `quicksort` | recursive quicksort using the shared random library |
| `binary-search` | iterative binary search |
| `linked-list` | vector-backed linked structures and reversal |
| `binary-tree` | vector-backed binary search tree and traversal |
| `hash-table` | chained hash table using vector-backed nodes |
| `word-count` | named MVS input stream and character/word/line counting |
| `rpn-calculator` | explicit stack and reverse-Polish evaluation |
| `expression-parser` | recursive-descent arithmetic parser |
| `maze` | recursive depth-first maze search |
| `stream-fanout` | three simultaneously open named MVS input streams |
| `coroutines` | allocator-backed coroutine generator using the packaged runtime |

The richer demonstrations that need additional explanation keep their own README files. Routine one-program descriptions are centralized here rather than repeated in every subdirectory.

Run a simple individual program with:

```sh
tools/compile-and-run --results \
    "$(tools/current-icint)" \
    suite/PROGRAM/PROGRAM.bcpl
```

Some programs need extra modules or DDs; `tools/run-demo-suite.sh` is the executable reference for the exact invocation.

## Language demonstrations

`suite/language/` contains smaller programs focused on one BCPL construct or idiom. Run them with:

```sh
tools/run-language-demos
```

See `suite/language/README.md` for the list.

## Regression versus demonstration

A demo succeeds when it compiles and executes successfully and its printed result is sensible. Behavior that must never silently change belongs in the exact-output regression panel under `tests/00-regression-panel/`.