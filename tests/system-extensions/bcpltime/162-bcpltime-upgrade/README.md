# Native regression 162 — BCPLTIME T.1

Part of **T.1 — Packaging and Acceptance**. This case uses
`source.bcpl`, `time-selection.asm`, and `expected.txt`.

The numbered runner compiles the BCPL application with the MVS-hosted
demoted Cambridge compiler, assembles optional extension sources through
IFOX in source mode, and verifies the IEWL MAP and native output.
Installed mode is read-only and requires separate owner-approved
BCPLTIME package installation. See
`bootstrap-toolchain/extensions/bcpltime/T1-REGRESSION.md`.

No MVS pass has yet been reported for this case.
