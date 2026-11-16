# CO.5 — First post-reconstruction regression failure, 16 November 2026

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.5 — Integration, Regression, and Release
**Source revision:** `172d5c1486a69ae427e167df22f075590d7d1654` (exact revision guarded by operator command)
**Status:** REGRESSION FAIL — ROOT CAUSE PENDING; CO.5 IN PROGRESS
**Evidence class:** Owner-reported project coordinator output (no case-level JES receipt inspected)

## Operator-reported MVS results

The first regression campaign after the successful 10-object production
clean-room reconstruction returned **RC=1**:

```text
CO.5 post-rebuild regressions RC=1
Evidence: mvs-state/reconstruction-evidence/co5-regressions-20261116T010039Z.log
PASS mr10: {'PASS': 12, 'FAIL': 0, 'SKIP': None, 'BLOCKED': None, 'TOTAL': 12}
FAIL bootstrap: {'PASS': 144, 'FAIL': 1, 'SKIP': 1, 'BLOCKED': 0, 'TOTAL': 146}
PROJECT REGRESSION RESULT: FAIL
SUMMARY: /home/calvin/Source/Repos/BCPL-for-MVS/workarea/project-regressions/20261116T010039Z-74548-kri5ahk9/summary.json
```

MR10 regular panel: **12 PASS**. Bootstrap: **144 PASS,
one actual FAIL, one expected SKIP (case 083)**. The coordinator
is fail-stop. Therefore `runtime-extensions`, `bcpltime`,
`coroutines` and `bcplqsam` in this selected campaign have **NOT
RUN** and must not be reported as passing the post-rebuild gate.
The `mr10-probes` suite was not selected.

The failing Bootstrap case ID and case-specific runner/JES diagnostics
were not included in the supplied summary excerpt. **Do not diagnose
by inference, change a test oracle, or rerun the entire suite before
retrieving the original case evidence.** The pre-rebuild regular-suite
PASS and the independent rebuild-installed coroutine GO PASS remain
distinct historical evidence; neither supersedes this real failure.

## Next evidence and disposition

Read the `FAIL <case>` record from
`workarea/project-regressions/20261116T010039Z-74548-kri5ahk9/bootstrap.log`.
The record points to the preserved case runner log under
`workarea/test-suites`. Review that case log, MVS payload/job identities,
return codes and unexpected actual-versus-expected output. Implement a
source-correct repair only if supported by that evidence, run assistant
host checks, commit the approved repair to GitHub `main`, and then
rerun the affected MVS case followed by the applicable remaining suites.

The accepted CO.4 scope, permanent globals, and the separately
qualified MR10 fixed-stack development-probe FAIL remain unchanged.
**CO.5 remains IN PROGRESS.**
