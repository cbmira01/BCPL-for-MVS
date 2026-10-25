# BCPLQSAM — Q.1 source-controlled candidate

**Status (25 October 2026): Q.1 — Linkage & OPEN/CLOSE skeleton,
UNACCEPTED candidate.** The separately approved Q.0 gate and four Q.1
implementation decisions permit source work, not MVS deployment or march
closure. Actual IFOX, IEWL, native BCPL, JES/QSAM, and REGION=256K
execution are **not yet verified**.

## Scope and files

- `bcplqsam.asm`: **one** relocatable assembly object, with BCEX v1
  `QSMDESC` (`QSMBEG/QSMEND`), G!200 `QSMDISP`, private handle/DCB
  machinery, and generic `QSMFIN` finalizer. Separate internal CSECTs
  do not constitute separately selected packages.
- `bcplqsam.h`: BCPL G!200 declaration and public manifest. Including
  the header does **not** install or register the package.
- `q1-catalog.asm` + `q1-selection.asm`: **temporary source-mode**
  `BCXCAT` overlay and `BCXREQ BCPLQSAM`, using temporary `QSMOBJ`.
  Never replace the installed production `BCXCAT` member.
- `test-q1-{3dd,output,negative,finish,stop}.bcpl`: proposed native
  callers, not observed execution evidence.
- `check-q1-offline.py`: local source/card/shape checks, not assembly.

## Q.1 behavior

`QSAMSVC(op,request,result)` follows the accepted native R7/R8/R9 ABI.
QUERY returns six format-1 words, API **1.0**, supported-opcode bitmap
**`X'00000019'`** (OPEN=1, CLOSE=4, INFO=5), and capability flags **0**.
READ=2 and WRITE=3 return `QS_ERR_OPCODE=-2`. Ordinary requests have
four BCPL words and results eight; unused result words are zero.

OPEN validates DDNAME spelling, mode and reserved words, reserves one
of **16 slots**, checks DD/JFCB via non-opening RDJFCB and geometry,
opens the selected per-slot DCB, checks effective geometry and allocates
an independently owned checked **1024-byte** stage. Only a fully
acquired handle is published. Positive IDs never recycle, even after
slot reuse. Slots hold per-mode pristine DCB snapshots, restored before
subsequent OPEN. F/FB support effective LRECL 1..1024; V/VB 4..1024
including four RDW bytes. INFO reports enum, LRECL, BLKSIZE and effective
maximum **application data bytes** (F/FB LRECL, V/VB LRECL minus 4).

CLOSE on verified success releases stage and retires ID. On a returned
CLOSE failure it quarantines the occupied slot, without blind retry or
unsafe freeing. The generic R.0 finalizer closes independently held live
DCBs and signals failure for remaining uncertain ownership. BCPLREG is
responsible for ordinary FINISH RC=8 upon returned finalizer error and
preservation of explicit STOP(n). Unrecovered MVS abends are outside the
returned-error guarantee.

**Separate owner gate remains:** exceptional returned-CLOSE test
methodology and cleanup-error precedence. The candidate currently
preserves the original OPEN/stage error during rollback and retains
uncertain ownership if rollback CLOSE fails. This provisional precedence
must not be treated as approved or MVS-validated.

## Local checks and proposed MVS acceptance campaign

From the repository root, using Python only:

```sh
python3 -m py_compile \
  bootstrap-toolchain/extensions/bcplqsam/check-q1-offline.py
python3 bootstrap-toolchain/extensions/bcplqsam/check-q1-offline.py
```

Proposed MVS checks (not authorized or performed by these files): IFOX
assembly, IEWL descriptor/registration MAP and relocation, QUERY
boundary/sentinel results, three independent DDs, output OPEN/INFO/CLOSE,
invalid/missing DDs, 16 simultaneous F1024 input DDs, 17th refusal,
slot reuse/stale handles, transactional rollback, FINISH and STOP(8)
finalizers, and the accepted 00–162 regression panel (162 PASS, 0 FAIL,
one expected SKIP 083). First run the **full native BCPL 16-handle
application at REGION=256K**; higher-region execution needs explicit
owner gate review. Use temporary input DDs and temporary object decks
only. Do not submit jobs or write permanent MVS PDS members without
separate authorization.

The dispatcher source uses DCB offsets grounded in accepted BCPLIO/Q.0
probes. OPEN/CLOSE macro forms, the DCB snapshot length, actual macro
return-code semantics and post-OPEN pointer checks still require IFOX
and MVS validation. Offline source checks cannot prove those behaviors.

## Authorities

- `packaging/milestone-qsam.md`
- `packaging/bcplqsam-public-interface.md`
- `packaging/qsam-q0-staging-resource-design-decision.md`
- `packaging/qsam-q0-error-and-r0-design-decisions-20261020.md`
- `packaging/runtime-extensions-r0-owner-abi-decisions.md`
- `packaging/runtime-extensions-r0-query-abi-decision-20261021.md`
- Accepted `bootstrap-toolchain/asm/bcplrgs.asm`, `bcplio.asm` and
  `bootstrap-toolchain/extensions/bcpltime/bcpltime.asm`.

This candidate is not a Q.1 closure or approval of permanent object
installation, native regression changes, record I/O, or Q.2.
