# Tests and probes

Two kinds of tests live here:

| Directory | Purpose |
| --- | --- |
| `00-regression-panel/` | 12 short tests with saved expected output |
| `01-echo-test/` | First INTCODE input/output |
| `02-honors-thesis-and-mapstore/` | Early ICINT and MAPSTORE tests |
| `03-compile-richards-factorial/` | Compiler pipeline and saved intermediate code |
| `04-module-test/` | Separate compilation and GLOBAL linkage |
| `05-named-dd/` | Named MVS input DDs |
| `06-dynamic-streams/` | Nested and dynamic streams |
| `07-many-streams/` | 12 simultaneous input streams |
| `08-character-translation/` | ASCII, EBCDIC, and BCPL characters |
| `09-multiple-assignment/` | Historical assignment order |
| `10-coroutines/` | Coroutine calls, frames, and storage |
| `11-getvec-freevec/` | Dynamic storage allocation |

## Run

```sh
tools/mr10/run-regression-panel
```

Use `tools/mr10/compile-and-run` for individual BCPL probes and `tools/mr10/run-intcode` for existing INTCODE files. Some probes need added modules or DD files; consult their local README.

Saved OCODE and INTCODE files are evidence, not build litter. Keep them where they explain an observed compiler or runtime behavior.
