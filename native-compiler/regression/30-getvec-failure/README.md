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

PENDING.

First attempt: Job 1144 compiled the BCPL source successfully. Job 1145
failed in IFOX with RC=0008 before link-edit or execution. A syntax cleanup
was tried, but Job 1147 also failed in IFOX with RC=0008.

The underlying issue was then identified: the older OS/360-style GETMAIN
macro interface used by this toolchain has unconditional register form R,
but conditional single-area allocation is form EC rather than the later
register-conditional RC form. The WIP now uses GETMAIN EC with A=GVRADDR
and tests the completion code returned in R15. The behavioral contract of
the test is unchanged.
