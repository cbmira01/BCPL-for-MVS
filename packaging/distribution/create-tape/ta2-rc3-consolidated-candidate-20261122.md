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
