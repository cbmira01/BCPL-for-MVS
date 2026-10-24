# T.1 — BCPLTIME optional-extension native regressions

**Status:** **T.1 CLOSED — 24 October 2026**, explicit owner approval; source-mode and installed-mode MVS cases 159–162 each PASS (4/4), full 00–162 production panel 162 PASS, 0 FAIL, 1 expected SKIP 083.
**Milestone:** BCPLTIME; **march:** T.1 — Packaging and Acceptance.
**Prior evidence:** T.0 JOB 5436 native PASS. Existing R.5 cases 146–158
continue to cover no extensions and BCPLDEMO alone.

## New numbered cases

| Case | Selection | BCPLREG bytes | Link requirement |
| --- | --- | ---: | --- |
| 159 | BCPLTIME required | 44 | TIMDESC/TIMDISP; DMODESC/DMODISP absent |
| 160 | BCPLDEMO then BCPLTIME required | 60 | Both extensions present once |
| 161 | BCPLTIME then BCPLDEMO required | 60 | Reverse order, both present once |
| 162 | BCPLTIME selected then required twice, BCPLDEMO required | 60 | Deduplication and upgrade |

Each case has a separately compiled native BCPL caller, output marker and
MVS IFOX selection fixture. Case 159 repeats QUERY, STCK, TIME, short
capacity and no-partial-write checks. Cases 160–162 interleave
DEMOSVC and TIMESVC calls, including calls immediately surrounding
MVS TIME DEC, to catch register corruption and interoperability faults.

PASS requires IFOX/IEWL/GO successful condition codes, an exact BCPL
marker and a real IEWL MAP with the expected BCPLREG length, selected
control sections and unique zero entry address. The report checker
does not independently prove physical JES DD attribution.

## Source-mode operation — no permanent writes

From repository root, after pulling GitHub main:

    python3 -m unittest discover -s tools/checks -p 'test_*t1_time*.py' -v
    python3 tools/checks/prepare-t1-time-regression.py --check
    tools/bootstrap/run-regression --check-numbering
    tools/bootstrap/run-regression 159 162 --show-output

The existing numbered runner compiles each caller with the MVS-hosted
demoted Cambridge compiler, assembles BCPLTIME and optionally BCPLDEMO
into temporary MVS object decks, and uses the accepted BCXPRE/BCXPOST
macros plus source-only t1-catalog.asm to produce a native BCPLREG and
IEWL INCLUDE cards. All PDS inputs are read-only; authenticated JCL
and full JES output remain in ignored workarea/.

## Installed-mode operation — accepted on MVS 3.8J

The identical four tests have a read-only installed-mode JCL path
using the manifest-managed `EXT_OBJ` and `EXT_MAC` libraries. It
passed under the owner-approved installation in JOB 5455 and resident
catalog publication in JOB 5457. Do not install the source-only
`t1-catalog.asm` as `EXT_MAC(BCXCAT)`.

Use these existing, manifest-resolved settings for **read-only**
installed-mode linkage of 159–162:

    BCPL_T1_EXTENSION_MODE=installed
    BCPL_T1_EXTENSION_DSN=HERC02.BCPL.EXT.OBJ
    BCPL_T1_MACRO_DSN=HERC02.BCPL.EXT.MAC

Environment variables select read-only linkage; their presence never
authorizes a future resident PDS installation. All existing 00–158
sources and test numbers remain unchanged.

**Accepted evidence, 24 October 2026:** 15 original T.1 offline tests
PASS (with a further 15 packaging/R.5 compatibility unit tests PASS).
Source-mode **159–162: 4 PASS, 0 FAIL, 0 SKIP**. Installed-mode
**159–162: 4 PASS, 0 FAIL, 0 SKIP**. Full
`tools/bootstrap/run-production-regression 0 162`: **162 PASS,
0 FAIL, 1 expected SKIP (083), TOTAL 163**. The runner checks
expected BCPL output and the actual IEWL MAP/XREF for each extension
test. Individual payload JOB IDs and every raw per-case report were
not independently audited in the supplied final-panel transcript.

See the [T.1 owner closure](../../../packaging/bcpltime-t1-closure-20261024.md)
and [installation/recovery procedure](../../../packaging/bcpltime-t1-installation-design.md).
**Milestone BCPLTIME is CLOSED.**
