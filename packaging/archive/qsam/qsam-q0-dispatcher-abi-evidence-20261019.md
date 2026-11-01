# Milestone QSAM — Q.0 dispatcher ABI execution evidence

**Date:** 2026-10-19  
**System:** Hercules / TK5 MVS 3.8J, owner-provided JES report  
**Scope:** `QSAMSVC` G!200 BCPL-to-assembler calling convention only  
**Finding:** **PASS**, without implementing any QSAM operations

## Inputs and reproducibility

- Retained source: `bootstrap-toolchain/probes/q0-dispatcher-abi-probe/`.
- Native BCPL caller compiled with the **demoted Cambridge compiler**
  (`CAMBCOMP` under `ICINT19`), using `tools/bootstrap/compile-mvs`.
- The test-only generated-trailer adapter `prepare-job.py` inserted exactly
  one external G!200 binding to `Q0DISP` at offset `200*4=800`.
- The separately assembled `dispatcher.asm` only simulates INFO and QUERY.
- The GO JCL linked the two temporary object decks with accepted runtime
  objects in `HERC02.BCPL.BOOT.OBJ` using the **OBJ** profile.
- No accepted object PDS member, compiler, BCPLMAIN, BCPLIO, or project
  manifest was modified to create or run this probe.

The initial preparation attempt stopped in a local Python exact-whitespace
assertion for `EXTRN BCPLMAIN` even though the generated code was valid. The
repaired `prepare-job.py` uses the existing regexp-based declaration parser.
The successful MVS run used the corrected script.

## Actual owner-observed results

| Stage | MVS job | Executed program | Observed result |
|---|---|---|---|
| Compile BCPL source | 2156 | CAMBCOMP / ICINT19 | Compiled CODE saved |
| Assemble application | 2157 | IFOX00 / ASMAP | RC=0000 |
| Assemble dispatcher | 2157 | IFOX00 / ASMNAT | RC=0000 |
| Link edit | 2157 | IEWL / LKED | RC=0000 |
| Run | 2157 | GO | RC=0000; BCPL printed **42** |

Both IFOX assembly listings reported **NO STATEMENTS FLAGGED IN THIS
ASSEMBLY** and highest severity **0**.

### ABI-specific corroboration from the actual listings

- The generated BCPL caller loaded G!200 with **`L 4,800(12)`** and
  invoked the native routine using `BALR 6,4`.
- The generated application trailer contained `DC F'800'` and
  `DC A(Q0DISP)`; the latter was an external relocatable reference.
- The IEWL map listed **Q0APPL**, **Q0DISP**, **BCPLMAIN**, **BCPLIO**,
  **BCPLBYTE**, **BCPLAPT**, **BCPLMEM**, and **BLIB**.
- The independently assembled `Q0DISP` checked the four request words,
  placed response values in an eight-word result vector, and exercised
  the six-word query descriptor. The BCPL caller completed its checks
  before emitting **42**.

The successful job's exact output was:

```text
QS0DISPR   ASMAP   IFOX00    RC=0000
QS0DISPR   ASMNAT  IFOX00    RC=0000
QS0DISPR   LKED    IEWL      RC=0000
QS0DISPR   GO      PGM=*.DD  RC=0000

42
```

The complete JES report was provided by the owner in conversation and can be
re-extracted locally using `tools/mvs/dump-report-for-job 2157` when that
spool content is still available. The entire JES report is **not** checked
in, to avoid machine-specific metadata or possible local credentials.

## Interpretation and limitations

**Demonstrated:** MVS external-object linkage, G!200 binding in the
application export trailer, correct native three-argument and pointer
representation for the tested cases, deterministic result-vector writes,
side-effect-free QUERY test cases, normal return to BCPL and RC0.

**Not demonstrated:** a shared `BCPLREG` registration mechanism (the test
patches the application's trailer), actual QSAM dataset OPEN/GET/PUT/CLOSE,
large record limits, buffer staging, MVS error recovery, V/VB records or
module lifecycle. These remain gated by Q.0/Q.1 and Runtime Extensions.

**Acceptance:** Record this probe as PASSED; **do not close Q.0** solely on
this evidence. The next investigation is the isolated MVS FB80 QSAM test.
