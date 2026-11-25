# DR.2 — Language manuals: migration and evidence

**Date:** 25 November 2026 EST  
**Baseline:** 28e1831b63886c9cff1110b10bf37ed7e236b660  
**Status:** Initial substantive draft; no contract transferred, no march closure.

The two language manuals follow the twelve and ten approved chapters respectively. Existing paths and accepted contracts remain intact. The reference is a working reference, not normative until explicitly approved. This ledger starts language-family reconciliation; it is not a completed clause-level audit.

## Evidence alignment

Compared recursive Git trees of the handoff revision and RC4 frozen program-source revision e910de51c19c09698be139e33084a90401511cc9. All 98 current blobs under mr10-kit-compiler/language-demo, bcpl-demo, tests/00-regression-panel, library and jcl matched by path and blob SHA. The same comparison against CO.6 tested revision 216b6707c404a91c796ed8f1419a99ef172b184a identifies twelve changed regression BCPL sources; no other current blobs in those directories differ. Do not attribute the changed regression sources directly to the earlier CO.6 run; RC4 acceptance is the relevant release evidence.

The [RC4 companion](../../distribution/publication/RC4-README.md) records 80/80 across MR10 and COMBINED (11 language demos, 17 application demos, 12 regressions each). The [CO.6 closure](../coroutines/co6-formal-acceptance-and-closure-20261116.md) separately records 208 supported passes and one expected skip plus the separately retained original historical coroutine failure. Raw JES receipts were not reopened and no new MVS execution is claimed here. Tutorial modification exercises are predictions, not newly tested programs.

## Migration ledger

| Existing source / provision | Destination | Authority / disposition | Reconciliation and remaining work |
| --- | --- | --- | --- |
| Historical MR10 SYN/TRN: lexical rules, declaration grammar, precedence, command and expression translation | Language reference 1–2, 4–7, 9–10 | Historical primary evidence retained unchanged; not a newly transferred contract | Initial source-observed synopsis; map current compiler source/decks and test lexer, full grammar, constant rules, edge cases, diagnostics |
| Historical Cambridge SYN/TRN: additional lexical and expression constructs, SECTION/NEEDS | Language reference 1, 5, 9–10 | Primary evidence retained; no supported feature promotion | Trace demoted/reconstructed source and native back end; separate recognized syntax from executable semantics |
| MR10 language-demo and bcpl-demo | Tutorial 1–12; reference positive examples | Existing executable examples and suite JCL retained | Unchanged release-source examples linked; derived exercise results require new runs |
| MR10 00-regression-panel source, expected records, manifest | Tutorial 1, 3–6, 8–9, 11; reference 3–9 | Test oracles retain authority; no changes | Golden results cited by case; release companion accepted suites; raw JES records not reopened |
| MR10 library GLOBALS.md and allocator implementation | Tutorial 8–9; reference 8–9 | Existing MR10 map and implementation preserved; Global Number Registry retains allocation authority | Reconcile full allocator contract and failure cases in runtime reference; do not move MR10 slots to native |
| docs/BCPL-memory-management.md and other existing programmer briefings | Tutorial 6, 9; reference 3, 8–9 | Existing explanatory material retained; no disposition | Dependency/semantic audit incomplete; examine complete relevant prose before any retirement |
| CO.6 common coroutine contract and qualified closure | Tutorial 11; reference 10; future runtime reference | Operative accepted contract remains in place; no transfer | Common domain and failure qualification preserved; complete lifecycle provisions belong in runtime reference |
| RC4 companion, manifests and frozen release documents | Both manuals: scope and execution | Release authority retained | Site substitutions and release limitations retained; no release bytes changed |

Additional source reconciliation: MR10 TRN TRANSDYNDEFS uses EVALCONST for VEC bounds and LOAD uses EVALCONST for TABLE entries. The MR10 compiler inventory identifies the executable decks; the current demoted Cambridge build documentation distinguishes generated units from old tracked snapshots. Six native cases (08, 18, 22, 34, 38, 40) were cross-checked against the CO.6 tested revision: all 18 source/README/expected blobs match. The language reference cites these native development examples without promoting them to RC4 guarantees. The original historical source and executable paths remain intact.

## Checks and open qualifications

- Verify both manuals' chapter coverage and relative link targets at the baseline plus the added documents; preserve the existing documentation index while adding navigation for actual manuals.
- Exact source extracts from arithmetic, recursion, coroutine generator and word-count were drawn from the baseline with full-line comments removed. Snippets and predicted modifications have not been compiled anew.
- MR10 historical parser precedence is source-observed. Numeric truth representation, unusual lexical forms, detailed expression evaluation order, STATIC, addressing/lifetime, error semantics, complete GET/section handling, and exhaustive MR10/Cambridge comparison require additional source/target reconciliation.
- No destructive action, source change, global-number reassignment, test-oracle modification, or normative authority transfer. DR.0 dependency-audit qualification remains applicable. Owner approval required for any individual transfer and DR.2 closure.
