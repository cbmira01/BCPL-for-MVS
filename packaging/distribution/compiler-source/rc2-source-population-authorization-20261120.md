# TA.2 — Approved one-shot historical CAMB_SOURCE population

**Project:** BCPL for MVS 3.8 Reconstruction
**March:** TA.2 — Manifest-Driven Tape Producer
**Date:** 20 November 2026
**Owner decision:** Approved one-time population of the 15 historical
Cambridge Compiler source members; **not** staging of BT0021 or writing
of a BC0002 tape.

## Accepted actual MVS prerequisite

The owner reported:

- `dspal stat CAMB_SOURCE` RC=0.
- `dspal ls CAMB_SOURCE` RC=0 and the actual response:

```text
HERC02.BCPL.CAMBRIDG.SOURCE:
    (empty)
```

Saved original owner-side directory evidence:
`workarea/ta2-rc2-cambsource-20261120T202805Z-855/mvs-members.txt`.
This demonstrates an allocated, empty source PDS but does not by itself
establish its DCB or any staged source records.

The approved tape manifest is `BCPL-0.1.0-rc2`, `BC0002`,
21 datasets. `BT0021` is the **historical** `CAMB_SOURCE` PDS only.
The original 20 selected datasets and prior accepted MVS staging are
untouched. The demoted, filtered, instrumented and GitHub-only compiler
does not belong on the tape.

## Approved MVS operation and safeguards

The tracked `rc2-populate-cambsource-once.py --execute` runner:
1. Validates the canonical rc2 manifest and registry digest and all
   15 original source files against the frozen Git source revision
   `78baec9a8546e4ab09caee779aa2b675379272f3`.
2. Requires local `main`, the exact effective managed target
   `HERC02.BCPL.CAMBRIDG.SOURCE`, and strict UTF-8/CP037 transfer
   settings; confirms the existing `dspal` population dry-run selects
   **only** the 15 historical members.
3. Submits a **fresh read-only** `dspal ls CAMB_SOURCE` MVS inquiry
   and requires the directory to remain strictly empty.
4. Atomically reserves
   `workarea/ta2-rc2-cambsource-population-once/` **before** any write.
   An existing reservation blocks all further execution; failed or
   ambiguous attempts must be reviewed, not silently retried.
5. Invokes the original `dspal populate CAMB_SOURCE --batch`
   implementation. That implementation checks live MVS DCB/space
   compatibility, transfers historical source via IEBGENER and
   independently checks every submitted job's expected RC=0000 steps.
   Existing batching is **8 + 7 members**, with 3,985 and 2,697
   counted JCL cards respectively, against the 4,000-card limit.
6. Persists both original MVS batch submission reports under the
   reserved private workarea directory and requires the explicit
   two-batch/15-member success receipt. It then runs one read-only
   `dspal ls CAMB_SOURCE` and compares the full directory against
   the 15-member canonical selection. **Record bytes are not yet
   independently accepted.**
7. All `dspal` temporary JCL uses `TMPDIR` inside repository
   `workarea/`. No temporary files are intentionally created outside
   the repository root.

The runner does **not** allocate the BT0021 stage target,
perform IEBCOPY staging, touch BT0001–BT0020, access a tape device,
change the release registry, or claim redistribution rights.

## Assistant-workspace checks

The runner and its test module were independently composed in
`/mnt/data/BCPL-for-MVS/packaging/distribution/compiler-source/`
(an assistant test workspace, **not** the owner's repository).
Git blob hashes were checked to match the tested local files.

**8/8 one-shot guard tests PASS**, covering a successful simulated
two-job operation, a second-attempt refusal, empty/nonempty directory,
source plan drift, attempted PDS mapping override, failing MVS jobs,
malformed success evidence and post-write directory mismatch.
An additional **15/15** existing compact `rc2` historical-only
source/manifest tests PASS. Python compilation passed.
These are simulated program logic checks, **not MVS execution**.

## Next acceptance checkpoint

Owner should run the single MVS-facing committed runner after
fast-forwarding local `main`; report its short terminal result and
retain the private `workarea` receipt directory. If it exits nonzero
**do not rerun it**: inspect the saved MVS receipts first.
If it reports the exact 15-member directory, the next step is
read-only source-record fidelity verification, followed by a
**separately approved** BT0021 selective IEBCOPY stage. No new
MVS state change has been performed by the assistant.
