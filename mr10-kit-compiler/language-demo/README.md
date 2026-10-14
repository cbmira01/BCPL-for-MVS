# BCPL language examples

Each small program tests one language feature and prints a short `DEMO:` line.

| Program | Feature |
| --- | --- |
| declarations | Local declarations and scope |
| valof-resultis | Returning a value with VALOF/RESULTIS |
| switchon | SWITCHON, CASE, DEFAULT |
| table-vector | TABLE, vectors, and word indexing |
| manifest-global | MANIFEST constants and GLOBAL slots |
| repeat-forms | REPEAT loop forms |
| strings-bytes | Strings and byte access |
| test-then-or | TEST/THEN/OR |
| boolean-operators | Comparisons and Boolean operations |
| pointer-idioms | Pointers and aliases |
| function-values | Functions passed or called through values |

## Run

```sh
tools/run-language-demos
```

On MVS, install `MR10_LANGDEMO` members and submit `MR10_JCL(MRLANGDM)`. See [suite jobs](../jcl/README-SUITES.md).

**BCPL rule:** Inside a block, local `LET` declarations must come before executable statements.
