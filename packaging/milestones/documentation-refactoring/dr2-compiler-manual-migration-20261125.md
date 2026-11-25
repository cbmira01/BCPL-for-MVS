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
