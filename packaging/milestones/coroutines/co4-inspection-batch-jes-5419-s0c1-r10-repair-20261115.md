# CO.4 — JOB 5419 S0C1: source-grounded CO4PROB R10 repair

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.4 — Robustness and Edge-Case Verification (**IN PROGRESS**)  
**Failed target revision:** `d1726d3cc3a829af679df671912677a9f3dc244b`  
**Reported:** 15 November 2026 UTC / Louisville local 14 November 2026  
**Evidence classification:** **OWNER-REPORTED NATIVE-MVS-TESTED — FAIL**  
**Repair classification:** **SOURCE-GROUNDED / HOST-CHECKED; NATIVE MVS PENDING**

## Separate failed attempt: native compiler/IFOX/IEWL succeeded, GO abended

The owner extracted the following directly from the original local
`workarea/co4-inspection-batch/20261115T031327Z-vrkmkomg/limits/`
receipt, after the first-attempt printer UTF-8 problem had been repaired:

- Cambridge compilation jobs: **5417, 5418**.
- Native `CO3BGO` JOB: **5419**.
- Four IFOX `ASMA`, `ASML`, `ASMM`, `ASMS`: **RC=0000** each.
- IEWL `LKED`: **RC=0000**.
- No GO RC=0000: `IEF450I CO3BGO GO - ABEND S0C1 U0000`
  and `IEF472I ... SYSTEM=0C1 USER=0000`.
- PSW at abend: `078D0000 000A9828`, `ILC 2`, `INTC 0001`.
- `JOB RESULT: FAILURE`; `HIGHEST RC: 0000` reflects only completed
  normal-RC steps and **does not** mean a successful GO.

The operator's report excerpt included literal EBCDIC `CO4LIM`
strings in a hexadecimal dump. They are not proof those records were
printed by BCPL. No valid LIMITS oracle was established. The
fail-fast batch did not run ACCOUNT or DENY. The separate earlier
UTF-8 decoding failure at `bdd1c4716cc0012d0ae314576d35bd489f4765bb`
remains separately documented as FAIL.

## Specific source defect

At the tested revision, test-only `co4probe.inc` had:

```asm
         BALR  10,0
         USING *,10
         ...
         L     15,=A(MEMSTAT)
         BALR  14,15
         LR    14,8
         SR    7,7
         B     C4PRET
```

The accepted `BCPLMEM` source defines `MEMSTAT` with `BALR 10,0`,
which **clobbers R10**. The test-only observer then performs
`B C4PRET` under its own `USING *,10`, but R10 still contains the
`MEMSTAT` base. This is a **definite wrong-base control-flow defect**
in the observer. It plausibly explains the reported operation
exception, although the provided truncated dump has not been mapped
to a specific machine instruction by a full link map.

The isolated repair saves the observer's R10 in R4 before loading/
calling `MEMSTAT`, then restores R10 **immediately on return**,
before the branch. `MEMSTAT` does not modify R4. R4 retains its
ordinary caller restoration through the original `RETIMPL` frame.
Original R14 continues to be saved/restored through R8.

Only the candidate `co4probe.inc`, its fail-closed source validator,
host tests and compact diagnostic reporting are changed. The
accepted `BCPLCO`, `BCPLMAIN`, `BCPLMEM`, CO.3 library, installed
`BOOT_OBJ`, Cambridge options, BCPL fixtures, and all 12/8/12
record native oracles are unchanged.

## Host verification and future target evidence

- The assistant's review workspace verified the original accepted
  `co4probe.inc` Git blob identity and the repaired blob identity.
  The repaired IFOX source remains ASCII, maximum 71 columns.
- **14 focused host tests PASS, 0 FAIL**, including detecting the
  original missing R10 restore, rejecting misplaced restoration,
  checking no unrelated machine statements were changed, and
  validating a bounded GO S0C1 diagnostic from synthetic JES text.
- The runner/test additions include further regression methods for
  the same contract and compact diagnostic path. This host model
  does not assemble or run System/370 machine code; no new MVS PASS
  is claimed.
- The next owner-operated test is **one** fail-fast inspection
  `--run` for LIMITS, ACCOUNT and DENY. It preserves independent
  new compiler/JES receipts and keeps both earlier failed directories.

**CO.4 remains IN PROGRESS; CO.5 NOT STARTED.** No public ABI,
permanent globals, installation, or release has been authorized by
this diagnosis.
