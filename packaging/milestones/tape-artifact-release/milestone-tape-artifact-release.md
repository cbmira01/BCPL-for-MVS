# Milestone — Tape artifact release

**Project:** BCPL for MVS 3.8 Reconstruction  
**Status:** **Milestone structure owner-approved, 16 November 2026; TA.0 ready for kickoff, not yet executed**  
**Authoritative source:** GitHub `main`  
**Target:** Standard-labeled Hercules AWS virtual tape distribution of the **Cambridge BCPL Programming System for MVS 3.8J**

## 1. Objective and product boundary

Deliver a complete, reproducible, independently installable release containing two usable, independent programming environments:

1. **Native Cambridge Compiler:** A ready-to-run, native System/370 compiler with its own source, supporting assembly, MVS build/link JCL, examples, verification procedures and the required Core Runtime and historical Base Library (`BLIB`).
2. **MR10 Kit Compiler:** A ready-to-run `ICINT19` with assembler source/build JCL; `SYNI`, `TRNI`, `CGI`, `BLIBI`, `ICLIB` INTCODE decks; supporting sources/libraries/JCL; 11 language demonstrations (`MRLANGDM`); 17 BCPL demonstrations (`MRBCDEMO`); and the standard 12-case regression panel (`MRREGRES`), including input data and expected results.

The native environment also includes the **Coroutine Support Library** (`coroutines.bcpl`, `coroutines.h`, `COROUTIN`) and its associated Core Runtime bridge `BCPLCO`; the three accepted optional **System Extensions** `BCPLDEMO`, `BCPLTIME`, and `BCPLQSAM`; and BCEX/BCRG v1 selection/registration instructions and assets. Coroutine Support remains logically distinct from historical `BLIB`. System Extensions are distributed, but remain optional at application link-edit time.

The two environments must be independently selectable, installable and usable; they do not share a binary ABI. Interpreted-versus-native coroutine equivalence is guaranteed only over the previously accepted common behavioral domain. Preserve accepted interfaces and prior milestone closures.

**Excluded/deferred:** `BCPLDEC` (indefinitely deferred); the unimplemented BCPL Standard Library; the interpreter-hosted/demoted Cambridge compiler `CAMBCOMP` unless separately approved; full development/reconstruction history and host-side Python, WSL, `dspal`, or Hercules tooling as *recipient* requirements.

The complete native-running Cambridge Compiler remains **unfinished**. A compiler that runs as INTCODE under `ICINT19` and merely generates native assembler is *not* a substitute for the release's native compiler/self-compilation gate.

## 2. Approved tape and source-of-truth architecture

- Preserve a single authoritative, Git-controlled, **per-release manifest** for selected inputs and member ownership, dataset attributes, source-to-tape-to-recipient mapping, validation, dependencies, and ordered 1-based *logical MVS tape dataset* sequence. `config/dspal.yaml` describes development datasets; it is **not** the release-selection authority.
- All standard-label tape DSNs follow `BCPL.BTnnnn`, continuously numbered by logical tape dataset sequence. `BCPL.BT0001` is human-readable EBCDIC FB80 installation/bootstrap text; `BCPL.BT0002` is the installation JCL/procedure PDS unload; `BCPL.BT0003` onward is selected by the manifest. The `BT` number is **not** a Hercules physical file number.
- Producer and consumer installation materials must come from the same manifest. A recipient provides an authorized site-specific HLQ and receives MVS-native bootstrap, allocation, restoration, instructions and verification without Git, TSO, Python, WSL or `dspal`. Initial bootstrap is read-only.
- Initial design is a single standard-labeled AWS tape volume. A candidate receives a frozen Git SHA, reviewed release/version identity, newly reserved unique six-character VOLSER, ordered inventory, and SHA-256 checksum; use one cross-release version/VOLSER registry. Publish **only the exact image bytes that passed acceptance**, with separate owner approval.
- Existing accepted PDS/object-library round trips validate only bounded single-dataset behavior; they do **not** establish multi-dataset production, recipient installation or complete release acceptance.

## 3. Formal marches and acceptance gates

| March | Name | Acceptance gate |
| --- | --- | --- |
| **TA.0** | **Release Architecture, Inventory, and Manifest** | Reviewed schema, inventory method and ownership for each required source/member; exact DCB/transport requirements; producer/consumer mapping, dependency and uniqueness checks, reserved bootstrap positions, and native-compiler work-to-be-completed identified. Approve major architectural choices before implementing the producer/installer. |
| **TA.1** | **Multi-Dataset Tape Mechanics** | On explicitly approved new scratch media, write two ordered standard-label logical datasets, preserve the first while writing the second, inspect logical labels/physical filemarks, independently restore/compare both. Separately establish a `RECFM=U` load-library transfer, restore and executable-use path. Record retention, positioning and safe failure behavior using MVS/JES/Hercules evidence. |
| **TA.2** | **Manifest-Driven Tape Producer** | From frozen Git-controlled inputs and validated MVS source artifacts, produce a *new* AWS candidate with generated JCL, contiguous aliases and correct label sequence, independent inventory/readback/structure validation, checksum, provenance, and fail-closed immutable artifact handling. |
| **TA.3** | **MVS Bootstrap and Installation** | `BT0001` can be read on a recipient without BCPL; `BT0002` yields operable MVS-only installation jobs; site HLQ/allocation and overwrite policy validated; independently selectable MR10-only, native-only or combined install paths, all without developer tools. |
| **TA.4** | **MR10 Kit Compiler Distribution and Verification** | Installed `ICINT19` and its rebuild source/JCL operate independently; all 11 + 17 demos and the complete 12-case `MRREGRES` panel compile/run on MVS. Every case emits fixed `EXP:` expected records and distinct `RP:` actual records; a human reviews expected versus actual and `CODE=` for *all 12*, recording per-case PASS/FAIL and explicit sign-off. Preserve unchanged WSL automated `RP:`/`CODE=` checking, proven by its regression run. |
| **TA.5** | **Native Runtime, Libraries, and Extensions Distribution** | Restore/link/execute the Core Runtime, `BLIB`, `BCPLCO`/`COROUTIN` Coroutine Support and `BCPLDEMO`, `BCPLTIME`, `BCPLQSAM` from the distribution; prove correct object/source provenance, BCEX/BCRG selection, optional-link behavior, build procedures and relevant native tests. |
| **TA.6** | **Native Cambridge Compiler Distribution and Self-Compilation** | Deliver and run the separate **native-running** compiler on recipient MVS; use that supplied native executable to compile its distributed source, assemble/link via IFOX/IEWL, then execute and verify the rebuilt native compiler. No `CAMBCOMP` or MR10 substitution. |
| **TA.7** | **Clean-Target Integration and Release Acceptance** | From an isolated clean target, install both environments independently, verify the full 12-case MR10 panel with documented human per-case review, run applicable native regressions/extension and coroutine checks, and pass native compiler self-compilation; retain actual JES/IFOX/IEWL/GO and tape/installation evidence. |
| **TA.8** | **Release Audit and Controlled Publication** | Complete provenance/redistribution review, version/VOLSER registry, documentation, checksum, manifest and test/evidence audit; obtain separate publication approval; tag and publish precisely the accepted bytes. |

**Milestone structure and march identifiers TA.0–TA.8 were owner-approved on 16 November 2026.** This approval establishes the work plan, not an accepted implementation, an MVS/tape write permit, or public-release authorization. No march is yet formally closed.

## 4. MR10 reporting and human verification — subsequent owner decision

The owner-approved [MR10 `EXP:` and human-verification decision](../../distribution/mr10-regression-exp-manual-verification-decision-20261116.md) **supersedes the previously proposed requirement for an MVS-resident automatic PASS/FAIL verifier** in the 16 November release payload decision, for the standard 12-case `MRREGRES` panel only.

Use `TEST:` to identify the test, `EXP:` for **fixed literal expected results**, and `RP:` for evaluated actual results. Keep `EXP:` text free of the substring `RP:`; the existing WSL runner collects lines containing `RP:` and compares them with tracked `.expected` golden files, and separately verifies interpreted `CODE=`. No unnecessary WSL runner changes. The `EXP:` display must match the independently retained golden records; do not generate expected values by repeating the computation under test.

On the recipient MVS system, a person must inspect all 12 cases against the adjacent `EXP:` lines, check the `ICINT19` completion `CODE=` (expected zero for the current standard panel), and retain a per-case review and a signed/identified overall verdict. **JES RC=0 is not a semantic PASS.** Human-reviewed divergence is a release failure, even though a separate automatic MVS comparator and nonzero semantic-mismatch step code are no longer required. Do not claim the source programs have already been updated or the manual procedure verified.

The earlier historical MR10 diagnostic/probe suites are not automatically part of the release; do not reclassify their known failures.

## 5. Dependencies, parallel work and critical path

The tape/installer path is **TA.0 → TA.1 → TA.2 → TA.3 → TA.7 → TA.8**. MR10 TA.4 and native library TA.5 can advance after inventory architecture review, in parallel with tape mechanics and producer work; their *installed-recipient* acceptance requires TA.3.

TA.6 depends on completion of the separate unfinished native-running Cambridge Compiler, outside this distribution milestone's early tape-mechanics work. **TA.6 is an unconditional TA.7/TA.8 gate**. Do not freeze the complete product candidate as accepted without that compiler.

The first TA.1 diagnostic experiment should use a **fresh, uniquely named scratch image**, two distinct fixtures approximating `BT0001` FB80 and `BT0002` IEBCOPY-PDS, explicit `LABEL=(1,SL)` and `LABEL=(2,SL)`, followed by label inspection and independent restore/comparison. Investigate `VOLUME=RETAIN`, `DISP=PASS`, MVS allocation/demount, step boundaries and positioning before execution; do not assume an append/resume protocol. Test load-library `RECFM=U` transport separately.

## 6. TA.0 open design decisions

Require owner review of: exact manifest schema and release inventories; installation profile/selection and destination-HLQ parameterization; PDS/load-library transport and DCB normalization; MVS tape step/job sequencing and error policy; expected-output presentation and manual sign-off format; version/candidate-to-final identity rules, VOLSER registry schema, and immutable artifact retention; component redistribution audit and recipient prerequisites.

The approved single-manifest/bootstrap/naming rules, independent environments, and manual MR10 verification decision are binding. Other architecture details in this section remain **proposals**, not presumed owner approvals.

## 7. Safety, verification and authority

- GitHub `main` owns all source/JCL/specification/decision files; MVS 3.8J, IFOX, IEWL, JES and actual program execution own target-system evidence.
- Demand separate owner authorization for destructive MVS operations, tape initialization/writes, dataset installation, existing production object replacement, and release publication. Do not silently reuse VOLSERs or overwrite tape images.
- Fail closed on incomplete candidates; never automatically reinitialize, append, seek, remount or resume a possibly written tape. Use separate new identities for replacement candidates.
- Test source/JCL and offline checks before commits where possible; never commit/push without explicit approval. This document's recording is documentation-only.
- Preserve earlier accepted milestone closures and qualifications; a scratch round-trip is not release acceptance.

## Governing references

- [Approved expanded payload](../../distribution/release-payload-scope-decision-20261116.md)
- [MR10 reporting decision](../../distribution/mr10-regression-exp-manual-verification-decision-20261116.md)
- [Native Cambridge distribution design](../../distribution/native-cambridge-compiler-distribution-decisions-20261108.md)
- [Version/VOLSER design](../../distribution/release-version-and-volser-registry-decisions-20261108.md)
- [Multi-dataset experiment guidance](../../distribution/multi-dataset-tape-and-append-experiment-20261108.md)
- [Distribution overview](../../distribution/README.md)
- [Runtime/library nomenclature](../../architecture/runtime-and-library-nomenclature.md)
