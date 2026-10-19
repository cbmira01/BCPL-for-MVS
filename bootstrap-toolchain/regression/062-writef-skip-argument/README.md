# 062 - WRITEF skip argument

Historical System/370 BLIB WRITEF contains
`CASE '$': T := T + 1; ENDCASE`. This skips a formatting argument
without writing any output.

## Source

```bcpl
WRITEF("A%$%NB", 13, 42)
```

Expected output:

```text
A42B
```

## Acceptance criteria

- Compile the source literal through resident Cambridge.
- Pass 13 and 42 as formatting arguments.
- Call G!76 at displacement 304.
- Skip the first argument for `%$` without output.
- Print the second argument through `%N` and terminate normally.
- Preserve the prior 000–061 regression contracts.

Evidence: `richards-bcpltape/bcplib/bcpl/blib`.
The native WRITEF remains a provisional BCPLMAIN bootstrap service.

## Status

**PASS** — native MVS regression on 2026-10-08; emitted `A42B` (1 PASS, 0 FAIL).
