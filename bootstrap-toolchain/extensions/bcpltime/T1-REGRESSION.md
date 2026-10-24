# T.1 — BCPLTIME optional-extension native regressions

**Status:** Source-mode MVS cases 159–162 reported PASS (4/4) on 24 October 2026; installed-mode and installation pending.
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

## Installed-mode gate — explicit owner authorization still required

The identical four tests also have a read-only installed-mode JCL
path using manifest-managed EXT_OBJ and EXT_MAC members. That mode
cannot pass until BCPLTIME's PDS installation and production BCXCAT
catalog entry have been designed, approved and verified separately.
Do not install the source-only t1-catalog.asm as EXT_MAC(BCXCAT).

After approved installation and read-back, export local
manifest-resolved settings and run 159–162:

    BCPL_T1_EXTENSION_MODE=installed
    BCPL_T1_EXTENSION_DSN=HERC02.BCPL.EXT.OBJ
    BCPL_T1_MACRO_DSN=HERC02.BCPL.EXT.MAC

Environment variables select read-only linkage; their presence
does not grant permission to install. The production 00–162 panel,
the expected case 083 skip and installation evidence are needed for
T.1 acceptance. All existing 00–158 sources and tests are unchanged.

**T.1 source-mode operator evidence:** 15 offline tests PASS and all four
native regressions 159–162 PASS, 0 FAIL, 0 SKIP. Individual JES payload
job numbers were not in the supplied console excerpt and should be
recorded from saved workarea reports for the acceptance receipt.

**Pending:** owner-authorized resident installation, binary object
readback, installed-mode matrix, full 00–162 production regression and
owner acceptance. See [the approved packaging design](../../../packaging/bcpltime-t1-installation-design.md).
No milestone/march closure is implied.
