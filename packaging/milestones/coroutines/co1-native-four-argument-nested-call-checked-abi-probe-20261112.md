# CO.1 — Checked native four-argument and nested-call ABI probe

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture
**Recorded:** 12 November 2026 (Louisville)
**GitHub source examined:** `9e06458ea7a0bfaff71e99affe65d25084887229`
**Evidence classification:** SOURCE-OBSERVED; HISTORICAL NATIVE TEST-REPORTED; HOST-ONLY TESTED; fresh MVS probe NOT YET RUN
**Status:** CO.1 IN PROGRESS, design gate OPEN; CO.2–CO.5 NOT STARTED

## Objective and authority

Continue the [initial CO.1 ABI investigation](co1-native-abi-and-stack-source-investigation-20261112.md) beyond the [checked/count option investigation](co1-ck-d-shared-checked-entry-and-counting-investigation-20261112.md) by verifying the **R7–R10 four-argument save**, **nested BCPL function calls**, **checked frame entry** and **normal return through the system vector** in one fresh resident Cambridge compiler source. This is an isolated **compile-only** probe for the [coroutine milestone](milestone-implement-coroutine-support-for-native-compiler.md). It does not select E1/E2, a native coroutine descriptor, the switch register save set, or a first-run frame.

## Source-derived native ABI

| Path | Evidence and resulting requirement |
| --- | --- |
| Four formals | `CGSAVE(N)` in `richards-bcpltape/bcplib/bcpl/cg` emits `STM 4,A,0(15)`. At four BCPL formals, A extends to `R10`; the existing native Bootstrap 15 README records `STM 4,10,0(15)` in the accepted four-argument callee |
| Checked entry | With generator `C`, `CGSAVE` calls `BAL 14,60(11)` followed by inline `DC A(Lnnn) STACK FRAME SIZE`. `STKIMPL` sets R5 from R15, checks byte-sized full frame against `STKLIM`, and advances R14 past the inline fullword |
| Nested call | `CGAPPLY` establishes new R15 from R5 and executes `BALR 6,4`; the caller's frame and continuation must remain valid across nested function calls |
| Normal return | Generated `BCR 15,11` transfers to the R11 system-vector return service. Current `BCPLMAIN RETIMPL` restores R6, R5, R4 from the callee and caller frames |
| Result | R7 carries normal BCPL function result; nested-call test 17 documents its successful propagation under the earlier native profile |

**Historical native observations, not new receipts:** Bootstrap **15 — Four-argument BCPL linkage** records IFOX/IEWL/GO RC0000 and result `42` from JOB **994** (6 October 2026). Bootstrap **17 — Nested calls** records IFOX/IEWL/GO RC0000 and result `42` from JOB **998** (6 October 2026). These are useful historical test documents but neither is a fresh checked-entry combination or native coroutine switch.

## The isolated candidate source

`packaging/milestones/coroutines/probes/co1-abi/source.bcpl` defines `SUM4(A,B,C,D) = A+B+C+D`, `WRAP(X,Y) = SUM4(X,Y,10,20)` and `START()` calling `WRAP(5,7)` before passing the result to `DEBUGINT`. The logical result is 42, but **it is not executed in this probe**.

The separate 80-column `cambridge-parm.txt` begins `/CN`: C requests checked entry, N suppresses the binary object deck. This avoids the unresolved +80 `/CK` handler and leaves the approved +60 checked-entry contract isolated.

## Reusable one-job MVS-facing compiler-only probe

The committed `tools/bootstrap/probe-co1-native-call-abi.py` invokes only the existing `tools/bootstrap/compile-mvs`, with pinned compiler image `CAMBCOMP` and job name `CO1ABI`. The MVS job uses `ICINT19` to compile and `IEBGENER` to recover textual System/370 assembler; there is **no IFOX, IEWL, native GO, coroutine switch, object installation or permanent dataset overwrite**.

Its emitted-code verifier requires:
1. At least three complete +60 checked entries, each with its own immediately following inline frame-size word, uniquely defined positive/word-aligned `EQU`.
2. Exactly one `STM 4,10,0(15)` for the four-argument callee.
3. At least three ordinary `BALR 6,4` calls (WRAP-to-SUM4, START-to-WRAP and START-to-DEBUGINT), at least one `LA 15,n(5)` workspace formation and one `BCR 15,11` system-vector return.
4. No +20 or +80 counted-entry service in the isolated `/CN` output.
5. Resident compiler driver RC=0, exactly one JES job number, and a nonempty recovered assembler.

**Oracle qualification:** These assertions verify *emission structure*, not that each nested call restores every live register correctly at execution. The generated procedure names and specific frame offsets are not verified by this simple textual oracle. Any failure needs inspected retained evidence; do not treat it as a regression in an already accepted native program without checking the output.

The command prints only compact PASS/FAIL with JOB and counts, plus the evidence directory. It preserves `compiler.log`, `generated.s370.asm` and `summary.json` under a new `workarea/co1-native-call-abi/<UTC>/` directory. The summary records exact Git HEAD, fixture hashes, compiler driver RC, job ID if recovered, checked-entry and call counts, frame sizes, and `assembled:false` / `linked:false` / `native_go:false`.

## Local verification performed before commit

- `python3 -W error -m unittest discover -s tools/checks -p test_co1_native_call_abi.py -v`: **15/15 PASS**, including negative tests for malformed inline metadata, unexpected +20/+80, duplicate/missing four-argument save, missing continuation and workspace, and invalid frame sizes.
- Both Python files passed `python3 -W error -m py_compile`.
- An end-to-end invocation against a **fake locally installed compiler driver** passed and preserved all evidence; its **JOB 8123 is synthetic, NOT a real MVS JOB**.
- The four GitHub blobs for the Python runner, unit tests, BCPL fixture, and `/CN` option file match the locally tested `git hash-object` identities exactly.
- Additional current-source assertions inspected the generator, runtime checked-entry path, accepted Bootstrap 15/17 test descriptions, and historical counting flag placement. The source also sets `COUNTFLAG := COUNTING` after branch emission and after a label, but this does **not** alone prove an eventual counter-increment implementation preserves System/370 PSW condition code. That question remains separate.

**Actual MVS result:** PENDING the owner-executed compile-only probe; no target JES evidence or generated output is claimed here. This checkpoint leaves the historical `/CK` discrepancy, R14/condition-code rules and all major CO.1 coroutine design decisions open.

**CO.1 IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED.**
