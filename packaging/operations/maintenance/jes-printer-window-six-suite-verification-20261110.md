# JES printer-window optimization — six-suite verification (10 November 2026)

**Project:** BCPL for MVS 3.8 Reconstruction
**Status:** Recorded PASS evidence; optimization remains explicitly opt-in
**Source revision tested:** `5cb4d64341f5dd478d87723b941258f177708f07` on GitHub `main`
**Evidence provenance:** Owner-provided WSL console output from the actual run. The full generated logs remain in the owner's local `workarea/`; they are **not** included in this Git commit.

## Execution contract

The operator executed `tools/tests/run-project-regressions` with:

- `BCPL_PRINTER_WINDOW_TRIAL=1` (pre-submission byte-offset printer reader for native cases 00–176).
- Explicit `--run` selection of all six suites: `mr10`, `mr10-probes`, `bootstrap`, `runtime-extensions`, `bcpltime`, `bcplqsam`.
- `--profile installed-r5-t1 --allow-device --progress`.
- Explicit device authorization covered BCPLQSAM cases 175–176; the existing guarded PUN1 policy for case 175 remained in force.
- The interpreted MR10 suite and probes retained their own independent execution/report paths; the optimized reader applied to the numbered native System/370 suites.

The operator's command first verified an up-to-date checkout at the tested revision, `git diff --check HEAD^ HEAD` (**RC=0**), all **13** host-only `test_printer_window*.py` checks (**PASS**, RC=0), and `tools/tests/run-project-regressions --check` (**PASS**, RC=0). Only then did the authorized JES regression run.

## Complete six-suite result

| Suite | PASS | FAIL | SKIP | BLOCKED |
| --- | ---: | ---: | ---: | ---: |
| MR10 | 12 | 0 | 0 | 0 |
| MR10 Development Probes | 6 | 0 | 0 | 0 |
| Bootstrap (00–145) | 145 | 0 | 1 | 0 |
| Runtime Extensions (146–158) | 13 | 0 | 0 | 0 |
| BCPLTIME (159–162) | 4 | 0 | 0 | 0 |
| BCPLQSAM (163–176) | 14 | 0 | 0 | 0 |
| **Total** | **194** | **0** | **1** | **0** |

- **Project coordinator:** `PROJECT REGRESSION RESULT: PASS`.
- **Operator shell:** `Full regression RC=0`.
- **Expected SKIP:** bootstrap case **083**, source-only instrumentation unavailable under the installed profile; no other skips or blocked cases.
- **Device cases:** BCPLQSAM **175** (class-B punch) and **176** (class-A printer) both reported PASS.
- **Evidence directory:** `workarea/project-regressions/20261110T162703Z-4802-6tbqwikq/`.
- **Coordinator summary:** `workarea/project-regressions/20261110T162703Z-4802-6tbqwikq/summary.json`.

These are the results reported by the executed suite coordinator; this record does not claim independent retrieval of each local JES job report or MVS spool artifact.

## Host elapsed time

The corrected WSL wall-clock timer used `date +%s` before and after the coordinator command, and reported:

| Measurement | Duration | Seconds |
| --- | ---: | ---: |
| Earlier complete baseline (10 Nov, revision `268600559e58defb410b7bb7719a66bc8e3c9a85`) | 73m 57s | 4,437 |
| Full opt-in printer-window run (this revision) | **9m 17s** | **557** |
| Difference | **64m 40s** | **3,880** |

This represents an observed **7.97×** shorter elapsed time and approximately **87.4%** reduction relative to the earlier full-suite baseline. The measurements were taken at different Git revisions and potentially different host conditions; they establish a compelling measured comparison, not a controlled attribution of every saved second. The one-second-resolution shell timer is not an MVS CPU-time measurement.

A preceding full six-suite PASS at `c0922f362a0e716104a7911b6d8d1a82e39b16c1` also reported 194 PASS / 1 expected SKIP, but its timer failed due to incorrect Bash arithmetic and no verified wall time was available for that run. That preceding revision had **not yet** enabled the offset reader for BCPLQSAM native jobs.

## Disposition and boundaries

1. The operator-provided evidence supports **complete passing native regression coverage of the opt-in reader**, including the new BCPLQSAM native reader path, without changing the accepted per-case outcomes.
2. The original full-file printer reader remains available by leaving `BCPL_PRINTER_WINDOW_TRIAL` unset. **This record does not authorize default-on activation**, release changes, object promotion, or additional JES/device activity.
3. The existing fail-closed rules for invalid cursors, uncertain JES submissions and printer-log identity remain unchanged.
4. This is a **regression-optimization verification record**, not a new QSAM milestone/march or an amendment to the historical Q.5 closure.

See [the opt-in reader design and boundaries](jes-printer-window-opt-in-trial-20261110.md) and [initial performance analysis](regression-runner-performance-analysis-20261109.md).
