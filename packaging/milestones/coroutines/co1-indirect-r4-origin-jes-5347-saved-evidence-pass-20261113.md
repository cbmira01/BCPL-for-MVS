# CO.1 — JOB 5347: indirect R4 origin, saved MVS compiler evidence PASS

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture
**Recorded:** 13 November 2026 (Louisville)
**Original compiler execution revision:** `34947dd2e8bc61faa6aaee0a2804835d144e48e7`
**Corrected saved-evidence audit revision:** `6adc9d1d1e133beb05847d7f43d96d6caa1fab66`
**Classification:** OWNER-REPORTED REAL MVS COMPILER EVIDENCE, REAUDITED LOCALLY BY OWNER; original generated assembler and JES records not independently inspected
**Result:** R4 indirect-target textual audit PASS, RC=0; **no new JES job submitted**
**Status:** CO.1 IN PROGRESS; owner design gate OPEN; CO.2–CO.5 NOT STARTED

## Owner-reported replay receipt

Following the [failed label-dependent audit and its corrected replay plan](co1-indirect-r4-origin-failed-label-and-replay-correction-20261113.md), the owner ran the guarded `--reuse-evidence` command after pulling and checking the exact new GitHub HEAD `6adc9d1d1e133beb05847d7f43d96d6caa1fab66`.

The owner provided:

```text
CO.1 TARGET PASS: JOB 5347, R4 from P!3 first formal F at 12(R5); saved MVS compiler evidence; no new JES
CO.1 TARGET evidence: workarea/co1-indirect-entry/20261113T123939Z-u8ft6blz
CO.1 saved-MVS-evidence audit RC=0
```

This **identifies JOB 5347** as the earlier original compiler job whose evidence was retained in `workarea/co1-indirect-entry/20261113T123939Z-u8ft6blz/`. The failed first audit did not print the JOB ID, so its number was previously deliberately left unknown. The successful replay is **not a second JES job**.

The versioned replay reads `target-probe.log`, `summary.json` and `generated.s370.asm` from that directory. It cross-checks the recorded structural compiler PASS, JOB, compiler driver RC=0, source/parameter fixture SHA-256 values, and the non-execution flags. It then runs the corrected source-only target audit and writes `target-audit-v2.json`, retaining the earlier `target-audit.json` failure report unchanged by design. The local files were not supplied for independent examination; the quoted result is the owner-reported result of the checked-in audit, not an independent reading of those files.

## Established scope of the emitted-code evidence

The corrected `tools/bootstrap/co1-indirect-target-audit.py` identifies the unique three-formal `STM 4,9,0(15)` checked prologue without requiring a source-name annotation such as `ENTRY TO CALLIND`. Within the bounded procedure body, it demands the matching +60 checked entry, one ordinary `BALR 6,4` call, a normal `BCR 15,11` return, and a narrowly recognized final R4 definition attributable to the first formal `F`.

The printed origin `P!3 first formal F at 12(R5)` is generated only by the audit's saved-formal branch matching an `L 4,12(5)` instruction. Thus **the versioned audit reports a compiler-emitted load of F from the current BCPL frame into R4 before the indirect call**. It is stronger than the earlier structural JOB 5346 probe, but the actual assembler line was not separately pasted or independently inspected in this conversation.

**Not established:** IFOX assembly, IEWL linkage, native GO, execution of the function-pointer call or its expected numerical result, preservation of all live registers across a native coroutine switch, synthetic worker first activation, stack switching, or actual `CHANGECO` behavior. The saved-evidence replay does not repair or execute the native runtime and does not authorize MVS dataset or object promotion.

## Disposition

The previous `expected exactly one ENTRY TO CALLIND, found 0` **audit failure** is resolved for this saved compiler listing by the corrected structural audit, without rewriting the original failed receipt. The exact reason the name annotation was absent remains unknown without inspection of the retained assembler; do not state it as a historical compiler defect.

The [original R4 audit preparation](co1-indirect-r4-origin-compiler-audit-preparation-20261113.md) and [first-activation frame investigation](co1-first-activation-return-frame-and-indirect-call-investigation-20261113.md) remain applicable with these evidence boundaries. CO.1 still requires owner review of E1/E2, synthetic worker frame, R6 exit continuation, complete save/restore and condition-code policy, and S1 coordination of `STKLIM` with `BCPLAPT APLIMIT` before CO.2.

**CO.1 IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED.**
