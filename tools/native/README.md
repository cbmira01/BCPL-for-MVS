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
