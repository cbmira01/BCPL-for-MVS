# Distribution manifest

Reserved for the **authoritative source-controlled release inventory**: selection of deployable datasets, **logical tape dataset sequence**, source DASD identifiers resolved against `dspal` where appropriate, position-based tape aliases, destination DASD templates, payload kind, attributes, constituent members, checks and release identity.

**Approved tape alias rule:** logical dataset sequence `n` has tape DSN `BCPL.BTnnnn`, with `nnnn` zero-padded (e.g. `BCPL.BT0003` means logical dataset sequence 3, **not** Hercules `hetmap` physical file 3). `BCPL.BT0001` is reserved for sequential FB80 installation instructions; `BCPL.BT0002` for installation JCL/procedures. Other assignments are release-manifest-driven. Producer and consumer JCL must use the same manifest; the target HLQ is supplied by the receiving MVS site.

See [native compiler distribution and tape naming decisions](../native-cambridge-compiler-distribution-decisions-20261108.md) and [cross-release version/VOLSER registry decisions](../release-version-and-volser-registry-decisions-20261108.md). The registry tracks identities across releases; this directory holds each release's actual ordered tape inventory.

The manifest format and authoritative inputs (including `config/dspal.yaml`) are to be specified before producing media. Do not treat this directory as a complete distribution manifest.

The [16 November approved payload scope](../release-payload-scope-decision-20261116.md) requires entries for both independently installable compiler environments, the Coroutine Support Library, the three accepted System Extensions, the MR10 11 + 17 demos and 12-case MVS-verifiable regression panel. These are **logical release selection requirements**, not assigned `BCPL.BTnnnn` slots, physical DASD datasets or finished member inventories. Preserve the single source-of-truth manifest and the reserved `BT0001`/`BT0002` roles.


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
