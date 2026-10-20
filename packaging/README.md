# MVS deployment and reconstruction

The canonical MVS dataset manifest is [`config/dspal.yaml`](../config/dspal.yaml) and its operator interface is `tools/datasets/dspal`. All tracked source files and build JCL reside in Git; MVS libraries hold deployed sources and rebuildable outputs.

## Documentation ownership and navigation

The [educational briefings](../docs/README.md) in `docs/` are for
human readers. Durable engineering records live here:

- [Current repository map](repository-map.md) — the maintained replacement
  for the retired, pre-M3 `docs/project-map.md`.
- [BCPLIO dynamic-stream milestone index](bcplio-dynamic-stream/README.md)
  — accepted DEVOBJ runtime contract, M0 design decisions, QSAM/JCL
  responsibilities, selected detailed verification and closure evidence.
- [BCPLIO accepted evidence metadata](bcplio-dynamic-stream-evidence/)
  — historical JSON/TSV receipts and checksums, not raw printer captures.
- [BCPL historical source audit](audits/BCPL-corpus-audit.md) — coverage
  against preserved compiler/application programs.
- [Stack-check contract](stack-check-contract.md) — reconstructed
  System/370 stack semantics from historical evidence.
- [Regression-runner maintenance handoff](maintenance/Handoff-repository-cleanup-regression-runner.md)
  — post-acceptance investigation, not a new active milestone.

The accepted dynamic candidate links DEVOBJ(BCPLM6+BCPLIO+BCPLBYTE+
BCPLAPT) with BOOT_OBJ(BCPLMEM+BLIB). Its 00..145 panel passed 145,
failed zero and skipped expected case 083. **No DEVOBJ-to-OBJ promotion**
was authorized. Earlier milestone progress journals are available through
Git history but were removed from the working tree.

## Complete reconstruction

**[Clean-room MR10-to-native MVS reconstruction runbook](clean-room-mvs-reconstruction.md)** is the single chronological procedure for emptying `workarea/`, inspecting and purging the manifest-defined PDS set, reinitialization, text population, ICINT19 rebuilding, MR10 demos/tests, demoted Cambridge bootstrap, runtime object rebuilding, and the complete native regression panel.

[Accepted M3 evidence](m3-native-reconstruction-acceptance-20261015.md) records the demonstrated component builds and **123 PASS / 0 FAIL / 1 expected SKIP** for the full native regression panel. The single combined destructive procedure still requires one-run verification.

## Runtime and library terminology

[Global Number Registry](global-number-registry.md) inventories historical and compiler-specific globals, MR10-local numbering, documented collisions, and the approved System Extension assignments **G!200 BCPLQSAM**, **G!201 BCPLTIME**, and **G!202 BCPLDEC**. Allocations do not imply implementations or successful registration.

[Cambridge runtime and library nomenclature](runtime-and-library-nomenclature.md) distinguishes the Compiler, Core Runtime, historical Base Library (BLIB/LIBHDR), System Extensions, Standard Libraries, and User/Site Libraries. It also defines module, package, header, object/load library, and the separate global-number allocation versus startup-registration responsibilities. This is a proposed packaging/ABI vocabulary, not a claim that new libraries are implemented.

## Proposed optional runtime registration architecture

[Milestone Runtime Extensions](milestone-runtime-extensions.md) (R.0–R.3)
proposes explicit IEWL selection and general startup registration.
**R.0 — Evidence and contract is in progress**; R.1 has not started.
The [R.0 source and ABI audit](runtime-extensions-r0-evidence-and-contract-20261020.md)
documents current `BCPLMAIN` export and FINISH/STOP paths and the
owner-approved shared `BCPLREG`/finalizer *model*. The
[candidate exact R.0 binary layout and finalizer ABI](runtime-extensions-r0-candidate-binary-abi-20261020.md)
is **a proposal for owner review**, not approved or implemented.
The [R.0 three-question review](runtime-extensions-r0-three-design-questions-review-20261020.md)
and [source-derived native owner ledger](runtime-extensions-r0-native-global-owner-inventory-20261020.md)
examine bounded descriptors, dependencies and historical global
ownership. Exact byte offsets and finalizer ABI remain **unapproved**.
R is not a prerequisite for M4.

The preferred R.0 candidate is **one public global-vector entry per optional package**, dispatching on stable package-local operation numbers. **Opcode 0** would provide a side-effect-free, versioned numeric capability query into caller-owned BCPL words, with API version, supported-operation bitmap, and feature flags. The global slots G!200–G!202 are assigned in the registry; the shared registration ABI and package-local opcodes still require R.0/Q.0 verification.

## Proposed optional native I/O milestone

[Milestone QSAM](milestone-qsam.md) defines a separately gated Q.0–Q.5 roadmap for a native BCPL QSAM record-I/O extension. The [BCPLQSAM Public Interface Specification](bcplqsam-public-interface.md) records the reviewed Q.0 design baseline, including numeric constants and fixed-size vector contracts; MVS 3.8 and optional-registration verification remain. The [Q.0 ABI evidence](qsam-q0-dispatcher-abi-evidence-20261019.md)
records observed JOB 2156/2157 **PASS** with permanent test sources.
The standalone [FB80 QSAM probe](../bootstrap-toolchain/probes/q0-qsam-fb80-probe/README.md)
passed in **JOB 2159**: [execution evidence](qsam-q0-fb80-evidence-20261020.md).
The [DASD FB/V/VB probes](../bootstrap-toolchain/probes/q0-qsam-dasd-probes/README.md)
also passed: **JOB 2160** (FB80), **JOB 2161** (V) and **JOB 2162**
(VB). See [MVS execution evidence](qsam-q0-dasd-evidence-20261020.md)
and [remaining Q.0 design questions](qsam-q0-design-review-20261020.md).
The [Q.0 record-size/failure/finalization review](qsam-q0-record-limits-failures-finalization-review.md)
separates historical MVS limits from a tested implementation ceiling.
The [approved Q.0 staging and resource decision](qsam-q0-staging-resource-design-decision.md)
and [JOBs 2180–2182 evidence](qsam-q0-1024-byte-stage-evidence-20261020.md)
establish **1024 total private stage bytes per handle** as the
version-1 BCPLQSAM design limit. The
[approved error/R.0 finalizer decisions](qsam-q0-error-and-r0-design-decisions-20261020.md)
specify conservative CLOSE ownership and FINISH/STOP diagnostics.
The [test-only 1/3/8/16-DCB generator](../bootstrap-toolchain/probes/q0-qsam-16-dcb-probes/README.md)
**PASSED on MVS in JOBs 2183–2186**; see
[concurrent-DCB evidence](qsam-q0-concurrent-dcb-evidence-20261020.md).
The 16-DCB standalone job used **GO REGION=256K**, held sixteen
private 1024-byte stages and checked interleaved F1024 records.
The 512K fallback was not run. Full BCPLQSAM runtime/application
storage accounting remains open.
**Q.0 — Reconnaissance & contract remains open**; Q.1 code implementation has not started. It is not a dependency of M4. Candidate object builds must remain separate from accepted runtime objects.

## Proposed optional numeric and clock milestones

- [Milestone Decimal Arithmetic](milestone-decimal-arithmetic.md): packed-decimal fixed-point arithmetic and business-record interoperability, proposed D.0–D.4.
- [Milestone Date and Time Services](milestone-date-and-time-services.md): Gregorian calendar helpers and MVS clock adapter, proposed T.0–T.4.

Both are optional, proposed, and independent of M4 and Milestone QSAM.

## Dataset ownership

| Namespace | Current status | Authority |
| --- | --- | --- |
| `MR10_*` (9 datasets) | Reconstructed historical kit interpreter, tests, demos | `mr10-kit-compiler/` and manifest |
| `NATIVE_*` (6 datasets) | Reconstructed resident compiler INTCODE, native runtime ASM/JCL, objects | `bootstrap-toolchain/` and manifest |
| `CAMB_*` (9 datasets) | Reserved for M4; **not used for M3 compiler reconstruction** | Manifest allocation only |

`BOOT_OBJ` contains the accepted BCPLMAIN, BCPLMEM, and BLIB objects. `BOOT_DEVOBJ` contains independently assembled BCPLM6, BCPLAPT, BCPLBYTE, and BCPLIO candidate objects for the accepted dynamic-stream profile. No binary migration or implicit object promotion is permitted.

A successful `dspal populate` updates explicitly mapped text members without pruning unlisted members. `dspal purgebcpl` is destructive to **all 24 manifest-managed datasets**; it does not delete datasets outside the manifest and prompts for explicit confirmation. Generated sources and binary outputs must be rebuilt after a purge. Keep local credentials in the ignored `config/dspal.local.yaml`.

## Historical design and evidence

The older proposal and milestone records elsewhere under `packaging/` preserve decisions and rationale as of their stated dates. In particular, previous `HERC02.BCPL.OBJ` proposals and old `SOURCE/JCL/DEVOBJ` commands are historical, **not current installation guidance**.

Useful further references: [Git/MVS source authority](git-mvs-authority.md), [M3 namespace migration log](m3-dspal-namespace-migration.md), and [M2.1 runtime acceptance](m2-1-gate-f-final-runtime-acceptance.md).
