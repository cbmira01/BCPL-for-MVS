# Milestone QSAM — March Q.0 candidate 1024-byte stage probes

**Status:** locally source/JCL checked; **not run on MVS**. These are
independent IFOX/IEWL experiments, not production `BCPLQSAM`, not public
`QSAMSVC:200` and not an approved BCPLQSAM size ceiling.

## What the profiles prove if they pass on MVS

| Profile | Job | Dataset / experiment | PASS marker |
| --- | --- | --- | --- |
| `v` | `QS0C102V` | V, effective LRECL=1024, BLKSIZE=1028 | `Q0 V1024 RDW4/16/1024 BINARY 15 PASS` |
| `vb` | `QS0C10VB` | VB, effective LRECL=1024, BLKSIZE=2052 | `Q0 VB1024 RDW4/16/1024 BINARY 15 PASS` |
| `stage16` | `QS0S16` | 16 simultaneous conditional GETMAIN areas of 1024 bytes | `Q0 16 STAGES 1024 GETMAIN FREEMAIN PASS` |

V/VB jobs independently assemble writer and reader, link separately,
write and read 15 records through a temporary `&&Q0CEIL` dataset and
check EODAD. Each profile uses five RDW-only records (total length 4),
five short records (total 16), and five full records (total 1024).
The reader verifies opened DCB RECFM, LRECL, BLKSIZE, RDW length and
zero reserved bytes, record order, and the **complete 1020 data bytes**
for every full record, including binary `X'00'` and `X'FF'` across
byte boundaries. It checks the exact 1024-byte QSAM move-mode area.

The `stage16` job allocates 16 separately owned 1024-byte MVS areas,
checks first/last sentinels after all 16 are live, then frees them and
checks exact acquisition/release counts. Failed requests use a
pointer-guarded drain; an unexpected outcome returns RC=8. It does
**not** OPEN 16 DCBs, account for QSAM block buffers, or prove
16 production BCPLQSAM handles fit under `REGION=256K`.

A candidate 1024-byte *total private stage* permits F/FB 1024-byte
logical data or V/VB at most 1020 data bytes (four RDW bytes private).
These tests are a prerequisite to, **not approval of**, that policy.

## Running the tests

From the repo root, after the source is available on GitHub `main`:

```sh
PROBE=bootstrap-toolchain/probes/q0-qsam-ceiling-probes
for profile in v vb stage16; do
    python3 "$PROBE/make-ceiling-jobs.py" "$profile" --check
    python3 "$PROBE/make-ceiling-jobs.py" "$profile"
    bash tools/mvs/submit-jcl "workarea/qsam-q0-ceiling/q0-ceiling-${profile}.jcl"
done
# Capture returned JOB numbers; for each:
tools/mvs/dump-report-for-job JOBNUMBER
```

Expected V/VB results: ASMWR, ASMRD, LKWR, LKRD, WGO and RGO at RC=0000.
Expected stage16 results: ASM, LKED and GO at RC=0000. Verify the
individual PASS marker; the parser must not confuse the assembler's
source listing PASSREC constant with an actual QOUT record.

`--check` does not load credentials or write JCL. Normal generated
JCL is mode 0600 in ignored `workarea/`, can contain JOB credentials,
and must never be committed. JCL uses temporary `&&` datasets only;
accepted `BOOT_OBJ`, `BOOT_DEVOBJ`, compiler and runtime are unchanged.

**March Q.0 remains open. Q.1 has not started.**
