# M2.0 Gate B — Independent BCPLAPT G40 Integration

**Status: ACCEPTED — Gate B closed** (MVS execution evidence 14 October 2026).

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

## Acceptance evidence — 14 October 2026

- Operator synchronized only `SOURCE(BCPLMAIN)`: removal JOB 1259, compression JOB 1260, put JOB 1261, readback JOB 1263. Readback inspection confirmed `EXTRN APTOVEC,APLIMIT` and `=A(APLIMIT)` / `=A(APTOVEC)` references. Byte-for-byte normalized readback equivalence was not separately reported; this evidence establishes required symbols in resident input.
- Rebuilt `DEVOBJ(BCPLMAIN)` with `JCL(BLDDEVN)` launcher JOB 1265 and payload **JOB 1266**: ASMMMAIN IFOX00 RC=0000, PUTMAIN IEBGENER RC=0000, zero flagged assembler statements/severity. BCPLMAIN assembly ESD shows independent ER entries `APTOVEC` and `APLIMIT`; BCPLMAIN SD length X'15A8'. DEVOBJ inventory retains BCPLAPT, BCPLBYTE, BCPLMAIN, BCPLMEM, BLIB.
- Focused installed DEVOBJ regressions **091, 092, 093: 3 PASS, 0 FAIL, 0 SKIP**; run reports JOBs **1269, 1271, 1273**, all with ASMAP IFOX00 RC=0000, LKED IEWL RC=0000, GO RC=0000.
- All three link-edit maps explicitly `INCLUDE OBJ(BCPLAPT)` and show a **separate BCPLAPT CSECT of X'6C' bytes**. Their ENTRY table locates APTOVEC and APLIMIT within BCPLAPT, not BCPLMAIN: JOB 1269 APTOVEC X'16B0', APLIMIT X'1718'; JOB 1271 X'16C8'/X'1730'; JOB 1273 X'1670'/X'16D8'. Cross-reference entries associate both referenced symbols with BCPLAPT. `STKOVFL` is resolved from BCPLMAIN. This establishes the independently linked G40 service and overflow linkage. The code sequence initializing APLIMIT from STKLIM is present in the assembled listing (L APLIMIT; L STKLIM; ST limit; L APTOVEC; ST G40) and tests 091–093 exercise its behavior. There was no direct storage dump of APLIMIT; it is not required beyond the combination of assembled instructions, linkage map, and executable overflow regression.
- **Gate B ACCEPTED**: separately assembled BCPLAPT provides G40 and shares the canonical stack limit; old local implementation is gone. Gate C is next. Full regression panel remains reserved for Gate F. **No production OBJ promotion is authorized or claimed.**
