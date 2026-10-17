# Clean-room MVS reconstruction — acceptance record

**Date:** 17 October 2026
**Result:** PASS — technical acceptance criteria satisfied
**Baseline Git commit:** 04c74af8b07b5cdc2aaec44d79f020a848cb7e65
**Runbook:** packaging/clean-room-mvs-reconstruction.md

## Reconstruction

The project-managed MVS environment was reconstructed from Git
and historical source, without migrating previously compiled
INTCODE, object modules, or load modules.

- 24 managed BCPL datasets purged and reinitialized.
- 145 tracked source and JCL members populated.
- Purge completion: JOB 8511.
- Dataset initialization: JOB 8536.
- Population began at JOB 8551; final population JOB identifier
  is not recorded here.
- Effective managed dataset definitions: config/dspal.yaml
  at the recorded Git baseline; local private overrides excluded.

## Interpreter and compiler evidence

| Component | Evidence |
|---|---|
| ICINT19 | Rebuilt, JOB 8701 |
| Installed interpreter smoke test | JOB 8704, CODE=0 |
| MR10 language demonstrations | JOB 8707, PASS |
| MR10 BCPL demonstrations | JOB 8710, PASS |
| MR10 regression suite | JOB 8713, PASS |
| Enlarged TRNILRG | Rebuilt, JOB 8714; installed JOB 8715 |
| Cambridge source staging | JOBs 8717–8730 |
| CAMBCOMP | JOB 8737, all 22 interpreted phases CODE=0 |
| Native compiler smoke test | JOB 8739, generated S/370 assembler |

The enlarged translator and Cambridge compiler were
regenerated from source and installed in NATIVE_INTCODE.

## Production object build

NATIVE_OBJ was confirmed empty before the build.

| Job | Operation | Result |
|---|---|---|
| 8744 | BLDBMAIN, five IFOX assemblies and five installs | All RC=0000 |
| 8748 | BLIBBLD, six build/install steps | All RC=0000 |

BLIB interpreted compilation reported:

    EXECUTION CYCLES = 9009776, CODE = 0

Final NATIVE_OBJ members:

    BCPLMAIN
    BCPLMEM
    BCPLBYTE
    BCPLAPT
    BCPLIO
    BLIB

NATIVE_DEVOBJ was confirmed empty after regression testing.

## Native production regression

Production-only profile: NATIVE_OBJ, all six rebuilt modules.

- Numbering check: PASS, 00..145.
- Focused cases 000, 052, 093, 124: PASS.
- Dynamic-stream accounting cases 139..145: 7 PASS.
- Complete production panel: 145 PASS, 0 FAIL, 1 SKIP.
- Total numbered cases: 146.
- Expected source-only skip: 083.
- Compile-only PASS: 048.
- Detailed saved-log audit: PASS, 145/145.
- No known-defect or ABEND exceptions detected.

Saved JES job/step manifest:

    workarea/native-regression/m44-00-145-jobs.tsv

## Evidence boundaries

The MR10 resident suites were checked through JES results,
interpreter completion codes, and observed output. They were
not automatically compared against checked-in golden-output files.

The saved-log audit examines regression harness reports,
not independent physical per-DD MVS record captures.

The generated bootstrap manifests and regression logs are
under workarea/ and are not incorporated into this Git
acceptance record as binary or generated artifacts.

The reconstruction satisfies the runbook's source-based
production OBJ acceptance target. No previously compiled
binary was used to populate the reconstructed libraries.
