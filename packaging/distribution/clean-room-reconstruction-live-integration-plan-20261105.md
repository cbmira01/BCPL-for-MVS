# Clean-room reconstruction automation — guarded live integration

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 5 November 2026  
**Status:** IN PROGRESS — offline-tested guarded live-entry candidate; no live reconstruction authorized  
**Predecessor:** [Step 3 owner closure and JOB 357 evidence](clean-room-reconstruction-step3-closure-20261105.md)  
**Authority:** [Owner-approved reconstruction automation decision](clean-room-reconstruction-automation-decision-20261104.md) and [manual reconstruction guide](../../docs/Rebuild-BCPL-for-MVS-from-source.md).

This is the next **automation development phase**, referred to in discussion as Step 4; it does not create a milestone/march, and is **not** the manual guide's Step 4 — Test the new interpreter. The independent MR10 regressions remain outside the reconstruction orchestrator.

## Owner decisions

Use the **one existing TK5/MVS installation** only. No cloned system-state or additional TK5 instance is required. All project-managed BCPL datasets are outputs intended to be reconstructed from GitHub source. A real purge nevertheless deletes the current managed objects and must be explicitly authorized. Recreating Docker containers is not the same as restoring the persistent bind-mounted DASD images.

The controller must own an **exclusive job-submission window** during the entire run: review, approval, JES-idle preflight, purge/build operations, verification, reporting and failure/interrupt cleanup. This is separate from the two-point-in-time `$DA` JES-idle safeguard.

## Current implementation candidate

The proposed cooperative admission mechanism is documented in [single-TK5 submission-control design](clean-room-reconstruction-submission-control-design-20261105.md). It uses a nonblocking Linux kernel `flock`, stored under `mvs-state/locks/`, to exclude other **integrated project submission tools**. The controller holds an exclusive descriptor; delegated project subprocesses receive it through explicit `pass_fds` handoffs. Ordinary submissions acquire shared admission until JES confirms start/rejection. The Python gate validates actual exclusive lock ownership, not just an environment variable or inode equality.

This controls `tools/mvs/submit-jcl`, its `dspal` clients (including INTERNAL READER payloads), and the direct MR10 `compile-and-run` socket path. Raw reader-port clients, direct console commands or 3270-based submissions are not blocked by this host advisory lock. **No technical guarantee of system-wide exclusivity is claimed.** Independent direct submitters must be quiescent, and stronger reader-network enforcement may be necessary before activating destructive automation.

## Read-only integrated live guard diagnostic

The `tools/reconstruction/run --check-live-guard` diagnostic is a separate,
non-destructive entry point into the same exclusive submission lock,
`observe_jes` console transport and `require_jes_clear` classifier used
by the controller. It always exits without invoking reconstruction, including
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
A fresh guard-only live retest is **pending**, and neither this observation
nor a future CLEAR response authorizes a destructive reconstruction.

## Remaining work before live activation

1. The submission-control integration is committed on GitHub `main` at `2eb099c`; finish independent regression coverage for the bootstrap Bash/TRNILRG descriptor handoff and guarded public CLI, then seek explicit owner approval before committing further changes. `--run` must require an interactive exact-scope acknowledgment and deny noninteractive execution.
2. Prove in a controller-level offline negative test that a second project submitter fails closed while the controller has the lock, including during approval, JES preflight and error handling; retain ordinary standalone tool usability afterward.
3. Review the existing single TK5 reader, printer, console, `dspal` configuration, `HERC02` dataset inventory and source revision before destructive operations. No other datasets are in approved scope.
4. With separately authorized MVS activity, verify a live active job rejects the **integrated controller** before any cleanup or purge. JOB 357 already verified `jes-idle` itself; it did not verify the integrated runner.
5. Only after a fresh explicit one-run authorization and an accepted submission-control boundary, perform one full rebuild from zero, verify JES payloads and installed members, then test interruption followed by an entirely new rebuild. No checkpoint/resume, regression side effect, object promotion, baseline tag or release.
6. Record evidence and seek separate owner acceptance. Do not treat successful synthetic tests as acceptance of live reconstruction.

## Safety boundary

The proposed `tools/reconstruction/run --run` entry point is terminal-only, and **does not authorize a reconstruction by its mere existence**. Every destructive attempt requires a fresh approval of the displayed plan; pending MVS acceptance and separate owner approval, no JES submission, workarea deletion, `dspal purgebcpl`, installed dataset change, tag or release has been requested.
