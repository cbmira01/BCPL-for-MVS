# M1.9 — Runtime Contract and Observability Audit

Status: **ACTIVE — Gate A in progress.** Opened 13 October 2026 after acceptance and closure of [M1.8](m1-8-reproducible-runtime.md).

## Objective

Produce a source-grounded, versioned **Runtime Contract Specification** for the five-component reconstructed BCPL runtime: BCPLMAIN, BCPLMEM, BCPLBYTE, BCPLAPT and BLIB. Identify existing behavior, interface exposure, historical compatibility and executable evidence. Establish an explicit observability contract for programmers and MVS operators.

**Audit first.** No production OBJ promotion, SOURCE/JCL synchronization, resident build, compiler modification, or runtime semantic change is authorized by opening M1.9. Git remains implementation authority; MVS is the build and execution target. DEVOBJ is the development/candidate object library; OBJ is the stable ordinary-application library, promoted only on separate authorization.

## Gates

| Gate | Scope | Acceptance evidence |
| --- | --- | --- |
| **A — Runtime interface inventory** | Five modules; exported entry points, global-vector slots, linkage conventions, dependencies, and registration | Source-anchored interface matrix, unknowns explicitly identified |
| **B — Storage and stack contracts** | GETVEC/FREEVEC, APTOVEC, stack frames, limits, ownership, cleanup | Implementation and boundary contracts; matching regressions or gaps |
| **C — I/O and termination contracts** | Stream naming, selected streams, record buffering, FINISH/STOP, completion codes, abnormal exit | Source-anchored I/O and termination map |
| **D — Observability inventory and exposure** | D1 mechanisms and owning modules; D2 BCPL/operator invocation and output; D3 tests and gaps | Observability contract with interface, trigger, data source, output, failure behavior, evidence |
| **E — Historical compatibility** | Cambridge BCPLMAIN/BLIB recovered evidence vs implemented semantics | Difference register: matched, intentional MVS adaptation, omission, uncertain, or defect |
| **F — Verification and acceptance** | Complete contract/evidence traceability, focused tests only where needed, document unresolved gaps | Accepted specification, coverage matrix, disposition register and milestone close |

## Gate A — preliminary source-grounded inventory

Source inspected directly at M1.9 opening: `asm/bcplmain.asm`, `asm/bcplmem.asm`, `asm/bcplbyte.asm`, `asm/bcplapt.asm`, and the M1.8 build/provenance record. **This is a preliminary inventory, not Gate A acceptance**; BLIB exported globals and all register preservation rules remain to be fully enumerated.

| Object/CSECT | Externally visible symbols or interface | Observed source behavior / audit question |
| --- | --- | --- |
| BCPLMAIN | CSECT BCPLMAIN; `ENTRY STKOVFL`; `EXTRN BLIB, GETVEC, FREEVEC, MEMDRAIN, MEMBIND` | MVS entry and saved caller context; allocates global/stack region; imports generated application and BLIB global registrations; publishes selected service slots; owns I/O, termination and stack failure path. |
| BCPLMEM | `ENTRY GETVEC,FREEVEC,MEMDRAIN,MEMBIND,MEMSTAT` | Owns vector allocation/deallocation, private teardown, G6!48-list binding and allocator statistics interface. Classify public BCPL services vs private assembler ABI. |
| BCPLBYTE | `ENTRY GETBYTE,PUTBYTE` | Byte primitives; BCPL argument/return register convention documented in source; G85/G86 slots published by BCPLMAIN. |
| BCPLAPT | `ENTRY APTOVEC,APLIMIT`, `EXTRN STKOVFL` | G40 temporary-vector call behavior and shared stack-overflow path; establish whether APLIMIT is a public symbol, runtime configuration, or purely internal state. |
| BLIB | Compiled generated BCPL object, imported via module trailer/global registration rather than assembler `ENTRY` list | Generated from historical `richards-bcpltape/bcplib/bcpl/blib` via `make-demoted.py`. Enumerate actual exported globals from source, not just historical names. |

### Confirmed BCPLMAIN publication paths requiring formal contract

- Main module trailer registration populates the global vector; BCPLMAIN then explicitly imports the separately linked BLIB module's global trailer (source around lines 687–719).
- G6 publishes a BCPL word pointer to save-area-compatible state, with modeled G6!29 load-list head and G6!48 allocator-list head. The details must be assessed for historical compatibility.
- G52/G53 main-program bounds and G54/G55 allocated stack extent are published at byte offsets 208/212 and 216/220. The safe frame limit is **not identical** to published G55: safe limit is 16,384 words from the stack base, with reserved clearance.
- G11, G12, G13, G14, G15, G16, G17, G33, G39, G40, G41, G42, G46, G47, G85, G86, G87, G88 and provisional G150 are among explicit service-publication paths observed around lines 752–810. This list is **not exhaustive** and must be reconciled to LIBHDR.
- G76 is imported from BLIB when present; BCPLMAIN installs a fallback only while the G76 slot retains the historical unset sentinel.

### Initial observability inventory, not yet a compatibility claim

| Mechanism | Source evidence | Exposure question for Gate D |
| --- | --- | --- |
| Stack markers and high-water measurement | BCPLMAIN initializes alternating markers across 16,384 usable stack words and installs guard/marker metadata (around lines 616–657); historical BLIB implements STACKHWM | Verify current BLIB export and whether G56 STACKHWM operates against published G54/G55 and sentinel layout, then classify result semantics. |
| Stack exhaustion | BCPLMAIN STKIMPL checks frames against STKLIM; STKOVFL writes a diagnostic to the output buffer and enters termination (around lines 1011–1047); BCPLAPT branches to STKOVFL | Establish exact SYSOUT destination, return status, and whether backtrace or map occurs. |
| Heap accounting | BCPLMEM exports MEMSTAT and controls GETVEC/FREEVEC/MEMDRAIN; BCPLMAIN connects MEMBIND to G6!48 | Determine MEMSTAT contract, whether it is BCPL callable, what values it exposes and which test covers it. |
| Debug output | BCPLMAIN explicitly publishes DEBUGINT at G150 and includes a decimal output routine | Determine if documented BCPL service or provisional developer hook; output record behavior. |
| Historical post-mortem | Historical BLIB includes ABORT, BACKTRACE, MAPSTORE, WRITEARG; reconstructed BLIB object may contain these | Verify installed global addresses, actual runtime prerequisites (load list, SAVEAREA fields, program bounds), and executable behavior **before** advertising programmer-visible support. |

## Existing acceptance baseline

M1.8 Gate F: `BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ tools/run-native-regression` resulted in **123 PASS, 0 FAIL, 1 expected SKIP (083 source-only instrumentation), TOTAL 124**. This is broad regression baseline evidence, not individual proof of every contract. Keep this baseline stable during audit.

## Immediate Gate A work

1. Enumerate the exact global-vector definitions in the tracked LIBHDR, and compare source-side registration and BLIB exports. Distinguish published and historical-only slots.
2. Extract actual BCPLMAIN, BCPLMEM, BCPLBYTE, BCPLAPT calling conventions and preserved/clobbered registers; classify assembler-private and BCPL-public entry points.
3. Map each service to existing regression cases and flag missing direct coverage.
4. Record unresolved differences, then accept Gate A only after a verified complete matrix. Gate B begins after Gate A closure.

## Non-goals and controls

No broad regression replay, change to resident MVS datasets, production library promotion, historical capability claims based solely on source presence, or speculative implementation while gates A–E are gathering evidence. Gate F may authorize focused new probes only with a clearly identified evidence gap.
