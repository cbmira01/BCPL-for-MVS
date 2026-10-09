# 082 — Outstanding vectors at termination

## Contract under test

BCPLMAIN must reclaim outstanding GETVEC blocks when a program
terminates through FINISH, before returning the combined global-vector
and stack allocation to MVS.

START allocates two independently backed BCPL vectors and initializes
their last elements to 17 and 25. It reads both values, emits 42, and
executes FINISH **without calling FREEVEC**.

Expected exact BCPL output: `42`.

Compared with test 029, this intentionally leaves the allocation list
nonempty at program exit. This exercises the new RELMEM traversal on a
two-element VECLIST instead of only its empty-list branch.

## What PASS establishes

A pass under TK5 demonstrates that the normal termination path can
return successfully with multiple outstanding vectors and preserved
BCPL output; it is not by itself proof that each FREEMAIN R executed
or that MVS reclaimed the exact amount of storage. The structural
source check should verify the RELMEM loop and the recorded allocation
length. Stronger reclamation evidence requires an independent
instrumented or observable test.

## Status

**PENDING TK5** — source-level preflight completed; no MVS execution
has yet been reported for regression 082.
