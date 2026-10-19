# Q.0 — MVS 3.8 QSAM fixed/blocked record behavior probe

**Status:** **PASS** on MVS/TK5, JOB 2159 (MVS job date 20 October 2026).
This is an isolated MVS assembler experiment, not the BCPLQSAM package.

## What it establishes, if successful

- A test-only S/370 program using the installed IFOX assembler and IEWL
  links and runs without the BCPL runtime, compiler, or G!200.
- `OPEN` for a JCL-allocated FB80 input stream (`QIN`) and an FB80
  JES SYSOUT stream (`QOUT`) using ordinary QSAM DCBs.
- QSAM move-mode `GET` (MACRF=GM) supplies **one logical record at a time**.
- Two 80-byte records have the exact prefixes, trailing blanks, and final
  nonblank bytes `X` and `Y` entered in the input JCL.
- `PUT` (MACRF=PM) copies those complete logical records to QOUT.
- QSAM transfers control to the `EODAD` label after the last record;
  the program requires exactly two records and returns RC0, or RC8 for
  a content/count mismatch.
- On successful execution, QOUT should show two records with prefixes
  `Q0FIX001` and `Q0FIX002`, trailing `X` and `Y` at column 80.

This is a **first behavior probe**: it does not prove variable-format
RDW handling, duplicate OPEN restrictions, unallocated DD handling,
read-ahead/staging, buffer-too-small retries, or every failure mode.

## Reproduce

With a running Hercules/TK5 environment, from the checkout root:

```sh
bash bootstrap-toolchain/probes/q0-qsam-fb80-probe/run-q0-fb80.sh
```

The script writes the **generated, local-only** (possibly credential-bearing)
JCL to `workarea/qsam-q0-fb80/qs0-fb80.jcl` and submits it through the
existing JES card-reader tool. No permanent MVS PDS member is created or
replaced. All IFOX/IEWL output and the load module are temporary.

Inspect the job number returned by the script:

```sh
tools/mvs/job-summary JOBNUMBER --max-rc 0
tools/mvs/dump-report-for-job JOBNUMBER
```

Expected step sequence: ASM 0000, LKED 0000, GO 0000. The QOUT SYSOUT should
show two records. A failure at OPEN may abend rather than return RC8: this
probe deliberately does **not** claim QSAM exception recovery.

**Observed PASS:** JOB 2159 (ASM/IFOX RC=0000, LKED/IEWL RC=0000,
GO RC=0000; zero assembler errors) emitted the two exact QOUT records.
The preceding JOB 2158 was rejected by JES (IEF652I and IEF605I),
before assembly, due to a DD DATA DCB conflict and missing continuation
comma. The generator in Git now matches the fixed JOB 2159 configuration.
See the [evidence record](../../../packaging/qsam-q0-fb80-evidence-20261020.md).

The test does **not** independently prove QIN's effective RECFM or
BLKSIZE, nor does its SYSOUT output demonstrate blocked DASD deblocking.
That is the purpose of the subsequent
[DASD probes](../q0-qsam-dasd-probes/README.md).

## Evidence basis

- Current native `bootstrap-toolchain/asm/bcplio.asm` uses
  `DCB ... MACRF=GM/EODAD`, `GET DCB,AREA`, `DCB ... MACRF=PM`,
  `PUT DCB,AREA`, `OPEN`, and `CLOSE` under the same MVS 3.8J system.
- OS/VS2 MVS Release 3.8 Data Management Macro Instructions, IBM
  GC26-3873-0 (March 1979), sections GET/PUT QSAM, available at
  [Bitsavers](https://www.bitsavers.org/pdf/ibm/370/OS_VS2/Release_3.8_1978/GC26-3873-0_OS_VS2_MVS_Data_Management_Macro_Instructions_Rel_3.8_Mar79.pdf).

## Scope boundary

This does not modify BCPLMAIN, BCPLIO, BOOT_OBJ, BOOT_DEVOBJ, the
Global Number Registry, the Runtime Extensions registrar, or the
BCPLQSAM public contract. It creates no persistent object module.
