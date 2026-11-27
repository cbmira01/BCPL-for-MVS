# DR.5 — BCPL language authority transfer proposal

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.5 — Validation and Reconciliation  
**Date:** 27 November 2026 EST  
**Source reviewed:** `a25fe905ffecc102750e1763d282f4e1e76b7dad`  
**Disposition:** PROPOSED — explicit owner approval required; no language authority transfer by this record.

The [remaining MR10 runtime/library transfer](dr5-mr10-runtime-library-authority-transfer-acceptance-20261127.md) is effective. Apply the [DR.1 authority safeguards](dr1-reference-authority-owner-decision-20261125.md). The proposed normative authority is the [Reference for the BCPL Language](../../../docs/product/Reference-for-the-BCPL-Language.md), chapters 1–10, for supported source syntax and semantics only within the documented dialect and verification boundaries. It is not a formal definition of all historical or modern BCPL, a promise of all source-recognized features, or a transfer of compiler options, runtime calls, linkage, allocation, release or test-oracle authority. The [tutorial](../../../docs/product/Tutorial-on-BCPL-Programming.md) remains instructional, not a competing normative authority.

## Reconciliation mapping

The [language migration ledger](dr2-language-manual-migration-20261125.md) records the detailed earlier source inspection, focused MVS verification and preservation requirements. Reviewed the current language reference, its ledger, historical MR10 and current Cambridge input SYN/TRN, the paired fixture and exact oracle, permanent cases 190–192, compiler correction evidence, RC4 companion, tutorial and the memory briefing.

| Chapter | Existing primary evidence and disposition |
| --- | --- |
| 1 Lexical structure | Historical [MR10 SYN](../../../richards-bcpltape/mr10/bcplkit/syn), NEXTSYMB, RDTAG, DECLSYSWORDS and [Cambridge SYN input](../../../bootstrap-toolchain/bootstrap-cambridge/source/syn); preserve source-derived forms, conventional uppercase examples, host mapping and verified newline correction. |
| 2 Syntax and grammar | MR10 RDBLOCKBODY, RDEF, RDSECT, RDCDEFS, RBEXP/REXP and RCOM; descriptive grammar, declarations before commands, matched tags and newline-sensitive continuation; no complete malformed-source grammar or recovery claim. |
| 3 Data representation | Historical [MR10 TRN](../../../richards-bcpltape/mr10/bcplkit/trn)/[CG](../../../richards-bcpltape/mr10/bcplkit/cg), [ICINT19](../../../mr10-kit-compiler/asm/icintv19.asm), native byte/word contracts and ordinary examples. Distinguish 32-bit storage from MR10 two logical packed bytes and native four; keep pointer identity and character mappings separate. |
| 4 Declarations and scope | MR10 and [Cambridge TRN input](../../../bootstrap-toolchain/bootstrap-cambridge/source/trn) EVALCONST, TRANS, DECLNAMES, TRANSNAME; preserve restricted constant domains, block scoping, nonclosure and source-observed diagnostics. |
| 5 Expressions and precedence | MR10 SYN binding powers and both TRN LOAD/JUMPCOND, ICINT19 instruction mechanisms and paired observations; distinguish word logical operations from branching, signed examples from arithmetic boundary promises. |
| 6 Commands and control | Both TRN TRANSFOR, ASSIGN, TRANSSWITCH and positive fixtures; preserve ordered simple-name stores, bound capture, inclusive signed-step cases and fallthrough/ENDCASE distinctions. |
| 7 Functions/routines | RDEF, LOADLIST, generated OCODE and accepted call/recursion/function-value examples; no arbitrary arity, calling side-effect order or unlimited stack guarantee. |
| 8 Storage/addressing | TRANSDYNDEFS, LOADLV/TABLE and accepted vector/byte/allocator examples; historical [memory briefing](../../../docs/BCPL-memory-management.md) is explanatory evidence, not an allocation ABI. |
| 9 Program structure/separate compilation | SYN PERFORMGET, FORMTREE, MR10 module example, corrected Cambridge host and independently compiled units; distinguish source GET, compiler workflow and runtime global binding. |
| 10 Dialect and evidence boundaries | Historical [Cambridge SYN](../../../richards-bcpltape/bcplib/bcpl/syn)/[TRN](../../../richards-bcpltape/bcplib/bcpl/trn), current input containers, generation tool, RC4 release and development acceptance. Recognized syntax is not demonstrated executable support. |

## Proposed reference clarifications

### Lexical, grammar and representation boundaries

The existing MR10 lexical and precedence tables agree with the inspected NEXTSYMB, RBEXP and REXP cases. The numeric scanner recognizes # plus octal digit, #B, #O, #X (uppercase radix spellings); not every invalid digit/error path is independently tested. Single-quoted one-character numeric literals undergo CHARCODE; other quoted strings use the packed representation, with source length bound. Asterisk escapes include T/S/N/B/P, literal asterisk and historical continued-string syntax (newline after asterisk, skip spaces/tabs and require asterisk). Keep these additional forms explicitly source-observed, not a new lexer acceptance guarantee. Do not silently convert historical comments or backslash operators into modern dialect syntax. The descriptive grammar is not exhaustive; continue using conventional spellings, matching tagged brackets and declarations before executable commands.

The conventional canonical Boolean values TRUE=-1 and FALSE=0 are source-derived language representation, not evidence that all nonzero words are interchangeable or that every Boolean operation/condition path is target-proven. The released [Boolean demonstration](../../../mr10-kit-compiler/language-demo/boolean-operators/boolean-operators.bcpl) prints numeric relational/logical results; its source and the accepted release suite provide positive-domain evidence but not a newly inspected exact per-value receipt. The paired DR.5 oracle establishes false word result zero and the observed conditional bypasses, not all truth patterns. In chapter 3 replace the earlier blanket requirement for explicit bit-pattern oracle before any transfer with a qualified statement distinguishing source-observed canonical representation from target-verified common cases; explicitly exclude noncanonical truth and unverified numeric boundary behavior from verified guarantees.

Logical newline 10 and ordinary native EBCDIC A=193 are established by JOB 9504 and case 190. MR10 remains logical ASCII via ICINT19 translation. Do not infer external encoding identity or assume the native application is executing with ICINT19's packed-byte layout. The [normative runtime reference](../../../docs/product/Reference-for-the-Cambridge-Runtime-and-Libraries.md) owns actual byte/stream procedures and ABI, including MR10 PUTBYTE byte-domain preconditions and opaque stream handles.

### Expression, command and declaration semantics

Retain the existing MR10-specific precedence table; do not extrapolate it to all Cambridge-only operators. Keep source-specific EVALCONST domains and diagnostics (MR10 subset, Cambridge extended forms), lexical recognition versus execution, constant VEC/TABLE bounds, block-local scope, outer-procedure local rejection and distinct definition/assignment initialization semantics. Require nonnegative representable VEC bounds and sufficient live workspace. There is no general zero-initialization, closure, bounds checking, arbitrary lvalue or aliasing safety. Keep historical diagnostic numbers as implementation observations.

The [shared language source](candidates/language-verification/source.bcpl) and [nine-record oracle](candidates/language-verification/expected.txt) independently establish in MR10 JOB 9489 and corrected native JOB 9502:

| Topic | Exact observed result |
| --- | --- |
| Sequential simple-name assignment | ASSIGN 20 20 (not simultaneous swap) |
| Captured nonliteral upper bound | BOUND 6 0 |
| Negative constant BY | STEP 9 |
| Conditional AND | BRANCH 0 (right-side call bypassed) |
| Value AND | VALUE 0 1 (right-side call executed) |
| Conditional OR | OR 1 1 (right-side call bypassed) |
| Signed division/remainder | SIGNED -3 -2 |
| Logical shifts | SHIFT 48 1 |
| Completion | END |

These observations agree with the earlier inspection of both translators' recursive ASSIGN, TRANSFOR, JUMPCOND and value-context LOAD. Document the demonstrated signed arithmetic and inclusive constant-step behavior as supported at the observed domain; preserve arithmetic overflow, zero divisor, invalid shift/step, general operand evaluation order, arbitrary aliasing and noncanonical truth qualifications. Middle operands in chained comparisons may be reevaluated because the source forms conjunctions of adjacent comparisons. Do not rely on value-context short circuit or on one common evaluation order for all operations. Keep function call argument emission distinct from general execution order/arity guarantees.

The [focused execution record](candidates/language-verification/README.md) retains failed native JOBs 9491 and 9493, seven matching complete records, GO RC12, and the explicit WRCH(10) workaround JOB 9495 (pre-fix newline 37). Corrected CAMBBLD 9498, BLIBBLD 9500, compile 9501/native 9502 pass the original unchanged oracle; independent JOB 9504 validates six exact FB132 records and EOF. The later 208-pass supported campaign is historical verification, not an all-language certification. No new focused test required for these already observed behaviors.

### Program structure: correct stale Cambridge GET status

Chapter 9 currently says Cambridge application GET verification remains unresolved. That is stale at the supported simple-header scope. The [compiler correction record](candidates/compiler-verification/README.md) records CAMBBLD JOB 9925 and permanent [case 191](../../../tests/bootstrap/191-cambridge-option-replay/source.bcpl) using GET "LIBHDR", including the [independent oracle](../../../tests/bootstrap/191-cambridge-option-replay/expected.txt) RP: RG191 HDR 4 32 -1 under J12Q/N/ and J12P3000R30Q/N/ with native GO. Q/H600N/ is compilation only. [Case 192](../../../tests/bootstrap/192-cambridge-source-lookahead/source.bcpl) tests top-level period, discarding rest of record and two complete independent source units; the [oracle](../../../tests/bootstrap/192-cambridge-source-lookahead/expected.txt) is FIRST 17 then SECOND 25. Both pass in the dedicated run and subsequent 211/212 supported campaigns; [case 190](../../../tests/bootstrap/190-native-logical-newline/source.bcpl) carries the newline check into regular production tests.

Distinguish historical source-observed PERFORMGET mechanics (one saved stream, line and lookahead triplet per inclusion; Cambridge checked depth, MR10 unchecked frame extent) from tested behaviors: MR10 JOB 9920 two nested GETs restoring at EOF and period, exact 17 5 20 42; JOB 9921 L6000N suppresses opening a deliberately unallocated DD, result 42. Cambridge single GET LIBHDR and top-level period multi-unit source are now verified; Cambridge arbitrary/nested GET and missing/overflow error recovery are not certified. The original JOB 9922 CODE=-1 from missing bootstrap G!15 remains FAIL. BOOTHOST replay and SKIPREC are host accommodations, not native or MR10 library semantics. Compiler options, source transport, DD bindings, artifact packaging and native linkage remain in the compiler/tool references. Do not infer general SECTION/NEEDS selection or linkage from case 192.

### Dialect and authority boundaries

Retain the existing Cambridge-only source-recognition matrix (BYTEAP, floating operators, ABS/FLOAT/FIX, SLCT/selector application, compound assignment, SECTION/NEEDS and additional aliases/identifier spelling). The [generation tool](../../../bootstrap-toolchain/bootstrap-cambridge/make-demoted.py) adapts the compiler implementation for INTCODE hosting; it is not a change to all application-language parser branches. No feature is promoted based only on a lexer/translator branch. Exact lowering and independent execution of additional Cambridge-only forms remain unverified; no comprehensive modern BCPL compatibility or native-running compiler is asserted.

Chapter 8 and tutorial should direct allocation behavior to the already normative runtime/library reference. The historical memory note's alternate heap architectures and moving-compaction research are not the current supported contract. Chapter 10 should refer to the [accepted coroutine transfer](dr5-coroutine-library-authority-transfer-acceptance-20261127.md) and normative runtime chapter 6, rather than suggest the common contract still awaits transfer. Preserve CO.6 evidence and historical manual-frame MR10 FAIL. These are library/runtime facilities, not new language syntax. Keep source and oracle ownership independent.

## Source and evidence reconciliation

Untruncated recursive Git trees establish:
- **103/103 exact blobs** at current main and RC4 frozen program-source revision `e910de51c19c09698be139e33084a90401511cc9`: current MR10 language-demo, application demos, regular semantic panel, libraries, JCL and five preserved compiler/runtime INTCODE inputs. The [RC4 companion](../../distribution/publication/RC4-README.md) records 11 language demos, 17 application demos and 12 semantic regressions per MR10/COMBINED installation (80/80 total). This is unchanged release input identity, not proof of source-to-deck regeneration, new release testing, or native certification.
- **57/57 exact blobs** at the accepted DR.5 212-pass campaign checkpoint `a0efe9a204e1f3f3968b60cb8c7065e9b423bce7`: historical MR10 and Cambridge SYN/TRN/CG, current Cambridge input SYN/TRN, generation tool, BOOTHOST/default options, selected native language fixtures (08,13–15,18,22,24,34–35,38,40–43,45–47,190–192), matching available source/oracle/profile/option files. This supplements earlier CO.6 positive examples; not binary identity or a current consolidated run.
- **5/5 exact blobs** for the focused language source, oracle and three diagnostic/newline variants against the correction-tested revision `828cf88dcd080868d7f126267f3650613571951d`.

The [DR.5 runtime migration ledger](dr2-runtime-library-manual-migration-20261125.md) records the later 212 PASS/one expected SKIP 083 campaign; 219 PASS/one expected SKIP is the later separate-suite cumulative baseline, not a consolidated run at current HEAD. Do not overwrite earlier observations or count historical negative diagnostics as supported passes. No fresh MVS execution or independent raw JES receipt inspection in this review.

## Requested decision

Approve the bounded language authority transfer and reference clarifications above. Apply the current reference status and chapter corrections, preserve the tutorial's instructional role, cross-link existing normative runtime provisions, record effective revision and append the migration ledger/milestone entry. Retain all historical source/old references, executable source, fixture identities and independent oracles. No additional focused language execution required to establish this qualified scope; the existing outstanding consolidated operational gate remains. Broader negative/dialect/backend coverage requires separately approved work, not an implicit promise here.

D (DEBUGINT) still requires native evidence; no clean-room reconstruction, release promotion, march closure or DR.6 activation. Local Git DNS remains unavailable; this comparison used GitHub directly. Original private JES receipts and installed binary identities have not been independently verified.
