# TA.2 — CAMB_SOURCE population accepted; historical record readback

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 20 November 2026  
**State:** Historical Cambridge PDS population **accepted at member-directory level**; member record fidelity pending.

## Actual MVS result, owner-reported

The approved, non-retryable `rc2-populate-cambsource-once.py --execute`
finished with its own receipt verification, reporting:

- IEBGENER batches **JOB 9325** and **JOB 9326**; 15 member writes.
- A read-only MVS directory inquiry found **15/15 exact historical names**.
- Original private receipts at
  `workarea/ta2-rc2-cambsource-population-once/`.

The submitted original MVS/JES report bytes were not separately supplied
to the assistant. The runner's reported success is supported by its
preexisting two-job RC verification and exact post-write LISTDS MEMBERS
check. **Do not rerun population.** The source PDS is
`HERC02.BCPL.CAMBRIDG.SOURCE`. The independent release-stage input
`HERC02.BCPL.TA2STG.BT0021` is **not** yet staged or accepted.

This result leaves the original 20 `BT0001`–`BT0020` sources and their
MVS acceptance undisturbed; `BCPL-0.1.0-rc2` / `BC0002` remains the
21-dataset source-inclusive candidate. The demoted compiler and its
GitHub-only development/test context remain excluded.

## Next read-only verification

`rc2-cambsource-record-readback.py --read-only` reuses the established
`dspal get CAMB_SOURCE member file` path (IEBGENER and MVS SYSOUT)
for exactly the 15 historical source members. Before its first MVS read,
it checks the frozen candidate/registry selection, source files at Git
commit `78baec9a8546e4ab09caee779aa2b675379272f3`, and the saved
JOB 9325/9326 and 15-member MVS directory receipts. It performs **no**
PDS write, re-population, staging, assembly, link-edit or tape operation.

The read-only MVS GET operation writes its returned member text, each
MVS JOB identity, stderr and SHA-256 evidence under a new exclusive
`workarea/ta2-rc2-cambsource-record-readback/` directory. No console
member dumps are produced. The verifier compares full record strings
and record counts against the frozen Git source after removing trailing
ASCII spaces, mirroring the established `dspal get` interpretation of
FB80 padding. It rejects mismatched/ambiguous MVS GET receipts and stops
on the first content mismatch, preserving all prior evidence.

**Interpretation:** Passing verifies logical text/record fidelity on the
readback path. It does *not* prove original fixed-80-byte CP037 data
bytes, PDS block layout or exact historical tape-image byte identity,
because `dspal get` strips trailing blanks and transports records via
SYSOUT. A separate raw-byte check would need a more direct facility if
required by the remaining TA.2 release gate; avoid turning that into
an independent IBM-utility certification project.

## Assistant-workspace checks

The new readback script and its 10 focused synthetic tests were exercised
in an independent assistant workspace (not the owner's host). The tests
cover complete 15-member MVS simulation, UTF/ASCII record restrictions,
strict JOB parsing, mismatches, aborted GET, duplicate run protection,
retained MVS population mismatch and symlink rejection. **28/28**
compact rc2 tests (including earlier readiness/population checks)
**PASS**, and the new Python sources compile. No live MVS readback has
yet been performed or inferred.

After actual MVS data is returned and inspected, TA.2 can decide whether
BT0021 may be staged by a **separately owner-authorized** selective
IEBCOPY operation. No staging or BC0002 tape-writing authorization is
implied by the current results.
