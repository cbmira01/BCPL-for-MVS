# JES printer-window reader — native regression default decision

**Project:** BCPL for MVS 3.8 Reconstruction
**Date:** 10 November 2026 (US Eastern)
**Authority:** Owner-directed change following the verified full six-suite regression
**Status:** Default selection implemented in regression harnesses; host checkout verification still required

## Decision

The guarded byte-offset JES printer reader is **the default for numbered native regression cases 00–176**, including BCPLQSAM. The default changes *selection* of an already-tested reader, not its cursor integrity, JOB completion, assembly, link, output, or fail-closed evidence contracts.

The existing environment variable remains supported for backward compatibility:

| Native regression environment | Reader selected |
| --- | --- |
| `BCPL_PRINTER_WINDOW_TRIAL` unset | **Offset-based (default)** |
| `BCPL_PRINTER_WINDOW_TRIAL=1` | Offset-based (explicit) |
| `BCPL_PRINTER_WINDOW_TRIAL=0` | Legacy full-printer scan (explicit opt-out) |
| Any other value | Error; do not proceed with JES |

The old variable retains its name to avoid breaking existing commands or tests. Default-on behavior is implemented at the native regression harness entry, with the setting exported to its Cambridge compiler and QSAM children. Direct BCPLQSAM regression invocation also defaults to the offset reader and propagates the selection to compilation.

## Boundaries

- **Only native regression execution** changes default. The reusable `tools/mvs/submit-jcl`, `tools/mvs/job-summary`, `tools/mvs/dump-report-for-job`, `tools/bootstrap/compile-mvs` when invoked independently, and dataset management utilities keep their established defaults.
- MR10 and MR10 Development Probes retain their independent execution/report paths.
- BCPLQSAM device authorization is unchanged: `--allow-device` and the existing guarded PUN1 controls are still required where applicable.
- Invalid, rotated, truncated or changed JES printer cursor fails closed; no silent fallback to historical records, no automatic submission retry, and no new parallel JES authorization.
- No MVS source, JCL cards, permanent datasets, installed objects, QSAM milestone/march identifiers, or release process are changed.

## Evidence and validation

The [owner-reported 10 November six-suite verification](jes-printer-window-six-suite-verification-20261110.md) passed **194 cases**, with **0 FAIL**, **1 expected SKIP (083)** and **0 BLOCKED** at revision `5cb4d64341f5dd478d87723b941258f177708f07`, while the offset reader was explicitly enabled. Measured elapsed time was **9m17s**, compared with an earlier 73m57s baseline (a cross-revision comparison, not isolated causal attribution). These results establish the reader's functionality across all native suites, but do not constitute a fresh execution under the new unset-variable default.

New host-only tests verify the default and explicit-legacy selection, the direct QSAM compiler path, and existing fail-closed behavior. Run these tests and the manifest check on the updated checkout before any separate owner-authorized live MVS regression.

See also the [historical opt-in trial](jes-printer-window-opt-in-trial-20261110.md) and [WSL operator command policy](../operator-wsl-command-policy.md).
