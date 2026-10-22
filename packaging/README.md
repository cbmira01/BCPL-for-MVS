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

[Global Number Registry](global-number-registry.md) inventories historical and compiler-specific globals, MR10-local numbering, documented collisions, and the approved System Extension assignments **G!200 BCPLQSAM**, **G!201 BCPLTIME**, and **G!202 BCPLDEC**, plus the permanent **G!203 BCPLDEMO / DEMOSVC** teaching/reference extension allocation. Allocations do not imply implementations or successful registration.

[Cambridge runtime and library nomenclature](runtime-and-library-nomenclature.md) distinguishes the Compiler, Core Runtime, historical Base Library (BLIB/LIBHDR), System Extensions, Standard Libraries, and User/Site Libraries. It also defines module, package, header, object/load library, and the separate global-number allocation versus startup-registration responsibilities. This is a proposed packaging/ABI vocabulary, not a claim that new libraries are implemented.

## Runtime Extensions — optional module registration

[Milestone Runtime Extensions](milestone-runtime-extensions.md) (R.0–R.3)
uses explicit IEWL selection and startup registration. **R.0 — Evidence
and contract CLOSED; R.1 — Generic registration foundation CLOSED**
(owner approval 22 October 2026). The [R.1 acceptance and closure record](runtime-extensions-r1-closure-20261022.md)
reports 24/24 integrated MVS jobs PASS, all five acceptance gates PASS,
and a fresh 145 PASS / 0 FAIL / 1 expected SKIP 083 native regression
under the temporary R.1 runtime overlay.
**R.2 — Selective interoperability is ACTIVE**, with [BCPLDEMO G!203 owner approval](runtime-extensions-r2-bcpldemo-decision-20261022.md) and a [first source candidate](../bootstrap-toolchain/extensions/bcpldemo/README.md). The first real BCPLDEMO end-to-end demonstration passed MVS JOB 3075 (six IFOX steps, IEWL, and GO at RC=0000; see [JOB 3075 evidence](runtime-extensions-r2-bcpldemo-job-3075-evidence-20261022.md)). Test-only extension B (G!299) and the 0/A/B/A+B positive matrix PASSED actual MVS JOB 3080; see [the R.2 matrix design](runtime-extensions-r2-matrix-candidate-20261022.md) and [probe instructions](../bootstrap-toolchain/probes/r2-interoperability/README.md). Actual MVS matrix evidence and negative registration gates remain pending. **R.3 — Packaging and acceptance is not started.** No accepted runtime PDS
promotion was authorized.
The [R.0 source and ABI audit](runtime-extensions-r0-evidence-and-contract-20261020.md)
documents current `BCPLMAIN` export and FINISH/STOP paths and the
owner-approved shared `BCPLREG`/finalizer *model*. The
[earlier candidate ABI](runtime-extensions-r0-candidate-binary-abi-20261020.md)
is a **historical superseded proposal**, not an implemented layout.
The [owner-approved R.0 decisions A–H](runtime-extensions-r0-owner-abi-decisions.md)
select the revised 28-byte `BCRG`, 48-byte `BCEX` and 8-byte public
finalizer block. [Decision G's exact v1 limits/diagnostics](runtime-extensions-r0-decision-g-contract-20261021.md)
were approved 21 October 2026. The
[isolated G boundary probe](../bootstrap-toolchain/probes/r0-g-limits-probe/README.md)
**passed MVS JOB 2203**, including 14 verified GO markers and
four RC=0000 steps. See the
[Decision G MVS evidence](runtime-extensions-r0-decision-g-job-2203-evidence-20261021.md)
and [R.0 gate review](runtime-extensions-r0-gate-review-20261021.md).
**Historical R.0 evidence (superseded gate status):** The [shared version-1 QUERY ABI](runtime-extensions-r0-query-abi-decision-20261021.md) was separately **owner-approved** on 21 October 2026, with six-word prefix, three standard errors and no partial copies. The [two-dispatcher QUERY probe](../bootstrap-toolchain/probes/r0-query-probe/README.md) **PASSED actual MVS JOB 2206**: all five steps RC=0000, ten host tests, and the verified BCPL GO marker. See [JOB 2206 evidence](runtime-extensions-r0-query-job-2206-evidence-20261021.md). The [R.0 gate review](runtime-extensions-r0-gate-review-20261021.md) retains the remaining open obligations.
The [R.0 three-question review](runtime-extensions-r0-three-design-questions-review-20261020.md)
and [source-derived native owner ledger](runtime-extensions-r0-native-global-owner-inventory-20261020.md)
examine bounded descriptors, dependencies and historical global
ownership. The revised design is [approved for R.0
experiments](runtime-extensions-r0-testing-decision-20261020.md);
[first test-only link/descriptor probes](runtime-extensions-r0-first-probes-evidence-20261020.md)
**passed in MVS JOBs 2187–2192**. The [batched dependency and
simulated-finalizer probe](runtime-extensions-r0-batch-job-2195-evidence-20261021.md)
**passed in JOB 2195**: 14+6 actual GO records, all eight steps
RC=0000. Together these establish **26 test-only cases**.
The [ownership audit](runtime-extensions-r0-global-ownership-audit-20261021.md),
[actual application/installed BLIB trailer evidence, JOB 2197](runtime-extensions-r0-trailer-job-2197-evidence-20261021.md),
and [owner ABI review](runtime-extensions-r0-abi-decision-review-20261021.md)
record the observed G!1 application and 21 BLIB exports with only a
potential historical G!76 native overlap. The
[test-only actual-runtime G!76 probe](../bootstrap-toolchain/probes/r0-g76-precedence-probe/README.md)
**passed in actual MVS JOB 2199** with four step RCs=0000;
BLIB-present G!76 precedence is verified at START. See the
[JOB 2199 evidence](runtime-extensions-r0-g76-job-2199-evidence-20261021.md).
At that R.0 evidence stage the BLIB-absent fallback and installed
object provenance were unresolved; those historical source/provenance
qualifications must not be confused with later R.1 acceptance.
The
[Decision A trusted-link stage-1 probe](runtime-extensions-r0-decision-a-stage1-20261021.md)
**PASSED under MVS in JOBs 2207–2216**, including all ten
verified QOUT markers, six step RC=0000 results per job,
and independent JOB 2207 IEWL MAP/XREF inspection.
See the [stage-1 evidence](runtime-extensions-r0-decision-a-jobs-2207-2216-evidence-20261021.md)
and [stage-2 approved design](runtime-extensions-r0-decision-a-stage2-design-20261021.md).
The [stage-2 `IEBCOMPR` test-only probe](../bootstrap-toolchain/probes/r0-object-identity-probe/README.md) subsequently **PASSED actual calibration JOB 2217**. **JOB 2218**
compared 18 installed and freshly assembled `BCPLMEM` FB/80 records,
revealing only one END-record run-day byte difference. Strict binary
identity **fails (RC=0008)**, while the separately approved
[date-only content-equivalence audit](runtime-extensions-r0-decision-a-jobs-2217-2218-evidence-20261021.md)
passes within its narrow evidence scope. Original installed-object
source/build provenance remains open.
The R.1 campaign subsequently verified the approved public finalizer ABI
in actual integrated MVS jobs 2780–2783. No BOOT_OBJ/BOOT_DEVOBJ
installation was performed. R is not a prerequisite for M4.

The approved model uses **one public global-vector entry per optional
package**, with stable package-local opcodes. The shared opcode-0 QUERY
contract describes a side-effect-free, versioned numeric capability
query into caller-owned BCPL words. The global slots G!200–G!202 are
allocated; allocation alone does not imply implementation. R.2 will
verify two independent optional dispatchers under integrated BCPLREG
selection and test their QUERY interoperability.

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
