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
