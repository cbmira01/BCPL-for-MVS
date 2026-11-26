# DR.2 — System Extensions manuals: migration and evidence

**Date:** 25 November 2026 EST  
**Baseline:** 76d169317324435df6e547be692933c93260d455  
**Status:** Four substantive working drafts; no authority transfer or march closure.

## Evidence alignment

Eighteen tracked files (three package assemblers, three headers, three BCX macros and source/expected/selection for 148,149,151) match both CO.6 tested revision 216b6707c404a91c796ed8f1419a99ef172b184a and RC4 frozen revision e910de51c19c09698be139e33084a90401511cc9 by path/blob SHA. Not installed binary identity or native RC4 functional acceptance. Tutorial reproduces three complete accepted clients, selection card and expected records; predicted modification and illustrative JCL untested.

## Migration ledger

| Original authority | Destination | Mapping / remaining work |
| --- | --- | --- |
| R.0 A–H, Decision G, QUERY v1 | Reference 1–2; explanation 2–5 | Binary layouts, limits, 15 IDs, precedence, all-or-nothing query, append-only format, finalizer and ownership. Exhaustive fault precedence pending |
| R.1–R.5 and expanded closure | Explanation 3–5,8; reference 2,6; how-to 3–4,8 | Transactional registration, known-package macro selection, duplicate upgrade, explicit ENTRY, reverse finalization; historical failure and raw MAP/rollback qualifications |
| BCPLDEMO public header/README/source and permanent support | Tutorial; reference 3 | Exact operations, outputs/errors, guard examples and independent selection |
| BCPLTIME header/README/source T.0/T.1 | How-to 6; reference 4; explanation 6 | Raw return words, capacity, register preservation, aligned scratch; date interpretation and DD attribution unverified |
| QSAM public specification sections 1–17,21,24 and header/source | Reference 5; how-to 5,7; explanation 6–7 | All 33 constants, request/result words, dispatch-level exception, formats, geometry, staging, retry, EOF, handles, error/lifecycle exclusions |
| Q.1–Q.5 closure and installation/source-mode records | Reference 5–6; how-to 3,5,7–8 | Preserve 16 slots and 1024 total-byte ceiling, RDW/ASA, device evidence and failure/retry chronology, actual/injected refusal distinction, independent installed receipt gap |
| Registry and current BCXCAT | Reference 2,6–7; explanation 2,5,8 | Current three-package catalog supersedes dated DEMO-only description; registry owns allocation; G!202 reserved, G!299 coroutine, R2TESTB fixture |
| RC4 and CO.6 | All manuals | Release versus development, no new native execution or release |

## Outstanding reconciliation

- QSMDISP rejects unsupported opcodes and nonpositive request/result pointers before clearing result; source-derived qualification to broad result-zero wording. QCVFORM geometry is source-observed, not universal device acceptance.
- Q.5 injection after successful CLOSE does not establish genuine exceptional OS ownership; combined rollback error precedence unresolved, source retains primary error. No software correction.
- Q.5 independent installed selected/unselected proof remains unestablished by that record. Current installation/catalog and later reported clean-room do not independently establish that specific gate; numbered QSAM tests source-selected, Q5QVFY retired.
- Complete register preservation, exhaustive fault matrix, exact extension GET transport and raw receipts require additional review before normative transfer. No new JES, IFOX, IEWL, ICINT19 or GO execution.
- Existing contracts, sources, oracles, allocation, releases and historical evidence unchanged. DR.0 dependency qualification retained; explicit owner approval required for authority transfer and DR.2 closure.

### DR.5 — Native tutorial newline qualification

The [DR.5 language investigation](candidates/language-verification/README.md) confirms native *N=37 while the accepted BCPLIO delimiter is numeric 10. The System Extensions tutorial retains its exact accepted 148/149/151 fixture extracts and adds an explicit warning: short output followed by FINISH does not prove a NEWLINE() physical record boundary. New multi-record examples should use the current WRCH(10) contract pending resolution. Existing regression results and extension APIs are unchanged; no extension suite rerun or physical record verification claimed.

### DR.5 — Verified logical newline correction

Owner-reported MVS PASS at `828cf88dcd080868d7f126267f3650613571951d`: CAMBBLD 9498, BLIBBLD 9500, original compile 9501/native GO 9502, independent newline compile 9503 and native FB132 exact readback 9504. The unchanged original source and oracle now pass MR10 9489 and native 9502. The second candidate confirms logical newline 10, ordinary EBCDIC A=193, input/output boundaries and exact sequential-dataset records. See the [verification record](candidates/language-verification/README.md). Earlier failures and pre-fix 37 observations retained. Affected manuals distinguish rebuilt development environment from older objects. Focused defect verification complete; full post-change regression, clean-room reconstruction and normative transfer not established. No software or oracle change in this update.
