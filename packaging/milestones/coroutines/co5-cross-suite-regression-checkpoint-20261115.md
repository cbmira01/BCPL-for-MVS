# CO.5 — Cross-suite regression checkpoint, 15 November 2026

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.5 — Integration, Regression, and Release
**Status:** Regression checkpoint qualified; CO.5 IN PROGRESS
**Tested source revision:** `6f039e7bd1e3cd8e57ef8b4fede986920b1172e7` (`main`)
**Evidence class:** OWNER-REPORTED MVS EXECUTION; summary-only for native runs, raw JES reports not independently inspected by assistant
**Profile:** `production` for the five-suite coordinator and BCPLQSAM native run

## Execution evidence from operator transcript

The operator's revision-guarded execution at `6f039e7bd1e3cd8e57ef8b4fede986920b1172e7` completed the three
previously unexecuted accepted MR10 Development Probes, then the five
selected coordinated suites, then BCPLQSAM's twelve non-device cases.
The transcript reports:

| Suite/campaign | PASS | FAIL | SKIP | NOT_RUN | Reported result |
| --- | ---: | ---: | ---: | ---: | --- |
| MR10 Development Probes, previous fail-stop run | 7 | 1 | 0 | 3 | FAIL; existing legacy incompatibility |
| MR10 Development Probes, remaining selection | 3 | 0 | 0 | 0 | PASS, RC=0 |
| MR10 Regression Panel | 12 | 0 | 0 | 0 | PASS |
| Bootstrap | 145 | 0 | 1 | 0 | PASS; expected SKIP 083 |
| Runtime Extensions | 13 | 0 | 0 | 0 | PASS |
| BCPLTIME | 4 | 0 | 0 | 0 | PASS |
| Coroutines (native cases 177–189) | 13 | 0 | 0 | 0 | PASS |
| BCPLQSAM non-device (163–174) | 12 | 0 | 0 | 0 | PASS, RC=0 |
| BCPLQSAM device (175–176) | 0 | 0 | 0 | 2 | NOT RUN; separate authorization required |

The MR10 Development Probe entries are **two separate runs**, not one
eleven-case PASS. Together they cover ten accepted PASS and the preserved
`10-coroutines/fixed-stack-producer-consumer` FAIL, the independently
documented CO.0 legacy first-activation incompatibility (JES 5499,
previously reproduced as JOB 5318). The separate compatible
`fixed-stack-co0-candidate.bcpl` passed JOB 5321; it does not reclassify
the original accepted fixture as PASS or SKIP.

Across distinct case identities under the applicable current inventory:
**209 PASS, 1 accepted legacy FAIL, 1 expected SKIP, 2 not run device
cases (213 total identities)**. The 209 PASS comprise 12 MR10 Regression
Panel, 10 MR10 Development Probes, and 187 native tests (including the
12 BCPLQSAM non-device cases). These are aggregated coverage counts from
separately executed campaigns, **not** a single all-suites PASS.

## Exact evidence locations and checks reported

- Remaining three Development Probes:
  `workarea/mr10-probes/20261115T214035Z-27407-fl8okmho/summary.json`;
  runner RC=0. All three passed their accepted goldens and **14+14+12
  = 40** individual JES step contracts, as attested by the runner:
  `10-coroutines/resumeco-chain`,
  `10-coroutines/create-delete-static-pool`,
  `11-getvec-freevec`.
- Five-suite coordinated campaign:
  `workarea/project-regressions/20261115T214044Z-27427-33vcqcdh/summary.json`;
  **PASS, RC=0**, elapsed **6m 30s**; **187 PASS, 1 expected SKIP,
  0 FAIL, 0 BLOCKED** across MR10 and four selected native suites.
  Per-suite breakdown above.
- BCPLQSAM isolated non-device campaign:
  `workarea/test-suites/20261115T214714Z-45584-bcplqsam-production-qwjrw2e_/summary.json`;
  cases **163–174** all PASS, RC=0. No device permission passed.
- The earlier fail-stop probe campaign and JES 5499 details remain in
  [the CO.5 fixed-stack compatibility report](co5-mr10-fixed-stack-negative-code-20261115.md)
  and its original local workarea receipts. That run terminated before
  the three cases completed in the later selection.

These reports were produced by the operator's source-controlled runners.
For native tests the runners report per-case logs and source-selected
BCPL/IFOX/IEWL/GO checks. The assistant received the console transcript,
not direct copies of the per-case raw output, JES records or compiler
listings. Accordingly this checkpoint is operator-attested evidence, not
an independent JES forensic audit.

## Remaining gate and release boundary

1. **The eleven-case `mr10-probes` coordinator suite cannot be called PASS.**
   The historical legacy fixed-stack source conflicts with the promoted
   canonical COBOOT-based MR10 bridge. Its accepted golden and status
   must not be silently rewritten, omitted, renumbered or marked SKIP.
   A future explicit owner decision must define its qualified treatment
   in project-wide regression and clean-room acceptance.
2. BCPLQSAM device tests **175 and 176** have not run in this campaign;
   their actual PASS/BLOCKED outcomes cannot be claimed. Device access,
   including any PUN1 recovery, remains a distinct authorization.
3. Clean-room source reconstruction, installed-object provenance,
   reproducible IFOX/IEWL linkage after rebuild and release rollback
   are **not** established by this non-destructive regression campaign.
   The clean-room guide currently refers to **six** accepted MR10 probes
   and older native coverage; review these stale acceptance descriptions
   before asking for destructive reconstruction authority.
4. No permanent `BOOT_OBJ` or `EXT_OBJ` promotion, public
   G!289–305 coroutine allocation, general ABI freeze or release
   publication has been authorized here.
5. Separate owner review and formal CO.5 acceptance remain required.
   CO.0–CO.4 retain their accepted qualified closures.

**Disposition:** Preserve all observed PASS, FAIL, SKIP and NOT_RUN
distinctions. Proceed with non-destructive clean-room/release-readiness
inventory and discuss the qualified legacy regression handling before
changing project-wide contracts or attempting any destructive rebuild.
