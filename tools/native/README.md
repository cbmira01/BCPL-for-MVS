# Native compiler tools

Canonical entry points for Cambridge/native compiler work:

- `prepare-bootstrap`: reconstruct disposable bootstrap input files.
- `build-cambridge`: build the MVS-resident Cambridge compiler.
- `compile-mvs`: compile BCPL using the installed resident Cambridge compiler.
- `compile-bootstrap`: legacy bootstrap-from-source Cambridge driver.
- `build-blib`: build the BLIB relocatable object module.
- `run-regression`: run the native regression panel.
- `capture-writef-cg370`: capture CG370 diagnostics.

Root `tools/` compatibility launchers remain in place during migration. The PDS namespace and build procedures have not yet been changed.

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
tools/native/build-cambridge --show-jcl
tools/native/build-cambridge
```

The staging command transfers ten demoted compiler units, `BOOTHOST`,
`OPTIONS`, and `CAMBPARM` into `NATIVE_SOURCE`; it never allocates a
dataset. `NATIVE_SOURCE` headers are populated directly by the manifest.
The generated resident build uses MR10 INTCODE phases, the installed MR10
interpreter, and writes `BCPL`, `SYN`, `LEX`, `TRNA`, `TRNB`,
`CGA` through `CGE`, `BOOTHOST`, and `CAMBCOMP` into
`NATIVE_INTCODE`. All outputs are disposable.

A matching stored JCL body is kept at
`native-compiler/jcl/build-cambridge-resident.jcl` and mapped as
`NATIVE_JCL(CAMBBLD)`. If invoking that form, first upload the revised job
body using `dspal put NATIVE_JCL CAMBBLD`. The host build driver is preferable
because it resolves dataset names from the current manifest and validates
interpreted completion codes.
