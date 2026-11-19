# TA.1 — Multi-Dataset Tape Mechanics: qualified acceptance candidate

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.1 — Multi-Dataset Tape Mechanics  
**Date:** 19 November 2026  
**Proposed disposition:** **ACCEPT and CLOSE TA.1 (qualified)** — **pending explicit owner decision**.  
**Next march, if approved:** **TA.2 — Manifest-Driven Tape Producer** (design/preflight only; no tape creation permission implied).

## Acceptance against the authoritative two-track contract

| TA.1 acceptance requirement | Actual MVS/Hercules evidence | Qualified result |
| --- | --- | --- |
| **Track A**: two ordered logical standard-label datasets on one scratch volume | BTA101 `BCPL.BT0001` FB80 and `BCPL.BT0002` IEBCOPY PDS, writer JOB 9076; SL map physical files `3,3,2,2,25,2,0` | PASS (qualified) |
| Preserve first dataset while writing second | Saved label/map evidence independently reviewed; both logical datasets survived | PASS (qualified) |
| Independent restoration and comparison of both payloads | JOBS 9084, 9086 restore; JOB 9089 two IEBCOMPR steps, all RC=0000; restored seven-member PDS and FB80 sequential DCB validated | PASS (qualified) |
| Immutable Track A image | BTA101 SHA-256 `d5900cbccaaa2f7eb1bcc59ae30847540e6911c577dafa5e131c0b3a9c8e3fe2` unchanged | PASS (qualified) |
| **Track B**: `RECFM=U` load-library selected-member tape transfer | BTA102 SL `BCPL.BT0001`, JOB 9120 IEBCOPY UNLOAD RC=0000, file counts `3,8,2,0` | PASS (qualified) |
| Independent load PDS restoration | JOB 9136 IEBCOPY RESTORE RC=0000 to new `HERC02.BCPL.TA1B.LOAD(ICINT19)` on TSO002, PO/U/0/6144 | PASS (qualified) |
| Compare restored/source member directory | IEHLIST `TA1BSRC` JOB 9151 on source TSO003 and `TA1BDST` JOB 9152 on restored TSO002, both RC=0000; member `ICINT19` entry `000000` and attributes `02E2` match | PASS (qualified) |
| Executable use from restored `STEPLIB` | JOB 9165 `TA1BGO`, eight pinned MRREGRES scalar/vector steps RC=0000; three ICINT19 invocations from restored library; semantic output matches golden records | PASS (qualified) |
| Immutable Track B image | BTA102 SHA-256 `c3b235ca78d221432199adcde1f7a83aead4f76bab0e0eaa19d77c81d9912210` unchanged after GO | PASS (qualified) |
| Positioning, retention, failure safety | Distinct scratch images BTA101/BTA102; prior read-only guard halts, empty-drive checks, no-overwrite/no-retry markers; checked physical tape filemarks and MVS unit state | PASS (qualified) for tested paths |

## Evidence standard and retained limitations

The evidence is actual operator-reported MVS 3.8J/JES/IEBCOPY/
IEHLIST/ICINT19 runner output, not synthesized execution.
The assistant reviewed committed implementations and output summaries,
but **has not independently opened** private JES/SYSPRINT/HETMAP
files. Original private evidence stays under ignored `workarea/`,
including:
- Track A write `workarea/ta1-operations/BTA101-track-a-execution-20261118T010626Z-5215/`
  and readback `workarea/ta1-operations/BTA101-track-a-readback-20261118T020430Z-5920/`;
- Track B write `workarea/ta1b-operations/BTA102-track-b-write-20261118T235204Z-9548/`,
  restore `workarea/ta1b-operations/BTA102-track-b-restore-20261119T021135Z-10863/`,
  directory `workarea/ta1b-operations/BTA102-track-b-directory-20261119T024927Z-11906/`,
  and restored GO `workarea/ta1b-operations/BTA102-track-b-go-20261119T121015Z-13509/`.

**No byte-for-byte `RECFM=U` load-member identity is claimed.**
Matching directory entry/attrs and the bounded executable GO prove
usable restoration on the accepted scalar/vector case, not bytes.
TA.1 is not final release candidate production, recipient installation,
site-specific HLQ transformation, complete MR10 regression,
native compiler self-compilation, rights clearance, or publication.
The reserved BTA101/BTA102 media are **scratch experiment evidence,
not the release artifact**. Do not reuse, reinitialize or overwrite
either AWS image.

## Decision required

**Proposed owner acceptance:** formally **CLOSE TA.1 (qualified)**,
retaining the above limitations; then establish **TA.2 —
Manifest-Driven Tape Producer** as the next march **for design and
read-only preflight only**.

No TA.2 frozen manifest, production identity/VOLSER selection,
new tape write, dataset installation, or publishing action is
authorized by the TA.1 test results or this proposal.
No further MVS JES test is requested merely to obtain this
formal TA.1 decision.

## Primary tracked references

- [TA.1 kickoff](ta1-kickoff-20261117.md)
- [Track A independent round-trip](../../distribution/create-tape/ta1-track-a-roundtrip-review-20261117.md)
- [Track B restored GO actual result](../../distribution/create-tape/ta1b-restored-go-evidence-20261119.md)
- [Governing tape milestone](milestone-tape-artifact-release.md)
