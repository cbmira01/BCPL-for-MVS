# Reconstructed BCPL runtime library

The `library/` directory contains portable BCPL runtime components reconstructed for the MR10 bootstrap environment. These modules are compiled separately and rendezvous with applications through the shared BCPL global vector.

The current validation baseline is `asm/icintv17.asm`.

## Validation status

The packaged allocator and coroutine layers have both been exercised successfully under ICINT V17.

The allocator regression:

```bash
tools/compile-and-run --results --listing heavy \
    asm/icintv17.asm \
    tests/11-getvec-freevec/getvec-freevec.bcpl \
    +library/getvec-freevec.bcpl
```

completes with interpreted `CODE = 0` after demonstrating variable-sized allocation, payload access, reuse, coalescing, and larger post-coalesce allocation.

The packaged coroutine create/delete regression:

```bash
tools/compile-and-run --results --listing heavy \
    asm/icintv17.asm \
    tests/10-coroutines/create-delete-static-pool.bcpl \
    +library/getvec-freevec.bcpl \
    +library/coroutines.bcpl
```

completes with interpreted `CODE = 0` after creating two coroutines, executing them, deleting them, reusing freed storage for a third coroutine, and returning to a root-only coroutine list.

The packaged `RESUMECO` parent-transfer regression:

```bash
tools/compile-and-run --results --listing heavy \
    asm/icintv17.asm \
    tests/10-coroutines/resumeco-chain.bcpl \
    +library/getvec-freevec.bcpl \
    +library/coroutines.bcpl
```

also completes with interpreted `CODE = 0`, preserving the already-established parent-transfer behavior through the library boundary.

## `getvec-freevec.bcpl`

Provides a simple first-fit fixed-arena allocator:

```text
GETVEC:87
FREEVEC:88
HEAPINIT:89
FREEHEAD:90
```

`HEAPINIT(BASE, WORDS)` installs an already BCPL-addressable arena. `GETVEC(N)` returns storage for a BCPL `VEC N`, and `FREEVEC(V)` reinserts the block by address and coalesces adjacent free blocks.

The allocator deliberately does not request arbitrary MVS storage. The arena remains inside ICINT's existing BCPL word-address space, so the V12 pointer representation does not change.

## `coroutines.bcpl`

Provides the portable coroutine operations:

```text
CREATECO:91
DELETECO:92
CALLCO:93
COWAIT:94
RESUMECO:95
```

These assignments are provisional reconstruction-local globals until the final runtime header is reconciled.

The module depends on:

```text
CHANGECO:6
CURRCO:7
COLIST:8
GETVEC:87
FREEVEC:88
```

`CHANGECO` remains machine-dependent. Under the interpreted bootstrap its proven implementation is in `intcode/iclib.int`; the BCPL coroutine module does not depend on how the backend implements the switch.

The established descriptor layout is:

```text
C!0 = saved P
C!1 = parent coroutine, or 0 when inactive
C!2 = COLIST link
```

The synthetic MR10 startup frame begins at `P=C+3`:

```text
P!2 = FN
P!3 = SIZE
P!4 = C
```

Keeping the descriptor below the synthetic frame is important: an earlier experiment stored persistent list metadata immediately above the initial frame, where nested calls later overwrote it.

## Current architectural boundary

```text
portable BCPL runtime
    HEAPINIT
    GETVEC
    FREEVEC
    CREATECO
    DELETECO
    CALLCO
    COWAIT
    RESUMECO

machine-dependent runtime
    CHANGECO
```

This separation is intentional. The interpreted bootstrap may continue to use the hand-written INTCODE `CHANGECO`, while the eventual native System/370 runtime can provide a native implementation without changing the portable allocator or coroutine semantics.
