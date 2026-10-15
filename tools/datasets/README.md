# Dataset management tools

The authoritative `dspal` dispatcher and its implementation modules live in this directory. Use `tools/datasets/dspal`; old paths at the tools root were removed in the M3 refactor.

`config/dspal.yaml` defines all 24 managed datasets: nine `MR10_*`, nine `CAMB_*` reserved for M4, and six `NATIVE_*`. Installation-specific credentials and overrides belong in the ignored `config/dspal.local.yaml`.

The full destructive clean-room procedure is [documented here](../../packaging/clean-room-mvs-reconstruction.md). In normal development, do **not** run `purgebcpl` unless you intend to delete and reconstruct every managed dataset.
