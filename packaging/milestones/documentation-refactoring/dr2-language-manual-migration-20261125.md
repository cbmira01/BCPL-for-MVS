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

## DR.5 — Language-family reconciliation checkpoint

**Baseline:** `14ad7d57965d927fde05cca8dead5ead4d4e8ce9`. Owner authorized the initial four-manual reconciliation and commits; individual authority transfer is not approved. This is a substantive source review, not exhaustive grammar or target acceptance.

| Provision / source | Destination | Reconciliation and disposition |
| --- | --- | --- |
| Historical MR10 TRN EVALCONST (812–840); Cambridge input TRN EVALCONST (837–894); make-demoted.py demote_trnb_abs | Reference 4, 8; tutorial 2, 6 | Clarified distinct compile-time domains, diagnostics, division guard and ABS implementation rewrite. Historical MR10 deck behavior and extended native constants remain unverified. |
| Both TRN TRANSFOR routines (MR10 614–646; Cambridge 627–661) | Reference 6; tutorial 4 | Clarified one-time bound load, constant BY, inclusive signed-direction comparison, LOOP increment and absent explicit zero-step guard. Increasing positive cases accepted; negative/zero steps and side-effect boundaries unverified. |
| MR10 TRN ASSIGN (after EVALCONST); Cambridge input TRN ASSIGN (after EVALCONST) | Reference 6; tutorial 6 | Clarified recursive component assignment order; no simultaneous assignment or swap guarantee. Case 47 tests independent constants, not overlapping destinations or RHS dependencies. |
| MR10 SYN PERFORMGET and period/EOF branch; Cambridge input SYN PERFORMGET and period/EOF branch | Reference 9; compiler reference 2–3 | Clarified named-stream stack/restore, MR10 N, Cambridge extent check and distinct top-level period behavior. Exact include depth and failure paths unverified; no host search semantics. |
| Native 41, 42, 45, 46, 47 source and expected files | Reference 10 | Reconciled positive scope: all ten blobs match CO.6 tested revision `216b6707c404a91c796ed8f1419a99ef172b184a`; case 47 oracle 422517, other four 42. This supplements the six prior examples; no binary identity or fresh GO claimed. |

**Remaining:** complete grammar/lexical and dialect matrix, exact declaration/scope and procedure semantics, runtime truth/short-circuit and arithmetic edge cases, MR10 preserved deck equivalence, extended Cambridge target lowering, and qualification of any authority transfer. Existing historical sources, old references, accepted common coroutine contract, fixtures and oracles retain their roles. No dependency retirement proposed. Consider focused scratch BCPL probes for overlapping assignments, negative BY/bound evaluation and constant/operator edge cases only if needed for accepted scope; no MVS job authorized or run here.

### DR.5 — Second reconciliation pass

**Baseline:** `dfc4f8496d643d32707c4c6a6862ef42c91c729f`.

| Source / provision | Destination | Disposition and qualification |
| --- | --- | --- |
| MR10 SYN NEXTSYMB, REXP, RDSECT, RDCDEFS, RDBLOCKBODY | Reference 1–2 | Clarified single-quote character/string distinction, tagged closure, newline continuation, declaration delimiters. Source-observed; complete malformed-input recovery and deck behavior remain unverified. |
| MR10 TRN TRANS, DECLNAMES, CHECKDISTINCT, TRANSNAME; Cambridge TRN TRANSNAME | Reference 4, 7 | Clarified name-table scope, declaration groups, outer-local rejection and diagnostics. No general closure or arity guarantee. |
| MR10 and Cambridge TRN LOAD, LOADLIST, JUMPCOND; ICINT19 OP4/OP5, DIVINT, REMINT, SHLINT, SHRINT | Reference 5, 7; tutorial 3 | Clarified word-valued logical operations versus conditional control, operand reordering, emitted argument order and interpreter instruction selection. Signed arithmetic, invalid shift counts, side effects and noncanonical condition behavior remain unverified on target. |
| Cambridge SYN FORMTREE/DECLSYSWORDS/NEXTSYMB/REXP; TRN COMPILEAE/TRANS; generator main | Reference 9–10; compiler explanation 5 | Traced SECTION/NEEDS recognition and OCODE emission, distinguished compiler source adaptation from application grammar, documented additional lexical/assignment forms without certifying native lowering. |
| RC4 and CO.6 source identity | Reference 10 | RC4 frozen source `e910de51c19c09698be139e33084a90401511cc9`: 5 MR10 INTCODE inputs, 11 language sources, 25 semantic source/oracle files all match. CO.6 `216b6707c404a91c796ed8f1419a99ef172b184a`: 12 source/oracle blobs for native 13–15, 24, 35, 43 all match. Exact tracked input identity only; no new execution or binary identity claimed. |

**Remaining:** comprehensive dialect/backend mapping, independently accepted negative diagnostics and side-effect/boundary cases, and source/deck equivalence. The reference now describes more of the actual parser/translator domains, but does not purport to be an exhaustive formal grammar. Existing normative sources and test oracles retain authority; no transfer requested or retirement authorized in this pass.

### DR.5 — Focused language verification preparation

Prepared [shared BCPL candidate, independent hypothesis and execution notes](candidates/language-verification/README.md) and a separate [MVS evidence driver](../../../tools/checks/run-dr5-language-verification.py) at baseline `7e3e977f4feccb528ff259547dce90cee050dca3`. Nine ordered records distinguish overlapping assignment, captured FOR bound, negative constant step, command/value Boolean behavior, signed division/remainder and logical shifts. Both compiler paths use the same source; no regular test numbering or suite changes. Source/oracle format and arithmetic predictions checked offline; actual BCPL compilation, IFOX, IEWL and MVS execution remain pending. Existing reference qualifications remain in effect. Nondefault options, GET and negative diagnostic probes are deferred until the first observations are reviewed.

### DR.5 — First focused MVS observations and native diagnostic

Owner-reported MVS evidence at candidate revision `edabc655d5b4df03b9fe7d686f479c28fe71cc06`, private run `run-4lcfzuag`: MR10 JOB 9489 matched all nine records with all JES steps RC=0 and three ICINT completion codes zero. Cambridge JOB 9490 completed COMP/SVCODE, and native JOB 9491 ASMAP/LKED, at RC=0. Native GO returned 12; ASSIGN, BOUND, STEP, BRANCH, VALUE, OR and SIGNED matched exactly, followed by incomplete `RP: DR5`, without SHIFT/END. Treat these seven complete records as positive observations in that failing job, not a passing native suite. The original paired result remains FAIL. Updated language reference chapters 5, 6 and 10 accordingly. Generated SLL/SRL, argument transfer and the counted SHIFT string are source/assembly-observed as expected; the failure cause remains unestablished. BCPLIO overflow STOP(12) is a candidate, not a finding. A separate native-only diagnostic checks shifts before formatting and independently tests counted string length, WRITES and WRITEF. See the [candidate record](candidates/language-verification/README.md). No production change, original oracle edit, replay or normative transfer; further MVS execution is operator-controlled.

### DR.5 — Repeated native failure and explicit-record candidate

Owner-reported native diagnostic JOB 9493 (revision `e9c9ff16f433f206edb96776bda949b5b3b14d48`) repeats GO RC=12 and the same seven complete records and partial RP: DR5. The 118 visible bytes, seven embedded X'25' newline bytes (as emitted by JOB 9490), and seven partial bytes account for exactly BCPLIO's 132-byte limit. CODE370 explicitly maps host 10 to 37; BCPLIO IOLF is 10 and IOWFULL calls STOP(12). This is a strongly supported newline-representation discrepancy, not proof of a shift-generation defect. The original and diagnostic remain FAIL. A separate explicit WRCH(10) native candidate preserves the language computations, reports both newline literal representations, and awaits MVS execution. See [candidate record](candidates/language-verification/README.md). No production fix or normative transfer is authorized or implied.

### DR.5 — Explicit-record MVS verification result

Owner-reported Cambridge JOB 9494 / native JOB 9495 PASS at `68ce7c76b14affc910f37f0241d4ca326464756b`, run `run-6kwy_ine`: all eight original language computation probes matched MR10 JOB 9489, plus native NEWLINE 37 37 and END. Language reference chapters 5, 6 and 10 now reflect these observations; original native JOBS 9491/9493 retain FAIL and their original fixtures/oracles. The output convention differs between the successful MR10 and native candidates. Verification is limited to these values and paths, not general grammar, compiler options, GET, negative diagnostics, installed-image identity, or raw record boundaries. The newline representation issue remains a separate unresolved compatibility decision; see the [candidate record](candidates/language-verification/README.md).
