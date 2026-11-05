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

The tests use an isolated Git fixture or in-memory plan stubs. They do not run JES, change MVS datasets, or create authorization artifacts. The [manual reconstruction guide](../../docs/Rebuild-BCPL-for-MVS-from-source.md) remains the operating procedure. Step 3 has an offline-tested stage engine, but **live destructive execution is disabled**. Console streaming, MVS-active-job checks, and complete evidence reporting remain future work.

## Step 3 — reconstruction stage engine (offline implementation)

`tools/reconstruction/run --list` displays the selected reconstruction operations in the established guide order. It does not submit JES jobs or change files.

The stage engine calls the existing `clean-workarea`, `dspal`, `prepare-bootstrap`, `compile-and-run`, and `compile-mvs` tools in order, using the **same-process, one-run** approval gate from Step 2. It checks the Git revision and effective `dspal` configuration throughout, stops on any required nonzero result, recognizes the precise first-population RC=2 exception, and inspects key interpreter, object-library and generated-assembler results. No regression suites, checkpoint/resume state, Git tags or release tasks are included.

`tools/clean-workarea` keeps its standalone interactive `DELETE` confirmation. An internal `--reconstruction-scope SHA256` form checks the exact top-level workarea entry set against a provided fingerprint, rejecting any changed set. **The fingerprint alone is not proof of operator approval.** The orchestration controller must enforce the Step 2 acknowledgment before using this interface. Do not invoke the internal mode manually.

**Live execution remains disabled.** `tools/reconstruction/run --run` currently returns RC=2 without prompting, cleaning or contacting MVS. Before enabling it, implement and verify a read-only MVS/JES active-job guard that fails closed if earlier work may still be writing managed datasets, and complete the payload-specific verification and evidence collection in subsequent steps. This deliberately prevents destructive behavior while the integration with real MVS 3.8J remains unverified.

Offline simulation:

```sh
python3 -B -m unittest discover -s tools/checks -p 'test_reconstruction_run.py' -v
```

The tests use temporary Git repositories, fake MVS command results, and source/configuration/approval stubs. They never submit actual MVS jobs. The manual reconstruction guide remains authoritative.
