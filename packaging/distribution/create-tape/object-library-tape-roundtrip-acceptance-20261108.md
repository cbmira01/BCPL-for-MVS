# Object-library tape round-trip acceptance — 8 November 2026

**Status: ACCEPTED** — bounded, operator-executed FB80 relocatable object-library
tape unload, restoration, binary comparison, and native BCPL smoke execution
on the existing MVS 3.8J/TK5 installation. This is **not** acceptance of a
distribution release, a clean MVS installation, or a RECFM=U load-library
round trip.

## Scope, authority, and evidence quality

The experiment used GitHub `main` implementation commit
`7d02227e675863bee16f88ca27d16ae9d70070ab`, containing JCL `TO01PRE`–`TO04COMP`, the scoped native
object-PDS linker override, and the reviewed
[object-library tape test plan](object-library-tape-test-plan-20261108.md).
The earlier accepted documentation-PDS experiment is recorded in
[scratch-pds-roundtrip-acceptance-20261108.md](scratch-pds-roundtrip-acceptance-20261108.md).

All results below come from the operator's supplied **live** `dspal`,
JES summaries, Hercules console, `hetmap --all`, SHA-256, and native
regression outputs, not mocked unit-test responses. Full JES SYSPRINT
listings and per-step native regression JES job IDs were **not** supplied
for independent inspection. Accordingly, the native smoke-test step RC
details are supported by the regression runner's PASS/RC=0 reports,
not separately quoted IFOX/IEWL/GO job summaries.

| Stage | Real JES job / test | Observed result |
| --- | --- | --- |
| `TO01PRE` | JOB 2483, `COPY` IEBCOPY | RC=0000; eight-object scratch PDS verified |
| `TO02UNLD` | JOB 2486, `UNLOAD` IEBCOPY | RC=0000; standard-labeled BTO001 AWS tape verified |
| `TO03REST` | JOB 2488, `RESTORE` IEBCOPY | RC=0000; eight-object restored PDS verified |
| `TO04COMP` | JOB 2491, `COMPARE` IEBCOMPR | RC=0000, `COMPARE TYPORG=PO` |
| `TO05LINK` | Native bootstrap regression `00` | PASS 1, FAIL 0, SKIP 0; runner RC=0 |
| `TO05LINK` | Native bootstrap regression `03` | PASS 1, FAIL 0, SKIP 0; runner RC=0 |

`TO05LINK` is the test **stage**, not a separate JES JOB name.

## Object-library identities and independent MVS checks

- Production input, **read-only**: `HERC02.BCPL.BOOT.OBJ` (`BOOT_OBJ`).
- Intermediate scratch copy: `HERC02.BCPL.TPOBJ.SRC`; absent before
  creation; inspected after JOB 2483.
- Restored scratch copy: `HERC02.BCPL.TPOBJ.RESTORE`; absent before
  JOB 2488; independently inspected afterward.
- Both scratch PDSes were observed with `DSORG=PO`, `RECFM=FB`,
  `LRECL=80`, `BLKSIZE=800`. The input `BOOT_OBJ` had the same DCB.
- All three inventories contained these eight members:
  `BCPLAPT`, `BCPLBYTE`, `BCPLIO`, `BCPLMAIN`,
  `BCPLMEM`, `BCPLREG`, `BCPLRGS`, `BLIB`.
- `TO04COMP` compared the scratch source and restored PDS, both
  `DISP=SHR`, using MVS IEBCOMPR `COMPARE TYPORG=PO`.
  JOB 2491 returned RC=0000. This is the record-comparison acceptance
  evidence; member inventories alone would not establish equality.
- Source PDS and restored PDS live on the same established TK5 MVS
  installation, not an isolated consumer installation.

## Written AWS tape — labels, physical structure, checksum

- Host image: `mvs-state/tape/bcpl-objtest-20261108-01.aws`
  (under Git-ignored state, **not** committed to Git).
- Emulator: Hercules `3420` at `0:0480`; MVS device `480`.
- Initialization: installed `hetinit -d -i` (v4.9.1.0-SDL);
  new VOLSER `BTO001`, creation RC=0.
- Standard-labeled tape dataset: `HERC02.BCTO01`,
  `LABEL=(1,SL)`, volume sequence `0001`, dataset sequence `0001`.
- `VOL1`: `BTO001`; `HDR1` and `EOF1`: `HERC02.BCTO01`;
  `HDR2` and `EOF2`: `RECFM=V`, block size `00820`,
  logical record length `00816`, block attribute `S`,
  job/step `TO02UNLD/UNLOAD`.
- The tape sequential **IEBCOPY unload format** is variable length;
  it must not be confused with the FB80 source/restored PDS DCB.
- After JOB 2486, `tools/mvs/tape-map --all` (Hercules `hetmap`)
  reported:

  | Physical file | Blocks | Function in observed layout |
  | ---: | ---: | --- |
  | 1 | 3 | 80-byte volume/header label records |
  | 2 | 52 | Sequential IEBCOPY unload data |
  | 3 | 2 | 80-byte EOF label records |
  | 4 | 0 | Terminal empty tape file |

  Total: **4 physical files, 57 blocks, 37,784 uncompressed bytes**.
  `EOF1` block count `000052` agrees with the 52 data blocks
  reported for physical file 2. These are not four distinct
  cataloged MVS datasets.

- SHA-256 recorded **after the unload**, before restoration:

  `30f1766dbb9ae57e06ef822dd533da2131dc568aeeb44e2132a55ad4091700db`

  No second SHA-256 after restoration was supplied; do not infer
  byte-for-byte image immutability after that point from the receipt alone.

## Native execution explicitly bound to the restored PDS

The operator ran the established native regression wrapper twice, with:

```sh
BCPL_TAPE_OBJECT_PDS=HERC02.BCPL.TPOBJ.RESTORE \
    tools/bootstrap/run-production-regression 0 --show-output \
    --log-dir "$PWD/workarea/obj-tape-smoke-20261108"

BCPL_TAPE_OBJECT_PDS=HERC02.BCPL.TPOBJ.RESTORE \
    tools/bootstrap/run-production-regression 3 --show-output \
    --log-dir "$PWD/workarea/obj-tape-smoke-20261108"
```

Both reported `PASS` with wrapper return code `0`. Regression
`00-most-degenerate-bcpl-program` exercises the minimum START/FINISH
lifecycle. Regression `03-single-character-output` verifies the
single-character output contract (expected fixture `A`); the runner
reported PASS, although the underlying GO SYSOUT was not separately
included in the supplied transcript.

The operator then directly inspected **both** generated
`workarea/native-regression/<case>/runtime-pds-go.jcl` files. Each
contained:

```jcl
//OBJ      DD DSN=HERC02.BCPL.TPOBJ.RESTORE,DISP=SHR
 INCLUDE OBJ(BCPLMAIN)
 INCLUDE OBJ(BCPLIO)
 INCLUDE OBJ(BCPLBYTE)
 INCLUDE OBJ(BCPLAPT)
 INCLUDE OBJ(BCPLMEM)
 INCLUDE OBJ(BLIB)
 INCLUDE OBJ(BCPLRGS)
 INCLUDE OBJ(BCPLREG)
```

No production `BOOT.OBJ` fallback or alternate object-library DD
appeared in the supplied selections. This directly establishes the
**linkage input selection**; the regression PASS reports establish
the tested behavior under that selection.

The wrapper's generic banner `NATIVE PRODUCTION REGRESSION: BOOT_OBJ`
does **not** identify the actual IEWL input PDS. The explicitly
inspected `//OBJ DD` in the generated JCL is the relevant provenance
evidence.

## Operational lesson — Hercules runtime file ownership

The first mount attempt failed with Hercules
`HHC00205E ... error in function open(): Permission denied`.
The `hetinit` invocation ran as container root and created the
`BTO001` image `root:root`, mode `0640`. Hercules itself ran as
`ubuntu` (UID/GID 1000). Although MVS later displayed `O`,
Hercules showed `3420 *`: **the tape was not mounted**.

The operator corrected *only the image ownership* through Docker root
`chown 1000:1000 /tk5/tape/bcpl-objtest-20261108-01.aws`
(RC=0), retaining `0640`. On retry Hercules opened the actual AWS
file and `devlist` identified
`/tk5/tape/bcpl-objtest-20261108-01.aws [1:00000000] IO[0] open`;
MVS `D U,TAPE` showed unit 480 `O` (ready).
After the successful unload, Hercules showed `3420 *` and MVS
`O-NRD`; the operator remounted the **same written image** for
restoration without reinitializing it.

For a future **new** image, initialize as the Hercules UID/GID
(e.g., `docker exec -u 1000:1000 mvs38j hetinit ...`) after checking
the actual runtime identity. Never repeat `hetinit` against a
written evidence tape.

## Offline tooling and remaining limits

The operator pulled Git commit `7d02227e675863bee16f88ca27d16ae9d70070ab` and ran:

```sh
python3 -B -m unittest discover \
    -s packaging/distribution/create-tape/tests -p 'test_*.py' -v
```

Result: **26 tests, OK, RC=0**. Mock JOB 42 and JOB 99 output in those
unit tests is *not* live MVS evidence; the real experiment uses
JOBS 2483, 2486, 2488, 2491 and the two real regression executions.

**Accepted scope:** MVS 3.8J IEBCOPY preserved a PDS of eight FB80
relocatable object members through a single-dataset BTO001 AWS
tape unload/restore; MVS IEBCOMPR RC=0; the native runner compiled,
linked, and executed two existing BCPL regression cases using objects
selected exclusively from the restored PDS.

**Not established:** multi-dataset tape sequencing, IEBGENER
bootstrap/documentation first file, `RECFM=U` executable load-library
transfer and execution, a tape-only installer, restore on a separately
clean MVS installation, comprehensive source/release manifest,
negative fault/recovery testing, or a complete Cambridge BCPL
Programming System production distribution.

This acceptance closes **only the bounded object-library experiment**.
It opens or closes **no official project milestone or march**.
Any new JES submission, media mount/initialization, permanent PDS write,
dataset deletion, or release publication requires its own approval.
