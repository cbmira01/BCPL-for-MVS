# 29 - Multiple live allocations

This regression stresses the VECLIST chain with several simultaneously live
GETVEC allocations and FREEVEC calls in different list positions.

Expected output:

```text
424242
```

## Sequence

GETVEC inserts new allocation records at the head of VECLIST. After allocating
A, B, and C, the WIP list is therefore:

```text
C -> B -> A
```

The test then deliberately exercises three unlink shapes.

First it frees B, a middle node:

```text
C -> B -> A
     |
     +-- FREEVEC(B)

C -> A
```

It verifies that A and C still contain their original values by emitting 42.

Next it allocates D, making D the new head:

```text
D -> C -> A
```

It frees D immediately, exercising head removal, and again verifies A and C
by emitting 42.

Finally it frees A while the list is:

```text
C -> A
```

This exercises tail removal. C is then read once more and combined with 10 to
emit the third 42 before C itself is freed.

## Purpose

Tests 27 and 28 established single GETVEC and FREEVEC operations. Test 29
proves that the WIP allocation bookkeeping remains coherent with multiple live
MVS allocations.

A passing test establishes that:

- multiple GETMAIN allocations can coexist;
- VECLIST chaining preserves all live allocation records;
- FREEVEC can unlink a middle record;
- FREEVEC can unlink the head record;
- FREEVEC can unlink the tail record;
- freeing one vector does not corrupt surviving vectors;
- a new allocation can be added after an interior free;
- every allocation in the test can ultimately be released normally.

Exact MVS storage addresses and address reuse are intentionally not part of
the contract.

## Status

PENDING.
