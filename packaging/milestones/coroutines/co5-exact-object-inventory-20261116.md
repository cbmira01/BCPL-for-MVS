# CO.5 — Exact production BOOT_OBJ inventory gate

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.5 — Integration, Regression, and Release
**Date:** 16 November 2026
**Status:** Host-verified bounded improvement; MVS clean-room verification remains pending

## Reason for follow-up

The earlier CO.5 clean-room integration required the exact ten-member
`BOOT_OBJ` inventory in the guarded controller, but the simple
`rebuild-from-source` entry point merely *listed* the object library.
A successful `dspal ls` did not establish which members were installed.

The simple driver now calls `tools/reconstruction/verify-boot-obj.py`
after `BLDCORCO` and `BLDCORLB`, before the installed-only GO oracle.
This command obtains the actual MVS `dspal ls BOOT_OBJ` listing,
uses the common `verify.inventory_members` and `required_inventory`
contracts, and refuses missing, extra, duplicated or wrong-library
entries. On success it emits one short receipt. On failure it returns
nonzero, preventing the coroutine GO oracle from running.

## Local host checks and limits

In the assistant's isolated container workspace, Python syntax
verification succeeded for the exact inventory-checking script.
Twelve focused synthetic Python checks passed, including:
- Existing CO.5 compilation, preparation, staging and installed GO
  receipt positive/negative tests (four).
- Exact member-inventory positive/negative tests (five).
- Subprocess-level CLI tests using an isolated synthetic `dspal-core`
  and executable inventory producer (three).

No MVS jobs or WSL commands were run by the assistant. The isolated
container could not resolve `github.com` to clone the full repository,
so **this record is not a claim that the full repository host-test
suite has executed**. Source and targeted test changes were reviewed
against the authoritative GitHub tree through the GitHub connector.

**CO.5 remains IN PROGRESS** until the operator executes a fresh
destructive clean-room reconstruction, verifies ten installed objects,
and supplies the resulting IFOX/IEWL/GO and oracle evidence for separate
owner acceptance.
