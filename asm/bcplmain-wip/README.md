# BCPLMAIN modularization — first checkpoint

Status: **source staging only**, not separately assembled or link-edited object modules.

## Boundary decision

Keep the compiler-visible entry point **BCPLMAIN**, the single CSECT,
global-vector conventions, and all generated-code linkage unchanged while
modularization is validated. The historical runtime may eventually be
multi-member (`BCPLMAIN`, `$LOAD$`, `$BLOCK$`, `$TPUT$`, `$IOS$`);
those contracts are not sufficiently recovered to split object modules yet.

Four ordered fragments are staged under `asm/bcplmain-wip/`:

| File | Current content |
| --- | --- |
| `00-contract.asmfrag` | Historical responsibility contract, provenance, public ABI notes |
| `10-bootstrap-and-system.asmfrag` | BCPLMAIN entry, startup, system vector, termination, stack, APTOVEC |
| `20-streams-and-services.asmfrag` | Stream operations, WRITEF bootstrap, byte and vector services, diagnostics |
| `30-control-data-and-end.asmfrag` | Static controls, DCBs, buffers, final assembler END |

The parts are **ordered lexical fragments of one assembler translation unit**.
They are not independently assembled CSECTs, cannot be used directly as
link-edit input, and should not be called finished component boundaries.
Data and code cross-reference each other extensively. In particular,
BLIB remains a separately compiled/linked BCPL object, and LIBHDR
remains an interface definition, not implementation.

## Non-regression gate

The split was established from the existing `asm/bcplmain-wip.asm`
without source edits. The four fragment contents were concatenated
during preparation and independently compared to the source string:
**63,153 bytes identical**.

To reproduce on the development host:

```sh
python3 tools/checks/check-bcplmain-modules.py
python3 tools/checks/check-bcplmain-modules.py --output workarea/bcplmain-modular-rebuilt.asm
cmp asm/bcplmain-wip.asm workarea/bcplmain-modular-rebuilt.asm
```

The check fails closed on **any** differing byte. Neither it nor the
`--output` option changes the baseline source. All pre-existing native
regression tools continue consuming `asm/bcplmain-wip.asm` and
therefore retain their previously accepted behavior.

## Next gated change

After the operator reports the check passing, change the native assembly
preparation path to consume a generated, independently compared modular
source, first on a disposable regression and then on the full panel.
Only after that should we extract independently assembled CSECT/object
members or change MVS PDS linkage, subject to module ABI evidence.

The historically described library division is a goal to investigate,
not grounds for inventing new calling conventions.

## Checkpoint 2 — opt-in native regression build source

`native-compiler/regression/run-test.sh` now supports `BCPLMAIN_MODULAR_SOURCE=1`.
It reconstructs the assembler into the individual regression work directory,
checks the fragments against the monolith byte-for-byte, then supplies the
reconstructed file to **all three** existing runtime assembly preparation
paths: ordinary regression, external native-global regression, and separately
compiled BCPL library regression. No assembler, linker, or JCL semantics
are otherwise changed. Default `BCPLMAIN_MODULAR_SOURCE=0` retains the
original monolithic file. Invalid values fail closed.

Targeted validation to perform on the running TK5 host:

```sh
bash -n native-compiler/regression/run-test.sh
BCPLMAIN_MODULAR_SOURCE=1 tools/run-native-regression 114 --show-output
cmp asm/bcplmain-wip.asm workarea/native-regression/114-interleaved-stream-records/bcplmain-modular.asm
```

If this passes, test a linked-BLIB regression with the opt-in mode
before proposing any default switch or full-panel rerun. **Checkpoint 2
is committed but not yet validated under MVS.**

## Checkpoint 3 — first independent assembler CSECT (candidate)

`asm/bcplbyte.asm` defines **BCPLBYTE CSECT**, exporting entry
symbols **GETBYTE** and **PUTBYTE**. These are the original seven-
and six-instruction machine-service implementations from the current
BCPLMAIN, without changes. They have no internal static-state references
or external macros. Their BCPL caller linkage is preserved (R5 frame,
R6 return, R7/R8/R9 args, R4 restored from workspace).

`tools/checks/check-bcplbyte-extraction.py` compares both extracted
instruction sequences against the monolithic implementation and verifies
the CSECT/ENTRY/END declarations. Run:

```sh
python3 tools/checks/check-bcplbyte-extraction.py
```

**Status:** independently assemblable candidate source created; not yet
assembled on TK5, resolved from a second object by the linkage editor,
or installed in the native runtime global vector as an external entry.
In particular, BCPLMAIN still contains its original copies of these
routines, and **the standard 120 native regression tests continue using
only those copies**. We do not substitute exported entry addresses or
edit runtime globals until two-object assembler/linkage acceptance.

Next gated experiment: assemble BCPLBYTE as its own object; check IFOX
external symbol visibility for GETBYTE/PUTBYTE; link with a small
caller module that actually calls both entry points. Only then replace
the internal runtime routines with external addresses under an opt-in
build and run targeted GETBYTE/PUTBYTE regressions followed by the
full suite.

## Checkpoint 4 — isolated two-object MVS linkage job prepared

The standalone `tools/checks/bcplbyte-linkage-caller.asm` provides
**BCBYTEST**: an independent MVS entry program that declares
`EXTRN GETBYTE,PUTBYTE` and calls both external symbols through IFOX/IEWL.
It verifies GETBYTE returns EBCDIC B (194), PUTBYTE changes the same
buffer byte to EBCDIC Z (233), and GETBYTE returns the changed byte.
GO exits RC=0000 for success and RC=0008 for a mismatch.

Reuse the existing proven two-object JCL generator; no changes to
the regression runner are necessary:

```sh
python3 native-compiler/regression/make-two-object-job.py \
  tools/checks/bcplbyte-linkage-caller.asm \
  asm/bcplbyte.asm \
  workarea/bcplbyte-linkage.jcl \
  --entry BCBYTEST --job-name BCBYTE1
bash tools/submit-jcl workarea/bcplbyte-linkage.jcl
tools/job-summary JOBNUMBER
```

Expected: `ASMBCPL=0000`, `ASMNAT=0000`, `LKED=0000`,
`GO=0000`. The independent ASM object and linking of both external
entry symbols must be confirmed from the link-edit listing if the
report is examined. Assembly or link-edit failure is not acceptance.

This probe does not alter the current BCPLMAIN, its G85/G86
installation, or any regression. **Pending actual operator MVS run.**

## Checkpoint 4 accepted — JOB 5515 (2026-10-10)

Operator submitted the isolated `BCBYTE1` two-object test, returned as **JOB 5515**. `tools/job-summary 5515` reports ASMBCPL IFOX00 RC=0000, ASMNAT IFOX00 RC=0000, LKED IEWL RC=0000, GO RC=0000, overall SUCCESS, and no flagged assembler statements. The external caller checks original GETBYTE, PUTBYTE modification, and GETBYTE readback. This **accepts independent BCPLBYTE assembly/link/execution**; it does not yet validate installing G85/G86 via external object addresses in BCPLMAIN. Next change must be opt-in and preserve the default 120-test baseline.

## Checkpoint 5 — opt-in BCPLMAIN-to-BCPLBYTE object integration

Added `tools/checks/prepare-bcplbyte-runtime-probe.py` to create a
**separate**, two-object MVS job from the existing generated native
regression 114 assembler. The preparation script:

- Requires exactly one BCPLMAIN CSECT, and exactly one G85/G86
  installation site each; fails closed if the expected source differs.
- Declares `EXTRN GETBYTE,PUTBYTE` in the BCPLMAIN assembler unit,
  replaces the internal `LA` address installations with
  `L 1,=A(GETBYTE)` / `L 1,=A(PUTBYTE)` (external relocations).
- Removes the two internal routine definitions from the copied source;
  leaves all other BCPLMAIN code in the independent assembler unit.
- Uses the established two-object IFOX/IEWL JCL generator to assemble
  `asm/bcplbyte.asm` independently and include it in the same load
  module; restores regression 114's alternate output DD.
- **Never edits** `asm/bcplmain-wip.asm`, existing regression 114
  source, or the standard regression runner.

On a host with the regression 114 generated source already present:

```sh
python3 tools/checks/prepare-bcplbyte-runtime-probe.py
bash tools/submit-jcl \
  workarea/native-regression/114-interleaved-stream-records/byte-object-probe/byte-object-probe.jcl
tools/job-summary JOBNUMBER
```

Accept only `ASMBCPL`, `ASMNAT`, `LKED`, and `GO` all RC=0000,
then verify the GO stream output remains SYSPRINT `AB`, `C` and
BCPALT `1`, `2`. A successful GO RC alone does not prove G85/G86
were exercised; regression 114 primarily exercises output streams.
A subsequent targeted native BCPL GETBYTE/PUTBYTE regression must be
tested against this externalized runtime before generalization.

**Status:** preparation committed; TK5 integration job not yet run.

## Checkpoint 5 MVS job result — JOB 5516 (2026-10-10)

Operator ran the opt-in `BY114R` two-object integration probe as **JOB 5516**. `tools/job-summary 5516` returned ASMBCPL IFOX00 RC=0000, ASMNAT IFOX00 RC=0000, LKED IEWL RC=0000, and GO RC=0000; no flagged assembler statements. This accepts assembling and linking the externalized BCPLMAIN G85/G86 installation against the independently assembled BCPLBYTE object, and successful execution of regression 114's program. Because regression 114 does not actually call G85/G86, **behavioral acceptance is still pending**: use a real byte-operation BCPL regression with this externalized runtime. SYSOUT contents were not independently rechecked in this run. Default build remains unchanged.
