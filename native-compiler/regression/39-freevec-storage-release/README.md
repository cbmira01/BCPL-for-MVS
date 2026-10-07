# 39 - FREEVEC storage release

This regression makes successful MVS storage release through FREEVEC
behaviorally observable.

Expected output:

```text
42
```

## Allocation size

The test repeatedly calls:

```bcpl
GETVEC(252)
```

For the current WIP allocator, GETVEC(N) obtains `(N+1)*4 + 12` bytes,
including the three-word private allocation header. For N=252 this is
exactly 1,024 bytes (1 KiB).

Using equal-sized 1 KiB allocations avoids depending on an exact initial free
storage figure while making the released extent suitable for an immediate
same-sized replacement request.

## Sequence

START repeatedly allocates 1 KiB vectors until GETVEC returns zero. Each
successful vector stores the previous head pointer in `V!0`, creating a
BCPL-side chain solely so at least one live allocation is retained explicitly.

Once allocation has been exhausted:

1. if no allocation ever succeeded, emit 98;
2. otherwise FREEVEC the most recently allocated 1 KiB block;
3. immediately request another 1 KiB block;
4. emit 42 if that replacement succeeds;
5. emit 99 if it still fails.

The remaining live allocations are intentionally left for MVS task termination
cleanup. The regression is concerned only with whether FREEVEC makes one
same-sized extent available again.

## Contract under test

Tests 28 and 29 established FREEVEC list traversal/unlink behavior and normal
execution through the FREEMAIN path, but their observable output did not depend
on storage actually being returned to MVS.

Test 39 strengthens that contract:

- repeated GETVEC calls must reach a genuine allocation-failure state;
- FREEVEC must identify and unlink a known live allocation;
- FREEMAIN must return that extent to MVS;
- a same-sized GETVEC must then succeed.

No exact address reuse is required.

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly `42`;
- reach GETVEC failure before FREEVEC is called;
- call FREEVEC on a known live 1 KiB allocation;
- succeed on the immediately following same-sized GETVEC.

Generated S/370 inspection should confirm the loop, G!87/G!88 calls, and
post-FREEVEC retry.

## Scope

This does not establish historical invalid-pointer behavior, subpool policy,
allocator coalescing, or exact address reuse. It tests the current one-GETMAIN
per GETVEC / one-FREEMAIN per FREEVEC policy.

## First run

The first run used 1 MiB blocks. The GO step completed normally but emitted
`98`, proving that even the first 1 MiB GETVEC could not be satisfied in the
small native test region. That did not exercise FREEVEC.

The test therefore now uses exact 1 KiB allocations. The behavioral contract is
unchanged: allocate equal-sized blocks to exhaustion, free one known live block,
then require one same-sized replacement allocation to succeed.

## Status

PENDING — revised after the first run proved the 1 MiB block size was too large.
