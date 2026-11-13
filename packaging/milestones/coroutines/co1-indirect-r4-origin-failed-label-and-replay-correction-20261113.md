# CO.1 — Indirect R4 origin: failed label oracle and saved-MVS-evidence correction

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture
**Recorded:** 13 November 2026 (Louisville)
**Owner's guarded execution revision:** `34947dd2e8bc61faa6aaee0a2804835d144e48e7`
**Result category:** OWNER-REPORTED MVS COMPILER-ONLY PROBE, **TARGET AUDIT FAIL**; no native GO evidence
**Status:** CO.1 IN PROGRESS; owner design gate OPEN; CO.2–CO.5 NOT STARTED

## Reported failure and evidence

The owner invoked the guarded command for the [first R4 indirect-target audit](co1-indirect-r4-origin-compiler-audit-preparation-20261113.md) and reported:

```text
CO.1 TARGET FAIL: expected exactly one ENTRY TO CALLIND, found 0
CO.1 TARGET evidence: workarea/co1-indirect-entry/20261113T123939Z-u8ft6blz
CO.1 indirect-target compile-only RC=1
```

**Retained owner-host evidence:** `workarea/co1-indirect-entry/20261113T123939Z-u8ft6blz/`.

The versioned wrapper at this revision does not invoke `audit_indirect_target` unless the existing `probe-co1-indirect-entry.py` has already returned RC=0, its structural compiler PASS matches its `summary.json`, and it has recovered nonempty textual assembler. Thus the reported failure is **in the additional label-dependent target audit**, not a demonstrated Cambridge compiler failure or new regression. The output does not disclose the actual JES job number, nor the saved source listing, frame sizes or individual JES-step outcomes; none is inferred.

The auditor assumed a single line matching `Lnn EQU * ENTRY TO CALLIND`. It found zero matches. **The exact listing presentation is not independently known** because the local `generated.s370.asm` and `target-probe.log` have not been supplied for examination. Potential name wrapping, omitted annotation, whitespace, or another emitted format cannot be distinguished from the console message alone.

## Repair: structural procedure identification, no new BCPL compilation necessary

The source-reviewed `CGSAVE` emits an `STM 4,9,0(15)` prologue for the fixture's only three-formal procedure, immediately followed under `/CN` by a +60 checked entry and inline frame-size fullword. The existing first-stage probe already requires exactly one such `STM` in its recovered listing. The revised **fail-closed** `co1-indirect-target-audit.py` now uses this machine-code prologue as its identifier rather than requiring a particular human-readable `ENTRY TO CALLIND` heading.

Within the candidate procedure, the revised audit requires the adjacent checked entry, exactly one normal `BCR 15,11` return before any later procedure prologue, exactly one `BALR 6,4`, and a nearby unambiguous final definition of R4 from `12(R5)` (first formal `F=P!3`) or from R7 (only if unchanged since entry). It rejects intervening branches, multi-register loads, register clobbers and unrecognized forms. A named heading, when present, is *supplemental* metadata only. A valid different code-generator sequence may still fail this deliberately narrow oracle; such a FAIL is not automatically a compiler defect.

The revised `tools/bootstrap/probe-co1-indirect-target.py` adds `--reuse-evidence` to inspect the **existing** MVS-generated `generated.s370.asm` and original `target-probe.log`, reconcile the original compiler-only PASS with `summary.json`, and validate source/option hashes against tracked fixtures. This option performs **no JES submission**, **no IFOX**, **no IEWL**, and **no native GO**. It leaves the original failed `target-audit.json` intact and writes a separate `target-audit-v2.json` in the same existing evidence directory. Default invocation without this option remains a fresh compile-only MVS job.

## Assistant-host checks, not owner-host checks

The assistant tested the revised code in a separate temporary workspace: **36/36 Python unit tests PASS**, Python syntax checks PASS, and a synthetic saved-evidence replay PASS. Tests include the name-marker absence, wrong/missing prologues, return/call scoping, changed R7, wrong R4 offsets and values, branches/LM, path-traversal rejection, compiler-summary mismatches, and preservation of the prior failure record. The local synthetic JOB **8125 is NOT a JES job**. The source/option fixture hashes match the tracked GitHub blobs; no local owner files or MVS datasets were accessed.

**Next evidence:** replay `workarea/co1-indirect-entry/20261113T123939Z-u8ft6blz` via the guarded MVS-evidence command, without repeating compilation. Even if the revised audit passes, that establishes only the recognized *emitted R4 instruction*, not actual native procedure-pointer execution or coroutine first activation.

The [first-activation frame review](co1-first-activation-return-frame-and-indirect-call-investigation-20261113.md), E1/E2 interface, descriptor layout, full register/PSW save set, S1 `STKLIM` and `APLIMIT` coordination, G54/G55 diagnostic choice and all CO.2 gates remain unapproved.

**CO.1 IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED.**
