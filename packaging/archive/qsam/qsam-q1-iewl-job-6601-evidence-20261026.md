# Milestone QSAM — Q.1 temporary IEWL linkage evidence (JOB 6601)

**March:** Q.1 — Linkage & OPEN/CLOSE skeleton  
**MVS JES date/time:** 26 October 2026, 00:04:54–00:04:55  
**Disposition:** Temporary IFOX+IEWL **PASS** within the tested standalone-link scope; **Q.1 remains OPEN**.

## Operator-supplied evidence

The operator executed the source-controlled `prepare-q1-link.py` and
its offline validation on GitHub `main` at commit `1aced1052068`.
The operator's transcript records four successful offline checks:
the Q.1 source-invariant check, four IFOX generator tests,
four linkage-generator tests, and the 807-card synthetic JCL validation.
A protected local `workarea/bcplqsam-q1/q1link.jcl` was generated.
The operator then submitted `Q1QSLNK` and obtained **JOB 6601**.

| Observation | Reported result |
| --- | --- |
| JOB and job name | `6601 Q1QSLNK` |
| ASMQ / IFOX00 | `RC=0000` |
| LKED / IEWL | `RC=0000` |
| JES result | `SUCCESS` |
| Highest step RC | `0000` |
| Assembler statements flagged | `0` |
| Assembler highest severity | `0` |
| Cards read | `809` |
| ASMQ region | `256K` |
| LKED region | `256K` |
| JES report extraction | `RC=0` |

The provided IEWL MAP/XREF excerpts include the following program
elements, with map values reported as hexadecimal offsets/lengths:

| Element | Address/offset | Length |
| --- | --- | --- |
| `QSMBEG` descriptor entry | `000000` | — |
| `QSMDISP` | `000038` | `0000E8` |
| `QSMCORE` | `000120` | `00061C` |
| `QSMFIN` | `000890` | `000170` |

The map includes `QSMCLS1` references and `IEW0000 ENTRY QSMBEG`.
The transcript reports `HIGHEST SEVERITY WAS 0` and successful
assembler and linkage return codes. The **complete** IEWL listing
is a local operator artifact, not part of this GitHub record; do not
claim a line-by-line audit of every MAP/XREF row from these excerpts.

## Accepted scope and boundaries

JOB 6601 verifies assembly and **standalone test-only IEWL linkage**
of the candidate BCPLQSAM relocatable object, including the
displayed descriptor and implementation CSECT references.
The JCL generator used only temporary object and load datasets; no
installed Runtime Extensions, `BOOT_OBJ`, `BOOT_DEVOBJ`, or
production `BCXCAT` were changed.

It **does not** establish native BCPL registration or `QSAMSVC:200`
dispatch, QUERY behavior, live QSAM OPEN/CLOSE ownership, slot reuse,
returned-CLOSE handling, the complete 16-handle GO REGION=256K
resource budget, or FINISH/STOP finalization.

## Next controlled test

Use an independently compiled native BCPL **QUERY-only** caller
under the approved temporary BCX registration sequence at
`GO REGION=256K`. This test must not OPEN a QSAM DCB.
It can establish that the BCEX/BCRG selection and public G!200 call
work in a real native application and that a no-live-handles
FINISH path completes. Record its JOB ID, every assembler/IEWL/GO
RC, the selected BCEX/BCRG map, and expected output.
Proceed to three-DD OPEN/CLOSE and 16-handle tests only after
native QUERY and source ownership review.

**Still owner-gated:** returned-CLOSE fault-injection methodology,
cleanup-error precedence, and any higher GO REGION attempt.
