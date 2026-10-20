# Q.0 — standalone QSAM DASD probes (FB, V, VB)

**Status:** Executed successfully under MVS 3.8J/TK5 on JES job date
20 October 2026: FB **JOB 2160**, V **JOB 2161**, VB **JOB 2162**.
Each completed all six assembly/link/execute steps with RC=0000.
See [Q.0 DASD execution evidence](../../../packaging/qsam-q0-dasd-evidence-20261020.md).
These are Q.0 reconnaissance tests, **not** BCPLQSAM implementation and not
Q.1 code. They compile and link two native S/370 programs from source with
IFOX and IEWL, creating only temporary object/load modules and DASD datasets.
No BCPLMAIN/BCPLIO source or persistent PDS member is changed.

## Tests

| Profile | Disk DD | Record/data plan | Intended evidence |
|---|---|---|---|
| `fb` | `RECFM=FB,LRECL=80,BLKSIZE=800` | 23 fixed logical records | Actual blocked DASD QSAM across multiple 10-record blocks; effective DCB attributes, data/order, EOF |
| `v` | `RECFM=V,LRECL=100,BLKSIZE=104` | 15 variable records, RDW total sizes 16/36/100 | Unblocked variable-record QSAM length/RDW/EOF behavior |
| `vb` | `RECFM=VB,LRECL=100,BLKSIZE=404` | Same 15 lengths | Blocked variable-record QSAM, BDW handled internally by MVS |

Writer (`ASMWR` + `LKWR` + `WGO`) creates `&&Q0DISK` on SYSDA,
then reader (`ASMRD` + `LKRD` + `RGO`) reopens it using the
allocated temporary DSN. Both use QSAM move mode, independently.
On success, reader emits a single 80-byte report record to `QOUT`:

- FB: `Q0 FB DASD 23 RECORDS PASS`
- V/VB: `Q0 VARIABLE 15 RECORDS PASS`

`RGO RC=0000` alone is not the complete acceptance criterion: also check
`QOUT`, the writer RC, reader RC, assembler/link reports, and any JCL
or QSAM system messages. MVS OPEN/GET/PUT/CLOSE failures may ABEND;
these exploratory routines do not promise recoverable system errors.

## Run (one profile at a time)

From the repository root after updating the checkout:

```sh
bash bootstrap-toolchain/probes/q0-qsam-dasd-probes/run-q0-dasd.sh fb
```

Only after checking the FB job, run the variable experiments:

```sh
bash bootstrap-toolchain/probes/q0-qsam-dasd-probes/run-q0-dasd.sh v
bash bootstrap-toolchain/probes/q0-qsam-dasd-probes/run-q0-dasd.sh vb
```

The generator leaves private, potentially credential-bearing JCL in
`workarea/qsam-q0-dasd/q0-{fb,v,vb}.jcl`. Never add those generated
files to Git. An offline structural JCL/source sanity check is possible:

```sh
python3 bootstrap-toolchain/probes/q0-qsam-dasd-probes/make-jobs.py fb --check
python3 bootstrap-toolchain/probes/q0-qsam-dasd-probes/make-jobs.py v --check
python3 bootstrap-toolchain/probes/q0-qsam-dasd-probes/make-jobs.py vb --check
```

For each submitted job use:

```sh
tools/mvs/job-summary JOBNUMBER --max-rc 0
tools/mvs/dump-report-for-job JOBNUMBER
```

## Evidence boundaries and construction

This experiment is based on the project’s already-tested IFOX/QSAM
FB80 SYSOUT probe (JOB 2159), current `bootstrap-toolchain/asm/bcplio.asm`,
and the period [IBM OS/VS2 MVS Data Management Macro Instructions, Release 3.8,
GC26-3873-0](https://www.bitsavers.org/pdf/ibm/370/OS_VS2/Release_3.8_1978/GC26-3873-0_OS_VS2_MVS_Data_Management_Macro_Instructions_Rel_3.8_Mar79.pdf).
The manual states that a variable logical record's `LRECL` includes a
four-byte RDW, and that a variable-blocked dataset uses a BDW at the
physical block level. On `GET` in move mode, the record area contains an
RDW plus data. Neither the RDW nor the BDW belongs in BCPLQSAM's public
logical-record payload.

The reader checks effective fixed-format DCB RECFM, LRECL and BLKSIZE
using offsets identified in the JOB 2159 IFOX DCB listing. The variable
reader checks LRECL and each returned RDW, with data and order. The
variable probes do **not** yet check every possible RECFM, record-size
limit or unusual zero-data-length case.

The observed PASS results validate the specified format, sizes and
observed TK5 behavior only. FB reader verified effective RECFM=FB,
LRECL=80 and BLKSIZE=800. The V/VB reader verified LRECL=100,
the individual RDW lengths and reserved bytes, identifiers, sequence
and EOF; it did not inspect effective V/VB RECFM/BLKSIZE or every
payload byte. No largest-size or zero-data-length case was tested.
The tests do not implement an optional registrar, buffering, error
recovery or pending-record retry. Q.0 remains open.
