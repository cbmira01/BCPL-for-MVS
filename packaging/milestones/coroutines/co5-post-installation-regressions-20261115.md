# CO.5 — Production post-installation regression checkpoint

**Milestone:** Implement coroutine support for native compiler
**March:** CO.5 — Integration, Regression, and Release
**Git revision:** `b2ff3bc8d4d8e1373aa1a58e8b08bcf1ab51be30`
**Date:** 15 November 2026
**Evidence:** Owner-provided 314-line terminal transcript; raw
workarea/JES artifacts remain operator-local.

| Suite | PASS | FAIL | SKIP | BLOCKED |
| --- | ---: | ---: | ---: | ---: |
| MR10 regular | 12 | 0 | 0 | 0 |
| Native Bootstrap 00–145 | 145 | 0 | 1 | 0 |
| Runtime Extensions 146–158 | 13 | 0 | 0 | 0 |
| BCPLTIME 159–162 | 4 | 0 | 0 | 0 |
| Native Coroutines 177–189 | 13 | 0 | 0 | 0 |
| BCPLQSAM 163–176, device authorized | 14 | 0 | 0 | 0 |
| **Regular suites** | **201** | **0** | **1** | **0** |
| MR10 Development Probes, individually | 10 | 1 | 0 | 0 |

The five-suite coordinator reported PASS in 6m22s. BCPLQSAM
returned 14 PASS including JES punch/printer cases 175–176. The
original `10-coroutines/fixed-stack-producer-consumer` MR10
probe returned interpreted CODE -1 rather than expected 0 and
remains a **genuine, previously qualified FAIL**, not a PASS or
a new native coroutine regression. All ten other accepted MR10
probes passed when launched individually.

**Operator-local evidence paths:**
- `workarea/project-regressions/20261115T234401Z-50242-mz4cpoyl/summary.json`
- `workarea/test-suites/20261115T235024Z-68252-bcplqsam-production-ds763jft/`
- Individual `workarea/mr10-probes/20261115T2351*-` results.

This verifies the installed production candidate, **not** the
yet-to-be-run clean-room reconstruction after manifest integration.
CO.5 remains IN PROGRESS.
