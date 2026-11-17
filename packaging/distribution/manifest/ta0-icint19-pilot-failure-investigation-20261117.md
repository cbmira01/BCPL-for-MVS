# TA.0 — Post-migration ICINT19 executable-use pilot failure investigation

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** TA.0 — Release Architecture, Inventory, and Manifest  
**State:** Investigation tooling, not a positive MVS execution or release acceptance result. TA.0 IN PROGRESS.

## Actual operator result — 17 November 2026

The owner ran `relocate-ta0-evidence.py` followed by the newly committed
`verify-icint19-executable.py` against the relocated evidence. The relocation
reported **168 files, 979,963 bytes**, preserved within
`workarea/ta0-mvs-evidence-20261117/`, with unchanged SHA-256 inventory. The
original `$HOME/ta0-mvs-evidence-20261117/` directory was no longer present.

The pilot reported only:

    TA.0 ICINT19 EXEC PILOT REFUSED/FAILED: ExecEvidenceError
    Private evidence retained; no automatic resubmission.

**This message does not establish a successful or unsuccessful JES submission.**
`ExecEvidenceError` is emitted both by preflight checks before directory
creation and by stricter checks after a retained MVS report has been read.
The assistant did not inspect the owner-private directory at the time of
this report. Do not assert that `TA0ICEX` ran or failed on MVS, and do not
rerun a potentially submitted job without first classifying the saved state.

## Tested, non-submitting inspection

`tools/distribution/inspect-icint19-failed-pilot.py` runs the **same read-only
source/review preflight** used by the execution pilot. It then examines only
allowlisted, ordinary files in its selected project-local `workarea/` output
directory. It cannot submit JES JCL. If a cursor is saved but the report is
absent, the state is **submission uncertain** and no automatic retry follows.
If a report and summary are both saved, it checks their job-number agreement
and runs the existing strict eight-step `ICINT19` report validator, with
interpreted `CODE=` and semantic `RP:` requirements. It prints only a stable
failure category, optional bounded JES number and current preflight result,
**never** the original report, source binary, raw printer output, JOB card,
password or private contents.

A saved report that passes these structural checks without a final pinned
receipt remains **not accepted**. The inspector neither repairs the pilot
receipt nor claims linkage, raw `RECFM=U` binary equality, source ancestry,
IEBCOPY roundtrip or tape installation. All actual claims must be reviewed
against the retained evidence and MVS result before proceeding.

The location-policy promotion also changed the error message of an existing
negative test without updating that test. This was a previously missed
**test regression**, not evidence of the real MVS failure. The test is
repaired. The original runner now exposes its read-only `validated_inputs`
preflight as one shared function for both execution and diagnosis, preventing
two divergent implementations.

**Assistant-workspace verification:** 13 isolated new inspector tests and
19 existing executable-pilot tests passed (32/32). Both tools compiled.
These tests use simulated report fixtures; JOB 9060's earlier approved
IEHLIST directory observation remains qualified, and no new `TA0ICEX`
execution has yet been verified from the actual owner-private report.

## Storage and safety

The private evidence directory is already inside the ignored repository
`workarea/` and should not be moved again. The inspector reads without
creating any output, modifying the Git working tree, or touching MVS.
`packaging/` holds only this source-controlled record; `mvs-state/` remains
Hercules runtime state. Historical unrelated `$HOME` directories must not be
moved without first checking whether they are used by live processes or
configured mounts.

## Next evidence-driven decision

Classify the retained `workarea/ta0-mvs-evidence-20261117/ta0-mr10-load-execution`
state with the inspector. A *missing output directory* means the prior pilot
did not reach the directory-creation point; a *captured cursor without a
trusted report* means a JES submission cannot be safely ruled out; a *saved
report* permits report-level failure analysis. The resulting live state,
not synthetic guesses, determines whether the next change concerns preflight,
MVS JCL, interpreted execution or strict report framing.
