# CO.1 — Generation-token same-address native PASS: JOB 5372/5373

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (**IN PROGRESS**)  
**Recorded:** 13 November 2026 (Louisville local date; UTC evidence on 14 November)  
**Classification:** **OWNER-REPORTED NATIVE-MVS-TESTED**, bounded generation-token experiment  
**Disposition:** Isolated candidate PASS; production ABI/design gate OPEN; CO.2–CO.5 NOT STARTED.

## Exact tested revision and operator receipt

GitHub `main` revision tested:

`4ffd056c95291b61b256ed0edeb6bb973a4d0f7d`

The owner executed
`tools/coroutines/run-co1-bcpl-generation.py --run` and reported:

```text
Git pull RC=0
HEAD=4ffd056c95291b61b256ed0edeb6bb973a4d0f7d
CO.1 BCPL PASS: compiler JOB 5372, GO JOB 5373; IFOX 3, IEWL 1, GO 1; A1 R1 A2 R2 PASS
CO.1 BCPL evidence: workarea/co1-bcpl-generation/20261114T025629Z-l6mr6x21
CO.1 generation native runner RC=0
```

The inherited strict MVS runner requires successful Cambridge
compilation, a completed `CO1BGO` job with three IFOX steps
(`ASMA`, `ASMM`, `ASMS`), IEWL `LKED` and native `GO`, all
RC=0000, highest RC=0000, and exactly these five ordered native
BCPL output records:

```text
CO1BCPL A1
CO1BCPL R1
CO1BCPL A2
CO1BCPL R2
CO1BCPL PASS
```

Full generated assembler and JES reports remain preserved in the
owner's WSL workarea. They were not separately supplied to the
assistant for independent review. This evidence is therefore
classified on the owner's actual runner output, not independent
machine-level inspection.

## Behavior supported by this native experiment

The BCPL fixture allocates one `GETVEC(23)` descriptor and
`GETVEC(1087)` stack for worker 1. `CO1INIT` issues the test-only
first-generation token **6**. Worker 1 executes, yields value 101,
resumes with 11, checks its local sentinel and returns 31. The root
revokes this terminated worker and frees its stack.

The root then allocates a replacement stack and deliberately
reinitializes worker 2 **using the exact same still-allocated
descriptor vector address**. The test expects token **10**, and
requires old token 6 not to resolve although token 10 maps to the
same physical descriptor address. The `CALLH` BCPL wrapper rejects
old token 6 with `-1` without calling the raw context switch.
Worker 2 must enter, yield 202, resume with 22, check local state
and return 42. Its token is revoked before stack and descriptor
storage are released, after which both old and new tokens must
fail resolution through `CALLH`.

That is native evidence for the **bounded identity separation
between successive worker lifetimes at the same descriptor
address**, including actual compiler-generated continuations and
normal returns for both workers. The host-only model additionally
exercised identical-address ABA token behavior, but the real BCPL
fixture itself already deliberately reuses the descriptor vector.

## Exact limitations and disposition

The experiment does **not** rely on, or demonstrate, an MVS
`GETMAIN` allocator returning a previously freed descriptor
address. It retains the descriptor allocation throughout both
worker lifetimes.

`CO1RES` provides test-only token resolution; `CALLH` is a BCPL
façade, not a production-enforced opaque-handle `CHANGECO`
interface. Raw `CHANGECO` remains callable with descriptor
pointers. The lookup and switch are separate operations and are
not designed to be atomic across MVS subtasks. No general stale
pointer safety, arbitrary-pointer recovery, task reentrancy,
full handle/ownership contract, ABI stability, wraparound beyond
the designed refusal, or production allocation reuse policy is
approved. G!295–299, the registry size, state values and return
codes remain experimental.

The run used temporary candidate objects and native load datasets,
with the installed `BOOT_OBJ` read-only. It did not install or
promote production Core Runtime code, reserve public globals,
modify historical sources, create numbered regressions, or close
CO.1.

**CO.0 CLOSED (qualified); CO.1 IN PROGRESS; CO.2–CO.5 NOT STARTED.**
Next gate: owner-reviewed production descriptor identity, enforced
handle validation, storage ownership, stack/guard and lifecycle
design before CO.2.
