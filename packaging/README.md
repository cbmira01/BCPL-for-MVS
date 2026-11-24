# Packaging — architecture, milestones and project records

This directory is an **index, not a document dump**. GitHub `main` is authoritative for BCPL reconstruction source, contracts and acceptance records; MVS 3.8J, IFOX, IEWL and JES establish target-system execution evidence.

| Directory | Purpose |
| --- | --- |
| [Application discussions](applications/README.md) | Research notes on possible native BCPL applications; not project deliverables |
| [Architecture](architecture/README.md) | Runtime/library terminology, global assignments, ABI and storage contracts |
| [Milestones](milestones/README.md) | Governing milestone documents, System Extension interfaces, decisions and owner-approved closures, grouped by milestone |
| [Operations](operations/README.md) | Repository authority, safe WSL procedures, runtime builds, promotion and repository navigation |
| [Evidence](evidence/README.md) | BCPL historical audit and BCPLIO verification receipts |
| [Archive](archive/README.md) | Completed experiments, earlier proposals and detailed historical test records; not current operating instructions |
| [Distribution](distribution/README.md) | Published RC4, release manifest and registry, production and installation materials; archived experiments are not active procedures |

**Canonical full rebuild:** [Rebuild BCPL for MVS from source](../docs/Rebuild-BCPL-for-MVS-from-source.md). This guide covers MVS dataset reconstruction; it does not authorize installation or modification of permanent MVS datasets.

**QSAM acceptance qualification:** Milestone QSAM is owner-closed, with a full 00–176 regression showing 175 PASS / 1 FAIL / 1 expected SKIP and a *separate* successful case 175 rerun—not an uninterrupted green panel. See [Q.5 closure](milestones/qsam/qsam-q5-closure-20261101.md) for the exact remaining verification limits.

All official milestone/march names, published API assignments and historical evidence are preserved. The former root-level file paths were relocated by this documentation-only reorganization.

**Tape artifact release:** formally CLOSED (qualified), 24 November 2026. See the [closure](milestones/tape-artifact-release/ta8-formal-qualified-closure-and-milestone-completion-20261124.md) and [post-release audit](distribution/post-release-audit-20261124.md). TA.5 is CLOSED (qualified); TA.6 N/A for RC4. No replay of accepted MVS operations is required.
