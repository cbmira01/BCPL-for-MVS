# MVS 3.8 access methods, BCPL I/O, and dspal — deferred architecture

**Recorded:** 2026-10-08. **Status:** Proposal only; no implementation, PDS changes, or active march authorized. Related: [lineage-based repository refactor](repository-lineage-refactor-proposal.md).

## Three distinct concerns

Do not conflate (1) the compiler's own input/output requirements, (2) MVS file-access services exposed to compiled BCPL applications, and (3) datasets provisioned and managed by host-side `dspal`. An allocated PDS member may be read as a sequential stream without the compiler implementing BPAM directory operations. Similarly, `dspal` defining a VSAM cluster does not demonstrate BCPL VSAM support.

## Dataset/access-method inventory

| Traditional organization | DSORG | Principal access methods |
| --- | --- | --- |
| Physical sequential | PS | QSAM, BSAM |
| Partitioned dataset | PO | BPAM; allocated members may be consumed sequentially |
| Direct access | DA | BDAM |
| Indexed sequential | IS | QISAM, BISAM |

| VSAM organization | Semantics |
| --- | --- |
| ESDS | Entry-sequenced, relative-byte-address access |
| KSDS | Key-sequenced, index/key retrieval and ordered traversal |
| RRDS | Relative-record-number addressing |

PS/ESDS, IS/KSDS, and BDAM/RRDS are only approximate functional analogies, not interchangeable on-disk formats. GDGs concern catalog/retention, not a different primary record organization. Alternate indexes and catalogs are ancillary structures. Do not assume modern PDSE or later VSAM organizations on MVS 3.8. Validate exact utilities, macros, versions and behavior under the actual TK5 environment before implementing anything.

## Per-line capability priorities — proposed, not implemented claims

| Access | MR10KIT | NATIV | CAMBRG |
| --- | --- | --- | --- |
| QSAM sequential | Fundamental historical bootstrap I/O | Essential compiler/regression I/O | Essential |
| BSAM | Optional | Diagnostic | Potential low-level extension |
| BPAM / PDS members | Primarily external build/allocated-member support | Essential **build** infrastructure, not necessarily exposed BPAM API | Essential build infrastructure; optional BCPL API |
| BDAM | Defer | Optional probe | Optional specialized extension |
| ISAM | Defer | Defer | Optional historical compatibility |
| VSAM ESDS | Defer | Optional probe | Desirable native extension |
| VSAM KSDS | Defer | Optional probe | Desirable native extension |
| VSAM RRDS | Defer | Optional probe | Desirable native extension |

Preserve MR10KIT as an independent historical bootstrap, not an artificially feature-matched production compiler. NATIV is the appropriate environment for native MVS interface experiments. CAMBRG should eventually be able to consume proven native libraries without interpreter dependence in normal use. Each line owns its own tests and acceptance evidence.

## BCPL library and runtime interfaces

Keep BCPLMAIN's fundamental stream/linkage interface small. Advanced access methods should be separately assembled and linkable assembler services plus BCPL-facing libraries when warranted, not automatically embedded in BCPLMAIN or historical BLIB. ABI, exported globals, and initialization remain separately gated design questions (Stage B is not thereby completed).

Provisional preference is **two related APIs**:
- **Conventional sequential streams**: open, character/record input/output, EOF, errors, close/reopen; QSAM first, compatible with established historical BCPL semantics.
- **Explicit record-file services**: key or RRN/RBA, buffer and length, keyed/relative reads, update, positioning, explicit operation status/errors. A KSDS should not be disguised as an RDCH/WRCH character stream.

Likely MVS machinery includes DCB/OPEN/CLOSE and QSAM/BSAM/BPAM/BDAM, and ACB/RPL for VSAM. These are prospective implementation tools, not a claim that the project has a working BCPL interface to each.

## dspal's proper responsibility

**dspal provisions, inspects, stages, loads and controls the lifecycle of datasets using MVS-native JCL/utilities. BCPL runtimes handle application-level record access.** Do not grow a parallel host-side VSAM/BDAM record engine inside dspal.

| Organization | Candidate future dspal function |
| --- | --- |
| PS | Allocate and inspect explicit RECFM/LRECL/BLKSIZE; load/extract test records |
| PDS | Existing member mapping, population, inspection; distinguish binary object decks from converted source |
| BDAM | Allocate and initialize for specific demonstrations; avoid inventing generic editing semantics |
| ISAM | Define/build with period-appropriate MVS facilities if genuinely needed |
| VSAM ESDS | Define cluster, load and inspect |
| VSAM KSDS | Define keys (length/offset), load and inspect |
| VSAM RRDS | Define and populate relative-record positions |

No such new support is asserted to exist now. A future manifest must distinguish organization, record format and encoding, binary/text handling, allocation details, fixture source, mutability, and destructive lifecycle safeguards. Inspect JES return codes and MVS diagnostics. Keep system-qualified `dspal` changes and `initbcpl`/`purgebcpl` scope changes coordinated with, but separate from, the deferred repository/PDS namespace refactor.

## SHARED fixture strategy

Implementation-neutral, immutable test data is a strong use case for eventual `HERC02.BCPL.SHARED.*`: FB/80 EBCDIC and padding/boundary inputs, variable-record and binary patterns, keyed fixtures, and relative-record cases. Example *unallocated* names: `HERC02.BCPL.SHARED.SEQ80`, `VARREC`, `KEYTEST`, `RELREC`, `BINARY`. Canonical host fixture content may later live under `shared/fixtures/`.

Shared **input** is not shared mutable scratch space. Regression runs should use read-only reference data (`DISP=SHR`) and private or per-line work datasets/clusters for changes and outputs. MR10KIT, NATIV, CAMBRG retain distinct program sources, expected results where semantics differ, reports, and pass/fail criteria. Shared fixtures do not imply identical runtime behavior.

## Future staged work — not activated

1. Establish dependable sequential I/O/EOF/errors/reopen behavior and existing PDS deployment; optionally add PS fixture provisioning to dspal when needed.
2. Verify VSAM independently: one MVS-native allocate/load/assembler-access proof per ESDS, KSDS, RRDS, with separate evidence for utility support and application API behavior.
3. Implement optional BCPL-callable record services as independently linked native modules only after interface/ABI review; likely start with proven KSDS/ESDS needs.
4. Defer advanced BDAM, ISAM, and BSAM features until requirements justify them.

Avoid mixing this effort with ongoing BCPLMAIN-wip global-vector design, historical compiler modification, the BLIB object-library milestone, or repository moves. Preserve established regressions and explicit three-line ownership throughout.

**Architectural principle:** Provisioning is not programmatic access; shared input is not shared runtime implementation; a native record-file API should not compromise the historical sequential-stream contract. This is documentation of discussion, not permission to change operational systems.
