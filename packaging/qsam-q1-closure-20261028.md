# Milestone QSAM — Q.1 owner closure (28 October 2026)

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** **Q.1 — Linkage & OPEN/CLOSE skeleton**  
**Owner disposition:** **CLOSED** by explicit approval on 28 October 2026  
**Next march:** **Q.2 — Fixed logical records OPEN / NOT ACCEPTED**  
**Final native diagnostic source:** [GitHub main 7f00ff897c94](https://github.com/cbmira01/BCPL-for-MVS/commit/7f00ff897c947d2140e5df6db95a935f18b4de41)

## Owner decision and revised acceptance scope

Following review of the native evidence through **JOB 6636**, the owner approved acceleration, expressly deferred the remaining Q.1 checks into consolidated regressions/hardening, and instructed: **"Approve. Proceed to Q.1 close, Q.2 open."**

**Q.1 is CLOSED on a deliberately narrowed exit gate.** The demonstrated, accepted capability is the separately selectable BCPLQSAM System Extension using the BCEX/BCRG version-1 registration and **QSAMSVC:200**: independent OPEN/INFO/CLOSE of three F1024 DDs with explicit validated GO geometry, a sixteen-slot handle lifecycle, output OPEN/INFO/CLOSE, and the normal FINISH finalizer automatically closing all sixteen outstanding handles.

The original Q.1 milestone gate also required clean failures, independently demonstrated STOP cleanup, and no regression. Those obligations **were not fully established** and are **explicitly deferred, not deemed PASS**. This owner waiver is limited to the Q.1 closure prerequisites; it is not evidence of untested behaviors or acceptance of Q.2.

## Accepted native results and limits

| JOB | Case | Observed outcome |
| --- | --- | --- |
| 6603 | QUERY-only BCPL linkage/registration | Native IFOX, IEWL and GO RC=0000, expected application result |
| 6620 / Q13DD | Three independently allocated F1024 input DDs | Ten steps RC=0000; OPEN/INFO/CLOSE, repeated-CLOSE error, native PASS; explicit reader DCB required for this tested case |
| 6627 / Q16FIN | Sixteen-handle application | Ten steps RC=0000, native application PASS; independent finalizer trace not proved by that job |
| 6628 / Q16STP | Sixteen-handle application and STOP(8) | Application PASS, GO RC=0008 as requested; independent finalizer resource-accounting trace not proved |
| 6630 / Q1OUT | Output OPEN/INFO/CLOSE | GO RC=0000 and native PASS; no record transfer attempted |
| **6636 / Q1FDIAG** | **Sixteen-handle normal FINISH** | **All ten steps RC=0000, zero assembler flagged statements and severity, native 16-handle PASS once, observed 16-CLOSE finalizer cleanup and status zero** |

The sixteen-handle application exercises the 17th OPEN refusal, closing and reopening a table slot with a new opaque identity, rejection of an old stale handle, INFO geometry, and READ/WRITE unsupported status appropriate to Q.1.

### JOB 6636 finalizer observations

The operator's single protected Q1FDIAG submission used a disposable 4,311-card deck derived from the preserved compiled Q16FIN case, substituting the five-counter-corrected BCPLQSAM assembler from **7f00ff897c947d2140e5df6db95a935f18b4de41** plus a test-only finalizer probe overlay. The JCL SHA-256 was **49d7d6336e7eb8ec707e29df07aaf2279446f4044b9ca68e12086c1998fd136f**. No permanent MVS object PDS was written.

All three correlated native console logs contained the same ordered Q1F records:

| Checkpoint | Hex values | Meaning |
| --- | --- | --- |
| Entry E | 00000000:00000010:00000010:00000010 | Reason 0; live 16, DCB 16, stage 16 |
| Post-loop L | 00000010:00000000:00000000:00000000:00000000 | 16 successful CLOSEs; resources 0; status 0 |
| Return X | 00000010:00000000:00000000:00000000:00000000 | Same successful results at return |

Two 3033 console log copies had byte-identical bounded intervals (SHA-256 **65d736527bf9fffee3756caeeb9f36910793bc20340aabb43feee36a5b3e398e**, 440 bytes). The hardcopy.log interval had different framing (SHA-256 **91147444718b60bcec6f0a5674c762ded3f332d7d227ab11c3fd11661769e000**, 1,271 bytes) but exactly the same Q1F values. The first evidence script failed closed because three interval copies existed; the follow-up comparison required identical complete log text, which is unnecessary for log formats with different framing. Consequently the strict native evidence checker **was not rerun on a selected canonical console interval**; do **not** claim an automated checker PASS. The owner accepts the agreeing actual native observations for normal FINISH closure, without resubmitting JOB 6636.

Preserved operator-local evidence: **workarea/bcplqsam-q1/q1fdiag-6636-review-BAb5IAzu** contains summary/report, with the submitted JCL, SHA/readiness and one-attempt markers under the same ignored workarea; original console streams remain under **mvs-state/log/**. All prior JOB evidence and attempt markers remain untouched.

## Deferred regression and hardening ledger — not yet verified

1. **Q1NEG:** JOB 6629 ended GO RC=0008 without negative-case PASS. The caller is known to retain a nonzero reserved Q!1 before its invalid-handle checks. Repair the test caller and verify invalid DDNAME/missing DD/mode/reserved word/invalid handle in the consolidated regression.
2. **STOP finalizer:** JOB 6628 established requested STOP(8) RC preservation; native sixteen-CLOSE resource accounting remains to be observed on that path.
3. **Failed-OPEN and returned-CLOSE exceptions:** resource rollback, surviving handles, ownership quarantine and finalizer accounting status need focused later validation. Preserve the approved no-blind-retry/no-unsafe-free policy; rare injection cases may move to Q.5 hardening by bounded owner decision.
4. **Omitted GO DCB geometry:** retain the approved **fail-closed hybrid** pre-OPEN policy. No universal explicit-DCB API mandate and no speculative OBTAIN/DSCB recovery. The separate test-only OBTAIN JOB 6631 ended S322 after a first Q00 observation; it is not a production fallback demonstration.
5. **Full regression:** no fresh post-7f00ff89 complete native 00–162 baseline panel ran before Q.1 closure. The owner explicitly deferred this check to the next consolidated acceptance panel; do not reuse older panel results as if they covered the Q.1 fix.
6. **Console evidence automation:** compare job-correlated Q1F values, not whole-file bytes, when logs have different framing. No repeat native Q1FDIAG run is required.

Q.2's consolidated panel should include the ordinary Q.1 negative, FINISH/STOP and lifecycle regressions along with Q.2 fixed-record tests and the full native baseline. The exotic returned-CLOSE and optional geometry recovery issues are tracked for subsequent hardening, not claimed accepted.

## Release and authority boundary

The five-increment assembler fix and offline counter guard are already in authoritative GitHub main commit **7f00ff89**. This documentation-only closure does not alter sources, create a JES job, install/promote BOOT_OBJ, BOOT_DEVOBJ or EXT_OBJ, change accepted Core Runtime/Base Library/compiler objects, or accept the entire Milestone QSAM. Original dated Q.1 exploratory reports remain historical evidence.

**Owner disposition: Q.1 CLOSED; Q.2 OPEN / NOT ACCEPTED.** See [Q.2 kickoff](qsam-q2-kickoff-20261028.md).
