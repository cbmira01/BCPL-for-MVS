# MR10 tools

These tools belong to the historical MR10 INTCODE compiler/interpreter workflow.

- `run-demo-suite` — run the 17 MR10 BCPL demonstrations.
- `run-language-demos` — run the language demonstration suite.
- `run-regression-panel` — run the interpreted regression panel.

The historical tool paths at the old tools root were retired during M3. Use the paths shown above. The installed interpreter is rebuilt from `MR10_JCL(IC19BLD)`; suite runners that omit `--installed-icint` may assemble an interpreter from the currently promoted source.

## Installed MR10 interpreter mode

After rebuilding `MR10_LOAD(ICINT19)` using `dspal submit MR10_JCL IC19BLD`, the compilation driver can reuse that installed load module instead of assembling and linking an interpreter in each job:

```sh
tools/mr10/compile-and-run --installed-icint MR10_LOAD --results \
  mr10-kit-compiler/tests/00-regression-panel/data-movement/scalar-vector.bcpl
```

`MR10_LOAD` is resolved from `config/dspal.yaml` (and its local override). The generated compiler steps execute `PGM=ICINT19` using that dataset in `STEPLIB`; no `ASM` or `LKED` step is emitted. Omitting the new option preserves the original assembler-source workflow, including the positional interpreter argument. Both modes use the same phase staging and output validation. Verify the generated JCL offline with `python3 tools/checks/check-mr10-installed-icint.py` before an MVS smoke run.

The native bootstrap's enlarged translator build uses this installed mode. All generated INTCODE remains disposable and must be regenerated after a purge.
