# Milestone QSAM — Q.0 effective INFO and record-ceiling review

**Status:** Owner-approved **1024-byte total private record stage per
handle** following MVS JOBs 2180–2182. Q.0 remains open; Q.1 not
started. This is an implementation ceiling, not an MVS maximum and not
a claim of working production BCPLQSAM.

## Existing verified MVS observations

| Evidence | RECFM | Effective LRECL | BLKSIZE | Stage-size implication |
| --- | --- | ---: | ---: | --- |
| JOB 2165 | F | 1024 | 1024 | 1024 logical data bytes proven |
| JOB 2166 | FB | 80 | 8000 | 80-byte records, not 8000-byte records |
| JOB 2167 | FB | 80 | 16000 | 80-byte records, not 16000-byte records |
| JOB 2161 | V | 100 | 104 | 4-byte RDW + up to 96 data bytes |
| JOB 2162 | VB | 100 | 404 | 4-byte RDW + up to 96 data bytes |
| JOB 2177 | -- | -- | -- | one 1 MiB GETMAIN refusal, R15=4, at REGION=256K |
| JOB 2180 | V | 1024 | 1028 | 1024 stage bytes including four-byte RDW; 1020 data bytes |
| JOB 2181 | VB | 1024 | 2052 | 1024 stage bytes including four-byte RDW; 1020 data bytes |
| JOB 2182 | -- | -- | -- | 16 concurrent 1024-byte GETMAIN areas, not 16 OPEN DCBs |

The fixed-record boundary tests checked effective post-OPEN DCB values.
The earlier V/VB readers checked effective LRECL but not post-OPEN
RECFM/BLKSIZE. **JOBs 2178 / QS0INFV and 2179 / QS0INFVB PASSED**,
observing effective RECFM, LRECL, BLKSIZE, enum mapping 3/4 and
96 dataset payload bytes. See [MVS INFO evidence](qsam-q0-post-open-info-evidence-20261020.md).
Neither implements `QSAMSVC` or a public `QSINFO` result vector.

The public INFO contract is already specified: `result!4` is a
project-defined record-format enum, `!5` the effective DCB LRECL,
`!6` the effective BLKSIZE, and `!7` the maximum supported **data bytes**.
For F/FB, logical data size is LRECL; for V/VB, the data maximum is at
most LRECL minus the four-byte RDW. The physical BDW is not public data.

## Accepted ceiling for the initial BCPLQSAM implementation

The owner approved **1024 bytes total private stage per handle**, after
reviewing [JOBs 2180–2182](qsam-q0-1024-byte-stage-evidence-20261020.md).
The standalone V/VB jobs verified length-4 RDW-only records,
length-16 records and length-1024 records with full byte-pattern checks;
JOB 2182 verified sixteen independent simultaneously allocated
1024-byte areas under GO REGION=256K. This approval selects a
**conservative BCPLQSAM contract**, not a universal MVS ceiling.

For supported datasets, the effective record format and LRECL must be
validated before GET/PUT. The supported geometry and the public
`INFO.result!7` are:

| Effective RECFM | Effective LRECL allowed | Public maximum data bytes |
| --- | --- | --- |
| F / FB | 1–1024 | effective LRECL |
| V / VB | 4–1024 (includes four-byte RDW) | effective LRECL minus 4 |

Valid F/FB and V/VB BLKSIZE relationships and device restrictions
still apply; invalid or unsupported geometry must be rejected without
issuing GET/PUT. Avoid known incompatible-OPEN abends through
preflight where practicable, not through unproven general recovery.

The sixteen private 1024-byte stages alone total **16,384 bytes**.
JOB 2182 did **not** account for sixteen DCBs or QSAM buffers.
**Subsequent [JOBs 2183–2186](qsam-q0-concurrent-dcb-evidence-20261020.md)
passed the 1/3/8/16-OPEN-DCB standalone test, with a private stage
per DCB at GO REGION=256K.** These programs include real QSAM DCBs
and access-method buffering, but not the completed BCPLQSAM
dispatcher/handle table or native BCPL runtime and application.
They are **not** proof that sixteen complete BCPLQSAM handles
fit into `REGION=256K`.

## Remaining Q.0 gate

1. Post-OPEN V/VB INFO: **passed JOBs 2178–2179** at LRECL=100.
   Public BCPLQSAM INFO remains unimplemented.
2. Candidate 1024-byte stage investigations: **passed JOBs 2180–2182
   and owner approved the initial implementation limit**. Separately
   verify the production private-stage implementation and negative
   over-limit behavior. The **standalone 16-live-DCB** test passed
   in JOB 2186, but the complete BCPLQSAM/BCPL application
   region budget is still unverified.
3. Resolve the error-path and exceptional CLOSE contracts, and the
   separate Milestone Runtime Extensions R.0 registration/finalizer
   design. The known S013-20 OPEN abend must remain documented.
4. The numeric stage ceiling is approved; **Q.0 gate acceptance is
   separate**, pending error/lifecycle decisions or explicit deferrals
   and owner review. Do not begin Q.1 from these probes alone.
