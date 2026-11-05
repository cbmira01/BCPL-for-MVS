# Clean-room reconstruction automation — Step 3 safety-hardening closure

**Project:** BCPL for MVS 3.8 Reconstruction  
**Owner decision:** 5 November 2026 — Step 3 CLOSED  
**Authority:** GitHub `main` and operator-supplied Hercules/TK5 MVS 3.8J / JES2 evidence  
**Implementation baseline tested:** `caf7a66610ba4dc498f2df96c457612093ba0da8`  
**Scope:** Safety-hardening of the *automation implementation*, not the manual reconstruction guide's Step 3 or Step 4. No project milestone/march numbering is created by this record.

## Decision and acceptance boundary

At the owner's direction, Step 3 — Safety Hardening is **CLOSED** based on the implemented safeguards, successful offline verification, and the controlled live-MVS active-job negative test. This does **not** assert a completed clean-room reconstruction, authorise `tools/reconstruction/run --run`, accept a build baseline, promote objects, create a tag, or publish a release.

The separate [owner-approved 4 November automation decision](clean-room-reconstruction-automation-decision-20261104.md) remains authoritative, as does the [manual rebuild guide](../../docs/Rebuild-BCPL-for-MVS-from-source.md). The guide's **Step 4 — Test the new interpreter** is a separate MR10 test workflow, not the next automation implementation phase.

## Implemented safeguards reviewed

Commit `caf7a666` introduced the shared 25-operation planner/runner manifest, same-process scope-bound one-run approval, fail-closed two-sample JES guard, exact `HERC02` and 29-managed-dataset boundaries (including nine `CAMB_*` datasets and `DIST_DOCS`), pre-purge and pre-allocation JCL scope checking, conservative descriptor-relative workarea cleanup, seven payload-specific verification contracts, and credential-redacted persistent reports outside disposable `workarea/`.

The final source review of `tools/reconstruction/run`, `contract.py`, `verify.py`, `evidence.py`, `jes-idle`, and the associated decision and operator policy confirmed the **public live-run entry point remains a deliberate hard stop**: `tools/reconstruction/run --run` returns RC=2. The independently callable tools retain their separate operating safeguards. Offline simulation is not equivalent to a verified full reconstruction.

The operator's WSL checkout of `caf7a666` executed:

```text
python3 -B -m unittest discover -s tools/checks -p 'test_reconstruction_*.py' -v
Ran 133 tests in 22.814s
OK
Reconstruction test RC=0
```

This evidence was supplied from the workstation transcript. It is not represented as a CI run or a fresh test by the documentation author.

## Controlled real-MVS negative test: JOB 357

**Date:** 5 November 2026. **Job:** `JESGTEST` / **JOB 357**. **Target:** TK5, MVS 3.8J, JES2. The test JCL was generated from a small System/370 IFOX program containing `STIMER WAIT,BINTVL=SEC120` with `SEC120 DC F'12000'`; the generated JCL used `ASM`, `LKED`, and `GO` steps, temporary `&&` data sets and shared system macro-library input. The submission helper was launched **concurrently** with JES inquiries so they could observe execution rather than only job completion.

### Evidence observations

| Phase | Console / job evidence | Safeguard outcome |
| --- | --- | --- |
| Initial idle baseline | `22:31:09` and `22:31:11`, `$HASP000 NO ACTIVE JOBS` | Two CLEAR; RC=0 |
| Concurrent reader/initiator activity | `22:31:15` `$HASP100 JESGTEST ON READER1` and `$HASP373 JESGTEST STARTED`; a preceding `$HASP000 NO ACTIVE JOBS` was present in the same captured delta | UNKNOWN, **BLOCKED**, RC=2; activity was not silently ignored |
| Executing batch job | `22:31:17` `JOB 357 $HASP000 JESGTEST EXECUTING A PRIO 4 TK5R` | ACTIVE, **BLOCKED**, RC=2 |
| Job completion | `05 NOV 26 23.31.15 - 23.33.15` (MVS report clock); `IFOX00`, `IEWL`, and `GO` each RC=0000 | JOB RESULT: SUCCESS; HIGHEST RC: 0000; CPU 0.05 seconds |
| Post-completion idle | `22:33:24` and `22:33:26`, `$HASP000 NO ACTIVE JOBS` | Two CLEAR; RC=0 |

Relevant raw operator transcript excerpts (the host console and job-summary timestamps differ by one hour in the captured display):

```text
Initial JES idle check (RC=0)
JES2 $DA sample 1/2: CLEAR
JES2 $DA sample 2/2: CLEAR

JES inquiry 1 (RC=2)
JES2 $DA sample 1/2: UNKNOWN — concurrent JES2 job activity observed
  22:31:15 /23.31.15 JOB  357  $HASP100 JESGTEST ON READER1     ASM LINK GO
  22:31:15 /23.31.15 JOB  357  $HASP373 JESGTEST STARTED - INIT  1 - CLASS A - SYS TK5R
BLOCKED: active/unknown JES2 state; no reconstruction actions performed.

JES inquiry 2 (RC=2)
JES2 $DA sample 1/2: ACTIVE — active batch job reported
  22:31:17 /23.31.17 JOB  357  $HASP000 JESGTEST EXECUTING A PRIO  4 TK5R
BLOCKED: active/unknown JES2 state; no reconstruction actions performed.

JOB 357  JESGTEST
05 NOV 26  23.31.15 - 23.33.15
ASM        IFOX00       RC=0000
LKED       IEWL         RC=0000
GO         PGM=*.DD     RC=0000
JOB RESULT: SUCCESS
HIGHEST RC: 0000

Post-job idle check (RC=0)
JES2 $DA sample 1/2: CLEAR
JES2 $DA sample 2/2: CLEAR

RESULT: PASS
Observed ACTIVE: True BLOCKED: True Post-job CLEAR: True
Controlled JES negative-test RC=0
```

An earlier JOB 356 completed successfully but the initial script checked the JES state too late, after the timed wait had ended. Its CLEAR observations were **not** used as active-job negative-test acceptance evidence; JOB 357 corrects that timing defect.

## Limitations and continuing requirements

- Two point-in-time CLEAR replies are not an exclusive lock on JES or a guarantee of future quiescence. Unexpected submissions after the inquiry remain possible; establish operator quiescence of independent submitters before any destructive rebuild.
- A controlled job verifies the active-state parser and refusal; it does not exercise all failure, timing, transport, cleanup, or device conditions against a live target. Offline tests remain the principal proof for those paths.
- `tools/reconstruction/run --run` **remains disabled (RC=2)**. This closure does not permit PDS purge, workarea cleanup, full reconstruction, MVS object promotion, or installation.
- Do not infer readiness for production from the successful two-minute test. The next automation work must establish a safe disposable MVS target, guarded live-entry integration and separate owner approval before any destructive attempt.

## Next work

Continue with the [guarded live integration planning record](clean-room-reconstruction-live-integration-plan-20261105.md). Its development sequence is **not** the manual guide's numbered Step 4, and this closure creates no new milestone or march.
