# 30 - GETVEC allocation failure

This regression establishes the first BCPL-facing allocation-failure contract
for native G!87 GETVEC.

Expected output:

```text
4242
```

## Sequence

The test first performs an ordinary small allocation after the GETVEC
implementation has been changed from unconditional GETMAIN to conditional
GETMAIN EC. This emits the first 42 and verifies that the successful path
still works.

It then requests GETVEC(4194299). For the current 24-bit runtime this
corresponds to almost the entire 16 MiB address space once the private
allocation header is included. The request is within the WIP arithmetic
bound, so it reaches MVS GETMAIN EC, but it cannot be satisfied in the
running MVS address space because program, runtime, and system storage
already occupy part of that space.

The required result is BCPL zero. The test emits the second 42 only if that
zero result is observed; an unexpected successful allocation emits 99.

## Runtime contract under test

GETVEC now:

- rejects negative N with result zero;
- rejects N greater than 4,194,299 with result zero;
- computes (N+1)*4 + 12 only after that bound check;
- uses conditional GETMAIN EC;
- returns zero when MVS reports allocation failure;
- creates no VECLIST record on a failed allocation;
- preserves R0-R3 and R15/W across the MVS service call;
- retains the successful GETVEC behavior proven by Tests 27-29.

The upper bound exists because the current native runtime is a 24-bit
System/370/MVS implementation and the WIP allocation length must remain
representable below 16 MiB.

## Scope

This test establishes failure-to-zero behavior, not a complete historical
allocator policy.

It does not yet prove exact historical subpool selection, an internal
first-fit/coalescing heap, heap growth/contraction, invalid FREEVEC error
behavior, or any moving compaction scheme.

## Status

PASS.

Job 1150 on 2026-10-07 compiled the BCPL test through the resident Cambridge
compiler path. Job 1151 then assembled, link-edited, and executed the native
program successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
4242
```

The first 42 proves that normal GETVEC allocation still works after changing
the runtime to conditional GETMAIN EC. The second 42 proves that an
unsatisfied allocation is reported to BCPL as zero rather than causing an
ABEND.

This establishes the first recoverable native allocation-failure path. It
does not settle the historical internal heap architecture or invalid
FREEVEC behavior.

First attempt: Job 1144 compiled the BCPL source successfully. Job 1145
failed in IFOX with RC=0008 before link-edit or execution. A syntax cleanup
was tried, but Job 1147 also failed in IFOX with RC=0008.

The underlying GETMAIN interface was then corrected to the historical EC
form. Job 1149 proved that GETMAIN EC itself expands successfully. The sole
IFOX diagnostic was IFO209 on the preceding C 7,=F'4194299' instruction:
the literal had been placed at the end of the CSECT beyond active base
addressability after DROP 10. The bound is now stored as nearby WIP data
(GVRMAX), addressable through the active SYSV/R11 base. The behavioral
contract of the test is unchanged.
