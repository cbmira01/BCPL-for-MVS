# Milestone QSAM — Q.5 returned-CLOSE quarantine experiment

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** **Q.5 — Hardening & release** (IN PROGRESS)  
**Decision:** Owner approved the bounded returned-CLOSE quarantine design and preparation on 31 October 2026. No native MVS compilation or JES execution is authorized by this approval.  
**Production baseline:** source-controlled `bootstrap-toolchain/extensions/bcplqsam/bcplqsam.asm` remains unchanged. No accepted MVS object or permanent dataset is modified.

## Purpose and limits

This experiment validates the **BCPLQSAM response to a returned nonzero CLOSE status**, rather than claiming MVS genuinely returned a CLOSE error. In particular:

1. Native `Q00` QSAM OPEN succeeds and owns a private 1,024-byte stage; native `Q01` OPEN succeeds independently.
2. `QSMCLS1` issues a **real MVS `CLOSE ((2))` for Q00**. Only if MVS has returned zero, the disposable **ASMQ-only overlay** sets R15 to 4 **once**, gated by published handle ID 1 (`Q00`) and test-only `Q5CONCE=0`. If MVS returns nonzero, its status is not overwritten. A failure or abend in the real CLOSE is neither manufactured away nor classified as a successful injection.
3. The unmodified production `LTR 15,15` / `BNZ QSCQUAR` handling then retires the public handle and returns `QS_ERR_CLOSE=-14`. It preserves the quarantined slot, DCB and private stage without a second CLOSE or unsafe FREEMAIN. A synthetic error **after actual successful CLOSE** deliberately creates retained diagnostic storage until MVS task termination. This is not proof that a real failed CLOSE leaves the same OS-owned state.
4. The real BCPL fixture calls repeated `CLOSE` and `INFO` on the invalidated Q00 handle, expecting `QS_ERR_HANDLE=-7`; it then performs real `INFO`, `READ` of one F1024 logical record, and successful `CLOSE` of surviving Q01.
5. The BCPL application prints `BCPLQSAM Q5 CLOSE QUARANTINE PASS` once and calls explicit `FINISH`. `QSMFIN` encounters quarantined state 4, does **not** retry its CLOSE or release its uncertain ownership, and returns 8. The generic BCEX/BCRG v1 registrar emits `BCPLREG 2001 FINALIZER RETURNED NONZERO`; native GO returns **RC=0008** despite a successful BCPL application marker.

Failures of BCPL assertions call `STOP(12)`. The checker must **not** accept RC=0012 merely because an application marker or some WTOs exist.

## Test-only implementation

- [`test-q5-returned-close.bcpl`](../bootstrap-toolchain/extensions/bcplqsam/test-q5-returned-close.bcpl): real BCPL assertions and normal `FINISH`.
- [`prepare-q5-returned-close.py`](../bootstrap-toolchain/extensions/bcplqsam/prepare-q5-returned-close.py): fail-closed source and in-stream ASMQ instrumentation, synthetic JCL check, and **one-shot** preparation of `workarea/bcplqsam-q5/q5rcclos.jcl` from independently native-compiled assembler. Uses the established Q16FIN 16 temporary F1024 DD campaign, source-selected BCX/BCRG version-1 registration, read-only `BOOT_OBJ`, and no permanent PDS writes.
- [`test_prepare_q5_returned_close.py`](../bootstrap-toolchain/extensions/bcplqsam/test_prepare_q5_returned_close.py): offline positive and tampering tests, including one-shot injection and keeping the real CLOSE before the synthetic status override.
- Existing Q.1 proven `QFPROBE` WTO list/execute code is used **only in the temporary ASMQ**. Its first count reads `QSQUAR` instead of `QFCOUNT` and the messages are relabeled `Q5C:E/L/X`; the separate production finalizer and diagnostics are not edited.

### Expected native trace (subject to MVS verification)

| Phase | Exact payload | Meaning |
| --- | --- | --- |
| `Q5C:E` | `00000001:00000002:00000002:00000002` | One-shot injected flag 1; two tracked live DCBs/stages after quarantining Q00 |
| `Q5C:L` | `00000001:00000001:00000001:00000001:00000000` | One quarantined slot; surviving Q01 successfully CLOSEd; only retained Q00 ownership remains |
| `Q5C:X` | `00000001:00000001:00000001:00000001:00000008` | Finalizer observed quarantine, returned status 8; did not retry or release uncertain DCB/stage |

Require exactly `E L X` with complete same-JOB `$HASP373` / `$HASP395` boundaries, zero IFOX severity, every IFOX/IEWL/WGO step RC=0000, **GO RC=0008**, the single BCPL PASS record, and the single registrar returned-finalizer diagnostic. The live `Q5C` markers are not a general public API guarantee.

## Gates and evidence

**Implementation/offline gate:** The assistant owns Python syntax checks, unit tests, patch/identity checks and source-controlled JCL preparation. Offline PASS is not proof that IFOX will assemble new macros or that the native MVS path works.

**Separate MVS compiler gate:** Compile this exact BCPL source using the **resident demoted Cambridge compiler** via the established `tools/bootstrap/compile-mvs` workflow with new job name `Q5RCCOMP` and output `workarea/bcplqsam-q5/returned-close-generated.asm`. Preserve full JOB/ICINT19/CODE recovery evidence and matching source/output SHA-256 in the distinct `q5rccomp-attempt` directory. Do not reuse JOB 8144's unrelated assembler.

**Separate native GO gate:** After compiler acceptance and hash/provenance checks, produce `Q5RCCLOS` temporary JCL, verify it never changes production `bcplqsam.asm` or permanent MVS datasets, and obtain **separate explicit JES authorization** for a single submitted attempt. Preserve console, hardcopy, MVS print, IFOX, IEWL, step RC and application evidence, including abnormal outcomes. No automatic retry.

**Scope exclusion:** Actual MVS returned-CLOSE exception behavior, DCB validity after an uncertain CLOSE, resource leaks following a genuine unrecovered abend, and a universal recovery promise remain unverified. Accepted JOB 8145 failed-OPEN rollback evidence is a distinct earlier Q.5 result. Completion of this experiment alone does **not** close March Q.5.

## Independent offline verification — 31 October 2026

The assistant ran Python 3.13 `py_compile` on the local, byte-identical test-only generator/test sources and executed **19/19 unit tests: PASS**. The post-CLOSE and finalizer WTO calls now load a relocatable literal `=A(Q5CONCE)` into R1 so the diagnostic address remains valid across CSECTs, rather than depending on a freed stage pointer or assuming a QSMCLS1 base in QSMFIN. The BCPL source is 46 ASCII lines (maximum length 72, no oversize 80-character records). Independently fetched GitHub production `bcplqsam.asm` contains **exactly one** of each five required source anchors plus its `QSMCTRL` insertion anchor; the diagnostic `PROBE` has exactly the expected three marker strings and one `QFCOUNT` load replaced with `QSQUAR`, with no added card over 71 columns. Git blob SHA-1 of each locally tested file matches its GitHub `main` content blob. Tests cover pristine source transformation, real CLOSE before one-shot override, injected status and quarantine paths, three retagged JCL identity fields, missing/duplicate anchors, invalid cards, and required BCPL assertions.

**Remaining offline limitation:** The full `--check` run against all source-controlled Q16FIN helper modules and the authenticated local manifest has **not** been executed inside this environment. These offline checks do not establish IFOX acceptance, actual MVS returned CLOSE semantics or native GO outcome. **Do not ask the operator to run Python/unit verification**; reserve operator steps for approved MVS-facing compiler and JES tasks.

## Resident Cambridge compiler gate — JOB 8146

The owner authorized one `Q5RCCOMP` compilation on 31 October 2026 and returned the native JES evidence. **JOB 8146 / Q5RCCOMP PASSED:** `COMP` ICINT19 RC=0000, `SVCODE` IEBGENER RC=0000, `JOB RESULT: SUCCESS`, `HIGHEST RC: 0000`, `EXECUTION CYCLES = 918876, CODE = 0`, with marked recovered CODE stream. Native output has **309 lines** and SHA-256 `37607f62e4acc6d0ec2a4cf3ca8908e2516695d4622b73e4e5991d5c2755c1ac`; `workarea/bcplqsam-q5/q5rccomp-attempt/` retains the source/assembler hashes, summary and printer report. Compilation does **not** test native OPEN/CLOSE behavior.

The owner has separately approved **one** `Q5RCCLOS` JES submission to test the temporary source-selected quarantine overlay. This approval does not authorize automatic retries, permanent dataset modification, or object promotion.

## First Q5RCCLOS preparation attempt — pre-JES failure

After the owner approved one Q5RCCLOS submission, the operator
fast-forwarded to GitHub `5330c5325ff99548d41f4a1ce9fe3347706922ce`
and ran the guarded one-shot shell. `prepare-q5-returned-close.py
--prepare` rejected the 309-line recovered JOB 8146 compiler output:

```
Q5RCCLOS preparation FAILED: unexpected generated CG370 assembler format
Preparation RC=1
No JES submission. Preserve preparation evidence.
Overall RC=1
```

**This is a pre-JES tooling failure, not a native QSAM failure.**
No `q5rcclos.jcl`, `q5rcclos-attempt/`, or submitted Q5RCCLOS
job was reported. The successful compiler JOB 8146 and its recovered
assembler remain unmodified. The original local
`workarea/bcplqsam-q5/q5rcclos-preparation.log` must not be
overwritten by a retry.

**Confirmed cause:** the preparation validator incorrectly required
the text `ENTRY R0APP` in *raw* demoted Cambridge CG370 output.
The established `application_source()` adapter in
`bootstrap-toolchain/probes/r0-export-trailer-probe/make-job.py`
correctly expects exactly one **unnamed CSECT** and adds
`R0APP CSECT` plus `ENTRY R0APP` only when preparing IFOX cards.
The recovered assembler's 309-line count is within the existing
100–500-line limit. That incorrect pre-adapter check was removed.

**Correction:** the source-controlled preparation now validates the
raw compiler code by invoking that accepted adapter, still requires
the adapted `ENTRY R0APP` exactly once, and retains the compiler
summary/input SHA/output SHA, record-count, IFOX/JCL structural
validation, and non-overwrite safeguards. Six unit cases were added
for valid unnamed CG370 and malformed variants. The assistant ran
**9 isolated local tests of the corrected guard/adapter contract:
PASS**. The complete source-dependent integration test and true
IFOX/IEWL/GO behavior remain distinct future evidence; do not claim
them as passing on the strength of isolated tests.

The existing **one** owner authorization for Q5RCCLOS submission
was unused. A corrected recovery procedure may exercise it once
after verifying its exact source revision and preserving the
earlier preparation-failure log; no new compiler submission or
permanent MVS dataset modification is necessary.
