# BCPLIO dynamic streams — M4.1 deterministic allocation failures

**Status: IMPLEMENTED AS TEST-ONLY HARNESS AND STAGED CASES 135–137; no MVS execution yet.**
Date: 2026-10-17
Parent: [Milestone - BCPLIO dynamic stream](Milestone-BCPLIO-dynamic-stream.md)
Predecessor: M4.0 regression 134 **targeted PASS**, M3 regression 133 **targeted PASS**.

## Owner-directed scheduling decision

The owner explicitly **DEFERRED** the proposed full 00..134
compatibility checkpoint in order to proceed to M4.1. Do not
run, require, or mark that full suite as completed as an
M4.1 entry prerequisite. The most recent completed full
panel remains **00..132: 132 PASS, 0 FAIL, 1 expected
source-only SKIP 083, 133 total**. Individual tests 133 and
134 passed on the installed DEVOBJ candidate. The deferred
sweep stays a future regression gate, particularly before
any runtime object promotion or milestone closure.

## Engineering approach

M4.1 tests deterministic *error-branch recovery* of existing
BCPLIO GETMAIN call sites without exhausting actual MVS
storage. It does **not** establish actual S/370 GETMAIN failure
codes or accounting, and does not test QSAM OPEN failure.

The instrumented assembler is regenerated from the canonical
`native-compiler/asm/bcplio.asm` by:
`tools/checks/prepare-bcplio-m41-fault.py`.

The strict generator recognizes **one and only one** chosen
GETMAIN anchor in the source. It inserts a test-private
three-phase counter in the private module's storage:

- First invocation: perform the original GETMAIN normally
  (opening DD01 and maintaining a live selected stream).
- Second invocation: bypass the macro and synthesize
  `R15=8` to enter the existing nonzero-result branch.
- Third and later invocations: perform GETMAIN normally again,
  establishing post-failure recovery.

The private mode file `io-fault-mode.txt` must have one of
`descriptor32`, `buffer268`, or `handle16`. Each mode
targets exactly one GETMAIN call site, not every storage
request of that length in other runtime components.

## Build isolation and linking

Normal PDS-based test runner and JCL generator remain the
default for all unmarked tests. For marked M4.1 tests only:

1. Compile the case's BCPL source using the installed Cambridge
   compiler as usual.
2. Generate `workarea/native-regression/<case>/bcplio-m41-fault.asm`
   from the canonical BCPLIO source. The generator aborts if
   source anchors are not unique or any assembler card exceeds
   column 71.
3. The marked PDS regression JCL adds `ASMFIO` (IFOX00) to
   assemble this instrumented private source into `&&IOOBJ`.
   The JCL never issues an IEBGENER to copy this module into
   `HERC02.BCPL.NATIVE.DEVOBJ` or production `OBJ`.
4. The link uses the **existing DEVOBJ(BCPLM6)** and accepted
   BCPLBYTE/BCPLAPT and production BCPLMEM/BLIB objects;
   it **omits** `INCLUDE OBJ(BCPLIO)` and concatenates the
   temporary `&&IOOBJ` before link-edit control statements.
   Thus the test-only BCPLIO resolves BCPLM6's external calls.
5. JCL runs the resulting temporary GO module and verifies
   expected logical BCPL output. The job contains explicit
   ASMAP/ASMFIO/LKED/GO gates; an assembler warning or
   failure is not to be mistaken for evidence of injected
   execution.

Only `BCPL_RUNTIME_PDS=1`, `BCPL_RUNTIME_LIBRARY=DEVOBJ`,
`BCPL_RUNTIME_CANDIDATE=1`, and
`BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6` permit this route.
No public BCPL G slots, entry points or runtime object members
are added or changed. All generated files under `workarea/`
remain disposable and reproducible.

## Candidate test matrix

| Test | Injected site | Exact recovery obligation |
|---|---|---|
| 135 | 32-byte descriptor GETMAIN in DALLOC | Return zero without registering descriptor; leave first selected stream intact |
| 136 | 268-byte QSAM region GETMAIN in DALLOC | Release the already allocated 32-byte descriptor, return zero, recover |
| 137 | 16-byte stable handle GETMAIN in HNEW | After OPEN, close QSAM DCB and release 268+32 bytes, return zero, recover |

Each permanent compiled-BCPL case opens DD01 successfully,
reads its first character, and selects it. It then attempts
to open DD02 and demands return zero on the injected second
allocation. DD01 must remain selected, and its cursor must
resume at the correct newline and second character. A third
attempt to open DD02 must now succeed, and both handles
must remain valid and independently closable. The test
fails with STOP(8) on any assertion mismatch.

Success markers:
`BCPL FAULT 32 OK` (135),
`BCPL FAULT 268 OK` (136),
`BCPL FAULT 16 OK` (137).

A non-instrumented runtime that returns a successful
second FIND would **FAIL** the test. The expected MVS
execution steps include Cambridge COMP/SVCODE, IFOX00
ASMAP/ASMFIO, IEWL LKED and GO.

## Host-side source-only QA gate

A separate fail-closed static test can check all three
transformer modes before any JCL submission:

```sh
python3 tools/checks/check-bcplio-m41-fault.py
```

This imports the source transform and verifies unique anchors,
preservation of the number of GETMAIN sites, correct one-shot
phase storage, IFOX card-width compliance and rejection of
repeat instrumentation. It **does not** assemble or link
the object under IFOX and cannot demonstrate that the MVS
fault is exercised at runtime. No verified execution result
for this local checker has been supplied yet.

## First operator gate: 135

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 135 --show-output
```

First **inspect ASMFIO assembler errors, LKED duplicate/unresolved
symbols, and GO RC** if failure occurs. This is new test
infrastructure: a first red test need not indicate a
canonical runtime bug. Do not install the private instrumented
module, modify BCPLIO or promote any object to production in
response to an uncharacterized failure.

After accepted 135, run 136 and 137 individually and record
JES job IDs and step CCs. These three focused cases establish
branch recovery only. M4.3 still needs independent
GETMAIN/FREEMAIN and OPEN/CLOSE counters (with no production
ABI pollution); M4.2 still needs real incompatible allocated
DD / QSAM OPEN diagnostic evidence.

## Deferred checkpoint and subsequent integration

Full `00..134` remains **explicitly deferred** by owner
direction. Once ready for broad compatibility testing, the
full panel would now also include 135..137 and the
expected source-only SKIP 083. Schedule the integration
gate separately rather than implying it already passed.
Production `HERC02.BCPL.NATIVE.OBJ` stays untouched.
