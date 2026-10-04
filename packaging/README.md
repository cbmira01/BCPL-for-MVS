# Packaging

This directory contains notes and tooling plans for placing BCPL program and data products onto MVS 3.8J/TK5 storage.

Current documentation:

- [`pdspal-and-mvs-storage.md`](pdspal-and-mvs-storage.md) — design for the proposed Linux-side `pdspal` PDS-management tool; command set; JCL transparency; text transfer policy; TK5 userid and safety conventions; recommended BCPL PDS namespace; and dedicated user-DASD/catalog guidance.
- [`pdspal-bcpl-layout-commands.md`](pdspal-bcpl-layout-commands.md) — reproducible project-layout commands `pdspal initbcpl` and `pdspal purgebcpl`, including idempotence, managed-dataset scope, confirmation, `--yes`, and `--show-jcl` semantics.

As packaging work develops, this directory is the intended home for installation layouts, MVS-side dataset conventions, transfer tooling, and release/deployment procedures.
