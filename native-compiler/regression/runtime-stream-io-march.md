# Native BCPL stream and character-I/O march

Status: **OPEN — selected-stream I/O implementation planning** (2026-10-09)

Entry baseline: operator-confirmed **94 PASS / 0 FAIL** for native
regressions 000–093 under TK5/MVS 3.8J. The FINISH/STOP runtime-exit
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

- Preserve 94/94 baseline while investigating.
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

## Restart after APTOVEC closure (2026-10-09)

The Capacity/APTOVEC march closed after **94/94** native regressions
passed. The older provisional 090–093 list above is historical planning
only: those numbers are now assigned to capacity/APTOVEC. Selected-stream
I/O regression identities start at **094**.

### Runtime interface and data-contract boundaries

Historical Cambridge LIBHDR assigns `SELECTINPUT:11`, `RDCH:13`,
`UNRDCH:15`, `INPUT:16`, `FINDINPUT:42`, `ENDREAD:46`, and
`ENDSTREAMCH=-1`. A name/slot assignment is not a complete statement
of stream-handle representation or call-time error behavior. In
particular, a direct RDCH connection to SYSIN is insufficient to claim
selected-stream I/O is implemented. The eventual design needs a stream
handle usable by FINDINPUT/SELECTINPUT/INPUT/ENDREAD, with a cursor,
record metadata, EOF state and unreading state per input stream.

Inspection of `native-compiler/regression/run-test.sh` confirms that
the regression job-generator currently alters GO EXEC TIME but does
not provide a general per-test GO-step input-DD facility. This should
be addressed **before** putting QSAM reads in canonical BCPLMAIN.
Never assume an existing JES in-stream DD can be rewound; reopening
must be tested separately with a suitable dataset type.

### First executable implementation rung: 094

**094 — deterministic named input DD and selected RDCH:**

- Add an opt-in regression fixture file, for example `input.records`,
  explicitly attached as a GO-step DD named `BCPIN`; use FB/80 or an
  explicitly specified record format. The runner must reject unsafe
  fixture/JCL delimiters and avoid changing jobs without a fixture.
- Implement the minimal stream handle needed to obtain the stream from
  `FINDINPUT("BCPIN")`, select it via `SELECTINPUT`, and retrieve the
  first EBCDIC character via `RDCH`. Preserve permanent S/370 BCPL
  registers, R4 caller-base restoration and MVS DCB ownership.
- For the first positive test use a known leading character and call
  existing WRCH to report it. Do **not** yet require newline/EOF
  semantics for record transitions; document those as the next tests.
- Keep `FINISH`/`STOP` close/cleanup contracts intact. Record the
  choice of lazy OPEN versus eager OPEN before implementing it.

**095 onward:** deterministic record-boundary/newline and EOF behavior;
UNRDCH and repeated EOF; explicit ENDREAD and handle switching; then
output streams and compiler-facing `FINDPARM`/WRAPOUTPUT support.

**Validation gate:** first run local repository checks on the complete
staged source (not merely isolated snippets), then TK5 focused test
094, and finally a full 000–094 panel. Do not report any of these as
passing until run. No I/O implementation code was changed by this
planning checkpoint.

### Fixture transport checkpoint

Native regression runner `run-test.sh` now conditionally injects
`//BCPIN DD DATA,DLM=ZZ` when the test has an `input.records`
fixture. This is an **opt-in JCL transport facility**, not an
implementation of FINDINPUT or RDCH. It rejects empty fixture sets,
over-80-column records and JCL/delimiter-looking record prefixes.
Tests without `input.records` retain their former GO deck shape.

Local synthetic fixture-transport unit tests passed for: absent
fixture/no changes, two input records and invalid record rejection.
The runner change itself remains **pending TK5 acceptance** and
BCPLMAIN has not yet gained a selected-input primitive. In
particular, no 094 regression has yet passed.

The documentation preserves the operator-confirmed 94/94 entry
baseline but does not claim those cases were rerun after this
runner-only change.

## First executable rung submitted — regression 094

Current candidate installs G11 `SELECTINPUT`, G13 `RDCH`, and G42
`FINDINPUT` in `asm/bcplmain-wip.asm`. It recognizes only the
length-prefixed EBCDIC BCPL string `"BCPIN"`, lazily opens a QSAM
input DCB named BCPIN, and returns a word-address stream handle.
`SELECTINPUT` installs the selected handle; `RDCH` retrieves bytes
from a fixed 80-byte record and eventually returns ENDSTREAMCH=-1
via its EODAD path. This is a **single-input bootstrap adapter**,
not yet a general historical stream implementation.

Regression `094-selected-input-first-character` transports the
`input.records` fixture via the GO BCPIN DD, requests the stream,
selects it, and prints its first character via WRCH. Expected: `A`.
Successful source-level width/anchor review is **not** IFOX or GO
acceptance. **094 remains pending TK5**. Its execution will also
test the JCL in-stream fixture and QSAM DCB assumptions together.

The first fixture implementation uses a JCL DD DATA delimiter `ZZ`;
the reader injects it only for tests with `input.records`.
No ENDREAD or multi-stream cleanup is yet provided. The rest of the
94-test baseline must be rerun after 094 is accepted.

## Regression 094 — first GO attempt, termination correction

Operator's TK5 JOB 3888: IFOX **RC=0000**, IEWL **RC=0000**,
the BCPL output was `A`, but GO reported an abnormal/nonzero
completion (regression wrapper RC=1; job summary GO RC=0155,
raw IEF142I condition code 5915). Therefore **094 FAILED**.

This establishes that named FINDINPUT, SELECTINPUT, first QSAM GET,
RDCH and WRCH reached their expected functional output path; it does
**not** establish correct termination or complete stream semantics.

First repair candidate: FINDINPUT lazily OPENs BCPIN but FINISH/STOP
only CLOSED BCPOUT. Termination now conditionally CLOSEs BCPIN
if INOPEN is set, before RELMEM and MVS return. This is a
lifetime/cleanup repair consistent with the existing runtime contract,
but **causation of the nonzero completion remains unproven** until TK5
retest. The code was checked in the execution environment for
71-column source width, labels <=8 characters, and stable BLIB
injection anchors; the actual Python check-native-runtime.py was
not executed in that environment.

Next: focused `tools/run-native-regression 94 --show-output`.
Do not advance to 095 unless output and GO completion both pass.

## Regression 094 accepted under TK5

Operator retested after the conditional BCPIN CLOSE repair at commit
`f9130df`:

```text
NATIVE REGRESSION  094..094  (1 tests)
RUN   094  094-selected-input-first-character
=== BCPL output ===
A

PASS  094  094-selected-input-first-character
NATIVE REGRESSION COMPLETE
PASS  1
FAIL  0
TOTAL 1
```

**094 is ACCEPTED.** The test verifies `FINDINPUT("BCPIN")`,
`SELECTINPUT`, one `RDCH` from a JES-supplied input DD, output
via WRCH, and normal termination. The first run produced correct output
but a nonzero GO completion; closing the lazily opened BCPIN DCB on
FINISH/STOP was followed by the passing retest. This is evidence of
successful cleanup for this case, not proof of general stream semantics.

The selected-stream I/O march remains **OPEN**. Regression 095 should
establish record-boundary/newline behavior; later tests must cover EOF,
UNRDCH, ENDREAD, multiple selected handles, and output streams.
A full native panel after the input changes has not yet been reported.

## Regression 095 candidate — two physical records

The BCPLMAIN RDCH adapter now trims trailing EBCDIC blanks from each
physical 80-byte fixed-length BCPIN record; interior blanks are
preserved. It returns BCPL character value 10 exactly once at each
physical record boundary, then fetches the next QSAM record. The
per-record position and pending-newline flag (`INNL`) are maintained
within the first one-stream adapter.

Test `095-selected-input-record-boundary` passes fixture records
`A` and `B` and displays the newline as `|`: expected `A|B`.
The trim/newline convention is provisional implementation policy, not
proof of the original Cambridge MVS treatment of blanks.

**Status: PENDING TK5.** Repository-fetched full-source static checks
confirmed no overlong source cards, tab/trailing whitespace, or
over-eight-character label definitions, and both stage-2 injection
anchors remain uniquely present. The actual local Python
`check-native-runtime.py` command could not be run because the GitHub
checkout was not available in the execution container. Do not claim
IFOX or GO success. First test 095, then repeat 094.

## Regression 095 TK5 attempt — character transport mismatch

Operator JOB 3893 completed Cambridge compile, IFOX assemble,
IEWL link-edit, and GO successfully (GO RC=0000). The output
comparison failed: the native GO SYSPRINT record appeared in
host-recovered text as `A�B` instead of expected `A|B`.

The BCPL test compares the boundary's RDCH value to 10 and
prints the display marker only on equality. Thus the observed
middle glyph suggests a host text-transport rendering problem
with EBCDIC `|`, rather than an incorrect boundary return,
although successful comparison must still be demonstrated.

Regression 095's display marker is changed to slash (`/`),
with expected `A/B`; runtime assembler is unchanged. Status
remains **PENDING TK5** and 094 remains the accepted baseline.

## Regression 095 accepted under TK5

After changing the test-only newline display marker from pipe to slash,
the operator pulled commit `87ee8e5` and ran
`tools/run-native-regression 95 --show-output`.
The BCPL output was `A/B`; the harness reported `PASS 1`, `FAIL 0`,
`TOTAL 1`. **095 ACCEPTED.** This establishes the first two-record
character stream with an inserted logical newline (value 10) for this
FB80 input fixture. The input adapter's trailing-blank trim remains a
provisional convention rather than a verified general historical rule.

Next checkpoint: repeat 094 to establish no regression in the earlier
single-character path; then progress to explicit EOF behavior in 096.
The complete 000–095 panel has not yet been rerun.

## Regression 094 compatibility retest after 095

Operator ran `tools/run-native-regression 94 --show-output` after
accepting 095. Output was `A`; harness reported PASS 1, FAIL 0,
TOTAL 1. Therefore **094 remains green against the 095 runtime**.
Together 094 and 095 are independently accepted. Next proposed
milestone is 096, repeated RDCH EOF after final record. Full panel
still not verified against this runtime.
