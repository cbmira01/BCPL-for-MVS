# 066 — WRITEN from complete historical Cambridge BLIB

## Objective

Exercise the `WRITEN` (G!62) service and its historical `WRITED`
(G!68) dependency from the **complete demoted historical BLIB** already
validated as a whole by regression 067. This regression carries no
copies of historical BLIB procedure bodies. `library-source.txt`
selects the generator-produced
`workarea/bootstrap-cambridge/demoted/blib`.

The application calls `WRITEN(42)`, `WRITEN(-17)`, and `WRITEN(0)`,
separated by a space written with native `WRCH` (G!14). A space is
used instead of the original vertical bar due to the output transport
anomaly observed in the first 067 run. This does not change BLIB.

Expected native output:

```text
42 -17 0
```

The generated-code assertions verify a G!62 call (offset 248) through
`BALR 6,4`. A passing run establishes decimal formatting for these
three values through complete BLIB, not merely an extracted procedure.

The generated library is statically combined at the assembler level.
Independently loadable BCPL library modules are not yet implemented.

## Status

**PENDING** — native MVS regression not yet run against complete BLIB.
