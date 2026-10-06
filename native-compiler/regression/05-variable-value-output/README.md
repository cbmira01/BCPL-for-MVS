# 05 - Output a variable value

This regression introduces the first explicit native diagnostic service for
publishing BCPL program state.

The BCPL program is deliberately minimal:

```bcpl
LET X = 42
DEBUGINT(X)
```

Expected output:

```text
42
```

## Purpose

Test 05 is intended to prove only the path from an ordinary BCPL variable to
observable diagnostic output:

```text
BCPL local variable
    -> ordinary BCPL argument passing
    -> provisional DEBUGINT runtime primitive
    -> decimal text in SYSPRINT
```

The test deliberately contains no BCPL decimal-conversion arithmetic,
library WRITEN, library WRITEF, vector manipulation, or formatting language.

## DEBUGINT

For bootstrap diagnostics, BCPLMAIN provisionally installs DEBUGINT at
G!150. The current historical global map identifies 150 as the first free
global boundary, so this hook is deliberately outside the recovered library
assignments used so far.

DEBUGINT is not a claim about the historical BCPL interface. It is an
instrumentation service for reconstruction work and must not be confused
with WRITEN or WRITEF, both of which belong to the BCPL library layer.

The machine routine accepts the ordinary first BCPL argument in R7 and emits
a signed decimal representation through the already proven buffered
SYSPRINT diagnostic path.

## Status

DEFINED. Not yet run.
