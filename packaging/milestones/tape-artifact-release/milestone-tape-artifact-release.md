# Milestone — Tape artifact release

**Project:** BCPL for MVS 3.8 Reconstruction  
**Status:** **TA.0 CLOSED (qualified); TA.1 IN PROGRESS — Track A PASS (qualified), saved MVS/Hercules physical-file review completed; Track B write approved; first attempt halted read-only at MVS unit-state gate; Track B BTA102 unload PASS (qualified), JOB 9120 IEBCOPY RC=0000; separate load-library restore/GO pending; milestone IN PROGRESS**
**Authoritative source:** GitHub `main`  
**Target:** Standard-labeled Hercules AWS virtual tape distribution of the **Cambridge BCPL Programming System for MVS 3.8J**

**TA.1 operator-reported write checkpoint (17 November 2026):**
The new uncataloged BTA101 scratch image was initialized and written by
TA1AWRIT JOB 9076; the guarded runner reported both logical standard-label
datasets and SHA-256 d5900cbccaaa2f7eb1bcc59ae30847540e6911c577dafa5e131c0b3a9c8e3fe2.
See [Track A write evidence](../../distribution/create-tape/ta1-track-a-write-evidence-20261117.md).
Readback and both independent IEBCOMPR steps subsequently completed with
MVS JOBS 9084, 9086 and 9089, all RC=0000, and the AWS SHA unchanged.
The [Track A round-trip record](../../distribution/create-tape/ta1-track-a-roundtrip-review-20261117.md)
now records Track A PASS (qualified): read-only review of the actual
saved tape-map reports found seven physical tape files containing
3, 3, 2, 2, 25, 2 and 0 blocks, with both datasets and original image
SHA-256 preserved. Track B remains pending. Owner approved its design on 18 November 2026;
source-controlled JCL and read-only preflight are implemented but no Track B
stateful operation has been authorized. No further stateful operation
is authorized here.

**TA.1 saved physical-file review checkpoint (18 November 2026):**
The owner executed the Git-controlled read-only reviewer at
`4845be9db79ecaa6b8dd4e777ba32bbcf4983886`; it reported
`TA.1 TRACK A: saved MVS evidence PASS (qualified)`, confirmed all
four actual MVS JES jobs 9076/9084/9086/9089 at required RC=0000,
seven physical tape file block counts `3,3,2,2,25,2,0`,
both expected standard-label dataset sequences, the restored seven-member
PDS and unchanged SHA-256. This is an actual owner-reported MVS/Hercules
evidence review, not an offline simulation. Track A is PASS (qualified);
**TA.1 remains open for Track B**. No new MVS operation is authorized.

**TA.1 Track B implementation checkpoint (18 November 2026):**
The owner approved the [separate RECFM=U selected ICINT19 load-library tape design](../../distribution/create-tape/ta1-track-b-design-proposal-20261117.md).
Tracked `TA1BWRIT.jcl` and `TA1BREST.jcl`, pinned canonical MRREGRES/IEHLIST
job generation and strictly read-only MVS/Hercules preflight are staged.
The [implementation record](../../distribution/create-tape/ta1b-implementation-20261118.md)
reports 44/44 synthetic/negative offline tests passing. No BTA102 image,
MVS tape job, remount, new load PDS or restored ICINT19 GO was executed.
Track B remains IN PROGRESS, and separate explicit authorization is required
for all stateful media and MVS operations.

**TA.1 Track B read-only MVS/Hercules evidence checkpoint (18 November 2026):**
The owner executed `ta1b-preflight --live` on GitHub main
`eb0a26e489255e43a1bdc5089589dc53fa8347a0`, reporting PASS.
`MR10_LOAD(ICINT19)` is PO/U/0/6144 on TSO003; BTA102 was absent among
four inspected existing images and the new filename was absent; Hercules
0480 was empty, MVS unit 480 reported, and the uncataloged tape DSN and
new target DASD load library were absent in the MVS catalog.
A new fail-closed one-shot `run-ta1-track-b-write` runner was isolated
and synthetic-tested 27/27 PASS, retaining the required fresh checks,
exclusive media creation, no-retry receipts, live JES/hetmap evidence
and protection of the existing BTA101 image. This is a new implementation
checkpoint, **not** proof that BTA102 was initialized or written.
See [TA.1B live-preflight and write gate](../../distribution/create-tape/ta1b-readonly-preflight-and-write-gate-20261118.md).
**No Track B stateful initialization, mount, write, restore or GO is authorized
by this design/preflight result.** TA.1 remains IN PROGRESS.

**TA.1 Track B stateful-experiment gate correction (18 November 2026):**
The owner approved ONE new `BTA102` initialization/mount and ONE
`TA1BWRIT` unload, but the first invocation at GitHub
`51c56b326fc48a1f47d9e4b19101f0694f333387`
stopped at the FIRST read-only `unit_ready()` inquiry with:
`MVS tape unit 480 is not unambiguously online/ready`.
The failure occurred before any operator confirmation, no-retry marker,
tape image creation, mount, or production job submission. No
MVS `D U,TAPE` raw status row was supplied; `O-NRD` is a grounded
hypothesis from the preflight/writer disagreement, not a measured claim.
The guard has been corrected to accept `O-NRD` for an **empty,
unallocated, online Hercules 0480** ONLY, while retaining strict
`O` status after BTA102 mount. Negative tests exercise offline,
busy, ambiguous and foreign-media refusal. See
[TA.1B first gated run and correction](../../distribution/create-tape/ta1b-first-write-gate-correction-20261118.md).
The approved scope is unchanged: the corrected live runner still
refuses any preexisting attempt receipt or AWS image. **No Track B
write, restoration or GO has been observed.** TA.1 remains IN PROGRESS.

**TA.1 Track B second read-only guard halt (18 November 2026):**
The owner invoked the corrected `run-ta1-track-b-write --run` from GitHub
main `efab256a987512b9e524557293faff99f206fac2`. It reported
`TA.1B WRITE HALTED: MVS tape unit 480 status row missing/ambiguous`;
private evidence was written to
`workarea/ta1b-operations/BTA102-track-b-write-20261118T232154Z-8887/`.
This was the FIRST `unit_ready(mounted=False)` inquiry, before the
operator confirmation, no-retry receipt, AWS file creation, mounting,
or JES submission. The previous read-only preflight searched for
`480 3400` anywhere within an output line and passed, whereas this
writer revision anchored it to the beginning of a line. A console
message prefix is a source-supported explanation, **not** an
assertion that a particular raw MVS status row was observed.
The revised writer counts in-line unit matches, still rejects
duplicates and unexpected statuses, accepts `O-NRD` only on
verified empty Hercules 0480, and requires `O` after mount.
It now includes a bounded observed-line diagnostic on a future
mismatch. Source and safety tests committed; no BTA102 tape
initialization, mount, write, restore or executable GO observed.
See [second guard correction](../../distribution/create-tape/ta1b-second-write-gate-correction-20261118.md).
TA.1 is still IN PROGRESS.

**TA.1 Track B third guarded read-only halt (18 November 2026):**
With GitHub `main` at `5bae753128c3f79f7e7cace74190c554a167a9a9`,
the owner ran `run-ta1-track-b-write --run`; the first
`unit_ready(mounted=False)` check stopped with `matches=2`.
The exact diagnostic contained *two byte-identical* console lines:
`23:36:00 / 480  3400 O-NRD              /REMOV 481  3400 OFFLINE`.
Thus 480 is `O-NRD` and separate unit 481 is `OFFLINE`; the duplication,
not a contradictory state, caused the halt. Owner-local private evidence:
`workarea/ta1b-operations/BTA102-track-b-write-20261118T233538Z-9227/`.
No operator confirmation, attempt marker, image, mount or production
JES submission was reached. The corrected guard requires one **distinct**
unit-480 record, collapsing only byte-identical echoed lines and
rejecting conflicting states, timestamps, different prefixes and
two instances on the same line. It isolates unit-480 allocation flags
from adjacent 481 output and retains the empty-Hercules and
post-mount MVS-`O` safety conditions. **24/24 focused offline tests
PASS**, with the tracked unit-test module expanded to 50 test methods;
the full suite was not separately asserted as executed.
See [third gate evidence](../../distribution/create-tape/ta1b-third-write-gate-correction-20261118.md).
TA.1 IN PROGRESS; no BTA102 write/restore/GO has been verified.

**TA.1 Track B BTA102 write checkpoint (18 November 2026, 23:52 UTC / 18:52 EST):**
The owner invoked the authorized, guarded one-shot writer at GitHub
`702617a30c765df06815bcf9c028930dfa3d91c8`. After fresh
read-only preflight and explicit initialization/JES confirmations,
BTA102 was initialized and mounted at Hercules 0480.
`TA1BWRIT` JOB **9120** completed `UNLOAD IEBCOPY RC=0000`;
the runner verified one complete standard-labeled `BCPL.BT0001`
data set, four Hercules physical-file segments with block counts
**3, 8, 2, 0**, and AWS SHA-256
`c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210`.
Source `MR10_LOAD(ICINT19)` remained read only and the tape DSN was
not cataloged. Original private evidence:
`workarea/ta1b-operations/BTA102-track-b-write-20261118T235204Z-9548/`.
This owner-reported success is the **Track B unload/write PASS
(qualified)**, not a restored executable proof.
A separately authorized restore to
`HERC02.BCPL.TA1B.LOAD` (PO/U/0/6144), followed by IEHLIST
directory comparison and actual restored-STEPLIB ICINT19 execution,
is still required. The new `run-ta1-track-b-restore` script defaults
to **read-only live preflight** and forbids a stateful restore
without its own explicit owner authorization and typed confirmations.
Its 26 synthetic/negative offline tests PASS. See
[Track B write receipt and restore staging](../../distribution/create-tape/ta1b-write-evidence-and-readback-preparation-20261118.md).
TA.1 remains IN PROGRESS; no restore/GO acceptance is claimed.

## 1. Objective and product boundary

Deliver reproducible, independently installable releases. The **complete** configuration contains two usable, independent programming environments:

1. **Native Cambridge Compiler:** A ready-to-run, native System/370 compiler with its own source, supporting assembly, MVS build/link JCL, examples, verification procedures and the required Core Runtime and historical Base Library (`BLIB`).
2. **MR10 Kit Compiler:** A ready-to-run `ICINT19` with assembler source/build JCL; `SYNI`, `TRNI`, `CGI`, `BLIBI`, `ICLIB` INTCODE decks; supporting sources/libraries/JCL; 11 language demonstrations (`MRLANGDM`); 17 BCPL demonstrations (`MRBCDEMO`); and the standard 12-case regression panel (`MRREGRES`), including input data and expected results.

The native environment also includes the **Coroutine Support Library** (`coroutines.bcpl`, `coroutines.h`, `COROUTIN`) and its associated Core Runtime bridge `BCPLCO`; the three accepted optional **System Extensions** `BCPLDEMO`, `BCPLTIME`, and `BCPLQSAM`; and BCEX/BCRG v1 selection/registration instructions and assets. Coroutine Support remains logically distinct from historical `BLIB`. System Extensions are distributed, but remain optional at application link-edit time.

The two environments must be independently selectable, installable and usable; they do not share a binary ABI. Interpreted-versus-native coroutine equivalence is guaranteed only over the previously accepted common behavioral domain. Preserve accepted interfaces and prior milestone closures.

**Excluded/deferred:** `BCPLDEC` (indefinitely deferred); the unimplemented BCPL Standard Library; the interpreter-hosted/demoted Cambridge compiler `CAMBCOMP` unless separately approved; full development/reconstruction history and host-side Python, WSL, `dspal`, or Hercules tooling as *recipient* requirements.

The complete native-running Cambridge Compiler remains **unfinished**. A **release without the native compiler** is also owner-approved: it provides the complete independent MR10 compiler environment and accepted native Runtime/BLIB/Coroutine Support/System Extensions but must not claim a native compiler or its self-compilation. `CAMBCOMP` is not a native compiler substitute. The [subsequent owner decision](../../distribution/release-without-native-compiler-decision-20261116.md) supersedes the unconditional native-compiler publication gate.

## 2. Approved tape and source-of-truth architecture

- Preserve a single authoritative, Git-controlled, **per-release manifest** for selected inputs and member ownership, dataset attributes, source-to-tape-to-recipient mapping, validation, dependencies, declared `native_compiler: absent | included` capability, and ordered 1-based *logical MVS tape dataset* sequence. `config/dspal.yaml` describes development datasets; it is **not** the release-selection authority.
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
| **TA.6** | **Native Cambridge Compiler Distribution and Self-Compilation** | Mandatory for a candidate declaring `native_compiler: included`: the genuine native executable compiles its distributed source, assembles/links through IFOX/IEWL and runs the rebuilt compiler. No `CAMBCOMP` or MR10 substitution. If absent, mark this **candidate gate N/A**, not PASS or formal TA.6 closure. |
| **TA.7** | **Clean-Target Integration and Release Acceptance** | On an isolated clean target, verify MR10-only, native-only and combined installed profiles; human-review all 12 MR10 cases and test 11+17 demos plus native runtime/BLIB/coroutine/extension linkage/execution. Require native compiler self-compilation **only if included**. Retain JES/IFOX/IEWL/GO and tape/installation evidence. |
| **TA.8** | **Release Audit and Controlled Publication** | Audit provenance/redistribution, scope disclosure, version/VOLSER registry, documentation, checksum, manifest and evidence. With separate publication approval, publish exactly tested bytes. A verified release without the native compiler is eligible. |

**Milestone structure and march identifiers TA.0–TA.8 were owner-approved on 16 November 2026.** This approval establishes the work plan, not an accepted implementation, an MVS/tape write permit, or public-release authorization. No march is yet formally closed.

## 4. MR10 reporting and human verification — subsequent owner decision

The owner-approved [MR10 `EXP:` and human-verification decision](../../distribution/mr10-regression-exp-manual-verification-decision-20261116.md) **supersedes the previously proposed requirement for an MVS-resident automatic PASS/FAIL verifier** in the 16 November release payload decision, for the standard 12-case `MRREGRES` panel only.

Use `TEST:` to identify the test, `EXP:` for **fixed literal expected results**, and `RP:` for evaluated actual results. Keep `EXP:` text free of the substring `RP:`; the existing WSL runner collects lines containing `RP:` and compares them with tracked `.expected` golden files, and separately verifies interpreted `CODE=`. No unnecessary WSL runner changes. The `EXP:` display must match the independently retained golden records; do not generate expected values by repeating the computation under test.

On the recipient MVS system, a person must inspect all 12 cases against the adjacent `EXP:` lines, check the `ICINT19` completion `CODE=` (expected zero for the current standard panel), and retain a per-case review and a signed/identified overall verdict. **JES RC=0 is not a semantic PASS.** Human-reviewed divergence is a release failure, even though a separate automatic MVS comparator and nonzero semantic-mismatch step code are no longer required. Do not claim the source programs have already been updated or the manual procedure verified.

The earlier historical MR10 diagnostic/probe suites are not automatically part of the release; do not reclassify their known failures.

## 5. Dependencies, parallel work and critical path

The tape/installer path is **TA.0 → TA.1 → TA.2 → TA.3 → TA.7 → TA.8**. MR10 TA.4 and native library TA.5 can advance after inventory architecture review, in parallel with tape mechanics and producer work; their *installed-recipient* acceptance requires TA.3.

TA.6 depends on completion of the unfinished native-running Cambridge Compiler. **It is an unconditional TA.7/TA.8 gate only for a candidate with `native_compiler: included`.** Candidates declaring `absent` may proceed to clean-target acceptance and controlled publication after all included MR10/native-component/redistribution requirements and separate approval; they must not claim two compilers. The native compiler remains mandatory for any **complete** release.

The first TA.1 diagnostic experiment should use a **fresh, uniquely named scratch image**, two distinct fixtures approximating `BT0001` FB80 and `BT0002` IEBCOPY-PDS, explicit `LABEL=(1,SL)` and `LABEL=(2,SL)`, followed by label inspection and independent restore/comparison. Investigate `VOLUME=RETAIN`, `DISP=PASS`, MVS allocation/demount, step boundaries and positioning before execution; do not assume an append/resume protocol. Test load-library `RECFM=U` transport separately.

## 6. TA.0 open design decisions

**Owner-approved design direction:** curated exact-member inventories, one canonical per-candidate manifest, MR10-only/native-only/combined installation profiles, site-HLQ parameterization, non-reusable VOLSERs and immutable artifacts, and a releasable no-native-compiler configuration. See [TA.0 inventory/architecture](../../distribution/manifest/ta0-release-architecture-and-inventory.md) and [manifest schema](../../distribution/manifest/schema-v1-design.md). **TA.0 verification checkpoint:** [read-only provenance/JCL dependency review](../../distribution/manifest/ta0-provenance-and-dependency-audit.md) confirms 110 Git-backed selected members have existing paths, identifies 2 generated and 15 resident binary members needing source-to-MVS provenance, and finds development `HERC02` references in ten release-selected JCL members. The updated offline validator passes 24 synthetic-fixture tests; these are not MVS readback or redistribution approval. **Still open:** final candidate identity, native source/JCL provenance, executable site-specific HLQ JCL, transport/DCB evidence, multi-dataset retention/positioning, MR10 `EXP:` implementation/human review, redistribution audit. TA.1 is separately gated.

**TA.0 implementation checkpoint, 17 November 2026:** [Read-only provenance/JCL dependency review](../../distribution/manifest/ta0-provenance-and-dependency-audit.md) identifies all ten selected Git JCL jobs and their declared source references. GitHub source inspection found no unselected or cross-profile permanent-dataset dependencies, but all ten remain tied to the development HLQ and lack standalone JOB cards. The [JCL scanner](../../../tools/distribution/audit-jcl-dependencies.py) and offline tests document these dependencies; they do **not** prove recipient MVS operation. The MVS binary/readback and source-generation receipts, site-safe release JCL and redistribution decisions remain outstanding. **TA.0 is not formally closed.**

**Further TA.0 binary provenance checkpoint, 17 November 2026:** the [read-only 15-member build-chain audit](../../distribution/manifest/ta0-provenance-and-dependency-audit.md#6-binary-source-to-build-chain-and-saved-inventory-checks--17-november-2026) reconciles source/build JCL and `tools/reconstruction/verify.py` step contracts. Historical CO.5 acceptance is acknowledged but not reclassified as a verified new candidate image. `BLIBBLD` remains unshipped and source rebuild of historical `BLIB` or Coroutine Support from BCPL requires compiler functionality not supplied by the scoped release. No new resident binary or redistribution evidence was produced; **TA.0 remains IN PROGRESS**.

**Further TA.0 retained-evidence preflight, 17 November 2026:** the [read-only evidence intake contract](../../distribution/manifest/ta0-mvs-build-evidence-intake.md) defines SHA-256-pinned operator-supplied JES reports and exact member listings. The offline suite passes 73/73 synthetic tests; no actual MVS evidence, binary record bytes, DCB correspondence, or redistribution approval was supplied. **TA.0 remains IN PROGRESS.**

The approved single-manifest/bootstrap/naming rules, independent environments, and manual MR10 verification decision are binding. Other architecture details in this section remain **proposals**, not presumed owner approvals.

**TA.0 qualified binary evidence checkpoint, 17 November 2026:** The
[consolidated development-evidence reconciler](../../distribution/manifest/ta0-binary-evidence-reconciliation-20261117.md)
now passes against the saved MVS evidence: **14/14** selected FB80 objects,
**902** FB80 records / **72,160** decoded printer bytes; two original
pre-pagination receipt schemas were accepted without rewriting the private
files. JOB **9060** confirms `MR10_LOAD(ICINT19)` formatted directory metadata,
and JOB **9061** confirms development interpreter executable use on the
bounded eight-step scalar/vector case. **This is qualified development
evidence, not TA.0 closure or binary-source/tape acceptance.** Eight historical
build-job source/provenance receipts, generated `BLIB`/`COROUTIN` lineage,
recipient JCL transformation/target DCB, rights clearance, and owner review of
the proposed post-`BT0002` dataset order remain open. No tape write, new
VOLSER or publication is authorized by this checkpoint.

## TA.0 formal closure and TA.1 transition — 17 November 2026

Owner direction authorizes formal **TA.0 CLOSED (qualified)** at the
[17 November 2026 acceptance/transition record](ta0-formal-acceptance-and-ta1-transition-20261117.md).
The architecture and inventory design baseline and the owner-reported live
14-member FB80 reconciliation plus JOB 9060/9061 evidence are accepted
**only in their specified development scope**. Binary/source provenance,
rights clearance, transport verification, recipient JCL, final artifact
identity and release acceptance remain explicitly unproven and are assigned
to their existing later marches. The TA.0 design record is not a frozen
candidate manifest. TA.0 is not a retroactive claim of test/tape production.

**TA.1 — Multi-Dataset Tape Mechanics is READY FOR DESIGN/PREFLIGHT.**
Its [kickoff and acceptance tracks](ta1-kickoff-20261117.md) require both a
two-logical-dataset standard-label scratch tape roundtrip and a separate
`RECFM=U` load-library unload/restore/executable-use experiment.
**No scratch AWS media initialization, JCL submission that changes MVS state,
tape mount/write, dataset overwrite, VOLSER reservation or publication is
authorized by this closure.** Obtain separate explicit approval for the
specific safe scratch operation.

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
