# CO.5 — Formal qualified acceptance review candidate

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.5 — Integration, Regression, and Release
**Status:** READY FOR OWNER REVIEW, **NOT CLOSED**
**Prepared:** 16 November 2026
**Tested full-regression revision:** `9a621d5aac0d5c6068e10c6425b861f7480cf30a`

## Acceptance evidence

| Required gate | Source-grounded verification | Disposition |
| --- | --- | --- |
| Named native coverage | Cases 177–189 retain names/IDs; original tests 00–176 unrenumbered | MET |
| Native BCPL/IFOX/IEWL/GO | After clean-room, installed-only coroutine compiler JOB 6489, native JOB 6490, IFOX/IEWL/GO all RC0000; accepted ordered 21-record oracle | MET (owner-reported MVS) |
| Git-source clean-room and installation | RC0, 2m47s, 29 managed datasets, exactly 10 `BOOT_OBJ` members, `BCPLCO` and `COROUTIN` installed | MET (owner-reported MVS) |
| Full regular post-rebuild regressions | Six selected suites coordinator RC0 PASS, 201 regular PASS, zero FAIL/BLOCKED, expected SKIP 083 | MET (per-suite counts derived from manifest and final coordinator PASS) |
| MR10 development-probe compatibility | Earlier separately executed 10 PASS; one original interpreted fixed-stack probe genuine FAIL | QUALIFIED — historical exception |
| First post-rebuild Bootstrap failure | Case 117 native IEWL `SB2D` in JOB 6745; isolated case PASS and whole suite later PASS without code change | QUALIFIED — original failure retained, cause open |
| Release and recovery | Deterministic rebuild from Git-backed source verified; independent earlier-image rollback and tape distribution not verified/published | QUALIFIED; no public release authorization |

GitHub `main` owns source, manifests, accepted JCL and evidence.
The current source-defined production build regenerates
`COROUTIN` IFOX after rebuilding Cambridge, installs and
IEBCOMPR-verifies `BCPLCO/COROUTIN`, checks the exact ten-object
inventory and runs the installed-only oracle. A controlled
reconstruction from the approved Git revision is the tested
recovery path; it is **destructive** and requires operator approval.
Restoration of an *older* object-library state requires a separately
identified backup or prior Git revision and newly verified restore.
No automatic backward rollback has been validated.

The qualified Approach A/S1 contract supports root and at most
two registered live workers, independent checked 1024-word S1
stacks, parent-chain transfers, normal lifecycle and root-controlled
deletion of known-live inactive workers. The private descriptor
layout is not an ABI promise. No unlimited workers, arbitrary
stale-address/ABA protection, general GETMAIN failure/abend
recovery, preemption or historical MR10 static-frame parity
is accepted. G!289–300 are owner-approved permanent native
coroutine globals.

Evidence:
- [Clean-room production installation PASS](co5-production-clean-room-pass-20261116.md)
- [Six-suite full regular regressions PASS](co5-post-reconstruction-full-regression-pass-20261116.md)
- [Case 117 original SB2D and isolated PASS](co5-bootstrap-117-post-cleanroom-abend-20261116.md)
- [Legacy MR10 fixed-stack probe FAIL qualification](co5-mr10-fixed-stack-negative-code-20261115.md)
- [Owner-approved production promotion](co5-production-promotion-20261115.md)

## Proposed owner decision — NOT YET APPROVED

> Close **CO.5 — Integration, Regression, and Release
> (qualified)**, accepting the 10-object Git-source clean-room
> reconstruction, installed-object native coroutine oracle and
> 201-PASS regular post-rebuild campaign with SKIP 083. Retain
> the genuine MR10 fixed-stack FAIL, original Bootstrap 117
> SB2D failure, and bounded Approach A/S1 limitations. No
> public distribution release, rollback to an unverified older
> image, new official march or broader coroutine semantics
> are authorized by this closure.

**Owner acceptance: PENDING. CO.5 remains IN PROGRESS.**
