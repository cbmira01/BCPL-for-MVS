# Milestone QSAM — Q.0 effective INFO and record-ceiling review

**Status:** Engineering proposal only. March Q.0 remains open; Q.1 has
not started. No maximum record size or public API change is approved.

## Existing verified MVS observations

| Evidence | RECFM | Effective LRECL | BLKSIZE | Stage-size implication |
| --- | --- | ---: | ---: | --- |
| JOB 2165 | F | 1024 | 1024 | 1024 logical data bytes proven |
| JOB 2166 | FB | 80 | 8000 | 80-byte records, not 8000-byte records |
| JOB 2167 | FB | 80 | 16000 | 80-byte records, not 16000-byte records |
| JOB 2161 | V | 100 | 104 | 4-byte RDW + up to 96 data bytes |
| JOB 2162 | VB | 100 | 404 | 4-byte RDW + up to 96 data bytes |
| JOB 2177 | -- | -- | -- | one 1 MiB GETMAIN refusal, R15=4, at REGION=256K |

The fixed-record boundary tests checked effective post-OPEN DCB values.
The earlier V/VB readers checked effective LRECL but did not check
post-OPEN RECFM or BLKSIZE. New **unexecuted** Q.0 test-only INFO probes
`QS0INFV` and `QS0INFVB` fill those two observational gaps for the
already-tested record geometry; they check raw DCB fields and the
proposed public format mapping `3/4` without implementing `QSAMSVC`.

The public INFO contract is already specified: `result!4` is a
project-defined record-format enum, `!5` the effective DCB LRECL,
`!6` the effective BLKSIZE, and `!7` the maximum supported **data bytes**.
For F/FB, logical data size is LRECL; for V/VB, the data maximum is at
most LRECL minus the four-byte RDW. The physical BDW is not public data.

## Candidate ceiling for owner consideration

**Candidate: 1024 bytes of private stage per handle**, subject to new
V/VB tests at effective LRECL=1024 and concurrent-handle storage checks.
This is attractive because the full 1024-byte F logical record has
already passed. It is **not accepted** merely because one fixed-format
record works; prior V/VB tests reach only LRECL=100.

For the proposed ceiling, `INFO.result!7` would be computed as:

- F/FB: effective LRECL, only if <=1024 and otherwise OPEN rejected.
- V/VB: effective LRECL minus 4, only if effective LRECL <=1024 and
  otherwise OPEN rejected; zero-data-length records remain valid.

The 16 private stages alone would consume 16 KiB, excluding DCB/control
regions, QSAM's own block buffers, and the core BCPL program. That is
**not** a measured total, nor a promise of 16-handle success at a given
REGION. The limit and memory budget require explicit approval and tests.

## Remaining Q.0 gate

1. Execute the new post-OPEN V/VB INFO probes and inspect all six JES
   step codes and markers. This remains independent of production BCPLQSAM.
2. For the 1024-byte candidate, separately verify V/VB records with
   effective LRECL=1024, including RDW-only and near-maximum payloads;
   select a region budget for 16 simultaneously staged handles.
3. Resolve the error-path and exceptional CLOSE contracts, and the
   separate Milestone Runtime Extensions R.0 registration/finalizer
   design. The known S013-20 OPEN abend must remain documented.
4. Ask the owner to approve a numeric ceiling and explicit Q.0 exit
   gate only after verifying those remaining facts or recording an
   explicit deferral. Do not begin Q.1 from these probe results alone.
