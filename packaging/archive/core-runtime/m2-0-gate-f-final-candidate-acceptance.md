# M2.0 Gate F — Final DEVOBJ Candidate Acceptance

**Status: ACCEPTED AND CLOSED — 14 October 2026. March M2.0 formally CLOSED.**
**Candidate:** Git `asm/bcplmain-d6-candidate.asm` assembled to `HERC02.BCPL.DEVOBJ(BCPLM6)`, linked with independent DEVOBJ(BCPLIO), DEVOBJ(BCPLAPT), DEVOBJ(BCPLBYTE), DEVOBJ(BCPLMEM), and DEVOBJ(BLIB).
**Predecessors:** Gates A–D accepted; Gate E source/maintainability review accepted, with runtime re-execution expressly transferred here.

## Why Gate F remains open

D6 was fully proven *before* Gate E comment/header refresh: IFOX/IEBGENER JOB 2389 RC=0000, IEWL JOB 2393 RC=0000, full native 00–123 **123 PASS, 0 FAIL, one expected source-only SKIP 083**. Source ownership and XREF showed BCPLMAIN X'0C00' (versus D5 X'1070') and independent BCPLIO X'0FF8'.

Gate E refreshed comments in BCPLAPT/BCPLBYTE/BCPLIO, then operator installed rebuilt independent DEVOBJ objects: JOBs 2722, 2725, 2728 IFOX and IEBGENER RC=0000, zero flagged assembler statements, and integrated D6LINK JOB 2731 IEWL RC=0000. **No post-refresh runtime GO/regression evidence has yet been received.** Claiming Gate F acceptance now would conflate the earlier execution with the newly rebuilt object members.

## Gate F acceptance execution

From repository root after `git pull --ff-only`:

```sh
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 0 --show-output
```

Require 1 PASS, 0 FAIL. Then run *the current final rebuilt object set*:

```sh
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression --show-output
```

Require exactly **123 PASS, 0 FAIL, 1 SKIP, 124 TOTAL** (083 is expected source-only instrumentation). The full run subsumes the smoke test, but recording both explicitly identifies Gate E's deferred check. Retain job IDs / failure reports if any test diverges.

## M1.9 comparison / bounded status

- M1.9 specified a native bootstrap/runtime contract and programmer-centric, historically modest diagnostic direction. The accepted M2.0 candidate preserves BCPL-visible service interfaces under tested cases; its changes are internal independent-CSECT modularization and linked service ownership.
- G40 APTOVEC resolved to BCPLAPT; G85/86 byte services to BCPLBYTE; G87/88 vector allocation to BCPLMEM; stream and PARM services to BCPLIO; BLIB remains a compiled BCPL object. BCPLMAIN coordinates MVS entry, global/vector registration, startup and shutdown; retains provisional DEBUGINT/WRITEST and system-vector logic.
- 124-case regression acceptance establishes coverage of those test contracts, *not* historical binary compatibility, all MVS I/O variants, complete STAE/SPIE ABORT/BACKTRACE/MAPSTORE, reentrancy or exhaustive register preservation.
- Gate E prologue changes were comment-only; the MVS compiler/link-editor rebuilt them with zero RC and isolated DEVOBJ members. A new execution panel is needed only to confirm the refreshed installed object set.
- No production `HERC02.BCPL.OBJ` promotion belongs to Gate F. Git-tracked assembler and documentation are authoritative; MVS object libraries are derived build state.

## Gate F closure checklist

- [x] Gates A–E decisions and documentary evidence linked.
- [x] DEVOBJ(BCPLM6) assembled and integrated; separate modules verified.
- [x] Source/ownership/XREF and M1.9 behavioral scope compared.
- [x] Gate E comment-only rebuild and IEWL success recorded.
- [x] Post-Gate-E DEVOBJ(BCPLM6) smoke test 00 PASS.
- [x] Post-Gate-E DEVOBJ(BCPLM6) complete 00–123 panel: 123 PASS / 0 FAIL / 1 expected SKIP.
- [x] Record explicit Gate F and March M2.0 closure decisions with final operator evidence.

**Superseded by the verified final execution and closure decision below.**

## Final operator execution and formal acceptance — 14 October 2026

The operator updated their Git checkout through commit `2401259` and ran both commands with **all four candidate selectors**: `BCPL_RUNTIME_PDS=1`, `BCPL_RUNTIME_LIBRARY=DEVOBJ`, `BCPL_RUNTIME_CANDIDATE=1`, and `BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6`.

- Post-Gate-E smoke regression **00 PASS**, standalone summary **1 PASS / 0 FAIL / 0 SKIP / 1 TOTAL**.
- Post-Gate-E full installed DEVOBJ regression **00..123**: **123 PASS / 0 FAIL / 1 SKIP / 124 TOTAL**. Exactly regression **083** skipped with stated reason `source-only instrumentation`. All remaining tests were individually listed PASS, including 120–123.
- This is **new post-rebuild execution evidence**, not the earlier D6 full-panel run. The three independent rebuilt DEVOBJ modules (JOBs 2722, 2725, 2728) and IEWL integrated linkage (JOB 2731) had already completed RC=0000, all assembler statements unflagged.

### Acceptance decision

**Gate F ACCEPTED AND CLOSED. March M2.0 — Runtime Modularity and Maintainability — ACCEPTED AND CLOSED, 14 October 2026.** All six charter gates A–F are closed; independent BCPLAPT, BCPLBYTE, BCPLMEM and BCPLIO ownership has been demonstrated at the tested ABI boundary. BCPLMAIN D6 (DEVOBJ member BCPLM6) remains the accepted development candidate. MVS system-level historical completeness, reentrancy, full Cambridge compatibility and additional stack/diagnostic extraction were not included in this march and are neither accepted nor required for closure. The production binary object PDS `HERC02.BCPL.OBJ` was **not promoted or modified** by Gate F.
