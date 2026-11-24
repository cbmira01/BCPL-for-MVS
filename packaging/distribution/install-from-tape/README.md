# Install from tape

## Current recipient documentation

Follow the [mandatory RC4 companion guide](../publication/RC4-README.md) for the published [0.1.0-rc4 / BC0004](https://github.com/cbmira01/BCPL-for-MVS/releases/tag/v0.1.0-rc4). Installation uses the BT0001 bootstrap, BT0002 installer PDS and standard MVS IEBGENER/IEBCOPY procedures in a fresh namespace. Choose MR10, NATIVE or COMBINED. Do not use older RC3 JCL or draft BT0003 instructions as the current installation procedure.

## Accepted scope

- All three profiles passed installation and directory/DCB verification; 42 PDSes / 315 member entries across fresh namespaces on the existing MVS system.
- MR10 and COMBINED passed 80 functional cases in total, including independent golden-result comparison of EXP, RP, TEST and CODE records.
- Native components are inventory/installation accepted only; the native-running Cambridge Compiler is absent.
- Independent IPL and alternate HLQ/site testing were not performed.

See [TA.3 installation results](ta3-rc4-all-profiles-accepted-20261123.md), [TA.5 formal closure](../../milestones/tape-artifact-release/ta5-formal-qualified-closure-and-ta7-transition-20261123.md) and [TA.7 acceptance](../../milestones/tape-artifact-release/ta7-clean-namespace-acceptance-20261124.md).

## Retained development verification

The JCL, RC2/RC3/RC4 trial runners, TA.4 MR10 verification/comparison and TA.7 clean-namespace runner are historical accepted implementation/evidence tools. They are not recipient commands. Several are dynamically imported by later runners; retain them and their tests until common functionality is extracted and dependencies are verified. Do not rerun consumed recipient/continuation or verification operations. Preserve the accepted installations, tape bytes and private receipts.

See the [post-release audit](../post-release-audit-20261124.md). [Previous chronological README](https://github.com/cbmira01/BCPL-for-MVS/blob/9f382203fcd6a5424cd916f304e3210c0f650212/packaging/distribution/install-from-tape/README.md) retains trial/recovery details.
