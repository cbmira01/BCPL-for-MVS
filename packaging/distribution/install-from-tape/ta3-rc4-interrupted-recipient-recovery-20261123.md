# TA.3 — RC4 interrupted tape-resident recipient: preserved evidence and guarded continuation

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** **TA.3 — MVS Bootstrap and Installation: IN PROGRESS**  
**Immutable tape:** `BCPL-0.1.0-rc4`, VOLSER `BC0004`, AWS SHA-256
`7cc5a1d61882bf88469fd9f9e38512f1976ef1a775e3095e12e3988600c57af1`

## Actual MVS incident (owner-reported; 23 November 2026 EST)

The first RC4 recipient trial was properly authorized, consumed its
original one-shot marker, and passed **MVS JOB 9398**, which reported
42 absent target PDSes and the unchanged BC0004 tape. After executing
the first on-tape MR10 profile, the runner halted:

```text
TA.3 RC4 RECIPIENT PREFLIGHT PASS: JOB 9398; 42 absent PDSes; BC0004 verified; drive EMPTY.
Install 3 BC0004 tape-resident profiles ONCE? [y/N]: y
TA.3 RC4 RECIPIENT HALTED: MVS job summary IEBCOPY executed-step count differs
Evidence: workarea/ta3-rc4-recipient/20261123T133542Z-36979
NO RETRY: preserve BC0004, partial recipient PDSes and all MVS reports.
```

**No original recipient rerun is authorized.** The exact original JES
job number for the first on-tape MR10 restore has **not** been supplied
in the console output. It will be extracted from the sealed local
saved job summary, never invented.

## Defect and MVS authority

The project `tools/mvs/job-summary` parser builds compact summaries
from `IEFACTRT`, with an optional program-name field. An in-stream
MVS `PROC` may be reported without an explicit `IEBCOPY` program
name on each summary row. The original RC4 runner had already
checked that the full ordered `IEF142I` records prove every
`R0003`–`R0012` executed with `COND CODE 0000`; it then applied
a redundant count of `IEBCOPY` program-name strings in the summary,
which caused the halt.

The source-controlled validator now relies on the **actual ordered
MVS IEF142I step identities and condition codes** plus the clean
JES completion; it no longer requires that optional summary-program
label. This fixes only evidence interpretation: no tape content,
MVS job deck, allocation, manifest or earlier accepted receipt changes.

**The first MR10 installation is not yet declared PASS** merely
from the failure message; its actual saved JES and fresh MVS
catalog/directory still require verification.

## One-shot no-replay continuation

A new, separate `scripts/ta3-rc4-continuation` verifies all
original evidence against the *original, unchanged*
`SHA256SUMS` manifest and consumed authorization marker. Its
mandatory first-profile evidence requires:

1. Exact `failure.json` status/reason for the one known interrupted
   run; no evidence of native-only or combined operations.
2. Original MVS readback of `BT0002(MR10)` byte-matching the frozen
   source JCL, including on-tape `COPY` readback.
3. Actual successful `T3R4MR` JES job result and ten ordered
   MVS `IEF142I` profile steps with RC0000.
4. A **fresh read-only** MVS LISTDS preflight proving all **11**
   `HERC02.BCPL.R4MR` datasets have the correct DCB/volume,
   and all **31** `R4NT`/`R4CB` targets remain absent.
5. A second independent actual MVS LISTDS/DCB and PDS member-directory
   verification for the **11 first-profile PDSes and 94 members**,
   plus unchanged BC0003/BC0004 checksums and approved idle drive.

**Only if every gate passes**, the runner asks one new, narrow
`[y/N]` question to install **only** the missing
`BT0002(NATIVE)` and `BT0002(COMBINED)` on-tape profiles.
The original MR10 restore, producer, previous one-shot marker
and BC0004 tape write are **never replayed**. The new approval
creates a separate no-retry marker under
`workarea/ta3-rc4-continuation/`.

Native-only must restore 11 PDSes and 71 members. Combined must
restore 20 PDSes and 150 members and execute installed
`ICINT19` SCALVEC `TEST:/EXP:/RP:/CODE=0`.
The recovered MR10 (11/94) and remaining profiles (11/71 and
20/150) then total **42 PDSes and 315 members**, all using the
new RC4 tape-resident JCL profiles. The native Cambridge Compiler
remains `absent`.

If any original evidence or fresh MVS dataset state differs,
**halt without consenting** and do not attempt a blind replay.
If the new stateful continuation stops after consent, retain
its new marker and evidence and investigate without retry.

## Qualification

This is a forensic continuation on the same running MVS 3.8J
system using independently isolated recipient namespaces.
It does not certify IBM utilities, prove a fresh IPL of a separate
MVS system, close TA.4/TA.5/TA.7, or approve release publication.
**TA.3 remains IN PROGRESS pending actual MVS continuation.**
