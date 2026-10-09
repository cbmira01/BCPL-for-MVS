# Native BCPL stream and character-I/O march

Status: **OPEN — evidence and interface design** (2026-10-09)

Entry baseline: operator-confirmed **90 PASS / 0 FAIL** for native
regressions 000–089 under TK5/MVS 3.8J. The FINISH/STOP runtime-exit
march is **CLOSED**; do not modify its proven termination semantics
without a specific regression need.

## Historical surface and current implementation

The surviving `richards-bcpltape/sys3/bcpl/libhdr` assigns:

| Global | Interface |
| --- | --- |
| 11, 12 | SELECTINPUT, SELECTOUTPUT |
| 13, 14, 15 | RDCH, WRCH, UNRDCH |
| 16, 17 | INPUT, OUTPUT |
| 18, 19 | INCONTROL, OUTCONTROL |
| 23–26 | READREC, WRITEREC, WRITESEG, SKIPREC |
| 35 | REWIND |
| 41, 42 | FINDOUTPUT, FINDINPUT |
| 46, 47 | ENDREAD, ENDWRITE |

The header also declares `ENDSTREAMCH=-1`. Historical BLIB uses
`FINDOUTPUT("SYSPRINT")`, `SELECTOUTPUT` and `RDCH`.
The reconstruction's `library/line-io.bcpl` already uses `RDCH`
and `ENDSTREAMCH` to implement READLINE, but cannot yet run
natively without a compatible input primitive.

Canonical `asm/bcplmain-wip.asm` currently installs G!14 WRCH
only. It appends a character to a single 132-byte SYSPRINT
buffer; it has no general selected-stream state, newline-record
handling or multi-record output. QSAM BCPOUT is opened at startup
and explicitly closed by FINISH/STOP. Do **not** conflate this
bootstrap output path with the historical full stream contract.

## First narrowly scoped objective

Establish repeatable **sequential character input** from a named
MVS DD, with a clear record-to-character contract, without changing
the proven output path. Use a dedicated input DD such as `BCPIN`
in native GO JCL, rather than relying on implicit DD discovery.

Research and document before coding:
1. The original Cambridge System/370 `RDCH` newline and EOF
   behavior, and whether physical 80-column records are trimmed
   or retained. Distinguish evidence from implementation choices.
2. The JCL runner's GO-step DD injection capability and how to
   carry deterministic fixture records to TK5 (including a
   reopened/closed input dataset if needed).
3. Input DCB/DCBE and buffer ownership, EBCDIC character
   representation, QSAM GET semantics, EOF/EODAD branch, and
   the expected native-primitive ABI: R7 result, return via R6,
   restore caller base R4 from 0(R5), preserve R0/R1–R3.
4. How RDCH relates to a selected input stream and to eventual
   UNRDCH; do not accidentally freeze a single-input design
   as the final multi-stream ABI.

## Proposed test ladder (numbers provisional)

- **090**: one character read from a deterministic input record,
  print its value through existing WRCH.
- **091**: two records, confirm the chosen record-boundary /
  newline convention with no dependence on trailing blank padding.
- **092**: EOF via ENDSTREAMCH=-1, including repeated calls
  after end-of-data (after contract review).
- **093**: READLINE from existing `library/line-io.bcpl`,
  linked through the native object machinery if feasible.
- **Later**: UNRDCH; INPUT/OUTPUT and SELECTINPUT/SELECTOUTPUT;
  FINDINPUT/FINDOUTPUT; ENDREAD/ENDWRITE; multiple output
  records; dataset/member discovery; REWIND for supported
  reopenable datasets.

The test numbers and exact expectations are not yet executable
commitments. The first implementation rung should remain
deliberately small, subject to verifying historic character/record
semantics and GO DD setup.

## Acceptance and boundaries

- Preserve 90/90 baseline while investigating.
- Add one or two tightly scoped input regressions and obtain TK5
  evidence **before** promoting a more general stream abstraction.
- Keep BCPLMAIN source-card constraints and preflight scripts
  in `tools/checks/`.
- Avoid claiming that all DD *, JES in-stream datasets, concatenated
  DDs, PDS members, and physical sequential DASD datasets support
  identical rewind/close semantics.
- Closure requires focused and complete native regression acceptance;
  retain the FINISH/STOP cleanup guarantees for any newly opened DCB.

## Dependency-audit handoff — 2026-10-09

The source-traced inventory at
`native-compiler/runtime-dependency-audit.md` identifies selected
stream I/O as a **native compiler bootstrap blocker**, not merely
general-purpose library enhancement. The compiler master itself
uses FINDPARM, FINDINPUT/FINDOUTPUT, SELECTINPUT/SELECTOUTPUT,
RDCH, UNRDCH, INPUT/OUTPUT, ENDREAD/ENDWRITE and WRAPOUTPUT;
LEX reads GET files through named input streams. Compiler listing
and generated CODE require multiple logical output streams rather
than a single SYSPRINT buffer.

The audit also highlights independent blockers: current G!0..200
capacity versus larger resident compiler global slots, and the
master's APTOVEC(COMP, size) workspace contract. Resolve these in
parallel with stream design, not by extending the MR10-oriented
native extension-library candidates. Historical records and
binary SYSGO output remain separate phases.
