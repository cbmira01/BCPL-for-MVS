# TA.3 — BC0003 MVS-only installation JCL (22 November 2026)

**Project:** BCPL for MVS 3.8 Reconstruction
**March:** TA.3 — MVS Bootstrap and Installation — IN PROGRESS
**Candidate:** BCPL-0.1.0-rc3; VOLSER BC0003; immutable AWS SHA-256
`6c54c4df2b75020a698110061c4f8003b09adbe21f738848dcaed3da495d81e1`.

## Recipient bootstrap and profiles

1. **`jcl/TA3BOOT.jcl`** — IEBGENER prints `BCPL.BT0001`
   (`LABEL=(1,SL)`) to JES output before BCPL is installed.
2. **`jcl/TA3BT2.jcl`** — IEBCOPY restores the tape-resident
   `BCPL.BT0002` installer PDS (`LABEL=(2,SL)`) to a NEW
   `<HLQ>.BCPL.DIST.INST`, with four members INSTALL, DATASETS,
   RELEASE, RESTORE.
3. **`jcl/TA3VIEW.jcl`** — read-only IEBGENER printing of those
   four members, including the 19-step on-tape RESTORE template.
4. Submit **one** of the independent source-controlled profile decks:

   | Job body | Tape positions | Installed PDSes |
   | --- | --- | --- |
   | `TA3MR10.jcl` | BT0003–BT0012 | Common docs + nine MR10 |
   | `TA3NATV.jcl` | BT0003, BT0013–BT0021 | Common docs + native components and Cambridge source |
   | `TA3BOTH.jcl` | BT0003–BT0021 | Deduplicated combined set |

All target operations are ordinary MVS IEBCOPY, with standard-label
`BCPL.BTnnnn`, `LABEL=(n,SL)`, `VOL=(PRIVATE,RETAIN,SER=BC0003)`.
All outputs use `DISP=(NEW,CATLG,DELETE)`. Boot file is FB80; the
MR10 load library BT0012 is PO/U/0/6144; other restored PDSes
are PO/FB/80/800. No tape catalog entries or media writes are made.

## Site contract

The MVS operator supplies one valid local JOB card and substitutes
`<HLQ>` (one legal 1–8-character qualifier), `<TAPE>` (MVS tape
unit, e.g. 480 on TK5), `<DASD>` (DASD allocation unit) and
`<DVOL>` (writable DASD volume serial) **in the job stream**
before submission. The recipient does not run BCPL, Python, Git,
WSL, TSO or `dspal` to execute these jobs. Site parameter substitution
and JOB-card sourcing are still operator integration tasks: the decks
are intentionally not blindly submit-ready.

The selected RC3/TA.2 track budgets are source-backed initial
allocations and **not universal capacity guarantees**. Confirm
site disk capacity and every catalog target absent before submitting.
Never retry after an ambiguous result. Do not attempt two profiles
with the same HLQ: `BCPL.DIST.DOCS` is shared and its NEW allocation
would conflict. A replacement/upgrade requires a new absent HLQ;
in-place overwrite or automatic cleanup is not supported.

**Native-only here means included native runtime, historical Base
Library BLIB, Coroutine Support Library, System Extensions, and
historical/reconstructed Cambridge source.** The candidate explicitly
declares `native_compiler: absent`. It cannot compile BCPL to native
System/370 application objects on an unmodified recipient.

## Remaining acceptance and frozen-media limitation

The printed BT0001, restored BT0002, profile restore, MVS recipient
DCB/directory verification, and installed ICINT19/BCPL execution have
not been performed under TA.3. Actual MVS/Hercules results must drive
the next corrections. New recipient allocations and any mount require
separate explicit stateful authorization. Accepted TA.2 jobs 9361,
9363, 9367, 9368 and 9369 are not to be repeated.

**BC0003 limitation:** its on-tape BT0002(RESTORE) is an inert,
all-payload template requiring site substitution, not three
independently selectable ready-to-submit profile decks. These
source-controlled JCL job bodies permit bounded external-card
recipient proof without changing BC0003. Making the profile decks
self-contained *on the tape* would require a new approved candidate,
not an alteration to the accepted image. The TA.3 acceptance gate
and TA.4/TA.5/TA.7/TA.8 remain open.
