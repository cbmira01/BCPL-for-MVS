# Dynamic BCPLIO streams — M2 input multiplicity progress

Status: **M2 16-concurrent-stream target ACCEPTED; DD close/reopen identity not yet validated**
Project: BCPL for MVS 3.8 reconstruction
Parent: [Milestone - BCPLIO dynamic stream](Milestone-BCPLIO-dynamic-stream.md)

## Incoming candidate and accepted baseline (MVS 2026-10-17)

The M1 development candidate is BCPLM6 + BCPLIO in
`HERC02.BCPL.NATIVE.DEVOBJ`, with the current BCPLIO source from
commit `8597a8874f081503489863a90524f4acce59f966`.
BCPLIO source staging JOB **7062**, BLDDEVI launcher **7064** and
payload **7065** reported IFOX ASMIO RC0000, IEBGENER PUTIO RC0000,
zero flagged statements. The operator then ran the complete
`tools/native/run-regression` DEVOBJ panel `00..129`:
**129 PASS, 0 FAIL, 1 expected SKIP 083**. Includes
dynamic two-input case 125, twelve-input case 126, duplicate FIND
case 127, dynamic output 124 and FINISH/STOP cleanup 128/129.

These are accepted results *before* the next test. Production OBJ
remains untouched. The user log provides the build job numbers
and regression summary; no per-test successful GO job IDs
were supplied.

## M2 contract

The parent milestone specifies independent input record cursors,
newline/EOF, per-stream UNRDCH, ENDREAD/reopen, and at least
**thirteen simultaneous ordinary input DD streams** to distinguish
dynamic registries from a twelve-slot scheme. M1 already validated
most behaviors with 125/126. Remaining M2 acceptance requires
the beyond-twelve concurrency threshold plus a separate
reopen-after-close identity/lifecycle test.

## Permanent regression 130 — 16 simultaneous DDs

Location:
`native-compiler/regression/130-dynamic-dd-sixteen-input-streams/`

**Status: FIRST ATTEMPT FAILED BEFORE NATIVE GO; compact retry staged.** The fixture uses
16 different `input-dd*.records` for `DD01..DD16`; all sixteen
are opened *before* any read or close. It asserts 16 nonzero
and 120 pairwise-distinct opaque handles. It interleaves two
one-character FB80 records per DD, verifies independent newline
and EOF, UNRDCH on a character and EOF, and ENDREADs in reverse
order while rejecting stale handles. Completion marker is
`BCPL SIXTEEN INPUT OK`, GO RC0000. Assertions fail with STOP(8).
The existing JCL preparation supports up to 36 dynamic input DD
fixtures; no runner or runtime change was needed to stage this test.

Run from the repository root with:
```sh
git pull --ff-only
export BCPL_RUNTIME_PDS=1
export BCPL_RUNTIME_LIBRARY=DEVOBJ
export BCPL_RUNTIME_CANDIDATE=1
export BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6
tools/native/run-regression 130 --show-output
```

Pass requires Cambridge compilation, IFOX/IEWL RC0000, GO
RC0000, expected exact logical record, and `PASS 130`.
If the job fails, diagnose the first failed gate; do not weaken
the fixture or claim unlimited capacity. The test does **not**
prove QSAM error-path cleanup, GETMAIN accounting, or physical
DD output attribution.

## First MVS execution — compiler CODE extraction failure

The operator pulled all test 130 files through `ba3ca23` and ran
`tools/native/run-regression 130 --show-output` using the DEVOBJ
candidate variables. Resident Cambridge compile JOB **7328 RG130C**
reported:

```text
COMP    ICINT19    RC=0000
SVCODE  IEBGENER  RC=0012
```

The compiler driver therefore exited with rc=2 and did not recover
`workarea/130-dynamic-dd-sixteen-input-streams.s370.asm` into
the native build workflow. There was **no regression-130 native
application assembly, link, or GO**, and no evidence of QSAM runtime
capacity failure. The first version of the BCPL source contained
438 lines and unrolled 120 pairwise handle comparisons as well as
three independent read rounds. The IEBGENER step concatenates
the Cambridge compiler's temporary `&&CODE` dataset between
literal begin/end SYSOUT markers, so SVCODE RC12 could reflect
a CODE dataset/read failure or a compiler-side production issue.
The step summary alone does **not** establish the root cause;
the complete JOB 7328 spool diagnostics are necessary for
a definitive explanation.

**Source-only test-refactoring commit `ded524f`:** replaced
the repetitious unrolled checks with `FOR` loops and BCPL VEC
indexing already exercised by regressions 23 and 10. Source is now
121 content lines, opening the same 16 DDs before the first read,
and testing 120 distinct handle pairs through a nested `FOR`.
All sixteen first/second record fixture checks, newline and EOF
assertions, UNRDCH, reverse-order ENDREAD, stale-handle rejection,
and expected `BCPL SIXTEEN INPUT OK` remain. All DD and output
fixtures unchanged. No compiler, BCPLIO, or regression-harness code
changed. **This revision has not yet been tested on MVS.**

Retry from the repository root with:

```sh
git pull --ff-only
export BCPL_RUNTIME_PDS=1
export BCPL_RUNTIME_LIBRARY=DEVOBJ
export BCPL_RUNTIME_CANDIDATE=1
export BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6
tools/native/run-regression 130 --show-output
```

If SVCODE again reports RC12, capture
`tools/mvs/dump-report-for-job 7328` for historical investigation
and the newly reported Cambridge JOB number for current diagnosis.
Look for IEBGENER messages, IEC/IEF system diagnostics, and
Cambridge `EXECUTION CYCLES` / `CODE` status. Do not further
reduce test coverage or change BCPLIO without observing the
actual failure cause.

## Remaining work

After the 16-stream threshold, stage a separate permanent compiled-
BCPL case testing ENDREAD/ENDWRITE, fresh FIND of the *same*
normalized DD after close, distinct new handle identity, stale
handle rejection even after reopening, and correct stream selection.
Assess MVS-specific constraints for reopening instream DD DATA
before making assertions; output SYSOUT may be a safer first
reopen candidate. Also retain an explicit M4 gate for graceful
OPEN failure, deterministic GETMAIN exhaustion, and instrumented
FREEMAIN/CLOSE accounting. DD-specific lossless extraction belongs
to M5 and cannot be inferred from the current combined JES report.

This document records project progress, not approval to promote
DEVOBJ into production OBJ.

## Regression 130 accepted — sixteen concurrent inputs (MVS 2026-10-17)

After compact-source test commit `ded524fec36ec741735f7c813d40724fce20a162` and related documentation through `8247e98`, operator pulled from `ba3ca23` to `8247e98` and reran the **unchanged DEVOBJ(BCPLM6 + BCPLIO)** candidate with `BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6`. Result:

```text
NATIVE REGRESSION 130..130 (1 tests)
RUN 130 130-dynamic-dd-sixteen-input-streams
PASS 130 130-dynamic-dd-sixteen-input-streams
PASS 1 FAIL 0 SKIP 0 TOTAL 1
```

The compiled BCPL test opened **16 independent DD01..DD16 inputs simultaneously**, asserted 16 nonzero pairwise-distinct opaque handles (nested FOR covering 120 pairs), interleaved two records per stream, checked synthetic newline, repeated EOF and UNRDCH, then ENDREADed in reverse order and rejected stale selection. **ACCEPTED: 16-stream concurrency threshold.** The previous original 438-line source failed JOB 7328 SVCODE IEBGENER RC0012, before native execution; compact 121-line source passed. That first transport failure remains unexplained by the available step summary and must not be called proof of a compiler source-length limit. No compiler, BCPLIO, DCB/runtime or harness modification was required for the passing test.

**Decision:** concurrency stress testing stops at **16**, as agreed with the owner. Dynamic linked descriptors have no intentionally fixed 16-slot ceiling, but no guarantee of arbitrary concurrency in resource-limited MVS follows from this test. Last independently accepted full panel remains **00..129: 129 PASS, 0 FAIL, expected SKIP 083**; 130 is an additional passing targeted case. A full 00..130 panel remains pending.

Next work: close/reopen the **same DD** after `ENDWRITE` first (QSAM SYSOUT), require a **fresh nonrecycled BCPL word handle**, old handle still rejected after reallocation and duplicate active FIND of that new handle returns the new identity. Do not presume input DD DATA can rewind on QSAM reopening; investigate separately.
