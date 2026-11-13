# CO.1 — Native `CO1INIT` return discrepancy: F​INIT evidence

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (IN PROGRESS)  
**Date:** 13 November 2026  
**Evidence:** Owner-reported actual MVS output; generated assembler not yet provided

## Observed execution

Running GitHub `main` at
`65791e7ef84af6225104a02a8ac5173a7f5713c9`, the owner
reported:

```text
Git pull RC=0
HEAD=65791e7ef84af6225104a02a8ac5173a7f5713c9
CO.1 BCPL FAIL: native BCPL records differ: ['FINIT']
CO.1 BCPL evidence: workarea/co1-bcpl-switch/20261113T195531Z-63mtn5ew
CO.1 native BCPL runner RC=1
```

The exact reported output is `CO1BCPL FINIT`, not a coroutine
success trace. The local evidence directory is on the owner's WSL
system; its underlying JES job IDs, job report, and assembler listings
have **not** been supplied here and are not asserted.

## What this result proves and does not prove

The committed candidate runner calls its native-output checker only
after verifying a completed `CO1BGO` job with five RC=0000 steps
(ASMA, ASMM, ASMS, LKED, GO), a successful JES summary, and an
accessible printer report. Therefore the *runner-reported* `FINIT`
is a real native BCPL behavioral mismatch, not an assembler or
link-editor failure.

The current diagnostic BCPL source writes `FALLOC` if
`GETVEC(1087)` returns zero; `FINIT` if the call
`CO1INIT(ROOT,PEER,STACK,WORKER)` compares nonzero; and
`FARG`/`FVALUE` for later worker/first-switch failures.
The absence of `A1` and appearance of `FINIT` means the
initialization call/return is the first failing checkpoint; the
worker has not yet been activated.

In tracked `co1change.asm`, `CO1INIT` ends:

```asm
         SR    7,7
         BCR   15,11
```

The tracked `BCPLMAIN RETIMPL` restores R6, R5 and R4 before
branching to R6, without intentionally changing R7. On the
documented Cambridge ABI, a normal `CO1INIT` completion should
therefore return zero in R7. The reason the BCPL caller observed
a nonzero comparison is **unresolved**; possible sources of mismatch
include the generated call/compare sequence, the actual entry and
return route, or caller-frame effects. None is asserted as proven.

## Next evidence before editing assembly

Inspect the existing
`workarea/co1-bcpl-switch/20261113T195531Z-63mtn5ew/generated.s370.asm`
(the exact emitted Cambridge assembly). This listing is generated
by the user's completed compile job, is not the output of a host
compiler simulation, and does not require another JES submission.
Review the emitted `CO1INIT` call, argument setup in R7–R10,
return to R6, and comparison of R7 to zero. Correlate against
`co1change.asm`, `RETIMPL`, and the saved GO summary if needed.

No source fix, additional MVS execution, installed-object change,
MR10 development, numbered regression, production acceptance, or
CO.1 closure is justified solely by the current `FINIT` record.
