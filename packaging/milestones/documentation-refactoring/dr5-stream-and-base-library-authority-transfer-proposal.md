# DR.5 — BCPLIO and Base Library authority transfer proposal

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.5 — Validation and Reconciliation  
**Date:** 27 November 2026 EST  
**Reviewed source:** `c7d39040f333f027902461f34642441413087b35`  
**Disposition:** PROPOSED — owner approval required; no authority transferred by this record.

Apply the [DR.1 authority safeguards](dr1-reference-authority-owner-decision-20261125.md). The destination is the [Reference for the Cambridge Runtime and Libraries](../../../docs/product/Reference-for-the-Cambridge-Runtime-and-Libraries.md) (the reference). Scope is the supported native application contract in the corrected development environment, not RC4 or MR10. Preserve the [migration ledger](dr2-runtime-library-manual-migration-20261125.md), the historical contracts, source, test oracles and accepted records.

## A — BCPLIO public character streams

Propose chapter 4, together with the relevant STOP/FINISH behavior in chapter 3.2, as the current public character-stream behavioral authority. The two source contracts are the [M5.4 dynamic-stream contract](../bcplio-dynamic-stream/BCPLIO-dynamic-runtime-contract.md) and the [M4.2 JCL/QSAM responsibility contract](../bcplio-dynamic-stream/BCPLIO-JCL-QSAM-stream-contract.md). Preserve both verbatim as dated engineering evidence after explicit transfer. Their DEVOBJ scope and historical procedures do not become current production instructions.

| Original provision | Destination / disposition |
| --- | --- |
| Dynamic §1, responsibility table; JCL/QSAM responsibilities | Chapter 4 introduction, 4.2–4.3: application supplies DD; job author supplies allocation, disposition and compatible data/device attributes, including effective attributes from labels/defaults; BCPLIO owns QSAM control structures and translation; MVS validates, JES2 owns spool and routing. Add explicit responsibility language. |
| Dynamic §2, G11–17, G33, G39, G41–42, G46–47 | Chapter 4 operation table; 4.1 fixed and dynamic lifecycle, 4.2 replay/record details. G30 termination belongs to chapter 3.2; no transfer of other termination/assembler provisions. |
| Dynamic §3 | Chapter 4.1: counted DD strings, normalization, duplicate FIND, opaque handles, dynamic non-reuse and 16 tested dynamic inputs. Explicitly distinguish fixed built-ins, which retain identity on reopen, from retired dynamic identities. FIND never changes selected stream. |
| Dynamic §4; JCL/QSAM supported shape | Chapter 4.2: FB80 input trimming and synthetic newline 10; FB132 output padding, empty records, 132-character maximum, STOP(12), no arbitrary record/data organization promise. QSAM effective DCB attributes remain MVS responsibility. |
| Dynamic §5; JCL/QSAM returned failures | Chapters 4.1 and 4.3: normal ENDREAD/ENDWRITE, normal FINISH/STOP drain, dynamic resource ownership, returned-control failure and retry, no promise for unrecovered abend. Preserve source-only private layout and accounting qualifications; do not extend dynamic zero-return guarantee to absent fixed built-ins. |
| Dynamic §6; JCL/QSAM evidence/limits | Chapters 4.3 and 9: M4.2/M4.3 synthetic failures; JOBs 7874–7876 did not prove real unsuccessful OPEN; 8184 routing, 8185 independent byte comparison, 8186 negative oracle, M5.5 DEVOBJ acceptance. Preserve interrupted duplicate-run caveat in the original acceptance. |
| Dynamic §7 and historical next gates | Retain dated procedures and closure evidence; current reconstruction and regression procedures belong in project manuals and executable tooling, not this transfer. |
| Runtime v1 §5, D7 v2 stream clauses | Historical fixed-DD predecessors only; do not alter candidate-specific evidence or return-code oracles. |

Reconciliation at current main: inspected BCPLIO IONORM, IOFOUT, IOFINDIN, IOSOUT/IOSDYN, IOSELIN, IORDCH/RDPM, IOWRCH, IOWRAP, IOENDW, DQFIND/DIFIND, DQOPEN/DQCLOSE and handle/drain paths. BCPLIO Git blob `aeb0ba35a751bb5b1739788150f2a582520dc7fe` equals the accepted correction revision a0efe9a204e1f3f3968b60cb8c7065e9b423bce7. Case [193](../../../tests/bootstrap/193-bcplio-stream-guards/README.md), JOBs 362/363/366 and the 212-pass production campaign establish the corrected public behavior at the tested scope. The earlier M5.5 145-pass candidate result and exact record/routing evidence remain distinct. The [M5.5 acceptance](../bcplio-dynamic-stream/Milestone-BCPLIO-dynamic-stream-final-acceptance.md) remains a historical milestone record.

Before making chapter 4 normative, explicitly state:
- The job author supplies compatible allocation, disposition, device and attributes; MVS/QSAM determines effective DCB characteristics; JES2 owns spool internals and subsequent routing. BCPLIO is not a general dataset validator or recovery subsystem.
- Ordinary interior input spaces survive trimming. Returned dynamic FIND failure preserves current selection and cursor; the built-in missing-allocation path is not given that recovery guarantee.
- FINISH and STOP(8) drain independent live partial output records at the scope of cases 128/129; do not promise successful cleanup after arbitrary abend. Preserve the fixed built-in lifetime exception and primary ENDWRITE no-op.

No new stream semantics, general storage-safety promise, raw spool-byte proof or BCPLIO private R14 ABI transfer. Defensive wrong-direction guards were source-observed, not fault-injected. Genuine unsuccessful SVC19 remains unverified.

## B — Base Library (BLIB) public supported subset

Propose chapter 5 as current behavioral authority for the 13 ordinary historical native BLIB routines and bounded diagnostic claims already accepted. This consolidates the public BLIB provisions of [runtime v1](../../architecture/runtime-contract-v1.md) §§2, 7–9 and [D7 v2](../../archive/core-runtime/m2-1-runtime-contract-v2.md) only for the current supported native domain. The historical [BLIB source](../../../richards-bcpltape/bcplib/bcpl/blib) and [LIBHDR](../../../richards-bcpltape/sys3/bcpl/libhdr) remain preserved historical and declaration evidence; no renumbering or source replacement.

| Provision | Chapter 5 destination / limitation |
| --- | --- |
| G60 WRITES; G63 NEWLINE; G64 NEWPAGE | Counted output, rebuilt logical newline 10, page-character emission without a universal printer/device guarantee. |
| G66 PACKSTRING; G67 UNPACKSTRING | Counted byte strings, caller storage, last packed word index N/4, tested exact in-place V=S only; no general overlap claim. |
| G62 WRITEN; G68 WRITED; G65 WRITEO; G74 WRITEX; G75 WRITEHEX; G77 WRITEOCT | Ordinary signed decimal/minimum width and specified digit positions; fixed wrappers widths 11 and 8; no full-range or arbitrary-width guarantee. |
| G76 WRITEF | Supported conversion table, one-character width, eleven declared argument words, caller obligations; preserve fallback distinction and case 075's original failure. |
| G70 READN; G71 TERMINATOR data | Optional sign, whitespace, digit prefix, consumed terminator, no-digit zero, no overflow guarantee; no pre-call TERMINATOR initialization claim. |
| Export membership and limited diagnostic behavior | 21 procedure exports, including eight historical diagnostics; G71 data and G79 hook are not exports. Census is not execution evidence. G56/G58/G59 bounded observations only; unsupported logging, LEVEL and PRINTWIDTH-dependent diagnostics remain excluded. |

Reopened historical procedure bodies and declarations, current BCPLMAIN BLIMP path, [READN evidence](candidates/readn-verification/README.md), [resident export census](candidates/blib-trailer-verification/README.md), and the [owner diagnostic decision](dr5-query-authority-and-qsam-precedence-acceptance-20261127.md). BLIB blob `351e2b1ccfb1205c1ef360a2e3e878d980ea04d4` and BCPLMAIN blob `8a4f02de4e6f2c4e02fdbbec16f53b51b53b2fa4` match the accepted resident census checkout bf62ed38816693ca8a000788243e9016dfb54757. JOBs 1301/1302 passed 12 numeric/terminator pairs; JOBs 1303/1304 confirmed the exact 21-slot census and maximum trailer global 100. The migration ledger records focused independent-object cases 069–081 and limited diagnostic cases 120–123. No new testing needed for these accepted fixtures absent evidence of defect.

Before transfer, explicitly say TERMINATOR is meaningful after READN, not an initialized input-state promise. The existing reference's source-observed formatting/packing details and restrictions remain qualified as such. Preserve historical diagnostic limits as already accepted, not a new support obligation or request to reconstruct them.

## Remaining Core Runtime and other authorities

The remaining public startup, native ABI, storage/byte, stack and termination clauses of v1/v2 map to chapters 2–3 and 9. The historical stack checkpoint and BCPLMEM private interface proposal remain separate evidence. Current APTOVEC is independently selected with initialized APLIMIT; D7 RC12 stack overflow is candidate-specific and must not replace current FINIMPL behavior. v1 observability describes private MEMSTAT and provisional DEBUGINT; remaining exact private linkage and exceptional exit audit is separate. Neither A nor B transfers those clauses, coroutine/MR10 library contracts, the Global Number Registry, System Extensions registration/finalization, tools, release-specific records, or private layouts.

## Requested owner decision

Approve A and B together or individually, including the stated bounded clarifications and exclusions. Upon approval record the effective revision, update the reference and migration/milestone indexes, and retain the old paths and historical records. Until then existing authorities remain operative.

No implementation, object, test oracle, numbered regression, release or march status change; no new MVS execution. The separate accepted campaigns are not a consolidated 219-pass run. Workspace Git DNS remains unavailable; the read-only source comparisons used GitHub blob identities and tracked records, not installed binary identity or independently reopened private JES receipts. No private ABI completeness or full historical compatibility claim.
