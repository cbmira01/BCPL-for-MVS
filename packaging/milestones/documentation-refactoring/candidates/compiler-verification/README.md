# DR.5 — Focused compiler input and option verification

Baseline `0de748ebef72965497dd1ac40330a99a33f56cae`. Three independent hypotheses, no changes to resident members, regular test numbering or suite oracles. Serial execution on the established corrected development installation.

| Probe | Input and prediction |
| --- | --- |
| MR10 nested GET | SYSIN GET DR5INC; outer header declares A, opens DR5NEST, then declares B and ends with period. Inner header declares C and ends at EOF. Require exact 17 5 20 42 output after both returns. |
| MR10 OPTIONS | L6000N should reprocess N after the decimal workspace argument, suppressing GET DR5MISS (no such DD allocated). Require option echo and exact 42 output. Does not measure actual workspace extent. |
| Cambridge CAMBPARM | J12Q/N/ slash-filled through column 80. Unknown first-phase J should warn and skip numeric suffix; Q should suppress ordinary phase diagnostics; second-phase N suppresses binary deck. GET LIBHDR supplies START/WRITEF and the three manifest values. Require warning, quiet diagnostics, zero ICINT CODE, IFOX/IEWL/native GO and exact 4 32 -1 output. No direct object-deck or native-running compiler claim. |

The separate [driver](../../../../../tools/checks/run-dr5-compiler-verification.py) uses existing MR10 and Cambridge host drivers, JES receipt checks and native object linkage. 904 is a private helper naming argument, not a new suite case. All three probes are expected to succeed; stop on first failure and retain private receipts. No automated retries, installations or full regression replay.

Offline Python compilation and fixture/oracle and option-record checks passed using a mocked shared helper. Actual MVS compilation, execution and diagnostic checks remain pending. Missing-input and nesting-overflow diagnostic paths are source-observed only; the MR10 suppressed-GET test deliberately avoids executing the unsafe unsuppressed missing-input path. No arbitrary nesting, all-option coverage, or malformed-input recovery certification.

## Host preflight correction

Owner reported the initial driver at `1b9835ef2543a1ebbe14d1eae5578e74131b6c08` aborted before submission: reversing a one-record oracle produced the unchanged valid sequence, which the shared helper incorrectly treated as a negative test. Previous mocked checks missed that integration defect. Reproduced the traceback offline with a byte-identical copy of the actual shared helper, corrected its negative-test construction, and ran the unmodified compiler driver `--check` with all ten exact tracked fixture inputs and the real corrected helper. PASS. Additional single-record, distinct multi-record, repeated-record, empty-oracle and malformed-record checks passed. No target jobs ran; all BCPL fixtures, option records, expected outputs and actual exact comparison gates remain unchanged. MVS verification is still pending.

## First target observations — qualified partial result

Owner-reported run `workarea/dr5-compiler-verification/run-r_bjwj8s` at `e743ee65e4fbfc41e086aa512c706bafa4138422`: MR10 nested GET JOB 9920 PASS, exact RP: DR5 GET 17 5 20 42; MR10 L6000N JOB 9921 PASS, exact RP: DR5 N 42, option echo gate satisfied. The installed compiler pipeline passed the driver's JES and three zero ICINT completion-code gates in each case. Both are accepted observations within fixture scope. Cambridge compile driver returned host RC=2 (cambridge-compile.log); underlying JES identity, completion code and diagnostics have not yet been supplied. Overall candidate run FAIL; no Cambridge native execution or option behavior is established. Preserve all fixtures, oracles and receipts. Inspect the existing compile log and corresponding MVS report before any follow-up; do not repeat the two successful MR10 probes.

## Cambridge JOB 9922 — missing bootstrap service

Owner-supplied full MVS report for the failing DR5CGET run at e743ee65e4fbfc41e086aa512c706bafa4138422. COMP ICINT19 and SVCODE IEBGENER both RC=0000, but ICINT CODE=-1 after 1346 cycles. The warning "Unknown compilation option J ignored" precedes the failure. READN (G!70=201877) returns 12, with G!71 TERMINATOR=81 (ASCII Q). Trace #61 (C=175433, W=5135 = X'140F', D=0) loads indirect G!15; #62 (W=49165 = X'C00D', D=13) performs OP6 call using A=0; #63 fetches address zero. MAPSTORE confirms G!15=0. Historical LIBHDR defines UNRDCH:15; the current tracked MR10 ICLIB provides G!13 RDCH but no G!15, and bootstrap-host.bcpl exports only DATE, WRAPOUTPUT and FINDPARM. The historical master has five UNRDCH sites: unknown first-phase option, P, R, second-phase H, and post-FORMTREE lookahead. The historical MR10 scanner instead explicitly reprocesses TERMINATOR. This identifies the absent host service on the option path, not a GET or native BCPLIO defect. The marked CODE output contains OCODE-like records, not acceptable native assembler; its provenance is not established and it must not be used. No application assembly/link/GO occurred. Preserve the original FAIL and both MR10 passes; do not rerun unchanged.

Proposed design for owner discussion: add a bootstrap-scoped character replay service in BOOTHOST, with initialization and exact selected-stream/last-character semantics, preserving the MR10 interpreter and published images. Alternatively implement native-style per-stream pushback in ICINT19 and bind G!15 through an appropriate compiler-host ICLIB; this has wider impact. A parser-only change using TERMINATOR does not cover the independent source lookahead site. Confirm design and verify all reached sites before modifying the compiler host. No implementation or installation authorized by this evidence record.

## Owner-approved compatibility repair and permanent regressions

Owner approved the bootstrap-host compatibility design and permanent Bootstrap coverage. BOOTHOST now installs scoped RDCH/SELECTINPUT/ENDREAD wrappers once at FINDPARM, capturing the loaded ICLIB functions; G!15 replays exactly one previously read character on the same selected stream. Duplicate unread, unread without a selected-stream read, and switching streams with pending replay fail closed. ENDREAD discards replay state; this is not a general cross-stream pushback API. The fifth historical call site requires a top-level period; historical SYN calls unbound G!26 SKIPREC first. Add the small host-only SKIPREC service that drains through the next synthetic newline or EOF, so source lookahead is directly testable. No changes to MR10 ICLIB, ICINT19, historical compiler source, native BCPLIO, native BLIB or published RC4. Rebuild CAMBCOMP using BOOTHOST and existing CAMBBLD; no need to rebuild BLIB for this host-only change. Permanent Bootstrap cases 190–192 appended after existing IDs: exact native newline/FB132, compiler option replay (unknown, P/R, H compile-only), and two-source-unit lookahead. Existing 00–189 fixtures unchanged. Initial target acceptance pending. The earlier MR10 PASS and Cambridge FAIL remain recorded.

Host checks before committing: copied the actual permanent Python runner and all ten source/oracle/option/input files into an isolated workspace, verified their Git blob identities, ran the three --check modes and tested malformed/extra/incomplete assembler-unit rejection. Copied the actual suite runner by matching blob SHA and exercised all 193 IDs, selection, three-case dispatch with a stub native runner, and rejection of missing marker files on a synthetic fixture tree. Reviewed tracked manifest/physical ownership and unchanged historical fixture identities. Local Git clone remains unavailable due to DNS; no actual BCPL compilation or MVS execution performed by the assistant. New regular campaign expectation after target acceptance: Bootstrap 148 PASS/1 expected SKIP, project total 211 PASS/1 expected SKIP, zero FAIL/BLOCKED. Existing 208 PASS result remains the pre-change historical campaign. The dedicated rebuild driver performs preflight and one approved in-place BOOTHOST stage and CAMBBLD; stops before the next case on failure. No automatic retry or rollback.

## Target verification — PASS (26 November 2026 UTC / 25 November EST)

Owner-reported run at `3f6a417504ab721c080d5af1ffaf54b580ea346b`, private evidence `workarea/dr5-bootstrap-host-fix/run-42l_ygz7`, BOOTHOST SHA-256 `6836f384a209e2ec4874a3e8ac1cea608f299abbbba1197f5af16d2f855f2837`. CAMBBLD JOB 9925 passed the driver's 23 ordered JES step/RC gates and 22 zero ICINT completion codes. The driver returned status PASS, stage complete, and all three permanent Bootstrap cases PASS:

| Case | Verified scope | Private suite evidence under workarea/test-suites/ |
| --- | --- | --- |
| 190 | Both logical newline representations, ordinary EBCDIC A, input delimiters/EOF, native output, six exact blank-padded FB132 records and EOF via independent QSAM verifier | 20261126T041242Z-73356-bootstrap-production-c16ecqfb |
| 191 | J12Q/N/ and J12P3000R30Q/N/ warning, quiet diagnostics, GET LIBHDR, zero ICINT CODE, single assembler unit and exact native output; Q/H600N/ compile only | 20261126T041254Z-73458-bootstrap-production-2pikheci |
| 192 | Top-level period record skip and post-FORMTREE character replay; exactly two complete assembler units with independently verified native executions | 20261126T041327Z-73673-bootstrap-production-xv1ct75_ |

This resolves the missing bootstrap G!15 and G!26 services at the tested scope. Earlier JOB 9922 remains FAIL, and MR10 JOBS 9920/9921 remain PASS. No general cross-stream replay, misuse-path runtime testing, arbitrary GET nesting, actual workspace/name-table extent measurement, H-enabled native execution, or general historical option certification is established. No MR10 ICLIB, ICINT19, native Core Runtime, historical compiler source, BLIB or RC4 changes were required for the host correction.

## Full supported post-correction regression — PASS

Owner-reported production-profile eight-suite campaign, following the above rebuild at the same checkout; no intervening Git update reported. Private summary: `workarea/project-regressions/20261126T041512Z-73815-04_87uje/summary.json`. Elapsed 11m 31s. PROJECT REGRESSION RESULT: PASS.

| Suite | PASS | FAIL | SKIP | BLOCKED |
| --- | ---: | ---: | ---: | ---: |
| mr10 | 12 | 0 | not reported | not reported |
| mr10-coroutines-supported | 5 | 0 | 0 | 0 |
| bootstrap | 148 | 0 | 1 (083) | 0 |
| runtime-extensions | 13 | 0 | 0 | 0 |
| bcpltime | 4 | 0 | 0 | 0 |
| bcplqsam | 14 | 0 | 0 | 0 |
| coroutines | 13 | 0 | 0 | 0 |
| coroutine-contract | 2 | 0 | 0 | 0 |
| **Supported total** | **211** | **0** | **1** | **0** |

All 212 selected cases accounted for; authorized device cases 175/176 passed. Bootstrap cases 190–192 passed a second time in this campaign. Preserve the pre-change 208 PASS campaign, original failed observations and all existing test identities/oracles. The separate historical MR10 diagnostic failure remains FAIL.

Evidence is the owner's supplied console transcript and focused driver result, interpreted against the tracked gates. Private JSON, per-case receipts and installed binary identities were not independently inspected. No clean-room rebuild, release installation, release promotion, normative authority transfer or march closure is claimed. No repeat rebuild or regression is required for these resolved defects without new evidence.
