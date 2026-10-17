# BCPLIO dynamic streams — M4.1 deterministic allocation failures

**Status: M4.1 CLOSED — source-only checker PASS and focused MVS 135/136/137 individually PASS; full regression panel intentionally deferred.**
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

## First M4.1 runtime acceptance — regression 135

The operator pulled repository changes through `175fc2e` and
ran `python3 tools/checks/check-bcplio-m41-fault.py`.
Output included separate PASS checks for descriptor32,
buffer268, and handle16, followed by `M4.1 source-only checks:
PASS (MVS execution NOT attempted)`. This is static validation
of generator anchors, generated source structure and card width;
it is not MVS execution evidence for 136 or 137.

The operator next executed the single DEVOBJ-isolated
`tools/native/run-regression 135 --show-output` case with
the four standard BCPL_RUNTIME candidate variables, yielding:

```text
NATIVE REGRESSION  135..135  (1 tests)
RUN   135  135-dynamic-dd-fault-descriptor32
PASS  135  135-dynamic-dd-fault-descriptor32

NATIVE REGRESSION COMPLETE
PASS  1
FAIL  0
SKIP  0
TOTAL 1
```

**ACCEPTED:** controlled second descriptor32 GETMAIN-site
failure, zero return to BCPL, preservation of already-selected
DD01 input and record cursor, and successful retry to open DD02.
The isolated ASMFIO/object-link strategy did not require
an installed PDS object change. The provided operator output
does not identify JES job number or independently enumerate
step return codes; record only the runner's PASS.

**Remaining M4.1 gates:** 136 (268-byte QSAM buffer/DCB
allocation failure) and 137 (16-byte stable handle failure
after OPEN), each to run individually using unchanged isolation.
Successful BCPL-level behavior will still not replace
M4.3 instrumented GETMAIN/FREEMAIN and OPEN/CLOSE accounting.
The owner's deferral of the complete 00..134 panel remains
in effect; no replacement full panel has been run.

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 136 --show-output
```

## Second M4.1 runtime acceptance — regression 136

After pulling Git main through `831ee82` (starting from
`175fc2e`), the operator ran targeted DEVOBJ-isolated regression
`136-dynamic-dd-fault-buffer268` with the same four
`BCPL_RUNTIME_*` candidate variables and observed:

```text
NATIVE REGRESSION  136..136  (1 tests)
RUN   136  136-dynamic-dd-fault-buffer268
PASS  136  136-dynamic-dd-fault-buffer268

NATIVE REGRESSION COMPLETE
PASS  1
FAIL  0
SKIP  0
TOTAL 1
```

**ACCEPTED:** synthetic failure of the second 268-byte
`DALLOC` QSAM DCB/buffer GETMAIN site, zero-valued FINDINPUT
failure without perturbing a live DD01 stream/cursor, and
successful subsequent DD02 FIND, reading and closure.
The canonical `DALNOMEM` path calls FREEMAIN for its earlier
32-byte descriptor. This test exercises observable recovery
consistent with that path, but **does not provide separately
instrumented FREEMAIN call counts**; exact reclamation and
OPEN/CLOSE counts remain M4.3 responsibilities. Genuine host
allocation exhaustion is not implied. The operator excerpt
has no JES job ID or individual step CCs.

**M4.1 focused gates:** 135 PASS; 136 PASS; 137 not yet run.
The explicitly deferred full panel stays deferred. The next
individual test is 137, which fails the 16-byte HNEW handle
allocation **after successful QSAM OPEN**, exercising the
DQCLOSE/DREL cleanup sequence:

```sh
cd ~/Source/Repos/BCPL-for-MVS
git pull --ff-only
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 137 --show-output
```

## M4.1 completion gate — regression 137 ACCEPTED

The operator pulled `main` from `831ee82` to `ccb0f1b`
and ran the **single** candidate-only compiled BCPL regression
`137-dynamic-dd-fault-handle16`, with the four standard DEVOBJ/
BCPLM6 candidate variables. The console reported:

```text
NATIVE REGRESSION  137..137  (1 tests)
RUN   137  137-dynamic-dd-fault-handle16
PASS  137  137-dynamic-dd-fault-handle16

NATIVE REGRESSION COMPLETE
PASS  1
FAIL  0
SKIP  0
TOTAL 1
```

**ACCEPTED:** after the first genuine HNEW handle allocation
succeeds, the isolated test-only BCPLIO forces a synthetic
failure of the second `GETMAIN RC,LV=16` following
successful DD02 OPEN. The failed FIND returns zero, leaves
DD01 selected with its cursor unchanged, and permits a
subsequent successful DD02 FIND and use/close of both streams.
Canonical source control flow takes `DIFCLOSE` →
`DQCLOSE` → `DIFCLEAN` → `DREL`. This is consistent with
proper recovery, but the test does **not** independently
observe/count the QSAM CLOSE or FREEMAIN calls.

### M4.1 close decision

**M4.1 CLOSED for deterministic synthetic GETMAIN failure-path
behavior**, with targeted MVS PASS **135** (32-byte descriptor),
**136** (268-byte QSAM/DCB region), and **137** (16-byte
stable handle). All were separate single-case runs with
**1 PASS, 0 FAIL, 0 SKIP** each, not a contiguous panel.
The host-side generator-checker also passed for all three modes.

Not proved by M4.1: genuine low-storage exhaustion, independent
OPEN/CLOSE or GETMAIN/FREEMAIN counts, or actual QSAM OPEN
failure recovery. These remain M4.2/M4.3 tasks. The owner
explicitly deferred a full regression run; the last accepted
complete panel remains **00..132, 132 PASS/0 FAIL/1 SKIP 083**.
The test source is rebuildable and disposable workarea
products may be deleted. **No DEVOBJ or production OBJ PDS
modification or object promotion occurred.**

The next march is **M4.2**: characterize what MVS 3.8 does
for allocated DDs with incompatible QSAM OPEN requirements,
using a controlled development-only probe and exact JES
evidence before promising graceful BCPL failure semantics.
