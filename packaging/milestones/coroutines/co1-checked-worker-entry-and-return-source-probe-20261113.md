# CO.1 — Checked worker entry and normal return: compiler-only probe preparation

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture
**Recorded:** 13 November 2026
**Reviewed GitHub `main` source:** `912b1a416cba08d9b56d031aecc370767053171f`
**Evidence class:** SOURCE-OBSERVED and ASSISTANT HOST-TESTED; real MVS emission result PENDING
**Status:** CO.1 IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED

## Purpose and authority

Following [JOB 5347's owner-reported saved-MVS R4-origin audit](co1-indirect-r4-origin-jes-5347-saved-evidence-pass-20261113.md), move from the indirect caller to the *ordinary generated callee entry and normal return* relevant to an eventual first-run worker. The authoritative [CO.1 milestone](milestone-implement-coroutine-support-for-native-compiler.md) requires design review before a native `CHANGECO` implementation. The [first-activation investigation](co1-first-activation-return-frame-and-indirect-call-investigation-20261113.md), [native runtime contract](../../architecture/runtime-contract-v1.md), and [stack-check contract](../../architecture/stack-check-contract.md) remain controlling.

This probe does **not** select E1/E2, synthesize an executable first-activation frame, add a Core Runtime primitive, allocate a descriptor or stack, assign a global number, patch installed MVS objects, or execute a worker in native GO.

## Source-observed ABI and required frame words

Historical `richards-bcpltape/bcplib/bcpl/cghdr` maps R4/R5/R6/R7 to callee-address `B`, frame pointer `P`, continuation `L`, and first argument `A1`. `richards-bcpltape/bcplib/bcpl/cg` `CGSAVE` calculates the last saved argument register and stores incoming registers beginning at R4 into the caller-provided workspace R15. For a generated one-formal `WORKER(ARG)`, the expected checked prologue is `STM 4,7,0(15)`, `BAL 14,60(11)`, and one inline generated frame-size word. The runtime `STKIMPL` establishes `R5=R15` and checks the full frame size against `STKLIM`.

The currently tracked `bootstrap-toolchain/asm/bcplmain.asm` `RETIMPL` is:

```asm
RETIMPL  L     6,8(5)
         L     5,4(5)
         L     4,0(5)
         BCR   15,6
```

The callee frame's saved words 0/1/2 therefore represent incoming R4, prior R5, and incoming R6. Upon normal return, R6 is restored from the callee's `8(R5)`, R5 from its `4(R5)`, and R4 from word zero of that **restored caller frame**, not from the callee's saved word zero. This order is source-observed; it is not proof that a never-run worker's synthetic caller has been constructed correctly.

**Consequence for design review:** any eventual worker entry through generated `CGSAVE` must receive a valid workspace R15, appropriate R4/R5/R6 and arguments, an addressable synthetic caller frame, a legitimate worker-exit continuation, and coherent active-stack limits before entering checked code. The precise initial state and trampoline remain owner decisions.

## New isolated real BCPL compiler fixture

- `packaging/milestones/coroutines/probes/co1-worker-entry/source.bcpl` defines `WORKER(ARG) = ARG+1`, `INVOKE(F,VALUE) = F(VALUE)`, and `START()`, which calls `INVOKE(WORKER,41)` and passes the result to `DEBUGINT`. Its intended result is 42, **not observed from native GO**.
- `cambridge-parm.txt` supplies one 80-column `/CN` record for checked entry, no deck.
- `tools/bootstrap/co1-worker-frame-oracle.py` checks one each generated `STM 4,6/7/8,0(15)` prologue for zero-, one- and two-argument procedures, three adjacent `BAL 14,60(11)` instructions with unique positive word-aligned frame-size definitions, the one-formal worker's normal `BCR 15,11` return, the two-formal indirect dispatch's `BALR 6,4`, at least three ordinary calls in total, and absence of +20/+80 counting calls. The oracle uses **machine-code shapes, not `ENTRY TO` name annotations**, following the JOB 5347 audit correction.
- The same oracle separately checks the **tracked BCPLMAIN source** for the exact `RETIMPL` instruction order and `STKIMPL LR 5,15`; this does not establish which resident binary is linked.
- `tools/bootstrap/probe-co1-worker-entry.py` invokes the installed `CAMBCOMP` image under `ICINT19` once, job name `CO1WRET`, and recovers assembler using the existing `tools/bootstrap/compile-mvs` driver. It does **not** assemble, link, or GO. It stores `compiler.log`, `generated.s370.asm`, and `summary.json` under a unique `workarea/co1-worker-entry/<UTC>/` directory, recording the exact Git revision, fixture and runtime source hashes, frame sizes, compiler RC, job number and explicit non-execution flags.
- `tools/checks/test_co1_worker_frame_oracle.py` is a **host-only** test suite and an abstract model of the existing return instruction order. This is not an implemented or approved first-activation frame.

The generated-code checks intentionally fail closed on different emitted forms. A failed oracle would require reviewing the preserved actual assembler; it is **not, by itself, evidence of a compiler regression**.

## Verification performed in the assistant's own workspace

- **27/27** `unittest` cases PASS, including missing/duplicate procedures, missing/bad frame metadata, checked-service count, missing/duplicate worker returns and nested calls, modified `RETIMPL`, and an abstract return-word model.
- **15/15** explicit source assertions PASS against the current GitHub historical generator, CGHDR, tracked BCPLMAIN and compiler driver.
- Python modules passed strict syntax compilation.
- A synthetic end-to-end run passed, preserving all three expected evidence files. Its **JOB 8126 is generated by a fake driver and is NOT an MVS/JES job**.
- All five Python/BCPL/option blobs were byte-matched against the locally tested workspace with Git blob hashes. BCPL source records and option lines fit within 80 columns.

## Next MVS gate and limits

A guarded `main` MVS-facing command can now submit one **compiler-only** `CO1WRET` job and report only its concise PASS/FAIL, job number if available, frame/call counts and evidence directory. No installed dataset mutation or source compilation at IFOX is requested. A compiler-emission PASS would provide evidence of the ordinary worker entry/return structure **only**.

The exact synthetic caller frame, entry/exit continuation, full register and condition-code save policy, S1 transition of `STKLIM` and `BCPLAPT APLIMIT`, diagnostics D1/D2 and lifecycle ownership remain **open for owner design approval** before CO.2.

**CO.1 IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED.**
