# Bootstrap toolchain tools

Established entry points for the interpreter-hosted bootstrap compiler,
its native-code output, and the regression suite:

- `prepare-bootstrap`: reconstruct disposable bootstrap input files.
- `BOOT_JCL(CAMBBLD)`: authoritative M3 resident compiler build job, sourced from `bootstrap-toolchain/jcl/cambbld.jcl`.
- `compile-mvs`: compile BCPL using the installed resident Cambridge compiler.
- `BOOT_JCL(BLIBBLD)`: build the BLIB relocatable object module using `bootstrap-toolchain/jcl/blibbld.jcl`.
- `run-regression`: run the native regression panel.
- `capture-writef-cg370`: capture CG370 diagnostics.

The `NATIVE_*` and `MR10_*` dataset names remain in use by this bootstrap
toolchain. The `CAMB_*` names belong to the separate native compiler work
in `cambridge-compiler/`.

## Current complete BOOT_OBJ clean-room runtime

The operator-requested target is a six-member native production
object library: `BCPLMAIN`, `BCPLIO`, `BCPLMEM`,
`BCPLBYTE`, `BCPLAPT`, and `BLIB`.
The canonical `BOOT_JCL(BLDBMAIN)` builds the five assembler
modules and `BOOT_JCL(BLIBBLD)` compiles/assembles BLIB.
Run `tools/bootstrap/run-production-regression 0 145` only
after fresh binary rebuilds and member-inventory checks.
This profile uses `OBJ` exclusively, with no `DEVOBJ` objects;
its end-to-end result is pending operator execution.
See [the current reconstruction runbook]
(../../packaging/clean-room-mvs-reconstruction.md).

## Historical M5.4 dynamic runtime DEVOBJ candidate

After an **approved** base M3 compiler/OBJ reconstruction,
the current M5 native stream candidate consists of
`BOOT_DEVOBJ(BCPLM6)` and
`BOOT_DEVOBJ(BCPLIO)`, assembled via
`BOOT_JCL(BLDDEVM6)` and
`BOOT_JCL(BLDDEVI)`. BLDDEVM6 must be
installed explicitly; it is not in the current `BOOT_JCL`
manifest. The job now reads `BOOT_ASM(BCPLMAIN)`.
The previous no-promotion policy applied to the accepted DEVOBJ
milestone. The owner has since explicitly authorized the fresh
all-OBJ source rebuild; the historical candidate remains independent.
Run candidate regressions with the four environment
variables documented in the [complete clean-room
runbook](../../packaging/bcplio-dynamic-stream/Milestone-BCPLIO-dynamic-stream-final-acceptance.md).

The [current dynamic BCPLIO stream contract]
(../../packaging/bcplio-dynamic-stream/BCPLIO-dynamic-runtime-contract.md)
describes the BCPL interface and supported QSAM
record semantics. The accepted M4.4 result was
145 PASS/0 FAIL/expected SKIP 083, while the
fresh M5.5 DEVOBJ panel and strict 145/145 log audit **passed**, and the owner formally **closed** the BCPLIO dynamic-stream milestone on 2026-10-17. Production BOOT_OBJ promotion remains a separate decision; see the [final acceptance](../../packaging/bcplio-dynamic-stream/Milestone-BCPLIO-dynamic-stream-final-acceptance.md).

## M3 clean bootstrap build (not M4)

This environment uses **only** `MR10_SOURCE`, `MR10_LOAD`, `BOOT_SOURCE`,
`BOOT_INTCODE`, and other `NATIVE_*` PDS definitions from
`config/dspal.yaml`. All `CAMB_*` datasets are reserved for M4.

After `dspal initbcpl` and `dspal populate all`, rebuild
`MR10_LOAD(ICINT19)` using `dspal submit MR10_JCL IC19BLD`.
Regenerate `TRNILRG` using `tools/bootstrap/prepare-bootstrap --with-trnilrg`
and position it with `dspal put BOOT_INTCODE TRNILRG`.

Stage the generated bootstrap sources using the `dspal populate` procedure in
[the clean-room runbook](../../packaging/clean-room-mvs-reconstruction.md).
The compiler build steps are:

```sh
python3 tools/checks/check-native-bootstrap-jcl.py
tools/datasets/dspal put BOOT_JCL CAMBBLD bootstrap-toolchain/jcl/cambbld.jcl
tools/datasets/dspal submit BOOT_JCL CAMBBLD
```

The manifest-driven population transfers BLIB and ten demoted compiler units, `BOOTHOST`,
`OPTIONS`, and `CAMBPARM` into `BOOT_SOURCE`; it never allocates a
dataset. `BOOT_SOURCE` headers are populated directly by the manifest.
The generated resident build uses MR10 INTCODE phases, the installed MR10
interpreter, and writes `BCPL`, `SYN`, `LEX`, `TRNA`, `TRNB`,
`CGA` through `CGE`, `BOOTHOST`, and `CAMBCOMP` into
`BOOT_INTCODE`. All outputs are disposable.

The authoritative build JCL source is
`bootstrap-toolchain/jcl/cambbld.jcl` and is installed as `BOOT_JCL(CAMBBLD)` through `dspal put`. No separate
host-side JCL-generation driver is maintained. JES return codes are insufficient
to establish interpreted compilation success; inspect the ICINT completion
codes in the job report and confirm the `BOOT_INTCODE(CAMBCOMP)` member.

## Runtime assembly and object build jobs (M3)

The Git-controlled runtime assembler sources under `bootstrap-toolchain/asm/`
are populated by `dspal populate BOOT_ASM` into `BOOT_ASM`, as
specified by `config/dspal.yaml`. Do not put assembler source into
`BOOT_SOURCE`, which contains BCPL compiler input and headers.

Rebuild accepted runtime objects with the authoritative JCL in
`bootstrap-toolchain/jcl/` installed as `BOOT_JCL(BLDBMAIN)` and
`BOOT_JCL(BLIBBLD)`. These source files are installed with `dspal put`
and executed with `dspal submit`. Accepted objects reside in
`BOOT_OBJ`; development candidates reside in `BOOT_DEVOBJ`.
The historical job-body steps for assembling, verifying, and installing
binary FB80 records are preserved. No host build-blib driver exists.

For the full from-scratch M3 reconstruction including MR10 demos and native regression, see [the clean-room PDS runbook](../../packaging/clean-room-mvs-reconstruction.md). The obsolete host source-bootstrap driver and the one-time tools relocation script were retired; their sources remain in Git history.
