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

PASS.

Job 972 on 2026-10-06 assembled, link-edited, and executed successfully:

```text
ASM   RC=0000
LKED  RC=0000
GO    RC=0000
```

The native program emitted:

```text
42
```

The regression runner reported:

```text
=== Regression result ===
TEST:        05-variable-value-output
OBJECTIVE:   PASS
TERMINATION: NORMAL
RESULT:      PASS
```

This proves that an ordinary BCPL scalar value can be passed through the
normal first-argument convention to provisional DEBUGINT and rendered as
observable decimal text by the native runtime.


### Job 970 assembler diagnosis

The first native build stopped in IFOX with RC=0008 before link-edit or
execution.  Both flagged statements were IFO209 addressability errors.

The affected operands were late literal references in DEBUGINT:

```asm
CH    9,=H'1'
C     4,=F'132'
```

DEBUGINT is assembled after the startup base has been dropped and executes
under the SYSV/R11 base region.  The literal pool placed at END was not
addressable from that region.

The fix removes both literals and performs the comparisons through register
values loaded with LA.  Test 05's BCPL source remains unchanged.


### What Test 05 does not yet prove

Test 05 intentionally does not claim that the value of `X` was reloaded
from its workspace slot immediately before DEBUGINT.

The generated program stores the value 42 into the local workspace, but the
same value may still be live in the first argument register when DEBUGINT is
called.  Therefore Test 05 proves the scalar-to-diagnostic-output path, but
not mutable local-state readback.

Regression 06 is defined specifically to close that gap by assigning a new
value to a local, making an intervening call that consumes the first
argument register, and then reporting the local's value.
