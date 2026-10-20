# Milestone Runtime Extensions — R.0 revised design approved for testing

**Date:** 20 October 2026. **March:** R.0 — Evidence and contract (open).
The owner approved proceeding with the revised descriptor and dependency
**design for isolated R.0 testing**. This is **not** acceptance of an
exact binary ABI, a working BCPLREG, or R.0 closure.
R.1 — Generic registration foundation remains unstarted.

## Approved testing direction and acceptance boundaries

| Area | Intended evidence | Not yet approved as final ABI |
| --- | --- | --- |
| Descriptor bounds | Linker-resolved independent begin/end, checked before extended fields, with source-controlled fixture bounds | Trust model for deliberately forged symbols, max counts, public label names |
| Dependencies | Application required-ID list plus package-local required-ID/version entries; dependency-first ordering, reverse teardown | Final binary encoding, transitive validator and error layout |
| Global ownership | Pre-START ledger for application CG370, BLIB, native core and optional exports; preserve verified historical precedence | Transactional importer implementation and complete collision/waiver ledger |
| Startup/finalizer | Reverse finalization, FINISH RC=8 on returned finalizer failure, STOP(n) unchanged | Exact assembler linkage, save areas and diagnostics |

For the first test, the **candidate** table is a 28-byte header plus
an 8-byte linked (begin,end) pair and 8-byte application required ID.
The **candidate** package descriptor is a 48-byte header followed by
one or two eight-byte (global,address) exports. Package-local
sixteen-byte dependency entries are reserved for a later probe.

These byte offsets are **test-fixture conventions only**.
The original 28/40-byte design document remains a historical candidate,
not a currently accepted implementation ABI.

## Prepared first test-only evidence package

Source: [R.0 descriptor/linkage probes](../bootstrap-toolchain/probes/r0-registration-probes/README.md).

Four independent IFOX assemblies and one IEWL link-edit produce a
temporary load module. Six profiles exercise valid relocated bounds,
bad table length, bad version, duplicate export, attempted occupied
native G!14 export and missing application required package.
Negative profiles must reject for their **specific expected internal
error code**, not merely abend or fail for unrelated reasons.

**Validation correction (2026-10-20):** The initial Morkies attempt
stopped at Python unittest discovery: `test_generator.py` line 62
was missing a closing parenthesis after `unittest.main(verbosity=2)`.
Therefore the earlier claim that all four unit tests passed was
**incorrect**. A one-character source correction is committed; the
full suite and six generated decks require re-verification on Morkies.
**Subsequent MVS results:** The corrected suite **PASSED** on Morkies,
then [JOBs 2187–2192](runtime-extensions-r0-first-probes-evidence-20261020.md)
all passed, each with six RC=0000 steps and its actual expected
QOUT marker. This supersedes the initial unrun status without
erasing the earlier syntax correction record.

The fixtures use the test-local placeholder PACKA/G!299 but do
not register an actual BCPL global. G!299 remains **unallocated**
to PACKA by the official Global Number Registry.

## Remaining separate R.0 evidence

Package-local dependency constraints, dependency graph/order, true
pre-START app/BLIB/native collision ledger, trusted load-module
span bounds, finalizer register/save-area ABI, and FINISH/STOP
end-to-end behavior are **not established** by this first probe.

The original R0VALID and five negative fixtures have **now all run
and passed**. The owner requested batching subsequent R.0 probes:
see the [one-JOB, 20-case package](../bootstrap-toolchain/probes/r0-batch-probes/README.md).
That new package has passed offline tests only; its actual MVS
assembler/link/GO results are still pending. A failed probe is a reason to
fix the isolated test, not to change accepted BCPLMAIN, BOOT_OBJ,
BOOT_DEVOBJ, or the demoted Cambridge compiler. Q.0 remains open
and neither Q.1 nor R.1 has started.