# DR.2 — Runtime and library manuals: migration and evidence

**Date:** 25 November 2026 EST  
**Baseline:** a8dd18e74db65971616b84cd9957629523f1c9bb  
**Status:** Initial substantive drafts; no authority transfer or DR.2 closure.

The eight explanation and nine reference chapters follow the approved outlines. Existing contract paths, history, source and oracles remain intact. This is an initial semantic mapping, not a complete replacement contract or exhaustive per-routine verification.

## Evidence alignment

Compared 23 selected tracked runtime/library blobs (eight production assembler modules, native coroutine source/header, historical BLIB/LIBHDR, and all MR10 library BCPL sources) with RC4 frozen program-source revision e910de51c19c09698be139e33084a90401511cc9: all match. Against CO.6 tested revision 216b6707c404a91c796ed8f1419a99ef172b184a, fifteen blobs match exactly; eight assembler files differ. For those eight, comparison after excluding full-line assembler comments and blank lines and trimming trailing whitespace found identical remaining lines. This is a source comparison, not assembler output or binary identity proof. It does not establish that every tracked item was distributed or tested independently.

CO.5 and CO.6 accepted development execution and RC4 release acceptance are distinct. No new JES, IFOX, IEWL, ICINT19 or GO run; original operator-local raw receipts were not reopened.

## Migration ledger

| Original provision / authority | Destination | Reconciliation and remaining work |
| --- | --- | --- |
| Nomenclature and runtime interface conventions | Explanation 1–3, 5–8; reference 1–2, 7–8 | Preserve logical/physical distinction, separate Coroutine Support Library and distinct global/behavior/ABI contracts. No authority transfer |
| Runtime v1, sections 1–9 | Reference 1–5, 9 | Historical five-component candidate; map registration, storage, byte/memory, diagnostic/termination behavior. Current independent APTOVEC and dynamic streams supersede old implementation descriptions, not their historical evidence. Complete private ABI and exceptional path audit remains |
| D7 v2 candidate | Reference 2–4, 9 | Candidate-only scope; independent APTOVEC, allocated extent versus safe limit, D7 RC12 differs from current STKOVFL/FINIMPL and D6-compatible oracle RC0. Do not change source or expected files to reconcile text |
| Stack-check checkpoint and CO.1 option matrix | Reference 2–3, 9 | Historical STKCK body missing; current checked +60 and skip-only +20/+80 source; combined compile-only evidence not GO. Retain exact frame and candidate-specific limits |
| BCPLIO dynamic contract and JCL/QSAM responsibility contract | Explanation 4; reference 4 | Map global calls, normalization, stable handles, record shape, resource lifetime, returned failures, synthetic accounting, MVS/JES2 boundary. Dated DEVOBJ scope preserved; current production source observed. Detailed private linkage and all fault paths still need reconciliation |
| LIBHDR and historical BLIB; v1 observability | Explanation 3; reference 2, 5, 9 | Source signatures and formatting table; focused independent-object tests 069–081; preserve 075 original failure/correction; exact READN, all formatting boundaries, trailer exports and diagnostic dependencies pending |
| CO.5 production promotion/closure; CO.6 contract/closure | Explanation 5–6; reference 6–7, 9 | Map known-live root/two-worker, fixed 1024, private context, registration before reclamation, source return codes, paired behavior and historical failure. No arbitrary pointer safety or paired natural-return proof. Preserve full lifecycle/bridge evidence |
| MR10 library README, GLOBALS, coroutine/allocator source and demo | Explanation 6, 8; reference 7 | Retain separate ABI/slots, module selection, summary restrictions. Complete per-function signatures and edge cases still pending |
| Global Number Registry, extension R.0/R.5, T.1, Q.5 records | Explanation 7–8; reference 2, 8–9 | Registry owns allocation; later closure records establish implementation state; do not change registry's dated implementation notes here. G!150 DEBUGINT/FORMTREE unresolved; historical G94 duplicate retained. Detailed extension API in separate reference |
| Native library staging README and BSL design discussion | Explanation 8; reference 8 | Source candidates and inherited slot collision risk; no native library promotion; no proposed API or new user range allocated |
| RC4 guide, CO.5/CO.6 evidence | Both manuals | Preserve release/development boundaries, expected SKIP 083 and genuine MR10/IEWL failure records; no changes to frozen release |

## Explicit discrepancies and verification debt

- v1 internal G40 versus current independent BCPLAPT with APLIMIT initialized; v1/v2 fixed stream names versus current dynamic BCPLIO.
- D7 stack-overflow RC12 versus current source's RC0 normal finalization; finalizer failure can independently change FINISH status. Keep profile-specific oracles.
- Current source allocates a worker lifecycle descriptor via GETVEC(27), while the accepted private 24-word context is described in CO.5; do not turn either into a public size contract.
- Native G!150 diagnostic versus historical FORMTREE; native candidate G101–116 versus historical/compiler ownership; no renumbering authorized. Registry remains authoritative.
- Check exact current BLIB export inventory, each MR10 library signature, private assembler ABI, built-in versus dynamic stream corner cases and exceptional behavior before requesting normative transfer. Source-derived and accepted-test claims remain distinct.

DR.0 dependency-audit qualification remains applicable. No deletion, relocation, software or oracle change, allocation change, new release, authority transfer or march closure.

### DR.5 — Cross-family newline representation discrepancy

From the [language candidate investigation](candidates/language-verification/README.md), native JOBS 9491/9493 fail with GO RC=12 after seven apparent logical lines and a partial seven-character prefix. Their byte counts (118+7+7=132), JOB 9490's X'25' format bytes, CODE370 host-10-to-37 mapping and BCPLIO IOLF=10/IOWFULL STOP(12) give a strong source/evidence explanation. Historical BLIB WRITES/WRITEF/NEWLINE and the accepted numeric-10 stream contract are not yet reconciled. Reference chapters 4–5 output and NEWLINE qualifications updated; explicit WRCH(10) is the existing contract, not a production repair. Preserve both failures, historical source, regression fixtures and oracles. Owner discussion required before choosing a compiler, runtime or library compatibility change. New explicit-record candidate target execution pending.

### DR.5 — Native newline mismatch confirmed

Owner-reported JOBS 9494/9495 passed the explicit-record candidate and observed NEWLINE 37 37 for string byte and character literal, respectively. This confirms the previously traced CODE370/BCPLIO incompatibility at this scope. The same computations passed without embedded output newlines; both earlier native failures remain FAIL. The [candidate record](candidates/language-verification/README.md) preserves the distinct outcomes. Reference chapters 4–5 and explanation chapter 4 qualify native stream boundaries; the operative contract is still numeric 10 for RDCH synthesis and WRCH record emission. No production correction or new authority transfer. Owner design decision required; verify input, output, BLIB and compiled application behavior including exact FB132 readback before any promotion.

### DR.5 — Approved logical newline alignment candidate

Owner approved preserving the numeric-10 BCPLIO stream contract and correcting CODE370 rather than altering the Core Runtime or historical Base Library source. Rebuild BLIB to regenerate historical *N uses, including NEWLINE(). The [focused verification](candidates/language-verification/README.md) will rerun the original failing program and separately verify native literal values, EBCDIC ordinary character translation, input record boundaries, BLIB output and independent full FB132 record/EOF readback. In-place development installation writes are scoped to the approved compiler/Base Library rebuild; no runtime or registry change. Acceptance pending; retain current reference qualifications until target evidence.

### DR.5 — Verified logical newline correction

Owner-reported MVS PASS at `828cf88dcd080868d7f126267f3650613571951d`: CAMBBLD 9498, BLIBBLD 9500, original compile 9501/native GO 9502, independent newline compile 9503 and native FB132 exact readback 9504. The unchanged original source and oracle now pass MR10 9489 and native 9502. The second candidate confirms logical newline 10, ordinary EBCDIC A=193, input/output boundaries and exact sequential-dataset records. See the [verification record](candidates/language-verification/README.md). Earlier failures and pre-fix 37 observations retained. Affected manuals distinguish rebuilt development environment from older objects. Focused defect verification complete; full post-change regression, clean-room reconstruction and normative transfer not established. No software or oracle change in this update.

### DR.5 — Post-correction supported regression PASS

Owner-reported production-profile eight-suite campaign following documentation checkpoint `f8ff445bf034d565a22ecee3af34ad0cd4cd5f77`: 208 PASS, 0 FAIL, 1 expected SKIP (083), 0 BLOCKED; BCPLQSAM 175/176 PASS; elapsed 10m 42s. See [verification record](candidates/language-verification/README.md) for private summary location and suite counts. The logical newline correction has focused and full supported-regression evidence in the existing development installation. No clean-room rebuild, release acceptance, or independent installed-image identity established. No normative transfer or march closure. Other reconciliation qualifications remain.

### DR.5 — Base Library and selected Core Runtime source reconciliation

Source checkpoint `52e4a3b271facd14a94a730d1bf7e472c0e4599b`. Matched historical BLIB top-level LET/AND procedure names to historical LIBHDR: 22 definitions, 21 numbered procedure candidates, PRINTWIDTH unnumbered; TERMINATOR data and USERPOSTMORTEM callback distinguished from procedure definitions. Reviewed make-demoted.py and BLIBBLD source path, BCPLMAIN import and G!76 fallback; installed trailer identity still unverified. Reconciled reference chapters 3, 5, 7 and 9 with BCPLBYTE, BCPLMEM, BCPLAPT, BLIB and MR10 general library/allocator sources. Native READN no-digit zero, consumed TERMINATOR, whitespace/sign handling and lack of overflow check are source observations only. MR10 READLINE and string capacities must fit one length byte; MR10 FREEVEC lacks native live-list pointer validation. Preserve exact V=S PACKSTRING test scope, distinct native/interpretive packing, and separate allocator ownership. No software defect correction is inferred from these caller restrictions.

Existing production campaign at 3f6a417504ab721c080d5af1ffaf54b580ea346b reported 211 PASS and expected SKIP 083; reviewed permanent 071, 072, 075, 091, 092, 093 and MR10 library-scalars/strings/line-io fixtures for their actual scope. No new MVS run or private receipt inspection. Complete native READN boundary testing, actual BLIB export trailer, exceptional diagnostic paths, private register preservation, dynamic stream clause audit and normative transfer remain open. Do not expand to arbitrary malformed pointers or unsupported historical services. No contract supersession, source/oracle/registry change, release change or march closure.

### DR.5 — Dynamic BCPLIO contract reconciliation and open implementation discrepancies

Source checkpoint `48accd2995b7b41486f22f6d1aae07a97ac99243`. Reviewed both operative BCPLIO contracts, fixed-DD predecessor, M5.5 acceptance, canonical bcplio.asm and cases 097–099, 104–105, 108–109, 115, 127, 131–132 and 134. Map contract sections 1–2 and 4 to runtime reference chapter 4; sections 3 and 5 to discovery/lifetime and ownership/error subsections; section 6 to preserved M5.1/M5.2/M5.5 evidence; section 7 to current reconstruction/test manuals (historical DEVOBJ procedure remains dated). No normative transfer requested while discrepancies are open.

| Finding | Source evidence | Verification / disposition |
| --- | --- | --- |
| Dynamic output selection lacks direction and open-state guard | IOSOUT/IOSDYN checks HLOOK nonzero only; IOSELIN checks direction byte and open-state byte; IOWDYN and DQPUT assume output DCB | Source-confirmed contract discrepancy. Case 105 uses correct built-ins; 131 tests retired dynamic output; 134 tests FIND failures, not wrong direction. No wrong-direction write or close attempt authorized. |
| Built-in lookup bypasses normalized identity | IOFOUT/IOFALT and IOFINDIN match exact uppercase before DQFIND/DIFIND call IONORM | Source-confirmed discrepancy. Case 127 verifies DD01/dd01 and REPORT/report, not built-in names. Lowercase built-ins can fall through to duplicate OPEN; do not test that path against the existing installed runtime without a safe design. |
| Fixed input handle can be selected after ENDREAD | IOSELIN accepts INCTRL/IN2CTRL without INOPEN/IN2OPEN check; IORDCH may issue GET; ENDREAD clears selection | Source-confirmed discrepancy. Case 098 re-FINDs before selection; 132 checks retired dynamic identity only. Fixed handles reuse addresses after reopen (115 confirms fixed BCPALT close/reopen behavior, not a new identity). |
| PARM, wrap and close semantics | IOPARMST/RDPM/ENDRPM, IOWRAP, IOENDW, IOFIN | Document source-derived 100-byte clamp, one newline then EOF, fixed PARM reset, BCPALT-only wrap and primary ENDWRITE no-op. Existing 108/109/115 prove selected paths, not every boundary. |
| Returned error and cleanup scope | DQFIND/DIFIND, DDVERIFY, DALLOC, DQOPEN, HNEW, DQCLOSE/DREL, IODRAIN | Preserve M4.2/M4.3 recovery qualifications, M5.1/2 independent sequential-dataset proof and M5.5 accepted candidate results; do not equate printer images with raw spool bytes. |

Proposed owner review: retain legacy fixed built-in handle identity (avoid unnecessary public interface redesign); normalize before built-in dispatch so case-equivalent names take one path; require live open input/output state at selection, especially IOSDYN, and consider defensive direction guards in IOWDYN/DQPUT. Preserve FIND/SELECT separation, primary SYSPRINT ownership and existing MVS recovery boundary. Investigate exact missing built-in allocation policy separately rather than silently expanding the dynamic failure guarantee. For first MVS evidence, an isolated compiled BCPL probe may pass a live dynamic input handle to SELECTOUTPUT, inspect OUTPUT(), and unconditionally restore the saved primary handle before any output/close; report mismatch without invoking wrong-mode QSAM. Similarly check INPUT() after selecting a just-closed built-in handle without issuing GET. Test normalized built-in duplicate lookup only after the code path has been safely corrected or with explicit safe isolation. Permanent case IDs and changes require owner review. No new MVS execution, implementation correction, source/oracle change, or approval to reopen the earlier accepted milestone.

### DR.5 — Owner-approved BCPLIO correction candidate

Owner authorized the proposed correction and commit on 26 November 2026.
Canonical BCPLIO normalizes counted DD names before built-in dispatch,
preserves fixed handle identity, checks built-in input open flags and
dynamic output direction/open state, and defends IOWDYN, DQPUT and dynamic
ENDWRITE against wrong direction. Existing dynamic lookup, allocation and
record semantics remain unchanged; no new public globals, general OPEN
failure contract or fixed-handle identity redesign. Permanent Bootstrap
case 193 checks both wrong-direction selections safely before any I/O,
both closed built-in inputs without GET, and mixed-case identity/cursors for
all four built-in DDs. It verifies the normal REPORT and BCPALT output and
SYSPRINT completion through existing logical record checks.

The dedicated driver first compiles the application and privately assembles
and links the actual canonical BCPLIO source; it requires exact zero-code
compiler and IFOX/IEWL/GO receipts plus the three logical record oracles.
Only the explicit rebuild mode, after candidate success and a fresh JES-idle
observation, stages BOOT_ASM(BCPLIO), checks text readback, and replaces only
BOOT_OBJ(BCPLIO) with an IFOX/IEBGENER/readback/IEBCOMPR job. It then runs
193 using the ordinary production profile. No new persistent JCL member,
other runtime rebuild, compiler/BLIB rebuild or RC4 modification. Retain
private evidence and stop on failure, without automatic retry or rollback.

Bootstrap 150 cases, native inventory 194, expected full supported campaign
212 PASS plus SKIP 083 after target acceptance. The last accepted 211-pass
campaign remains historical evidence; no MVS verification yet for this
candidate. No normative transfer or march closure.

Precommit host checks: exact proposed run-suite and test_stage2b_suite.py
copies matched Git blob IDs; all eight synthetic suite tests passed, with
additional case 193 dispatch in both profiles and missing-marker rejection.
Exact proposed driver copy matched its Git blob and passed Python syntax
compilation; its actual install_cards function passed synthetic scoped-JCL,
ordered-step and invalid-configuration checks with mocked DSPAL helpers.
Verified all 194 manifest IDs and physical ownership, assembler card hygiene,
unique labels and existing fault/accounting anchor counts. Git clone in the
assistant workspace remains unavailable (DNS); no actual IFOX, IEWL, BCPL
compiler or MVS execution by the assistant. Target verification remains the
required next gate.

### DR.5 — BCPLIO target verification and full supported regression PASS

Owner-reported 26 November 2026 results, correction source checkpoint
`a0efe9a204e1f3f3968b60cb8c7065e9b423bce7`. Canonical BCPLIO SHA-256
`76a5b9ed79cd88aa2ad1f17f2dbd7eede6298930eb9f0f4ca6a64f911f162b9a`.
Private driver evidence: `workarea/dr5-bcplio-fix/run-2pivdj58`;
status PASS, stage complete. Compiler JOB 362, private IFOX/IEWL/GO JOB 363,
and BLDIOFIX JOB 366 (IFOX, install, independent readback, IEBCOMPR) passed
the tracked driver gates. Ordinary installed case 193 PASS in
`workarea/test-suites/20261126T133242Z-95570-bootstrap-production-tuns_vgp`.
This verifies the approved public stream-selection and normalized lookup
corrections at the fixture scope. Defensive IOWDYN/DQPUT/ENDWRITE checks
remain source-observed; no deliberate wrong-mode QSAM call or private-state
fault injection was performed.

The subsequent owner-reported eight-suite production campaign completed
in 12m 22s, with PROJECT REGRESSION RESULT: PASS. Private summary:
`workarea/project-regressions/20261126T135428Z-95734-3o_8l8rf/summary.json`.
No intervening checkout change reported.

| Suite | PASS | FAIL | SKIP | BLOCKED |
| --- | ---: | ---: | ---: | ---: |
| mr10 | 12 | 0 | not reported | not reported |
| mr10-coroutines-supported | 5 | 0 | 0 | 0 |
| bootstrap | 149 | 0 | 1 (083) | 0 |
| runtime-extensions | 13 | 0 | 0 | 0 |
| bcpltime | 4 | 0 | 0 | 0 |
| bcplqsam | 14 | 0 | 0 | 0 |
| coroutines | 13 | 0 | 0 | 0 |
| coroutine-contract | 2 | 0 | 0 | 0 |
| **Supported total** | **212** | **0** | **1** | **0** |

All 213 selected cases accounted for, including device cases 175/176.
Case 193 passed a second time. The 211-pass pre-correction campaign and
earlier historical observations remain preserved. Current supported
development baseline is 212 PASS with the same expected SKIP. The three
public stream-selection/lookup discrepancies are resolved at the tested
scope; no repeat rebuild or regression required absent new evidence.
Fixed built-in handle reuse, missing built-in allocation policy, MVS abend
boundary, and physical JES DD attribution limitations remain unchanged.

Evidence consists of owner-supplied console transcripts and driver result,
not independently inspected private receipts. No clean-room reconstruction,
release installation, RC4 modification, normative authority transfer or
DR.5 closure is claimed. Resume reconciliation of System Extensions.

### DR.5 — Focused native READN verification candidate

Source checkpoint `bcfa2c51cb4beaa024c2ded53762969f6a67b588`. The historical BLIB READN routine and LIBHDR,
BLIBBLD and BCPLMAIN's BLIMP trailer-import path were reviewed again.
The earlier compiler-host numeric-option evidence does not establish native
G!70/G!71 behavior. The [focused candidate](candidates/readn-verification/README.md)
uses installed BOOT_OBJ and four BCPIN records, with 12 independent numeric
and consumed-terminator expectations (signs, whitespace/newline, nondigit,
zero, sign without digits and repeated EOF). No existing case or oracle is
changed. No numeric overflow/tab-input proof, complete installed BLIB
export-trailer inventory, or new target acceptance yet. Private native
compile/IFOX/IEWL/GO verification is the next gate. No normative transfer.

### DR.5 — Focused native READN verification accepted

Owner-reported checkout `7bc3196009c8036f4466c325afa06e8aace4c259` and private evidence
`workarea/dr5-readn-verification/run-vk9rmndr`: compiler JOB 1301 and native
JOB 1302 PASS, twelve exact observed records matched the tracked oracle.
See [candidate evidence](candidates/readn-verification/README.md) for the
reported input SHA-256 values, scope and limits. Reference chapter 5 now
records native G!70/G!71 acceptance at the exercised scope. No production
change or repeat submission required. Tab input, overflow, complete BLIB
export-trailer census and other outstanding ABI/diagnostic qualifications
remain. No numbered regression allocation or change to supported suite
counts; no normative transfer, release change or march closure.

### DR.5 — Resident BLIB export-trailer reconciliation

Source checkpoint `6763eb9f69f7812d84d9d320c6704154f4ebf6ee`. Reopened the historical CGGLOBAL emitter,
canonical BCPLMAIN BLIMP import path, BLIB/LIBHDR, and actual [R.0 JOB 2197
export census](../../archive/runtime-extensions/runtime-extensions-r0-trailer-job-2197-evidence-20261021.md).
The older installed BLIB exported exactly 21 procedures, not G!71 data or
G!79 callback. This agrees with the DR.5 source inventory and is now
acknowledged in the runtime reference. The earlier binary is not the
subsequently rebuilt resident BLIB; a fresh census is warranted.

The [DR.5 candidate](candidates/blib-trailer-verification/README.md) reuses
the unchanged R.0 IFOX observer and parser, adding the current resident
BCPLRGS/BCPLREG linkage to a disposable deck and requiring the exact
historical 21-slot set. No startup, procedure calls, PDS updates, device
operations, production changes, new numbered cases or normative transfer.
Local Python syntax and isolated exact-inventory/linkage tests passed;
GitHub DNS prevents full local checkout. Target results pending.

### DR.5 — Resident BLIB export census accepted

Owner-reported checkout `bf62ed38816693ca8a000788243e9016dfb54757`, private run
`workarea/dr5-blib-trailer/run-xyrd4qt6`: compiler JOB 1303 and observer
JOB 1304 PASS. Actual resident BLIB exports match all 21 historical slots,
application exports G!1, no overlap, BLIB maximum global 100. Generated
application assembler SHA-256 matches historical JOB 2196 exactly; this
is not general compiler or installed-object binary equivalence.
See [candidate evidence](candidates/blib-trailer-verification/README.md).
Reference chapter 5 now records the current census. No new numbered
regression, production correction or repeat submission required. Full
procedure execution, private ABI preservation, diagnostic dependencies,
and object build provenance remain qualified. No normative transfer,
release change or march closure.

### DR.5 — Historical BLIB diagnostic dependency reconciliation

Source checkpoint `1ea630fc8ed1a188d8a7533824006731b41f5d43`. Reviewed the eight exported historical
diagnostic bodies, PRINTWIDTH, current BCPLMAIN initialization/global stores,
BCPLIO IOFOUT and fixed IOCTL1 handle, BCPLMEM MEMBIND/list publication,
and exact native case 120–123 sources. G!31 LEVEL and G!36/G!37 logging
are not populated by the ordinary Core Runtime; historical ABORT's optional
G!79 callback is not a BLIB export. PRINTWIDTH's assumed byte-address DCB
is incompatible with the opaque word-address stream handle. Documented
this concrete source limitation in reference chapter 5; no unsafe direct
invocation of unestablished diagnostics or public handle representation
change proposed. Existing bounded STACKHWM/INPROGRAM/VALIDPOINTER evidence
is retained; 122's manual list publication is distinguished from 123's
automatic publication. The 21-slot census is not a complete diagnostic
execution contract. Recommend retaining historical diagnostic recovery,
exact high-water/sentinel boundaries and arbitrary-pointer safety as
explicit qualifications, rather than expanding this documentation march
into historical runtime reconstruction. No new native execution or
production change; owner acceptance of the remaining qualifications
is still required.

### DR.5 — Owner acceptance of historical BLIB diagnostic limitations

On 27 November 2026 the owner accepted the documented limitations, including
PRINTWIDTH's incompatible DCB assumption and unestablished historical
logging, frame traversal and postmortem dependencies. See [owner decision](dr5-query-authority-and-qsam-precedence-acceptance-20261127.md).
No reconstruction of unsupported diagnostics is required for DR.5 at this
accepted scope. This is not a transfer of the remaining runtime/library
contract or acceptance of arbitrary-pointer safety. Preserve the native
READN, export census and bounded cases 120–123 evidence.

### DR.5 — Owner-approved BCPLIO and Base Library authority transfers

On 27 November 2026 the owner approved both transfers and bounded clarifications in the [proposal](dr5-stream-and-base-library-authority-transfer-proposal.md). See the [acceptance record](dr5-stream-and-base-library-authority-transfer-acceptance-20261127.md). Reference chapter 4 and the relevant stream behavior in chapter 3.2 now govern supported native BCPLIO; chapter 5 governs the supported native BLIB subset and bounded diagnostic behavior. Original contracts and candidate acceptance history are retained unchanged. Remaining Core Runtime startup, ABI, allocation, byte, stack and termination provisions, private assembler interfaces, and coroutine/MR10 contracts remain outside this transfer. No new target execution, implementation or oracle change, or march closure.

### DR.5 — Remaining public Core Runtime authority transfer (C) and DEBUGINT authorization (D)

Owner directed “Proceed C and D” on 27 November 2026. See the [reviewed proposal](dr5-core-runtime-authority-transfer-proposal.md) and [acceptance record](dr5-core-runtime-authority-transfer-acceptance-20261127.md). Chapters 2–3 and relevant scope/limitations in chapters 1 and 9 now govern the supported native public Core Runtime contract, excluding detailed DEBUGINT behavior, private assembler interfaces, coroutine and MR10 contracts. Four reviewed assembler modules match CO.5 post-clean-room non-comment lines after trailing whitespace normalization; not object identity. Preserve D7 candidate RC12 overflow versus production D6-compatible RC0, exceptional path limitations, private R10 clobber and bounded resource evidence. D authorizes focused native reproduction and a minimal operand-preservation correction with separate private and installed verification; no G!150 allocation change, new numbered case or broader diagnostic support. No new MVS result or software change in this authority decision.

### DR.5 — DEBUGINT correction candidate prepared

Owner-approved D: canonical BCPLMAIN preserves R7 across the negative-sign DBGAPND call using two LR instructions and scratch R8. See the [isolated verification candidate](candidates/debugint-verification/README.md). The driver compiles one BCPL fixture and requires the installed negative operand defect to reproduce, then requires six exact records from private canonical BCPLMAIN before any persistent write. Explicit rebuild mode stages/readbacks only BCPLMAIN source and replaces/readbacks/compares only its object, then repeats the identical application against installed production objects. The baseline semantic FAIL is retained. No numbered case, allocation, existing oracle, broader diagnostic behavior, or release change. Host syntax and isolated gate tests passed; local Git DNS prevents full checkout and no MVS verification has yet occurred. C remains effective; D target acceptance pending.

### DR.5 — Coroutine Support Library authority transfer

On 27 November 2026 the owner approved the [reconciled proposal](dr5-coroutine-library-authority-transfer-proposal.md) and authorized commits. See the [acceptance record](dr5-coroutine-library-authority-transfer-acceptance-20261127.md). Chapter 6 and coroutine-specific provisions of chapters 7 and 9 now govern the qualified public native/common coroutine contract. The earlier migration table's source-only natural-return qualification is superseded by accepted CO.6 paired re-entry evidence, not a new execution. Native one-time zero state, explicit application export binding and separate COROUTIN/BCPLCO linkage are now explicit. Preserve the original historical MR10 fixed-stack FAIL and distinct supported variant, private descriptor/bridge limits, registry authority and original CO.5/CO.6 documents. 26 exact blob matches plus non-comment BCPLCO equivalence at the CO.6 baseline are source evidence only. D remains pending; remaining MR10 contracts are next. No new MVS execution or code change.
