# 38 - PUTBYTE / GETBYTE round-trip

This regression introduces the native PUTBYTE machine primitive and verifies it
by reading the same byte back through the already-proven GETBYTE primitive.

Expected output:

```text
42
```

## Sequence

START creates a local vector, then executes:

```bcpl
PUTBYTE(V,3,42)
DEBUGINT(GETBYTE(V,3))
```

The byte written at offset 3 from the BCPL word pointer V must be read back as
42.

## Contract under test

Earlier regressions established:

- local vector representation;
- BCPL word-pointer addressing;
- three-argument linkage in R7/R8/R9;
- GETBYTE;
- DEBUGINT.

Test 38 adds only the PUTBYTE store path.

The native primitive must:

- convert the BCPL word pointer in R7 to a byte address;
- add the byte offset in R8;
- store the low eight bits of R9 with STC;
- preserve the permanent/runtime register contract required by generated code;
- return normally through the ordinary machine-primitive linkage.

GETBYTE must then recover the same byte from the same effective address.

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler and historical CG370;
- assemble, link-edit, and execute normally under MVS;
- emit exactly `42`;
- show the generated call to PUTBYTE through G!86;
- show the generated call to GETBYTE through G!85; and
- confirm by generated/runtime code inspection that the byte store and reload
  use the expected BCPL word-pointer-to-byte-address conversion.

## Scope

This test adds no new allocator, loader, stream, or language feature. It is a
focused machine-primitive regression.

## Status

PENDING — ready for first native run.
