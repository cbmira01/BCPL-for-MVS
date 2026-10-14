# Build ICINT19 on MVS

`ICINT19` interprets BCPL INTCODE. Its source is `asm/icintv19.asm`, stored on MVS as `MR10_ASM(ICINT19)`.

| Build step | Tool | Result |
| --- | --- | --- |
| ASM | IFOX00 | Relocatable object |
| LKED | IEWL | `MR10KIT.LOAD(ICINT19)` |
| SAVEOBJ | IEBGENER | `MR10KIT.OBJ(ICINT19)` |

## Build

From the repository root:

```sh
git pull --ff-only
tools/dspal put MR10_JCL IC19BLD mr10-kit-compiler/jcl/build-icintv19.jcl
tools/dspal submit MR10_JCL IC19BLD
tools/dspal ls MR10_LOAD
tools/dspal ls MR10_OBJ
```

The stored JCL has no JOB card. Use `dspal submit`, not `submit-jcl`.

## Check

The assembly, link-edit, and object-copy steps must each return RC=0000. Then run a separate ICINT19 test. Building the load module does **not** prove the interpreter works.

An earlier installation was verified by its step results and installed load-module listing. JES job numbers are not stable evidence because they wrap. The `asm/CURRENT` host-tool default is independent of the installed MVS version.
