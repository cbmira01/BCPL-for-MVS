# 28 - FREEVEC

This regression introduces native G!88 FREEVEC and exercises release of
storage previously obtained through G!87 GETVEC.

The program allocates one vector, uses it, frees it, allocates another vector,
uses that second allocation, frees it, and terminates normally.

Expected output:

```text
42
```

## Purpose

Test 27 proved the successful GETVEC allocation path and BCPL word-pointer
representation. Test 28 proves the matching release path through the VECLIST
bookkeeping introduced with GETVEC.

The native FREEVEC implementation:

- receives the BCPL word pointer in R7;
- walks VECLIST looking for a record whose VECBASE equals that pointer;
- unlinks the matching record;
- loads the recorded VECLEN;
- passes the original allocation base and length to MVS FREEMAIN;
- restores permanent generated-code registers and R15/W; and
- returns through the ordinary BCPL runtime linkage.

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler path;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show G!88 installed as the native FREEVEC entry;
- show generated BCPL calls to FREEVEC through the global vector;
- release the first GETVEC allocation without ABEND;
- permit a subsequent GETVEC allocation to return usable BCPL storage;
- release the second allocation without ABEND.

Source/listing inspection is part of the proof that FREEMAIN is actually
issued; the test does not require MVS to reuse the exact same address.

## Scope

This is the successful FREEVEC path only.

Unknown nonzero pointers are currently ignored by the WIP implementation and
GETVEC allocation failure remains unreconstructed. Those behaviors belong to
later edge/failure regressions.

## Status

PASS.

Job 1140 on 2026-10-07 compiled the BCPL test through the resident Cambridge
compiler path. Job 1141 then assembled, link-edited, and executed the native
program successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

This establishes executable evidence that G!88 FREEVEC can locate a matching
GETVEC allocation through VECLIST, unlink its control record, release the
recorded MVS allocation through FREEMAIN, and return normally to generated
BCPL code. A subsequent GETVEC allocation also returned usable storage and
was itself released successfully.

The test does not require exact address reuse and does not yet define error
behavior for invalid FREEVEC pointers.
