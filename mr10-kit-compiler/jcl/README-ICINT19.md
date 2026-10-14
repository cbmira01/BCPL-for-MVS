# ICINTv19 persistent MR10KIT installation

The canonical stored JCL body is `mr10-kit-compiler/jcl/build-icintv19.jcl`, mapped by dspal as `MR10_JCL(IC19BLD)` to `HERC02.BCPL.MR10KIT.JCL(IC19BLD)`.

The body intentionally has **no JOB statement**: `tools/dspal submit MR10_JCL IC19BLD` generates an authenticated JOB card before forwarding the stored member through JES INTRDR. Do not submit the bare body using `tools/submit-jcl`.

The procedure assembles `MR10KIT.ASM(ICINT19)` with IFOX00 into a temporary FB80 deck, link-edits with IEWL entry `ICINT` and `NAME ICINT19(R)` into `MR10KIT.LOAD`, then copies the relocatable object to `MR10KIT.OBJ(ICINT19)` only after successful assembly and link-edit. No interpreter program is run by this installation job; a subsequent smoke test is required.

## Operator commands

```sh
git pull --ff-only
tools/dspal put MR10_JCL IC19BLD mr10-kit-compiler/jcl/build-icintv19.jcl
tools/dspal ls MR10_JCL
tools/dspal submit MR10_JCL IC19BLD --show-jcl
tools/dspal submit MR10_JCL IC19BLD
tools/dspal ls MR10_OBJ
tools/dspal ls MR10_LOAD
```

Inspect the payload build-job report and verify ASM/LKED/SAVEOBJ RC=0000 before accepting the installed object and load module. If these fail, do not claim installation success. Verify a separate `EXEC PGM=ICINT19` with `STEPLIB DD DSN=HERC02.BCPL.MR10KIT.LOAD,DISP=SHR` and suitable interpreter INTCODE input.

Do not change `mr10-kit-compiler/asm/CURRENT` (still ICINTv17). Installing V19 does not promote its runtime/semantic baseline. The old `HERC02.BCPL.LOAD` library is preserved.

This procedure is committed in Git. Executing `dspal put` and `dspal submit` requires the user's Hercules host; it has not been run through the repository connection.
