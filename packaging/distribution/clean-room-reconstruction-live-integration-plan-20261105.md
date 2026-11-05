# Clean-room reconstruction automation — next phase: guarded live integration

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 5 November 2026  
**Status:** STARTED — source review and design planning only; live execution **NOT AUTHORISED**  
**Predecessor:** [Step 3 safety-hardening closure and JOB 357 evidence](clean-room-reconstruction-step3-closure-20261105.md)  
**Authority:** [4 November automation decision](clean-room-reconstruction-automation-decision-20261104.md); [manual reconstruction guide](../../docs/Rebuild-BCPL-for-MVS-from-source.md).

The owner's request to proceed to **Step 4 of automation development** starts the next planning and integration phase. This is **not** the manual guide's **Step 4 — Test the new interpreter**, which is a separate test workflow deliberately excluded from automated reconstruction. This record does not create a milestone or march number.

## Objective

Wire and accept an operator-invoked, one-shot live reconstruction path **only after** proving that the single interactive approval, fail-closed JES guard, exact target/source/scope checks, existing `dspal` and bootstrap tools, and persistent reports remain correct end to end. Restart from zero after any failed or interrupted attempt; no checkpoints or resume. Independent regression and release workflows remain separate.

## Initial read-only review completed

The existing `tools/reconstruction/run` already implements `authorized_run(...)`, a controller that requests in-process approval, creates per-attempt evidence outside `workarea/`, verifies two JES CLEAR observations, rechecks the plan, then executes the 25 approved operations. The CLI `main()` deliberately does **not** call that controller: `--run` returns RC=2. The next phase must not remove that hard stop until the live-entry design and target isolation have been reviewed.

The `HERC02` namespace and current 29-dataset inventory are not a substitute for a disposable MVS target. Reusing the operator's active development PDSes would still be destructive, even though the DSNs are in scope.

## Proposed implementation and verification order

1. **Specify isolation.** Choose a disposable TK5/MVS system-state copy with distinct DASD volumes and a verifiable operator-controlled lifecycle. Confirm the reader, console, printer and `dspal` endpoints all target that copy. Verify source Git SHA, tracked files and effective private configuration; prevent accidental contact with the ongoing development installation.
2. **Design guarded CLI wiring.** Use the existing single-run `authorized_run` and fixed `jes-idle.check_twice` interface, not a second approval mechanism. Keep `--list` and `plan` read-only. Define interruption/timeout, console progress and final RC behavior; no ambient `--yes` bypass.
3. **Offline integration acceptance.** Revalidate all reconstruction tests and add controller/CLI tests that prove no unapproved entry can call cleanup, purge, population or submission. Cover malformed JES output, active jobs, drift after acknowledgment, an extra managed DSN, and interrupted steps.
4. **Disposable-system negative verification.** With separately authorized MVS activity, verify that an actual active batch job blocks the **integrated controller** before host cleanup or PDS purge. The existing JOB 357 test verifies the *safeguard*; it does not yet prove the public live controller's destructive boundary.
5. **Disposable full rebuild.** Only after independent scope and target review and explicit operator approval, run a fresh whole reconstruction on the disposable installation, inspect all payload reports, verify object libraries and outputs, then repeat after a deliberately interrupted attempt from zero. Preserve reports outside `workarea/`.
6. **Acceptance review.** Confirm reproducibility and failure evidence against the manual guide. Do not automatically run regressions, promote a baseline, tag, package tape, or publish a release.

## Critical design decisions before implementation

- **Target isolation:** how the disposable MVS state and its device/console/reader endpoints will be made distinguishable from the active development system, so no misdirected purge can be approved.
- **External JES quiescence:** how an operator will prevent independent submitters from starting after the two read-only `$DA` inquiries; sampling alone cannot lock JES.
- **Live entry-point exposure:** whether the initial enablement is limited to a disposable-target-only switch, retaining the hard stop for other environments until validated. No general-purpose destructive `--run` exposure is proposed at this stage.

These choices require owner review before code changes to enable live reconstruction. No new commit, even one implementing the entry point, constitutes MVS-operation approval.

## Current boundary

**The public live runner remains disabled:** `tools/reconstruction/run --run` returns RC=2. No JES job, workarea deletion, `dspal purgebcpl`, dataset installation or full reconstruction is authorised by this planning record.
