# Milestone QSAM — Q.0 geometry precheck and empty-EOF probes

**Status: locally generated and statically checked; not yet executed in MVS.** These are isolated assembler reconnaissance jobs, not a BCPLQSAM module. They do not install or modify object-library PDS members. All data sets are temporary; JCL is generated under ignored `workarea/`.

## GEOMETRY: `QS0GEOM`

`geometry-check.asm` invokes non-opening `RDJFCB` on two JCL-allocated temporary DDs: `QGOOD` (FB, LRECL=80, BLKSIZE=800) and `QBAD` (FB, LRECL=80, BLKSIZE=801). It checks the returned 176-byte JFCB fields before dividing BLKSIZE by LRECL. **No OPEN is issued on either input DCB.** The only QSAM OPEN/PUT/CLOSE serves `QOUT` to emit the marker.

The JFCB offsets are **provisional for MVS 3.8J** and are specifically being tested: `JFCRECFM` +100 (X'64'), `JFCBLKSI` +102 (X'66'), `JFCLRECL` +104 (X'68'). IBM documents these for a later JFCB layout; applicability to MVS 3.8J remains to be demonstrated. The probe checks X'90' for FB and the actual expected values 800/80 versus 801/80. An unexpected result is useful evidence, **not** proof the DD lacks its JCL attributes.

Expected three RC=0000 steps (`ASM`, `LKED`, `GO`) and marker:

```text
Q0 JFCB FB80/800 OK FB80/801 REJECT PASS
```

This is a narrow **pre-OPEN guard** proof, not generic abend recovery and not implemented BCPLQSAM.

## EMPTY: `QS0EMPTY`

`empty-write.asm` opens and closes a temporary FB80/800 DASD file without PUT. The independent reader opens the empty file, issues GET, observes EODAD once, and retains an EOF flag. It simulates a second application READ, which returns EOF using the flag **without issuing another GET**. It verifies two application requests, one EODAD event and no data records.

Expected six RC=0000 steps (`ASMWR`, `ASMRD`, `LKWR`, `LKRD`, `WGO`, `RGO`) and marker:

```text
Q0 EMPTY FB EOF2 EODAD1 PASS
```

This tests a standalone persistent-EOF policy. It does **not** prove an operational BCPLQSAM READ API.

## Run from repository root, one job at a time

```sh
PROBE=bootstrap-toolchain/probes/q0-qsam-followup-probes
python3 "$PROBE/make-followups.py" geometry --check
python3 "$PROBE/make-followups.py" empty --check
python3 "$PROBE/make-followups.py" geometry
bash tools/mvs/submit-jcl workarea/qsam-q0-followups/q0-geometry.jcl
# Inspect JOBNUMBER from the submit command before submitting EMPTY:
tools/mvs/dump-report-for-job JOBNUMBER
python3 "$PROBE/make-followups.py" empty
bash tools/mvs/submit-jcl workarea/qsam-q0-followups/q0-empty.jcl
tools/mvs/dump-report-for-job JOBNUMBER
```

The `--check` mode writes no deck and uses no configured credentials. Normal generation uses the project's authenticated JOB card; generated JCL has mode 0600 and must **never** be committed. Check the full JES execution, step codes, and marker; static generation alone is not an MVS PASS. If a job fails or abends, retain the report.

**Q.0 remains open. Q.1 has not started.**
