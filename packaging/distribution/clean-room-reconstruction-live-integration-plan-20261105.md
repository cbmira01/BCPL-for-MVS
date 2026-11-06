# Clean-room reconstruction automation — guarded live integration

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 5 November 2026  
**Status:** IN PROGRESS — dedicated single-operator/no-lock redesign approved 6 November 2026; no live reconstruction authorized  
**Predecessor:** [Step 3 owner closure and JOB 357 evidence](clean-room-reconstruction-step3-closure-20261105.md)  
**Authority:** [Automation decision](clean-room-reconstruction-automation-decision-20261104.md), [dedicated-TK5 no-lock decision](dedicated-tk5-operator-controlled-reconstruction-decision-20261106.md), and [manual reconstruction guide](../../docs/Rebuild-BCPL-for-MVS-from-source.md).

This is the next **automation development phase**, referred to in discussion as Step 4; it does not create a milestone/march, and is **not** the manual guide's Step 4 — Test the new interpreter. The independent MR10 regressions remain outside the reconstruction orchestrator.

## Owner decisions

Use the **one existing TK5/MVS installation** only. No cloned system-state or additional TK5 instance is required. All project-managed BCPL datasets are outputs intended to be reconstructed from GitHub source. A real purge nevertheless deletes the current managed objects and must be explicitly authorized. Recreating Docker containers is not the same as restoring the persistent bind-mounted DASD images.

**Revised 6 November 2026:** No host-side or MVS dataset-based reconstruction lock is used. The single operator must keep independent submissions stopped before and throughout reconstruction, including review, approval, JES preflight, and reporting. The two-sample `$DA` safeguard remains a point-in-time observation.

## Current implementation candidate

Remove the WSL cooperative gate from `tools/reconstruction/run`, the ordinary
JES submitter, `dspal`, MR10 direct socket submission, and bootstrap children.
Keep normal standalone-tool behavior, interactive approval, managed dataset
and JCL scope checks, two-sample JES-idle refusal, and durable reports.
The former [submission-control design](clean-room-reconstruction-submission-control-design-20261105.md)
is superseded but retained for traceability. No new MVS or host lock is introduced.

## Read-only integrated live guard diagnostic

The `tools/reconstruction/run --check-live-guard` diagnostic is a separate,
non-destructive entry point using the same `observe_jes` console transport
and `require_jes_clear` classifier as the controller, without locking. It always exits without invoking reconstruction, including
when the two samples are CLEAR. It is suitable for controlled real-MVS ACTIVE
and idle observations without risking a purge if a test job finishes early.

This is a **preliminary integration observation only**: it does not exercise
the normal `--run` approval or 25-operation path against MVS, and does not
replace the remaining fully integrated-controller acceptance requirement.
Do not run `--run` to test ACTIVE refusal, because the test job might finish
between approval and the live check.

## First guarded live JES observation — 5 November 2026

The operator updated the existing WSL checkout to GitHub `main` commit
`b7cd0611d943b533e1fba49b2acf208e40dd4401`. The first
`tools/reconstruction/run --check-live-guard` run returned **RC=2**
(UNKNOWN). The read-only diagnostic
`tools/reconstruction/jes-idle --live --diagnose` likewise returned
**RC=2**, and exposed this exact five-line console delta:

```text
02:44:01 HHC00013I '/' input entered for console 0:0009: "$DA"
02:44:01 $DA
02:44:01 HHC00013I '/' input entered for console 0:0009: "$DA"
02:44:01 $DA
02:44:01 / 3.44.01           $HASP000 NO ACTIVE JOBS
```

All four echo lines conform to the previously verified identical double-pair
envelope. The fifth line differs from the previously recognized TK5
`$HASP000` idle envelope **only** by one ASCII space between the slash and
the one-digit response time. This is a parser false negative, not
evidence of an active job, and the safeguards correctly refused to
continue. The guard-only entry point did not invoke reconstruction.

The correction candidate accepts **zero or one literal ASCII space**
after the slash, never unrestricted whitespace. The full observed delta
and rejection of multiple spaces, tabs, newline substitutions,
additional JES activity and incomplete replies are independently tested.
**175 offline tests passed** (reconstruction and JES submission control).
The 6 November 2026 guard-only live retest at commit `2430efb0` returned two CLEAR samples and RC=0. Neither this nor a future CLEAR response authorizes a destructive reconstruction.

## Further live observation — 6 November 2026

First, temporary JOB 358 JESGTEST caused repeated `SubmissionDenied` results
because the submission helper still held the host lock. This did not exercise
JES ACTIVE classification. A revised test submitted JOB 359 under a short
shared admission, released it, and the read-only integrated guard observed
**ACTIVE — JOB 359 JESGTEST EXECUTING**, refusing with RC=2.

The test script subsequently retrieved an *older* JOB 359 DSPALPUT
completion report because JES reused job number 359. The after-job inquiry
still correctly reported ACTIVE. The whole test was inconclusive, but
the live ACTIVE refusal is valid evidence. It is not a completed
reconstruction or confirmed completion report for that JESGTEST job.

These tests informed the owner's simpler dedicated single-operator model.
Future reports must pair fresh START and END job records, not just job numbers.

## Remaining work before live activation

1. Remove host lock acquisition and file-descriptor handoffs from project
   tools and replace lock-specific regression tests.
2. Keep independent submissions stopped by operator procedure, with a
   fresh two-CLEAR JES check immediately before any authorized purge.
3. Review the single TK5 reader, printer, console, `dspal` configuration,
   HERC02 managed datasets, and source revision before destructive work.
4. After **separate owner authorization**, validate all 25 reconstruction
   operations and their actual JES payload evidence.
5. After any failed/interrupted attempt, allow earlier MVS writes to finish
   before restarting from zero. Keep regressions, tags, and releases separate.
6. Record evidence and request separate owner acceptance.

## Safety boundary

The proposed `tools/reconstruction/run --run` entry point is terminal-only, and **does not authorize a reconstruction by its mere existence**. Every destructive attempt requires a fresh approval of the displayed plan; pending MVS acceptance and separate owner approval, no JES submission, workarea deletion, `dspal purgebcpl`, installed dataset change, tag or release has been requested.
