# DR.5 — Common registration and finalizer authority transfer proposal

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.5 — Validation and Reconciliation  
**Baseline:** `ed04ba40b7155ca0032d9bf0548de547c58d72db`  
**Disposition:** PROPOSED — no transfer effective without explicit owner approval.

The shared QUERY transfer and primary OPEN rollback decision are already
effective at the baseline. See [owner acceptance](dr5-query-authority-and-qsam-precedence-acceptance-20261127.md).
The next proposed transfer covers common registration and finalization
only, from the [R.0 owner ABI decisions A–H](../runtime-extensions/runtime-extensions-r0-owner-abi-decisions.md)
and [Decision G numerical contract](../../archive/runtime-extensions/runtime-extensions-r0-decision-g-contract-20261021.md)
to chapter 2 of the [Reference for System Extensions](../../../../docs/product/Reference-for-System-Extensions.md).
Package-specific APIs and IFOX macro/tool interfaces are not superseded here.

## Clause reconciliation

| Original provision | Destination | Evidence / required clarification |
| --- | --- | --- |
| A: independently relocated trusted begin/end, source/link checks | 2.1, 2.2 | R.1 source/IEWL acceptance; numeric alignment cannot prove callable ownership; explicitly retain build/link checks |
| B: BCRG header 28, selected pairs 8, required IDs 8, exact length, real empty table | 2.1 | Exact layout and limits, R.1 empty/selected jobs |
| C: BCEX header 48, exports 8, dependencies 16, exact major/minimum minor, dispatcher default | 1, 2.1 | Exact layout; retain one dispatcher by default, additional exports require documented exception |
| D: transitive requirements, dependency-first, lazy init, no v1 initializer, transactionality and reverse finalization | 2.1–2.3 | R.1, R.2 and DR.5 cases 194–197; clarify transitive validation is not automatic selection |
| E: effective actual app/BLIB/Core Runtime owner ledger, Global Number Registry, verified historical precedence | 2.1, 2.2 | R.1 collision jobs 2777–2779; G!76 JOB 2199; DR.5 resident BLIB census 1304; registry remains separate authority |
| F: exact eight-byte MVS finalizer block, register preservation, returned status, FINISH/STOP behavior | 2.3 | R.1 jobs 2776, 2780–2783; DR.5 combined case 200; no public extra test words |
| G: count/span limits, exact arithmetic, diagnostic bands/IDs, startup RC12 and no publication | 2.1, 2.2 | All numeric values and IDs match; R.1 1001–1014 and DR.5 structural cases; clarify post-structural error ordering below |
| H: generic startup before START and shutdown before IOFIN/MEMDRAIN; retain existing core/BLIB semantics | 2.2, 2.3 | Current BCPLMAIN and BCPLRGS paths, R.1 integrated acceptance |

## Qualification: deterministic rejection order

The approved Decision G calls for structural validation categories in order,
first offending record within category, then identities/entries, ownership
and dependencies. The corrected current registrar completes registry
extent/header/counts and all selected package extent, header and count
passes before reading variable records. Case 196 verifies structural
category precedence.

The remaining checks are not separate global passes for every diagnostic
ID. In the current [registrar](../../../../bootstrap-toolchain/asm/bcplrgs.asm),
PKNEXT walks selected packages in linked order; it checks package identity,
each export's scalar fields, existing ownership, prior duplicate exports,
then the finalizer address. DPSTART walks dependencies only after that pass;
REQLIST checks application-required IDs last. Within a dependency the
record fields and duplicate checks precede lookup, then order precedes
version compatibility. Multiple simultaneous post-structural faults may
therefore yield a different first diagnostic than a globally sorted
diagnostic-ID/category scheme. Do not promise a universal ID-priority
rule. The original contract's structural precedence is retained; the
post-structural traversal is source-observed and the full multi-fault
matrix is unverified.

**Recommendation:** accept that explicitly bounded post-structural order
as the current documented behavior and retain the unverified matrix as
a qualification. Do not redesign the registrar in this documentation
march absent a demonstrated supported-contract defect. Owner approval
is required for the clarified precedence and transfer.

## Evidence boundaries and proposed reference additions

- Preserve [R.1 closure](../runtime-extensions/runtime-extensions-r1-closure-20261022.md):
  24 integrated jobs, 14 startup diagnostic categories, three ownership
  cases, finalization and source/link gates, temporary runtime overlay.
- Preserve [expanded milestone closure](../runtime-extensions/runtime-extensions-milestone-formal-closure-20261116.md):
  known-package selection only; no arbitrary discovery, dynamic loader,
  auto-dependency selection or independent general library catalogs.
- Preserve [DR.5 extension evidence](dr2-extension-manual-migration-20261125.md):
  18 corrected registrar assertions in private and installed probes,
  numbered cases 194–197 accepted, no full hostile-pointer or multi-fault
  claim. Source trust remains mandatory.
- Add explicit lazy initialization, exact span bounds (28–540 BCRG,
  56–368 BCEX), current G!699 limit is not a permanent historical limit,
  no additional aggregate restriction, halfword alignment for callable
  targets with source-trusted provenance, and exclusion of test-only
  extra finalizer words. Preserve diagnostic bands and all 15 IDs.
- The Global Number Registry remains allocation authority; source,
  test oracles, release/configuration data and old evidence remain intact.

No new MVS execution, software change, numbered case, release action or
march closure. On approval, update chapter 2 and record the effective
revision and exact superseded scope, retaining original decisions.
