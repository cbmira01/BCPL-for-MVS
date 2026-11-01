# Milestone Runtime Extensions — R.1 positive-path MVS evidence

**Date:** 22 October 2026 (TK5 MVS job date). **Candidate source:** GitHub
`main`, commit `1ecbee157d62c042f4ee5f90666bf7e8e2cc5e7e`.
**Disposition:** Two integrated positive-path cases **PASSED**. R.1 — Generic
registration foundation remains **ACTIVE**. No accepted `BOOT_OBJ`
objects were updated or promoted.

## JOB 2226 — R1EMPTY

- ASMA, ASMN, ASMR, ASMG, LKED, GO: each **RC=0000**.
- IFOX: no flagged statements, highest severity 0.
- BCPL output: `R1 EMPTY BCPLREG PASS`.
- Linked a genuine 28-byte BCRG with N=M=0, generic `RGINIT` and
  `RGFINI`, and the temporary BCPLMAIN adaptation.
- Accepted `HERC02.BCPL.BOOT.OBJ` was accessed read-only (`DISP=SHR`).

## JOB 2228 — R1SELECT

- ASMA, ASMN, ASMR, ASMG, ASMD, ASMS, LKED, GO: each **RC=0000**.
- IFOX: no flagged statements, highest severity 0.
- BCPL output: `R1 SELECTED BCPLREG PASS`.
- A BCEX descriptor for `R1TEST` registered one assembler QUERY
  dispatcher at **test-only G!298**, using the selected BCPLREG object.
- The compiled BCPL caller tested QUERY size=6, undersized-buffer -1
  and unchanged guard words, six-word reply and untouched trailing guard,
  opcode 1 result 101, and unsupported opcode 2 result -2.
- Test objects and the linked load module were temporary; `BOOT_OBJ`
  was used read-only and remains unchanged.

## Evidence boundaries

These successful jobs show startup, registration and ordinary termination
for an empty registry and one selected no-dependency package. They do
**not** establish negative-diagnostic behavior 1001–1014, late-failure
transactionality, effective owner attribution, nonzero finalizer handling,
reverse finalizer order, STOP(n) behavior, or the full native regression
panel. In particular, `G!298` is a **test fixture**, not a new Global
Number Registry allocation. `G!200` remains BCPLQSAM's allocation.

The source evidence was the owner's complete JES job reports for JOBs
2226 and 2228 (including the IFOX and IEWL listings, and SYSPRINT).
No authenticated JCL or other local credentials are included here.
