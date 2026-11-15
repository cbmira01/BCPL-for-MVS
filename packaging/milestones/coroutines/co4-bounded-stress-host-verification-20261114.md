# CO.4 — Bounded stress/refusal candidate: host verification

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.4 — Robustness and Edge-Case Verification (**IN PROGRESS**)  
**Source authority:** GitHub `main` baseline `aca120fdf444e8aa8a14f8167b1fb2a74f28f337`  
**Evidence classification:** **HOST-CHECKED / NATIVE MVS PENDING**  
**Recorded:** 14 November 2026, Louisville local date (15 November UTC)

## Reviewed candidate

- `packaging/milestones/coroutines/candidates/co4-bounded-stress/source.bcpl`
- `packaging/milestones/coroutines/candidates/co4-bounded-stress/README.md`
- `tools/coroutines/run-co4-bounded-stress.py`
- `tools/coroutines/test_run_co4_bounded_stress.py`

The approved test uses two known-live workers, 16 alternating calls per worker, 15 suspended recursive continuations per worker, bounded refusals, root context validation and orderly deletion. The machine oracle is exactly nine `CO4BCPL` records. The accepted CO.3 BCPL library, CO3DROP candidate, BCPLCO and installed `BOOT_OBJ` are not changed.

## Host verification (assistant workspace)

- Checked the additive patch with `git apply --check` in a separate disposable Git repository; applied cleanly.
- Compared all four added files byte-for-byte with the supplied ZIP; all matched.
- Ran `python3 -B -m unittest discover -s tools/coroutines -p 'test_run_co4_bounded_stress.py' -v`: **10 PASS, 0 FAIL**. Synthetic success/failure receipts are explicitly not MVS evidence.
- Ran Python bytecode compilation of both runner and unit-test modules: **PASS**.
- Ran the candidate's `--check` source/identity validator in an isolated review workspace: **PASS**. The accepted CO.3 library, `co3drop.inc` and compiler options were copied from their reviewed GitHub source; their calculated Git blob identities matched the three pinned values.
- Exercised the exact nine-record parser and checked rejection of extra and malformed `CO4BCPL` records: **PASS**.

**Limit of this host evidence:** The isolated validation workspace used existence-only placeholders for the inherited runner and assembler paths. It did **not** run a full checkout's inherited compilation pipeline, the Cambridge compiler, IFOX, IEWL, JES or native GO. No target job number, target RC or native PASS is claimed. The operator-facing runner must perform these checks with a complete current GitHub checkout under MVS.

## Required target evidence

The first native run is gated on two independent real Cambridge compilation receipts, four RC=0000 IFOX steps, RC=0000 IEWL, RC=0000 GO, JES SUCCESS/highest RC=0000, and the exact nine-record oracle. Preserve any initial failure separately; use the resulting `workarea/co4-bounded-stress/` evidence for source-revision-tracked review. Do not alter installed `BOOT_OBJ`, permanently allocate G!289–300, or advance to CO.5 without the CO.4 acceptance gate.
