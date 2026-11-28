# DR.5 — First clean-room reconstruction attempt stopped at BLIBBLD

**March:** DR.5 — Validation and Reconciliation (IN PROGRESS)  
**Date:** 27 November 2026 EST  
**Source revision:** `7b335e2932a82734113c60f62bffb9bd8df1ec6b`  
**Evidence:** `mvs-state/dr5-clean-room/rebuild.log`

Owner authorized the unattended batch clean-room reconstruction as the first of three distinct remaining target gates. The owner-reported shell transcript establishes two fresh JES2 idle responses before the rebuild, presence of both previously preserved DEBUGINT result files, and execution of `tools/reconstruction/rebuild-from-source --unattended --batch-populate`. Guide Step 7 completed RC0. Guide Step 8 stopped at the first job, BLIBBLD, launcher JOB 1378 / payload JOB 1379, because the submit helper reported JOB RESULT: FAILURE despite HIGHEST RC: 0000.

| Observed step | Program | RC |
| --- | --- | --- |
| COMP | ICINT19 | 0000 |
| PREPASM | IFOX00 | 0000 |
| PREPLK | IEWL | 0000 |

The summary reported ABEND detected and one or more bypassed steps, no assembler flags, highest assembler severity zero. The next step in the tracked [BLIBBLD job](../../../bootstrap-toolchain/jcl/blibbld.jcl) is FIXASM, which executes the temporary BLIBPREP load module. The later steps are ASMBLIB and INSTALL. The exact failing step, completion code, and cause require the retained JES report; do not infer a particular ABEND from the summary alone. The driver stopped at Step 8 RC1; total elapsed 6m 34s, rebuild RC1. No successful clean-room acceptance, independent installed inventory or consolidated regression is claimed. The previously accepted focused DEBUGINT verification remains historical evidence, not verification of the newly reconstructed target.

Preserve JOB 1379's report under the existing evidence directory, review its actual JES/system diagnostics and the tracked JCL before proposing a correction. Do not replay the rebuild or submit later steps as an unapproved resume. Any further destructive reconstruction requires a reviewed disposition and fresh authorization. No production code or JCL changed by this evidence record.

## Actual JES diagnostic and narrowed investigation

Owner supplied the retained JOB 1379 report extracts: IEC020I 001-4 in BLIBBLD FIXASM RAW, device 292, volume WORK03, temporary dataset SYS26331.T222221.RA000.BLIBBLD.CODE. IEC020I reports DCB EROPT=ABE or invalid code and/or missing SYNAD exit; IEF450I and IEF472I confirm S001 U0000. ASMBLIB and INSTALL were flushed. The dataset was subsequently deleted; no BLIB installation occurred in this payload. The report is retained at mvs-state/dr5-clean-room/job-1379-BLIBBLD.log.

The tracked BLIBBLD JCL is byte-identical (Git blob 01eb17f93b3ae5e08d8ac81a455325d1e50f6e9e) to the accepted CO.5 clean-room revision 788616e6d34325cbe6a9473edcc6be340da3e577. The ICINT19 assembler source also matches that revision. The bootstrap host and demotion generator have changed for DR.5's accepted compiler stream and newline work; this does not by itself establish a causal relationship. The compiler writes temporary FB80 CODE with BLKSIZE=80; FIXASM uses QSAM GET with the inherited dataset DCB attributes. S001-4 identifies the error disposition, not the underlying physical or record-format cause. Do not suppress the failure by changing EROPT to ACC or SKP. Obtain console evidence around JOB 1379 and the affected device/volume, and the compiler completion/allocation messages from the saved report before deciding on any new JCL, diagnostic or rerun. No code change or new submission is authorized by this record.

## Compiler completion evidence supersedes storage-only hypothesis

The owner supplied JOB 1379's COMP report: `Error near line 467:  Region too small`, `EXECUTION CYCLES = 6442369, CODE = 8`. The MVS ICINT19 step nevertheless reported RC0000, so the JCL COND gate admitted the later steps despite a failed interpreted compilation. The subsequent FIXASM S001-4 on RAW is consistent with an incomplete or unwritten CODE dataset; the exact QSAM failure mechanism is not proven. The Hercules startup log recorded WORK03 CCKD free-space/header inconsistencies and reported rebuilding free space; no contemporaneous device check is shown in the supplied excerpt. Preserve these as independent observations, not proof of a storage root cause.

Source review: demoted/trna TRNMESSAGE case 145 prints Region too small and sets the fatal report limit. demoted/trnb CHECKWORKSPACE computes SLACK=DVEC+DVECS-OBUFP and calls TRANSREPORT(145, CURRENTBRANCH) and STOP(8) when the minimum slack reaches zero. The historical master allocates WORKSPACESIZE=STACKSIZE-FREESTACKSIZE, with default FREESTACKSIZE=3000 and front-end Pnnn option. This is shared compiler workspace exhaustion, not evidence of an MVS GETMAIN failure; increasing JCL REGION alone does not enlarge the ICINT19 fixed 40001-word program vector. Obtain the actual compiler banner, tree-size and surrounding diagnostic records before choosing a workspace change. Also investigate BLIBBLD's interpretation of compiler completion before permitting any new installation. No correction or retry authorized by this record; no other target gate started.

## Measured workspace and compile-only diagnostic

Owner supplied JOB 1379's complete compiler diagnostic: resident program 27346 words, PROGVEC capacity 40001, free stack/work 12655, stack base 202384, stack end 215039, global capacity 700, globals used 382, highest global G!699. Cambridge stack size 12655, tree size 6486; error 145 near line 467 and CODE=8. The historical default free-stack reservation 3000 gives workspace 9655 and only 3169 words before the translator's declarations and OCODE consume the shared arena. The ICINT19 fixed vector capacity, rather than the JCL region alone, constrains that arena.

A single non-installing diagnostic uses the [P2000 parameter card](candidates/blib-workspace-verification/cambridge-parm-p2000.txt). It preserves the ordinary second-phase /N behavior and fills one 80-column option record with ignored slashes. The existing first-phase Pnnn option selects free-stack reservation; P2000 would provide 10655 workspace words, leaving 4169 before translation, an increase of 1000. This is an experiment, not a promoted stack-sizing policy. The assistant verified the exact parameter construction and arithmetic locally. Use the actual BOOT_SOURCE(BLIB) text read back from MVS and the resident CAMBCOMP; invoke the existing compile-mvs tool with the option override and a private output path. Its compiler completion parser requires exactly one CODE=0 and nonempty recovered code. Preserve JES evidence including stack and tree sizes, OCODE size, workspace utilization and completion. No persistent installed member changes, new clean-room attempt, or reduction of the default stack reserve is authorized by this probe. Success would establish sufficiency for this observed compilation only, not a general safe stack bound. If insufficient, review the actual result rather than reducing P repeatedly or silently changing ICINT19. The separate interpreted-CODE/JCL gate issue remains open.

## P2000 compile-only target result — PASS

Owner-reported actual execution at `99414c4e13dc31c3b6f3d5c768cbe5c1bb4de632`: JOB 1380 retrieved BOOT_SOURCE(BLIB), JOB 1381 (DR5BLP2) compiled it with resident CAMBCOMP and the tracked P2000 option override. Tool RC0, recovered nonempty assembler at mvs-state/dr5-blib-workspace-p2000/blib.asm. Full diagnostic report retained as job-1381.log in that directory. Program size 27346, PROGVEC capacity 40001, free stack/work 12655, tree size 6486, OCODE size 2813, reported 927 unused workspace words of 10655. EXECUTION CYCLES = 9515157, CODE = 0. All observed sizes through tree formation match the failed baseline. This demonstrates the scoped reservation adjustment resolves the observed translation exhaustion. The 927-word figure is compiler-reported workspace slack, not a measured free execution-stack high-water margin. No private assembly or installation was performed and no new clean-room acceptance is claimed.

Source review of ICINT19 MAINEND confirms unconditional RETURN (14,12),RC=0 even when the printed interpreted result is nonzero. Changing that convention globally would affect historical MR10 and compiler/test consumers and is not an implicit correction under DR.5. Recommend owner review of a BLIB-only parameter selection and a separate explicit interpreted-completion acceptance check; distinguish a post-job acceptance check from a true pre-install JCL gate. No production parameter, interpreter, or JCL change made; no further destructive rebuild or device campaign started.

## Approved correction under implementation

Owner approved the BLIB-only P2000 reservation and a dedicated negative reconstruction-integrity regression, without another numbered native BCPL application case. BLIBBLD captures the complete compiler SYSPRINT in temporary FB132 COMPRPT, copies it to JES with IEBGENER, and passes it to BLIBPREP. Before opening RAW, the IFOX-assembled gate requires exactly one completion record with unsigned decimal cycle count, CODE = 0, and blank padding; absent, nonzero, malformed or repeated completion records fail with RC8. The downstream steps use all-prior-step zero conditions; INSTALL cannot run if FIXASM or any preceding step has failed. ICINT19, its default return-code convention, global compiler options, BLIB source and runtime code are unchanged. The guarded reconstruction receipt now requires the added COMPRPT IEBGENER step and exact successful interpreted completion. Native verification must test both private success and deliberate CODE8 rejection with a nonpersistent object destination before another authorized clean-room rebuild. No native success of the gate is claimed by this implementation record.

## Private BLIB build-integrity target verification — PASS

Owner supplied actual WSL console output on 27 November 2026 EST, from the [private verification driver](../../../tools/checks/run-dr5-blib-build-verification.py) at `415b1e75f1adfbc561214f96fbf5bceb9a1dc63e` (Git pull RC0). The tested implementation is unchanged from the [final offline PASS](dr5-offline-verification-and-target-gates-20261127.md) at c5b56cef0e2f9aa830a9b49631868cbc5d380b02; the intervening commit records documentation evidence only.

| Observation | DR5BLPOS, JOB 1382 | DR5BLNEG, JOB 1383 |
| --- | --- | --- |
| Interpreted compiler CODE | 0 | 8 |
| COMP | 0 | 0 |
| COMPRPT | 0 | 0 |
| PREPASM | 0 | 0 |
| PREPLK | 0 | 0 |
| FIXASM | 0 | 8 |
| ASMBLIB | 0 | FLUSH |
| INSTALL | 0 | FLUSH |

Driver status PASS, stage complete, process RC0, tee RC0, receipt-copy RC0. The negative result reports installation_flushed=true. Under the reviewed driver oracle, PASS additionally requires the correct JES identities, no ABEND or JCL error, exactly one expected interpreted completion record per job, two zero IFOX severity records for the positive job and one for the negative job, and explicit ASMBLIB and INSTALL flush evidence in the negative report. These additional checks are established through the reported driver verdict; the underlying private JES reports were not independently reopened by the assistant.

Original receipts: workarea/dr5-blib-build/run-gw9bhlu8. Preserved copy: mvs-state/dr5-blib-build/receipts/run-gw9bhlu8; driver.log in mvs-state/dr5-blib-build/. Keep authenticated decks private. Both jobs use the temporary FB80 destination rather than BOOT_OBJ(BLIB). The positive result verifies the P2000 BLIB-specific build through IFOX and private IEBGENER output; the negative result demonstrates the pre-RAW interpreted-completion guard and downstream suppression despite ICINT19 RC0. No persistent installed object replacement is claimed. The missing, malformed and repeated completion scenarios retain offline/source verification only, not separate native executions. No general execution-stack high-water bound is established.

Private positive/negative acceptance is satisfied at this tested scope. Preserve JOB 1379 and all earlier failed reconstruction and diagnostic evidence. Do not resume at Step 8. Next obtain fresh owner authorization for Gate 1, a complete unattended batch clean-room reconstruction on the dedicated TK5 target; Gate 2 independent installed object inventories and Gate 3 consolidated production regression with explicit device authorization remain separate and unstarted. No DR.5 closure, DR.6 activation, release production or full clean-room PASS is claimed.

## Gate 1 — Second unattended batch clean-room reconstruction — PASS

Owner explicitly authorized a new destructive reconstruction from Step 0 using batch population and supplied the successful final console output on 27 November 2026 EST. Approved revision e922d3daff98181f7e90c8673e15aedca4a9c461. The guarded operator block requires the preserved first-attempt and focused diagnostic receipts, a clean tracked checkout, exact revision (including the driver's internal pull), expected HLQ/write boundary/container and two fresh JES idle observations before invoking `tools/reconstruction/rebuild-from-source --unattended --batch-populate`.

Observed: Guide Step 9 RC0 (42 seconds); final EXT_OBJ listing HERC02.BCPL.EXT.OBJ contains BCPLDEMO, BCPLQSAM and BCPLTIME; listing RC0; REBUILD COMMANDS COMPLETED; total elapsed 8m 05s, rebuild RC0 and log RC0. Protected evidence path: mvs-state/dr5-clean-room-second/rebuild.log. Previous failed attempt and private verification receipts remain separate. Under the reviewed routine driver's stop-on-error stage sequence, this establishes successful execution through all required stages, including corrected BLIBBLD, the built-in BOOT_OBJ inventory check, installed coroutine verification and extension installation jobs. The full retained rebuild log and individual JES reports have not yet been independently reviewed by the assistant; obtain the stage/step and payload evidence excerpts for reconciliation before final march closure. No independent Gate 2 inventory or Gate 3 regression acceptance is inferred from this result.

Gate 1 is accepted at the reported routine-driver completion scope. Next conduct Gate 2 as fresh MVS LISTDS MEMBERS inquiries with the existing strict exact-set inventory oracle for both BOOT_OBJ and EXT_OBJ; retain the listings outside workarea. Gate 3 remains separate and requires explicit device authorization. No guarded-controller acceptance, release production, DR.5 closure or DR.6 activation is claimed.

## Gate 2 — Independent installed object inventories — PASS

Owner supplied actual console output from two fresh MVS LISTDS MEMBERS inquiries at revision 34899a7c4e3460cdbe607b454ae3c35d4fc58a45 (Git pull RC0), following Gate 1 on the same reconstructed target. The intervening revision records only Gate 1 evidence. Both listings were separately checked by the existing strict inventory_members and required_inventory functions in tools/reconstruction/verify.py.

| Library | Actual exact members | Inquiry / log / oracle RC |
| --- | --- | --- |
| HERC02.BCPL.BOOT.OBJ | BCPLAPT, BCPLBYTE, BCPLCO, BCPLIO, BCPLMAIN, BCPLMEM, BCPLREG, BCPLRGS, BLIB, COROUTIN | 0 / 0 / 0 |
| HERC02.BCPL.EXT.OBJ | BCPLDEMO, BCPLQSAM, BCPLTIME | 0 / 0 / 0 |

Observed BOOT_OBJ INVENTORY PASS: 10 exact members; EXT_OBJ INVENTORY PASS: 3 exact members. No missing, unexpected or duplicate members. Listings retained in mvs-state/dr5-clean-room-second/inventory/BOOT_OBJ.txt and EXT_OBJ.txt. This accepts Gate 2 at exact directory membership scope; neither byte identity nor executable behavior is inferred from membership. No installed object modification was performed.

Gate 3, the separate consolidated eight-suite production regression, is the sole remaining target campaign. Obtain explicit printer/punch device authorization before invocation with --allow-device. Expected 219 PASS, one expected SKIP (083), 0 FAIL and 0 BLOCKED. Retain Gate 1 and Gate 2 receipts and reconcile outstanding rebuild payload evidence before formal DR.5 closure. DR.6 remains NOT STARTED.

## Gate 3 — Consolidated eight-suite production regression — PASS

Owner explicitly authorized the complete supported campaign including BCPLQSAM printer and punch cases 175–176. Owner supplied the full case-progress transcript on 27 November 2026 EST. Revision a70a424567d670ca8ff60d29da1663903663d09d (Git pull RC0; intervening commits since Gate 1 record evidence only). Two fresh JES idle observations passed. The coordinator ran the eight supported suites with --profile production --allow-device --progress on the reconstructed target.

| Suite | PASS | FAIL | SKIP | BLOCKED |
| --- | ---: | ---: | ---: | ---: |
| mr10 | 12 | 0 | 0 | 0 |
| mr10-coroutines-supported | 5 | 0 | 0 | 0 |
| bootstrap | 149 | 0 | 1 | 0 |
| runtime-extensions | 17 | 0 | 0 | 0 |
| bcpltime | 4 | 0 | 0 | 0 |
| bcplqsam | 17 | 0 | 0 | 0 |
| coroutines | 13 | 0 | 0 | 0 |
| coroutine-contract | 2 | 0 | 0 | 0 |
| Total | 219 | 0 | 1 | 0 |

MR10 does not implement skip/blocked counters (reported None); zeros in the aggregate denote no such outcomes. The sole expected SKIP is 083 instrumented-storage-reclamation. Cases 175 qsam-fb80-sysout-punch and 176 qsam-fba133-sysout-printer both PASS, as do private rollback cases 198–200. No overlapping historical diagnostics were selected. PROJECT REGRESSION RESULT: PASS; total 13m 40s; regression RC0, log RC0, archive RC0.

Coordinator receipt: workarea/project-regressions/20261128T024630Z-54880-nkvpb0mv/summary.json. Preserved private evidence: mvs-state/dr5-production-regression/regression.log and workarea.tar.gz (complete workarea archive); idle.log also retained. Acceptance is based on the actual owner-supplied progress transcript and the reviewed coordinator's independent suite oracles; raw private JES reports and summary JSON have not been independently reopened. The supported production profile does not imply all optional extension cases use installed rather than source-selected/private objects.

All three distinct target gates now PASS. No additional reconstruction or device campaign is required at this scope. Before formal DR.5 closure, reconcile the retained Gate 1 build payload receipts and remaining documentation qualifications. No DR.6 activation, release production or guarded-controller integration acceptance is implied.
