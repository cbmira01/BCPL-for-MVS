# TA.2 — BCPL-0.1.0-rc3 consolidated tape candidate

**Milestone:** Tape artifact release. **March:** TA.2 — Manifest-Driven Tape Producer (IN PROGRESS).
**Date:** 22 November 2026. **MVS execution:** NOT YET PERFORMED.

## Candidate identity

- Candidate `BCPL-0.1.0-rc3`, standard-label AWS volume `BC0003`.
- New image `mvs-state/tape/bcpl-0.1.0-rc3-BC0003.aws`.
- Manifest SHA-256 `b130e4a246cecb6d810f45febd945e3ed0e854164e83012899c86c730f365486`, independently reserved in the existing candidate registry.
- Source revision `e910de51c19c09698be139e33084a90401511cc9`, containing 12 updated MR10 BCPL regression sources with 23 literal `EXP:` records; actual development MVS regression PASS 12/12.
- The 21-dataset logical manifest, 146 PDS members, original DCBs and Cambridge historical source inclusion remain unchanged. Native Cambridge Compiler is *absent* in this qualified candidate.
- The original `BC0002`, RC2 source/stage/readback/installed datasets and accepted JOBS 9343–9346/evidence remain immutable.

## One guarded MVS operation

`packaging/distribution/create-tape/scripts/ta2-rc3-consolidated --run` requires clean `main`, source SHA consistency with the already tested source revision, accepted BC0002 media/readback evidence, one read-only MVS LISTDS inquiry, 21 matching source DCBs, 42 absent new target datasets, and safe distinct `BC0003` media.

One explicit operator `Y` creates a durable exclusive no-retry marker, then performs the following in one procedure:

1. `TA2R3STG`: 21 new staged datasets `HERC02.BCPL.TA2R3S.BTnnnn`, copying 20 old PDS datasets, regenerating the first bootstrap PS, replacing four RC3 installer members and the 12 regression BCPL source members. 37 MVS utility steps expected, all RC0000.
2. `TA2R3WR`: initialize and mount one new `BC0003` AWS; 21 tape write steps; independently inspect standard labels and 64 physical tape files; seal AWS SHA-256.
3. `TA2R3RES`: remount the same tape and restore 21 logical datasets *directly* into the isolated `HERC02.BCPL.TA2R3I.*` recipient namespace. This consolidates restoration and installation, avoiding a second all-dataset copy.
4. Read-only recipient LISTDS (`DSPALST`): independently check all 21 newly restored datasets on `TSO002`, including DSORG, RECFM, LRECL, and BLKSIZE. Capture its JES report and refuse wrong/missing recipient DCBs before executable use.
5. `TA2R3MR`: retarget canonical 63-step `MRREGRES` to installed MR10. Require **all 63 ordered steps** at RC=0000 in both JES summary and actual MVS IEF142I records; independently require all 12 interpreted execution steps, the printed `TEST:` and `EXP:` and computed `RP:` against the tracked golden records, and `CODE=0`. Store a sealed per-case semantic report referencing the **actual RC3 JOB number**, not RC2's JOB 9346.

The regenerated installer includes the nineteenth Cambridge historical-source PDS IEBCOPY template and RC3-specific volume/version references. New state lives inside repository `workarea/` and `mvs-state/`, tracked code/docs inside `packaging/`. Never automatically retry or overwrite the original release; no `set -e` or fast-fail shell option is used.

## Local evidence and acceptance boundaries

The initial RC3 source-controlled module passed **8/8 offline synthetic and negative tests**. Three further repository tests now cover recipient DCB/volume verification, all 63 regression JES/IEF142I steps (including missing, duplicate, reordered or nonzero evidence), and the actual RC3 semantic-review JOB identity. The new 63-step and job-identity validators were independently exercised in an isolated Python execution with one valid and multiple invalid synthetic reports; the full revised 11-test module has **not** been executed against a complete local repository checkout in this environment. The real MVS result remains the acceptance authority. No AWS image or MVS success is claimed by this commit.

TA.2 remains IN PROGRESS. TA.3/TA.7 fresh-recipient requirements, TA.4 human per-case sign-off, third-party source rights qualifications, and publication approval remain separate acceptance gates.


## 22 November RC3 pre-stateful JCL-column refusal and correction

The owner ran `python3 -B .../ta2-rc3-consolidated --run` on current
GitHub `main` and received `RC3 REFUSED: JCL operands over column 71`.
The attempt did **not** consume the permanent one-shot marker, initialize
or mount `BC0003`, submit any JES job, or modify MVS datasets: the
validation runs in `stage_body()` before `execute()` creates its
stateful-attempt marker and before live preflight.

Root cause was identified in the exact 12 canonical Git BCPL sources:
each starts with 73-column `// ===...` comment separators. During
`DD DATA,DLM=Z9` inline staging these lines are ordinary 80-column
source data, but the former `cards()` validator indiscriminately applied
the JCL column-71 operand rule to all lines beginning `//`.

The corrected renderer tracks the `DD DATA,DLM=Z9` region through its
exact `Z9` delimiter, retaining the 80-column source-record bound while
applying column-71 checks only to actual JCL control statements.
An orphan/missing in-stream delimiter is rejected. Two tracked regression
tests cover 73- and 80-column source data, genuine overlong JCL,
overwidth data and malformed delimiters. The exact validator algorithm
passed **9/9 isolated executable positive/negative checks** in an
assistant workspace under the repository workarea, including 17
consecutive data sections. The complete revised 13-test module and
real MVS tape/install/regression workflow were **not** executed in the
assistant's workspace.

The user may now rerun the original `--run` entry point once after
pulling this correction. Existing `BC0002` remains immutable.
RC3 production, installed execution, EXP/RP/CODE acceptance, TA.4 human
signoff, and publication remain pending **actual MVS evidence**.
**TA.2 remains IN PROGRESS.**


## 22 November RC3 pre-stateful staging-count refusal and correction

After pulling the DD DATA column-width repair, the owner reran the RC3
entry point, which refused `RC3 REFUSED: stage JCL count/safety contract
altered`. This is another **pre-stateful** refusal: the runner reaches
`stage_body()` before creating its one-shot marker, invoking MVS
preflight or submitting JES.

The stage generator writes the recipient's BT0002(RESTORE) installer
template as in-stream `DD DATA,DLM=Z9` input. That inert distributed
member contains **19 genuine-looking IEBCOPY EXEC statements** and
**19 DISP=(NEW,CATLG,DELETE) allocations**. The old safety gate
scanned the *entire rendered text*, counting these as active JCL:
56 instead of 37 EXEC cards and 40 instead of 21 allocations.
The earlier lightweight stage fixture used an inert `RESTORE` string
and therefore did not cover this important case.

The repaired safety gate uses the same delimiter-aware JCL/card scanner
to exclude in-stream data, checks the **exact ordered 37-step**
IEBGENER/IEBCOPY sequence (21 S, 4 B, 12 E), **21 active NEW
allocations**, and **17 active DD DATA sections**. It retains the
FB80 limit for all records, strict JCL operand column-71 checks,
forbidden legacy namespace checks and missing/orphan delimiter
refusals. New tracked regression cases include a realistic 19-step
embedded RESTORE and active-step-order drift; an existing test now
validates actual JCL rather than mistaking embedded BCPL data for
control statements.

An executable assistant-workspace harness using the corrected
`stage_body` contract passed **9/9** positive and negative checks,
including the 19 embedded IEBCOPY statements, 73/80-column
in-stream BCPL data, exact active step order and malformed/overwidth
rejection. This is **not** a full checked-out repository test run.
The tracked test module now has **15** tests, but no full module or
MVS execution was performed in the assistant's isolated environment.
The owner may safely retry the original guarded RC3 operation after
updating to the new GitHub `main` commit. `BC0002` remains untouched.
**TA.2 remains IN PROGRESS** pending real MVS evidence.


## 22 November — MVS BC0003 write PASS (qualified), automatic demount, and approved TA.2 continuation

The owner executed the corrected consolidated RC3 runner on actual MVS
3.8J at GitHub `main` `fd2f7737`. **JOB 9359** passed its
read-only MVS preflight (21 existing original source DCBs, 42 new
staging/recipient datasets absent, `BC0003` unused, empty tape unit).
**JOB 9360** completed all new staging and 16 member updates.
**JOB 9361** completed the 21-position standard-labeled AWS write at
RC=0000; independent HETMAP verification reported **21 labels** and
**64 physical tape files**. The owner supplied immutable AWS SHA-256:

`6c54c4df2b75020a698110061c4f8003b09adbe21f738848dcaed3da495d81e1`

The original stateful runner then halted at `BC0003 disappeared after
write`. The owner's independently reviewed, sealed evidence in
`workarea/ta2-rc3-consolidated/20261122T202323Z-30995`
demonstrates that Hercules unit `0480` was mounted immediately
before JOB 9361, then became EMPTY after it. MVS unit `480` was
`O` while mounted and `O-NRD` after the job. This is a normal
final-step **tape-volume demount**, consistent with the write JCL
omitting `RETAIN` on its final dataset; it is not an unsuccessful
write. The owner's `sha256sum -c SHA256SUMS` reported all files
**OK**, and the current AWS image still matched the exact original
SHA-256. Original receipt `failure.json` documents the misleading
halt, and the original production one-shot marker remains consumed.

**Do not rerun `ta2-rc3-consolidated --run` or reinitialize,
restage, rewrite, delete, or replace `BC0003`.** No RC3 restore,
recipient inventory or installed MR10 execution had yet been attempted.

The owner explicitly approved a **separate one-shot TA.2 readback,
installation, and regression continuation**. The source-controlled
`scripts/ta2-rc3-restore-continuation` reuses the exact original
RC3 manifest, MVS reader and installed MRREGRES generator. It
requires immutable original JES/HETMAP evidence, original marker,
original image SHA, the exact JOB 9360/9361 ordered RC0000 and
IEF142I results, fresh HETMAP validation, empty/ready 0480, and
a new MVS read-only preflight proving 21 new recipient targets absent.
Only after one explicit `Y` does it exclusively mark the distinct
restore attempt, mount the **existing** `BC0003` image, submit one
21-step `TA2R3RES`, verify 21 recipient DCBs on `TSO002`, use
independent `LISTDS MEMBERS` to compare **all 146 PDS members**,
execute canonical `TA2R3MR` with 63/63 JES+IEF142I RC0000,
and compare 12/12 interpreted `TEST:`, `EXP:`, `RP:` and
`CODE=0` against the actual MVS report. It accepts either
mounted or automatically demounted tape after use, but requires
unchanged AWS SHA and records all JES/HETMAP evidence in a separately
sealed recipient workarea. Any stateful halt is **NO RETRY**.
It never executes `hetinit`, source staging, a tape-write job,
or a destructive cleanup.

The exact continuation source was syntax-checked and its assistant-workspace
isolated safety/negative/mock-MVS test module passed **10/10**.
No complete GitHub checkout/MVS 3.8J was available in that assistant
workspace, and **no actual RC3 restore or installed regression has
yet been observed**. Human TA.4 per-case sign-off, TA.3/TA.7
fresh-recipient requirements, redistribution-rights review, and
release publication remain separately governed.

**TA.2 remains IN PROGRESS** until actual continuation results are
reviewed.


## 22 November — RC3 MVS 21-step restore PASS; BOOT DCB diagnosis pending

The owner pulled the committed one-shot readback continuation,
passed read-only recipient-absence preflight **JOB 9362**, and
explicitly approved the mount and new installation attempt.
**TA2R3RES JOB 9363** restored all 21 ordered tape datasets
to the isolated `HERC02.BCPL.TA2R3I.*` recipient namespace
with IEBGENER/IEBCOPY **RC=0000** throughout. This establishes
**readback/restore JES PASS (qualified)**, not yet a 21-dataset
DCB/directory or installed compiler acceptance.

The continuation halted at
`RC3 RESTORE REFUSED: recipient DCB/volume differs:
HERC02.BCPL.TA2R3I.BOOT` during post-restore MVS
`LISTDS LABEL` verification. Its immutable private receipt is
`workarea/ta2-rc3-restore-continuation/20261122T232532Z-31994`.
The second, distinct one-shot restore marker is **consumed**.
Do **not** repeat the original production, mount-and-restore or
21-step JOB 9363, do not delete or replace restored recipient
datasets, and preserve BC0003 plus both sealed incidents.

The failure text does **not** identify whether the actual discrepancy
concerns VOLUME, DSORG, RECFM, LRECL or BLKSIZE, nor whether
classic TSO LISTDS parsing is at fault; **no DCB cause is asserted**.
A separately committed read-only
`scripts/ta2-rc3-recipient-diagnostic --live` first validates the
sealed original receipt, JOB 9363's 21 step summary/IEF142I records,
original one-shot marker and unchanged AWS SHA, then issues two
fresh actual-MVS TSO queries. It captures all 21 DCB comparisons,
exact BOOT parsed and raw values, and 20 PDS directories against
146 manifest members. Only diagnosis, not acceptance or installed
MR10 execution, is authorized by this operation.
Ten local isolated tests PASS; the real MVS output remains the
acceptance authority. **TA.2 IN PROGRESS**.


## 22 November — JOBS 9365/9366 isolate BOOT-prefix parser error; installed MR10 continuation

The owner executed the independently source-controlled read-only
`ta2-rc3-recipient-diagnostic --live` following successful JOB **9363**
(21/21 IEBGENER/IEBCOPY restore RC0000). The actual MVS results:

- **JOB 9365**: `LISTDS LABEL` for all 21 existing recipient datasets.
  Existing `core.extract_listds_block()` reported one apparent difference:
  `HERC02.BCPL.TA2R3I.BOOT` expected `PS/FB/80/800`, but parsed `PO`.
- The saved *raw block* for that BOOT query begins
  `HERC02.BCPL.TA2R3I.BOOT.JCL` and reports
  `PO/FB/80/800` on `TSO002`. That is a **different dataset**.
  The generic parser's unbounded substring match and last-occurrence
  selection used `BOOT.JCL` rather than the exact `BOOT` label.
  This demonstrates a **false-positive DCB mismatch in the verifier**;
  it is not yet an independent affirmation of BOOT's actual PS DCB.
- **JOB 9366**: `LISTDS MEMBERS` for 20 restored PDSes, **20/20
  directories match** the expected member identities; collectively
  **146 selected members** verified on actual MVS, qualified by the
  read-only directory inquiry.
- Both the saved prior `LISTDS` and fresh JOB 9365 inquiry were
  misparsed identically. Original diagnostic evidence:
  `workarea/ta2-rc3-recipient-diagnostic/20261122T234725Z-32362`.
  The AWS image, 21 restored DASD datasets, source stage and original
  write/restore receipts remain untouched.

The new **TA.2 installed MR10 continuation**
`scripts/ta2-rc3-installed-mr10-continuation` targets this exact
accepted state. It first replays all original sealed MVS evidence
(9360/9361, 9363, 9365/9366), both consumed operation markers,
unchanged `BC0003` SHA-256, exact 21-member recipient selection
and the 146-member result. It reinterprets saved JOB 9365 using an
**exact standalone DSN-label** parser that refuses prefix-only,
missing, conflicting or ambiguous LISTDS responses. It then executes
one fresh **read-only** MVS `LISTDS LABEL` for all 21 recipients and
one `LISTDS MEMBERS` for all 20 PDSes. It requires the entire
canonical DCB/volume contract and **146/146** directory identities
before offering one **[y/N]** approval for a single installed
`TA2R3MR` regression. It then requires all 63 JES+IEF142I steps
RC0000 and all 12 `TEST:`/`EXP:`/`RP:`/`CODE=0` semantic checks.
An exclusive no-retry marker protects that **new regression attempt**.

This continuation **does not mount, unmount, initialize, readback,
restore, restage, or rewrite any tape or dataset**. It does not
modify the generic `dspal-core.py` parser during this bounded
MVS acceptance stage; wider parser regression remediation can be
addressed separately after verified MVS results. The exact code
and test blobs committed to GitHub match the executable assistant
workspace artifacts byte-for-byte. **18/18 focused Python tests
PASS**, including success, the observed BOOT/BOOT.JCL collision,
contradictory entry refusal, original-receipt tampering,
full one-shot mocked execution and genuine DCB-failure refusal.
The complete repository test panel was not run in the isolated
workspace; no new actual installed `TA2R3MR` result is claimed.

**TA.2 remains IN PROGRESS.** Human TA.4 case sign-off, fresh
recipient TA.3/TA.7, rights review and publication remain separate.
