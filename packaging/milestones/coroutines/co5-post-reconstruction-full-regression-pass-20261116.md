# CO.5 — Complete post-clean-room regular regression PASS

**Project:** BCPL for MVS 3.8 Reconstruction
**March:** CO.5 — Integration, Regression, and Release
**Source revision:** `9a621d5aac0d5c6068e10c6425b861f7480cf30a`
**Date:** 16 November 2026 (UTC evidence)
**Status:** REGULAR SUITES PASS; CO.5 IN PROGRESS pending owner acceptance
**Evidence class:** OWNER-REPORTED MVS result. The original case summaries/JES spool were not independently inspected.

## Operator evidence

The revision-guarded six-suite `tools/tests/run-project-regressions`
campaign executed with `--profile production --allow-device`, selecting
`mr10`, `bootstrap`, `runtime-extensions`, `bcpltime`,
`coroutines`, and `bcplqsam`.

- Permanent MVS-facing log: `mvs-state/reconstruction-evidence/co5-full-regressions-20261116T015902Z.log`
- Coordinator: `workarea/project-regressions/20261116T015903Z-89277-ukfu4oxd/summary.json`

The owner reported `CO.5 full regressions RC=0`,
`PROJECT REGRESSION RESULT: PASS`, and native `coroutines`
**13 PASS, 0 FAIL, 0 SKIP, 0 BLOCKED**. Individual PASS lines
for cases 181–189 were also supplied.

The coordinator requires every selected suite to PASS and stops on
any failing or blocked suite. The per-suite counts below derive
from that contract and the original suite manifests; only the
coroutines details and coordinator final result were directly
included in the supplied excerpt.

| Suite | PASS | FAIL | SKIP | BLOCKED |
| --- | ---: | ---: | ---: | ---: |
| MR10 Regression Panel | 12 | 0 | 0 | 0 |
| Native Bootstrap 00–145 | 145 | 0 | 1 (083) | 0 |
| Runtime Extensions 146–158 | 13 | 0 | 0 | 0 |
| BCPLTIME 159–162 | 4 | 0 | 0 | 0 |
| Native Coroutines 177–189 | 13 | 0 | 0 | 0 |
| BCPLQSAM 163–176, device cases included | 14 | 0 | 0 | 0 |
| **Regular campaign** | **201** | **0** | **1** | **0** |

The first full post-rebuild campaign **failed** on native JOB
6745, case 117, due to IEWL `LKED` abend **SB2D** after
`ASMAP RC=0000`. That failure is preserved. The subsequent
isolated case-117 rerun passed, and the complete six-suite
campaign subsequently passed without BCPL, IFOX, runtime or
golden-oracle modifications. The underlying SB2D cause remains
unresolved; a passing retry does not erase the earlier FAIL.

The 11 accepted `mr10-probes` Development Probes were not
selected for this new regular campaign. The separate earlier
execution record remains **10 PASS and one genuine, qualified
FAIL** in the original legacy
`10-coroutines/fixed-stack-producer-consumer` (interpreted
CODE -1). This must not be marked SKIP or PASS.

## Disposition

The owner-reported complete regular campaign passes the CO.5
post-clean-room regression gate. It does **not** itself close CO.5,
prove arbitrary coroutine semantics or authorize release publication.
The [qualified acceptance review](co5-qualified-acceptance-review-candidate-20261116.md)
remains subject to an explicit owner decision.
