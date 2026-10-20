# Milestone QSAM — Q.0 V/VB zero-data-length logical-record evidence (2026-10-20)

**March:** Q.0 — Reconnaissance & contract (in progress). **Status:** Two standalone MVS 3.8J/TK5 QSAM read/write experiments PASS. This is not evidence of an implemented BCPLQSAM dispatcher or Q.0 closure.

**Origin:** Owner-supplied complete JES, IFOX and IEWL reports for JOB 2168 and JOB 2169, run 20 October 2026. Reproducible [probe generator and operator instructions](../bootstrap-toolchain/probes/q0-qsam-zero-record-probes/README.md) are tracked in Git. Original spool reports remain in the owner's TK5/JES output and were not committed; generated JCL is private to ignored `workarea/qsam-q0-zero/`.

## Observed execution

| Experiment | JOB / name | DASD DCB | Logical records | ASMWR | ASMRD | LKWR | LKRD | WGO | RGO | Reader SYSOUT |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| VZERO | 2168 / QS0VZER | RECFM=V,LRECL=100,BLKSIZE=104 | 15 | 0000 | 0000 | 0000 | 0000 | 0000 | 0000 | `Q0 VZERO 15 RECORDS PASS` |
| VBZERO | 2169 / QS0VBZER | RECFM=VB,LRECL=100,BLKSIZE=404 | 15 | 0000 | 0000 | 0000 | 0000 | 0000 | 0000 | 0000 | `Q0 VBZERO 15 RECORDS PASS` |

Both writer programs emitted fourteen normal variable logical records (cycling total RDW lengths 16, 36, 100) followed by a fifteenth record with **RDW length 4** and zero reserved bytes (a complete four-byte RDW, no application data). The independently linked QSAM readers confirmed the ordinary records' identifiers, lengths, sequence bytes and RDW reserved bytes; for record 15, they separately checked the RDW total length was **4** and reserved bytes were **0**. The reader required EODAD only **after** all 15 records, and emitted the success marker. Both run steps and all four assembly/link steps ended RC=0000.

MVS placed VZERO's temporary `&&Q0DISK` on **WORK01** (device 0290) and VBZERO's `&&Q0DISK` on **WORK04** (device 0293); these are confirmed TK5 3390 work volumes. The data sets were deleted by the read steps. All object and load modules were temporary, and neither `BOOT_OBJ` nor `BOOT_DEVOBJ` changed.

## Narrow conclusion and Q.0 design consequence

On the tested DASD V and VB QSAM paths, a logical record containing **zero data bytes** is representable and returned to the reader as a valid logical record, distinct from an end-of-data indication. The public BCPLQSAM READ contract must therefore preserve successful data length **0** independently of its explicit `QS_EOF` status. In particular, a private staged record must use an explicit pending flag, **never** `pending_length != 0` as the pending-record test. That distinction is already required by the [approved Q.0 staging/resource decision](qsam-q0-staging-resource-design-decision.md); this report adds MVS evidence for zero payload.

These tests do **not** establish that every V/VB geometry accepts zero-payload records, test a zero record at the beginning or middle of a dataset, verify arbitrary binary payloads (including X'00' and X'FF'), test malformed RDWs, repeated EOF reads or undersized-buffer retries, determine supported record-size ceilings, or prove that native BCPLQSAM already implements these semantics. The readers checked the DCB effective **LRECL=100** after OPEN; they did not independently check effective RECFM or BLKSIZE. The JCL DCB values above identify the requested data-set attributes, not a complete independently observed INFO return.

## Reproduce

```sh
PROBE=bootstrap-toolchain/probes/q0-qsam-zero-record-probes
python3 "$PROBE/make-jobs.py" vzero --check
python3 "$PROBE/make-jobs.py" vbzero --check
python3 "$PROBE/make-jobs.py" vzero
bash tools/mvs/submit-jcl workarea/qsam-q0-zero/q0-vzero.jcl
python3 "$PROBE/make-jobs.py" vbzero
bash tools/mvs/submit-jcl workarea/qsam-q0-zero/q0-vbzero.jcl
# For each reported number:
# tools/mvs/job-summary JOBNUMBER --max-rc 0
# tools/mvs/dump-report-for-job JOBNUMBER
```

Check each fresh JES result independently before declaring PASS. Generated JCL contains locally configured job-card credentials and must remain outside Git. **Q.0 remains open. Q.1 has not started.**
