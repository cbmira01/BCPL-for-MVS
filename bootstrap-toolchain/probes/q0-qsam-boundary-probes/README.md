# Milestone QSAM — March Q.0 fixed-record boundary probes

**Status:** All four profiles passed in MVS/TK5 on 20 October 2026. [Execution evidence](../../../packaging/qsam-q0-fixed-boundary-evidence-20261020.md).

| Profile | JOB | RECFM | LRECL | BLKSIZE | Logical records |
| --- | --- | --- | ---: | ---: | ---: |
| f80 | 2163 | F | 80 | 80 | 23 |
| f1024 | 2165 | F | 1024 | 1024 | 7 |
| fb8k | 2166 | FB | 80 | 8000 | 105 |
| fb16k | 2167 | FB | 80 | 16000 | 210 |

This uses the original q0-qsam-dasd-probes writer and reader as sources, modifies them in-memory, and produces test-only IFOX/IEWL/JCL. The independent reader checks the effective DCB, logical record content, count and end-of-data. No persistent PDS writes.

To verify static generation from the repository root:

    PROBE=bootstrap-toolchain/probes/q0-qsam-boundary-probes
    python3 "$PROBE/make-jobs.py" f80 --check
    python3 "$PROBE/make-jobs.py" f1024 --check
    python3 "$PROBE/make-jobs.py" fb8k --check
    python3 "$PROBE/make-jobs.py" fb16k --check --allow-large

To run: bash "$PROBE/run-q0-boundary.sh" PROFILE, adding --allow-large for fb16k only after verifying SYSDA device geometry. TK5 WORK01–WORK04 were confirmed as Hercules 3390. JCL generated in ignored workarea/ can contain configured JOB-card credentials and must never be committed.

These are standalone QSAM probes, not working BCPLQSAM. Q.0 remains open; Q.1 has not started.
