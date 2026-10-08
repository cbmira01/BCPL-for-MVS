# 065 — Native execution of historical Cambridge BLIB WRITES

## Objective

Compile an independent BCPL library module containing the unchanged
`WRITES` procedure body from
`richards-bcpltape/bcplib/bcpl/blib` and execute it natively.

The historical body is:

```bcpl
LET WRITES(S) BE
       FOR I = 1 TO GETBYTE(S,0) DO WRCH(GETBYTE(S,I))
```

Only the surrounding global declarations differ from the source, to
make the dependencies explicit without requiring source preprocessing
of `GET "LIBHDR"`. The global numbers come directly from
`richards-bcpltape/sys3/bcpl/libhdr`:

- G!60 WRITES — defined by this library module.
- G!14 WRCH — existing BCPLMAIN native primitive.
- G!85 GETBYTE — existing BCPLMAIN native primitive.
- G!1 START — defined in the application module.

The test application calls `WRITES("HELLO")`; expected output
is `HELLO`. The caller should load G!60 at displacement 240
and call it using `BALR 6,4`.

## Execution boundary

The existing Test 25 static combiner joins two separately compiled
Cambridge units and merges exported globals. This is test
scaffolding and **does not** claim the MVS native multi-section
loader is finished. No assembler runtime changes are required.

## Status

**PASS** — native MVS execution on 2026-10-08; output `HELLO` (1 PASS, 0 FAIL).
