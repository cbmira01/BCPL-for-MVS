# M2.1 Gate B — Termination and Failure Semantics

**Status: OPEN — 14 October 2026.** Predecessor Gate A accepted/closed, per `m2-1-gate-a-contract-reconciliation.md`.

## Objective and bounds

Determine whether the accepted D6 candidate has an actionable mismatch between programmer-visible failure messages, MVS completion codes and resource cleanup. Start with **evidence only**; modify assembler only after a narrow policy/test decision. Preserve M2.0 modular architecture and existing production `HERC02.BCPL.OBJ`.

## Accepted executable baseline

`asm/bcplmain-d6-candidate.asm` -> DEVOBJ(BCPLM6), alongside independent BCPLIO, BCPLMEM, BCPLBYTE, BCPLAPT and BLIB. M2.0 final DEVOBJ execution: **123 PASS / 0 FAIL / 1 expected SKIP 083** (00–123). Compilation and link-edit acceptance: JOBs 2722, 2725, 2728 (IF​OX/IEBGENER RC=0000) and JOB 2731 (IEWL RC=0000).

## Source-derived exit map (not new execution evidence)

| Condition | Source path in D6 | Completion and cleanup | Assessment |
| --- | --- | --- | --- |
| FINISH via system vector +40 | `FINIMPL` clears STOPRC, `FINEXIT` invokes `IOFIN`, then `RELMEM` | RC=0, closes output/input, MEMDRAIN, MEMBIND(0), FREEMAIN | Existing intended normal behavior |
| STOP(N) G30 | `STOPENT` stores R7 to STOPRC, falls through FINEXIT | RC=N; same orderly cleanup | Existing intended explicit termination |
| BCPLIO record overflow | `IOSTOP` sets R7=12 and branches STOPENT | RC=12; orderly cleanup | Existing intended controlled failure |
| Stack overflow (checked frame / BCPLAPT limit) | `STKOVFL` calls private `IOREPL` then branches `FINIMPL` | **RC=0**, IOFIN and RELMEM; diagnostic `STACK OVERFLOW`; previous buffered default output replaced | **Proven by source**; likely incorrect success signal but policy not yet accepted |
| Malformed checked-entry frame metadata | `STKFORM` branches directly to MVS return | RC=36; bypasses IOFIN and RELMEM | Distinct issue, requires safe-path analysis before any change |
| Oversize global import | `GTOOBIG` -> RELMEM -> MVS return | RC=16, no IOFIN | Mostly pre-initialization failure |
| Missing START | `NOSTART` -> RELMEM -> MVS return | RC=20, no IOFIN | Mostly pre-initialization failure |
| Initial main GETMAIN failure | `GNOCORE` -> MVS return | RC=24, no main allocation to free | Appropriate early failure boundary |
| Unexpected START return | `BADRETN` -> RELMEM -> MVS return | RC=36, IOFIN bypassed | Rare control-flow failure, evaluate consequences |

## Focused executable baseline probe

The existing `native-compiler/regression/093-aptovec-stack-overflow/` case already triggers the independent G40 limit and asserts the diagnostic text `STACK OVERFLOW` without reaching its `DEBUGINT(999)` callee. Its dated README says it expects **GO RC=0000**; therefore it is historical evidence of the current behavior, not a policy specification for future nonzero status.

Current `native-compiler/regression/run-test.sh` uses `tools/job-summary` to distinguish completed GO status; its `expected-go-rc.txt` fixture only participates in the *nonzero failure* branch (RC=1 from job-summary). Merely adding an RC=0000 fixture to regression 093 would **not** assert RC=0. Instead capture the actual step summary from the baseline D6 candidate, including the GO RC and diagnostic.

Operator command (no rebuild or object changes):

```sh
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/run-native-regression 93 --show-output
```

Acceptance of the **baseline probe** requires `STACK OVERFLOW`, absence of `999`, successful compile/link steps, and explicit recorded `GO RC=0000`. If RC differs, investigate resident build selection and report; do not edit code reflexively.

## Proposed decision after baseline probe

Recommend simple programmer/MVS policy: stack exhaustion is a failed execution and should retain the historical diagnostic but return a **defined nonzero GO completion**, tentatively RC=12, through the existing `FINEXIT` cleanup path. RC=12 would match another controlled capacity failure but is only a candidate; ensure historical and regression compatibility before adoption. The minimal prospective change would be a shared STOPRC-setting branch from STKOVFL, **not** a new recovery framework. Test both the checked-frame and APTOVEC paths if practicable.

Evaluate `STKFORM` separately. Jumping from its corrupted-frame context into ordinary FINEXIT might be unsafe; do not assume that full cleanup is always possible. Similarly, pre-IOINIT GTOOBIG/NOSTART do not automatically need IOFIN. Prefer documenting sensible early-exit behavior rather than wholesale refactoring.

## Follow-on acceptance criteria

- [x] Gate A accepted; D6 baseline and production boundary established.
- [x] Source-derived normal and abnormal termination path map.
- [x] Reuse existing 093 baseline rather than inventing a redundant test.
- [ ] Capture actual D6 candidate 093 GO step RC and diagnostic in owner-supplied JES output.
- [ ] Decide exact STKOVFL completion-code policy and whether a targeted code/test change is justified.
- [ ] If changed, implement only against a distinct DEVOBJ candidate, assemble/link it, and add RC assertion while preserving the diagnostic and no-999 check.
- [ ] Independently verify both tested failure mechanism and normal STOP/FINISH semantics; run full 00–123 candidate suite before subsequent acceptance.
- [ ] Record owner acceptance and close Gate B; defer unrelated historical compiler features to Gate C.

**No assembler code, regression fixture or resident MVS dataset has been changed by opening Gate B.**
