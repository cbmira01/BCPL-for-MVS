# 27 - GETVEC

This regression introduces the first native dynamic-storage allocation through
G!87 GETVEC.

The program is deliberately small:

```bcpl
GLOBAL $( START:1; GETVEC:87; DEBUGINT:150 $)

LET START () BE
$(1
    LET V = GETVEC(2)

    V!0 := 17
    V!2 := 42

    DEBUGINT(V!2)
    FINISH
$)1
```

Expected output:

```text
42
```

## Purpose

Earlier vector regressions used local workspace vectors only. Test 27 moves
vector storage outside the BCPL stack/workspace and into storage obtained
dynamically by BCPLMAIN.

The test deliberately accesses V!2 after GETVEC(2). This reflects the BCPL
`VEC N` convention that the vector has elements 0 through N, so GETVEC(N)
must provide N+1 payload words.

## WIP allocator shape

The first native GETVEC implementation follows the shape suggested by the
surviving BCPLMAC VECAREA definitions. Each MVS allocation begins with a
three-word private record:

```text
+0   VECBASE   returned BCPL word pointer
+4   VECLEN    bytes obtained from MVS
+8   VECNEXT   next allocation record
+12  payload   N+1 BCPL words
```

BCPLMAIN keeps a VECLIST head so FREEVEC and exit cleanup can be added without
replacing the GETVEC representation.

## Acceptance criteria

A successful run must:

- compile through the resident Cambridge compiler path;
- assemble and link with no errors;
- terminate normally under MVS;
- emit exactly `42`;
- show G!87 installed as the native GETVEC entry;
- show the generated call loading GETVEC through the global vector;
- return a BCPL word pointer in R7;
- allow stores and loads through that returned pointer, including V!2.

## Scope

This is the GETVEC success path only.

The first WIP implementation uses unconditional MVS GETMAIN. Allocation
failure semantics are intentionally deferred to the later edge/failure test.
FREEVEC is also deferred to Test 28.

## Status

PASS.

Job 1138 on 2026-10-07 compiled the BCPL test through the resident Cambridge
compiler path. Job 1139 then assembled, link-edited, and executed the native
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

This establishes executable evidence that G!87 GETVEC can obtain MVS-backed
storage, return it as a BCPL word pointer, and support ordinary generated
vector indexing through the returned address, including the upper element
V!2 from GETVEC(2).

The test covers only the successful allocation path. FREEVEC, exact release
semantics, repeated allocation behavior, exit cleanup, and allocation-failure
behavior remain separate regressions.
