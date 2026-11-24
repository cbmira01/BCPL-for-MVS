# Install from tape

## Current recipient documentation

Follow the [mandatory RC4 companion guide](../publication/RC4-README.md) for the published [0.1.0-rc4 / BC0004](https://github.com/cbmira01/BCPL-for-MVS/releases/tag/v0.1.0-rc4). Installation uses the BT0001 bootstrap, BT0002 installer PDS and standard MVS IEBGENER/IEBCOPY procedures in a fresh namespace. Choose MR10, NATIVE or COMBINED. Do not use older RC3 JCL or draft BT0003 instructions as the current installation procedure.

## Accepted scope

- All three profiles passed installation and directory/DCB verification; 42 PDSes / 315 member entries across fresh namespaces on the existing MVS system.
- MR10 and COMBINED passed 80 functional cases in total, including independent golden-result comparison of EXP, RP, TEST and CODE records.
- Native components are inventory/installation accepted only; the native-running Cambridge Compiler is absent.
- Independent IPL and alternate HLQ/site testing were not performed.

See [TA.3 installation results](ta3-rc4-all-profiles-accepted-20261123.md), [TA.5 formal closure](../../milestones/tape-artifact-release/ta5-formal-qualified-closure-and-ta7-transition-20261123.md) and [TA.7 acceptance](../../milestones/tape-artifact-release/ta7-clean-namespace-acceptance-20261124.md).

## Reusable verification and historical implementation

The [distribution tools](../../../tools/distribution/README.md) contain the reusable writer/installer JCL renderer, HETMAP and MR10 evidence reviewers and extracted MVS bootstrap, readback, exact catalog/member verification and JES helpers. The dedicated BC0005 exercise passed all three profile installs and 80 MR10 cases; the extracted helper module itself has offline verification only.

The consumed RC2–RC4 trial/recipient/continuation runners, TA.4 and TA.7 orchestration, dedicated tests and seven old external JCL decks have been removed from active main. Their exact contents remain at the [pre-retirement revision](https://github.com/cbmira01/BCPL-for-MVS/tree/bacf928f0364d24d89c6fa2ed3f88e2ff53fd9fc/packaging/distribution/install-from-tape). The MR10 EXP source checker and its tests remain. Historical records are unchanged; use that revision for links to retired files. Do not replay accepted installation or verification operations.

See the [post-release audit](../post-release-audit-20261124.md). Preserve installed namespaces, accepted media and private receipts. The published RC4 companion is still the recipient procedure.
