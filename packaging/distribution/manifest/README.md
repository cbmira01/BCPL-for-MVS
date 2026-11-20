# Distribution manifest

Reserved for the **authoritative source-controlled release inventory**: selection of deployable datasets, **logical tape dataset sequence**, source DASD identifiers resolved against `dspal` where appropriate, position-based tape aliases, destination DASD templates, payload kind, attributes, constituent members, checks and release identity.

**Approved tape alias rule:** logical dataset sequence `n` has tape DSN `BCPL.BTnnnn`, with `nnnn` zero-padded (e.g. `BCPL.BT0003` means logical dataset sequence 3, **not** Hercules `hetmap` physical file 3). `BCPL.BT0001` is reserved for sequential FB80 installation instructions; `BCPL.BT0002` for installation JCL/procedures. Other assignments are release-manifest-driven. Producer and consumer JCL must use the same manifest; the target HLQ is supplied by the receiving MVS site.

See [native compiler distribution and tape naming decisions](../native-cambridge-compiler-distribution-decisions-20261108.md) and [cross-release version/VOLSER registry decisions](../release-version-and-volser-registry-decisions-20261108.md). The registry tracks identities across releases; this directory holds each release's actual ordered tape inventory.

The manifest format and authoritative inputs (including `config/dspal.yaml`) are to be specified before producing media. Do not treat this directory as a complete distribution manifest.

The [16 November approved payload scope](../release-payload-scope-decision-20261116.md), as revised by the [subsequent scoped-release decision](../release-without-native-compiler-decision-20261116.md), requires the full independent MR10 compiler/demos/12-case panel and accepted native Core Runtime, historical `BLIB`, Coroutine Support Library and three System Extensions. The native-running Cambridge Compiler is required **only** when `native_compiler: included`. These are release-selection requirements, not assigned tape slots beyond `BT0001`/`BT0002`, recipient datasets or completed acceptance. One manifest remains authoritative.


## TA.0 owner-approved design, 16 November 2026

- [TA.0 architecture / inventory](ta0-release-architecture-and-inventory.md)
- [Manifest schema v1 design](schema-v1-design.md)
- [Release without the unfinished native compiler](../release-without-native-compiler-decision-20261116.md)

The per-candidate manifest must explicitly declare `native_compiler: absent` or `included`. A scoped release without the compiler remains valid after full MR10 and selected native-component verification, clean-target installation, provenance audit and separate publication approval. The TA.6 self-compilation gate applies only to candidates including the compiler. **Only BT0001 and BT0002 roles are reserved; later logical positions are proposals.** No candidate identity, VOLSER or AWS image has been created.

## TA.0 implemented design-stage inventory and static preflight

See [ta0-inventory.yaml](ta0-inventory.yaml) for the **design-only** approved
selection (20 logical tape datasets, 127 PDS members including 79 MR10).
Sequence positions after BT0002 are proposed, not frozen for any candidate.

See the read-only [manifest validator](../../../tools/distribution/validate-manifest.py)
and its [offline tests](tests/test_validate_manifest.py).
See the [TA.0 member provenance and recipient-JCL dependency audit](ta0-provenance-and-dependency-audit.md), which derives from the inventory rather than selecting release content. It requires PyYAML
on the **development host**, not on recipient MVS.

```sh
python3 -B tools/distribution/validate-manifest.py
python3 -B tools/distribution/validate-manifest.py --audit-json
python3 -B -m unittest discover -s packaging/distribution/manifest/tests -p 'test_*.py' -v
```

The optional `--release` preflight must **FAIL** on the design-only inventory.
It does not create media or reserve any version/VOLSER. No completed per-release
manifest, rights audit, MVS readback evidence, consumer JCL or tape exists.
Retire the TA.0 proposed selection into one reviewed per-candidate manifest
at release preparation; do not maintain two competing authoritative inventories.

## TA.0 selected-JCL source dependency preflight

The [read-only JCL dependency auditor](../../../tools/distribution/audit-jcl-dependencies.py) checks the ten selected MR10/native build/demo/regression jobs against the **same** design inventory, reports used programs and selected dataset/member references, and flags missing site JOB cards and `HERC02` development HLQ. For a source-level dependency worksheet:

```sh
python3 -B tools/distribution/audit-jcl-dependencies.py --json
```

The stricter `--strict` run is expected to **fail** on existing development JCL. See the [17 November JCL findings](ta0-provenance-and-dependency-audit.md#5-nativemr10-release-jcl-dependency-closure--17-november-2026-checkpoint) and [offline tests](tests/test_jcl_dependency_audit.py). This does not transform JCL, provide the absent native-running compiler or replace recipient MVS execution evidence.

## TA.0 selected MVS binary build-chain audit

The read-only [binary build-chain auditor](../../../tools/distribution/audit-binary-build-chain.py) and [offline tests](tests/test_binary_build_chain.py) map all **15** selected binary object/load members to their selected source members, reconstructed build JCL and expected IFOX/IEWL steps without executing them. It detects drift from `tools/reconstruction/verify.py`, and can inspect *saved* exact-member `dspal ls` listings supplied later by an operator.

```sh
python3 -B tools/distribution/audit-binary-build-chain.py --json
python3 -B tools/distribution/audit-binary-build-chain.py --strict
```

`--strict` **must fail** on the design-only inventory and empty evidence slots. `BOOT_OBJ(BLIB)` depends on non-distributed development `BLIBBLD`; `BOOT_OBJ(COROUTIN)` depends on pre-generated assembler. Historical qualified reconstruction receipts do not automatically establish the binary contents or redistribution rights of a new tape candidate. See the [source-to-build mapping and evidence limitations](ta0-provenance-and-dependency-audit.md#6-binary-source-to-build-chain-and-saved-inventory-checks--17-november-2026).

## TA.0 retained MVS build evidence preflight

The [read-only retained-evidence contract](ta0-mvs-build-evidence-intake.md)
and [inspector](../../../tools/distribution/audit-mvs-build-evidence.py)
check operator-supplied SHA-256-pinned JES summary/report pairs and exact
binary PDS member listings using the existing reconstruction verifier.

The inspector does not execute MVS jobs, compare object/load records, prove
source Git-to-MVS equivalence, decide rights, or authorize a release.
See [18 synthetic evidence tests](tests/test_mvs_build_evidence.py).



## TA.0 development binary evidence reconciliation — 17 November 2026

The [JOB 9061 ICINT19 executable-use and fourteen-object reconciliation record](ta0-binary-evidence-reconciliation-20261117.md)
documents the owner-reported **SAVED_EXECUTION_VERIFIED** result (twice
revalidated, no new JES job). The read-only
[TA.0 binary reconciler](../../../tools/distribution/reconcile-ta0-binary-evidence.py)
rechecks the three retained FB80 object panels and the pinned JOB 9060/9061
directory/executable receipt together using the *one* existing TA.0 design
selection and the historical printed hash ledger. It writes its derived
private index only under ignored repository workarea/.

This is development MVS printer and executable-use evidence. It is not raw
source-to-DASD byte provenance, a RECFM=U restore, a production manifest, tape
proof, rights clearance or release acceptance. TA.0 remains IN PROGRESS.


## TA.0 successful retained-binary reconciliation

The [17 November binary reconciliation evidence](ta0-binary-evidence-reconciliation-20261117.md)
now records a **live PASS (qualified)**: 14/14 selected FB80 object members,
902 records / 72,160 decoded printer bytes, exactly two historical
pre-pagination receipts, JOB 9060 load directory, and JOB 9061
development `ICINT19` executable-use verification. The original JES reports
and derived `reconciliation.json` remain private under ignored
`workarea/`. This is *not* an independent DASD byte comparison, build
provenance clearance, `RECFM=U` tape restoration, or candidate/release
acceptance. Continue with the existing eight-build-job provenance intake
contract without rerunning accepted printer pilots.

## TA.2 — Corrected owner-approved historical-source-only rc2

The owner reconfirmed candidate `BCPL-0.1.0-rc2` and VOLSER
`BC0002`, but superseded the earlier proposed two-source-PDS layout.
The canonical `releases/BCPL-0.1.0-rc2.yaml` now selects **21**
logical tape datasets: the original 20 in unchanged order plus
`BT0021`, a 15-member historical Cambridge Compiler source PDS
(`CAMB_SOURCE`). The demoted compiler, development-specific filters,
regression instrumentation and support are **GitHub-only**, not tape
content. `CAMB_DEMOTED` and `BT0022` are excluded.

`native_compiler: absent` remains true even though
`cambridge_source: included`. `cambridge-source` is an optional
one-PDS source-only group for the native-components and combined
installation profiles; MR10-only remains independent. The
`BCPL-0.1.0-rc1` manifest and `BC0001` reservation are preserved.

`tools/distribution/validate-manifest.py` is the canonical schema-v1
preflight; the supplementary `compiler-source/successor-contract.py`
cross-checks historical-member identity and registry SHA-256. Both
exclude a demoted PDS from the release contract. The existing 20 MVS
staging receipts remain accepted historical evidence; new `BT0021`
directory, DCB, record-fidelity and provenance evidence are **pending**.
No AWS media, new staging job, recipient install or rights approval
has been obtained for rc2.
