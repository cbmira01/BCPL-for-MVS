# M2.0 Gate B — Independent BCPLAPT G40 Integration

**Status: IMPLEMENTED IN GIT; MVS acceptance PENDING** (13 October 2026).

## Scope and source change

Canonical `asm/bcplmain.asm` now declares `EXTRN APTOVEC,APLIMIT`, writes its tested `STKLIM` byte limit into independent BCPLAPT's `APLIMIT` data word, and publishes relocated external `APTOVEC` in global G40 (offset 160). The old BCPLMAIN local APTOVEC instruction body and APMAXN datum were removed. BCPLAPT's separately assembled `asm/bcplapt.asm` and its `EXTRN STKOVFL` remain unchanged. BCPLMAIN retains `ENTRY STKOVFL`. The former local APTOVEC was **not proof** of independent execution; a successful link edit alone does not close this gate.

This is an internal service implementation change, not a BCPL-facing G40 ABI change. `APLIMIT` is an exported **data symbol**, initialized before START; it is not a BCPL-callable global. The independent implementation uses its own R10 base, saves the caller R10 in the frame, and transfers overflow to exported STKOVFL. Its static APMAXN remains 16380.

**Caution:** `tools/checks/externalize-bcplapt.py` was an earlier disposable-source transformation, and expects the **old** BCPLMAIN local implementation. Do not run it on the newly integrated canonical source. Its earlier replacement also tried to duplicate `ENTRY STKOVFL`, which was already present. Canonical source is now the authoritative integration.

## Candidate build and validation sequence

No resident MVS writes were performed by this Git source change. Operator must explicitly synchronize only `asm/bcplmain.asm` to `HERC02.BCPL.SOURCE(BCPLMAIN)` through the established DSPAL text-member procedure, with readback verification. Follow `packaging/m1-8-reproducible-runtime.md` Gate C rules: inventory `tools/dspal ls SOURCE`, replace only member BCPLMAIN (selective `dspal rm`, `dspal compress SOURCE`, `dspal put SOURCE BCPLMAIN asm/bcplmain.asm`), readback and CP037/FB80 normalization comparison. Rebuild **only** DEVOBJ(BCPLMAIN) using existing resident `JCL(BLDDEVN)` or `jcl/build-dev-bcplmain.jcl`; confirm assembler RC=0000 and install RC=0000. Confirm `DEVOBJ(BCPLAPT)` remains independently assembled and present. Do not alter stable `HERC02.BCPL.OBJ` or rerun compiler bootstrap.

Then execute:

```bash
git pull --ff-only
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ tools/run-native-regression 91 --show-output
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ tools/run-native-regression 92 --show-output
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ tools/run-native-regression 93 --show-output
```

These checks validate nested APTOVEC calls and overflow against the installed candidate library. **Additional mandatory structural evidence:** review assembler external-symbol/reference records and link-edit map (or equivalent executable address trace) demonstrating that G40's relocated address resolves to independent DEVOBJ(BCPLAPT), not an internal BCPLMAIN duplicate. Link-editor member inclusion is insufficient on its own. Confirm APLIMIT is nonzero and matches initialized STKLIM in the executing image, by focused probe or suitable object/runtime evidence. Record job IDs, assembler/link-edit CCs, output and expected results. Any build/link failure or regression mismatch keeps Gate B open.

After targeted acceptance, Gate C reviews BCPLMEM and BCPLBYTE; full 124-test DEVOBJ panel remains Gate F acceptance.

## Disposition

- Source integration: **committed**, `c8de75de98dd615823223decfff382a7f03e148b`.
- No new MVS execution or new regression results were observed here.
- Gate B: **PENDING acceptance**, until readback, DEVOBJ assembly, independent-dispatch proof and regressions 091–093 pass.
- No production OBJ promotion is authorized.
