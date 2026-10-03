# BCPL Language Demonstrations

This directory contains small programs whose primary purpose is to demonstrate BCPL language constructs and characteristic programming idioms. Unlike the algorithm-oriented demonstrations in the parent `suite/` directory, these examples are intentionally simple enough that the language feature itself remains the focus.

The current examples are:

- `declarations` — `LET`, `AND`, local variables, and declaration scope;
- `valof-resultis` — expression-valued blocks using `VALOF` and `RESULTIS`;
- `switchon` — `SWITCHON`, `CASE`, `DEFAULT`, and `ENDCASE`;
- `table-vector` — `TABLE` expressions, vectors, `!` indexing, and simple copying;
- `manifest-global` — `MANIFEST` constants and an explicitly assigned `GLOBAL`-vector slot;
- `repeat-forms` — `REPEAT`, `REPEATWHILE`, `REPEATUNTIL`, and `BREAK`;
- `strings-bytes` — packed BCPL strings, their length byte, and `GETBYTE` access;
- `test-then-or` — BCPL's `TEST ... THEN ... OR` conditional command;
- `boolean-operators` — truth values, relational operators, logical AND/OR, and logical NOT;
- `pointer-idioms` — vector addresses, pointer aliases, and `!` indexing through an alias;
- `function-values` — routine values, assignment of a routine to a variable, and indirect invocation through `APPLY`.

Run the complete language demonstration class with:

```text
tools/run-language-demos
```

The runner uses ICINT V17 and reports each example as `PASS` or `FAIL`.

Run an individual example from the repository root with:

```text
tools/compile-and-run --results --listing heavy \
    asm/icintv17.asm \
    suite/language/EXAMPLE/EXAMPLE.bcpl
```

These examples deliberately follow the declaration discipline accepted by the historical MR10 compiler used by this reconstruction: declarations appear at the beginning of their enclosing block before executable commands.

The first seven examples have been exercised successfully on the local MVS/TK5 environment. The later examples should likewise be treated as executable probes of the historical compiler and hosted runtime: if a construct fails, inspect the compiler/runtime behavior before rewriting valid-looking BCPL into a different idiom.

Additional language demonstrations can be added as the hosted compiler/runtime coverage grows. Suitable future topics include byte modification, explicit stream selection, `FOR` loop details, arithmetic and shift operators, and cross-module language examples.
