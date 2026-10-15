# Native compiler tools

Canonical entry points for Cambridge/native compiler work:

- `prepare-bootstrap`: reconstruct disposable bootstrap input files.
- `NATIVE_JCL(CAMBBLD)`: authoritative M3 resident compiler build job, sourced from `native-compiler/jcl/build-cambridge-resident.jcl`.
- `compile-mvs`: compile BCPL using the installed resident Cambridge compiler.
- `compile-bootstrap`: legacy bootstrap-from-source Cambridge driver.
- `build-blib`: build the BLIB relocatable object module.
- `run-regression`: run the native regression panel.
- `capture-writef-cg370`: capture CG370 diagnostics.

M3 uses the refactored `NATIVE_*` and `MR10_*` dataset namespace. Do not use `CAMB_*` datasets before M4.

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

The staging command transfers ten demoted compiler units, `BOOTHOST`,
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
