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

The tests use an isolated Git fixture or in-memory plan stubs. They do not run JES, change MVS datasets, or create authorization artifacts. The [manual reconstruction guide](../../docs/Rebuild-BCPL-for-MVS-from-source.md) remains the operating procedure. Step 3 now has offline-tested safety hardening and per-attempt evidence reporting. **Live destructive execution is still disabled.** The real-MVS active-job negative test passed on 5 November 2026 and Step 3 is owner-closed; separate live-integration acceptance and operation authorization remain required.

## Step 3 — Safety-hardened reconstruction engine (CLOSED 5 November 2026)

The [Step 3 owner closure and JOB 357 MVS evidence](../../packaging/distribution/clean-room-reconstruction-step3-closure-20261105.md) record completion of safety-hardening acceptance, not authorization of a destructive rebuild.

`tools/reconstruction/run --list` displays the **25 canonical operations** shared by the planner and runner, ordered under the manual guide's Steps 1–9. The runner uses the existing independent tools, not replacement implementations. There are no regression suites, checkpoints, resume, baseline tags or release side effects.

The read-only planner presents all managed dataset targets, tracked and generated member writes, host cleanup entries, implicit JES build writes, source revision, effective nonsecret configuration digest and operation digest. Approval is interactive, temporary and scoped to the **entire immutable plan**. After the acknowledgment, the runner checks the source, configuration and dataset inventory before operations and refuses drift.

The fail-closed JES idle gate requires two independently verified CLEAR observations from the existing `jes-idle` diagnostic. No `False`, missing, ambiguous, incomplete or ACTIVE observation can pass. An idle check is not exclusive control of JES; other submitters must still be quiesced by the operator.

`tools/clean-workarea` remains independently executable with its interactive `DELETE` confirmation. In reconstruction mode, it uses the exact reviewed recursive host object inventory and a descriptor-relative deletion procedure. It rejects symlinks, mount points, cross-device entries, replacement and unexpected objects. It preserves `workarea/.gitignore`. **The fingerprint by itself is not an authorization token**; the controller must enforce the single-run gate before using it.

For the approved `HERC02` boundary, the runner compares effective configuration with the tracked managed dataset manifest (currently **29 logical datasets**, including all nine `CAMB_*` datasets and `DIST_DOCS`). Before purge and allocation, it independently compares the generated JCL targets with the full approved DSN inventory. Canonical build JCL undergoes static target preflight.

Each of the seven build payloads is verified by its JES payload number, exact step inventory and zero return codes, independently obtained full job report, required interpreter `CODE=0` records, IFOX assembler severity where applicable, and readback/compare checks for the three installed System Extensions. Compiler, runtime, base-library and extension member inventories are checked as distinct requirements. Bootstrap-generated inputs and outputs are matched to the SHA-256 generation manifest.

Reports, payload summaries, job details and diagnostic results are written outside disposable `workarea/` under `mvs-state/reconstruction-evidence/`; credentials are redacted. Reports are **diagnostic evidence only**, not completion checkpoints, release approval or baseline acceptance.

**Live execution remains disabled:** `tools/reconstruction/run --run` returns RC=2 and cannot reach the engine from its public CLI. The completed Step 3 live guard test is documented separately. Future guarded live-entry integration and explicit scoped operator authorization remain required. A successful read-only idle sample does not authorize destructive reconstruction.

Offline verification from the checkout root:

```sh
python3 -B -m unittest discover -s tools/checks -p 'test_reconstruction_*.py' -v
```

The synthetic tests never start JES jobs or change MVS datasets. The [manual reconstruction guide](../../docs/Rebuild-BCPL-for-MVS-from-source.md) remains authoritative.

## Next automation phase — single-TK5 submission control (candidate)

An offline-tested candidate adds a cooperative kernel `flock` admission gate for `tools/mvs/submit-jcl` (and its `dspal` clients) plus the direct MR10 `compile-and-run` socket transport. The reconstruction controller acquires an exclusive lease before interactive approval and retains it until completion or failure. Only explicitly delegated child processes inherit that lease. Contending project submitters are refused while reconstruction owns the window.

This is **cooperative project-tool exclusivity**, not a hardware or JES system lock. A direct `nc` client, independent console/3270 submission, or other unintegrated connection to Hercules' reader can bypass it. Operator quiescence remains required. The existing single TK5 installation is used; no additional installation is created. See the [design and tests](../../packaging/distribution/clean-room-reconstruction-submission-control-design-20261105.md). This candidate still requires full-project regression and acceptance; `tools/reconstruction/run --run` remains hard-disabled (RC=2).

## Read-only JES2 activity safeguard (calibration candidate)

The fixed-command diagnostic `tools/reconstruction/jes-idle --live` uses
`tools/mvs/mvs-console`'s transport to issue `/$DA` twice. On OS/VS2 MVS
JES2 Release 4.1, `$DA` displays active **batch jobs**, including execution
and unit-record-device processing. `$HASP612 NO ACTIVE JOBS` is its explicit
empty-list response; `$HASP611 LIST INCOMPLETE` prevents reliable inference.

Each sample reads only console bytes appended after issuing the command. The
parser accepts either a timestamp-wrapped TK5 `$HASP000 NO ACTIVE JOBS`
reply (optionally preceded by an exact `$DA` echo) or an echoed inquiry
followed by exactly one `$HASP612` reply. Unrecognized additional console
lines block rather than being silently ignored. Contradictory jobs, JES2
activity, incomplete listings, and transport failures also block. Two independent clear samples are
required to report a point-in-time idle observation. These rules intentionally
may reject a harmless but unfamiliar TK5 console format.

The initial diagnostic calibration described below was pending real-MVS verification when written. The later controlled JOB 357 observation established ACTIVE/BLOCKED behavior and two-sample idle verification on TK5; see the [Step 3 closure record](../../packaging/distribution/clean-room-reconstruction-step3-closure-20261105.md). Synthetic tests alone remain insufficient evidence.

No active-job inquiry can reserve the system or prevent another submitter from
starting a job after the query. Before enabling destructive automation, also
establish operator quiescence of independent job submitters and validate the
console response handling under actual idle and active conditions.

`tools/reconstruction/run --run` remains disabled. The diagnostic never calls
`dspal`, cleans the workarea, submits JES jobs, or modifies MVS datasets. It
returns RC=0 only when it sees two qualifying clear samples; RC=2 otherwise.

Run offline tests from any directory:

```sh
python3 -B -m unittest discover \
    -s "$HOME/Source/Repos/BCPL-for-MVS/tools/checks" \
    -p 'test_reconstruction_jes_idle.py' -v
```

Historical sources: *Operator's Library: OS/VS2 MVS JES2 Commands*, JES2
Release 4.1 (GC23-0007-1), Chapter 6; *MVS/370 Message Library*,
`$HASP611` and `$HASP612`.

### TK5/MVS 3.8J console calibration (5 November 2026)

The first live observation from TK5 produced:

```text
15:20:00 /16.19.59           $HASP000 NO ACTIVE JOBS
```

The original synthetic parser expected the later `$HASP612` message and a
separate `$DA` command echo; TK5's console returned neither. The revised
parser recognizes **only this timestamp-wrapped `$HASP000 NO ACTIVE JOBS`**
shape as an additional idle response. `$HASP000 OK`, a bare `$HASP000` line,
extra console messages, and contradictory active/incomplete replies do not
qualify. The existing `$HASP612` and command-echo requirements remain.

This calibration is derived from the real console line above, not proof that
all valid TK5 reply shapes are covered. A second live inquiry on 5 November 2026
also returned:

```text
15:38:17 /16.38.17           $HASP000 NO ACTIVE JOBS
```

This line also matches the existing strict timestamp pattern. The original
one-line-only condition can nevertheless reject an otherwise recognizable
response when the console delta contains an extra command echo. The revised
parser permits only a preceding recognized `$DA` echo; other extra lines
still BLOCK. Because earlier diagnostics printed only `$HASP` messages,
the contents of any other lines were not visible.

For a **read-only diagnostic** of a blocked result, run:

```sh
tools/reconstruction/jes-idle --live --diagnose
```

The opt-in diagnostic prints escaped raw console deltas **only on BLOCKED**.
They may contain other operator messages, including sensitive data; review
and redact before sharing. The diagnostic does not authorize reconstruction.

Live two-sample verification and a controlled active-job observation were completed with JOB 357 (5 November 2026). An idle observation is not a lock on other job submitters. Live reconstruction remains disabled.

### TK5 Hercules echo-pair calibration (5 November 2026)

The next live diagnostic returned one `$HASP000 NO ACTIVE JOBS` reply preceded
by **two identical pairs** of Hercules submission messages and `$DA` echoes:

```text
16:36:36 HHC00013I '/' input entered for console 0:0009: "$DA"
16:36:36 $DA
16:36:36 HHC00013I '/' input entered for console 0:0009: "$DA"
16:36:36 $DA
16:36:36 /17.36.35           $HASP000 NO ACTIVE JOBS
```

The prior parser correctly blocked this previously unrecognized console
envelope (RC=2). The revised recognition accepts a single exact Hercules
submission/typed-echo pair or **two byte-for-byte identical pairs** before
one timestamped idle reply. Mismatched timestamps, extra unrelated lines,
partial pairs, three or more pairs, activity, and incomplete-list indicators
still block. The later `$HASP612` parsing remains unchanged.

This is a diagnostic calibration, **not** a guarantee that JES is reserved
or quiescent. The subsequent fresh two-sample live result and separate active-job negative verification passed with JOB 357. This does not authorize reconstruction.
`tools/reconstruction/run --run` remains disabled.
