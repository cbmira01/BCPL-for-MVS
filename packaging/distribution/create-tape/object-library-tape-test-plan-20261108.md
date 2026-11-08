# Object-library tape round-trip — reviewed design (8 November 2026)

**Status:** Historical reviewed design, subsequently **executed and accepted as a bounded test**
on 8 November 2026; see [object-library tape round-trip acceptance](object-library-tape-roundtrip-acceptance-20261108.md).
This plan is not blanket authorization for further JES, tape, or resident dataset
operations, nor an official milestone closure. Based on accepted TP01PRE–TP04COMP
FB80 documentation round-trip.

## Boundaries and identities

- Source (read-only): `HERC02.BCPL.BOOT.OBJ` — accepted binary FB80 objects.
- Scratch source: `HERC02.BCPL.TPOBJ.SRC` — must not exist first.
- Scratch restoration: `HERC02.BCPL.TPOBJ.RESTORE` — must not exist first.
- New tape dataset: `HERC02.BCTO01`, `LABEL=(1,SL)`, VOLSER `BTO001`.
- New AWS filename: `mvs-state/tape/bcpl-objtest-20261108-01.aws`.
- Observed Hercules drive `0480`, MVS unit `480` (verify again before use).
- Preserve the accepted first-run tape `BTP001` and `bcpl01.aws` untouched.
- Expected source and restored PDS DCB: `DSORG=PO,RECFM=FB,LRECL=80,BLKSIZE=800`.
- Expected eight members (verify current live inventory): `BCPLMAIN`, `BCPLIO`,
  `BCPLMEM`, `BCPLBYTE`, `BCPLAPT`, `BCPLRGS`, `BCPLREG`, `BLIB`.

## Execution order and acceptance evidence

| Stage | Job or harness | Required evidence |
| --- | --- | --- |
| `TO01PRE` | IEBCOPY read-only `BOOT.OBJ` -> new `TPOBJ.SRC` | utility RC=0; eight members; PDS DCB |
| `TO02UNLD` | IEBCOPY unload `TPOBJ.SRC` -> new BTO001 file 1 | RC=0; AWS labels; dataset name; HETMAP; checksum |
| `TO03REST` | IEBCOPY BTO001 -> new `TPOBJ.RESTORE` | RC=0; eight restored members; PDS DCB |
| `TO04COMP` | IEBCOMPR `COMPARE TYPORG=PO` | RC=0; compare report reviewed |
| `TO05LINK` | Existing native production regression cases **00 and 03** | both Cambridge compile, IFOX, IEWL and GO PASS; case 03 outputs `A` |

`TO05LINK` names the test **stage**, not a newly invented MVS JOB name.
The existing harness uses its established compiler and runtime regression
JES job names (for example, the case 00 and 03 RG jobs). This prevents
a competing BCPL compiler, linker or execution implementation.

## Operator gating (one stage at a time)

1. Check pinned Git revision, working-tree status and effective MVS identity.
   Confirm no `HERC02.BCPL.TPOBJ.SRC` or `.RESTORE` exists with
   `tools/datasets/dspal stat`. If either exists, stop. Confirm eight
   existing binary objects with `tools/datasets/dspal ls BOOT_OBJ` and
   DCB with `tools/datasets/dspal stat BOOT_OBJ`.
2. Preview each JCL with `packaging/distribution/create-tape/scripts/submit-scratch-job TO01PRE`
   (and `TO02UNLD`, `TO03REST`, `TO04COMP`). The preview redacts the
   batch password. Actual `--run` requires exact typed confirmation for
   **each job**. Do not submit until separately authorized.
3. Execute `TO01PRE` only when both scratch targets are absent.
   Require IEBCOPY RC=0000, eight members and FB80 attributes.
4. After separate media authorization, check drive idle and MVS `O-NRD`.
   Create a **new** AWS image with installed Hercules `hetinit -d -i`
   using VOLSER BTO001 as the actual Hercules runtime user. Check
   `tools/mvs/tape-map` for the new volume label. Do not reuse or
   reinitialize a written tape. Mount using `tools/mvs/mvs-console tape mount`
   with typed YES and verify both Hercules and MVS drive status.
5. Execute `TO02UNLD`; require IEBCOPY RC=0000. MVS may automatically
   unmount media on close; inspect drive state and output with
   `tools/mvs/tape-map --all bcpl-objtest-20261108-01.aws` (only after
   the writer has closed). Verify VOLSER BTO001 and HERC02.BCTO01
   dataset/EOF labels and record the image checksum.
6. Verify the restored target still does not exist. Check idle drive,
   remount the **same** BTO001 image if it was unloaded, and execute
   `TO03REST` once. Require RC=0000, full inventory and DCB.
7. Execute `TO04COMP` only after independent restore inventory checks.
   Require IEBCOMPR RC=0000 and inspect SYSPRINT.
8. **Only after TP04-style equality evidence**, explicitly authorize
   native execution of the two bounded `TO05LINK` smoke regressions.
   Do not run a broad panel with the tape override.

## TO05LINK native link and execution verification

The existing JCL generator is modified to accept **only** the opt-in
environment variable `BCPL_TAPE_OBJECT_PDS=HERC02.BCPL.TPOBJ.RESTORE`.
It rejects any other override, any other test ID than `00` or `03`,
non-production library/candidate profiles and R.1 acceptance mode.
With the override absent, normal production JCL is unchanged.

After separately authorizing MVS jobs, run **one case at a time**:

```sh
BCPL_TAPE_OBJECT_PDS=HERC02.BCPL.TPOBJ.RESTORE \
  tools/bootstrap/run-production-regression 0 --show-output \
  --log-dir "$PWD/workarea/obj-tape-smoke-20261108"

BCPL_TAPE_OBJECT_PDS=HERC02.BCPL.TPOBJ.RESTORE \
  tools/bootstrap/run-production-regression 3 --show-output \
  --log-dir "$PWD/workarea/obj-tape-smoke-20261108"
```

Inspect the actual generated `workarea/native-regression/00-*/runtime-pds-go.jcl`
and `03-*/runtime-pds-go.jcl` prior to interpreting success. Each must
contain `//OBJ DD DSN=HERC02.BCPL.TPOBJ.RESTORE,DISP=SHR`
(normal JCL spacing applies), **never** `BOOT.OBJ`, `DEVOBJ`, or other
object-PDS DDs. Each must include all eight objects via `INCLUDE OBJ(...)`.
Require the actual JES compiler, IFOX/ASMAP, IEWL/LKED and GO RC=0000,
and the expected `A` output of case 03. Preserve the full reports.

Failures or timeouts are not permission to retry tape writes or restart
the workflow. Do not modify accepted production objects or remove
scratch datasets except by a separately authorized cleanup operation.

## Offline tests

```sh
python3 -B -m unittest discover \
  -s packaging/distribution/create-tape/tests -p 'test_*.py' -v
```

The object-tape tests verify JCL structure, submission confirmation,
and the JCL generator's scoped override behavior without using JES.

## Limits

This test is about FB80 relocatable object library preservation and
subsequent linkage/execution on the **same TK5 installation**. It does
not validate `RECFM=U` load libraries, multiple tape files, clean
MVS installation, or production distribution tape readiness.
