# BCPL language demonstrations

These small programs isolate language constructs accepted by the historical MR10 compiler used by the hosted bootstrap.

Current examples cover:

- `declarations` — `LET`, `AND`, local variables, and declaration scope;
- `valof-resultis` — `VALOF` and `RESULTIS`;
- `switchon` — `SWITCHON`, `CASE`, `DEFAULT`, and `ENDCASE`;
- `table-vector` — `TABLE`, vectors, and `!` indexing;
- `manifest-global` — `MANIFEST` and explicit `GLOBAL` slots;
- `repeat-forms` — `REPEAT`, `REPEATWHILE`, `REPEATUNTIL`, and `BREAK`;
- `strings-bytes` — packed strings, the length byte, and byte access;
- `test-then-or` — BCPL's `TEST ... THEN ... OR` command;
- `boolean-operators` — relations and logical operators;
- `pointer-idioms` — vector addresses and aliases;
- `function-values` — routine values and indirect invocation through `APPLY`.

Run the complete set with:

```sh
tools/run-language-demos
```

The runner uses the promoted interpreter from `config/CURRENT` and reports each example as `PASS` or `FAIL`.

These examples intentionally follow the declaration discipline accepted by the historical compiler: declarations precede executable commands in their enclosing block. If a valid-looking historical construct fails, treat that as evidence to investigate before rewriting the example into a different idiom.