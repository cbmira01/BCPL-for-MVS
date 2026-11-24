# Create tape

**Status:** Tape artifact release CLOSED (qualified). RC4 / BC0004 was produced and accepted on MVS, then publicly distributed on 24 November 2026. See the [formal closure](../../milestones/tape-artifact-release/ta8-formal-qualified-closure-and-milestone-completion-20261124.md) and [RC4 companion guide](../publication/RC4-README.md).

This directory preserves the producer, JCL, tests and engineering records used to establish tape mechanics, manifest-driven production and the RC4 installer. It is not a repeatable general-purpose release runbook.

## Retained implementation

- [RC4 installer generator](scripts/ta3-rc4-installer) and [RC4 production runner](scripts/ta3-rc4-production): accepted candidate-specific implementation. The production operation is consumed; do not replay it.
- [Offline manifest renderer](scripts/ta2-offline), [bootstrap installer generator](scripts/ta2-bootstrap-installer), RC2/RC3 producers and readback utilities: retain because later scripts dynamically load earlier helpers.
- [Stage-space proposal](ta2-stage-space-proposal-20261119.json), approval records, JCL and tests: retain as exact historical inputs and regression fixtures.
- TA.1 and scratch PDS/object tape experiments: historical experiments, not current operator entry points. Retire their runnable wrappers only after checking dependencies and preserving the release-era source.

See [RC4 production evidence](ta3-rc4-production-operator-result-20261123.md), [installer design](ta3-rc4-tape-resident-installer-design-20261123.md) and the [post-release audit](../post-release-audit-20261124.md).

Preserve BC0003, BC0004, accepted evidence and consumed markers. Future production requires an independently approved new candidate, manifest, VOLSER and operational scope; do not reuse old candidate-specific approval records. No new MVS operation is authorized.

[Previous detailed README](https://github.com/cbmira01/BCPL-for-MVS/blob/9f382203fcd6a5424cd916f304e3210c0f650212/packaging/distribution/create-tape/README.md) preserves all 902 lines of chronological experiment and checkpoint instructions; the individual evidence records remain at their original paths.
