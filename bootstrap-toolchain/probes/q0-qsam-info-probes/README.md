# Milestone QSAM — March Q.0 effective DCB INFO probes

**Status: prepared and locally checked; NOT yet run on MVS.** Two isolated
IFOX/QSAM jobs (`QS0INFV` and `QS0INFVB`) extend the accepted V/VB DASD
reader with post-OPEN checks. They do **not** implement BCPLQSAM, `QSAMSVC:200`,
public BCPL vectors, or Runtime Extensions registration.

The generator uses the existing V/VB writer and reader as read-only
source material. It inserts assertions into the reader *after* `OPEN`:

| Job | RECFM from opened DCB | Effective LRECL | BLKSIZE | Project `QS_FMT_*` enum | Payload limit from DCB |
| --- | --- | ---: | ---: | ---: | ---: |
| `QS0INFV` | `X'40'` V | 100 | 104 | 3 (`QS_FMT_V`) | 96 bytes |
| `QS0INFVB` | `X'50'` VB | 100 | 404 | 4 (`QS_FMT_VB`) | 96 bytes |

The reader checks DCB offsets `+36` (RECFM), `+62` (BLKSIZE), and `+82`
(LRECL), as derived from the project's IFOX DCB expansions and earlier
Q.0 FB tests. It maps the raw DCB byte to the project's numeric format
code and computes `LRECL-4` for V/VB data capacity. It then reads and
validates all 15 logical records and EODAD using the existing reader.

This calculation uses the observed **dataset** limit and does not
establish the BCPLQSAM implementation ceiling. The accepted INFO contract
specifies `result!7 = min(dataset data limit, implemented limit)`.
A separate final BCPLQSAM implementation must validate its own bounds.

## Operation

From repository root, after applying the checked patch:

```sh
PROBE=bootstrap-toolchain/probes/q0-qsam-info-probes
python3 "$PROBE/make-info-jobs.py" v --check
python3 "$PROBE/make-info-jobs.py" vb --check
python3 "$PROBE/make-info-jobs.py" v
bash tools/mvs/submit-jcl workarea/qsam-q0-info/q0-info-v.jcl
python3 "$PROBE/make-info-jobs.py" vb
bash tools/mvs/submit-jcl workarea/qsam-q0-info/q0-info-vb.jcl
# For each returned job number:
tools/mvs/dump-report-for-job JOBNUMBER
```

Each deck contains six steps (`ASMWR`, `ASMRD`, `LKWR`, `LKRD`, `WGO`,
`RGO`) using an isolated temporary `&&Q0DISK` dataset. Expected all
RC=0000 and corresponding QOUT marker:

```text
Q0 INFO V OPEN DCB ENUM3 DATA96 PASS
Q0 INFO VB OPEN DCB ENUM4 DATA96 PASS
```

The `--check` mode creates no file, reads no credentials, and submits no
job. The normal generator writes mode-0600 authenticated decks under
ignored `workarea/`; never commit them. No BOOT_OBJ, BOOT_DEVOBJ, core
runtime, or compiler source changes are required. Do not report MVS PASS
until the owner supplies the actual JES output.
