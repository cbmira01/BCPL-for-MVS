# Milestone Runtime Extensions — R.0 G!76 no-export fallback, JOB 2220

**Date:** 21 October 2026. **March:** **R.0 — Evidence and contract (open)**.
**Disposition: PASS**, within the owner-approved test-only no-export fixture.
**Git source:** `ae9cc07e4eba7536dc6723b1a2f16df8ac24a427`.
**R.1 — Generic registration foundation** has not started.

The owner ran [the tracked probe](../bootstrap-toolchain/probes/r0-g76-noexport-probe/README.md).
JOB **2219** compiled the minimal BCPL test under the interpreter-hosted
**demoted Cambridge compiler**, saving native CG370 assembler.
JOB **2220**, `R0G76F`, executed on MVS 3.8J/TK5 on 21 OCT 26
at 20:32:56 (system time).

| Step | Program | Actual result |
| --- | --- | --- |
| ASMA | IFOX00 | RC=0000 |
| ASMB | IFOX00 | RC=0000 |
| LKED | IEWL | RC=0000 |
| GO | Temporary native executable | RC=0000 |

JES result **SUCCESS**, highest RC **0000**; no flagged IFOX statements
and highest severity 0. ASMA punched **6** binary object records; ASMB
punched **4**. **18 host tests** passed. The generator reported an
82-card synthetic JCL check and 115 generated cards; the actual
submission was **117 JES cards**, **371 SYSOUT records**.

## Independently reviewed IFOX and IEWL evidence

The owner supplied the **entire** JOB 2220
`tools/mvs/dump-report-for-job` output, including assembler ESD,
source/listing, IEWL `NCAL,LIST,XREF,MAP`, and GO output.
The temporary ASMB ESD has **BLIB SD length 0x18**.
Its exact prefix/trailer is:

```asm
BLIB     CSECT
         ENTRY BLIB
         EXTRN BCPLMAIN
         STM   14,12,12(13)
         L     4,12(15)
         BCR   15,4
         DC    AL2(BLEND-BLIB)
         DC    A(BCPLMAIN)
         DC    F'2796'
         DC    F'0'
BLEND    EQU   *
```

The last two words form **only the empty export sentinel**.
The fixture therefore has **no G!76 or other BCPL global export**.

| IEWL CSECT | Origin hex | Length hex | Owner |
| --- | ---: | ---: | --- |
| `R0APP` | `000000` | `000080` | Temporary ASMA |
| `BLIB` | `000080` | `000018` | **Temporary ASMB** |
| `BCPLMAIN` | `000098` | `000C00` | Installed `BOOT_OBJ` |
| `BCPLIO` | `000C98` | `001FB4` | Installed `BOOT_OBJ` |
| `BCPLMEM` | `002C50` | `0002AC` | Installed `BOOT_OBJ` |
| `BCPLBYTE` | `002F00` | `000026` | Installed `BOOT_OBJ` |
| `BCPLAPT` | `002F28` | `00006C` | Installed `BOOT_OBJ` |

The total linked length is **0x2F98**, entry `R0APP`.
IEWL XREF shows `BCPLMAIN` referring to **temporary** `BLIB`
at relative **0x39C** and the temporary BLIB's reference back
to BCPLMAIN at **0x8C**. The five explicit `INCLUDE OBJ(...)`
statements name only BCPLMAIN, BCPLIO, BCPLMEM, BCPLBYTE and BCPLAPT.
**Installed `BOOT_OBJ(BLIB)` is not included.**
`HERC02.BCPL.BOOT.OBJ` is an input `DISP=SHR` dataset;
assembled objects and the linked executable use temporary `&&`
datasets only. No accepted PDS member was changed.

The **actual** GO record, verified by the probe report checker, is:

```text
R0 G76 FALLBACK 31415 PASS
```

The program calls G!76 WRITEF with `%N` to produce the numeric
argument. This establishes real execution of the Core Runtime's
`WRITEST` fallback when the linked BLIB contains no G!76 export.

## Exact disposition

[JOB 2199](runtime-extensions-r0-g76-job-2199-evidence-20261021.md)
verifies preservation of real BLIB WRITEF when it exports G!76;
**JOB 2220** verifies the opposite, **no-G!76-export** branch.
Both agreed R.0 G!76 precedence paths now have actual MVS evidence.

The fixture **did provide a BLIB linker symbol**. It does **not**
prove the current BCPLMAIN supports completely omitting BLIB,
nor BLIB library services with an empty substitute; and it
does not implement BCPLREG or optional collision rejection.

Retain the credential-bearing full JES report under ignored
`workarea/`, not in Git. **R.0 open, R.1 not started.**
