# Clean-room reconstruction — single-TK5 submission-control design

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 5 November 2026  
**Status:** Source-controlled cooperative gate (commit `2eb099c`); guarded live-entry integration remains unaccepted  
**Predecessor:** Step 3 safety-hardening closure (JOB 357)  
**Scope:** Next clean-room automation development phase, not the manual reconstruction guide's Step 4.

## Owner direction

Use **one existing TK5/MVS 3.8J installation**, not a disposable copy or
multiple Docker installations. BCPL-managed datasets are reconstructible
outputs from GitHub. Do not equate recreating a Docker container with
resetting bind-mounted DASD volumes.

The reconstruction controller must have **exclusive control of supported
project JES submission paths** for the lifetime of each attempt, including
review/approval, preflight, every JES operation, evidence processing, and
failure/interrupt cleanup. A new attempt must start from zero, without resume.

## Cooperative single-host mechanism

Use a fail-closed Linux advisory `flock` at
`mvs-state/locks/jes-submission.lock`, outside disposable `workarea/`.
A controller obtains an exclusive, nonblocking kernel lock before approval and
releases it only on termination. Existing project submitters obtain shared,
nonblocking admission covering reader connection and confirmation of acceptance;
refuse while the controller owns exclusivity.

Controller-owned subprocesses inherit the controller's open lock-file descriptor
across `pass_fds` and can submit without downgrading or reacquiring the exclusive
lock. Require matching trusted inode and proof that the inherited open-file
description itself holds the exclusive kernel lock; independently verify
contention from a fresh description. A forged descriptor targeting the same
file is not sufficient. A bare environment variable is
not authorization. Invalid/missing leases fail closed.

The public `tools/mvs/submit-jcl` interface continues to behave as before and
runs the existing Bash implementation (`submit-jcl-core.sh`) inside admission.
`dspal-core.py` forwards the controller FD to that public helper.
`tools/mr10/compile-and-run-core.py` admits direct socket submission and retains
admission until the new JES job is recognized. The reconstruction controller
holds exclusivity from the start of `authorized_run` until final reporting.

## Limits and failure handling

The lock is **cooperative**, enforced by these project tools. It does not secure
Hercules' network port 3505, stop other direct `nc` clients, block 3270/console
submissions, or isolate external users. An operator must still ensure no outside
submission paths are in use. `jes-idle` retains the two-sample active-job guard
inside the locked window before any destructive operation. The lock must not
be described as a JES/MVS system-wide reservation.

No authorization is implied by possessing a lock or inherited FD. Approval is
still one-run, scope-bound and interactive. No direct `--yes` bypass, automatic
release/tagging/regression or checkpoint/resume is added.

**The guarded `tools/reconstruction/run --run` integration is pending verification and owner approval**
through integration and offline tests. Separate permission is still required for
a destructive reconstruction of the single TK5 installation.

## Verification

The isolated offline gate implementation ran 18 Python unittest cases covering
process contention, delegated FD through grandchildren, invalid or mismatched
FDs, symlink and insecure-path refusal, normal submission, long-lived submission
admission, refusal of unrelated submissions during controller ownership, error
exit codes, rejected forged same-inode descriptors, and lock release
following exceptions or controller termination (SIGKILL). This is not a full MVS test
or a full project regression run. No JES jobs or MVS datasets were touched.
