# TA.2 — JOB 9330 raw FB80 fingerprint reconciliation and transport character mapping

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone/march:** Tape artifact release / TA.2 — Manifest-Driven Tape Producer  
**Date:** 20 November 2026 EST  
**Status:** Observed MVS transport-encoded FB80 records reconciled; **literal CP037 byte identity and BT0021 stage acceptance remain open**.

## MVS evidence and findings

The owner ran the approved read-only IFOX/IEWL/QSAM verification
as **MVS JOB 9330**. The job executed all 15 member-reading GO steps;
the runner reported **7/15 literal CP037 checksum/FNV matches** and
**8/15 fingerprint discrepancies**. Every member's QSAM record
count and trailing all-blank record count nevertheless matched
the frozen historical Git source. In particular, `BLIB` genuinely
holds all **474** records, including its last **two** blank records.
The preceding `dspal get` SYSOUT-based text path, not the source
PDS, had omitted those final blank records from its returned text.

The full raw MVS JOB output and original failed result were retained
by the original runner under
`workarea/ta2-rc2-cambsource-qsam-fidelity/`. Those original
bytes have not been independently inspected by the assistant;
the displayed MVS results and existing script behavior support
the following **candidate byte-translation explanation**.

## Exact observed source-character mapping

Independent GitHub inspection of **all 15** source files at frozen
commit `78baec9a8546e4ab09caee779aa2b675379272f3`,
plus reconstruction of FNV-1a and additive sums over each
80-byte padded EBCDIC record, established an exact match to every
reported JOB 9330 result when only the following three ASCII
characters are remapped from standard CP037:

| Source glyph | CP037 expectation | Effective MVS reader byte |
| --- | --- | --- |
| `\|` | `4F` | `6A` |
| `[` | `BA` | `AD` |
| `]` | `BB` | `BD` |

This is an **empirical profile of the current TK5/Hercules
transport**, not a claim that the whole system uses IBM-1047,
IBM-875, or another standard EBCDIC encoding. Every other ASCII
source character is unchanged relative to Python `cp037`
for the tested 15 member files.

The summed byte differences are exactly explained by the source
character occurrences:

| Member | `\|` | `[` | `]` | Observed MVS minus CP037 sum |
| --- | ---: | ---: | ---: | ---: |
| BCPL | 6 | 0 | 0 | +162 |
| BLIB | 9 | 0 | 0 | +243 |
| CG | 68 | 0 | 0 | +1,836 |
| CGHDR | 32 | 0 | 0 | +864 |
| PM | 6 | 2 | 2 | +140 |
| SYN | 42 | 1 | 1 | +1,123 |
| TRN | 8 | 0 | 0 | +216 |
| TRNHDR | 4 | 0 | 0 | +108 |

`27 × count('|') - 13 × count('[') + 2 × count(']')`
predicts each additive sum discrepancy exactly, including the
two exceptional `PM` and `SYN` members. More significantly,
the **order-sensitive FNV-1a value of every previously failing
member also matches** this exact mapping; the other seven
members still match their original CP037 fingerprints.

**Result:** 15/15 record counts, trailing all-blank record counts,
FNV fingerprints and additive sums agree with the frozen source
after applying the *observed reader transport profile*.
This supplies reproducible evidence that the MVS source-member
bytes are consistent with the approved historical input under
the actual transfer path. It is not a claim of literal CP037
byte-for-byte fidelity, a collision-proof full-byte equality
test, or established portability to differently configured MVS
systems. The original failed CP037 check must remain preserved,
not silently reclassified as passed.

## New saved-MVS-evidence reconciliation gate

`rc2-qsam-reconcile-transport.py --saved-job9330` (read-only
against MVS) checks the original saved **JOB 9330** receipt,
job summary, and full JES report against one another. It
checks the original **JOBs 9325/9326**, all 15 selected source
files against their frozen Git revision and manifest contract,
recomputes both CP037 and narrowly remapped FB80 fingerprints,
and refuses any changed/incomplete result or unexpected
character-mapping discrepancy.

The reconciled report is saved separately under
`workarea/ta2-rc2-cambsource-qsam-transport-reconciliation/`.
It **never** modifies the original JOB 9330 evidence, submits
JES, stages IEBCOPY input, updates the tape candidate, or changes
source members. The new code and test have passed **10/10
focused offline unittest cases** in the assistant workspace,
covering exact mapping, all-blank records, successful and
tampered receipt/report comparisons and fail-closed refusal
cases. The authoritative actual saved-MVS-evidence result
remains to be run on the owner system.

## Decision required before BT0021 staging

The owner must choose the intended **canonical on-tape
EBCDIC source representation**:

1. Preserve exactly the bytes produced by the demonstrated
   TK5/Hercules reader profile (`6A` for `|`, `AD` for
   `[`, `BD` for `]`) and explicitly document this
   transport representation in the release/installation contract.
2. Require literal CP037 source bytes; design and separately
   authorize a controlled MVS correction/repopulation of only
   affected members, then re-verify. This would supersede
   the current source-PDS acceptance and requires an owner
   design decision before any write.

The verification can be closed on **observed-transport fidelity**
once the saved JOB 9330 reconciliation passes, while the final
portable release encoding policy remains an explicit open gate.
No `BT0021` staging or `BC0002` AWS production is
authorized by this record. `BT0001`–`BT0020` staging and
`BCPL-0.1.0-rc2`/21-dataset release selection remain unchanged.
**TA.2 IN PROGRESS.**
