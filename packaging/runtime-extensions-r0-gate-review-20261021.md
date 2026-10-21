# Milestone Runtime Extensions — R.0 evidence and gate review

**Review date:** 21 October 2026.
**March under review:** **R.0 — Evidence and contract**.
**Next march:** **R.1 — Generic registration foundation** (**not started**).
**Gate disposition:** **NOT READY TO CLOSE R.0**. The shared QUERY
contract was [owner-approved](runtime-extensions-r0-query-abi-decision-20261021.md);
its isolated two-dispatcher native client test subsequently **PASSED
as JOB 2206**. See [verified JOB 2206 evidence](runtime-extensions-r0-query-job-2206-evidence-20261021.md).
The common QUERY ABI/client gate is **complete within the isolated R.0
scope**; the remaining provenance, ownership, actual-owner collision
and negative-validation obligations stay open. No permission to change
accepted runtime objects follows from this review.

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
| Historical G!76 | **JOBs 2199 and 2220**: real installed Core Runtime START preserves BLIB WRITEF when exported, and supplies WRITEST with no BLIB G!76 export | Both branches passed; JOB 2220 still links a temporary BLIB symbol, not a wholly BLIB-free runtime |
| Decision G | Owner-approved N/M=32, K=8, D=16, BCRG/BCEX maxima 540/368 bytes, diagnostic IDs 1001–1014/2001, proposed startup RC=12 | **JOB 2203** verified 14 numerical count/size scenarios; host tests cover more fields, not live registrar |
| Shared opcode-0 QUERY | Six-word prefix and -1/-2/-3 rules owner-approved; **JOB 2206** five steps RC=0000, ten host tests, two independently assembled dispatchers and actual GO marker | Test-local G!298/G!299 export bindings, not `BCPLREG` or matching production `BCEX` descriptors |
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

1. **Shared opcode-0 QUERY contract and isolated client verification —
   COMPLETE for R.0.** The
   [approved ABI](runtime-extensions-r0-query-abi-decision-20261021.md)
   fixes the six-word prefix, append-only size rules, version/bitmap
   semantics and errors. The [JOB 2206 two-dispatcher experiment](runtime-extensions-r0-query-job-2206-evidence-20261021.md)
   **PASSED** under actual MVS. Production `BCEX` matching, optional
   startup registration and BCPLQSAM remain outside this isolated test.
2. **Trusted build/link evidence for descriptor extents and deployed
   objects.** Require reproducible trusted begin/end and code-address
   provenance/MAP evidence under Decision A. Reconcile the 17 October
   clean-room build ledger with any subsequent `BOOT_OBJ` replacement
   before asserting the current installed members' exact source revision.
   Do not mistake JOB 2200 inventory or JOB 2197 relocation for a
   binary hash. The [approved stage-1 trusted-link probe](runtime-extensions-r0-decision-a-stage1-20261021.md)
   **PASSED ten actual MVS jobs (2207–2216)**; the
   [stage-1 evidence](runtime-extensions-r0-decision-a-jobs-2207-2216-evidence-20261021.md)
   includes reviewed JOB 2207 IEWL MAP/XREF, all step results
   and exact QOUT verification. The host rendered-source SHA-256
   manifest values were not supplied, and the remaining nine
   full IEWL MAP listings were not independently reviewed.
   Installed `BOOT_OBJ` byte identity remains open; its
   [stage-2 review](runtime-extensions-r0-decision-a-stage2-design-20261021.md)
   recommends a calibrated **read-only** object-deck comparison,
   and was then executed: **JOB 2217** calibrated IEBCOMPR
   (SAME RC=0000, expected DIFFER RC=0008), and **JOB 2218**
   compared the actual installed `BOOT_OBJ(BCPLMEM)` read-only
   against a fresh temporary 18-record object. The comparison
   **failed strict byte identity** due solely to the OBJ END
   run-day field; the separately owner-approved date-only
   [content-equivalence evidence](runtime-extensions-r0-decision-a-jobs-2217-2218-evidence-20261021.md)
   and its guarded report auditor distinguish this from a strict
   binary match. The incumbent's original Git build identity
   remains unproven.
3. **Effective global ownership scope.** **JOB 2220 now PASSED**
   the approved no-G!76-export fallback, with the temporary
   BLIB owner confirmed by actual IEWL MAP/XREF. With JOB 2199,
   both G!76 precedence branches are complete in the isolated
   R.0 scope; a BLIB linker symbol is still mandatory. See
   [JOB 2220 evidence](runtime-extensions-r0-g76-noexport-job-2220-evidence-20261021.md).
   The [G!150 owner review](runtime-extensions-r0-g150-startup-ownership-review-20261021.md)
   identifies the outstanding startup conflict. The
   [owner-approved test-only observer](../bootstrap-toolchain/probes/r0-g150-startup-probe/README.md)
   has passed 24 offline tests and synthetic JCL validation;
   real MVS execution, owner-address reporting and reviewed IEWL
   MAP/XREF are **pending**. No G!150 resolution is approved.

 Extend the per-executable
   ownership method beyond JOB 2197's single START application,
   review possible indirect Core Runtime writers and compiler
   allocations (including G!150), and record exact historical
   precedence exceptions. **JOB 2220 verifies G!76 when
   the linked temporary BLIB exports no G!76** (but does not
   demonstrate operation without a BLIB linker symbol). The [21 October ownership follow-up](runtime-extensions-r0-effective-owner-followup-20261021.md)
   distinguishes missing BLIB linkage from **a linked module
   exporting no G!76**; a temporary no-export BLIB fixture is
   owner-approved and prepared for the latter. The [fixed,
   test-only probe](../bootstrap-toolchain/probes/r0-g76-noexport-probe/README.md)
   passed 18 host tests and actual MVS/IEWL verification in JOB 2220. Source review distinguishes G6!48 save-area
   binding from G!48 publication and confirms FORMTREE:150
   versus DEBUGINT:150 as an unresolved compiler/core conflict.
4. **R.0 collision/transactionality evidence.** The source audit
   requests an isolated rejection against an **actual**
   app/BLIB/native owner, before START with no optional publication.
   JOB 2195's G!14 and G!200 fixture rejection is not that proof.
   A test-only harness can establish this R.0 preflight contract;
   the actual integrated registrar and transactional writes are
   explicitly **R.1 implementation and acceptance**.
5. **Remaining negative validation and diagnostic coverage.**
   JOB 2203 establishes the **1003/1006 count envelope**.
   JOBs 2207–2216 now verify isolated fixture rejection of
   1001–1006 (selected header/extent/length conditions) and
   1013 (a wrong-but-linked finalizer target), **not all variants
   or the production registrar**. Identity, dependency, collision,
   overflow and runtime pointer provenance checks still need
   bounded disposition; record what must wait for integrated R.1.
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
and JOB 2206 verified the approved shared QUERY ABI using two
independent test dispatchers. JOBs 2207–2216 passed the isolated
Decision A trusted-link panel; installed object identity remains
separate. The R.0 QUERY/client gate is complete,
but provenance, effective ownership, actual-owner collision rejection,
remaining negative validations and the final owner gate decision
remain outstanding. **Keep R.0 open; do not start R.1 or change
accepted `BOOT_OBJ` objects.** Avoid inventing new milestone
or march numbers. GitHub is the source of the contract and evidence,
and credential-bearing JCL/full JES dumps remain in ignored
`workarea/`.
