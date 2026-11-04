# Operations, policies and repository navigation

- [Repository and MVS authority](git-mvs-authority.md) — Git source authority and resident-system verification responsibilities
- [WSL operator command policy](operator-wsl-command-policy.md) — guarded commands, no fail-fast, approvals and reporting
- [Repository map](repository-map.md) — directories, sources, build and test entry points
- [Runtime development workflow](runtime-development-workflow.md)
- [Runtime object promotion](runtime-object-promotion.md)
- [Maintenance](maintenance/) — historical repository/regression maintenance notes
- [Stage 2A precommit source relocation review](maintenance/repository-module-stage2a-precommit-review-20261103.md) — proposed extension-path move, candidate checks, and verification gates
- [Stage 2A V2/V3 host-check remediation](maintenance/stage2a-v2-v3-host-check-remediation-20261103.md) — failing checks, corrections and 49-deck offline parity gate
- [Stage 2A V1–V3 host verification record](maintenance/stage2a-v1-v3-verification-20261103.md) — owner-reported WSL unit tests, Q5PKG synthetic check, and 49-deck old/new parity
- [Stage 2A V4 verification and completion](maintenance/stage2a-v4-verification-and-completion-20261103.md) — four read-only MVS PDS inventories; 16 successful native cases; bounded Stage 2A completion
- [Stage 2B suite ownership implementation](maintenance/stage2b-manifest-implementation-20261104.md) — 177-case suite manifest design, compatible runner and host-only checks; native parity pending
- [Stage 1 repository/module and regression migration audit](maintenance/repository-module-and-regression-migration-stage1-audit-20261103.md) — current source/test layout, path dependencies, target mapping and gated migration plan

The canonical [clean-room reconstruction guide](../../docs/Rebuild-BCPL-for-MVS-from-source.md) remains in `docs/`, not here. A Git commit does not authorize JES submissions, dataset writes or production-object promotion.
