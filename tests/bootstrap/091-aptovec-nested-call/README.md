# 091 — APTOVEC temporary stack vector and nested call

Status: **PENDING TK5**.

The test passes a compiled BCPL function address and N=3 to G!40
APTOVEC. The function checks that it receives N, stores at V!0 and
V!N, and returns their sum. The caller prints 42.

This tests the minimum APTOVEC contract: temporary stack vector
containing N+1 words, two-argument nested BCPL linkage, preservation
of the caller frame, and function result propagation.

It does not yet prove negative/huge argument behavior, reentrancy,
deeply nested frames, precise historical stack-clearance policy, or
full native compiler workspace viability.

Acceptance: BCPL output 42, assembler/link-edit/GO success,
then complete native regression panel 000..091.
