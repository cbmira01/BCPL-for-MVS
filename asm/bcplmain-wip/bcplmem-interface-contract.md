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

## Checkpoint 2d: JOB 6280 accepted — independent FREEVEC

Operator tested canonical regression **028-freevec** (PASS 1/1), generated a fresh isolated BCPLMEM two-object job, and executed **MM028R JOB 6280** (11 Oct 2026). Preflight checks each reported OK. ASMBCPL IFOX00, ASMNAT IFOX00, LKED IEWL and GO each returned **RC=0000**; both assembler steps reported no errors. The application printed **42**. The IEWL cross-reference identifies **BCPLMEM X'1458'**, with `GETVEC X'1458'`, `FREEVEC X'14F8'`, and `MEMDRAIN X'157E'`; the three BCPLMAIN external references resolve to this independent CSECT. Regression 028 calls GETVEC, FREEVEC, then GETVEC and FREEVEC again: this proves the external module's basic explicit release/reallocation behavior, not arbitrary linked-list stress or measured MVS storage reclamation.

**Next gate:** isolated regression 029 multiple allocations, then 039 storage release, 082 outstanding allocations at exit, and 088 STOP with outstanding allocations. Continue to defer 083's instrumentation adaptation. This entry records operator-supplied TK5 results; canonical runtime and runner remain unchanged.

## Checkpoint 2e: JOB 6283 accepted — multiple simultaneous allocations

On 11 Oct 2026, the operator reported canonical regression **029-multiple-allocations** PASS 1/1, successful preparation/preflight for the isolated two-object deck, and **MM029R JOB 6283** completed successfully. All four steps — ASMBCPL IFOX00, ASMNAT IFOX00, LKED IEWL, GO — returned **RC=0000**, with zero flagged assembler statements. IEWL identified separate CSECT **BCPLMEM at X'14E0'** (length X'01C4'), with exports `GETVEC=X'14E0'`, `FREEVEC=X'1580'`, and `MEMDRAIN=X'1606'`, referenced by BCPLMAIN at X'3D4', X'3D8', and X'548' respectively. Program output **424242** matched expectations.

Test 029 demonstrates a list containing several live vectors and both allocation and explicit release, with successful payload reads/writes. It is **not** yet a count of actual FREEMAIN calls at STOP/FINISH: that requires additional instrumentation (existing regression 083 is currently monolith-specific). This experimental object-only acceptance leaves canonical BCPLMAIN and standard runner unchanged.

Next gates: **039** (storage release), **082** (outstanding allocations at FINISH), **088** (STOP with outstanding allocations). Inspect each job before promoting runner integration.

## Checkpoint 2f: JOB 6286 accepted — storage-release regression 039

Operator report from 11 Oct 2026: canonical `tools/run-native-regression 39 --show-output` gave **PASS 1/1**. Preparation of the isolated two-object BCPLMEM experiment passed both assembler preflights, and `MM039R` **JOB 6286** completed **ASMBCPL IFOX00 RC=0000, ASMNAT IFOX00 RC=0000, LKED IEWL RC=0000, GO RC=0000**. IFOX flagged no assembler statements. IEWL cross-reference: **BCPLMEM X'1470'**, `GETVEC X'1470'`, `FREEVEC X'1510'`, `MEMDRAIN X'1596'`; external references from BCPLMAIN resolve at X'364', X'368', and X'4D8'. GO output: **42**. These are operator-supplied real-TK5 results.

Regression 039 validates free/reallocate behavior in the external BCPLMEM arrangement, including a 252-word vector, **but does not instrument or count actual MVS FREEMAIN calls**. This limitation is intentionally retained until a module-aware adaptation of regression 083.

Next focus: **082** (outstanding vectors at FINISH), followed by **088** (STOP with outstanding vectors). Do not enable BCPLMEM in the full runner until these gates and the instrumentation contract are addressed.

## Checkpoint 2g: JOB 6289 — FINISH with outstanding vectors

Operator evidence: canonical regression 082 PASS 1/1; isolated MM082R JOB 6289, ASMBCPL/ASMNAT/LKED/GO all RC=0000, output 42. IEWL placed BCPLMEM at X'1430', with GETVEC X'1430', FREEVEC X'14D0', MEMDRAIN X'1556'; references from BCPLMAIN were resolved. Two vectors remained live on FINISH. This validates successful termination through the external cleanup interface, but does not directly count FREEMAIN invocations or prove leak freedom. Next gate: test 088, STOP with outstanding allocations. Canonical source and runner remain unchanged.

## Checkpoint 2h: JOB 6292 — STOP with outstanding vectors

Operator evidence (11 October 2026): canonical regression 088 PASS 1/1; MM088R JOB 6292 assembled both objects (IFOX00 RC=0000 each), linked (IEWL RC=0000), and executed (GO RC=0000), printing 42. IEWL shows independent BCPLMEM at X'1438', exporting GETVEC at X'1438', FREEVEC at X'14D8', and MEMDRAIN at X'155E'. Both GETVEC-created vectors remained outstanding when STOP(0) was invoked. The listing shows STOPENT enters FINEXIT, followed by RELMEM calling external MEMDRAIN and BCPLMAIN freeing its own allocation. This is successful execution-path evidence, not direct FREEMAIN instrumentation. This closes the isolated functional 088 gate. Next: adapt regression 083 with module-aware reclamation counts, then consider opt-in runner integration. Canonical runtime and normal runner remain unchanged.

## Checkpoint 2i: external regression 083 instrumented deck staged

Experimental preparer: `tools/checks/prepare-bcplmem-083-probe.py`. It reads regression 083's generated `native-test.asm` only after the normal regression has been run. The normal regression deliberately instruments the *monolithic* RELLOOP; this preparer strictly reverses those five test-local changes **in a disposable copy**, invokes the existing BCPLMEM externalizer, and instruments the independent objects separately. It deletes older derived assembler sources and decks **before** attempting a new preparation; it does not edit `asm/bcplmain-wip.asm`, regression 083, or the normal runner.

The test-only `BCPLMEM` CSECT exports `MEMDCNT` and increments it **only after each FREEMAIN in MEMDRAIN returns**, not for the earlier explicit FREEVEC(B). The BCPLMAIN copy imports this counter, increments its own private `TRM083` after the global/stack FREEMAIN returns, and emits `V=2 M=1` after its normal `42` output. BCPOUT is kept open through the final record. This distinction protects separate CSECT ownership of the list and prevents conflation with explicit FREEVEC or main storage.

Execution gate (operator's TK5 environment):

```sh
git pull --ff-only
tools/run-native-regression 83 --show-output
python3 tools/checks/prepare-bcplmem-083-probe.py &&
bash tools/submit-jcl \
  workarea/native-regression/083-instrumented-storage-reclamation/bcplmem-object-probe/bcplmem-083-object-probe.jcl
```

Inspect job-summary and complete report. Expected: ASMBCPL, ASMNAT, LKED and GO each RC=0000; IEWL resolves GETVEC/FREEVEC/MEMDRAIN/MEMDCNT into the separately assembled BCPLMEM CSECT; GO writes **42** then **V=2 M=1**. Test evidence counts *returns from* FREEMAIN, not independent MVS storage manager validation. **Not yet executed** as of this preparation commit; do not claim acceptance before seeing job evidence.

## Checkpoint 2j: JOB 6295 accepted — module-aware FREEMAIN counts

Operator report, **11 October 2026**: canonical regression **083-instrumented-storage-reclamation** PASS 1/1. The dedicated external `prepare-bcplmem-083-probe.py` completed both assembler-source preflights and prepared a fresh `MM083R` JCL deck. **JOB 6295** completed `ASMBCPL` IFOX00 RC=0000, `ASMNAT` IFOX00 RC=0000, `LKED` IEWL RC=0000, and `GO` RC=0000, with zero assembler diagnostics. The two output records were exactly:

```text
42
V=2 M=1
```

The independent IEWL CSECT is **BCPLMEM X'14B0'**, length X'01D4', exporting `GETVEC X'14B0'`, `FREEVEC X'1550'`, `MEMDRAIN X'15D6'`, and test-only `MEMDCNT X'1680'`; all four external references from the BCPLMAIN copy resolve into that object. The test calls GETVEC three times, explicitly FREEVECs the middle allocation, then FINISHes with two live vector-list entries. `MEMDCNT` counts two *returned* FREEMAIN calls in MEMDRAIN; BCPLMAIN's private `TRM083` counts one *returned* main global/stack FREEMAIN. Thus the private cleanup ownership and test-specific returned-call counts are directly demonstrated on TK5.

**Qualification:** this confirms returned control from the expected MVS FREEMAIN service sites, not an independent accounting of MVS memory-manager success or absence of all leaks. Instrumentation and its extra exported `MEMDCNT` remain test-only; they are not part of the production BCPLMEM public contract. This completes isolated functional and reclamation gates (027, 028, 029, 039, 082, 088, 083), without modifying canonical runtime or normal regression runner.

**Next architectural checkpoint:** integrate an explicitly opt-in `BCPLMEM_OBJECT=1` mode, retain baseline default, then exercise combination with BCPLBYTE and BCPLAPT objects and finally the full 120-test suite. No such combined regression result is claimed yet.

## Checkpoint 3a: staged BCPLMEM_OBJECT opt-in runner integration

Commit `52e3ff8` adds an explicit `BCPLMEM_OBJECT=1` switch to `native-compiler/regression/run-test.sh` for the **ordinary assembled-runtime regression path**. Default `0` follows the original combined-runtime behavior. For `1`, the runner externalizes G87/G88 and MEMDRAIN from a **disposable generated source**, assembles `tools/checks/bcplmem-linkage-probe.asm` as a separate object, and appends it to the established object list after any case-specific assembler, BCPLBYTE, and BCPLAPT objects. The five-object builder already supports `--fifth-source` and generates separate IFOX/IEWL steps for the selected sources; this change exposes that capacity. The object source is the previously validated **experimental BCPLMEM** implementation, not yet a stabilized production module or installed PDS member.

Fail-closed boundaries: nonbinary `BCPLMEM_OBJECT` values are rejected; test 083 requires its dedicated `tools/checks/prepare-bcplmem-083-probe.py` because canonical 083 instruments a monolithic runtime; and BLIB-object-staged cases are explicitly refused while their separate prepare-stage2 linkage is not updated. These restrictions prevent a partially externalized pass being mistaken for validated object-mode integration. The intended initial **operator validation** is:
```sh
git pull --ff-only
BCPLMEM_OBJECT=1 tools/run-native-regression 27 --show-output
BCPLMEM_OBJECT=1 tools/run-native-regression 29 --show-output
BCPLMEM_OBJECT=1 BCPLBYTE_OBJECT=1 BCPLAPT_OBJECT=1 \
  tools/run-native-regression 29 --show-output
```
Capture job-summary, assembler steps, IEWL externals, output checks. At this stage **no runner-level MVS execution has been reported**; no 120/120 opt-in suite result is claimed. Full-suite acceptance requires adding appropriate BLIB-object staging and native regression 083 module-aware instrumentation, and verifying them under TK5. The all-default baseline remains unchanged.

## Checkpoint 3b: BCPLMEM_OBJECT runner acceptance — operator report

On 11 October 2026, after pulling main through `7b2d8ec`, the operator executed `BCPLMEM_OBJECT=1 tools/run-native-regression 27 --show-output` and `... 29 --show-output`. **Both reported PASS 1/1.** The operator then ran `BCPLMEM_OBJECT=1 BCPLBYTE_OBJECT=1 BCPLAPT_OBJECT=1 tools/run-native-regression 29 --show-output`, also **PASS 1/1**. These are end-to-end regression-runner pass results, including its normal output checks. The abbreviated console report does not contain individual IFOX, IEWL cross-reference, or JOB numbers, so separate object resolution in these three specific jobs is supported by the selected build path and prior isolated tests rather than fresh displayed IEWL evidence. Normal mode remains unchanged. Next: broaden runner coverage, integrate the special 083 case and BLIB-object path before claiming full opt-in suite acceptance.

## Checkpoint 3c: six additional three-object runner regressions pass

Operator report, 11 October 2026, following pull through `f89ef01`: with `BCPLMEM_OBJECT=1 BCPLBYTE_OBJECT=1 BCPLAPT_OBJECT=1`, `tools/run-native-regression 30 32 --show-output` passed **3/3** (030 GETVEC failure, 031 vectors across calls, 032 returned vector pointer). Separate invocations passed **039 FREEVEC release/reallocation 1/1**, **082 FINISH with outstanding vectors 1/1**, and **088 STOP with outstanding vectors 1/1**. Total for this checkpoint **6/6 PASS**, zero failures; with prior checkpoint 3b **9/9 opt-in executions**. Console output supplies runner acceptance, not individual IEWL symbol listings or per-step RC details. The opt-in runner still intentionally refuses monolithic-instrumented 083 and BLIB-object staging. Address these boundaries before claiming 120/120 object-mode support. Default runner stays unchanged.

## Checkpoint 3d: module-aware 083 integrated into the opt-in runner

The native runner now admits `BCPLMEM_OBJECT=1` for regression **083**. After the ordinary 083 test-local monolithic instrumentation, it invokes the **previously exercised** `tools/checks/prepare-bcplmem-083-probe.py` to create the independent BCPLMAIN and test-only instrumented BCPLMEM assembler sources from a disposable copy. The runner then uses the resulting *main source* as its current combined input, optionally externalizes BCPLBYTE and BCPLAPT as in all other regressions, and selects the test-only `bcplmem-083-instrumented.asm` instead of the standard BCPLMEM object. The ordinary two-to-five-object JCL builder and GO submission/report-validation code are reused. Existing `expected.txt` already contains `42` and `V=2 M=1`, so both records are verified by the standard runner output checker.

Regression 083 without BCPLMEM_OBJECT remains on its original monolithic instrumentation path; all other BCPLMEM_OBJECT regressions still use the ordinary BCPLMEM CSECT. The standalone preparer's own independent JCL is merely a derived artifact in the workarea; the runner prepares and submits its own `native-test-heavy.jcl`. The test counter export `MEMDCNT` remains exclusively test-local.

**Validation required, not yet claimed**:
```sh
git pull --ff-only
BCPLMEM_OBJECT=1 tools/run-native-regression 83 --show-output
BCPLMEM_OBJECT=1 BCPLBYTE_OBJECT=1 BCPLAPT_OBJECT=1 \
  tools/run-native-regression 83 --show-output
tools/run-native-regression 83 --show-output
```
Each must pass 1/1 and emit the two exact output records. The preexisting isolated JOB 6295 establishes the module-aware instrumentation, not yet the automated runner path or its three-object coexistence. BLIB-object staging remains separately excluded.

## Checkpoint 3e: automated regression 083 triple acceptance

Operator report, 11 October 2026, after pulling main through `668c11c`: three independent `tools/run-native-regression 83 --show-output` invocations all reported **PASS 1/1**, FAIL 0: (1) `BCPLMEM_OBJECT=1`; (2) `BCPLMEM_OBJECT=1 BCPLBYTE_OBJECT=1 BCPLAPT_OBJECT=1`; (3) default mode with no object switches. The expected regression fixture is exactly two records, `42` and `V=2 M=1`, verified through the ordinary runner's JES output checker. The abbreviated console report does not individually display output records or IEWL symbols. These results close the runner-level module-aware 083 acceptance gate and confirm default regression compatibility. Remaining integration boundary: BLIB-object staging with BCPLMEM_OBJECT, before full three-object 120-test suite.

## Checkpoint 4a: BLIB-object staging supports opt-in BCPLMEM (pending TK5)

The `069-independent-blib-object/prepare-stage2.py` now accepts `--external-mem`, externalizes the *disposable runtime source* through the existing strict BCPLMEM extractor, assembles `bcplmem-linkage-probe.asm` in a separate `ASMMEM` step, and passes `&&MEMOBJ` to IEWL while preserving `INCLUDE OBJ(BLIB)` from `HERC02.BCPL.OBJ`. The native `run-test.sh` forwards `BCPLMEM_OBJECT=1` on the BLIB-object path. Extra object order: BCPLBYTE, BCPLAPT, BCPLMEM when selected. Legacy BLIB staging remains the default. Preparer removes any older output JCL before starting, preventing stale-deck reuse after failure.

**Operator acceptance gates (not yet executed):**
```sh
git pull --ff-only
BCPLMEM_OBJECT=1 tools/run-native-regression 69 --show-output
BCPLMEM_OBJECT=1 BCPLBYTE_OBJECT=1 BCPLAPT_OBJECT=1 \
  tools/run-native-regression 69 --show-output
tools/run-native-regression 69 --show-output
```

Confirm that each reports PASS, the IEWL report contains the BLIB PDS INCLUDE and resolves exported GETVEC, FREEVEC, MEMDRAIN, and that every selected IFOX step completed normally. As usual, there are no local TK5 results at commit time, and this is not full-suite acceptance.

## Checkpoint 4b: BLIB-object regression 069 accepted in three modes

Operator report, 11 October 2026, after pull through `9254acf`: regression **069-independent-blib-object** passed 1/1 with `BCPLMEM_OBJECT=1`, passed 1/1 with `BCPLMEM_OBJECT=1 BCPLBYTE_OBJECT=1 BCPLAPT_OBJECT=1`, and passed 1/1 with default options. All reported FAIL 0. This is runner-level end-to-end evidence that the BLIB PDS object staging continues to work with the new independent BCPLMEM service and alongside BCPLBYTE and BCPLAPT; the console summaries do not provide per-step IEWL listings. Normal mode remains functional. The targeted external-service and BLIB-object integration gates are now accepted. The remaining planned validation is a full 120-test opt-in regression sweep; no 120/120 result is claimed at this checkpoint.

## Checkpoint 4c: full 120/120 opt-in object-mode suite ACCEPTED

Operator report, **11 October 2026**, after pulling `main` through `e861093`: the complete native regression suite `tools/run-native-regression` ran with **BCPLMEM_OBJECT=1 BCPLBYTE_OBJECT=1 BCPLAPT_OBJECT=1**. All numbered tests **000–119** individually reported PASS. The aggregate result was **PASS 120 / FAIL 0 / TOTAL 120**. This includes object-linked BLIB tests, module-aware reclaimed-storage instrumentation in 083, GETVEC/FREEVEC functional cases, and STOP/FINISH teardown scenarios. It is direct operator evidence of complete regression-suite acceptance of the simultaneous three-module opt-in configuration under MVS/TK5.

The baseline (no object options) remains the default and was not altered by this march. The external BCPLMEM implementation is still housed in experimental tooling; the passing suite does **not** prove historical equivalence or leak freedom beyond measured instrumentation. Architectural promotion to a permanent runtime module and MVS object-PDS lifecycle is a separate, deliberate decision. **Do not claim production readiness or default-mode migration from this result alone.**

## Next march: four-module relocatable object library — staging checkpoint

Following full 120/120 acceptance of the opt-in source-object configuration, the project is moving BCPLMAIN, BCPLBYTE, BCPLAPT, and BCPLMEM into `HERC02.BCPL.OBJ` alongside BLIB. This is **not yet a completed promotion**.

Canonical source candidates are `asm/bcplbyte.asm`, `asm/bcplapt.asm` (copied from accepted external probe), and `asm/bcplmem.asm` (copied from accepted external probe). The BCPLMAIN object candidate is **derived reproducibly** from frozen `asm/bcplmain-wip.asm` through the established strict byte, apt, and mem extraction passes. The derivation is written under `workarea/runtime-object-library/` and leaves the original runtime untouched. A committed standalone BCPLMAIN source and actual installed-object link path remain future gates.

`python3 tools/checks/prepare-runtime-object-library.py` runs source checks and **only generates**, but does **not submit**, `workarea/runtime-object-library/build-runtime-objects.jcl`. It obtains the job card and managed `OBJ` dataset through the project's **dspal** configuration. Its four IFOX assembly steps and four guarded IEBGENER member-install steps use the exact FB80 PDS object format already established by `jcl/build-blib-object.jcl`. It does not rebuild, delete or replace `OBJ(BLIB)`.

**Caution:** the generated installer overwrites four production object members and is **non-atomic**; successful early member installs would remain if a later step failed. **Do not submit** until source preflight, backup/recovery procedure, and downstream installed-object consumer JCL have been reviewed. Review `tools/dspal stat OBJ` and `tools/dspal ls OBJ` first. No fresh TK5 job has run for this staging checkpoint and the 120/120 evidence applies to the earlier object-source configuration, not installed members.
