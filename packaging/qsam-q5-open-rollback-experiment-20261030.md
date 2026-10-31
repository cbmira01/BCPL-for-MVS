# Milestone QSAM — Q.5 failed-OPEN rollback experiment

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** **Q.5 — Hardening & release**  
**Design:** Owner authorized proceeding with the bounded failed-OPEN rollback experiment.  
**Status:** **Owner ACCEPTED the bounded failed-OPEN rollback experiment on 31 October 2026**, based on corrected compiler JOB 8144 and native Q5RBFIN JOB 8145 (all ten steps RC=0000, exact BCPL PASS, five zero finalizer counters). Prior JOBs 8142–8143 remain historical S0C1 failures. The additional final `P` is explained by the IFOX-proven test-only `QFPEX` → `Q5RPST` fall-through; earlier console harvester spacing failure remains recorded separately. See [formal owner acceptance](qsam-q5-failed-open-rollback-acceptance-20261031.md). March Q.5 remains IN PROGRESS.  
**Authority:** GitHub `main`, native MVS 3.8J and actual JES/IFOX/IEWL/GO for target behavior.

## Design and limits

This experiment deliberately **injects one stage-allocation refusal after an actual QSAM OPEN succeeds**; it does **not** claim that MVS GETMAIN returned a real failure. The tested production control-flow is the existing `QCSTFAIL` → `QCCLEAN` → `QSMCLS1` branch, with a **real QSAM CLOSE macro** for the partially opened `Q01` DCB. It does not inject a failure into MVS CLOSE, retry an uncertain CLOSE, change error precedence, or modify the accepted assembler source. On actual returned CLOSE failure, the accepted quarantine/no-blind-free policy remains in force and requires a separate experiment.

Source-controlled components:

- [`test-q5-open-rollback.bcpl`](../bootstrap-toolchain/extensions/bcplqsam/test-q5-open-rollback.bcpl): open `Q00` successfully; first `Q01` OPEN should return `QS_ERR_RESOURCE=-11` without a public handle; verify `Q00` still works; reopen `Q01` successfully; verify both handles and explicit CLOSEs; print one exact PASS record; normal FINISH RC=0. Assertions use `STOP(12)` so a failure is not mistaken for success.
- [`prepare-q5-open-rollback.py`](../bootstrap-toolchain/extensions/bcplqsam/prepare-q5-open-rollback.py): builds temporary `Q5RBOPEN` from the already source-controlled 16-DD `Q16FIN` JCL preparation machinery and a separately compiled real BCPL application. Requires exact current `bcplqsam.asm`; makes a **test-only ASMQ overlay** with one-shot `Q01` injection, the approved three-checkpoint `QFPROBE` logic relabeled `Q5R`, and no changes to other JCL beyond the temporary job/load identity. Preserves 16 independent temporary F1024 DDs, `REGION=256K`, BCEX/BCRG v1 and read-only production `BOOT_OBJ`.
- [`check-q5-open-rollback-evidence.py`](../bootstrap-toolchain/extensions/bcplqsam/check-q5-open-rollback-evidence.py): verifies a real JOB's ten IFOX/IEWL/GO steps, zero assembler flagged statements/severity, exact BCPL PASS, and one ordered E/L/X sequence inside that JOB's console START/END interval. No automated submission or retry.
- [`test_check_q5_open_rollback.py`](../bootstrap-toolchain/extensions/bcplqsam/test_check_q5_open_rollback.py): synthetic positive and negative evidence-checker tests. Their PASS is not MVS evidence.

## Expected native trace

The injected probe emits these **hexadecimal fullword** payloads:

| Checkpoint | Exact expected payload | Interpretation |
| --- | --- | --- |
| `Q5R:E` | `00000001:00000002:00000002:00000001` | Injection reason 1, Q00+Q01 live, two DCBs, one stage (Q00 only) |
| `Q5R:L` | `00000001:00000001:00000001:00000001:00000000` | One actual rollback CLOSE success; only Q00 DCB/stage remains, CLOSE status zero |
| `Q5R:X` | `00000000:00000000:00000000:00000000:00000000` | After BCPL explicitly closes both handles, normal FINISH finds zero outstanding resources |

`Q5R:L` uses the **actual `QSMCLS1` return status** to set its close-success counter. The `Q5R:X` record is emitted from the real optional-package finalizer path. Require **ASMWR, LKWR, ASMA, ASMN, ASMR, ASMQ, ASMG, LKED, WGO, GO all RC=0000**, no abend, zero IFOX severity/flagged statements, exact `BCPLQSAM Q5 OPEN ROLLBACK PASS`, and exactly one job-correlated sequence matching the table. GO RC=0000 alone does not prove rollback.

## Operator gates (no local source editing)

1. Fast-forward GitHub `main`; check Python syntax, `prepare-q5-open-rollback.py --check` and `python3 .../test_check_q5_open_rollback.py -v`. The `--check` path uses a **synthetic** BCPL assembler sample and does not contact MVS. Halt on any nonzero return.
2. **Separate MVS compiler JES authorization:** compile exactly `test-q5-open-rollback.bcpl` using the resident demoted Cambridge compiler via `tools/bootstrap/compile-mvs` with `--job-name Q5RBCOMP --output workarea/bcplqsam-q5/rollback-generated.asm`. Save full compiler JOB, CODE extraction and RC. This is a *real MVS compiler job*, not an offline conversion.
3. **JCL preparation only:** run `python3 bootstrap-toolchain/extensions/bcplqsam/prepare-q5-open-rollback.py --prepare`. It requires that compiled file in the ignored Q.5 workarea, authenticates the job card via the local manifest, produces `workarea/bcplqsam-q5/q5rbopen.jcl` once, and prints card count/SHA-256. It never submits JES or installs a PDS. It refuses to overwrite an existing JCL file.
4. **Separate `Q5RBOPEN` JES authorization:** submit the prepared deck **once** through `tools/mvs/submit-jcl`, with a persistent one-attempt marker recorded before the socket-reader call. On uncertain result, inspect JES; do **not** retry blindly.
5. Capture `job-summary --max-rc 0`, `dump-report-for-job`, and one console log with a complete `JOB N Q5RBOPEN` start/end interval. Then run `check-q5-open-rollback-evidence.py --job N --summary ... --report ... --console ...` and preserve full evidence regardless of result.

The operator shell command policy forbids fail-fast options in pasted WSL blocks; use conditional return-code gates and leave the interactive shell usable on failures. Do not remove earlier attempt markers or replace historical Q.1/Q.4 evidence. The runbook does not authorize either native JES job or permanent object installation merely because its test-only code is committed.

## Acceptance and follow-on decisions

A target-native PASS establishes **safe ordinary rollback after a simulated stage allocation refusal**, one actual successful CLOSE on the rollback path, retention of an independent Q00 handle, successful slot reuse on fresh Q01 OPEN, and full tracked-resource cleanup. It does **not** establish a real GETMAIN allocation denial from BCPLQSAM, returned MVS CLOSE failure, uncertain ownership quarantine, unrecovered MVS abend recovery, or promotion to `EXT_OBJ`. The source's provisional primary-OPEN-error precedence if cleanup CLOSE also fails remains a separate owner decision.

Q.5 remains **IN PROGRESS** until the remaining exceptional scenarios, packaging decision, clean-from-Git verification, native focused/full regression and owner acceptance.

## Native compiler and failed execution, 30 October 2026

The owner explicitly authorized one MVS Cambridge compilation, **Q5RBCOMP JOB 8141**. ICINT19 COMP and IEBGENER SVCODE each returned RC=0000; the Cambridge compiler recorded **EXECUTION CYCLES=904650, CODE=0**. It emitted 308 source lines in `workarea/bcplqsam-q5/rollback-generated.asm`, SHA-256 `7a36834df35a191f07b4d8113b6d493cec014840f8571ab3c9ebd314534eb721`. No second compiler execution is presently needed.

The separately authorized one-shot **Q5RBOPEN JOB 8142** used 4,123 cards, deck SHA-256 `0c32e034328fdbb18ce4ff677dad5029e8de7ed67258c87a86320296f0764716`. The owner reported:

- ASMWR, LKWR, ASMA, ASMN, ASMR, ASMQ, ASMG, LKED and WGO **RC=0000**; zero assembler statements flagged and severity zero.
- **GO ABEND S0C1 U0000** (JOB RESULT FAILURE). PSW at entry to abend `078D0000 00000004`, ILC=2, INTC=0001. It indicates an operation exception with the instruction address in low memory; **the precise faulty return path is not yet identified**.
- The JOB 8142 console showed **`Q5R:E:00000001:00000002:00000002:00000001`** and **`Q5R:L:00000001:00000001:00000001:00000001:00000000`**. This is bounded evidence of two opened DCBs followed by a successful real rollback CLOSE, with Q00 accounting intact.
- The required **`Q5R:X`** was absent, as was the BCPL application PASS record. **GO did not complete**. Therefore neither BCPL control-flow recovery, Q01 reopen, normal FINISH nor final cleanup is accepted.
- The IFOX listing located `QCCLEAN` at offset `000540`, `Q5RBDONE` `00058A`, `QCROLLRT` `0005B2`, `QCRET` `0007A2`, and `QFPROBE` `000F48` in their assembler control sections. These are **section-relative** offsets, not a proven faulting instruction location. An S0C1 due to low-memory transfer is consistent with a bad branch/return but does not distinguish test instrumentation, runtime behavior or BCPL-generated code.
- The owner retained the original deck and one-attempt marker under `workarea/bcplqsam-q5/q5rbopen-attempt/`. **Do not overwrite or resubmit that deck**.

The operator-provided summary, report excerpt, program symbol excerpts and console records are the basis of these claims. The complete JES dump is not tracked in GitHub.

## Scoped six-marker return-path refinement — Q5RBTRC

The owner directed a **diagnostic refinement**, without authorizing any new JES execution. [`prepare-q5-rollback-trace.py`](../bootstrap-toolchain/extensions/bcplqsam/prepare-q5-rollback-trace.py) derives a **new** source-selected `Q5RBTRC` deck from the same verified JOB 8141 compiled BCPL output and exact current `bcplqsam.asm`. It reuses the original one-shot injected stage refusal and real rollback CLOSE. Its new labels and WTO data are confined to the temporary ASMQ overlay; `BCPLQSAM` production source and accepted `BOOT_OBJ` remain untouched.

Three **register-preserving QFPROBE** calls identify the path *after* the successful `Q5R:L` snapshot:

| Marker | Injection location | Meaning if observed |
| --- | --- | --- |
| `Q5R:P:POST-CLEAN` | `Q5RBDONE`, after `Q5R:L` | Diagnostic probe returned; reached post-cleanup branch |
| `Q5R:R:ROLL-RETURN` | `QCROLLRT`, before restored primary error | Reached reserved-slot rollback return path |
| `Q5R:T:CORE-EPILOGUE` | `QCRET`, before restoring `QSMCORE` register/save-area state | Reached core epilogue; **not proof of successful transfer back to BCPL** |

On complete success, expected ordered phases are **`E L P R T X`**, followed by native GO RC=0000 and one exact `BCPLQSAM Q5 OPEN ROLLBACK PASS` application record. The two initial counters and final counters remain as above. On any abend, [`check-q5-rollback-trace.py`](../bootstrap-toolchain/extensions/bcplqsam/check-q5-rollback-trace.py) reports the last observed checkpoint but must return nonzero, preserving failure evidence. Pure offline negative tests are in [`test_check_q5_rollback_trace.py`](../bootstrap-toolchain/extensions/bcplqsam/test_check_q5_rollback_trace.py).

The new deck's preparation mode is **offline only** and produces `workarea/bcplqsam-q5/q5rbtrc.jcl` once, without modifying `q5rbopen.jcl`, its attempt marker, or any installed dataset. The generator validates source-controlled compilation provenance and the exact SHA-256 of JOB 8141's 308-line recovered assembler. New **Q5RBTRC JES submission requires separate explicit authorization** and a distinct one-attempt marker. Q.5 rollback remains open until MVS target evidence demonstrates successful end-to-end recovery; adding markers is not acceptance.

## JOB 8143 trace outcome and corrected BCPL termination

The owner explicitly authorized one native **Q5RBTRC JOB 8143**, using the 4,151-card preserved deck SHA-256 `ce6036d2ed04cbfec83ef01ba18a1e0e37755b92a002d1b180876818d8b54623` and the original JOB 8141 compiled BCPL. Actual MVS reported:

- ASMWR, LKWR, ASMA, ASMN, ASMR, ASMQ, ASMG, LKED, WGO: **RC=0000**; zero assembler flagged statements and zero highest severity.
- GO: **ABEND S0C1 U0000**, PSW `078D0000 00000004`, ILC=2, INTC=0001; no application PASS or finalizer `Q5R:X`. **NOT ACCEPTED.**
- JOB-correlated WTO markers in order: `Q5R:E` (expected counters), `Q5R:L` (expected successful rollback-CLOSE counters), `Q5R:P:POST-CLEAN`, `Q5R:R:ROLL-RETURN`, `Q5R:T:CORE-EPILOGUE`. This places the observed failure **after reaching the core epilogue marker**, but does not prove successful return to the BCPL caller.
- S0C1 repeated the JOB 8142 low-memory PSW. In the reported JOB 8143 dump, R14=`000A5C5A`, which points into the BCPL application PASS literal in the displayed memory map. The register snapshot cannot alone identify the instruction that spoiled control flow.

Source review revealed the pre-correction [`test-q5-open-rollback.bcpl`](../bootstrap-toolchain/extensions/bcplqsam/test-q5-open-rollback.bcpl) ended `WRITES(...); NEWLINE(); $)1` with **no `FINISH`**, whereas the independently tested Q.1 normal-completion programs explicitly invoked `FINISH`. This is a **plausible root-cause hypothesis, not yet native confirmation**. At owner direction, commit `d0529e16887645ce99d4711a05d33f702633e30f` inserted one `FINISH` statement after `NEWLINE()` without changing the assertion `STOP(12)` branches. A later offline source guard requires that ending and retains failing assertions.

The original JOB 8141 compiler output, JOB 8142 `Q5RBOPEN` deck, JOB 8143 `Q5RBTRC` deck and both one-shot attempt directories are **historical failed/diagnostic evidence**. Do **not** delete, edit, overwrite, or resubmit them.

**Next gates (not yet authorized):** compile the **corrected** BCPL source into a **new filename**, with a new compiler JOB identity (proposed `Q5RFCOMP`); generate a **new** test-only IFOX/IEWL/GO deck and JOB identity (proposed `Q5RBFIN`), reusing the six-marker trace and one-shot stage-refusal logic without reusing the previous assembly image; verify the resulting source/output hashes and native GO/FINISH evidence. Both native jobs require distinct explicit owner authorizations. No production `bcplqsam.asm`, installed object or MVS dataset was changed by the correction.

## Corrected compilation JOB 8144 and independent Q5RBFIN preparation

The owner separately authorized **Q5RFCOMP JOB 8144**, compiling the corrected test-only source at Git revision `73a077cbcd829f52f8657bc4a5c2d8c708ba6de0`. The resident demoted Cambridge compiler reported COMP/ICINT19 RC=0000, SVCODE/IEBGENER RC=0000, JOB RESULT SUCCESS, execution **CODE=0** after **909851** cycles. The recovered **311-line** native System/370 assembler was saved as `workarea/bcplqsam-q5/rollback-finish-generated.asm`, SHA-256 **`f68e03ea2cdc8bc9a25a8f4df49c8c8cc1fd4b54056eed1a858be952b207d4ed`**.

With the owner's subsequent authorization to implement preparation tooling, [`prepare-q5-rollback-finish.py`](../bootstrap-toolchain/extensions/bcplqsam/prepare-q5-rollback-finish.py) now produces the uniquely named **`Q5RBFIN`** deck at `workarea/bcplqsam-q5/q5rbfin.jcl` using the preserved source-controlled Q16FIN lifecycle campaign, the same six-marker ASMQ diagnostic overlay used by Q5RBTRC, and **only** the verified JOB 8144 assembler. It never reads the obsolete `rollback-generated.asm` as its compiler input or overwrites `q5rbopen.jcl` / `q5rbtrc.jcl`. It requires the matching preserved JOB 8144 compiler attempt metadata (source revision, source SHA, job number, zero step RCs and nonempty assembler with exact SHA/line count).

`--check` generates a synthetic JCL deck, validates E/L/P/R/T/X trace markers and rejects three damaged identity variants, without calling MVS. [`test_prepare_q5_rollback_finish.py`](../bootstrap-toolchain/extensions/bcplqsam/test_prepare_q5_rollback_finish.py) adds isolated negative checks against missing `FINISH`, wrong compiler JOB, stale source digest, corrupted generated assembly, missing output and nonzero compile-step RC. `--prepare` writes `q5rbfin.jcl` **once**, exclusively, after provenance/JCL verification; it does not submit JES, install PDS members or alter the production BCPLQSAM object.

**Gate result:** Owner's WSL checks passed (Python syntax, synthetic deck, seven provenance tests); offline preparation created the 4,154-card `q5rbfin.jcl`. The owner separately approved **one** Q5RBFIN JES submission, yielding JOB 8145. JOBs 8141–8144 and their evidence remain preserved. No further native execution or installed dataset modification has been authorized. The initial missing-`FINISH` diagnosis is supported by JOB 8145's successful corrected native return; it does not retroactively change JOBs 8142–8143.

## Corrected native Q5RBFIN JOB 8145 and test-probe fall-through

The operator used the owner-approved one-shot `Q5RBFIN` deck (4,154 cards; SHA-256
`e315f22394c9a0fa7118abfaf330c73869936406cebe2e1f8ae4acc7306e4b70`).
The original full JOB 8145 evidence is preserved under
`workarea/bcplqsam-q5/q5rbfin-attempt/` and in MVS printer output and Hercules
logs; GitHub tracks the checker and the acceptance interpretation, **not a
substitute synthetic JES run**.

- `ASMWR`, `LKWR`, `ASMA`, `ASMN`, `ASMR`, `ASMQ`, `ASMG`, `LKED`,
  `WGO`, and `GO`: all **RC=0000**. JES reported **JOB RESULT: SUCCESS**,
  **HIGHEST RC: 0000**; IFOX **zero statements flagged** and
  **highest severity zero**.
- The actual native `GO` report contains **exactly one**
  `BCPLQSAM Q5 OPEN ROLLBACK PASS` output record. The BCPL test's
  failing `STOP(12)` assertions were not taken.
- The independent console `mvs-state/log/3033.log` and MVS
  `mvs-state/log/hardcopy.log` show the same seven WTO observations,
  all between JOB 8145 `$HASP373` and `$HASP395`:
  `E L P R T X P`. `E` and `L` carry the agreed rollback counters;
  `X` records **five zero fullword counters** at finalizer exit.
- The seventh, extra `P` is **not** evidence of an additional QSAM
  OPEN/rollback: the actual JOB 8145 IFOX ASMQ listing shows
  `QFPEX` emitting `Q5R:X` via **`0010CA 0A23` / `SVC 35`**,
  immediately followed at **`0010CC`** by `Q5RPST LA 1,Q5RPL`
  and its own WTO call. The test-only probe overlay placed
  `Q5RPST` directly after `QFPEX` without a branch to `QFPDONE`.
  This fall-through executes the `P` message a second time **after**
  finalization; the production `bcplqsam.asm` is unchanged.
- The initial collection script's `console.rc=1` is independently
  explained: it searched for literal `Q5RBFIN STARTED` and
  `Q5RBFIN ENDED`, but actual JES writes **two spaces** between
  the jobname and STARTED/ENDED. The old script skipped its inline
  acceptance checker; its `evidence.rc=1` is a **collection/checker
  failure**, not an MVS GO RC. Both original logs contain complete
  JOB 8145 boundaries. Neither retained result has been rewritten.

The dedicated, read-only
[`check-q5-rollback-finish.py`](../bootstrap-toolchain/extensions/bcplqsam/check-q5-rollback-finish.py)
checks JOB **8145** only. It pins the unique submitted JCL and native
compiler output digests and the one-shot attempt metadata, all ten
JES RC=0000 steps and zero IFOX severity, exactly one BCPL PASS,
both original console and hardcopy complete job intervals with identical
`E L P R T X P` payloads, **and** the actual IFOX SVC-35/next-instruction
adjacency proving why the otherwise unexpected seventh marker is safe.
Seventeen synthetic positive and negative cases are in
[`test_check_q5_rollback_finish.py`](../bootstrap-toolchain/extensions/bcplqsam/test_check_q5_rollback_finish.py).
It cannot execute MVS, rewrite evidence or authorize a new job. The
original strict
[`check-q5-rollback-trace.py`](../bootstrap-toolchain/extensions/bcplqsam/check-q5-rollback-trace.py)
remains unchanged for historical JOB 8143 interpretation.

**Owner gate:** The owner accepted the bounded failed-OPEN rollback result on 31 October 2026. The offline checker and local workarea provenance status must be recorded independently from this acceptance; no fabricated offline test execution or rewrite of native evidence is implied. Returned-CLOSE quarantine, geometry/resource, packaging, clean-from-Git and full native regression remain separate Q.5 obligations. **Q.5 is not closed.**

