# Native MVS EXEC PARM support for G39 FINDPARM — candidate implementation

**Status: SOURCE IMPLEMENTED, TK5 ASSEMBLY/LINK/EXECUTION NOT YET VERIFIED.**
2026-10-11. Baseline before these changes: 120/120 mixed-mode, 119/119
installed-object PDS acceptance. Do not attribute those older results to
this implementation.

## Behavior

* Preserve the initial MVS linkage R1 parameter-list pointer in
  `PARMLIST` at BCPLMAIN entry.
* On first G39 FINDPARM, follow R1 -> parameter list word -> pointer to
  halfword length and EBCDIC parameter bytes. Mask last-address flag in
  the parameter-list word. Limit accessible bytes to 100.
* Return an independent `PMCTRL` word-address stream handle. G11
  SELECTINPUT recognizes that handle alongside BCPIN and BCPINB.
* G13 RDCH reads PARM bytes, then one newline (10), then end-of-stream
  (-1). G15 UNRDCH and G46 ENDREAD have separate PARM stream state.
* **No required BCPIN DD** for FINDPARM. G42 FINDINPUT remains DD-backed,
  unchanged. **G45 PARMS remains uninitialized and out of scope.**
* This is MVS task-step parameter input, not a general terminal or dataset
  stream implementation.

## Verification gate

From WSL after `git pull --ff-only`:

```sh
python3 tools/checks/check-bcplmain-modules.py
BCPL_RUNTIME_PDS=0 tools/native/run-regression 108 --show-output
```

Regression 108's GO step now carries `PARM='P'` from
`bootstrap-toolchain/regression/108-findparm-stream/exec-parm.txt`,
while an independent BCPIN DD provides `X`. Expected user output
is P, demonstrating the PARM stream rather than BCPIN is selected.

**Only if 108 source-runtime succeeds:** build and install the revised
BCPLMAIN production object using
`tools/checks/prepare-runtime-object-library.py` and the established,
credential-protecting operator workflow. **CAUTION:** that generator
replaces four runtime PDS objects, is not atomic, and requires review
before submission. Then test the installed runtime:

```sh
BCPL_RUNTIME_PDS=1 tools/native/run-regression 108 --show-output
tools/native/run-regression
```

Record IFOX/IEWL/GO return codes and summary before accepting the
implementation. Re-run the installed-object 119-case acceptance if the
production PDS is updated. Do not claim acceptance before TK5 evidence.

## Risks to examine on the first TK5 run

* Availability and exact convention of the MVS entry parameter-list R1
  when invoked as `PGM=*.LKED.SYSLMOD`.
* IFOX literal/base addressing and branch reachability after adding
  new PARM stream routines.
* Whether EXEC `PARM=` data includes surrounding delimiters on this
  TK5 configuration (the regression expects only character P).
* Cleanup and subsequent FINDPARM use: the present model reuses the
  parameter stream and resets read position after ENDREAD.

All source changes are narrowly focused on G39 and regression 108;
there is no new PDS object member or interface change to BLIB.
