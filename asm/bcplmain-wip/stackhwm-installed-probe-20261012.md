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

## TK5 operator result — JOB 7815 (12 October 2026)

The operator prepared with `prepare-stackhwm-pds-probe.py` (Cambridge compile JOB **7814**) and submitted the generated application-only JCL as JOB **7815** (`RG120R`).

| Step | Program | RC |
| --- | --- | --- |
| ASMAP | IFOX00 | 0000 |
| LKED | IEWL | 0000 |
| GO | temporary linked BCPL load module | 0000 |

Assembler flagged **0** statements. IEWL listed `INCLUDE OBJ(BLIB)` and mapped BLIB as a resident linked control section (origin `17D8`, length `1BB0`). The production OBJ PDS was read as `DISP=SHR`; no installation took place.

Observed SYSPRINT:

```text
STACKBASE 174016
STACKEND 190464
STACKHWM 0
```

**Evidence evaluation:** The program invokes G56 and completes RC=0000, establishing that the installed runtime/global registration resolves to executable STACKHWM behavior. A fully independent export-trailer dump remains outstanding, but the runtime call succeeds with the actual installed BLIB. The zero result is `OVERFLOW` according to historical BLIB's contract; the current runtime has not initialized the required marker words. It must **not** be interpreted as proof that a real stack overflow occurred (there was no abnormal termination). Nor does this isolated observation establish the exact reason for failing the historical checks until marker values are examined.

**Next gate:** Propose a bounded, regression-first initialization of the historical stack alternating patterns and two top metadata words, respecting the WIP's safe stack limit. Preserve current OBJ members until source-mode plus installed-mode evidence is obtained.

## Follow-on G56 implementation candidate — pending source-mode verification

BCPLMAIN startup in `10-bootstrap-and-system.asmfrag` and synchronized `asm/bcplmain-wip.asm` now paints the 16,384-word safe stack before invoking the BCPL START routine: 8,192 consecutive pairs of `#X5C40E2E3` and `#XC3D2405C`. It stores `EVENSTACK` at `STACKEND-2` and stores `(STKLIM-8)/4` as the BCPL-word Q at `STACKEND-1`. The top two metadata words remain inside the 256-byte clearance, not the checked working stack. No changes to G54/G55 values, STKLIM, or BLIB itself.

`native-compiler/regression/120-stackhwm-initialized` tests that BLIB's G56 returns an in-range word address rather than the 0/1 historical diagnostic result. It does not assert an absolute address or claim accurate usage under every path.

**Source-mode verification gate (before promotion):**

```sh
 git pull --ff-only
 python3 tools/checks/check-bcplmain-modules.py
 python3 tools/checks/check-asm-source.py asm/bcplmain-wip.asm
 BCPL_RUNTIME_PDS=0 tools/run-native-regression 120 --show-output
```

The source runtime regression uses installed `OBJ(BLIB)` but assembles the newly staged BCPLMAIN; existing `OBJ(BCPLMAIN)` is unchanged. Inspect the test's ASMRUN and GO return codes if failure occurs. **Do not yet invoke `--only-main` installation.** The existing JOB 7815 result (`STACKHWM 0`) remains the observed production baseline until a new installed-runtime probe is explicitly run and accepted.

## Initial source-mode regression — JOB 7817, assembler addressability

Operator ran regression 120 source mode. Cambridge compile JOB 7816 succeeded; application ASMAP RC=0000. Runtime ASMRUN RC=0008 and LKED/GO were bypassed. IFOX listed one failing instruction, startup `LA 1,GETVEC`, displaced beyond the available base-addressing range by the additional marker-initialization code. The fix replaces that startup instruction with `L 1,=A(GETVEC)`, in both the staged fragment and the canonical assembler; this is an address-loading correction, **not** evidence that STACKHWM now works. Repeat `BCPL_RUNTIME_PDS=0 tools/run-native-regression 120 --show-output`; production OBJ remains unchanged.
