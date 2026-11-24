# Distribution manifest

The manifest is the authoritative release selection, dataset sequence and DCB contract. The [release registry](../registry/releases.yaml) owns candidate identity, VOLSER reservations and lifecycle annotations. The development dataset map [config/dspal.yaml](../../../config/dspal.yaml) is not the release selection authority.

## Published candidate

[BCPL-0.1.0-rc4.yaml](releases/BCPL-0.1.0-rc4.yaml) defines BC0004, 21 logical datasets, three installation profiles, native compiler absent and historical Cambridge source included. Preserve all four frozen manifests and their registry reservations. RC1–RC3 are historical candidate records, not current recipient instructions.

The [schema v1 design](schema-v1-design.md), [TA.0 inventory](ta0-inventory.yaml), provenance and binary-evidence records retain the original design and acceptance qualifications.

## Validation

The [manifest validator](../../../tools/distribution/validate-manifest.py) is a read-only structural checker; its default input is the historical TA.0 inventory, not RC4. Select the desired manifest explicitly. Its strict --release mode requires complete MVS inventory and rights evidence and must not be interpreted as having passed for the qualified preservation-policy RC4 release.

See [distribution tools](../../../tools/distribution/README.md) for retained evidence utilities and the [post-release audit](../post-release-audit-20261124.md) for dependency/retirement decisions. Do not modify frozen manifests to make an obsolete strict gate pass.

[Previous manifest README](https://github.com/cbmira01/BCPL-for-MVS/blob/9f382203fcd6a5424cd916f304e3210c0f650212/packaging/distribution/manifest/README.md) preserves the TA.0/TA.2 chronological notes.
