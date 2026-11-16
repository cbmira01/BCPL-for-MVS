# Manual rebuild steps for BCPL maintainers

Use this reference when you need to run the MVS reconstruction **one command at a time**. For routine rebuilding, use the shorter [Rebuild BCPL for MVS from source](Rebuild-BCPL-for-MVS-from-source.md) guide and its automated driver.

These commands reproduce the current `tools/reconstruction/rebuild-from-source` sequence on GitHub `main`. They build the interpreter-hosted Cambridge Compiler, the native application runtime, BLIB, and the native coroutine modules. **They do not build the separate native-running Cambridge Compiler.**

**Warning:** Steps 1 and 2 delete the host's managed `workarea/` content and the BCPL datasets selected by your effective `dspal` configuration. Review the deletion list, back up anything needed, and confirm no other operator is using those datasets. A partially completed manual build is not an installed production baseline.

Run commands from the repository root. Check each command and its MVS payload before proceeding. Manual commands do **not** automatically provide the automated driver's stop-on-error protection.

## Step 0 — Check Git, MVS and sources

```sh
git status --short
git pull --ff-only
git rev-parse HEAD
tools/mvs/start-tk5 --detached
tools/datasets/dspal status --probe
tools/datasets/dspal info
tools/bootstrap/prepare-bootstrap --check-inputs
```

Check the Git revision and effective MVS target. Stop if any source is missing or the target is not the intended system. Do not publish passwords from local configuration.

## Step 1 — Clean the managed work area

```sh
tools/clean-workarea
git status --short
```

Review the removal list. Type `DELETE` only if the contents may be erased. The tool keeps `workarea/.gitignore`.

## Step 2 — Recreate and populate the BCPL datasets

```sh
tools/datasets/dspal purgebcpl --show-jcl
tools/datasets/dspal purgebcpl
tools/datasets/dspal initbcpl --show-jcl
tools/datasets/dspal initbcpl
tools/datasets/dspal stat
tools/datasets/dspal populate all --dry-run
tools/datasets/dspal populate all
tools/datasets/dspal ls
```

Inspect the exact delete list before typing `YES`. The first population normally reports **RC=2** because exactly **12 generated bootstrap members** do not yet exist. Verify that the tool reports those 12 missing generated members **and** the Git-backed members installed successfully. Any other RC=2 or missing tracked input is a failure; do not continue.

For fewer JES submissions, use `tools/datasets/dspal populate all --batch` instead of the unbatched installation command. Batch mode is optional; it does not change what sources are installed.

## Step 3 — Build and check ICINT19

```sh
tools/datasets/dspal submit MR10_JCL IC19BLD
tools/datasets/dspal ls MR10_LOAD
tools/datasets/dspal ls MR10_OBJ
tools/mr10/compile-and-run --installed-icint MR10_LOAD --results \
    mr10-kit-compiler/tests/00-regression-panel/data-movement/scalar-vector.bcpl
```

Inspect the **payload** job, not just the `dspal` launcher. Require successful assembler, linker and object-save steps, and interpreted completion `CODE=0` in the sample execution.

## Step 5 — Create and install compiler bootstrap inputs

```sh
tools/bootstrap/prepare-bootstrap --with-trnilrg
cat workarea/bootstrap-cambridge/prepare-bootstrap-manifest.json
tools/datasets/dspal populate all --generated-only --dry-run
tools/datasets/dspal populate all --generated-only
tools/datasets/dspal ls BOOT_SOURCE
tools/datasets/dspal ls BOOT_INTCODE
```

Require `trnilrg_rebuilt` to be true in the generated manifest and the second population to finish at **RC=0**. This population writes the generated members; it does not replace tracked inputs. For optional batched installation, add `--batch` to the non-dry-run generated-only population command.

## Step 6 — Build CAMBCOMP and prepare COROUTIN

```sh
tools/datasets/dspal submit BOOT_JCL CAMBBLD
tools/datasets/dspal ls BOOT_INTCODE

tools/bootstrap/compile-mvs \
    tests/bootstrap/00-most-degenerate-bcpl-program/source.bcpl \
    --output workarea/m3-clean-smoke.s370.asm
test -s workarea/m3-clean-smoke.s370.asm

tools/bootstrap/compile-mvs \
    bootstrap-toolchain/library/coroutines.bcpl \
    --job-name COPRLCMP \
    --cambridge-parm \
        packaging/milestones/coroutines/candidates/co3-delete-reuse/cambridge-parm.txt \
    --output workarea/co5-production/coroutines-generated.asm

python3 -B tools/coroutines/prepare-production-library.py \
    --compiled workarea/co5-production/coroutines-generated.asm \
    --output workarea/co5-production/coroutin-prepared.asm
test -s workarea/co5-production/coroutin-prepared.asm

tools/datasets/dspal put BOOT_ASM COROUTIN \
    workarea/co5-production/coroutin-prepared.asm
```

Require `CAMBCOMP` to be present in `BOOT_INTCODE` and the compiler's interpreted phases to complete successfully. The coroutine library is compiled from Git-backed BCPL source, prepared as IFOX cards and staged as `BOOT_ASM(COROUTIN)`. **Do not copy a prior installed coroutine object into the new library.**

## Step 7 — Build the initial runtime and registration objects

```sh
tools/datasets/dspal ls BOOT_ASM
tools/datasets/dspal ls BOOT_JCL
tools/datasets/dspal ls BOOT_OBJ
tools/datasets/dspal submit BOOT_JCL BLDBMAIN
tools/datasets/dspal ls BOOT_OBJ
```

The fresh `BOOT_OBJ` must now contain seven members: `BCPLMAIN`, `BCPLMEM`, `BCPLBYTE`, `BCPLAPT`, `BCPLIO`, `BCPLRGS` and `BCPLREG`. Inspect all IFOX and installation steps in the payload job.

## Step 8 — Install BLIB and the two coroutine objects

```sh
tools/datasets/dspal submit BOOT_JCL BLIBBLD
tools/datasets/dspal submit BOOT_JCL BLDCORCO
tools/datasets/dspal submit BOOT_JCL BLDCORLB

python3 -B tools/reconstruction/verify-boot-obj.py
python3 -B tools/coroutines/verify-installed-production.py --run
tools/datasets/dspal ls BOOT_DEVOBJ
```

Require `BOOT_OBJ INVENTORY PASS: 10 exact production members` and the installed-coroutine application's success. The ten objects are:

| Core Runtime / registration | Base Library | Coroutine support |
| --- | --- | --- |
| `BCPLMAIN`, `BCPLMEM`, `BCPLBYTE` | `BLIB` | `BCPLCO` |
| `BCPLAPT`, `BCPLIO`, `BCPLRGS`, `BCPLREG` | | `COROUTIN` |

The installed-object test must compile, link and run against `BOOT_OBJ`; it must not silently substitute `BOOT_DEVOBJ` candidates. Confirm the assembler, object installation, readback and comparison results in the three payload jobs.

## Step 9 — Install the System Extensions

```sh
tools/datasets/dspal ls

tools/datasets/dspal submit BOOT_JCL BCPLDEMO
tools/datasets/dspal submit BOOT_JCL BCPLTIME
tools/datasets/dspal submit BOOT_JCL BCPLQSAM

tools/datasets/dspal ls EXT_OBJ
```

Submit each extension job **separately**. Inspect its payload before submitting the next: all expected step return codes are zero, IFOX severity is zero, and `IEBCOMPR` readback verification succeeds. `EXT_OBJ` must include `BCPLDEMO`, `BCPLTIME` and `BCPLQSAM`.

## Finish and recover

Run the supported regression campaign using the [main rebuild guide](Rebuild-BCPL-for-MVS-from-source.md#5-run-the-supported-regressions). The manual build commands above do not run it.

If a build command fails, stop and inspect the exact JES payload job. Do not continue with a mixture of missing and installed objects. The supported recovery method is to correct the issue and start a **new complete rebuild** from Step 0, including the destructive steps after renewed authorization.

For command reference and job-report tools, see [Guide to Project Tools](Guide-to-Project-Tools.md). The dataset-to-source map is `config/dspal.yaml`; GitHub remains authoritative for the source and JCL.
