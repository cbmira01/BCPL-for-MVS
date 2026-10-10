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

## Regression 096 candidate — EOF after final input record

The operator has confirmed 094 remained PASS 1/1 after 095 was
accepted. Regression 096 is added with one BCPIN record (`A`).
It expects four RDCH results in order: `'A'`, `10` (logical
newline), `-1` (EOF), and `-1` again (persistent EOF). It
renders these as `A/EE` using slash to avoid the problematic
host rendering of the pipe character.

No BCPLMAIN change is required in this first attempt: the existing
QSAM EODAD branch marks INEOF, and the RDCH entry tests INEOF
before attempting another GET. **096 status: PENDING TK5.**
095 and 094 are the independently accepted baselines.

If 096 passes, the next step should focus on the historical
UNRDCH/ENDREAD semantics with explicit tests, not assume that
this one-input-stream implementation is production-complete.

## Regression 096 accepted under TK5

Operator pulled commit `c20a6ce` and ran
`tools/run-native-regression 96 --show-output`. Observed BCPL output
`A/EE`; harness reported PASS 1, FAIL 0, TOTAL 1. **096 ACCEPTED.**
This verifies the one-record sequence 'A', logical newline 10, first
EOF -1, and repeated EOF -1, with the existing EODAD/INEOF logic.
No new BCPLMAIN change was required for regression 096.
Next planned regression is 097, UNRDCH one-character pushback; confirm
its actual interface from project sources before implementing.
Full 000–096 native suite has not been rerun.

## Regression 097 candidate — one-character UNRDCH

The 1974 Cambridge IBM System/370 BCPL manual, section 2.8.1,
specifies zero-argument `UNRDCH()`: the following `RDCH()`
returns the same character as the preceding read on the currently
selected input stream.

The WIP runtime now publishes G!15 and retains the latest RDCH
result, a valid-result flag, and a single pending pushback flag.
Pending pushback is examined before INEOF so a previous result
can be repeated without repositioning the underlying QSAM DCB.
Only one selected stream is supported.

Regression `097-selected-input-unrdch` reads physical records A
and B; it pushes back A, the logical newline, and B. The expected
single buffered SYSPRINT output is `AA//BB`.

Status: **PENDING TK5**. Direct source checks against the complete
modified assembler verified ASCII-safe content, no lines beyond
71 columns, no tabs/trailing whitespace, no labels longer than
8 characters, and unique existing BCPLMAIN CSECT and GIDONE BLIB
injection anchors. The executable Python
`tools/checks/check-native-runtime.py` was not run: the tool
environment cannot clone the GitHub repository. These source-level
checks are not represented as completion of that executable gate.
No runtime execution or regression panel pass is claimed.

## Regression 097 accepted under TK5

Operator pulled `2284bfd` and ran `tools/run-native-regression 97 --show-output`.
Observed BCPL output `AA//BB` and harness PASS 1 / FAIL 0 / TOTAL 1.
**097 ACCEPTED.** The test exercises one-character UNRDCH pushback of
an ordinary character, the logical newline separating two input records,
and the first character of the second record.

Individual native regressions 094–097 are now accepted. A full 000–097
panel following the 097 runtime change has not yet been executed.
Next proposed milestone: ENDREAD lifecycle and explicit CLOSE, subject
to inspection of historical interface and existing handle semantics.

## Full 000–097 panel: one tooling failure, repaired pending retest

Operator ran `tools/run-native-regression` after accepting 097.
Result was **97 PASS / 1 FAIL / 98 TOTAL**. The only failure was
083-instrumented-storage-reclamation, where its Python test-local
instrumenter rejected the prior strict source anchor
`FINRETN  CLOSE (BCPOUT)\n         BAL   14,RELMEM`.
The stream-I/O work had inserted the conditional BCPIN CLOSE between
those two statements; 083 therefore failed before assemble/link/GO.
All 094–097 tests PASS in the full panel.

Commit `08773ea` changes 083's instrumenter to match and replace
just `FINRETN  CLOSE (BCPOUT)` with `FINRETN  EQU   *` in the generated
copy, preserving conditional BCPIN closure while leaving BCPOUT open
for its post-RELMEM diagnostic PUT. An independent in-memory
simulation of the five transformations against current BCPLMAIN found
unique anchors, no source-card width/label/whitespace violations and
retained BCPIN CLOSE. **083 pending TK5 retest; a clean full panel is
not yet confirmed.**

## Regression 083 second retest — GO completion RC=0155

Operator's retest after the instrumentation anchor repair successfully
compiled and linked (IFOX and IEWL RC=0000), emitted both expected
records `42` and `V=2 M=1`, but ended GO with RC=0155. Job 4102's
assembler listing shows the instrumented `FINRETN EQU *` suppressing
BCPOUT CLOSE while `RELDONE` issues a final PUT without subsequent
CLOSE. This differs from canonical normal termination and resembles
the unclosed-DCB symptom previously encountered in regression 094.

Commit `1454e1a` moves `CLOSE (BCPOUT)` after `PUT BCPOUT,OUTBUF`
in the test-local RELDONE instrumentation. BCPIN conditional closure
in the canonical exit path remains undisturbed. This is a focused
**hypothesis**, not yet TK5-confirmed. Regression 083 and the fully
green 000–097 suite remain pending that retest.

## 083 third retest: register restore ordering defect isolated

Operator job 4104 produced both `42` and `V=2 M=1`, ASM/LKED
RC=0000, but GO RC=0153 (previously 0155 without test-local BCPOUT
CLOSE). The IFOX listing revealed canonical FINEXIT executes
`LM 14,12,12(13)` and only then `L 15,STOPRC`. The restore changes
R11, which is the assembler base used to address STOPRC. This causes
the completion-code load to use a stale caller R11 and explains the
unreliable GO RC even after successful cleanup.

Commit `9e9cccb` moves `L 15,STOPRC` ahead of caller-register restore
and replaces the wraparound load-multiple with separate `LM 14,14`
and `LM 0,12`, skipping R15 so it retains the chosen return code.
This corrects canonical native FINISH/STOP exit linkage rather than
loosening regression 083. **Pending TK5 retest of 083, then full
000–097 panel** because canonical BCPLMAIN changed.

## Regression 083 accepted after FINEXIT repair

Operator pulled `ee37a34` and ran
`tools/run-native-regression 83 --show-output`. The observed BCPL
output was `42` followed by `V=2 M=1`. The harness reported
**PASS 1 / FAIL 0 / TOTAL 1**. This accepts the focused 083 repair:
test-local output CLOSE after final diagnostic PUT and canonical
FINEXIT completion-code retrieval before caller register restore.
The preceding complete 000–097 suite had 97 passes and only 083
failed; **fresh 000–097 full-panel verification against the latest
canonical FINEXIT change is still pending**.

## Complete 000–097 panel accepted — 2026-10-10

Operator pulled repository commit `3ba85f9` and ran the unqualified
`tools/run-native-regression` command, thereby rerunning the entire
native suite after canonical FINEXIT was corrected. The displayed
harness summary was **PASS 98 / FAIL 0 / TOTAL 98**. Regression 083
produced `42` and `V=2 M=1` and PASSED; FINISH/STOP cases 084–089
PASSED; selected-input cases 094–097 PASSED with their expected output.
**Accepted 000–097 baseline on TK5 / MVS 3.8J.** This acceptance
covers the present regression contracts, not untested production I/O
semantics. March remains open for 098 (ENDREAD/explicit input close).

## Regression 098 candidate — ENDREAD and reopen

The historical 1974 System/370 manual states that zero-argument
`ENDREAD()`, G!46, closes the currently selected input stream.
The current WIP publishes G!46 and closes the single selected
`BCPIN` DCB, clears the selection, resets EOF/newline/pushback,
and resets the next-read position. A subsequent `FINDINPUT("BCPIN")`
opens that DD again with fresh read state. All QSAM CLOSE paths save
the BCPL machine registers.

The regression reads A, closes the selected input, checks the
bootstrap no-selected-stream RDCH policy (-1), reopens BCPIN,
reads A again and then its logical newline. Expected output `AEA/`.
Its fixture has two physical input records A and B; this proves
restart without relying solely on a one-record EOF transition.

**PENDING TK5**: this commits a test candidate, not an accepted
result. The source-level assembler-card width/whitespace checks
passed; no TK5 assemble/link/GO run has yet occurred. Baseline
000–097 is independently accepted with 98/98 PASS.

## Regression 098 accepted under TK5

Operator pulled `7374c24` and ran `tools/run-native-regression 98 --show-output`. The observed output was `AEA/`, with harness **PASS 1 / FAIL 0 / TOTAL 1**. **098 ACCEPTED.** The test establishes G!46 ENDREAD closing the selected BCPIN stream, provisional no-selection RDCH EOF (-1), and successful reopening from the first record with newline handling. The last full native panel remains 000–097 at 98/98 PASS; a complete 000–098 panel has not yet been rerun after ENDREAD was added.

## Full 000–098 suite accepted — 2026-10-10

Operator pulled `965a57e` and ran `tools/run-native-regression` without a test-number filter. The harness executed regressions 000–098, including 083 storage-reclamation instrumentation, 084–089 FINISH/STOP, and 094–098 selected-input stream I/O. All passed: **PASS 99 / FAIL 0 / TOTAL 99**. Output for 098 was `AEA/`. This establishes an accepted full-suite 99/99 TK5 / MVS 3.8J baseline after the G!46 ENDREAD implementation. This does not imply broader multistream or production-QSAM coverage beyond the exercised regressions.

## Batch candidate 099–103 — awaiting sequential TK5 execution

User approved staging five regressions together, with **sequential**
operator acceptance. Compatibility target: historical Cambridge BCPL
API where known, explicitly provisional TK5 FB80 text conventions
elsewhere. Output must support at least two simultaneously OPEN DDs.

The candidates are:

- 099: push back immediately after EOF, then verify stable repeated EOF.
  Deterministic BCPIN input; expected `A/EEE`.
- 100: a zero-content text fixture record transported as blank-padded
  FB80, contributing one logical newline; expected `A//B`.
- 101: open both SYSPRINT and BCPALT, select alternately, confirm
  independent output destinations; default `AC`, alternate `B`.
- 102: while both DDs remain OPEN, newline-delimited output records
  in BCPALT; default `Z`, alternate lines `A` and `B`.
- 103: ENDWRITE flushes pending BCPALT text, CLOSEs its DCB, and
  subsequent WRCH uses default SYSPRINT; default `Z`, alternate `Q`.

Runtime candidate installs G!41 FINDOUTPUT, G!12 SELECTOUTPUT, G!47
ENDWRITE and a BCPALT descriptor/DCB separate from SYSPRINT. For
limited bootstrap compatibility, default SYSPRINT retains existing
output-buffer semantics; the new BCPALT path treats character 10 as
a logical record boundary. Unsupported overflow currently stops
appending to its 132-byte buffer; this is a **known limitation**,
not an accepted no-truncation contract. A future independent error
policy must be established before calling output production-ready.
The runner conditionally injects a BCPALT SYSOUT DD when a test has
`expected-alt.txt`, and checks its content in post-link job output.
The post-link search is not yet a strict JES DD identity check;
that evidence limitation must be evaluated during 101 acceptance.

Source width and unique-label checks were applied to the assembled
runtime source text, and fixture/run-script anchors were checked.
**No IFOX, IEWL or GO execution has been performed** for these
candidates; all 099–103 are PENDING. The last complete accepted
suite remains 000–098 with **99 PASS / 0 FAIL**.

## 099 first TK5 attempt — assembler-card preflight failure

Operator attempted 099 on 2026-10-10. Cambridge compiler JOB 4517 passed; native deck preflight rejected `OUTRESULT` (nine-character IFOX label) at combined-source line 2020. Native ASM/LKED/GO were not run; this is **not** an EOF/UNRDCH behavior result. Commit `f7bc1ab` renames all three occurrences to `OUTRES`. An audit of canonical BCPLMAIN's instruction-column symbol definitions found no further labels longer than eight characters. Focused 099 TK5 retest remains pending; 000–098 stays the last verified 99/99 full-suite baseline.

## Focused 099–103 TK5 results — 2026-10-10

Operator ran each regression sequentially following the IFOX-label fix: 099 output `A/EEE` PASS; 100 output `A//B` PASS; 101 SYSPRINT output `AC` PASS; 102 SYSPRINT output `Z` PASS; 103 SYSPRINT output `Z` PASS. Each wrapper summary reported PASS 1 / FAIL 0 / TOTAL 1. Review of committed `run-test.sh` confirms that successful normal-return runs invoke `show_alt_output` for tests carrying `expected-alt.txt`, requiring expected alternate records in the post-link report (101 B; 102 A then B; 103 Q). Wrapper transcript exposes only primary BCPL output, and DD-specific SYSOUT identity has not been independently verified. Thus 101–103 satisfy current runner assertions, not yet independent DD isolation proof. Full 000–103 acceptance still pending; most recent full panel remains 000–098 at 99/99. The alternate 132-byte output buffer's overflow policy remains provisional.

## Complete native regression panel 000–103 accepted — 2026-10-10

Operator pulled commit `4dc4253` and ran `tools/run-native-regression` without filtering. Every case through 103 passed: **PASS 104 / FAIL 0 / TOTAL 104**. Specifically, 099 and 100 returned `A/EEE` and `A//B`; 101–103 produced primary output `AC`, `Z`, and `Z` respectively and passed the existing secondary-output assertions. This establishes the 000–103 TK5 / MVS 3.8J full-suite checkpoint. The same earlier qualification applies: the post-link alternate-output assertion is not an independent DD-identity check, and overlength output behavior remains unfinished. Next series should focus on compiler-facing INPUT/OUTPUT, stream switching, FINDPARM/WRAPOUTPUT, and multistream semantics, with acceptance gates decided before implementation.

## Batch 104–109 staged for sequential operator testing

Entry checkpoint: all 104 regressions 000–103 PASS under TK5 (reported 2026-10-10). Candidate files for 104–109 have been committed together. Current expected results: 104 IA (INPUT G16); 105 SYSPRINT DS and BCPALT A (OUTPUT G17); 106 SYSPRINT ACE and BCPALT BD (switch partial buffers); 107 AY1B2 (two independent input DDs BCPIN and BCPINB, distinct record positions); 108 P (FINDPARM G39 using a provisional BCPIN text-stream bridge); 109 SYSPRINT Z and BCPALT records A/B (WRAPOUTPUT G33 as provisional logical-record flush). The runner supports opt-in input-b.records for the BCPINB DD and expected-alt.txt for BCPALT. All six remain **PENDING TK5**; none is accepted by source inspection.

Compatibility caution: the provisional FINDPARM bridge does not decode MVS EXEC PARM, and the provisional WRAPOUTPUT behavior is NOT established as historically equivalent to the Cambridge interface. The current SYSPRINT path remains legacy single-buffer and differs from the BCPALT newline implementation. The 132-column output overflow contract and strict JES DD identity attribution remain follow-on engineering tasks. In particular the current post-link alternate-output textual check is insufficient to independently establish DD identity. Acceptance of 105, 106, and 109 therefore proves their current harness contract, not physical routing identity.

Static checks on canonical BCPLMAIN: no assembler source lines beyond column 71, no duplicate assembler labels, and no labels exceeding eight characters. All new BCPL test files end in newline. These checks do not replace actual IFOX, IEWL, and GO evidence. Test in increasing numerical order; stop at first failure and repair without weakening expectations.

## 104 first native TK5 attempt: assembler addressability

Operator ran regression 104 after the 104–109 batch commit. Cambridge compilation JOB 4740 succeeded, source preflight passed, but native JOB 4741 IFOX returned RC=0008 and bypassed link-edit/GO. The IFOX listing identified many IFO209 addressability errors: static controls at the end of BCPLMAIN now lie beyond the 12-bit unsigned displacement reachable with the runtime SYSV R11 base; startup R10 also cannot reach those remote controls. This is an addressability failure, not an INPUT() behavior result. No expected output or test assertions were relaxed.

A proposed relocation before SYSV was committed then reverted without TK5 execution because runtime R11 cannot address data preceding SYSV. The current candidate instead uses a local address literal to establish the runtime MVS save area, makes its stable R13 a separate assembler data base via `USING MSVSAVE,13`, moves MSVSAVE to the beginning of the static controls, and delays `ST 3,MODBASE` until this base is active. It retains R11 as the mandated system-vector base and R12 as global-vector base. **Pending 104 TK5 IFOX/LKED/GO retest; this register-base repair is not yet accepted.**

## Focused 104–109 TK5 acceptance — 2026-10-10

Operator pulled commit `262b664` and verified `USING MSVSAVE,13` in BCPLMAIN at source line 599. Regression 104 compiled, assembled, linked, ran, and passed with primary output `IA` (PASS 1 / FAIL 0). Then operator ran `tools/run-native-regression 105 109 --show-output`; all five passed (PASS 5 / FAIL 0): 105 `DS`, 106 `ACE`, 107 `AY1B2`, 108 `P`, 109 `Z`. These are six focused passes, **not yet a full-suite 000–109 acceptance**. Secondary BCPALT output for 105/106/109 is checked by the current harness but physical JES DD-specific attribution remains unproven. FINDPARM and WRAPOUTPUT are still documented provisional TK5 bootstrap contracts. The R13 assembler base repair resolved the reported IFOX addressability failure for 104. Next mandatory gate: unfiltered `tools/run-native-regression`, target 110 PASS / 0 FAIL / 110 TOTAL.

## Full-suite checkpoint and 110–119 behavioral candidates — 2026-10-10

Operator ran the complete native panel against commit `de579af`: **110 PASS / 0 FAIL / 110 TOTAL**, cases 000–109. This is the last independently established full-suite baseline.

The 110–119 candidates were staged together and remain **PENDING TK5**. Expectations: 110 SYSPRINT A/B as two logical records; 111 A/blank/B; 112 exact 132 A characters followed by Z; 113 133rd character triggers controlled GO RC=0012 (new `expected-go-rc.txt` fixture); 114 interleaved SYSPRINT AB/C and BCPALT 1/2; 115 close/reopen BCPALT A/B, default YCZ, and closed-handle selection rejection; 116 unknown FINDINPUT/FINDOUTPUT names both return zero while input/output selections remain unchanged (IOAD); 117 EOF and UNRDCH isolation across BCPIN/BCPINB (AEBE); 118 ENDREAD and reopen preserve other input position (1A2A); 119 FINISH drains partial buffers of both streams (SYSPRINT A, BCPALT B).

Runtime candidate: WRCH(10) on default SYSPRINT now emits a QSAM FB132 record and resets its buffer; both default and alternate FB132 output paths branch to STOP(12) on a 133rd character instead of silently truncating. Native regression runner accepts `expected-go-rc.txt` for intentional nonzero GO completion; test 113 does not expect a stdout fragment. All ten BCPL source files satisfy source-line width <=71 and terminate with newline; BCPLMAIN has no lines >71, no duplicate labels, and no labels >8 characters. These static checks **do not establish IFOX or GO correctness**. The stdout and alternate-output checkers still use text matching after linker authorization; they **do not yet prove JES DD identity or exact fixed-record whitespace**. Their existing looseness must not be mistaken for verified strict record attribution. Strengthen using real TK5 report examples before claiming that contract closed. Run tests sequentially, stop at first failure, and rerun the complete panel when 110–119 are accepted.

## TK5 focused 110–114 attempt and 114 branch repair — 2026-10-10

After pulling `930d44f`, operator ran 110–114 in order. **110 PASS** (`A`, `B`); **111 PASS** (`A`, empty logical record, `B`); **112 PASS** (132 A characters and Z); **113 PASS** (the harness accepted the expected controlled GO RC=0012). Regression **114 FAIL**: Cambridge compile JOB 4988 succeeded; IFOX/IEWL JOB 4989 each RC=0000, but GO RC=0012 instead of expected zero. Inspection of the IFOX source listing proves that successful `WO2PUT` execution flowed directly into `WROVFL2` after clearing OUT2BUF; the new overflow handler incorrectly fired on every BCPALT newline. Minimal correction inserted unconditional `B WO2RET` after the newline buffer reset and before `WROVFL2`. Source-level checks: no line beyond column 71, duplicate labels, or >8-character labels. **114 remains PENDING TK5 retest**; 115–119 have not been executed. No test expectations were weakened. Full suite remains last accepted 000–109 (110/110 PASS).

## 114 accepted, 115 Cambridge syntax correction — 2026-10-10

Operator pulled `d791483` and reran 114: primary output `AB` and `C`, harness PASS (1/1), with BCPALT expectations checked by the existing runner. 115 failed *during Cambridge compilation*, not during IFOX or GO: JOB 4992 ICINT19 reported `Syntax error near line 13: Error in command`, immediately before a `LET` following executable statements. Regression 115 declared `LET T=FINDOUTPUT("BCPALT")` midway through the block; corrected to an initial `LET T=0` alongside declarations and subsequent `T :=FINDOUTPUT("BCPALT")`. Applied identical proactive correction to 118 (`LET T=FINDINPUT("BCPIN")` after executable statements). No expected text changed; 115 and 118 remain pending compiler/native rerun. All touched sources <=71 columns and newline terminated. Next operator test: 115, then continue sequentially.

## 115 accepted; 116 Cambridge declaration-order correction — 2026-10-10

After pulling `6fd70d6`, operator ran 115 and got expected primary `YCZ` and harness PASS 1/1; the runner also checked `expected-alt.txt` (subject to previously documented attribution limitations). 116 compilation JOB 4995 failed with `Syntax error near line 9: Error in command ... LET`; assembler and GO were not entered. Source had `SELECTINPUT(A)` before `LET I=...` and `LET O=...`. Moved `LET I=0; LET O=0` into the initial declaration sequence and made later discoveries assignments (`I := FINDINPUT(...)`, `O := FINDOUTPUT(...)`). Retained expected `IOAD` and failed-discovery selection-preservation assertions. Inspected 117 and 119 for the same misplaced declaration pattern; neither had a late LET. Source line-width check passed. **116 remains pending TK5 retest.**

## Focused 110–119 acceptance complete — 2026-10-10

Operator pulled commit `1318b05` and executed four remaining native tests sequentially: 116 PASS (`IOAD`), 117 PASS (`AEBE`), 118 PASS (`1A2A`), 119 PASS (`A`). Earlier TK5 runs established 110–115 PASS, including 113 expected controlled GO RC=0012, 114 BCPALT newline fallthrough repair, and 115 declaration-order correction. **All ten focused regressions 110–119 have now passed under TK5, separately.** This is not yet complete-panel acceptance: last full suite was 000–109, 110/110 PASS. Next acceptance gate: `tools/run-native-regression`, expected 120 PASS / 0 FAIL / 120 TOTAL. The runner's `expected-alt.txt` verification still matches the post-link job report and has not yet established physical JES DD attribution or exact FB132 record whitespace. Do not claim stream behavioral-contract completion until this independent record-level validation is addressed and full suite remains green.

## Full native regression acceptance — 2026-10-10

Operator pulled commit `04d607b` and ran `tools/run-native-regression` across native tests **000–119**, obtaining **PASS 120 / FAIL 0 / TOTAL 120**. This is the first complete-panel acceptance following the 110–119 stream-behavior candidate march. Individual cases 110–119 also passed in sequence. The current harness uses post-link report text matching and does not yet independently attribute alternate output to a specific JES DD or prove exact FB132 record contents; this full-panel pass establishes compatibility of the current implementation with the existing assertions, not completion of that stricter validation objective. Next work: improve output/DD record validator using real JES evidence, document the frozen stream contract, then modularize BCPLMAIN.

## Combined JES validator tightening and stream-contract document — 2026-10-10

Introduced `tools/checks/check-combined-jes-records.py` and its independent unittest driver `tools/checks/test-combined-jes-records.py`. The regression runner now uses this helper on nonempty expected primary and alternate output. It searches only after the final linker authorization boundary; requires contiguous ordered records; treats empty expected lines as real records; preserves leading blanks and interior spaces; and rejects empty expectations. **This is NOT physical JES DD attribution**: dump-report-for-job yields a combined printer report without reliable source-DD labels, and physical trailing FB132 spaces are still not provable. The helper explicitly reports DD attribution NOT VERIFIED. Expected nonzero GO RC fixtures remain supported. Wrote `native-compiler/regression/native-stream-contract.md` enumerating documented interfaces, observed lifetime/buffering/error semantics, the incomplete historical services and QSAM error limitations, and the precise unverified record-evidence boundary. Runtime code and existing regression expected output files are unchanged. **Changed runner is NOT YET TK5-validated.** Suggested gate: run `python3 tools/checks/test-combined-jes-records.py`, then `tools/run-native-regression 110 119 --show-output`, stop on failure, then full `tools/run-native-regression` (120/120 target). A subsequent separate JES spool extraction exercise is required for real DD-scoped record verification.

## Strict combined-report validator focused acceptance — 2026-10-10

Operator pulled `7eedf8c` and executed `python3 tools/checks/test-combined-jes-records.py`: **7 tests ran, OK**. Next `tools/run-native-regression 110 119 --show-output`: **PASS 10 / FAIL 0 / TOTAL 10**, all 110–119. Thus the newly introduced stricter combined-report logical-record checker has focused live TK5 acceptance. This does NOT certify physical JES DD identity or exact FB132 trailing padding. No runtime code changed in this validator phase. Next required gate is full `tools/run-native-regression` against the updated checker (target 120/0/120); only then accept the entire panel under the new validator.
