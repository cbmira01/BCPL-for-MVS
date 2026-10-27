# Milestone QSAM — Q.1 consolidated pre-acceptance development campaign

**March:** Q.1 — Linkage & OPEN/CLOSE skeleton. **Status:** test-only candidate;
OPEN and NOT ACCEPTED. Owner approved the consolidated approach and subsequently approved a
GitHub commit of this test-only candidate. No JES submission, production
modification, MVS installation, or Q.1 closure is authorized. GitHub `main` is authoritative; workarea outputs are disposable.

## Objective and dependency boundaries

Re-use the Q.1 `QSAMSVC:200` and accepted BCEX/BCRG selection ABI, not an
independent registrar. Continue the tested explicit-F1024-DCB three-DD
baseline, isolate missing-DCB `OBTAIN` feasibility, and exercise independent
resource ownership, finalization, and ordinary negative cases without
mixing Q.2 record transfer into Q.1.

### Track A — native lifecycle, four distinct job identities

| Case | BCPL caller | Assertions | Native GO RC |
|---|---|---|---|
| `Q16FIN` | `test-q1-finish.bcpl` | 16 live handles, 17th refusal, close/reopen, stale handle, INFO, unsupported READ/WRITE, finalizer 16-CLOSE trace | 0 |
| `Q16STP` | `test-q1-stop.bcpl` | Same operations; preserve explicit STOP(8) after 16-CLOSE trace | 8 |
| `Q1NEG` | `test-q1-negative.bcpl` | Invalid DD names/modes/reserved argument words, missing DD, invalid handle | 0 |
| `Q1OUT` | `test-q1-output.bcpl` | Output OPEN/INFO/CLOSE against temporary `QOUT`, no record writing | 0 |

`prepare-q1-campaign.py` reuses the accepted Q.1 three-DD/query temporary
link templates and the Q.0 16-DCB initialized F1024 writer. All sixteen
GO reader DDs carry explicit `RECFM=F,LRECL=1024,BLKSIZE=1024` to avoid
making lifetime evidence depend on omitted-geometry recovery. The negative
case has no QSAM DD allocations; the output case uses a separately allocated
temporary QOUT. Every job is independently executable at `REGION=256K`.
Source-controlled JCL generation does **not** compile, submit, or install.

The existing candidate `QSMFIN` emits
`BCPLQSAM Q1 FINALIZER 16 CLOSE PASS` only when sixteen CLOSE operations
succeed and the private live/DCB/stage counters become zero. The review
script requires this **native** trace after link-edit output, not merely
source-listing text or a pre-FINISH BCPL message. A STOP GO RC=8 is expected
only for `Q16STP` and does not by itself imply finalizer failure.

### Track B — independent test-only pre-OPEN VTOC feasibility

`prepare-q1-obtain.py` upgrades the existing `Q13DD` identity-only
instrumentation for temporary DASD DDs Q00/Q01/Q02, but does not modify
the production assembler or execute QSAM OPEN. It retrieves the currently
allocated 44-byte dataset name, 6-byte volser and single-volume count from
successful `RDJFCB`, then issues **read-only** `OBTAIN` using `CAMLST
SEARCH`. It prints R15 plus two independent 48-byte raw data slices from
the returned 140-byte DSCB work area: `Q1O:Qnn:RC/DS0/DS1`; otherwise a
`Q1O:Qnn:SKIP` line. The probe skips blank/ambiguous or multi-volume
identities and always returns the Q.1 diagnostic `QS_ERR_OPEN=-6`.

Only a target-MVS IFOX/JES execution can confirm the `OBTAIN` macro,
return-code conventions, 96-byte DSCB data layout and field offsets.
No DSCB record attributes are interpreted as production geometry by the
candidate, and no automatic fallback is approved on these results alone.
The period OS/VS2 Release 3.8 data-management reference describes this
non-opening `OBTAIN`/`CAMLST SEARCH` mechanism. The test does not use
`SCRATCH`, `RENAME`, catalog-only identity, GET, PUT or QSAM OPEN.

### Track C — design review / next development subcampaign

We can combine ordinary failed OPEN, surviving-handle checks, private
stage/slot accounting, rollback, and returned-CLOSE cleanup observations
with the Track A harness, **but not yet treat their exceptional behavior
as owner-approved**. The candidate's current error precedence preserves
the primary OPEN/stage error and quarantines uncertain returned-CLOSE
ownership. Before implementing fault injection, settle these questions:

1. Whether test-only post-OPEN conditional-stage-refusal injection may be
   used to validate rollback and surviving handles under disposable DDs.
2. Whether returned-CLOSE injection should simulate a nonzero return
   *without* executing native CLOSE (leaving a real opened DCB under
   test-job termination), or use a narrower mock of the private cleanup
   result without claiming it proves actual macro failure.
3. Whether the original primary failure or the returned cleanup failure
   takes precedence in the public result; no unapproved status API changes.

The safe immediate candidate includes Tracks A and B; Track C is a design
proposal, **not** an authorized injection or production change.

## Evidence expectations and execution discipline

- Run source syntax and synthetic deck tests before any commit.
- Run source-controlled `--check` with the complete repository in WSL;
  synthetic isolated fixtures do not prove the full JCL integration.
- Do not compile/submit JES until an exact, separately approved batch
  enumerates each compilation and execution job, output checksum, and
  one-attempt guards. No implicit retries, polling loops, or RC-based
  resubmission.
- Preserve full JES reports, IFOX severity, IEWL MAP/XREF and every GO step
  result. `check-q1-campaign-evidence.py` fails closed for missing native
  output or unexpected step codes; it does not decide milestone acceptance.
- Preserve JOB 6620/6621/6622 evidence and all earlier local decks.
- When all functional and native code paths pass, run the accepted full
  native regression panel separately as Q.1's last acceptance gate.
- No changes to accepted `BCPLIO`, Core Runtime, compiler, registry or
  installed PDS members. Q.2 is not started.
