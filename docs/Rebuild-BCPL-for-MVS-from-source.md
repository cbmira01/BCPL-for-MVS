# Rebuild BCPL for MVS from source

Use this guide to rebuild the supported BCPL programming environment on a dedicated Hercules/TK5 MVS 3.8J system. Run all commands from the Git repository root.

The rebuild creates the `ICINT19` interpreter, the interpreter-hosted Cambridge Compiler (`CAMBCOMP`), the native Core Runtime, historical `BLIB`, native coroutine support (`BCPLCO` and `COROUTIN`), and the installed System Extensions (`BCPLDEMO`, `BCPLTIME`, and `BCPLQSAM`). **It does not build the separately planned native-running Cambridge Compiler.**

## 1. Check before starting

**Warning: This procedure deletes data.** It clears the managed `workarea/` contents and deletes and recreates the BCPL MVS datasets selected by the effective `dspal` configuration, including installed object libraries. It does not recreate TK5 itself or erase the MVS system datasets.

Save any needed output first. Make sure no other user or job is working in the managed BCPL datasets. Check the Git working tree and the exact target datasets:

```sh
git status --short
tools/datasets/dspal info
tools/datasets/dspal purgebcpl --show-jcl
```

Review the high-level qualifier, the proposed delete list, and any local changes **before** continuing. The rebuild driver will also run `git pull --ff-only` and start TK5 if needed.

## 2. Run the rebuild

**Recommended: interactive rebuild**

```sh
tools/reconstruction/rebuild-from-source
```

Follow the on-screen prompts:

| Prompt | Action |
| --- | --- |
| `hit ENTER to continue` | Review the previous step, then press Enter. |
| `DELETE` | Confirm removal of managed `workarea/` contents. |
| `YES` | Confirm deletion of the listed BCPL MVS datasets. |
| System Extension checkpoint | Check the JES job results and read-back comparison before pressing Enter. |

**Unattended rebuild — only after authorizing the full deletion and rebuild:**

```sh
tools/reconstruction/rebuild-from-source --unattended --batch-populate
```

`--unattended` skips all confirmation prompts and authorizes the destructive steps for that invocation. `--batch-populate` groups source-member transfers into fewer MVS jobs; it is optional and can also be used in interactive mode.

## 3. What the driver does

| Driver step | Operation |
| --- | --- |
| 0 | Check Git, configuration and MVS availability. |
| 1 | Clear the managed host work area. |
| 2 | Recreate the managed BCPL datasets and install Git-tracked sources. |
| 3 | Assemble and run `ICINT19`. |
| 5 | Generate and install the Cambridge bootstrap inputs. |
| 6 | Rebuild `CAMBCOMP`; compile and stage the coroutine library source. |
| 7 | Build the seven initial Core Runtime/registration objects. |
| 8 | Install `BLIB`, `BCPLCO`, and `COROUTIN`; verify the ten production objects and run the installed-coroutine check. |
| 9 | Install `BCPLDEMO`, `BCPLTIME`, and `BCPLQSAM`. |

The driver prints each command's return code. **It always starts at step 0 and cannot resume after a failure.** It does not run the complete regression campaign.

## 4. Confirm the build

The run should end with `REBUILD COMMANDS COMPLETED` and no failed command. Look for the ten-member `BOOT_OBJ` verification and the successful installed-coroutine application check.

To check the object libraries again:

```sh
python3 -B tools/reconstruction/verify-boot-obj.py
tools/datasets/dspal ls EXT_OBJ
```

`BOOT_OBJ` must contain exactly these ten members:

| Core Runtime and registration | Base Library | Coroutines |
| --- | --- | --- |
| `BCPLMAIN` | `BLIB` | `BCPLCO` |
| `BCPLMEM` | | `COROUTIN` |
| `BCPLBYTE` | | |
| `BCPLAPT` | | |
| `BCPLIO` | | |
| `BCPLRGS` | | |
| `BCPLREG` | | |

`EXT_OBJ` should contain `BCPLDEMO`, `BCPLTIME`, and `BCPLQSAM`. Review the three installation JES jobs for zero return codes, zero IFOX severity, and successful `IEBCOMPR` verification.

## 5. Run the supported regressions

This is a **separate operation**. The command below submits MVS jobs. `--allow-device` also authorizes the BCPLQSAM printer and punch tests; obtain explicit permission before using it.

```sh
tools/tests/run-project-regressions --check

tools/tests/run-project-regressions \
    --run \
    --suite mr10 \
    --suite mr10-coroutines-supported \
    --suite bootstrap \
    --suite runtime-extensions \
    --suite bcpltime \
    --suite bcplqsam \
    --suite coroutines \
    --suite coroutine-contract \
    --profile production \
    --allow-device \
    --progress
```

A successful campaign reports `PROJECT REGRESSION RESULT: PASS`. The last accepted campaign recorded **208 PASS, 0 FAIL, 0 BLOCKED and 1 expected SKIP (083)**. Check the results of your own run; do not substitute this earlier result. The coordinator saves a `summary.json` and supporting logs under `workarea/project-regressions/`.

## If something fails

Stop at the first error. Read the failing command and its JES job report before taking action. Do not treat a partially rebuilt object library as complete. After fixing the problem, rerun `tools/reconstruction/rebuild-from-source` **from the beginning**; it will clear and recreate the managed data again.

For manual build commands and detailed operator checks, see [Manual reconstruction steps for maintainers](Manual-Rebuild-BCPL-for-MVS.md). For tool syntax and diagnostics, see [Project Tools](Guide-to-Project-Tools.md) and [the test runner guide](../tools/tests/README.md).
