# DR.5 — Final evidence reconciliation and qualified closure recommendation

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.5 — Validation and Reconciliation (IN PROGRESS)  
**Date:** 27 November 2026 EST  
**Reviewed documentation and oracle revision:** `1851fae57d9fd0508d61a41f66030de348142cbc`  
**Disposition:** Required verification PASS at approved scope; qualified closure recommended, not yet authorized. DR.6 NOT STARTED.

## Verification reconciliation

The [final offline receipt](dr5-offline-verification-and-target-gates-20261127.md) records Actions run 46087048256, job 140798947580, at `c5b56cef0e2f9aa830a9b49631868cbc5d380b02`: 963 checker unit tests, 38 release unit tests, project inventory, bootstrap inputs and DEBUGINT preflight all PASS, zero gate failures. Hosted MVS integration remains deferred until milestone closure.

The [DEBUGINT native record](dr5-debugint-native-baseline-20261127.md) preserves the reproduced signed-operand defect and private/installed six-record correction evidence, including signed extrema. The [first attempt and target gate record](dr5-clean-room-first-attempt-20261127.md) preserves the failed JOB 1379, diagnosed compiler workspace exhaustion, BLIB-specific P2000 reservation and interpreted-completion gate before RAW OPEN. Private JOB 1382 passed all seven steps and interpreted CODE=0; negative JOB 1383 retained interpreted CODE=8, COMP RC0, FIXASM RC8 and flushed ASMBLIB/INSTALL. No installed BLIB replacement in these private jobs. ICINT19 return-code convention unchanged.

| Target gate | Actual accepted result |
| --- | --- |
| 1 — Unattended clean-room reconstruction | `e922d3daff98181f7e90c8673e15aedca4a9c461`, Step 0 onward, routine driver with batch population, rebuild/log RC0, 8m 05s |
| 2 — Fresh independent installed inventories | Exact ten BOOT_OBJ members and three EXT_OBJ members; both inquiry/log/oracle RC0 |
| 3 — Consolidated production regression | `a70a424567d670ca8ff60d29da1663903663d09d`, 219 PASS, 0 FAIL, 1 expected SKIP (083), 0 BLOCKED; regression/log/archive RC0; 13m 40s |

Gate 3 passed mr10 12, mr10-coroutines-supported 5, bootstrap 149 (one expected SKIP), runtime-extensions 17, bcpltime 4, bcplqsam 17, coroutines 13, coroutine-contract 2. Device cases 175–176 explicitly authorized and passed; private QSAM cases 198–200 passed. No overlapping historical diagnostics counted. MR10 skip/blocked counts are unavailable rather than independently measured zero. Gate 2 directory membership is not byte identity or execution. Gate 3 production profile does not imply every extension case uses installed objects.

## Original reconstruction payloads

Owner ran a read-only audit of retained rebuild.log and original printer reports at `1851fae57d9fd0508d61a41f66030de348142cbc`, using tools/mvs/job-summary, tools/mvs/dump-report-for-job and unchanged [verify_payload](../../../tools/reconstruction/verify.py). No new JES jobs were submitted.

| Payload | JOB | Executed steps | Successful interpreted records | Verdict |
| --- | ---: | ---: | ---: | --- |
| IC19BLD | 1424 | 3 | 0 | PASS |
| CAMBBLD | 1436 | 23 | 22 | PASS |
| BLDBMAIN | 1445 | 14 | 0 | PASS |
| BLIBBLD | 1448 | 7 | 1 | PASS after report recovery |
| BLDCORCO | 1450 | 4 | 0 | PASS |
| BLDCORLB | 1452 | 4 | 0 | PASS |
| BCPLDEMO | 1459 | 4 | 0 | PASS |
| BCPLTIME | 1461 | 4 | 0 | PASS |
| BCPLQSAM | 1463 | 4 | 0 | PASS |

All required step inventories and zero step return codes, applicable program identities, IFOX severity records, interpreted completions and applicable IEBCOMPR checks passed under that oracle. BLIBBLD has no IEBCOMPR requirement. The initial audit reported 8 PASS / 1 FAIL (RC1): strict UTF-8 subprocess decoding raised on byte 0xBD before BLIBBLD verification. Recovery read original launcher JOB 1447 and payload JOB 1448, both retrieval RC0, preserved 203062 raw report bytes with 15 undecodable bytes using reversible surrogateescape; SHA-256 0001382acd3e2765552b3c4ae92156796c1a2c501fc489c3c554708c9cae52a4. The unchanged oracle passed seven steps, two IFOX severity-zero records and one exact successful interpreted completion; recovery RC0. Aggregate PAYLOAD AUDIT: 9 PASS, 0 FAIL. The failed initial audit remains recorded, not erased.

Rebuild stage records 0/1/2/3/5/6/7/8/9 all RC0, respectively 6/0/220/25/45/61/35/51/42 seconds; Step 4 is not executed by this routine driver. Built-in BOOT_OBJ inventory PASS (10 exact members); installed coroutine compiler JOB 1454 and native JOB 1455, IFOX/IEWL/GO all RC0000, installed verification PASS. The independent inventories and consolidated production results above remain distinct gates.

Private evidence: mvs-state/dr5-debugint/run-zo69cmat/ and run-c2qfuajf/; mvs-state/dr5-clean-room/; mvs-state/dr5-blib-workspace-p2000/; mvs-state/dr5-blib-build/; mvs-state/dr5-clean-room-second/rebuild.log, inventory/, payload-audit/ and payload-audit/blibbld-recovery/; mvs-state/dr5-production-regression/regression.log and workarea.tar.gz. Coordinator receipt workarea/project-regressions/20261128T024630Z-54880-nkvpb0mv/summary.json. Evidence rests on owner-supplied actual transcripts and reviewed oracles, not independent access to the operator's raw files. Preserve successful and unsuccessful evidence, authenticated decks and raw reports privately. No credentials or raw reports committed.

## Documentation reconciliation and retained qualifications

All thirteen product and five project manuals (152 chapters) remain committed. The five reference manuals govern only their individually approved public contracts; the selection-macro transfer is complete. The [navigation audit](dr5-documentation-navigation-and-reconciliation-audit-20261127.md) records 715 literal relative-link occurrences and eight heading fragments at its reviewed revision, not a fresh repository-wide certification. Current procedural and reference status and regression totals are reconciled in the documentation catalog, reconstruction and development guides, Project Tools reference, retained canonical runbook and test inventory. Earlier campaign counts and failures remain historical evidence.

- Public contract transfer does not transfer private assembler or helper interfaces, source/configuration authority, global allocation, release manifests, registry, independent oracles or frozen release documents. Exhaustive private-interface, pointer/register, diagnostic and multifault coverage remains qualified.
- DEBUGINT detailed behavior remains outside the normative transfer; G!150 remains provisional and conflicts with historical FORMTREE:150. No allocation change or native-running compiler compatibility claim.
- Historical BLIB diagnostic limitations accepted by the owner; no unsupported postmortem reconstruction. MR10 original manual fixed-stack activation remains a genuine historical FAIL, not SKIP or XFAIL. Case 083 remains expected SKIP, not measured complete storage reclamation.
- BCPLQSAM private rollback evidence is not a guarantee of genuine exceptional MVS CLOSE recovery; bounded registrar structural precedence is not an exhaustive simultaneous-fault ordering. Preserve all package-specific scope limitations and earlier failures.
- DR.0 repository-wide inbound dependency and individual-file certification incomplete; outgoing navigation is not proof that old paths may be retired. No source-local paths removed. DR.4 defers dedicated documentation transformation tests, offline rendering and expanded distribution; preserve existing Markdown and MVS FB80 release representation.
- Routine reconstruction verified; guarded controller live integration and new release-driver live acceptance remain pending. No new release candidate, published RC4 change, hosted MVS integration or native distribution certification. Historical redistribution rights and unfinished native-running Cambridge Compiler remain separate qualifications.
- The printer-report audit's strict UTF-8 transport assumption was corrected for the single recovery only. No general tool encoding redesign or oracle relaxation is implied.

## Recommendation

Accept DR.5 — Validation and Reconciliation as CLOSED (qualified) on explicit owner approval of this evidence and the retained qualifications. No additional reconstruction, installation, inventory, device or regression campaign is required without a demonstrated defect or changed scope. DR.6 — Acceptance and Closure remains NOT STARTED until owner direction; its maintenance policy, release integration and final milestone acceptance are separate. No formal march closure is effected by this recommendation.
