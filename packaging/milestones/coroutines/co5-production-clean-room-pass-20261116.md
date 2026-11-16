# CO.5 — Git-driven production coroutine clean-room reconstruction PASS

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.5 — Integration, Regression, and Release
**Operator-local date:** 15 November 2026 (EST)
**UTC log timestamp:** 16 November 2026, 00:51:14Z
**Status:** CLEAN-ROOM RECONSTRUCTION PASS (owner-reported); CO.5 IN PROGRESS
**Source revision:** `788616e6d34325cbe6a9473edcc6be340da3e577` (expected by the revision-guarded operator stanza)
**Evidence class:** OWNER-REPORTED MVS EXECUTION, console summary excerpt;
the complete operator-local log and JES SYSOUT have not been independently inspected.

## Run identity and retained evidence

The operator executed the approved, exact-revision-gated destructive
`tools/reconstruction/rebuild-from-source --unattended --batch-populate`
workflow. Output was redirected to the persistent operator-local log:

`mvs-state/reconstruction-evidence/co5-rebuild-20261116T005114Z.log`

The operator supplied these exact terminal result records:

```text
CO.5 reconstruction RC=0
Evidence: mvs-state/reconstruction-evidence/co5-rebuild-20261116T005114Z.log
BOOT_OBJ INVENTORY PASS: 10 exact production members
INSTALLED COROUTINES PASS: compiler JOB 6489, native JOB 6490; IFOX/IEWL/GO all RC=0000
REBUILD COMMANDS COMPLETED. Save build evidence separately.
TOTAL REBUILD EXECUTION TIME: 2m 47s (RC=0)
```

The snippet establishes the build driver exited zero, the new strict
`BOOT_OBJ` verifier saw the exact ten-member production inventory,
and `tools/coroutines/verify-installed-production.py --run` accepted
the installed-object native coroutine oracle. That verifier compiles
the CO.3 delete/reuse application against the rebuilt Cambridge
compiler, then runs native IFOX/IEWL/GO against installed object
members. It verifies the ordered 21-record CO3BCPL output contract;
the 21 records themselves were not printed in the supplied excerpt.

The reconstruction driver executes Guide Steps 0, 1, 2, 3, 5, 6,
7, 8 and 9, including source population, native runtime assembly,
production `BLDCORCO` and `BLDCORLB` installation, the ten-object
inventory check, installed-object GO and extension installation.
Its overall RC=0 supports a completed automated end-to-end run.
The individual installation JOB identities and detailed IEBCOMPR,
assembler severity and IEWL map remain in the retained local log/JES
artifacts; they were not separately furnished for this review.

## Verified scope and qualifications

**Newly satisfied CO.5 gate:** the permanently promoted native
coroutine objects survive a destructive clean-room reconstruction
from Git-backed sources, and the rebuilt installed objects run the
accepted coroutine application under MVS. This replaces the earlier
8-object baseline clean-room proof, which predated manifest promotion.

**Not yet satisfied:** fresh post-rebuild full MR10/native/system
regressions, separately reviewed release/rollback readiness and the
owner's formal CO.5 acceptance decision. The earlier
[post-installation regression results](co5-post-installation-regressions-20261115.md)
(201 regular PASS, one expected SKIP 083; 10 accepted MR10 probe
PASS and one known genuine legacy fixed-stack FAIL) were collected
*before* this destructive reconstruction and cannot be relabeled as
post-rebuild verification.

The bounded Approach A/S1 qualification, up to two live workers,
fixed 1024-word safe worker stacks, descriptor preconditions, excluded
unbounded/exception recovery and the qualified original MR10 fixed-stack
FAIL remain unchanged. No general coroutine ABI or public release
publication is claimed.

**Disposition:** Preserve this owner-reported MVS PASS as the
clean-room gate. Continue with MVS-facing post-rebuild regressions,
review their per-suite results, prepare a qualified CO.5 closure
candidate and request a separate owner decision.
