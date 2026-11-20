# TA.2 — BT0001/BT0002 saved MVS preflight review

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 19 November 2026 EST / 20 November UTC  
**State:** Owner-operated read-only MVS preflight completed; offline independent saved-output review implemented; **no new staging or production tape authorized**.

## Actual MVS checkpoint

The owner executed `scripts/ta2-bootstrap-target-preflight --live` on `main`
`3c97e6f7f0c943ca4f5268bd4922536ea697a008`, reporting:

```text
TA.2 BT TARGET PREFLIGHT: 2 catalog-absent; TSO002 VTOC observed.
Private MVS evidence: workarea/ta2-bootstrap-target-preflight/20261120T025333Z-20572
No allocation, tape write or repeat of accepted JOB 9310.
```

This establishes the **owner-reported MVS LISTDS catalog-absence result** for
`HERC02.BCPL.TA2STG.BT0001` and `BT0002`, with an IEHLIST VTOC observation
on TSO002. The assistant did not directly inspect the private full JES reports;
the observation is not a free-space review or staging-write permission.
Accepted BT0003–BT0020 staging (JOB 9310) and 9311/9312 verification remain closed.

## New tool and precise scope

`scripts/ta2-bootstrap-preflight-review --evidence <existing-run>` consumes
the **saved** read-only LISTDS/IEHLIST run and submits **no additional JES
jobs**. It reuses the existing `dspal-core`, `ta2-bootstrap-target-preflight`,
`ta2-target-preflight` and `ta2-target-review` MVS parsers; it does not
implement IBM LISTDS or IEHLIST.

The review checks the original SHA256-sealed report set, exact two names,
TSO002, two distinct JES job IDs, reported catalog absence, formatted VTOC
inventory and IEHLIST-reported free tracks. It compares the observed total
to the **proposed** allocation budget from the already-generated staging JCL:

| New input | Primary tracks | Secondary tracks | Directory blocks |
| --- | ---: | ---: | ---: |
| BT0001 sequential FB80 | 5 | 1 | — |
| BT0002 installer PDS FB80 | 20 | 5 | 10 |
| **Initial primary + one secondary allowance** | **25** | **6** | |

This **31-track preliminary allowance** sums the primary allocations
plus one secondary extent each; it is not an upper bound if MVS needs
further secondary extents. The comparison does not prove extent contiguity or present-time vacancy. Real MVS allocation results will
determine whether the proposed SPACE amounts work.

A successful offline review creates a **new**, SHA256-sealed
`workarea/ta2-bootstrap-preflight-review/<run>/` private receipt and prints
a compact verdict. The original user MVS evidence is not modified.
A missing or malformed free-space summary produces a clear REFUSAL rather
than assuming capacity. No version, release VOLSER, manifest registry,
PDS, PS, tape, or JOB card is created.

## Verification and next boundary

**14/14 focused synthetic offline tests PASS** in the assistant's
repository-root workspace. They exercise the exact MVS receipt, saved report
integrity, wrong targets/jobs, VTOC collision, 31-track limit, nonexistent
free-space summary, output no-overwrite and refusal of unexpected inputs.
Python syntax compilation PASS. These tests do not replace running the tool
against the owner's private raw saved MVS output.

Once the saved-MVS review is confirmed, the next actual build decision is
the proposed release identity/version/VOLSER and specific BT0001/BT0002
allocation authority; neither is inferred from this read-only success.
The generated six-step one-shot stage deck remains **unsubmitted** until
the separate explicit approval; accepted BT0003–BT0020 must never be
reallocated. Candidate tape writing, restoration and TA.2 closure remain
subject to their own milestone gates.

**TA.2 IN PROGRESS; TA.0/TA.1 qualified closures unchanged.**
