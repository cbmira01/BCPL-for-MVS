# CO.1 — Indirect-entry compiler-only result: JOB 5346

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.1 — Native ABI and Stack Architecture
**Recorded:** 13 November 2026
**Execution revision:** `c2a68b719be82fcb8d6f23191edaaef10a930aef` (verified by the owner's guarded WSL command)
**Evidence class:** OWNER-REPORTED REAL MVS COMPILER-ONLY PROBE; local assembler/JES records not independently inspected
**Disposition:** Emitted-code oracle PASS; CO.1 IN PROGRESS, design gate OPEN; CO.2–CO.5 NOT STARTED

## Exact owner-reported result

The owner executed the guarded MVS-facing invocation of `tools/bootstrap/probe-co1-indirect-entry.py`, which required a successful quiet fast-forward GitHub pull and an exact local HEAD match before submitting the job. Its console output was:

```text
CO.1 INDIRECT PASS: JOB 5346, checked 4, three-formal 1, calls 4; compile-only
CO.1 INDIRECT evidence: workarea/co1-indirect-entry/20261113T082652Z-rjkhlkxp
CO.1 indirect compiler-only RC=0
```

**Retained evidence on owner WSL host:** `workarea/co1-indirect-entry/20261113T082652Z-rjkhlkxp/`. The tracked wrapper writes `compiler.log`, `generated.s370.asm` and `summary.json` here. These local files were not provided and have **not been independently inspected**. Exact frame sizes, stored hashes, and individual JES step return codes are not claimed in this report.

## Checked source and accepted scope

The versioned `tools/bootstrap/probe-co1-indirect-entry.py` invokes the existing `tools/bootstrap/compile-mvs` with `CAMBCOMP` and `/CN`, using the isolated [BCPL fixture from the preparation checkpoint](co1-first-activation-return-frame-and-indirect-call-investigation-20261113.md). The established driver compiles through `ICINT19` and recovers textual System/370 CODE. The wrapper requires zero compiler-driver RC, a single recognized JES job identifier, and all the following textual assembler conditions:

- At least four complete `BAL 14,60(11)` entries, each followed by the correctly defined, positive word-aligned inline frame-size fullword.
- One `STM 4,9,0(15)` three-formal entry for `CALLIND(F,A,B)`.
- At least three `BALR 6,4` calls, an `LA 15,n(5)` workspace formation, and a `BCR 15,11` normal return.
- No +20 or +80 counting-service entries under `/CN`.

The owner-reported result meets these probe conditions with **four checked entries, one three-formal entry, four calls, JOB 5346 and RC=0**. That is source-backed *compiler-emission* evidence, not an independent reinspection of the actual code listing.

The fixture passes a procedure value through `NEST(F,X)` to `CALLIND(F,A,B) = F(A,B)`. Its BCPL arithmetic would produce 42, but **no native GO result of 42 was observed**. Importantly, the structural verifier does **not** check the actual instruction used to load `F` as the indirect target; correct native indirect invocation remains unverified.

## Explicit exclusions and next review

There was **no IFOX, IEWL, native GO, coroutine CHANGECO, synthetic first-entry frame or S1 safe-limit transition**. The [first-activation return-frame review](co1-first-activation-return-frame-and-indirect-call-investigation-20261113.md) remains the design reference: the native `RETIMPL` requires both a valid exit continuation and an addressable synthetic caller-frame word zero. Source evidence does not yet approve any actual frame offsets, descriptor layout, E1/E2 switch interface, register/PSW save set, D1/D2 diagnostics, or public global assignments.

The earlier preparation note's pending-MVS state is now superseded for this specific probe. No runtime sources, test manifests, accepted MVS objects, datasets or historical compiler material have been changed by this evidence-only checkpoint.

**CO.1 IN PROGRESS; design gate OPEN; CO.2–CO.5 NOT STARTED.**
