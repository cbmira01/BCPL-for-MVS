# BCPL memory management, heap allocation, and compaction

## Purpose

This note records the current project understanding of BCPL dynamic storage,
especially GETVEC/FREEVEC, heap allocation, coalescing, and the still-open
question of whether a historically relevant BCPL implementation used a very
simple compacting allocator.

Do not assume all BCPL implementations used the same allocator.

## Programmer-visible contract

Contemporary BCPL documentation describes GETVEC(N) as providing N+1 words
and FREEVEC as returning the vector to a managed heap. The proposed 1979
definition explicitly describes coalescing returned store with contiguous
free store and returning zero when allocation cannot be satisfied.

Reference:

- *A Proposed Definition of the Language BCPL* (1979), store-allocation
  discussion in Appendix A7:
  https://softwarepreservation.computerhistory.org/BCPL/cambridge/
  Middleton-Proposed_Definition_of_BCPL-1979.pdf

## Finning BCPL allocator

The 1977 Finning BCPL System Reference Manual documents a simple
general-purpose allocator using first fit, boundary tags, adjacent-free-block
coalescing, and a SLOP parameter controlling whether a small remainder is
split or absorbed into an allocation.

Reference:

- *Finning BCPL System Reference Manual* (1977), section 7.26:
  https://softwarepreservation.computerhistory.org/BCPL/finning/
  Finning_BCPL_Compiler_Reference_Manual__1977.pdf

This is an important implementation reference, but there is presently no
evidence that the Cambridge System/370 runtime used this exact algorithm.

## Richards Cintcode allocator

Richards' Cintcode documentation describes a particularly simple allocator
that is relevant to the remembered "simple BCPL heap allocator":

- blocks are chained in memory order;
- word zero of each block contains both size and allocation state;
- the least significant bit is the allocated/free flag;
- the remaining even value is the block size in words;
- GETVEC uses first fit;
- FREEVEC marks a block free; and
- GETVEC coalesces adjacent free blocks while walking the chain.

The block list lives inside the Cintcode memory itself.  This is not simply
one host malloc/free operation per BCPL GETVEC/FREEVEC request.

Richards also describes an extra size word before the user vector and guard
words after the block for detecting common allocation errors.

This algorithm is simple enough that it may be related to the remembered
allocator.  It still performs coalescing rather than moving live vectors.

Reference:

- Martin Richards, *The BCPL Cintcode System* / later Cintcode and Cintpos
  manuals, BLIB GETVEC/FREEVEC description.

## Coalescing versus moving compaction

Keep these concepts distinct:

```text
coalescing
    join adjacent FREE blocks
    live objects do not move

moving compaction
    relocate LIVE blocks to close holes
    references to moved objects must be repaired
```

The BCPL material identified so far explicitly documents coalescing, not
moving compaction.

Moving arbitrary BCPL objects is difficult because BCPL words are typeless;
a runtime normally cannot know which arbitrary words are pointers requiring
relocation unless the allocator uses handles, descriptors, or another
restricted reference discipline.

## Open research lead: simple compacting allocator

A specific recollection remains unresolved: there may have been a very simple
BCPL heap allocator with a compression or compaction operation based on a
simple algorithm.

Possible explanations include:

- the remembered implementation was the Richards Cintcode first-fit block
  chain, whose simplicity is now documented explicitly;
- the remembered operation was adjacent-block coalescing;
- compression meant compacting or rebuilding a free list;
- objects were referenced through handles, making movement possible;
- it belonged to a particular BCPL application or teaching runtime;
- it was from a later portable/Cintcode runtime; or
- it was a source-level library rather than BCPLMAIN.

This is worth searching explicitly rather than dismissing the recollection.
Useful search terms include BCPL compact store, compress store, heap
compaction, garbage collection, GETVEC, FREEVEC, PUTVEC, boundary tags,
storage map, and heap collect.

## Surviving System/370 evidence

SYS3 LIBHDR assigns GETVEC to G!87 and FREEVEC to G!88.

The surviving BCPLMAC material defines a VECLIST head and VECAREA fields:

```text
VECBASE   BCPL address of vector
VECLEN    number of bytes obtained
VECNEXT   link to next vector
```

This proves that allocated vectors were tracked explicitly by the historical
machine-dependent runtime. It does not by itself prove whether each BCPL
vector corresponded to one MVS allocation or whether larger MVS chunks were
subdivided by an internal BCPL heap.

APTOVEC at G!40 is another unresolved clue and should be investigated before
declaring the historical allocation architecture settled.

## Current reconstruction

Native regression Tests 27-29 currently implement a narrow host-backed
allocator:

```text
GETVEC(N)
    -> MVS GETMAIN
    -> three-word private allocation record
    -> return payload as BCPL word pointer

FREEVEC(V)
    -> search VECLIST
    -> unlink matching record
    -> MVS FREEMAIN
```

The private record mirrors the historical VECAREA shape:

```text
+0   VECBASE
+4   VECLEN
+8   VECNEXT
+12  payload
```

Tests 27-29 prove successful allocation, release, multiple live allocations,
and head/middle/tail VECLIST removal. These tests validate the WIP behavior;
they do not establish historical identity.

Test 30 changes GETVEC to conditional GETMAIN EC and establishes the
BCPL failure-to-zero contract.

## Candidate final architectures

Three plausible designs remain:

```text
A. direct host allocation
   GETVEC -> GETMAIN
   FREEVEC -> FREEMAIN

B. fixed BCPL heap
   one host arena
   first-fit/split/coalesce internally

C. expandable BCPL heap
   GETMAIN larger chunks
   subdivide/coalesce internally
   optionally return empty chunks with FREEMAIN
```

Model C is architecturally attractive because it reconciles an abstract BCPL
heap with explicit MVS storage ownership, but it remains an inference.

## Project rule

Do not replace the working Tests 27-30 implementation merely because a
portable BCPL allocator is attractive. First recover stronger historical
evidence. Keep the simple-compaction recollection open as a research lead.
