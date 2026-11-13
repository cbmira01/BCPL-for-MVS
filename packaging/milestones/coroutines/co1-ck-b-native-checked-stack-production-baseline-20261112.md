# CO.1 — CK-B production native checked-stack baseline: owner-supplied run

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture
**Recorded:** 12 November 2026, America/Kentucky/Louisville (run evidence directory dated 13 November 2026 UTC)
**Evidence class:** OWNER-REPORTED NATIVE REGRESSION SUMMARY; per-case JES/IFOX/IEWL/GO logs not independently reviewed
**Status:** CK-B baseline reported PASS 4/4; CO.1 design gate OPEN

## Run invocation and provenance

The owner provided console output from this exact existing MVS-facing regression invocation:

```text
tools/tests/run-suite bootstrap --run --profile production --case 49 --case 50 --case 51 --case 52
```

The runner reported this local evidence directory:

```text
workarea/test-suites/20261113T004711Z-10548-bootstrap-production-76esg_or
```

The directory and its `summary.json` / per-case `runner.log` files reside in the owner's WSL workspace, **not in this GitHub commit**. The owner did not provide their contents. Although the coordinator records `git_head` in its local JSON summary, the displayed console excerpt does **not** contain that field. **Do not infer the executed source revision from the current GitHub HEAD.**

## Reported results

| Case | Canonical native Bootstrap test name | Reported suite outcome | Reported native runner RC |
| --- | --- | --- | --- |
| 49 | `49-checked-procedure-entry` | PASS | 0 |
| 50 | `50-stack-frame-size` | PASS | 0 |
| 51 | `51-checked-recursion` | PASS | 0 |
| 52 | `52-controlled-stack-overflow` | PASS | 0 |

The reported suite totals are **PASS 4; FAIL 0; SKIP 0; BLOCKED 0; TOTAL 4**. Every case line records its local log under `workarea/test-suites/20261113T004711Z-10548-bootstrap-production-76esg_or/case-NN/runner.log`.

The implementation of `tools/tests/run-suite` at GitHub source revision `81f8a2e65d1c9f2accdbda0356d90c5d2cddc919` marks a case PASS only when the native runner returns RC=0 **and** its recorded output contains `PASS NN`, `PASS 1`, `FAIL 0`, `SKIP 0`, and `TOTAL 1` for that selected case. This explains the **coordinator-level** meaning of the reported PASS values. It is not an independent inspection of the underlying JES reports.

No specific IFOX severity, IEWL RC, GO RC, JES job number, individual job outcome, device action, or installed object revision can be reconstructed from the pasted summary alone. The native runner logs remain the authoritative evidence for those finer-grained claims.

## Scope of the verified baseline

This satisfies the planned **CK-B baseline at the coordinator-reporting level** in [CO.1 checked-entry option matrix](co1-cg370-checked-entry-option-matrix-20261112.md). Existing test evidence uses the `S.STKCK` system-vector **+60** checked-entry path. It does **not** exercise `S.STKCKCOUNT` **+80** under combined `/CK` or prove a correction to the source-observed +80 gap. No coroutine-specific context switch, first activation, worker-stack switching, `BCPLAPT` active-limit integration, or new native coroutine oracle was exercised by these four existing baseline cases.

The owner-reported suite result does not itself close CO.1, approve a register save set or descriptor, permit CO.2 implementation, or authorize any installed-MVS dataset change.

## Disposition and further evidence needed

- Retain the owner's exact four-PASS production baseline and local evidence path.
- If a formal independent target-JES acceptance decision is later required, inspect the already-retained `case-49` through `case-52` runner logs and JES receipts, including their exact GO RCs and runtime/object profile; **do not repeat the run solely to generate console printouts**.
- Continue the separate, compile-only CK-C examination of `/CK` emission only with appropriate MVS authorization; **do not execute the current +80 stub**.
- Preserve existing native case IDs, generated fixtures and accepted failure/skip policies.

**CO.1 IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED.**
