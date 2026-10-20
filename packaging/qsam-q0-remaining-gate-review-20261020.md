# Milestone QSAM — Q.0 remaining-gate review (2026-10-20)

**March:** Q.0 — Reconnaissance & contract. **Not closed.**
**Next March:** Q.1 — Linkage & OPEN/CLOSE skeleton (**not started**).
This is an evidence inventory and risk register; no new public API,
numeric maximum, or Runtime Extensions decision is approved here.
The authorities are `packaging/milestone-qsam.md`,
`packaging/bcplqsam-public-interface.md`, the Q.0 approved staging
record, and `packaging/milestone-runtime-extensions.md`.

## Mechanisms already demonstrated on MVS/TK5

| Area | Evidence | Scope / limit |
| --- | --- | --- |
| BCPL-to-assembler dispatcher ABI | JOB 2157 | Test-only G!200 binding, not generic R.0 registration |
| QSAM sequential FB/V/VB | JOBs 2159–2162 | Selected formats/lengths, not full size ceilings |
| Fixed-record boundaries | JOBs 2163, 2165–2167 | Specific tested F/FB sizes |
| Zero-data-length V/VB | JOBs 2168–2169 | Successful RDW-only logical records |
| Non-opening DDNAME inquiry | JOB 2170 | Tested present/missing DD, not universal error recovery |
| Incompatible OPEN | JOB 2171 | S013-20 abend demonstrates a nonrecoverable path |
| Non-opening geometry / empty EOF | JOBs 2172–2173 | Tested JFCB FB offsets, sticky EOF policy |
| Staged pending READ retry | JOB 2174 | Single statically staged FB80 reader |
| Conditional storage ownership | JOB 2175 | Real GETMAIN/FREEMAIN; injected explicit rollback |
| Shared rollback handler | JOB 2176 | Real small allocations, injected failure through handler |

## Remaining questions before owner accepts Q.0

1. **Real conditional allocation refusal and error return.** Observe
   an actual nonzero R15 from a bounded, single `GETMAIN RC` request,
   then cleanup and continued small allocation. The guarded experiment
   is **prepared, not run**. Do not equate a failing job with a safe
   returned-control failure.
2. **Exact practical record and storage limits.** Establish relevant
   TK5 DASD device type and dataset geometry; choose a *tested*
   supported per-handle stage maximum. An MVS-documented numeric ceiling
   is not automatically the BCPLQSAM limit. Verify what 16
   simultaneous handles imply for the selected stage size and job region.
3. **Effective INFO attributes.** Exercise the opened-DCB values and
   public mapping for RECFM, LRECL, BLKSIZE and supported *data-byte*
   maximum. JFCB pre-OPEN evidence alone does not prove post-OPEN INFO.
4. **Error semantics.** Document which missing DD, incompatible mode,
   SYNAD/GET/PUT and exceptional CLOSE conditions can return safely
   and which can abend. An S013-20 was observed; no promise of generic
   MVS abend recovery is permitted.
5. **Shared optional-module lifecycle (Milestone Runtime Extensions).**
   R.0 registrar/descriptor format, duplicate/missing package behavior,
   finalizer entry ABI/order, FINISH vs STOP(n) return-code policy, and
   exceptional implicit CLOSE treatment need explicit owner decision.
   Do not add a QSAM-only registration/finalizer mechanism.
6. **Owner Q.0 gate review.** Reconcile the accepted version-1
   BCPLQSAM Public Interface Specification with supported evidence,
   record permitted deferrals, and explicitly approve Q.0 before Q.1.
   A run of standalone assembler probes does not close Q.0 by itself.

**Production BCPLQSAM remains unimplemented.** Neither BOOT_OBJ nor the
accepted core BCPL runtime was changed by the Q.0 resource tests.
