# Create tape

**Status:** Tape artifact release CLOSED (qualified). RC4 / BC0004 was accepted and publicly distributed on 24 November 2026. See the [formal closure](../../milestones/tape-artifact-release/ta8-formal-qualified-closure-and-milestone-completion-20261124.md) and [RC4 companion guide](../publication/RC4-README.md).

## Current implementation

Use the [distribution tools](../../../tools/distribution/README.md) for reusable release JCL generation, saved evidence review and MVS transport/verification functions. BC0005 passed the private end-to-end MVS test. The extracted helper library is offline-tested, but there is not yet an accepted candidate-independent live release driver.

## Retained source preparation and evidence

- [Offline manifest gate](scripts/ta2-offline), [bootstrap installer generator](scripts/ta2-bootstrap-installer), source inventory, lineage, allocation and stage preparation tools and their tests are retained. Their candidate-specific approval and receipt checks remain historical. Do not execute consumed operations.
- [Stage-space proposal](ta2-stage-space-proposal-20261119.json), frozen approvals, source-preparation tests and all accepted engineering records remain.
- Earlier scratch PDS/object experiments remain outside this retirement.
- RC2–RC4 production, preview, readback, recovery and installer runners and their dedicated tests are retired from active main. Their exact source, including specialized record/binary readback logic not yet generalized, is preserved at the [pre-retirement revision](https://github.com/cbmira01/BCPL-for-MVS/tree/bacf928f0364d24d89c6fa2ed3f88e2ff53fd9fc/packaging/distribution/create-tape).
- TA.1 experimental runners and JCL were retired in the earlier cleanup; use the [earlier historical tree](https://github.com/cbmira01/BCPL-for-MVS/tree/52850c4c21b6b10db3174304f5cc778bc95283fe/packaging/distribution/create-tape).

See [RC4 production evidence](ta3-rc4-production-operator-result-20261123.md), [installer design](ta3-rc4-tape-resident-installer-design-20261123.md) and the [post-release audit](../post-release-audit-20261124.md). Browse historical records at their corresponding pinned revision to resolve retired relative source links.

Preserve BC0003, BC0004, BC0005, private evidence and all consumed markers. Future production requires independently approved source preparation, manifest, unused VOLSER and operational scope. No new MVS operation is authorized by this README.
