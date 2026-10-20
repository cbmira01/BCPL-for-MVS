# Milestone QSAM — Q.0 MVS DASD FB/V/VB execution evidence

**Status:** PASS for all three standalone MVS 3.8J/TK5 DASD experiments;
**Q.0 — Reconnaissance & contract remains open.**

**Evidence origin:** Owner-supplied full JES listings for JOBs 2160
and 2161–2162, with MVS job date **20 October 2026**. These are
standalone assembler experiments, not compiled BCPLQSAM calls or
a release acceptance. Job reports remain in the owner's JES/printer
output; the repository stores reproducible source and this concise
evidence summary, not raw printer captures.

## Jobs and step return codes

| Profile | JES job | Test DD | ASMWR | ASMRD | LKWR | LKRD | WGO | RGO |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FB | 2160 `QS0FBD` | `RECFM=FB,LRECL=80,BLKSIZE=800` | 0000 | 0000 | 0000 | 0000 | 0000 | 0000 |
| V | 2161 `QS0VQD` | `RECFM=V,LRECL=100,BLKSIZE=104` | 0000 | 0000 | 0000 | 0000 | 0000 | 0000 |
| VB | 2162 `QS0VBD` | `RECFM=VB,LRECL=100,BLKSIZE=404` | 0000 | 0000 | 0000 | 0000 | 0000 | 0000 |

Both IFOX assemblies in each job reported **no statements flagged**
and **highest severity zero**. The temporary QDISK dataset was
created by `WGO` and reopened for independent reading by `RGO`,
then deleted. All object and load modules were temporary; no
`BOOT_OBJ`, `BOOT_DEVOBJ` or manifest PDS objects changed.

The readers wrote these actual `QOUT` records:

```text
JOB 2160: Q0 FB DASD 23 RECORDS PASS
JOB 2161: Q0 VARIABLE 15 RECORDS PASS
JOB 2162: Q0 VARIABLE 15 RECORDS PASS
```

## Exactly what the tests establish

**FB, JOB 2160:** One assembler program wrote **23** 80-byte
logical records to a temporary FB dataset; an independently linked
program used QSAM GET to read them back. The reader checked the
effective DCB byte for `RECFM=FB`, halfword `BLKSIZE=800`,
and halfword `LRECL=80` after OPEN, plus the record identifier
`Q0FBTEST`, each sequence byte, 70 blank bytes and final `X`.
It reached EODAD only after 23 records. A ten-record block
capacity ensures the record sequence spans multiple disk blocks.

**V, JOB 2161:** The temporary dataset used `RECFM=V`,
`LRECL=100`, `BLKSIZE=104` per JCL. The writer PUT **15**
records, repeating total RDW lengths **16, 36 and 100**. The
reader checked effective DCB LRECL=100 after OPEN, each returned
RDW length, zero in both reserved RDW bytes, the `Q0VRTST!`
marker at byte offset 4, sequence at byte offset 12, and EODAD
after exactly 15 records.

**VB, JOB 2162:** The same two programs and assertions ran
against `RECFM=VB`, `LRECL=100`, `BLKSIZE=404` per JCL.
The successful round trip demonstrates tested QSAM blocked-variable
logical-record deblocking with caller-visible RDWs, not direct BDWs.

**Conservative scope:** The V/VB reader verified actual LRECL, RDW,
identifiers and order; it did **not** independently inspect effective
DCB RECFM/BLKSIZE after OPEN, compare every payload byte, test a
zero-data-length record, or establish maximum legal MVS sizes.
The test writer provided well-formed RDWs. It did not exercise
malformed RDWs, SYNAD, recoverable OPEN failures or retries.

## Reproducible source

- [FB writer](../bootstrap-toolchain/probes/q0-qsam-dasd-probes/fb-write.asm)
  and [FB reader](../bootstrap-toolchain/probes/q0-qsam-dasd-probes/fb-read.asm)
- [V/VB writer](../bootstrap-toolchain/probes/q0-qsam-dasd-probes/v-write.asm)
  and [V/VB reader](../bootstrap-toolchain/probes/q0-qsam-dasd-probes/v-read.asm)
- [JCL generator](../bootstrap-toolchain/probes/q0-qsam-dasd-probes/make-jobs.py)
  and [operator instructions](../bootstrap-toolchain/probes/q0-qsam-dasd-probes/README.md)

This follows the earlier [Q.0 dispatcher ABI evidence](qsam-q0-dispatcher-abi-evidence-20261019.md)
and [FB80 SYSOUT evidence](qsam-q0-fb80-evidence-20261020.md).
All numeric BCPLQSAM protocol values remain governed by the
[public interface specification](bcplqsam-public-interface.md).

## Acceptance boundary

Record **FB/V/VB standalone MVS behavior: PASS**. Do **not**
interpret these standalone results as an implementation of BCPLQSAM,
a production record-size guarantee, a passing native regression panel,
approval of the R.0 registrar, or closure of Q.0.
