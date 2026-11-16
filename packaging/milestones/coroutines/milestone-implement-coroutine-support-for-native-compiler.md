# CO.6 — Formal qualified acceptance review candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.6 — Common Coroutine Behavioral Contract and Cross-Compiler Verification  
**Status:** AMENDED — SUPPORTED-SUITE MVS VERIFICATION PENDING; **NOT CLOSED**  
**Prepared:** 16 November 2026  
**Tested GitHub `main`:** `7e41425cc272c68edea792b1d16b1b2c783eb556`  
**Evidence classification:** OWNER-REPORTED MVS/JES suite receipts; complete individual raw JES reports were not independently inspected in this conversation.

## Consolidated MVS acceptance campaign

The operator executed the planned campaign using two separate coordinator invocations. The seven PASS-eligible suites ran together (with production native profile and explicit BCPLQSAM device authorization), followed by the independent five-case historical MR10 coroutine diagnostic selection. Two separate coordinator invocations are intentional: the coordinator stops after a failed suite, and the original MR10 static-frame case must remain a genuine FAIL.

| Selection | PASS | FAIL | SKIP | BLOCKED | Coordinator result |
| --- | ---: | ---: | ---: | ---: | --- |
| `mr10` | 12 | 0 | 0 | 0 | PASS |
| `bootstrap` | 145 | 0 | 1 (083) | 0 | PASS |
| `runtime-extensions` | 13 | 0 | 0 | 0 | PASS |
| `bcpltime` | 4 | 0 | 0 | 0 | PASS |
| `bcplqsam` | 14 | 0 | 0 | 0 | PASS, including authorized device cases |
| `coroutines` | 13 | 0 | 0 | 0 | PASS; existing native cases 177–189 |
| `coroutine-contract` | 2 | 0 | 0 | 0 | PASS; both MR10/native paired cases |
| **Seven PASS-eligible suites** | **203** | **0** | **1** | **0** | **PASS / RC=0** |
| `mr10-coroutines` | 4 | 1 | 0 | 0 | **FAIL / RC=1**, genuine historical exception |
| **All eight selections** | **207** | **1** | **1** | **0** | **Qualified result; not an all-PASS run** |

The source-controlled `coroutine-contract` suite checked `co6-pair` (11 exact ordered records) and `co6-nested` (18 exact ordered records). Each source pair separately executes interpreted MR10/ICINT19 and Cambridge-generated native System/370, and validates the relevant compiler phases, MR10 completion codes, IFOX/IEWL/GO job steps, retained JES records and exact output oracle. Both individual cases returned PASS in the new regular coordinator.

The `mr10-coroutines` selection checked all five accepted identities:
compiler-probe, frame-layout-probe, resumeco-chain and
create-delete-static-pool **PASS**;
`10-coroutines/fixed-stack-producer-consumer` **FAIL** with
`interpreted CODE expected 0, got ['-1']`.
The narrow diagnostic continuation allowed the last two probes to finish without reclassifying the original failure. **No accepted source, golden oracle, expected CODE or test status was overwritten to make this run appear green.**

### Operator-local evidence

- PASS-eligible coordinator summary:
  `workarea/project-regressions/20261116T130728Z-35427-w963446s/summary.json`;
  operator log:
  `mvs-state/reconstruction-evidence/co6-final-regressions-20261116T130728Z.log`.
- Historical coroutine diagnostic coordinator summary:
  `workarea/project-regressions/20261116T131744Z-56157-nsm6p61_/summary.json`;
  operator log:
  `mvs-state/reconstruction-evidence/co6-final-probes-20261116T130728Z.log`.
- The separately executed first paired candidate previously passed at
  `workarea/co6-pair/20261116T123048Z-sfas9clu`;
  the second passed at
  `workarea/co6-nested/20261116T124503Z-mczybqy0`.
  The new coordinated 2/2 PASS supersedes the need for another independent pair rerun.

## CO.6 acceptance-gate assessment

| Governing gate | Observed evidence | Recommendation |
| --- | --- | --- |
| Source-controlled MR10 diagnostic with faithful classification | All five exercised: four PASS, one original CODE=-1 FAIL; no XFAIL/SKIP or patched fixture | **MET with explicit qualification** |
| Common valid first activation and argument/result transfer | `co6-pair` and `co6-nested` both interpreted and native PASS with exact record oracles | **MET** |
| Suspended locals/nested continuations, RESUMECO parent handoff and busy refusal | Two-worker `co6-nested` PASS under both paths; 18 strict records | **MET within tested bounded domain** |
| Ordinary worker return/re-entry | One-worker `co6-pair` PASS under both paths; 11 strict records | **MET within tested bounded domain** |
| Delete/reuse known-live inactive workers | `co6-nested` PASS under both paths and native `coroutines` 13/13 PASS | **MET within tested bounded domain** |
| Fresh coordinated production regressions | Six established suites 201 PASS, zero FAIL/BLOCKED and one expected SKIP 083; `coroutine-contract` additional 2/2 PASS | **MET** |
| Owner approval for the CO.6 historical first-activation exception and formal closure | Previous CO.0 qualified disposition exists, but this CO.6 decision is not yet given | **PENDING OWNER DECISION** |

## Conditions and limits of proposed qualified acceptance

The original fixed-stack producer/consumer uses an incompatible manually assembled initial MR10 frame. Its `CODE=-1` outcome remains an actual negative result. The separately named corrected-frame candidate passed the canonical interpreter in CO.0 JOB 5321; this establishes a supported *valid-frame* path, **not** retroactive PASS for the original fixture. A distinct later corrected-frame JOB 7693 returned driver RC=0, but the user's compact excerpt did not independently establish its entire record oracle.

CO.6 verifies *program-visible application behavior*, not identical interpreter/native coroutine descriptors, stack frames, global-number layouts or machine code, and not a natively executing Cambridge compiler. The accepted native **Approach A/S1** constraints remain a root and at most two live workers, checked **1024-word** stacks, known-live handles, and permanent coroutine globals **G!289–300**. Neither arbitrary dangling-pointer safety, unlimited stack sizes/workers, preemption, abnormal cancellation, system exhaustion recovery nor complete historical source/binary compatibility was verified.

Retain CO.5's original Bootstrap case 117 IEWL **SB2D** incident in JOB 6745 as a failed attempt even though the case and subsequent full campaigns passed; its underlying cause remains unproven. The CO.5 Git-backed ten-object clean-room rebuild and installed-only verification remain accepted previously recorded evidence, **not a fresh rebuild performed by this CO.6 campaign**.

No production BCPL/IFOX/IEWL object, public API/global allocation, distribution tape or published release is modified or authorized by this proposed qualified closure. Only the owner can authorize formal CO.6 closure.

## Proposed owner decision — NOT YET APPROVED

> Close **CO.6 — Common Coroutine Behavioral Contract and Cross-Compiler Verification (qualified)**, accepting both independently MVS-verified paired BCPL behaviors and the fresh seven-suite 203-PASS / one expected SKIP production campaign. Retain the separately executed historical `mr10-coroutines` diagnostic as **four PASS, one genuine FAIL**, explicitly accepting its incompatible manually constructed first-activation frame as a bounded historical exception rather than silently changing its source, golden output or status. Preserve existing CO.5 Bootstrap 117 SB2D, Approach A/S1 resource limits, and release restrictions. Authorize no new official march, production runtime changes or distribution publication through this decision.

**Owner approval: PENDING. CO.6 remains IN PROGRESS.**

## 16 November 2026 — amendment: supported-fixture acceptance pending

After this review candidate was drafted, the owner explicitly chose
to resolve the suite organization rather than accept a standalone
failing coroutine *regression* as the final result. The original
historical FAIL remains an actual negative result, but the accepted
valid-frame candidate is being promoted under its **own supported
test identity**. The five-case `mr10-coroutines-supported` suite
must complete one fresh integrated ICINT19/JES run, distinct from the
five-case historical `mr10-coroutines` diagnostic.

**This previous acceptance proposal is NOT READY for owner approval
until the new supported suite is MVS-verified.** The earlier
203-PASS regular result and the 4-PASS/1-FAIL historical result
remain valid, dated evidence for the previous Git revision; they
must not be overwritten or retrospectively reclassified. After the
new campaign, update this recommendation with the actual counts
and a newly tested revision. CO.6 is still IN PROGRESS; no closure,
production object change or distribution release is authorized.

## 16 November 2026 — final supported/historical MVS campaign completed

At **tested** GitHub `main` `216b6707c404a91c796ed8f1419a99ef172b184a`, the owner executed the
single eight-suite supported campaign with `--profile production`,
`--allow-device`, and `--progress`: **RC=0,
PROJECT REGRESSION RESULT: PASS; 208 PASS, zero FAIL/BLOCKED,
one expected Bootstrap SKIP 083**. These are six established
suites (201 PASS, one SKIP) plus the verified
`mr10-coroutines-supported` selection (5 PASS) and the
`coroutine-contract` paired selection (2 PASS).
The supported suite's **five real interpreted MVS tests** passed;
this supersedes only the earlier MVS-UNVERIFIED status of the
supported runner, not historical evidence.

A separate original historical `mr10-coroutines` diagnostic
returned **RC=1/FAIL** with **4 PASS, one genuine original
`fixed-stack-producer-consumer` interpreted CODE=-1 FAIL**.
No original fixture, golden, accepted code or manifest was changed.
The four overlapping historical passing identities are not new
unique supported test cases.

Evidence: `workarea/project-regressions/20261116T151624Z-56400-i4ueoalx/summary.json`,
`workarea/project-regressions/20261116T152532Z-76357-_s4f83jy/summary.json`;
operator logs `mvs-state/reconstruction-evidence/co6-supported-final-20261116T151623Z.log`
and `mvs-state/reconstruction-evidence/co6-historical-final-20261116T151623Z.log`.
The submitted terminal excerpts show status/counts, not the
raw JES reports or the whole receipts independently.

The [revised CO.6 formal qualified acceptance review candidate](co6-qualified-acceptance-review-candidate-20261116.md)
documents met gates and retained limits. **CO.6 remains IN PROGRESS
until explicit owner qualified-closure approval.**
No MVS reruns, source/runtime changes or new march are requested.
