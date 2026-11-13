# CO.1 — CK-D: shared checked-entry service and call-counting research

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture
**Recorded:** 12 November 2026 (Louisville)
**Source HEAD:** `0f535b1e14f89a79d436b5d83bf26f2c4e2c3438`
**Evidence classification:** SOURCE-OBSERVED, HOST-ONLY TESTED, and a PROPOSED design seam; no new native JOB reported
**Status:** CK-D DESIGN REVIEW OPEN; CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED

## Authority and scope

This investigates the next gate in the [checked-entry option matrix](co1-cg370-checked-entry-option-matrix-20261112.md) after [CK-B 49–52 production PASS](co1-ck-b-native-checked-stack-production-baseline-20261112.md) and [CK-C compiler-emission JOB 5342 PASS](co1-ck-c-jes-5342-compile-only-result-20261112.md). The governing [coroutine milestone](milestone-implement-coroutine-support-for-native-compiler.md) and [CO.1 research gates](coroutine-research-and-design-gates.md) require an owner-reviewed ABI before implementation. This document **does not approve** a new public global, descriptor, runtime patch or counted-entry semantics.

## 1. Historical compiler options reveal two kinds of counting sites

Source anchors: `richards-bcpltape/bcplib/bcpl/bcpl`, generator-option parser lines 177–212; `richards-bcpltape/bcplib/bcpl/cg`, `CGSAVE` lines 652–675, `INSERTCOUNT` lines 2110–2114 and `GEN*` emitters around 2017–2093; `richards-bcpltape/bcplib/bcpl/cghdr`, system-vector offsets around lines 161–173.

- `K` sets `CALLCOUNTING`. With stack-check option `C` also set, `CGSAVE` emits `BAL 14,80(11)` plus an inline zero counter and a separate inline full frame-size word. CK-C's MVS compile-only JOB 5342 reported two verified +80 entries.
- `P` sets **both** `CALLCOUNTING` and `COUNTING`. With `C`, the entry remains +80, **and** generated executable-code sites may receive `INSERTCOUNT` instrumentation. `INSERTCOUNT` first aligns to four bytes with `CNOP(0,4)`, then emits `BAL 14,20(11)` and an inline `DC F'0'`. Its emission is controlled by `COUNTFLAG`; do not assert a universal number of additional sites without compiling a specific source.
- `K` without `C` emits +20 at procedure entry, after which the compiler emits `LR 5,15` itself. `P` without `C` also enables both entry and extra counted-code instrumentation.
- In the current reconstructed `bootstrap-toolchain/asm/bcplmain.asm`, **`CNTIMPL` at +20 and `STKCIMP` at +80 are stubs** that only advance R14 by four bytes, with **no counter increment**. Therefore supporting safe control flow does not, by itself, implement historical call counting or `P`-level profiling.

Historical `richards-bcpltape/sys1/userproc/bcplclg` defaults to `PARMC='/CK'`, but the missing original machine-code BCPLMAIN prevents asserting how its counters were updated, exported, cleared or read. The accepted native +60 checked-only stack tests cannot establish counting semantics.

## 2. Candidate shared-entry seam — design only

`STKIMPL` at `R11+60` already: (a) sets `R5=R15`, (b) fetches the required frame size at the current R14, (c) rejects invalid/non-word-aligned size, (d) tests `R15 + required-frame-bytes` against `STKLIM`, (e) restores saved R4 and (f) advances R14 to the next instruction. The existing source's `STKOVFL` and `STKFORM` branches remain part of that contract.

A **non-executed, source-derived candidate** for the combined service at +80 is:

```asm
STKCIMP  LA    14,4(14)      SKIP INLINE COUNTER
         B     STKIMPL       REUSE CHECKED FRAME ENTRY
```

If R14 initially addresses the inline counter at byte address `A`, the first instruction makes it `A+4` (the frame-size word). `STKIMPL` then inspects that word and, on success, advances R14 once more to `A+8` (the first executable instruction). It also establishes R5 and runs the existing full frame bound check. The compiler's `STM` saved R4–R6 before the entry; `STKIMPL` restores R4 from `0(R15)`. A branch, rather than a link call, must preserve the original continuation at R14. This would share existing checked-entry behavior **without duplicating the stack arithmetic**.

**Limit:** This candidate still leaves the counter word unchanged. It would make `/CK` *control-flow and stack-check compatible* with the current **stub-level** `K` behavior, **not** historically call-counting compatible. Nor does it prove behavior under all possible addresses, stack arithmetic overflow, MVS abends or coroutine switches. This fragment is an architectural proposal in a document, **not assembler submitted to IFOX or a patch to BCPLMAIN**.

For the S1 direction, the common `STKIMPL` reads the **currently installed** `STKLIM`; a future native switch must coordinate that with external `BCPLAPT APLIMIT` and agreed stack-bound metadata. The proposal does not itself implement or validate such switching.

## 3. Owner decisions required for CK-D

| Alternative | Meaning | Unresolved acceptance issue |
| --- | --- | --- |
| **Count-compatibility first** | Make +80 use existing checked-entry service while leaving counter operations at their current stub behavior | Admit explicitly that `K`/`P` instrumentation is emitted but **not accumulated**; define whether this bounded functionality can ship |
| **Full historical counting** | Implement increment/usage of +20 and +80 inline counters as part of the compatibility fix | Determine counter arithmetic, wrap behavior, instrumentation ownership and output/inspection API from evidence; needs separate tests and review |

These alternatives are **not owner approvals**. An initial safety-only candidate is a low-change option but must not be advertised as supporting historical profiling. The existing CO.1 E1/E2 switch-entry and D1/D2 stack-diagnostic choices remain separately open. No descriptor offsets, register save set, new globals or first-activation frame is selected here.

## 4. New isolated compiler-only counting investigation

The committed `tools/bootstrap/probe-co1-counting.py` is a separate, one-job **compile-only** probe. It uses the unchanged `tests/bootstrap/51-checked-recursion/source.bcpl` and the 80-column `/CPN` fixture at `packaging/milestones/coroutines/probes/co1-counting/cambridge-parm.txt`. Generator `C` requests checked entry, `P` requests entry and code-site counting, and `N` suppresses binary deck output.

Its source oracle requires:
1. At least two complete +80 procedure entries (counter zero, frame-size word with one positive, word-aligned `Lnnn EQU` definition per entry).
2. At least one complete **separate +20 counted-code site** with a zero inline counter; every +20 branch must have this structure.
3. No +60 checked-only entry and at least one `BALR 6,4`.

The wrapper invokes the existing `tools/bootstrap/compile-mvs` only: `ICINT19` and textual CODE recovery; **no IFOX, IEWL, or native GO**. It keeps `compiler.log`, `generated.s370.asm` and `summary.json` in a fresh `workarea/co1-counting/<UTC-run-id>/`, recording compiler RC, source/parameter hashes, Git HEAD, job ID if known, entry/site counts and explicit `assembled:false`, `linked:false`, `native_go:false`. It prints only a compact PASS/FAIL, JOB and evidence-directory line; never the complete JCL or assembler.

**Current evidence status:** The new `/CPN` probe is **PREPARED, NOT YET MVS-RUN**. In the assistant's isolated local workspace, `tools/checks/test_co1_counting_probe.py` passed **12/12** Python unit tests, including both missing/malformed +20 and +80 cases; `py_compile` passed with warnings treated as errors; and a **fake compiler-driver** end-to-end smoke produced two +80 and one +20 entry. Synthetic smoke **JOB 9999 is NOT an actual JES job** and must not be entered as native acceptance. Existing CK-C code and MVS objects remain unchanged.

Additional source-contract audit: **26/26** static source assertions passed, including `CGSAVE`, `INSERTCOUNT`, `CNTIMPL`, `STKCIMP`, `STKIMPL` and `BCPLAPT APLIMIT`. An **abstract, non-MVS** offset/boundary model passed **180/180** cases showing the candidate entry's `A -> A+4 -> A+8` arithmetic for bounded positive/aligned frame sizes. Neither constitutes actual System/370 execution of the candidate.

## 5. Next gate and restrictions

The owner may run the isolated `/CPN` compile-only probe to establish whether the resident compiler emits extra +20 sites, and the result should be recorded with exact JES JOB, revision, RC and retained evidence path. This does **not** authorize executing the generated code against current `CNTIMPL/STKCIMP`. CK-D still needs owner review of counted-entry semantics and Core Runtime module ownership before considering a candidate assembler implementation and later candidate-only IFOX/IEWL/GO.

**CO.1 IN PROGRESS; design gate OPEN. CO.2–CO.5 NOT STARTED.**
