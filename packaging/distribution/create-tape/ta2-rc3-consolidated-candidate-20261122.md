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
