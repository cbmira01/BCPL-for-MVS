# Native compiler tools

Canonical entry points for Cambridge/native compiler work:

- `prepare-bootstrap`: reconstruct disposable bootstrap input files.
- `NATIVE_JCL(CAMBBLD)`: authoritative M3 resident compiler build job, sourced from `native-compiler/jcl/build-cambridge-resident.jcl`.
- `compile-mvs`: compile BCPL using the installed resident Cambridge compiler.
- `NATIVE_JCL(BLIBBLD)`: build the BLIB relocatable object module using `native-compiler/jcl/build-blib-object.jcl`.
- `run-regression`: run the native regression panel.
- `capture-writef-cg370`: capture CG370 diagnostics.

M3 uses the refactored `NATIVE_*` and `MR10_*` dataset namespace. Do not use `CAMB_*` datasets before M4.

## M5.4 dynamic runtime DEVOBJ candidate

After an **approved** base M3 compiler/OBJ reconstruction,
the current M5 native stream candidate consists of
`NATIVE_DEVOBJ(BCPLM6)` and
`NATIVE_DEVOBJ(BCPLIO)`, assembled via
`NATIVE_JCL(BLDDEVM6)` and
`NATIVE_JCL(BLDDEVI)`. BLDDEVM6 must be
installed explicitly; it is not in the current `NATIVE_JCL`
manifest. The job now reads `NATIVE_ASM(BCPLMAIN)`.
Submitting production `BLDBMAIN` with that canonical D6 source
would change `NATIVE_OBJ` and requires separate authorization.
Run candidate regressions with the four environment
variables documented in the [complete clean-room
runbook](../../packaging/clean-room-mvs-reconstruction.md#10-m54-addendum--reproduce-the-accepted-dynamic-bcplio-candidate).

The [current dynamic BCPLIO stream contract]
(../../packaging/bcplio-dynamic-stream/BCPLIO-dynamic-runtime-contract.md)
describes the BCPL interface and supported QSAM
record semantics. The accepted M4.4 result was
145 PASS/0 FAIL/expected SKIP 083, while the
fresh M5.5 DEVOBJ panel and strict 145/145 log audit **passed**, and the owner formally **closed** the BCPLIO dynamic-stream milestone on 2026-10-17. Production NATIVE_OBJ promotion remains a separate decision; see the [final acceptance](../../packaging/bcplio-dynamic-stream/Milestone-BCPLIO-dynamic-stream-final-acceptance.md).

## M3 clean native-compiler bootstrap (not M4)

This environment uses **only** `MR10_SOURCE`, `MR10_LOAD`, `NATIVE_SOURCE`,
`NATIVE_INTCODE`, and other `NATIVE_*` PDS definitions from
`config/dspal.yaml`. All `CAMB_*` datasets are reserved for M4.

After `dspal initbcpl` and `dspal populate all`, rebuild
`MR10_LOAD(ICINT19)` using `dspal submit MR10_JCL IC19BLD`.
Regenerate `TRNILRG` using `tools/native/prepare-bootstrap --with-trnilrg`
and position it with `dspal put NATIVE_INTCODE TRNILRG`.

Stage the host-generated native bootstrap sources **only through dspal**:

```sh
python3 tools/native/stage-bootstrap --dry-run
python3 tools/native/stage-bootstrap
python3 tools/checks/check-native-bootstrap-jcl.py
tools/datasets/dspal put NATIVE_JCL CAMBBLD native-compiler/jcl/build-cambridge-resident.jcl
tools/datasets/dspal submit NATIVE_JCL CAMBBLD
```

The staging command transfers BLIB and ten demoted compiler units, `BOOTHOST`,
`OPTIONS`, and `CAMBPARM` into `NATIVE_SOURCE`; it never allocates a
dataset. `NATIVE_SOURCE` headers are populated directly by the manifest.
The generated resident build uses MR10 INTCODE phases, the installed MR10
interpreter, and writes `BCPL`, `SYN`, `LEX`, `TRNA`, `TRNB`,
`CGA` through `CGE`, `BOOTHOST`, and `CAMBCOMP` into
`NATIVE_INTCODE`. All outputs are disposable.

The authoritative build JCL source is
`native-compiler/jcl/build-cambridge-resident.jcl` and is installed as `NATIVE_JCL(CAMBBLD)` through `dspal put`. No separate
host-side JCL-generation driver is maintained. JES return codes are insufficient
to establish interpreted compilation success; inspect the ICINT completion
codes in the job report and confirm the `NATIVE_INTCODE(CAMBCOMP)` member.

## Runtime assembly and object build jobs (M3)

The Git-controlled runtime assembler sources under `native-compiler/asm/`
are populated by `dspal populate NATIVE_ASM` into `NATIVE_ASM`, as
specified by `config/dspal.yaml`. Do not put assembler source into
`NATIVE_SOURCE`, which contains BCPL compiler input and headers.

Rebuild accepted runtime objects with the authoritative JCL in
`native-compiler/jcl/` installed as `NATIVE_JCL(BLDBMAIN)` and
`NATIVE_JCL(BLIBBLD)`. These source files are installed with `dspal put`
and executed with `dspal submit`. Accepted objects reside in
`NATIVE_OBJ`; development candidates reside in `NATIVE_DEVOBJ`.
The historical job-body steps for assembling, verifying, and installing
binary FB80 records are preserved. No host build-blib driver exists.

For the full from-scratch M3 reconstruction including MR10 demos and native regression, see [the clean-room PDS runbook](../../packaging/clean-room-mvs-reconstruction.md). The obsolete host source-bootstrap driver and the one-time tools relocation script were retired; their sources remain in Git history.
