# Clean-room reconstruction — preflight and operator approval

The approved [clean-room automation decision](../../packaging/distribution/clean-room-reconstruction-automation-decision-20261104.md) calls for a complete rebuild from zero after **one explicit, scope-specific operator acknowledgment**. There is no checkpoint/resume system. Regression testing and release are separate workflows.

## Step 1 — Read-only planner

```sh
tools/reconstruction/plan
tools/reconstruction/plan --dry-run
tools/reconstruction/plan --probe
```

The default and `--dry-run` modes are identical. The planner reports the Git SHA and branch, effective non-secret configuration fingerprint, target/reader endpoint, workarea entries proposed for deletion, all configured managed datasets and their allocation attributes, source counts, and build stages. `--probe` adds read-only Docker/TCP checks; it does **not** inspect active JES jobs, establish an authenticated session, or start services. No files, JES jobs, or MVS datasets are modified.

The effective configuration fingerprint deliberately **excludes credentials** but includes other effective settings and source/dataset mappings, including private local overrides. Review the full proposed deletion list carefully. The actual purge JCL and allocation JCL can also be inspected independently with `dspal purgebcpl --show-jcl` and `dspal initbcpl --show-jcl`.

## Step 2 — Single-run acknowledgment gate (exercise only)

```sh
tools/reconstruction/authorize
tools/reconstruction/authorize --probe
```

`authorize` prints the full current read-only plan and asks the operator to type an exact `REBUILD <HLQ> <plan-fingerprint>` phrase on an **interactive terminal**. Piped input, a changed or blocked preflight, an incorrect phrase, and an interrupted prompt are rejected. After the typed acknowledgment, the plan is recomputed and must still match the original review.

**Important:** This is a safe exercise of the approval gate. It **does not initiate a rebuild** and **does not persist, export, or transfer approval**. The in-memory approval is discarded when the standalone program ends. The future execution runner must call the same approval function in *its own process* and validate that scope immediately before the first destructive action. No `--yes`, approval token file, or reusable bypass is provided.

Standalone return codes: `0` = acknowledgment exercise accepted (not a rebuild); `2` = preflight blocked, stale scope, or noninteractive terminal; `3` = operator cancelled or declined.

## Offline tests

From the repository root:

```sh
python3 -B -m unittest discover -s tools/checks -p 'test_reconstruction_*.py' -v
```

The tests use an isolated Git fixture or in-memory plan stubs. They do not run JES, change MVS datasets, or create authorization artifacts. The [manual reconstruction guide](../../docs/Rebuild-BCPL-for-MVS-from-source.md) remains the operating procedure. Steps 3–5 (actual destructive orchestration, progress and report) are **not yet implemented or authorized**.
