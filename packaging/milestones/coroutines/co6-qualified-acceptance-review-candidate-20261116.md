# CO.6 — Formal qualified acceptance review candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.6 — Common Coroutine Behavioral Contract and Cross-Compiler Verification  
**Status:** READY FOR OWNER REVIEW — **NOT CLOSED**  
**Prepared and updated:** 16 November 2026  
**MVS-tested source:** GitHub `main` `216b6707c404a91c796ed8f1419a99ef172b184a`  
**Evidence classification:** OWNER-REPORTED MVS/JES project-coordinator results. Source-controlled runners validate their own job and oracle receipts. The full individual raw JES reports and JSON receipts are preserved in the operator workarea and were not independently opened in this conversation.

## Final supported campaign — MVS PASS

The owner performed one combined, fail-stop, **eight-suite supported regression campaign** on MVS 3.8J with the `production` profile and explicit BCPLQSAM printer/punch authorization. Project coordinator returned **RC=0, PASS**.

| Suite selection | PASS | FAIL | SKIP | BLOCKED | Outcome |
| --- | ---: | ---: | ---: | ---: | --- |
| `mr10` | 12 | 0 | 0 | 0 | PASS |
| `mr10-coroutines-supported` | 5 | 0 | 0 | 0 | PASS |
| `bootstrap` | 145 | 0 | 1 (083) | 0 | PASS |
| `runtime-extensions` | 13 | 0 | 0 | 0 | PASS |
| `bcpltime` | 4 | 0 | 0 | 0 | PASS |
| `bcplqsam` | 14 | 0 | 0 | 0 | PASS, including device cases 175–176 |
| `coroutines` | 13 | 0 | 0 | 0 | PASS, native cases 177–189 |
| `coroutine-contract` | 2 | 0 | 0 | 0 | PASS, both paired MR10/native cases |
| **Supported total** | **208** | **0** | **1** | **0** | **PASS / RC=0** |

The five-case `mr10-coroutines-supported` selection comprises
`compiler-probe`, `frame-layout-probe`, `resumeco-chain`,
`create-delete-static-pool` and the distinct
`fixed-stack-co0-candidate`. This is the **first fully coordinated
MVS PASS for the new supported selection**. The versioned runner
checks the accepted four original cases using their existing
golden/JES verifier and the corrected-frame candidate using an
independent exact ten-record producer/consumer oracle,
**ten zero-RC JES steps** and **three zero-valued interpreted
completion phases**. The corrected source retains the valid
`P=C+3` / `COBOOT` initial frame.

The paired `coroutine-contract` selection also passed both
`co6-pair` (eleven ordered records) and `co6-nested`
(eighteen ordered records), with independent MR10/ICINT19 and
Cambridge-generated native System/370 compilation/execution receipts.
These demonstrate the agreed *observable* cooperative coroutine
behavior within the explicitly bounded contract, not ABI/frame
identity across compilers.

### Supported execution evidence

- Coordinator JSON: `workarea/project-regressions/20261116T151624Z-56400-i4ueoalx/summary.json`
- Retained console/job summary log: `mvs-state/reconstruction-evidence/co6-supported-final-20261116T151623Z.log`
- Verified Git code revision: `216b6707c404a91c796ed8f1419a99ef172b184a`
- Owner-reported terminal line: `PROJECT REGRESSION RESULT: PASS`; coordinator **RC=0**

## Separate original historical diagnostic — genuine FAIL retained

The owner ran the **unchanged** five-case `mr10-coroutines`
historical diagnostic in a **separate** coordinator invocation.
It returned **4 PASS, 1 genuine FAIL, 0 SKIP, 0 BLOCKED; RC=1**.
The failure remains precisely
`10-coroutines/fixed-stack-producer-consumer` with
`interpreted CODE expected 0, got ['-1']`.

The original manually constructed first-activation frame
(`C!0 := C`) does not meet canonical ICINT19/ICLIB
`CHANGECO` continuation requirements. The original source,
original exact golden, accepted expected CODE=0 and frozen
17-entry historical development-probe manifest are **untouched**.
The corrected, separately named `fixed-stack-co0-candidate`
PASS **does not convert that original FAIL** into PASS, SKIP,
XFAIL, OBSERVED or a successful negative test.

The four historical PASS identities overlap the supported
selection; therefore **do not add historical diagnostic results
to the 208 distinct supported-case total** and describe the
combined execution as an all-PASS run.

- Diagnostic JSON: `workarea/project-regressions/20261116T152532Z-76357-_s4f83jy/summary.json`
- Diagnostic operator log: `mvs-state/reconstruction-evidence/co6-historical-final-20261116T151623Z.log`
- Owner-reported terminal line: `PROJECT REGRESSION RESULT: FAIL`; coordinator **RC=1**, consistent with the preserved exception.

## CO.6 governing acceptance gates

| Requirement | Observed evidence | Assessment |
| --- | --- | --- |
| Historical MR10 originals remain honestly classified | Five original probes run: four PASS and original fixed-stack CODE=-1 genuine FAIL | **MET, qualified** |
| Valid-frame supported interpreted coroutine regression | All five `mr10-coroutines-supported` cases PASS, including corrected-frame fixed-stack program | **MET** |
| Independently compiled interpreted/native behavioral parity | `co6-pair` and `co6-nested` PASS, complete exact-output and JES contracts enforced by their runners | **MET in tested common domain** |
| First activation, value transfers, nested continuations, preserved locals | Both shared oracles and 13 native coroutine cases PASS | **MET in bounded domain** |
| RESUMECO parent chain, busy refusal, natural return/re-entry, deletion/reuse | Both shared oracles PASS | **MET in bounded domain** |
| Regular full production regressions | Six original suites: 201 PASS, zero FAIL/BLOCKED, expected SKIP 083 | **MET** |
| Separate owner approval for CO.6 qualified closure | Not yet provided | **PENDING** |

## Qualifications preserved from prior marches

The accepted native **Approach A/S1** scope remains a root coroutine
with at most **two live registered worker coroutines**, separately
checked **1024-word** worker stacks and approved coroutine
**G!289–300** global assignments. The ABI, descriptor layout and
compiler execution modes are not shared between MR10 and native
System/370. The Cambridge compiler currently executes as INTCODE
under ICINT19 while generating native System/370 application code;
no native-running Cambridge compiler is claimed.

Not verified: general stale/freed-pointer or ABA-proof recovery,
unbounded workers/stacks, actual GETMAIN exhaustion, exceptional
cancellation/abend recovery, preemption/reentrancy, complete
historical frame compatibility, or full historical source/binary
compatibility.

The original Bootstrap case 117 IEWL **SB2D** abend in JOB 6745
remains a recorded failure despite subsequent isolated and full-suite
PASS. Its cause has not been independently resolved. The accepted CO.5
Git-source **ten-object** clean-room reconstruction, production
`BOOT_OBJ(BCPLCO)` and `BOOT_OBJ(COROUTIN)` installation and
installed-only verification remain the existing evidence, **not a
fresh clean-room rebuild performed as part of CO.6**.

This review does not authorize production object changes,
unverified historical-image rollback, distribution tape publication,
or a new official march.

## Earlier CO.6 checkpoint preserved

The preceding checkpoint at
`7e41425cc272c68edea792b1d16b1b2c783eb556`
contained **203 PASS, one expected SKIP** across seven supported
suites, plus the separate four-PASS/one-FAIL historical diagnostic.
That prior result remains valid for its tested revision.
At the new tested revision `216b6707c404a91c796ed8f1419a99ef172b184a`, the five-case
supported MR10 suite was added and passed: **208 PASS,
one expected SKIP**, with the separate historical FAIL unchanged.

## Proposed owner decision — NOT YET APPROVED

> Approve and close **CO.6 — Common Coroutine Behavioral Contract
> and Cross-Compiler Verification (qualified)**. Accept the MVS-tested
> eight-suite **208 PASS, zero FAIL/BLOCKED, one expected SKIP 083**
> supported campaign; the independent shared MR10/native coroutine
> oracles; the separate **five-PASS** supported MR10 coroutine suite,
> including the corrected-frame `fixed-stack-co0-candidate`; and
> the distinct original historical diagnostic as **four PASS,
> one genuine CODE=-1 FAIL**. Preserve the original fixture,
> original golden, original expected CODE, Bootstrap 117 SB2D
> history and Approach A/S1 architectural limits. Authorize no
> runtime object changes, public release or new official march
> through this acceptance alone.

**Owner approval: PENDING. CO.6 remains IN PROGRESS, NOT CLOSED.**
