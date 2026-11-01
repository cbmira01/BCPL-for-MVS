# Dataset management tools

The authoritative `dspal` dispatcher and its implementation modules live in this directory. Use `tools/datasets/dspal`; old paths at the tools root were removed in the M3 refactor.

`config/dspal.yaml` defines the managed MR10, Cambridge, bootstrap, and optional-extension datasets. Installation-specific credentials and overrides belong in the ignored `config/dspal.local.yaml`.

The full destructive clean-room procedure is [documented here](../../packaging/clean-room-mvs-reconstruction.md). In normal development, do **not** run `purgebcpl` unless you intend to delete and reconstruct every managed dataset.

For a clean-room reconstruction, run `tools/datasets/dspal populate all`
after dataset initialization, then run
`tools/datasets/dspal populate all --generated-only` after
`prepare-bootstrap --with-trnilrg`. The latter
selects only `generated_members` mappings, requires the existing SHA-256
provenance inventory, and does not rewrite Git-tracked members. It also
supports `--dry-run` and `--show-jcl`.
