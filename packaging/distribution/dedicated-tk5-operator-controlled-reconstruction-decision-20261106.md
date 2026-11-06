# Decision — dedicated TK5 reconstruction without a submission lock

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 6 November 2026  
**Status:** Owner-approved architecture decision; implementation requires offline and live verification  
**Authority:** GitHub `main`, the [reconstruction automation decision](clean-room-reconstruction-automation-decision-20261104.md), and the [operator WSL command policy](../operations/operator-wsl-command-policy.md).  
**Scope:** The one existing dedicated Hercules/TK5/MVS 3.8J instance. This does not create a new milestone, march, or manual reconstruction-guide step.

## Decision

The dedicated TK5 instance exists to build, test, reconstruct, package, and release the Cambridge BCPL Programming System. It is not a general-purpose, concurrent-user MVS service.

**Do not impose a WSL, filesystem, or MVS dataset-based reconstruction lock.** Remove the cooperative WSL `flock` submission gate and its inherited file-descriptor machinery from the reconstruction controller, ordinary JES submitter, `dspal`, MR10 direct reader transport, and bootstrap child processes. Do not implement the proposed `HERC02.BCPL.LOCK` QSAM/dataset-existence scheme.

The earlier [single-TK5 submission-control design](clean-room-reconstruction-submission-control-design-20261105.md) records the superseded approach and historical verification evidence; it is no longer the operating contract.

## Operator responsibility

Only one operator controls project activity. **Before reconstructing, stop independent submissions and allow earlier work to finish.** During a reconstruction, do not launch any independent project regression, compile, dataset, JES, reader-port, console, or 3270 submission activity. Do not use a second controller.

The controller continues to require an explicit, fresh, interactive, scope-bound `REBUILD <HLQ> <fingerprint>` approval. It still checks two fresh JES2 `/$DA` observations for CLEAR before destructive work and refuses ACTIVE, UNKNOWN, partial, or unrecognized replies. A CLEAR reply is a **point-in-time observation**, not exclusive ownership of JES, a reservation, or proof against later arrivals.

If a run stops or is interrupted, examine outstanding JES work before beginning a new full-from-zero attempt. Never purge while an earlier job may still be writing managed datasets.

## Safety mechanisms retained

- GitHub `main`, clean source and effective configuration checks, fixed managed-DSN inventory and JCL target validation
- One-use exact scope approval before the first deletion, purge, or MVS write
- Two independently verified JES2 idle observations and fail-closed error behavior
- Per-step return codes, payload identity, IFOX/IEWL/ICINT and installed-member checks
- Durable credential-redacted evidence outside the disposable workarea
- Separate approvals for MVS execution, commits, candidate promotion, tags, and releases

The read-only `tools/reconstruction/run --check-live-guard` CLI is retained for compatibility. Despite its historical name, it checks JES only and must never enter the reconstruction engine. No lock is obtained.

## Evidence and limits

On 6 November 2026 the integrated read-only guard detected **JOB 359 JESGTEST EXECUTING** and blocked with RC=2 after the temporary submission lock had been released. The same transcript also contained an older, reused **JOB 359 DSPALPUT** report, so the test harness incorrectly treated the older report as the current job's completion; its final overall RC=2 is **not** accepted as a completed job-lifecycle test. This establishes a real ACTIVE refusal, not a full reconstruction acceptance.

Removing the host lock is an **operating-model decision**, not evidence that concurrent operations became safe. The standalone submit tools will no longer refuse concurrent work; compliance with the single-operator rule is essential. If multi-operator or general-purpose MVS use is introduced, revisit a true concurrency-control design.

No destructive live reconstruction is authorized by this decision. No automatically resumed run, regression run, tag, release, or dataset change is implied.

## Implementation acceptance

Verify the simplified controller and the standalone submission paths through offline regression testing. Check `--check-live-guard` still refuses ACTIVE/UNKNOWN and that `--run` still refuses noninteractive use. Independently authorize any live MVS test or reconstruction after review.
