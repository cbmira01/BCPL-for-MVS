# G56 STACKHWM — installed BLIB verification and observation gate

**State: prepared, NOT RUN on TK5.** No runtime assembler, library objects, or numbered regression tests changed. Accepted production baselines remain 119/119 and 120/120.

## Source verification vs installed verification

Historical `richards-bcpltape/bcplib/bcpl/blib` explicitly defines `AND STACKHWM() = VALOF`, and `MAPSTORE` calls it. SYS3 LIBHDR declares `STACKHWM:56`. These establish the historical source's intended global, **not** that the current installed `HERC02.BCPL.OBJ(BLIB)` actually exports the same global.

The installed production BCPLMAIN imports the BLIB module's global definition pairs during startup; an IEWL INCLUDE alone confirms a library object was included, **not** an exported BCPL G56 registration. The probe must therefore check both the IEWL linkage evidence and actual BCPL call behavior. A separate reading of the installed BLIB exported-global trailer, or an assembler listing of the built BLIB, is required for strict export-table verification.

## Reproducible non-mutating probe

```sh
git pull --ff-only
python3 tools/checks/prepare-stackhwm-pds-probe.py
```

This compiles `tools/checks/stackhwm-pds-probe.bcpl` using the established MVS-resident Cambridge compiler, and stages `workarea/stackhwm-pds-probe/stackhwm-installed.jcl` via the existing installed-PDS JCL builder, with `INCLUDE OBJ(BCPLMAIN)`, `OBJ(BCPLBYTE)`, `OBJ(BCPLAPT)`, `OBJ(BCPLMEM)`, and `OBJ(BLIB)`. The module uses global G56 directly and prints STACKBASE, STACKEND, and STACKHWM values. Number **120** is used only for temporary job and assembler identifiers; this probe is NOT placed in the numbered regression directory and does not expand the formal regression panel.

Review the generated deck (it can hold local job authentication information; keep it private). It must contain ASMAP, LKED, GO only; it must not contain an assembler step for runtime or any writable OBJ member DD.

```sh
tools/submit-jcl workarea/stackhwm-pds-probe/stackhwm-installed.jcl
tools/job-summary <returned-job-number>
tools/dump-report-for-job <returned-job-number> \
  > workarea/stackhwm-pds-probe/job-report.txt
```

Provide the job summary and relevant IEWL map/global evidence plus the GO output; do not treat a nonzero STACKHWM number as correctness automatically. **Expected uncertainty:** Since current BCPLMAIN has no sentinel setup, G56 might return 0 (OVERFLOW), 1 (UNSET), an unrelated word address, or encounter a runtime failure. Results must be observed, not presupposed.

## Required evidence to close the gate

1. IFOX RC=0, IEWL RC=0, GO outcome and the value printed for STACKHWM.
2. Linker evidence BLIB CSECT present, plus an explicit verification of G56 exported-global registration where available; call success is behavioral evidence but is not alone a substitute for inspecting the export trailer.
3. Compare STACKBASE/STACKEND to returned high-water value; identify the uninitialized-marker failure mode.
4. Only after observing results, derive and implement historical markers in a separately scoped march, with focused tests first.

No changes to G45 or G57, no modifications to BCPLMAIN or BLIB, no PDS member replacements.
