# M2.1 Gate A — Native Runtime Contract Reconciliation

**Status:** ACCEPTED AND CLOSED — 14 October 2026; owner directed progression to Gate B.
**Predecessor:** M2.0 Gate F and march accepted/closed 14 October 2026.
**Purpose:** decide the smallest justified runtime contract work needed for Cambridge BCPL compiler reconstruction, without treating every M1.9 deferred feature as an implementation order.

## Accepted baseline and authority

- Git source: `asm/bcplmain-d6-candidate.asm` -> `HERC02.BCPL.DEVOBJ(BCPLM6)`; independent `asm/bcplio.asm`, `asm/bcplmem.asm`, `asm/bcplbyte.asm`, `asm/bcplapt.asm`; separately compiled BLIB object.
- `packaging/m2-0-gate-f-final-candidate-acceptance.md`: Gate E updated independent DEVOBJ objects (2722/2725/2728, IFOX and IEBGENER RC=0000), integrated IEWL JOB 2731 RC=0000, then D6 development candidate smoke 00 PASS and complete 00–123 panel **123 PASS, 0 FAIL, one expected SKIP 083**.
- `packaging/m2-0-runtime-modularity-architecture.md` and `packaging/m2-0-gate-e-maintainability-review.md` govern the modular boundaries.
- `packaging/runtime-contract-v1.md` and `packaging/m1-9-runtime-contract-audit.md` describe **M1.9**, not the modified D6 implementation. Preserve them as dated evidence, not as a current-source override.
- No production `HERC02.BCPL.OBJ` promotion; no changes to assembler, MVS resident SOURCE/JCL, or development object members authorized by Gate A.

## Preliminary discrepancy register

Evidence notation: **S** = inspected current D6 source; **E** = accepted M2.0 linker/executable evidence in Gate F; **U** = behavior not demonstrated for the stated boundary.

| M1.9 observation / discrepancy | Current disposition | Evidence / further action |
| --- | --- | --- |
| B-APT-01 G40 still selects BCPLMAIN-local APTOVEC | **Resolved by M2.0** | S: D6 stores external `APTOVEC` at G40 byte offset 160 and initializes external `APLIMIT` from STKLIM; E: Gate B 091–093, final panel. |
| G85/G86 separate BCPLBYTE included but local dispatch concern | **Resolved by M2.0** | S: D6 publishes external GETBYTE/PUTBYTE at offsets 340/344; E: Gate C and Gate F. |
| Stream QSAM handlers embedded in BCPLMAIN | **Resolved structurally by M2.0** | S: D6 publishes external BCPLIO entries for G11–17, G33, G39, G41–42, G46–47; BCPLIO owns QSAM DCBs and IOINIT/IOFIN; E: Gate D and final panel. Not a claim of full historical I/O compatibility. |
| B-STK-02 outdated 16KB comment | **Documentation-only discrepancy remains** | S: D6 stack-check comment near STKIMPL still says provisional boundary 16KB, despite contract's 16,384-word working stack. Verify assembled size/limits before correcting source comments in another gate. |
| C-EXIT-01 / D-OBS-02 stack-overflow RC=0 | **Still open, source-demonstrated** | S: `STKOVFL` invokes IOREPL then branches `FINIMPL`; `FINIMPL` clears STOPRC. E: 093 exercises selected overflow diagnostic; does not establish an appropriate nonzero RC. Candidate for focused Gate B decision/probe. |
| C-EXIT-02 exceptional cleanup | **Still open; path-specific** | S: normal FINEXIT calls IOFIN and RELMEM (MEMDRAIN, MEMBIND(0), main FREEMAIN). NOSTART/GTOOBIG/BADRETN use RELMEM but bypass IOFIN; STKFORM branches straight to MVS return with RC=36; GNOCORE returns RC=24 without acquired main block. Evaluate concrete effects, not blanket teardown refactor. |
| Missing START RC=20 | **Intentional existing exceptional behavior; verify before changing** | S: NOSTART runs RELMEM and returns 20; no evidence yet this prevents compiler reconstruction. |
| B-STK-03 STACKHWM exactness | **Uncertain / insufficiently tested** | M1.9 reports regression 120 in-range word-address result only, not exact high-water usage. No automatic diagnostic work ordered. |
| B-MEM-01, D-OBS-01 private MEMSTAT | **Intentional interface boundary** | S: BCPLMEM ENTRY MEMSTAT private R1 four-fullword snapshot; D6 does not publish a BCPL global. Retain private unless compiler evidence requires exposure. |
| B-MEM-02 FREEMAIN accounting | **Uncertain / not demonstrated quantitatively** | Source MEMDRAIN and normal suite demonstrate control flow, not measured OS storage balance after exceptional termination. |
| D-OBS-03 DEBUGINT | **Historical feature deferred / provisional local extension** | S: D6 publishes G150; not historical LIBHDR routine. No evidence that redesign is necessary. |
| D-OBS-04 through D-OBS-07 BACKTRACE, logging, MAPSTORE, USERPOSTMORTEM | **Historical features deferred** | Source names/BLIB definitions are not proof of all runtime dependencies or a Cambridge compiler blocker. No automatic native implementation. |
| Complete BLIB trailer export verification | **Still uncertain / insufficiently tested** | M1.9 source describes trailer import algorithm; Gate F confirms independent BLIB integrated, not every byte-level pair. Probe only if compiler linkage requires exact mapping. |
| C-TEST-01 exhaustive per-case fixture matrix | **Documentation / test-coverage gap** | 123 PASS is aggregate execution evidence, not proof of untested historical paths. |
| 80/132-byte record-based QSAM I/O vs Cambridge environment | **Intentional MVS adaptation** | M1.9 stream contract plus D6 BCPLIO implementation. Revisit only if compiler source/OCODE/assembly workload exposes a specific deficiency. |

## Immediate Cambridge compiler dependency analysis

**Demonstrated foundation:** native module entry and global trailer registration, START dispatch, BCPL frames and checked stack entry, APTOVEC, byte primitives, vector allocation, selected character/record streams, BLIB formatting, STOP/FINISH, and independent link-edit are exercised under the accepted panel. This is not equivalent to successful native execution of the complete Cambridge compiler.

**Expected historical dependencies to cross-check:** compiler source's real use of LIBHDR streams, allocation and formatting, segment/module loading, failure exits, and generated code's system-vector conventions. The presence of a LIBHDR name is not evidence of a required feature; identify actual call sites and source-stage requirements before ranking additions.

**Not established as compiler blockers:** exact STACKHWM accounting, public MEMSTAT, DEBUGINT enhancement, full BACKTRACE/MAPSTORE/ABORT recovery, full block-file or logging interfaces, call-count implementation.

**Evidence task still required for Gate A acceptance:** assemble a source-level crosswalk from the next compiler stage's tracked source and headers to current published runtime globals and system-vector hooks; distinguish executed dependencies from merely referenced/anticipated facilities. Do not claim completion of this crosswalk from the regression panel alone.

### Preliminary historical compiler-source call-site inspection (not an executable dependency proof)

Directly inspected tracked `richards-bcpltape/bcplib/bcpl/syn`, `trn`, `cg`, and `richards-bcpltape/sys3/bcpl/libhdr`. These sources have a mixture of actual calls, local definitions and code-generation text; a name match by itself is **not** a runtime-provider dependency.

- `syn` directly calls `LONGJUMP(REC.P,REC.L)` in syntax-error recovery, `FINDINPUT(...)`, `SELECTINPUT(...)`, `ENDREAD(...)`, `GETBYTE(...)`, `PUTBYTE(...)`, `RDCH(...)`, `WRCH(...)`, `WRITEF(...)`, and `STOP(8)`, among other library services. The tracked LIBHDR assigns **LONGJUMP G32**, for which M1.9 did not establish an installed native provider. This is a **credible potential compiler blocker**, not proof the relevant historical phase is presently executing native under D6.
- `trn` calls `SELECTOUTPUT`, `GETBYTE`, `PUTBYTE`, `WRITEF`, `STOP`, and historical BLIB string/packing functions. Not every textual `LOAD(...)` is LIBHDR G10 LOAD: translator source contains its own internal names and expressions. Resolve symbols before claiming a module-loader dependency.
- `cg` directly calls `DATE()` in the module-prefix generation path, plus `GETBYTE`, `SELECTOUTPUT`, `WRITEF` and output operations. LIBHDR assigns **DATE G29**, with no established native runtime publisher in the inspected D6 installation block. This is another **credible potential blocker** for direct native compiler execution. `READN(...)` and `LOAD(...)` textual matches require symbol-resolution scrutiny because generator internals can have identically named procedures.
- Existing tests validate much of the character, vector, byte and BLIB foundation; they do **not** establish G29 DATE or G32 LONGJUMP compatibility. Before adding runtime code, determine the exact compiler source variant and intended next execution stage, whether native execution really traverses these paths, and whether existing compiler-local or bootstrap providers supply them.

**Revised Gate A priority:** resolve DATE and LONGJUMP provider/usage contracts alongside termination semantics. Do not silently treat either historical name as implemented and do not presume an absent D6 native publication is automatically an implementation mandate.

## Gate A completion review — compiler execution boundary (14 October 2026)

The `native-compiler/mvs-resident-cambridge.md` record establishes that the **currently operating compiler is CAMBCOMP INTCODE executed by ICINT V19**. It is not yet a natively linked System/370 compiler. Therefore missing D6 services do **not** block today's 123-case compiler-to-native-application regression workflow; they become relevant when pursuing the later native compiler bootstrap.

The historical native-compiler candidate is more than the three phases previously skimmed. `richards-bcpltape/bcplib/bcpl/bcpl` is the compiler's driver and contributes requirements beyond `syn`, `trn`, `cg`:

| Candidate interface | Historical concrete use | D6 status / Gate C action |
| --- | --- | --- |
| G31 LEVEL and G32 LONGJUMP | `syn` FORMTREE and nested parser recoveries save `LEVEL()`, then syntax errors invoke `LONGJUMP(REC.P,REC.L)` | Neither is installed by D6's explicit publication block. **Treat as coupled language/runtime control semantics, not simply optional postmortem tracing.** Determine frame-level contract and CG370 support before any implementation. |
| G29 DATE | `cg` CG370 invokes DATE and emits three words from returned structure into module prefix | No established D6 provider; required on this historical CG370 code-generation path. Reconstruct exact DATE return layout before implementing, do not substitute a generic printable date. |
| G42 FINDINPUT / G41 FINDOUTPUT with stream names | Compiler driver requests `SYSIN`, `SYSPRINT`, `OCODE`, `CODE`, `SYSGO`; SYN opens nested GET streams | BCPLIO currently recognizes BCPIN/BCPINB input and SYSPRINT/BCPALT output. Actual compiler DD/stream strategy **cannot be presumed supported**. Understand compile/link/run pipeline and stream mapping before adding names or record modes. |
| G39 FINDPARM, G11–17 character I/O, G33 WRAPOUTPUT, G46–47 close | Driver's option parsing, source reading, output flushing | Native equivalents exist and are regression-exercised for narrower usage; driver also uses PARMS G45, unestablished as a native publication. |
| G40 APTOVEC, G85–88 byte/vector services | Compiler workspace, byte manipulation and nested work area | Native implementations installed and regression exercised; capacity against real compiler workload not yet demonstrated. |
| G10 LOAD, G7/G9 UNLOAD variants, segment/file services | Driver `NEEDS "$LOAD$"`, optional overlays `LOADSEG("SYN"/"TRN"/"CG")`, `UNLOAD`, `LOADCODE` | Potential dependency of overlay/load-and-go modes, **not** proof normal nonoverlay native compiler requires complete historical loader. Bound by selected build mode. |
| G3 ABORT, G36–37 logging, G78 MAPSTORE | Driver has an own ABORT routine, logging fallback if SYSPRINT unavailable, optional MAPPING | Secondary/error/optional behaviors; do not equate mere references with immediate runtime obligations. |

This source inspection is a **candidate dependency crosswalk**, not complete name binding, feature exercise or a native compiler executable test. `LEVEL`/`LONGJUMP`, the output stream naming/format, and the DATE structure are the highest-priority historical semantics to establish **when scheduling native compiler self-hosting**. A future Gate C should first decide whether its intended payload is a driver/phase source module or a smaller independent compiler component; implementing all of the driver contract by default would be premature.

### Gate A gate recommendations (bounded)

- **B, targeted failure semantics:** record observed stack-overflow diagnostic **and current RC=0** using a dedicated D6 candidate probe; adopt a nonzero failure policy only after separate decision. Check the narrowly identified abnormal cleanup branches; no blanket exception subsystem.
- **C, source contract study first:** focus G29 DATE representation, G31 LEVEL/G32 LONGJUMP semantics and driver stream needs; do not write native implementations before an agreed native compiler integration slice requires them. Record unsupported globals explicitly.
- **D, documentation-only initially:** retain historical/minimal programmer observability, do not expand MEMSTAT or implement generalized BACKTRACE/MAPSTORE.
- **E, executable integration:** use a representative separately compiled BCPL program with existing services, verify both resolved DEVOBJ objects and actual GO; **do not** claim the full Cambridge compiler is native.
- **F, acceptance:** focused tests and the complete 00–123 regression panel after any code changes, independent builds/linker verification, explicit closing decision.

**Gate A source-review recommendation:** planning/reconciliation can be accepted with historical compiler execution gaps clearly identified as conditional on a later native bootstrap slice. Acceptance of this audit is **not** acceptance of G29/G31/G32 or SYSIN/CODE/SYSGO runtime functionality. No assembler implementation has been authorized.

## Candidate work and priority

1. **Gate B — termination/failure:** first establish historical and MVS completion-code policy for STKOVFL; develop a focused test that asserts diagnostic **and** RC on the installed D6 candidate. Confirm whether bypass paths leak observable buffered output or skip indispensable cleanup. Make a minimal correction only if the test/contract decision warrants it.
2. **Gate C — historical compatibility:** audit actual compiler call-site requirements; fix only reproducible incompatibilities needed by the next compiler stage. A no-code outcome is acceptable.
3. **Gate D — diagnostics:** bounded review of STACKHWM, DEBUGINT and failure messages; use existing programmer-facing facilities. No new monitoring framework; no automatic MEMSTAT/global or postmortem build-out.
4. **Gate E — application integration:** separately compiled/link-ed representative BCPL applications against candidate DEVOBJ, emphasizing the interfaces actually needed by compiler reconstruction; record object resolution and execution separately.
5. **Gate F — candidate acceptance:** independently build changed DEVOBJ members if any, verify IEWL and focused cases, rerun full 00–123 suite, record changes/deviations and explicitly accept/close M2.1. Production OBJ stays unchanged unless separately authorized.

Priority incorporates compiler-blocking effect, demonstrated correctness, historical grounding, implementation cost, testability, and regression risk. The source-confirmed overflow RC deserves evaluation, but **is not yet authorized for modification**.

## Explicit exclusions

No re-modularization of the accepted service components, no BCPLSTACK extraction without evidence, no new speculative global-vector service, no broad I/O redesign, no historical compatibility claims unsupported by executable/source evidence, no compiler/code-generator redesign, no resident MVS changes, no production OBJ promotion.

## Gate A acceptance criteria (open)

- [x] Verified accepted M2.0 object/module baseline against repository closure evidence.
- [x] Reconciled principal M1.9 gaps with D6 source and M2.0 accepted execution; separated resolved, open, uncertain, intentional adaptations, deferred historical facilities and documentation drift.
- [x] Completed bounded candidate crosswalk for historical SYN/TRN/CG and BCPL driver, explicitly distinguishing current ICINT compiler from prospective native compiler; exact ABI/provider validation transferred to Gate C.
- [x] Proposed bounded B–E scope and focused acceptance probes; code changes remain conditional on separate gate decisions.
- [x] Owner authorized progression to Gate B on 14 October 2026; Gate A accepted as a bounded source/contract audit, not as proof of native compiler execution.

**Gate A ACCEPTED AND CLOSED — 14 October 2026.** The owner's direction to proceed Gate B accepts the source-grounded reconciliation and limited gate scope. Remaining historical ABI questions are expressly transferred to Gate C. No assembler implementation was authorized by Gate A.
