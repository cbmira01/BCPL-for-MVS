# BCPL Language Demonstrations

This directory contains small programs whose primary purpose is to demonstrate BCPL language constructs and characteristic programming idioms. Unlike the algorithm-oriented demonstrations in the parent `suite/` directory, these examples are intentionally simple enough that the language feature itself remains the focus.

The first group covers constructs already well exercised by the hosted MR10 compiler:

- `declarations` — `LET`, `AND`, local variables, and declaration scope;
- `valof-resultis` — expression-valued blocks using `VALOF` and `RESULTIS`;
- `switchon` — `SWITCHON`, `CASE`, `DEFAULT`, and `ENDCASE`;
- `table-vector` — `TABLE` expressions, vectors, `!` indexing, and simple copying.

Run an individual example from the repository root with:

```text
tools/compile-and-run --results --listing heavy \
    asm/icintv17.asm \
    suite/language/EXAMPLE/EXAMPLE.bcpl
```

These examples deliberately follow the declaration discipline accepted by the historical MR10 compiler used by this reconstruction: declarations appear at the beginning of their enclosing block before executable commands.

Additional language demonstrations can be added as the hosted compiler/runtime coverage grows. Suitable future topics include `MANIFEST` and `GLOBAL`, functions used as values, packed strings and byte access, repetition forms, explicit stream selection, and pointer-oriented BCPL idioms.
