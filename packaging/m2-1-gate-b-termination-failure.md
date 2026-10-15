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

Current `native-compiler/regression/run-test.sh` uses `tools/mvs/job-summary` to distinguish completed GO status; its `expected-go-rc.txt` fixture only participates in the *nonzero failure* branch (RC=1 from job-summary). Merely adding an RC=0000 fixture to regression 093 would **not** assert RC=0. Instead capture the actual step summary from the baseline D6 candidate, including the GO RC and diagnostic.

Operator command (no rebuild or object changes):

```sh
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 93 --show-output
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


## Baseline executable evidence — JOB 2983 (14 October 2026)

Owner executed with `BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6`:

```text
NATIVE REGRESSION 093..093: PASS 1, FAIL 0, SKIP 0
JOB 2983 RG093R
ASMAP IFOX00 RC=0000
LKED IEWL   RC=0000
GO   PGM=*.DD RC=0000
JOB RESULT: SUCCESS
Assembler: 0 statements flagged, highest severity 0
```

This **confirms actual GO RC=0000** on the accepted installed D6 stack-overflow path. The regression's `expected.txt` is `STACK OVERFLOW`; its passing result establishes that the diagnostic assertion succeeded and did not reach its `DEBUGINT(999)` callee. Do not call this a successful *application* termination: it is a successfully recognized failure condition masked as MVS success.

**Proposed Gate B policy for owner decision:** preserve message and orderly IOFIN/MEMDRAIN/FREEMAIN, but route STKOVFL through STOPENT with R7=12 rather than FINIMPL (which zeroes STOPRC). Recheck BCPLAPT and checked-frame callers and how their register context arrives at STKOVFL before making an instruction-level patch. Update regression 093 to assert `GO RC=0012` using supported `expected-go-rc.txt` fixture; make no speculative change to `run-test.sh`. This is a recommendation pending explicit semantic acceptance, not a committed assembler change.

**Status:** focused baseline evidence accepted; **Gate B OPEN**, completion code policy and changed-object execution still pending.


## Authorized D7 candidate — stack overflow RC=12 (14 October 2026)

The owner explicitly **approved RC=12 as the stack-overflow completion code**. The change has been implemented in a new Git-only **D7** candidate, not the accepted D6 source:

- `asm/bcplmain-d7-candidate.asm`: after `IOREPL` and restoring R10, `STKOVFL` now sets R7=12 and branches to existing `STOPENT`. This preserves `FINEXIT` IOFIN / MEMDRAIN / MEMBIND(0) / FREEMAIN and bypasses `FINIMPL`'s RC=0 reset. Shared checked-entry and BCPLAPT failures still converge on STKOVFL.
- `jcl/build-dev-bcplmain-d7.jcl`: assemble SOURCE(BCPLM7), binary-safe install DEVOBJ(BCPLM7) only.
- `jcl/bcplio-d7-integration-link.jcl`: D7 candidate linker MAP/XREF, without GO or production OBJ.
- `native-compiler/regression/093-aptovec-stack-overflow/expected-go-rc.txt`: now asserts GO RC=0012 using the existing run-test.sh fixture machinery, in addition to `expected.txt` diagnostic. **This deliberately makes test 093 fail against the old D6 RC=0000 until D7 is selected.**

**Pending execution:** these Git edits do not constitute assembled, linked or executed proof. Run this sequence after `git pull --ff-only` while MVS is available:

```sh
tools/datasets/dspal put SOURCE BCPLM7 asm/bcplmain-d7-candidate.asm
tools/datasets/dspal put JCL BLDD7MN jcl/build-dev-bcplmain-d7.jcl
tools/datasets/dspal put JCL D7LINK jcl/bcplio-d7-integration-link.jcl
tools/datasets/dspal submit JCL BLDD7MN
# Verify payload assembler and IEBGENER steps, both RC=0000.
tools/datasets/dspal submit JCL D7LINK
# Verify payload IEWL RC=0000 and distinct BCPLM7 object.
BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM7 \
tools/native/run-regression 93 --show-output
```

Then exercise normal STOP/FINISH and a checked-frame overflow (where independently testable), and rerun full 00–123 against selected DEVOBJ(BCPLM7). **No MVS jobs or tests are claimed executed by this commit.** A documented focused pass and full panel are acceptance requirements.

## M2.1 return-code registry decision

Maintain a versioned **completion and failure code register** as part of the native runtime contract, consolidating all runtime-generated R15 completion values and deliberate `STOP(N)` user codes, with ownership, triggering condition, message, cleanup path, evidence level and historical/MVS provenance. **Do not confuse** an MVS step RC with system/user ABEND codes or assembler/link-editor return codes. Begin with this Gate B table; stabilize the consolidated registry no later than M2.1 Gate F. The register is documentary, not a claim that every possible `STOP(N)` value is reserved.

**Historical note:** this statement describes the pre-test state; see final Gate B acceptance below.


## D7 resident build and linkage evidence — 14 October 2026

Operator synchronized Git through a4e4ee8 and staged:
- JOB 2984: SOURCE(BCPLM7) from asm/bcplmain-d7-candidate.asm — successful.
- JOB 2985: JCL(BLDD7MN) — successful.
- JOB 2986: JCL(D7LINK) — successful.
- Payload JOB **2989 BLDD7MN**: ASMMMAIN IFOX00 RC=0000; PUTMAIN IEBGENER RC=0000; zero flagged assembler statements, severity 0.
- Payload JOB **2992 D7LINK**: LKED IEWL RC=0000.

These prove assembled/installed DEVOBJ(BCPLM7) and successful integration link-edit. No D7 GO has yet been reported. Proceed to focused regression 093 against BCPLM7 (expect STACK OVERFLOW and GO RC=0012), followed by normal FINISH/STOP cases and full panel before Gate B closure. Stable BCPLM6 and production OBJ remain outside the write targets.

## D7 regression harness block and correction — 14 October 2026

Owner attempted D7 candidate regression 093 after successful D7 assembly/link. Compiler payload JOB **2993 RG093C** completed ICINT19 COMP RC=0000 and SVCODE IEBGENER RC=0000, but the host regression builder rejected BCPLM7 **before the native assembler/link/GO job was submitted**, reporting `candidate member must be BCPLM3, BCPLM4, BCPLM5 or BCPLM6`. No D7 runtime failure or GO result is implied.

Cause: `tools/checks/prepare-runtime-pds-regression.py` contained the outdated candidate allowlist. Commit `f643f6b` extends it to BCPLM7 while retaining DEVOBJ-only candidate restrictions and explicit opt-in. Next action: rerun 093 against DEVOBJ(BCPLM7); check returned GO RC=0012 and diagnostic. No resident source/object rebuild is needed.

## D7 focused execution acceptance — 14 October 2026

Owner synchronized commit 124e9d7 and ran native regression 093 with `BCPL_RUNTIME_PDS=1`, `BCPL_RUNTIME_LIBRARY=DEVOBJ`, `BCPL_RUNTIME_CANDIDATE=1`, `BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM7`. Report: `PASS 093 093-aptovec-stack-overflow`, panel 1 PASS / 0 FAIL / 0 SKIP. Current test fixture `expected-go-rc.txt` requires `0012` and `expected.txt` requires `STACK OVERFLOW`; the passing harness therefore demonstrates both via its recorded test criteria (though no step-by-step job summary was supplied in this run). The earlier D7 assembly/install payload JOB 2989 and link payload JOB 2992 were RC=0000. **Focused D7 behavior accepted as evidenced.** Gate B remains open pending ordinary STOP/FINISH checks, full candidate regression, and owner gate closure.


## Full D7 panel — first pass; expected-contract discrepancy in test 52

The owner ran the full 00–123 panel with DEVOBJ(BCPLM7). Results: **122 PASS, 1 FAIL (052), 1 expected SKIP (083)**, 124 total. Normal FINISH and STOP regressions 084–089 **all passed**, as did regression 093's newly required RC=0012.

The single failing case, **052 controlled stack overflow**, demonstrated a *correct D7 runtime result*: payload JOB **3101 RG052R**, ASMAP IFOX00 RC=0000, LKED IEWL RC=0000, **GO RC=0012**; the `STACK OVERFLOW` output matched. It was classified FAIL because fixture 052 had not yet acquired `expected-go-rc.txt` and its README described the older D6 success-completion contract. Test 093 already verifies the same new policy via the fixture mechanism.

Git-only remedy:
- `native-compiler/regression/52-controlled-stack-overflow/expected-go-rc.txt`: `0012`.
- Test 052 README updated to distinguish D6 RC=0000 from D7 RC=0012 and record JOB 3101.

**This is a regression acceptance-contract update, not a new runtime code correction.** The first full D7 panel cannot be reported as 123 PASS; rerun 052 first and the full panel afterward before formal Gate B acceptance. D6 may no longer pass the updated 052 and 093 fixtures without an explicit baseline-specific fixture mechanism, which has not been introduced. Production OBJ and D6 remain unchanged.


## Final full D7 candidate regression — 14 October 2026

Owner executed `tools/native/run-regression` with `BCPL_RUNTIME_PDS=1`, `BCPL_RUNTIME_LIBRARY=DEVOBJ`, `BCPL_RUNTIME_CANDIDATE=1`, and `BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM7`, following the regression 052 fixture correction.

**Recorded result:** native regression 00–123, **123 PASS / 0 FAIL / 1 expected SKIP / 124 total**. SKIP 083 remains the planned source-instrumentation-only case. Both independent stack-overflow paths, **052 checked-frame** and **093 APTOVEC**, passed under the explicit GO RC=0012 fixture. Termination regressions **084–089** (FINISH and STOP, including nonzero and buffered exits) all passed. Regression 119, termination flushing both destinations, also passed. This matches the M2.0 aggregate baseline while enforcing the new RC=12 failure semantics.

Earlier build/link evidence remains payload JOB 2989 (IF​OX00 and IEBGENER RC=0000) and JOB 2992 (IEWL RC=0000); earlier checked-frame overflow payload JOB 3101 demonstrated GO RC=0012 and expected STACK OVERFLOW before its test fixture was corrected. No D7 assembler change was required after these jobs.

**Gate B engineering exit criteria satisfied:** focused failure diagnostics/completion code, both overflow entry paths, ordinary STOP/FINISH, and full native candidate panel are validated. Owner has not explicitly directed formal Gate B closure in this message; status remains **READY FOR OWNER ACCEPTANCE**, not automatically closed. No production promotion authorized.


## Formal Gate B closure — 14 October 2026

The owner subsequently directed **“Proceed Gate C”** following the reported final D7 full native regression. This constitutes acceptance of Gate B's bounded delivery and authorization to transition.

**ACCEPTED AND CLOSED:** D7 DEVOBJ(BCPLM7), stack exhaustion completion GO RC=0012 via STOPENT; IFOX/IEBGENER build JOB 2989 RC=0000; IEWL LINK JOB 2992 RC=0000; checked-frame 052 and APTOVEC 093 PASS with RC=0012; ordinary STOP/FINISH 084–089 PASS; full 00–123 panel **123 PASS, 0 FAIL, 1 expected SKIP (083)**. Earlier source-only audit qualifications for exceptional pre-init exits and historical language services are **not** claims of complete compatibility. No production OBJ promotion or rewrite of accepted D6 performed.

Gate C may now perform its separate historical compiler-runtime contract inquiry. Gate B is not reopened merely because Gate C identifies unsupported historical services.
