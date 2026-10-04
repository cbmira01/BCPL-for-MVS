# Packaging

This directory contains notes and tooling plans for placing BCPL program and data products onto MVS 3.8J/TK5 storage.

Current documentation:

- [`dspal-direction.md`](dspal-direction.md) — current direction for the unified Linux-side `dspal` data-set tool, covering both partitioned and sequential MVS data sets; records the renaming from `pdspal` and the current BCPL managed dataset set.
- [`dspal-deployment-policy.md`](dspal-deployment-policy.md) — default `HERC02`/HLQ policy, no pinned volume by default, Git as the source of truth, and reproducible `dspal populate all|PDS` semantics including dry-run behavior.
- [`pdspal-and-mvs-storage.md`](pdspal-and-mvs-storage.md) — earlier detailed design work for the proposed Linux-side PDS-management tool; still authoritative for the underlying PDS concepts, JCL transparency, text transfer policy, TK5 userid and safety conventions, recommended BCPL namespace, and dedicated user-DASD/catalog guidance. Read `pdspal` there as superseded terminology for `dspal`.
- [`pdspal-bcpl-layout-commands.md`](pdspal-bcpl-layout-commands.md) — reproducible project-layout commands, now documented as `dspal initbcpl` and `dspal purgebcpl`, including idempotence, managed-dataset scope, confirmation, `--yes`, and `--show-jcl` semantics.

As packaging work develops, this directory is the intended home for installation layouts, MVS-side dataset conventions, transfer tooling, and release/deployment procedures.
