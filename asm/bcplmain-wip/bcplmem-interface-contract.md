# BCPLMEM private allocator boundary — Checkpoint 1

Status: **proposed interface only; no executable transformation, JCL or public ABI change**. Baseline: operator-verified 120/120 native regressions with `BCPLAPT_OBJECT=1 BCPLBYTE_OBJECT=1` at commit `5e69214`, subsequently recorded at `5d71a0f`.

## Verified current-source facts

Current authority: `asm/bcplmain-wip/10-bootstrap-and-system.asmfrag`, `20-streams-and-services.asmfrag`, `30-control-data-and-end.asmfrag`. This document describes observed WIP behavior, not an independently proven historical BCPLMAIN.

* Startup publishes the addresses of `GETVEC` and `FREEVEC` at byte displacements 348 and 352 in the BCPL global vector (G87/G88). It obtains a **separate** global/stack allocation through `GETMAIN EC`, keeping `DYNLEN` and `DYNBASE` in BCPLMAIN.
* `GETVEC(N)` accepts N in R7 and allocates **N+1 BCPL words**, plus a private **12-byte header**. It rejects negative N, N greater than 4194299, and conditional `GETMAIN EC` failure, returning BCPL zero. Each allocated header contains at offsets +0 the returned **word pointer**, +4 the total **byte length**, and +8 the next header's **byte address**.
* `FREEVEC(V)` scans the list for a matching word pointer; unlinks the record **before** issuing `FREEMAIN R`. A zero or unknown V currently does nothing. This is WIP behavior, not historical error-semantics evidence.
* `VECLIST` is a static **byte-address** header-list head. `GVRMAX GVRLEN GVRADDR GVRSAVE GVRPSAVE GVRLSAVE GVRWSAVE FVRSAVE FVPSAVE FVLSAVE FVWSAVE` are singleton static allocator fields.
* `RELMEM` is called by `FINIMPL/STOPENT` after stream flush/close, and also by selected startup/error exits. It currently detaches each `VECLIST` head, frees the corresponding vector allocation, then releases `DYNBASE` using `DYNLEN` and clears `DYNBASE`.
* The allocation primitives save R0–R3, P=R5, L=R6 and W=R15 across MVS services; restore caller R4 from `0(R5)` before returning through R6. These are BCPL machine-routine conventions, **not standard MVS CALL linkage**.

## Proposed ownership and private interface

| Ownership | BCPLMEM (new independent CSECT) | BCPLMAIN (remains coordinator) |
|---|---|---|
| Public BCPL entries | `GETVEC`, `FREEVEC` installed at G87/G88 | installs relocated addresses in G |
| Allocator state | `VECLIST`, all GVR*/FVR* fields | no raw access to allocator state |
| Heap/vector MVS service | GETMAIN EC, FREEMAIN R per vector | neither walks nor frees vector records |
| Global vector and stack | none | `DYNBASE`, `DYNLEN`, `DYNWORK`, `DYNEND`, `STKLIM` |
| Exit control | proposed `MEMDRAIN` private assembler entry | calls `MEMDRAIN`, then frees its own global/stack allocation |
| Streams, DCBs, STOP RC, save areas | none | FINISH/STOP close/flush ordering and MVS return |

### Proposed private contract: MEMDRAIN

* **Meaning:** synchronously free every allocation still held by BCPLMEM; make its list empty. Does **not** free `DYNBASE` or close streams.
* **Calling sequence:** BCPLMAIN performs a direct `BAL 14,MEMDRAIN` (or equivalent external-address load and `BALR` after real linkage testing). R14 is the return address, **not** the BCPL-generated procedure-linkage R6.
* **Inputs:** none; only BCPLMEM-private state. **Output:** returns to the instruction following the call after its own vector list is empty. No BCPL result in R7 is defined.
* **Initial preservation requirement:** preserve R13 (private MVS save-area chain), R11/R12 (S/G bases) and the BCPL permanent R0–R3. The implementation must preserve or explicitly document all other registers observed live at the BCPLMAIN call site; unlike GETVEC/FREEVEC, this call executes in an MVS termination context. Preserve the R14 return address across FREEMAIN. Do not assume the macro leaves R14 intact.
* **State ordering:** detach the list head **before** freeing the allocation; do not dereference released storage. Once done, set/retain `VECLIST=0`. Make an empty-list call a no-op (idempotent only while the same runtime instance remains valid).
* **Failure/reporting:** no new status contract is proposed until the MVS FREEMAIN result/error policy is established. Do not silently change STOP return code. MVS abend handling and recovery are outside this extraction.
* **Scope:** singleton WIP module, explicitly **non-reentrant and not task-safe**. A reentrant or multi-instance production allocator will require per-instance state or a runtime context pointer; moving singleton data into a different CSECT is not sufficient.

### Proposed BCPLMAIN teardown sequence

```text
FINISH / STOP / selected bootstrap error
  1. BCPLMAIN finishes buffered output and closes applicable DCBs
  2. BCPLMAIN invokes BCPLMEM.MEMDRAIN
  3. BCPLMAIN frees DYNBASE using DYNLEN (only if allocated)
  4. BCPLMAIN restores the MVS save-area linkage and exits
```

**Important:** bootstrap paths may invoke reclamation before START. `MEMDRAIN` must tolerate a not-yet-used allocator. `GNOCORE` is an exception: it exits without calling `RELMEM` because the primary allocation failed.

## Extraction plan and acceptance gates

1. Introduce `tools/checks/bcplmem-linkage-probe.asm` as an independent BCPLMEM source **without changing canonical BCPLMAIN**, carrying GETVEC, FREEVEC, all private state and MEMDRAIN.
2. Implement a fail-closed, opt-in transformation of a **disposable combined assembler file**: remove original GETVEC/FREEVEC bodies, remove allocator-only static fields, import `GETVEC,FREEVEC,MEMDRAIN`, install relocated G87/G88 addresses, and replace only the vector-drain portion of RELMEM. Retain BCPLMAIN's own global/stack FREEMAIN and exit/save-area logic. Verify there are no duplicate definitions or residual references to removed private symbols.
3. First TK5 two-object tests: regressions 027–030 (basic allocation/release/failure), 039 (storage release), 082 (outstanding allocations at termination), 083 (instrumented reclamation), 088 (STOP with outstanding vectors). Use ESD/XREF evidence for two-directional control references and zero IFOX/IEWL errors.
4. Then add `BCPLMEM_OBJECT=1` to the runner, with coexistence with `BCPLAPT_OBJECT=1`, `BCPLBYTE_OBJECT=1`, native third-party routines, and the existing **BLIB PDS** flow. No auto-promotion to default.
5. Full acceptance: combined option mode passes all **120/120** native regressions and externally linked allocators are verified by linker cross-reference and execution. Re-run baseline if any canonical source must ever change.

## Deliberate open questions before implementation

* Does `MEMDRAIN` need to preserve R15 and R6 at the termination call site, or can it use documented scratch registers? Prove this by inspecting every caller and generated MVS macro expansion.
* Can a standalone BCPLMEM use a private base register across GETMAIN/FREEMAIN without corrupting BCPL permanent registers or R14/R15? Demonstrate through actual IFOX listing.
* The current allocator is static and singleton. Decide whether to retain this limitation through extraction (recommended for the bounded march) or defer until a per-invocation control block exists.
* Distinguish the proven normal FREEMAIN path from invalid-pointer and MVS-service-failure behaviors, which remain provisional.

**Decision for this checkpoint:** approve the interface as a *testable proposal*, not implementation proof. Leave all executable code and the default and opt-in regression runners unchanged pending a separate, reviewed BCPLMEM proof.

## Checkpoint 2: isolated two-object experiment staged (not yet validated)

Added experimental sources under `tools/checks/`:

* `bcplmem-linkage-probe.asm`: independent `BCPLMEM` CSECT exporting `GETVEC`, `FREEVEC` and `MEMDRAIN`. Owns all private `GVR*/FVR*` fields and `VECLIST`. The allocator is still intentionally singleton/non-reentrant.
* `externalize-bcplmem.py`: guarded transformation of a *disposable* generated/runtime assembler copy. Installs external G87/G88 routine addresses, replaces RELMEM's vector-list loop with a private MEMDRAIN call, and leaves BCPLMAIN's `DYNBASE` teardown intact.
* `prepare-bcplmem-runtime-probe.py`: generates independent IFOX assembly and IEWL JCL from an already generated `workarea/native-regression/<case>/native-test.asm` for cases 027–032, 039, 082 and 088.

The current experiment intentionally excludes regression **083**, whose existing runtime instrumentation directly edits the `RELMEM` vector-loop and counts FREEMAIN operations. That instrumentation will need a module-aware interface before it can become an external-BCPLMEM acceptance test. The opt-in full runner has not been modified.

**Next live gate (operator TK5):**

```sh
git pull --ff-only
tools/run-native-regression 27 --show-output
python3 tools/checks/prepare-bcplmem-runtime-probe.py 27
bash tools/submit-jcl \
  workarea/native-regression/27-getvec/bcplmem-object-probe/bcplmem-object-probe.jcl
```

Inspect with `tools/job-summary JOBNUMBER` and `tools/dump-report-for-job JOBNUMBER`. Expect `ASMBCPL`, `ASMNAT`, `LKED`, `GO` each RC=0000 and the same BCPL output as canonical regression 027. **This expectation is unverified** until the real IFOX/IEWL/SYSOUT report is examined. Stop and diagnose any failure; do not run other extracted-object cases automatically.

This checkpoint is a *staged experiment*, not confirmation of BCPLMEM linkage or completed extraction. The prior combined 120/120 suite remains the accepted baseline.

## Checkpoint 2a: JOB 6275 first assembler failure and narrow correction

Operator ran canonical regression 027 (PASS 1/1), prepared the isolated
BCPLMEM object job, and submitted **MM027R JOB 6275**. ASMBCPL returned
**RC=0008** (IFOX flagged exactly one error, statement 1049 `IFO209
ADDRESSABILITY ERROR` at `L 1,=A(MEMDRAIN)`). JES bypassed ASMNAT,
LKED and GO; consequently no BCPLMEM object execution has yet been
validated. The ESD did report imported `GETVEC`, `FREEVEC`, and
`MEMDRAIN`, so this is not evidence of a missing EXTRN declaration.

The assembler placed `=A(MEMDRAIN)` at the *final* literal pool,
unreachable by R11's system-vector base when `RELMEM` executes.
Commit `bc0f3aa` changes **only the disposable extraction generator**:
insert `LTORG` immediately after the `RELDONE` return so the literal
is addressable from RELMEM, without modifying canonical BCPLMAIN,
the standalone BCPLMEM assembler object, or the normal regression runner.

Next gate: repeat 027 prepare/submit on TK5 and require four zero
return codes, correct runtime output and external-reference resolution.
Do not claim a pass until the operator supplies execution evidence.

## Checkpoint 2b: JOB 6276 was stale after failed preparation

Operator pulled through `2c48ca2`, then
`prepare-bcplmem-runtime-probe.py 27` **failed**:
`externalize-bcplmem: expected one anchor 'RELDONE ... \\n ...'; got 0`.
The previous patch mistakenly used escaped `\\n` characters in a Python
string-match expression instead of linefeed escapes. Nevertheless the
operator manually submitted the preexisting `bcplmem-object-probe.jcl`,
producing **MM027R JOB 6276**, whose ASMBCPL RC=0008 and
unchanged `L 1,=A(MEMDRAIN)` IFOX addressability failure are **the
old deck again**, not a fresh assessment of the proposed LTORG remedy.

Commits `6e5bd20` and `41d7f28` correct both match and emitted
newlines. Commit `8bece33` invalidates any old JCL and transformed
assembler **before** regenerating; a failed preparation can no longer
leave those stale outputs as eligible submission artifacts.

Repeat after `git pull --ff-only`; only submit if the generator prints
`Prepared:` successfully. No BCPLMEM IFOX/IEWL/GO success has yet
been demonstrated. Maintain the accepted default and combined-object
120/120 baseline.

## Checkpoint 2c: JOB 6277 accepted — first independent BCPLMEM execution

Operator evidence from **MM027R JOB 6277** on TK5 (11 Oct 2026, machine-local job date), after pulling through `e849d5d`. Python source compilation and both assembler source preflights succeeded; standalone preparation reported a newly written deck (so this run does not reuse the stale JOB 6275/6276 JCL).

| Step | Program | Result |
|---|---|---|
| ASMBCPL | IFOX00 | RC=0000 |
| ASMNAT | IFOX00 | RC=0000 |
| LKED | IEWL | RC=0000 |
| GO | load module | RC=0000 |

The operator-supplied complete IEWL cross-reference shows **BCPLMAIN at X'0090'**, **BCPLMEM at X'1410'**, exports `GETVEC=X'1410'`, `FREEVEC=X'14B0'`, `MEMDRAIN=X'1536'`; the imported addresses at the application/runtime's X'0304', X'0308' and X'0478' are resolved to those BCPLMEM exports. Both assembler outputs report zero flagged statements and IFOX severity zero. GO writes `42` and returns RC=0000.

**Acceptance scope:** first separately assembled/link-edited BCPLMEM GETVEC and private cleanup invocation with one live vector remaining at FINISH (regression 027), including BCPLMAIN's retained DYNBASE teardown. This is strong linkage and smoke-test evidence, but not yet proof of explicit FREEVEC operation, multi-node allocation-list manipulation, or STOP/FINISH cleanup with several live nodes. Canonical BCPLMAIN and runner unchanged.

Next isolated sequence: 028 (FREEVEC), 029 (multiple allocations), 039 (storage release), 082 (outstanding allocations), 088 (STOP with outstanding allocations), with per-job ASMs/LKED/GO evidence before integration. Regression 083's instrumentation requires special module-aware adaptation.
