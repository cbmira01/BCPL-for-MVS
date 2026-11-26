# DR.2 — Compiler manuals: migration and evidence

**Date:** 25 November 2026 EST  
**Baseline:** 901f6117df958d58c5c9b135da0a330e94477ca0  
**Status:** Initial substantive manuals; no authority transfer or march closure.

The compiler explanation and reference follow the approved eight and seven chapters. The existing documents remain operative at their original paths. This is a preliminary provision-level migration, not a completed authority-transfer request.

## Evidence alignment

Recursive Git tree comparison of the baseline, RC4 frozen program-source revision e910de51c19c09698be139e33084a90401511cc9 and CO.6 tested revision 216b6707c404a91c796ed8f1419a99ef172b184a: ten MR10 files (five compiler/runtime INTCODE decks, ICINT19 assembler, build and three suite JCL files) match by path and blob SHA at all three revisions. Eight demoted compiler input files (source/syn, source/trn, make-demoted.py, bootstrap-host.bcpl, cambridge-options.txt, options-large-tree.txt, make-mr10-trn-large-names.py and cambbld.jcl) also match at all three revisions. Source equality does not prove generated object identity, and does not mean the demoted compiler was distributed in RC4.

The [RC4 companion](../../distribution/publication/RC4-README.md) accepts 80/80 functional cases in the two MR10-capable installed profiles; the [CO.6 closure](../coroutines/co6-formal-acceptance-and-closure-20261116.md) separately records 208 supported development passes and one expected skip. Original raw JES logs were not reopened. No new execution is claimed.

## Migration ledger

| Existing provision / source | Destination | Reconciliation and disposition |
| --- | --- | --- |
| Historical tape INDEX; BCPL history briefing; CG370 architecture notes: lineage, AE/OCODE, CGI, CG370, section layout, fixups and external linkage | Explanation 1–3, 5–7; reference 5–6 | Historical primary sources retained; distinguish OCODE branch paths; no retirement |
| MR10 options inventory: OPTIONS input/defaults, P/T/C/M/N/A/S/E/L/3, mutable scanner flag, fallback and driver binding | Reference 2, 7 | Mapped all ten spellings and defaults; checked historical SYN START, TRN save-space references and CG START; no comprehensive executable-image equivalence or individual switch test |
| Cambridge option transport note: two phases, active/disabled switches, defaults, historical runtime PARM, BCPLCLG/MAKEOBJ, CODE/SYSGO and CAMBPARM | Reference 3–5, 7; explanation 5–6 | All active and inactive cases mapped against historical master; clarify early A/N/ example versus current /N/; digits also fall into OPTWARN; unknown phase-2 options STOP(8); retain source note and original authority |
| Bootstrap source README, generator and host shim, CAMBBLD and compile-mvs | Explanation 5; reference 3, 5–6 | Distinguish tracked old snapshot and generated units, host/target packing, exact current parameter file, DUMMY SYSGO and textual output recovery; existing build dependencies untouched |
| Historical BCPLCLG, MAKEOBJ, MAKELIB and BCPLMAC; copied native JCL | Explanation 6; reference 4 | Historical parameter construction and library composition recovered; no native-running compiler acceptance; preserve destructive historical examples as evidence, not run instructions |
| ICINT19 source, MR10 phase inventory and suite jobs | Explanation 4; reference 2, 6 | Source-derived capacities, packed-byte geometry and stages; compare tracked files with RC4/CO.6 revisions; leave job bodies and executable dependencies intact |
| CO.1 checked-entry matrix, CK-B, CK-C, CK-D; BCPLMAIN source | Reference 6 | /CN reported checked-only baseline; /CKN and /CPN compiler-only evidence; current STKCIMP remains four-byte skip-only, not a working combined handler. No runtime changes |
| RC4 guide and CO.6 closure | Both manuals, release and verification boundaries | Preserve qualification, genuine historical failure and test oracle authority; no release changes |
| Existing language reference chapter 3 | Small clarification of physical word versus logical packed bytes and TRUE/FALSE source evidence | ICINT19 ICGETBY/ICPUTBY divide byte index by 2 then scale word address by 4; historical MR10 CG GENCODE loads -1 and 0. No new MVS result or authority transfer |

## Remaining work

- Complete exact clause mapping, verify historical parser/executable behavior where material, especially nondefault options, switch combinations, GET/parameter edge cases, timing and naming.
- Reconcile historical and reconstructed runtime contracts in the runtime/library reference. Do not treat /CKN or /CPN emission as successful execution. No implementation change is authorized by the discrepancy.
- Validate generated output and target operation only where outstanding questions warrant it; reuse accepted receipts where available. No fresh JES submission, assembly, link-edit or run was made.
- Existing contracts, source and fixture dependencies, release and allocation registries retain authority. DR.0 dependency-audit qualification remains. Individual authority transfer and march closure require explicit owner approval.

## DR.5 — Compiler-family reconciliation checkpoint

**Baseline:** `14ad7d57965d927fde05cca8dead5ead4d4e8ce9`. Owner authorized initial reconciliation and commits, not normative transfer.

| Provision / source | Destination | Reconciliation and disposition |
| --- | --- | --- |
| MR10 option inventory; historical SYN/TRN/CG | Reference 2 | Existing ten spellings, defaults, indexed scanner and option transport retained as source-observed. Independent nondefault-option behavior and source/deck equivalence remain unverified. |
| Historical Cambridge master (139–217, 265–385); option transport note | Reference 3–5, 7 | Confirmed active/disabled cases, numeric terminator reprocessing, G's verbatim remainder, phase-sensitive N and distinct OCODE/CODE/SYSGO selection. Earlier A/N/ wording is historical, not current default. No broadened bootstrap support. |
| ICINT19 FINDIN, MAKENAME, DYNFIND; MR10 compile-and-run-core.py --dd | Reference 2.4; explanation 4 | Clarified name normalization, fixed table before dynamic DD allocation discovery, named inputs to compile/run, reserved/duplicate name rejection. Missing-DD, nested include and repeated-open target behavior not asserted. |
| compile-mvs build_deck and main (60–94, 203–223); bootstrap-host.bcpl FINDPARM | Reference 3.1; explanation 5 | Clarified four header bindings, absence of general --dd, CAMBPARM substitution and preview's existing output deletion. The latter is a source-observed operational hazard, not a software correction. |
| make-demoted.py demote_lex_readfloat, demote_trnb_abs and packing transformations | Explanation 5; language reference 4 | Distinguished compiler implementation adaptations from target-language recognition and unsupported literal parsing. |

**Proposed future authority-transfer scope:** MR10 option inventory and Cambridge option/parameter transport note to compiler reference chapters 2–5 and 7, explicitly retaining source-observed and historical qualifications. Not ready for approval until remaining input/output, current generated-unit and nondefault-option behavior is reconciled; existing paths remain operative. Historical runtime parameter service, compiler/runtime contracts, Global Number Registry and frozen release facts retain separate authority. No old paths retired. No fresh BCPL, IFOX, IEWL or MVS execution; no private raw evidence reopened. Remaining work includes complete option/diagnostic and GET behavior, precise transport limitations, checked/counting execution restrictions and any target verification warranted by the eventual accepted scope.

### DR.5 — Second reconciliation pass

**Baseline:** `dfc4f8496d643d32707c4c6a6862ef42c91c729f`.

- Compared all five tracked MR10 INTCODE inputs with the RC4 frozen program-source tree at `e910de51c19c09698be139e33084a90401511cc9`: 5/5 identical blob SHAs. This does not prove regeneration from the preserved historical BCPL source or every nondefault option's behavior.
- Compared the maintained Cambridge SYN/TRN containers, demotion generator, bootstrap host and default parameter file with CO.6 tested tree `216b6707c404a91c796ed8f1419a99ef172b184a`: 5/5 identical. Source review of generator main confirms the distinct source containers, historical master/CG inputs, derived section units, occurrence checks and diagnostic generation. Other generator dependencies and installed images were not compared in this check.
- Updated compiler reference chapters 2 and 6 and explanation chapter 5. SECTION/NEEDS parsing and emitted metadata do not establish native link resolution. No generated-unit build, source-to-deck reproduction, nondefault-option execution or fresh MVS verification was performed. No authority transfer or path retirement is approved; remaining qualifications from the preceding checkpoint persist.

### DR.5 — Newline character representation observation

The [language verification evidence](candidates/language-verification/README.md) at `68ce7c76b14affc910f37f0241d4ca326464756b` records native JOB 9495 PASS with explicit WRCH(10), and GETBYTE("*N",1) / '*N' both 37. This confirms CODE370's deliberate host-10-to-X'25' adaptation and its incompatibility with the current BCPLIO numeric-10 stream delimiter. Compiler reference chapter 3 now qualifies the adaptation; no compiler-source, compiler image or BLIB modification, option change or normative transfer authorized. Owner decision pending on the coherent character-stream convention.

### DR.5 — Owner-approved compiler newline correction candidate

Owner approved changing private CODE370 host newline mapping from #45 to 10, preserving ordinary inverse CODEA and the historical source. The generator change is implemented; CAMBCOMP and BLIB must be rebuilt and MVS-verified. See the [focused candidate record](candidates/language-verification/README.md). No external encoding conversion is added and no published release changes. The original native failures and numeric-10 explicit-record PASS remain preserved. Do not represent the correction as accepted before the live result.

### DR.5 — Verified logical newline correction

Owner-reported MVS PASS at `828cf88dcd080868d7f126267f3650613571951d`: CAMBBLD 9498, BLIBBLD 9500, original compile 9501/native GO 9502, independent newline compile 9503 and native FB132 exact readback 9504. The unchanged original source and oracle now pass MR10 9489 and native 9502. The second candidate confirms logical newline 10, ordinary EBCDIC A=193, input/output boundaries and exact sequential-dataset records. See the [verification record](candidates/language-verification/README.md). Earlier failures and pre-fix 37 observations retained. Affected manuals distinguish rebuilt development environment from older objects. Focused defect verification complete; full post-change regression, clean-room reconstruction and normative transfer not established. No software or oracle change in this update.

### DR.5 — Post-correction supported regression PASS

Owner-reported production-profile eight-suite campaign following documentation checkpoint `f8ff445bf034d565a22ecee3af34ad0cd4cd5f77`: 208 PASS, 0 FAIL, 1 expected SKIP (083), 0 BLOCKED; BCPLQSAM 175/176 PASS; elapsed 10m 42s. See [verification record](candidates/language-verification/README.md) for private summary location and suite counts. The logical newline correction has focused and full supported-regression evidence in the existing development installation. No clean-room rebuild, release acceptance, or independent installed-image identity established. No normative transfer or march closure. Other reconciliation qualifications remain.

### DR.5 — GET, diagnostics and option reconciliation

Baseline `0de748ebef72965497dd1ac40330a99a33f56cae`. Reopened MR10 SYN 115–203, 367–379, 549–565, 609–660, 670–696; Cambridge SYN 65–100, 148–180, 884–905, 1037–1052; historical Cambridge master 139–217, 259–374 and final ERRORS check. MR10 missing input 96 uses ordinary CAEREPORT recovery, immediate abort when REPORTCOUNT>REPORTMAX; Cambridge -87/-88 are fatal and use >= with negative codes setting REPORTMAX=0. Both GET frame stores consume three words; Cambridge checks VEC 10 extent, MR10 does not. Cambridge labels included-file diagnostics using 10001-based line numbering. No general malformed-source recovery or JES return-code equivalence established. Updated compiler reference chapters 2, 3 and 6. Recompared five CO.6 blobs: 4 identical, generator differs by approved and verified newline correction; updated stale identity statement. Prepared [focused compiler input/option candidate](candidates/compiler-verification/README.md) for nested MR10 GET, L6000N suppression and Cambridge J12Q/N/ with installed LIBHDR. Source and oracle checks only; target pending. No production change, authority transfer or path retirement.

### DR.5 — First compiler input verification results

Owner-reported run at `e743ee65e4fbfc41e086aa512c706bafa4138422`: MR10 JOB 9920 nested GET PASS (17 5 20 42), JOB 9921 L6000N suppressed GET PASS (42 and option echo). Exact outputs, required JES steps and zero ICINT codes passed. Cambridge host compile driver RC=2, cause not yet established; no native GO. See [candidate evidence](candidates/compiler-verification/README.md). These results qualify the tested MR10 inclusion and option behavior, not general nesting or malformed-input recovery. No production change or authority transfer; further Cambridge investigation requires the existing diagnostic receipt.

### DR.5 — Cambridge JOB 9922 diagnosis

Owner-supplied full receipt establishes COMP and SVCODE RC=0 but ICINT CODE=-1. Trace and global map identify G!15=0 after READN returns 12 and TERMINATOR=81. Historical master calls UNRDCH; current MR10 ICLIB and BOOTHOST do not provide it. All five historical call sites, including independent source lookahead, must be considered. Compiler reference chapter 3 now records the bootstrap restriction. See [candidate record](candidates/compiler-verification/README.md). Native BCPLIO remains unaffected; no GET result, production change, normative transfer or closure. Owner design approval pending.

### DR.5 — Owner-approved bootstrap compatibility correction candidate

BOOTHOST scoped RDCH replay (G!15), stream-selection/close state and historical source period SKIPREC (G!26); permanent Bootstrap cases 190–192, including the accepted newline/FB132 oracle, numeric option paths and multi-source lookahead. No historical/native runtime or MR10 interpreter modification. MVS rebuild and first regular-suite acceptance pending. See [candidate record](candidates/compiler-verification/README.md). No authority transfer.
