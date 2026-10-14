# M2.1 Gate A — Native Runtime Contract Reconciliation

**Status:** OPEN — initial source reconciliation recorded 14 October 2026; **not accepted or closed**.
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
- [ ] Complete compiler-source call-site dependency crosswalk for the **next** Cambridge reconstruction stage.
- [ ] Decide scope and acceptance probes for B–E based on actual blockers and testability.
- [ ] Record project-owner Gate A acceptance decision; **do not** infer acceptance from existence of this document.

**Gate A remains OPEN.** This document is an initial source-grounded planning record, not an authorization to implement assembler changes.
