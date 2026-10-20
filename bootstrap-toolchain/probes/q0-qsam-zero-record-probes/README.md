# Milestone QSAM / March Q.0 — V/VB zero-data-length record probe

**Status: prepared, not yet executed on MVS.** This is a standalone assembler test, not an implementation of BCPLQSAM. Original `q0-qsam-dasd-probes` files remain unchanged.

The writer emits 15 records using the original V/VB assembler, except that the last record's RDW total length is **4** (`X'00040000'`) and therefore its payload length is **0**. The reader verifies records 1–14 as before; for record 15 it verifies length 4 and both reserved RDW bytes zero, then verifies **EODAD occurs only after record 15**. The marker is checked only after successful completion. This distinguishes a zero-data-length logical record from EOF.

Run from repository root:

```sh
PROBE=bootstrap-toolchain/probes/q0-qsam-zero-record-probes
python3 "$PROBE/make-jobs.py" vzero --check
python3 "$PROBE/make-jobs.py" vbzero --check
python3 "$PROBE/make-jobs.py" vzero
bash tools/mvs/submit-jcl workarea/qsam-q0-zero/q0-vzero.jcl
# Review job report before trying VB:
# tools/mvs/dump-report-for-job JOBNUMBER
python3 "$PROBE/make-jobs.py" vbzero
bash tools/mvs/submit-jcl workarea/qsam-q0-zero/q0-vbzero.jcl
```

Each job creates and deletes a private `&&Q0DISK` dataset, compiles and links temporary programs and writes its PASS marker to QOUT. No PDS writes. Check all six RCs and reader output; a static `--check` is **not** an MVS PASS. If the writer fails/abends, capture full JES report and do not treat it as proof that zero payload is forbidden in every MVS setting.
