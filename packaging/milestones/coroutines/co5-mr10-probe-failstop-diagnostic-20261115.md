# CO.5 — MR10 Development Probe fail-stop coordinator diagnosis

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.5 — Integration, Regression, and Release
**Date:** 15 November 2026
**Failed campaign revision:** `5e37c5353b97e97d3c4a11cbac3ee151c863dc9b`
**Status:** IN PROGRESS; root probe failure not yet identified from raw receipts

## Source-revision-tracked operator report

The operator ran `tools/tests/run-project-regressions` with MR10, the
accepted MR10 Development Probes, and selected native suites under
`production`. The coordinator created:

`workarea/project-regressions/20261115T203132Z-26985-zq2u6pm2/summary.json`

The operator transcript reported **MR10 12/12 PASS**, then
`FAIL mr10-probes: MR10 probes: unaccepted case selected`, overall project
FAIL, RC=1 and 30 seconds elapsed. The coordinator stopped before native
suites. This is NOT a PASS or proven actual probe regression. Raw
`mr10-probes` runner receipts were not supplied in this conversation.

## Source investigation and coordinator defect

GitHub `main` contains exactly eleven accepted MR10 Development Probe
identities. Inventory preflights and selects only those accepted entries.
The probe runner stores case `verification` only after it begins executing
each case. On any early failure it leaves subsequent entries `NOT_RUN`
without a `verification` field. The coordinator incorrectly demanded
`verification=ACCEPTED` on **every** entry before inspecting the FAIL and
NOT_RUN statuses, generating `unaccepted case selected` and masking the
earlier failing probe and its diagnostic.

The repair:

- Initializes each selected probe receipt with its manifest `verification`,
  before any MVS work begins.
- Accepts a missing verification field only for legacy `NOT_RUN` entries
  already constrained by the preflight accepted inventory. Explicit
  `UNVERIFIED` or other unexpected verification remains rejected.
- Preserves the first failing case's actual reason in project summary and
  emits one concise `MR10 PROBE FAILURE` line on genuine probe FAIL.
- Retains fail-stop behavior, all accepted goldens, test identities, RC
  verification and legacy device permissions. No BCPL/assembly/JCL/MVS
  dataset or installed object is modified.

## Assistant-operated host verification

Eight isolated Python host unit tests passed on the corrected
`parse_mr10_probes` contract: complete PASS, new-style fail-stop,
legacy fail-stop, unaccepted executed/pending cases, inconsistent
counts, incorrect runner RC and NOT_RUN without FAIL. The same eight
checks are source-controlled in
`tools/checks/test_stage3_mr10_probe_failstop.py`.

**Next evidence:** Retain the original failing case as FAIL. Rerun only
the MR10 Development Probe suite at the new Git revision with
`--progress` to identify the exact first failed case and native JES
or compiler diagnostic, then address that cause rather than guessing.
The earlier MR10 12-case PASS is unchanged. Other native/project
suite results remain pending for this campaign.

**CO.5 — Integration, Regression, and Release remains IN PROGRESS.**
