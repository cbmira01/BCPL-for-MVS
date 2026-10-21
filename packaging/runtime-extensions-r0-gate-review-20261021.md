# Milestone Runtime Extensions — R.0 evidence and gate review

**Review date:** 21 October 2026.
**March under review:** **R.0 — Evidence and contract**.
**Next march:** **R.1 — Generic registration foundation** (**not started**).
**Gate disposition:** **NOT READY TO CLOSE R.0**. The shared QUERY contract was subsequently [owner-approved](runtime-extensions-r0-query-abi-decision-20261021.md) on 21 October; its two-dispatcher MVS verification remains pending. This review retains its original open-item descriptions as the historical gate snapshot. Record the validated
contracts and completed isolated tests, but keep the specific remaining
R.0 evidence/decisions below open. No approval to change accepted runtime
objects follows from this review.

**Authority:** [Milestone Runtime Extensions](milestone-runtime-extensions.md),
[official nomenclature](runtime-and-library-nomenclature.md),
[Global Number Registry](global-number-registry.md),
[owner-approved ABI Decisions A–H](runtime-extensions-r0-owner-abi-decisions.md),
[Decision G exact contract](runtime-extensions-r0-decision-g-contract-20261021.md),
and the [effective ownership audit](runtime-extensions-r0-global-ownership-audit-20261021.md).
The milestone's R.0 exit gate calls for a verified ABI, slot ownership
rules, a candidate six-word QUERY descriptor with client tests,
registration and empty-table semantics, and **no speculative source
refactor**. Its **actual generic registrar and FINISH/STOP integration
belong in R.1 and subsequent marches**, not in this review.

## Verified evidence and accepted contract

| Area | Concrete evidence / adopted decision | Boundary |
| --- | --- | --- |
| Linked descriptor extent | **JOBs 2187–2192**, six isolated IFOX/IEWL/GO passes including five negative cases | Tight test-only formats, not a general pointer-safety guarantee |
| Dependency/owner/finalizer policy | **JOB 2195**, fourteen validator cases plus six simulated finalizer cases, all 20 actual GO markers, eight steps RC=0000 | Three-package fixture limit; simulated finalizer, not BCPLMAIN |
| Application and installed BLIB exports | **JOB 2197**, one application G!1 and exactly 21 relocated installed BLIB exports, no overlap between the two; link MAP examined | One small application, not a compiler-load ownership census |
| Historical G!76 | **JOB 2199**, real installed Core Runtime START compared BLIB's relocated WRITEF address with runtime G!76, RC=0000 and actual PASS marker | BLIB-present branch only; absent-BLIB WRITEST fallback not exercised |
| Decision G | Owner-approved N/M=32, K=8, D=16, BCRG/BCEX maxima 540/368 bytes, diagnostic IDs 1001–1014/2001, proposed startup RC=12 | **JOB 2203** verified 14 numerical count/size scenarios; host tests cover more fields, not live registrar |
| Installed binary inventory | **JOB 2200**, `BOOT_OBJ` FB80 PDS lists BCPLMAIN, BCPLMEM, BCPLBYTE, BCPLAPT, BCPLIO, BLIB | A PDS directory listing does not prove member bytes or build date |
| Source rebuild lineage | [17 October clean-room acceptance](clean-room-mvs-reconstruction-acceptance-2026-10-17.md), baseline `04c74af8`, BLDBMAIN JOB 8744 and BLIBBLD JOB 8748; 145 production regression PASS | Does not establish byte identity of today's installed objects |

The owner-approved binary contract is **28-byte `BCRG` fixed header,
48-byte `BCEX` fixed header, and an 8-byte public finalizer parameter
block**. It includes dependency-first selection, an actual effective
owner ledger, transactional validation before START, preservation of
only proven historical precedence, reverse finalizer order, and no
version-1 initializer hook. **These are design commitments, not a
claim that the generic registrar or finalizer runs in the accepted
runtime.**

The earlier R.0 fixture's **4/8/12 etc. internal statuses** are not
Decision G public diagnostic IDs. JOB 2203 compared **1003 and 1006**
in assembler, with GO RC=0000 because each expected outcome matched.
RC=12 on real startup rejection remains an approved **future** policy.

## Remaining R.0 gate items (require explicit disposition)

1. **Shared opcode-0 QUERY contract and client verification.**
   The milestone still calls its six-word shared capability layout and
   return/error semantics **provisional**. QSAM Q.0 **JOB 2157**
   exercised a six-word test-only QUERY over G!200, but did not accept
   the generic cross-package contract. Decide the shared signature,
   size/prefix behavior, version/bitmap/error rules and demonstrate a
   generic caller/test without claiming BCPLQSAM implementation.
2. **Trusted build/link evidence for descriptor extents and deployed
   objects.** Require reproducible trusted begin/end and code-address
   provenance/MAP evidence under Decision A. Reconcile the 17 October
   clean-room build ledger with any subsequent `BOOT_OBJ` replacement
   before asserting the current installed members' exact source revision.
   Do not mistake JOB 2200 inventory or JOB 2197 relocation for a
   binary hash.
3. **Effective global ownership scope.** Extend the per-executable
   ownership method beyond JOB 2197's single START application,
   review possible indirect Core Runtime writers and compiler
   allocations (including G!150), and record exact historical
   precedence exceptions. The **BLIB-absent G!76 fallback** remains
   untested; determine and execute a safe isolated test if this branch
   is to be claimed verified.
4. **R.0 collision/transactionality evidence.** The source audit
   requests an isolated rejection against an **actual**
   app/BLIB/native owner, before START with no optional publication.
   JOB 2195's G!14 and G!200 fixture rejection is not that proof.
   A test-only harness can establish this R.0 preflight contract;
   the actual integrated registrar and transactional writes are
   explicitly **R.1 implementation and acceptance**.
5. **Remaining negative validation and diagnostic coverage.**
   JOB 2203 establishes the **1003/1006 count envelope**, not
   all IDs. Document the expected validation order and produce
   separately bounded evidence for wrong extents, corrupt lengths,
   invalid nonzero finalizer targets, overflow, and identifier or
   dependency faults to the extent feasible without modifying
   accepted code. Document what must wait for integrated R.1.
6. **R.0 gate decision and scope of deferral.** After items above,
   obtain an explicit owner acceptance of the documented R.0
   evidence and any precise deferrals. A contract may be accepted
   ahead of integrated code, but a test-only pass must not be
   misrepresented as verified production behavior.

## Explicit R.1 / later work — not a condition to implement during R.0

- Adapt `BCPLMAIN` once to consume the version-1 empty registry and
  selected descriptors, validating all selections before START and
  publishing only after success.
- Exercise real pre-START RC=12 and deterministic diagnostics using
  a startup-safe channel independent of uninitialized BCPLIO.
- Integrate the conventional MVS finalizer ABI into FINISH/STOP,
  execute exactly once in reverse order, preserve STOP(n), handle
  returned error 2001 and retain IOFIN/MEMDRAIN behavior.
- Exercise empty and selected-registry native applications and
  full regression; R.2 owns broader A/B/A+B interoperability, and
  R.3 owns packaging and final accepted-object deployment decisions.

## Review conclusion

**Decision G: approved and isolated boundary evidence PASSED
(JOB 2203).** R.0 has made substantial, repeatable progress,
but its specified ABI/ownership/QUERY evidence and scope review
are **not yet complete**. **Keep R.0 open; do not start R.1 or change
accepted `BOOT_OBJ` objects.** Avoid inventing new milestone
or march numbers. GitHub is the source of the contract and evidence,
and credential-bearing JCL/full JES dumps remain in ignored
`workarea/`.
