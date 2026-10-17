# Dynamic BCPLIO streams — M2 input multiplicity progress

Status: **M2 test 130 staged; not yet MVS executed or accepted**
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

**Status: STAGED, NOT EXECUTED, NOT ACCEPTED.** The fixture uses
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
