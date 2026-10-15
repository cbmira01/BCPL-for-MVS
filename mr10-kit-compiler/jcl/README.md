# MVS JCL

| File | Purpose |
| --- | --- |
| `build-icintv19.jcl` | Assemble and link the installed ICINT19 interpreter |
| `run-language-demos.jcl` | Compile 11 language examples, then run them |
| `run-bcpl-demos.jcl` | Compile 17 BCPL demos, then run them |
| `run-regression-tests.jcl` | Compile 12 regression cases, then run them |
| `icintv12-honors-thesis.jcl` | Saved V12 experiment |
| `icintv13-honors-thesis.jcl` | Saved V13 experiment |
| `icintv13-mapstore.jcl` | Saved V13 MAPSTORE experiment |
| `hello-world-heavy.jcl` | Assembler example |
| `dump-jes2-parameters.jcl` | JES2 configuration inspection |

The three suite files and ICINT19 build are **stored JCL bodies**; `tools/datasets/dspal submit` supplies the JOB card. See [suite commands](README-SUITES.md) and [ICINT19 build instructions](README-ICINT19.md). Older JCL decks are historical examples.
