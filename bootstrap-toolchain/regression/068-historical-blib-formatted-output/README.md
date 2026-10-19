# 068 — Historical BLIB formatted-output smoke test

## Objective

Exercise four exported services from the **complete historical BLIB**,
not copied procedure fragments: `WRITEX` (G!74), `WRITEOCT`
(G!77), `NEWLINE` (G!63), and `WRITEF` (G!76).

The source unit is regenerated from the untouched
`richards-bcpltape/bcplib/bcpl/blib` by
`native-compiler/bootstrap-cambridge/make-demoted.py --blib-only`
into `workarea/bootstrap-cambridge/demoted/blib`.
The marker `library-source.txt` selects it using the same mechanism
as regressions 065–067. No BLIB, BCPLMAIN, or CG370 changes are made.

## Historical calling contracts

The original BLIB defines:

- `WRITEX(N)` as `WRITEHEX(N, 8)`, rendering eight hexadecimal digits.
- `WRITEOCT(N, D)` as `D` octal digits, including leading zeros.
- `NEWLINE()` as `WRCH('*N')`.
- `WRITEF(FORMAT, ...)` as a format scanner with `%N` invoking
  `WRITED` with default width zero.

We use 42 to make decimal, hexadecimal, and octal representations
easy to verify independently. Simpler services precede the format
parser, so a `WRITEF` runtime fault does not obscure their execution.

## Expected output

```text
HEX 0000002A
OCT 052
FORMAT 42
DONE
```

The generated-code assertions check dynamic global-vector references
at offsets 296, 308, 304, and 252. All four services must be
dispatched through the shared BLIB's exports.

The current regression combiner statically joins separately
compiled BCPL units at the assembler level. This test does not
establish independently loadable native BCPL sections.

## Status

**PASS** — native MVS regression on 2026-10-08; exact output `HEX 0000002A`, `OCT 052`, `FORMAT 42`, and `DONE` on separate records (1 PASS, 0 FAIL).
