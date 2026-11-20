# TA.2 — CAMB_SOURCE empty PDS, frozen input sizing and next MVS gate

**Project:** BCPL for MVS 3.8 Reconstruction
**March:** TA.2 — Manifest-Driven Tape Producer
**Date:** 20 November 2026
**Status:** Read-only MVS source directory evidence accepted as **empty**;
no source-member population or BT0021 staging has occurred.

## Actual MVS observation

The owner reported `tools/datasets/dspal stat CAMB_SOURCE` RC=0
and later `tools/datasets/dspal ls CAMB_SOURCE` RC=0:

```text
HERC02.BCPL.CAMBRIDG.SOURCE:
    (empty)
```

Original owner-side evidence: `workarea/ta2-rc2-cambsource-20261120T202805Z-855/mvs-members.txt`.
The command result shown in the conversation is the observed MVS
directory; the saved file bytes have not been independently retrieved.
A successful `stat` does not by itself establish the PDS DCB; the
existing `dspal populate` checks MVS target attributes before writing.

**Conclusion:** The development/source PDS is allocated but has no
release members. The target release staging PDS
`HERC02.BCPL.TA2STG.BT0021` is a separate data set and has not been
allocated or verified. Do **not** stage an empty source PDS to tape.

## Frozen historical source measurements

Read-only GitHub inspection of all 15 selected historical source files
at the frozen rc2 source revision
`78baec9a8546e4ab09caee779aa2b675379272f3`
found **15/15** ASCII LF files with terminal LF and no lines above 80
columns. Exact selected member order and observed record counts:

| Member | FB80 source records |
| --- | ---: |
| BCPL | 490 |
| BLIB | 474 |
| CG | 2255 |
| CGHDR | 219 |
| EDITMAIN | 113 |
| IOS | 97 |
| LIBHDR | 50 |
| PM | 231 |
| SYN | 1099 |
| SYNHDR | 81 |
| TRN | 1162 |
| TRNHDR | 100 |
| MAKEOBJ | 113 |
| MAKELIB | 72 |
| PROGRAM | 21 |
| **TOTAL** | **6577** |

The existing `tools/datasets/dspal populate CAMB_SOURCE --batch`
uses canonical `config/dspal.yaml` mappings, CP037-compatible FB80
source preflight, MVS target DCB checks, IEBGENER, and verified JES
return codes. Its 4,000-card batching policy, accounting for seven
control/delimiter cards per member, yields two prospective MVS jobs:

1. Eight members (`BCPL` through `PM`), 3,985 counted cards.
2. Seven members (`SYN` through `PROGRAM`), 2,697 counted cards.

The historic `MAKEOBJ` and `MAKELIB` source records include
JCL-looking text such as `//*`; they are **archival payload**, not
job-control commands for installation. `dspal` uses
`SYSUT1 DD DATA,DLM=...` and IEBGENER to transfer them.
Actual MVS result and subsequent record readback determine acceptance.

## Implemented read-only preflight

`rc2-cambsource-readiness.py` verifies the corrected rc2 manifest,
BC0002 registry, exact historical selection and the 15 frozen Git
sources; rejects source drift, UTF/FB80 incompatibility, unknown or
partial MVS member directories and divergent population batching
policy. It accepts only existing MVS directory evidence inside
`workarea/`. The currently observed empty listing is a
**pending-population** outcome (exit status 3), not a stage PASS.

The matching 10 synthetic offline tests and Python compilation
passed in the assistant's repository workspace. No live MVS command
was performed by the assistant. This preflight does not compete with
the existing `dspal` population implementation.

## Decision and operation boundary

**Next bounded state change, not yet authorized:** populate exactly
15 historical `CAMB_SOURCE` members with the existing
`dspal populate CAMB_SOURCE --batch`. Run only after separate owner
approval, and guard against a nonempty PDS before beginning. Preserve
original MVS JOB/STEP/RC evidence; if any batch fails or ends
ambiguously, do not automatically rerun/rewrite members. Check the
directory for precisely 15 members and compare records to frozen
source before staging `BT0021`.

Do not modify any `BT0001`–`BT0020` accepted staging inputs, add
the GitHub-only demoted compiler, initialize an AWS tape, or claim
a final source redistribution-rights decision. **TA.2 IN PROGRESS.**
