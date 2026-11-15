# CO.5 — Clean-room reconstruction MVS PASS, 15 November 2026

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.5 — Integration, Regression, and Release
**Status:** Baseline reconstruction PASS; CO.5 IN PROGRESS
**Tested GitHub `main`:** `2d0cfb90a1cda0cfeb73c45cb00a8fe1f90b3c18`
**Evidence:** Operator-supplied 2,041-line terminal transcript; not an independent raw JES spool audit

## Command, scope and result

After fast-forwarding `main` from `6f039e7b` to `2d0cfb90`, the owner ran:

```sh
tools/reconstruction/rebuild-from-source --unattended --batch-populate
```

All driver Guide Steps **0, 1, 2, 3, 5, 6, 7, 8, 9** returned RC=0.
`TOTAL REBUILD EXECUTION TIME: 2m 11s (RC=0)`.

The explicitly destructive run deleted **81** top-level `workarea/`
items, retaining `.gitignore`, and deleted/recreated **29** managed
MVS datasets. Purge jobs: **5902/5903**; allocation: **5904/5905**.
Git source population wrote **171** members in 25 batch jobs
**5911–5935**. The first-population RC=2 was the documented
**exactly 12 missing generated members** condition, not an error.
Generated population wrote the final **12** members through jobs
**5944–5946**, RC=0. `prepare-bootstrap` produced its source/output
SHA-256 inventory in `workarea/bootstrap-cambridge/prepare-bootstrap-manifest.json`.

## Build and installation verification

| JES payload job | Phase | Operator-reported verification |
| ---: | --- | --- |
| 5938 | ICINT19 | IFOX ASM, IEWL, SAVEOBJ RC=0000; severity 0 |
| 5941 | Installed interpreter smoke | Interpreted CODE=0; runner RC=0 |
| 5942 | MR10 translator bootstrap | Seven INTCODE files and TRNILRG generated |
| 5950 | CAMBBLD | 22 interpreted phases, PACKCOMP all RC=0000 |
| 5952 | Cambridge compiler smoke | Nonempty System/370 assembly generated, RC=0 |
| 5957 | BLDBMAIN | Seven IFOX modules and seven installs RC=0000; severity 0 |
| 5960 | BLIBBLD | ICINT19, IFOX, IEWL, BLIB install RC=0000; severity 0 |
| 5965 | BCPLDEMO | IFOX, install, readback, IEBCOMPR RC=0000 |
| 5967 | BCPLTIME | IFOX, install, readback, IEBCOMPR RC=0000 |
| 5969 | BCPLQSAM | IFOX, install, readback, IEBCOMPR RC=0000 |

Final `BOOT_OBJ` contained **BCPLMAIN, BCPLMEM, BCPLBYTE,
BCPLAPT, BCPLIO, BCPLRGS, BCPLREG, BLIB**.
`BOOT_DEVOBJ` was **empty**. `EXT_OBJ` contained **BCPLDEMO,
BCPLTIME, BCPLQSAM**.

## Qualifications and next acceptance gates

This proves baseline interpreter-hosted bootstrap and installed
core/extension reconstruction; it does **not** install the private
native coroutine candidate into production `BOOT_OBJ`. The driver
explicitly does **not** run regression suites. The previously
reported **209 PASS, one accepted MR10 legacy FAIL, SKIP 083 and
two unrun device cases** were pre-rebuild results and have not been
reconfirmed on the reconstructed MVS state. The cleanup removed the
local `workarea/` receipts from those earlier campaigns; Git
documentation of the operator-reported results remains.

The transcript also printed `?? FETCH_HEAD` at both Git status
checks. This appears to be an untracked root-level file; its origin
and effect have not been investigated. Do not silently delete it.

Pending CO.5 gates include post-rebuild native coroutine IFOX/IEWL/GO,
applicable MR10/native regression execution, qualified handling of
the known CO.0 legacy fixed-stack fixture, separately authorized
BCPLQSAM device cases 175–176, release/rollback documentation,
private-to-public ABI decisions and formal owner acceptance.
**CO.5 remains IN PROGRESS.**
