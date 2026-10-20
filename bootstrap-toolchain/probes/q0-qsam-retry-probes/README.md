# Milestone QSAM — Q.0 pending logical-record retry probe

**Status: MVS PASS — JOB 2174, 20 October 2026.** This is a standalone System/370 IFOX/QSAM experiment, not an implementation of BCPLQSAM or `QSAMSVC:200`. March Q.0 — Reconnaissance & contract remains open. Q.1 has not started.

The approved [Q.0 staging/resource decision](../../../packaging/qsam-q0-staging-resource-design-decision.md) requires a distinct private stage for each input handle and `READY`/`PENDING`/`EOF` state. This probe exercises the *single-input-handle state machine* without public request/result vectors, storage allocation, or multiple handles. The private stage is a statically allocated 80-byte buffer, not yet the proposed dynamic per-handle allocation.

## Exact experiment: `QS0RETRY`

The writer opens temporary DASD `&&Q0RETRY` as `RECFM=FB,LRECL=80,BLKSIZE=800`, writes two complete logical records, and CLOSEs it. The independent reader opens the same dataset for input and simulates multiple READ requests using an 80-byte application destination, a declared capacity word, and its private 80-byte stage.

| Sequence | Requested capacity | Expected simulated status | Required/actual length | QSAM GET calls so far |
| --- | ---: | ---: | ---: | ---: |
| First record, initial READ | 7 | `QS_ERR_CAPACITY = -1` | 80 | 1 |
| First record, short retry | 79 | `QS_ERR_CAPACITY = -1` | 80 | 1 |
| First record, sufficient retry | 80 | `QS_OK = 0` | 80 | 1 |
| Second record, initial READ | 0 | `QS_ERR_CAPACITY = -1` | 80 | 2 |
| Second record, sufficient retry | 80 | `QS_OK = 0` | 80 | 2 |
| First end-of-data READ | 80 | `QS_EOF = 1` | 0 | 3 (EODAD) |
| Second end-of-data READ | 80 | `QS_EOF = 1` | 0 | 3 (no extra GET) |

The reader ensures the application's destination remains completely unchanged (80 bytes of `X'5A'`) on each too-small result and at EOF. It verifies record order and bytes at the record head, including `X'00'` and `X'FF'`, and a distinct final byte, plus 69 blank filler bytes. Counting GET attempts **before** the macro means the first EODAD GET is included. The `PENDING` state prevents extra GET attempts during capacity retries; `EOF` prevents extra GET calls after EODAD.

**Observed MVS result (JOB 2174):** all six steps (`ASMWR`, `ASMRD`, `LKWR`, `LKRD`, `WGO`, `RGO`) ended RC=0000 and `QOUT` contained:

```text
Q0 FB80 PENDING RETRIES 2 RECORDS PASS
```

[JOB 2174 evidence](../../../packaging/qsam-q0-pending-retry-evidence-20261020.md) records the owner-verified JES results.

## Run from repository root

```sh
PROBE=bootstrap-toolchain/probes/q0-qsam-retry-probes
python3 "$PROBE/make-jobs.py" --check
python3 "$PROBE/make-jobs.py"
bash tools/mvs/submit-jcl workarea/qsam-q0-pending-retry/q0-retry.jcl
# For the returned number:
tools/mvs/job-summary JOBNUMBER --max-rc 0
tools/mvs/dump-report-for-job JOBNUMBER
```

The `--check` path uses no job-card credentials and writes no JCL. The generated deck has mode 0600, uses only temporary private DASD, and may contain local job-card credentials; keep it in ignored `workarea/` and never commit it. JOB 2174 passed on MVS. Reruns must still be checked against their own JES output; a static generator check alone is never an MVS PASS.

**Limits:** This probe does not test the public BCPL buffer pointer conversion or vector ABI, V/VB RDW handling or zero-data-length pending records, distinct handles, MVS storage allocation/cleanup, or a general recovery mechanism for an MVS abend. Those require separate tests and milestone gates. No accepted PDS objects change.
