# TA.4 — Automatic MR10 semantic acceptance decision

Project: BCPL for MVS 3.8 Reconstruction
Milestone: Tape artifact release
March: TA.4 — MR10 Kit Compiler Distribution and Verification
Owner decision: Approved 23 November 2026
Status: Implemented and locally tested; actual evidence review pending.

## Superseding acceptance contract

The owner explicitly removes the requirement to make individual human
PASS/FAIL decisions or provide a SIGN token for twelve MRREGRES tests.
This supersedes the 16 November manual-verification decision only in
that respect. Retain TEST:, literal EXP:, computed RP:, interpreted
CODE=0, independent .expected golden records and 12-case MVS coverage.

Pass only if the source-controlled comparator verifies all twelve
ordered cases from the sealed actual MVS JOB 9369 against the pinned
goldens. It must reject mismatched, missing, extra or reordered output,
nonzero interpreted codes, job failures, manifest/source discrepancies,
missing or changed evidence seals, and media checksum mismatches.

Recheck the sealed RC4 TA.4 interpreter rebuild, SCALVEC and all
11 language plus 17 BCPL demos from actual JOBS 9418–9422.
Do not rerun those jobs. Original evidence has a historical
human_signoff PENDING field; this does not block automated acceptance.

## Read-only implementation

Run packaging/distribution/install-from-tape/scripts/
ta4-mr10-automatic-acceptance without arguments or prompts.
It reuses the established historical sealed-evidence verification
and records twelve separate machine-derived PASS verdicts plus the
five accepted TA.4 MVS job identities in acceptance.json. Output
is separately sealed under workarea/ta4-mr10-automatic-acceptance.
No tape, MVS, JES, source, original evidence or PDS changes occur.
The prior ta2-rc3-human-review command is retired from acceptance
workflow; its existing accepted() validation remains a dependency.

Implementation tested with six local isolated positive and refusal
tests, including case omissions, semantic mismatch, nonzero CODE,
modified RC4 receipt and refusal of a human-signature argument.
Actual private saved evidence was not inspected in that test.

## Closure and separation

TA.4 may close after actual automatic acceptance and required WSL
regression evidence are confirmed. TA.5/TA.7/TA.8 and publication
have independent gates. TA.6 is N/A with native_compiler absent.
