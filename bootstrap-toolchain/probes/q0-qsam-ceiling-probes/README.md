# Milestone QSAM — March Q.0 candidate 1024-byte stage probes

**Status:** **PASS on MVS 3.8J/TK5, 20 October 2026** (JOBs 2180,
2181 and 2182). These are independent IFOX/IEWL experiments, not
production `BCPLQSAM` or public `QSAMSVC:200`. The owner subsequently
**approved a 1024-byte total private stage per handle** as an initial
BCPLQSAM design limit, not a universal MVS record maximum.

## Executed Q.0 probe profiles

| Profile | Job | Dataset / experiment | PASS marker |
| --- | --- | --- | --- |
| `v` | `QS0C102V` (JOB 2180) | V, effective LRECL=1024, BLKSIZE=1028 | `Q0 V1024 RDW4/16/1024 BINARY 15 PASS` |
| `vb` | `QS0C10VB` (JOB 2181) | VB, effective LRECL=1024, BLKSIZE=2052 | `Q0 VB1024 RDW4/16/1024 BINARY 15 PASS` |
| `stage16` | `QS0S16` (JOB 2182) | 16 simultaneous conditional GETMAIN areas of 1024 bytes | `Q0 16 STAGES 1024 GETMAIN FREEMAIN PASS` |

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
The owner **approved** that initial stage policy after JOBs 2180–2182;
see [the MVS execution evidence](../../../packaging/qsam-q0-1024-byte-stage-evidence-20261020.md).
Neither the public BCPLQSAM implementation nor sixteen complete OPEN
QSAM handles have been verified.

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

Observed V/VB results: ASMWR, ASMRD, LKWR, LKRD, WGO and RGO each
RC=0000 in JOBs 2180/2181. Observed stage16 results: ASM, LKED and
GO each RC=0000 in JOB 2182. The actual QOUT PASS markers appeared.
Keep testing the markers as output records, not merely the assembler
listing's PASSREC constants.

**JOB-card padding fix:** The original generator's `stage16 --check`
passed but normal generation rejected the authenticated `QS0S16  JOB`
card, because it expected the word JOB after exactly one name-space.
The owner ran JOB 2182 using an ignored-`workarea` deck generated
through a one-time workaround. The generator now checks the full
eight-column job-name field and constructs identically padded
`--check` cards, so both paths handle six- and eight-character names.

`--check` does not load credentials or write JCL. Normal generated
JCL is mode 0600 in ignored `workarea/`, can contain JOB credentials,
and must never be committed. JCL uses temporary `&&` datasets only;
accepted `BOOT_OBJ`, `BOOT_DEVOBJ`, compiler and runtime are unchanged.

**March Q.0 remains open. Q.1 has not started.**
