# Milestone Runtime Extensions — R.4 — JOB 3721 integration evidence

**Date:** 23 October 2026  
**JES:** `R4BCXINT` / **JOB 3721**  
**Git revision tested:** `764ac6648d7a99e28c8ad4f74d729815014fabfe`  
**Disposition:** **FAIL — GO ABEND S0C1**. R.4 remains open; this is not BCPL registrar acceptance.

## Observed JES and IEWL results

| Step | Actual result |
| --- | --- |
| `COMP` (ICINT19 and resident demoted Cambridge compiler) | RC=0000; `COMPILATION SUCCESSFUL`; compiler code 0 |
| `PREP`, `CATP`, `POSTP` | IEBGENER RC=0000 each |
| `ASMA`, `ASMN`, `ASMR`, `ASMP`, `ASMG` | IFOX RC=0000 each |
| `LINK` | IEWL RC=0000; `INCLUDE PKGA` processed |
| `GO` | **S0C1**, no BCPL `START` marker |

The IEWL MAP localizes the defect:

```text
CONTROL SECTION   ORIGIN  LENGTH
$PRIVATE             00      B0  (CG370 client)
BCPLMAIN             B0    1048
RGINIT             10F8     A20
DMODESC            1C18      38
DMODISP            1C50      C8
BCPLREG            1D18      2C
ENTRY ADDRESS        B0
```

CG370 generated an unnamed private control section whose `END`
had no operand. The later BCPLMAIN assembler source ended with
`END BCPLMAIN`. Without an explicit IEWL `ENTRY`, the linker
selected BCPLMAIN instead of the compiled application prefix at zero.
Entering the runtime directly bypasses its expected application
calling sequence. This explains the observed S0C1 but does not prove
the registrar was actually reached.

## Narrow test-only correction

Prepend these source records through a concatenated in-stream
`ASMA.SYSIN` DD, before the untouched `&&R4CODE` dataset:

```asm
         CSECT
         ENTRY R4APP
R4APP    EQU   *
```

The compiler's own unnamed `CSECT` resumes that section. The
label is a zero-length external definition at byte offset zero;
no executable code or data is inserted. Add `ENTRY R4APP` to IEWL
control input immediately before `NAME`. Acceptance requires an
IFOX external label `R4APP` in the private CSECT, IEWL
`ENTRY ADDRESS 0`, the BCPL `START` marker and GO RC=0000.

IBM *OS/360 Linkage Editor* C28-6538-3 (1966), p. 28/28.1,
documents the ENTRY control statement and distinguishes externally
defined entry names from unnamed private code. `$PRIVATE` in the
IEWL MAP is only a display name for the anonymous CSECT, not an
application-defined entry symbol.

**The revised JCL has not yet run under MVS.** No production
runtime, compiler, or persistent object library is changed.
