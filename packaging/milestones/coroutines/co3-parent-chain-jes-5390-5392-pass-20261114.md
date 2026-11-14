# CO.3 — Parent-chain native PASS, JOBS 5390–5392

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.3 — Coroutine Library and Lifecycle (**IN PROGRESS**)  
**Local date:** 14 November 2026  
**GitHub revision tested:** `52801f6274a78ea8f227ef7505f239b417269122`  
**Classification:** OWNER-REPORTED NATIVE-MVS-TESTED

The owner executed `tools/coroutines/run-co3-first-lifecycle.py`
`--scenario parent-chain --run` and reported:

    CO.3 first lifecycle PASS: compiler JOBS 5390/5391,
      native JOB 5392; IFOX 4, IEWL 1, GO 1
    CO.3 parent-chain verification RC=0

The strict runner requires four IFOX steps, IEWL and GO all RC=0000,
job result SUCCESS/highest RC=0000, and exactly 13 ordered BCPL records:

    MADE A1 B1 A2 B2 R1 A3 R2 B3 R3 A4 R4 PASS

Operator-local complete receipts remain at:
`workarea/co3-first-lifecycle/20261114T232638Z-skwqfecr`.
The assistant inspected the GitHub candidate and strict oracle, not the
operator-local raw JES report. Do not elevate this owner-reported evidence
to independently inspected assembly/JES output.

This validates independent Cambridge BCPL application and library
compilation, separate IFOX object modules and IEWL linkage, native nested
`CALLCO`/`COWAIT`/`RESUMECO`, busy-target refusal, preserved continuation
locals, ordinary return/re-entry, parent-chain transfer, and root stack
boundary restoration within the bounded candidate.

The first parent-chain JOB 5389 remains a separate FAIL (GO RC=0012,
full 132-byte output buffer, truncated final marker). Its fixture was
corrected to use the native `WRCH(10)` newline control for this PASS.

The next gate is separately linked `DELETECO`, IFOX unregister-before-
`FREEVEC`, and reproducible registry/storage reuse; public ABI,
production objects and release enrollment remain unapproved.

**Disposition:** CO.3 IN PROGRESS; CO.4 and CO.5 NOT STARTED.
