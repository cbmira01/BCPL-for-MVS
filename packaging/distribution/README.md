# MVS tape distribution

**Status:** Tape artifact release formally CLOSED (qualified), 24 November 2026. The published prerelease is [0.1.0-rc4 / BC0004](https://github.com/cbmira01/BCPL-for-MVS/releases/tag/v0.1.0-rc4).

Start with the [RC4 companion guide](publication/RC4-README.md), which supersedes the older BT0003 documentation. It describes installation using MVS utilities, MR10 use, limitations and provenance. The MR10 Kit Compiler is independently usable. The native compiler is absent; native components and historical Cambridge sources are work in progress. All three profiles passed inventory and installation; MR10 and COMBINED passed 80 functional cases on the existing MVS system in fresh namespaces. Historical redistribution rights remain unresolved.

## Authoritative records and materials

| Location | Purpose |
| --- | --- |
| [Manifest](manifest/README.md) | Frozen release manifests, design inventory and schema |
| [Registry](registry/releases.yaml) | Version, VOLSER and lifecycle records |
| [Publication](publication/) | Mandatory RC4 companion, release notes and exact-byte package reviewer |
| [Create tape](create-tape/README.md) | Retained producer and historical MVS experiments |
| [Reusable release interface](../../tools/distribution/README.md) | Candidate-independent offline write/install JCL and saved tape/MR10 review |
| [Install from tape](install-from-tape/README.md) | Installer design and retained recipient/acceptance tooling |
| [Compiler source](compiler-source/README.md) | Historical source selection and fidelity investigation |
| [Documentation PDS inputs](docs/) | Frozen draft input text for BT0003; not authoritative RC4 instructions |
| [Formal closure](../milestones/tape-artifact-release/ta8-formal-qualified-closure-and-milestone-completion-20261124.md) | Accepted scope and qualifications |
| [Post-release audit](post-release-audit-20261124.md) | Keep/retire/delete decisions and dependency constraints |

RC4 contains 21 logical datasets, 64 AWS physical files and 150 selected PDS member entries across the combined profile. Do not modify the published archive, frozen manifests, reservation entries, release tag, RC3/RC4 tape images or accepted evidence. Do not replay consumed one-shot operations.

## Development reconstruction is separate

Use the [canonical clean-room reconstruction runbook](../../docs/Rebuild-BCPL-for-MVS-from-source.md) for development-system reconstruction; it is not the RC4 recipient installer. The [reconstruction automation decision](clean-room-reconstruction-automation-decision-20261104.md) and [batch reconstruction closure](clean-room-batch-reconstruction-closure-20261109.md) remain applicable historical design/evidence records.

Private MVS reports, evidence seals, original release archives and no-retry markers belong under the established ignored workarea or protected owner backups. Preserve accepted release evidence before any workarea cleanup. The historical [TA.0 evidence placement policy](manifest/ta0-evidence-placement-and-migration-20261117.md) remains relevant; the migration operation is not a routine task.

[Previous distribution README](https://github.com/cbmira01/BCPL-for-MVS/blob/9f382203fcd6a5424cd916f304e3210c0f650212/packaging/distribution/README.md) preserves the chronological development notes. Use the current links above for status and procedures.
