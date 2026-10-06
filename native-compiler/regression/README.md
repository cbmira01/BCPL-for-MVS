# Native compiler regression panel

This directory is the durable regression panel for the reconstructed native
System/370 BCPL compiler/runtime path.

The panel is driven by BCPL behavior.  Tests are deliberately ordered from the
smallest possible native BCPL program upward through progressively larger parts
of the compiler and BCPLMAIN contract.

The normal path under test is:

```text
BCPL source
  -> Cambridge SYN/LEX/TRN
  -> OCODE
  -> historical CG370
  -> System/370 assembler
  -> IFOX / linkage editor
  -> asm/bcplmain-wip.asm
  -> execution under MVS 3.8J
```

Assembler-only probes may diagnose a failing contract, but they are not panel
tests.

## Test layout

Each regression test has its own numbered directory:

```text
native-compiler/regression/
    README.md
    00-most-degenerate-bcpl-program/
        source.bcpl
        README.md
    01-...
    02-...
```

The numeric prefix is part of the test identity.  It records the intended
progression through the native execution contract.

Generated assembler, JCL, listings, load modules, and printer reports belong
under `workarea/`, not in the regression directories.

## Test design rule

A test should introduce as little new behavior as possible beyond all earlier
tests.  When a test fails, the difference between it and the preceding passing
tests should point toward a reasonably narrow compiler/runtime contract.

Tests should therefore be:

- BCPL source programs, not assembler ABI probes;
- small enough that generated S/370 code can be inspected directly;
- deterministic under MVS;
- retained permanently after they pass;
- ordered so that later tests build on contracts already established by
  earlier tests.

## Running one native regression test

With the TK5/Hercules container already running, invoke a numbered case from
the repository root with:

```sh
bash native-compiler/regression/run-test.sh 00
```

The runner compiles the case through the Cambridge compiler, recovers CG370
assembler, combines it with `asm/bcplmain-wip.asm` in `workarea/`, performs
assembler-source preflight, builds an IFOX/IEWL/GO job, submits it, and prints
the final job summary.  Generated artifacts remain under
`workarea/native-regression/<case>/`.

## Current panel

### 00-most-degenerate-bcpl-program

Status: **PASS** — first successful end-to-end native run, JES Job 948,
2026-10-06.

Establishes only the minimum native lifecycle:

```text
compiled module entry
  -> BCPLMAIN
  -> install G!1 = START
  -> enter START
  -> FINISH through R11
  -> normal MVS return
```

No procedure calls, locals, arithmetic, strings, library I/O, recursion, or
dynamic storage are involved.

### 01-one-procedure-call

Status: **PASS** — first successful end-to-end native run, JES Job 950,
2026-10-06.

Adds one ordinary BCPL procedure call and return.

This extends Test 00 by exercising:

- caller/callee workspace setup;
- R5/R15 workspace handling;
- R6 linkage;
- procedure return through the R11 return path.

It still avoids strings, arithmetic, recursion, global library calls, dynamic
storage, and stream I/O.

### 02-local-zero-test

Status: **PASS** — first successful end-to-end native run, JES Job 952,
2026-10-06.

Adds one local integer and one comparison with zero.

This extends the earlier tests by exercising:

- local workspace storage and reload;
- comparison against zero;
- condition-code and branch generation;
- the runtime invariant that R0 must remain zero while generated BCPL code
  executes.

It still avoids procedure arguments, recursion, strings, global library calls,
dynamic storage, and stream I/O.

## Test 00

`00-most-degenerate-bcpl-program` is intentionally almost empty.  Its only
job is to establish the minimum native BCPL lifecycle:

```text
compiled module entry
  -> BCPLMAIN
  -> global 1 / START
  -> FINISH
  -> normal MVS return
```

It should not depend on WRITEF, strings, arithmetic, procedure calls,
recursion, dynamic storage, stream I/O, or other library services.

The remaining tests should be chosen one at a time as the BCPLMAIN contract is
reconstructed.

### 03-single-character-output

Status: **PARTIAL** — G!14 WRCH emitted `A` in Job 954; termination ABENDs.

Introduces the first observable native output through `WRCH`.

This extends the earlier tests by exercising:

- installation of G!14 as `WRCH`;
- one ordinary global runtime call;
- passing one character argument;
- native character output through BCPLMAIN.

It deliberately avoids `WRITEF`, string formatting, recursion, dynamic
storage, and general stream-management machinery.

### 04-string-output

Status: **PASS** — Job 968 emitted `HELLO`; ASM/LKED/GO all RC=0000.

Traverses the BCPL string literal `"HELLO"` using the historical
`WRITES` shape expressed inline with G!85 `GETBYTE` and G!14 `WRCH`.

This adds:

- BCPL string-literal representation;
- count-byte interpretation;
- repeated GETBYTE access;
- FOR-loop control;
- repeated WRCH calls;
- visible multi-character output.

It deliberately does not introduce a machine-code `WRITES`.  Real WRITES
belongs to the BCPL library layer and should arrive through BLIB integration.

### 05-variable-value-output

Status: **PASS** — Job 972 emitted `42`; ASM/LKED/GO all RC=0000.

Assigns `X = 42` in BCPL and passes that scalar value to provisional G!150
`DEBUGINT`.

This is the first regression whose purpose is to publish a BCPL value through
the native diagnostic channel. Decimal conversion is kept out of the BCPL
test itself and no library WRITEN/WRITEF interface is claimed.

Test 05 does not by itself prove that X was reloaded from mutable local
storage immediately before the call; Test 06 is designed to establish that
separately.

### 06-mutable-local-readback

Status: **PASS** — Job 974 emitted `X42`; ASM/LKED/GO all RC=0000.

Initializes `X` to 17, mutates it to 42, calls `WRCH('X')` to consume the
normal first argument register, then calls `DEBUGINT(X)`.

Generated S/370 inspection confirmed an explicit `L 7,12(5)` after the
WRCH call and before the DEBUGINT call. The printed 42 is therefore a real
reload of mutable local workspace state rather than a value left live in R7.

This establishes mutable local assignment, persistence across an intervening
global call, workspace reload, and observable value reporting.

### 07-global-state-visibility

Status: **PASS** — Job 978 emitted `42`; ASM/LKED/GO all RC=0000.

START stores 42 into user global `X = G!151`, then calls a separate BCPL
procedure which reloads X and passes it to DEBUGINT.

Generated S/370 inspection confirmed:

```asm
ST 7,604(12)
...
L  7,604(12)
```

This establishes user global-vector state, persistence across an ordinary
BCPL procedure call, and cross-procedure visibility through R12/G.

The first run, Job 976, also revealed and motivated correction of the WIP
runtime's former G!0..G!150 static-capacity limit.

### 08-local-vector-store-load

Status: **PASS** — Job 980 emitted `42`; ASM/LKED/GO all RC=0000.

Creates a local `VEC 2`, stores 42 into `V!0`, then reloads that element
and passes it to DEBUGINT.

Generated S/370 proves the local-vector representation: the byte address
`16(R5)` is shifted right two bits to form the BCPL word pointer, and
`0(7,7)` after doubling R7 reconstructs four times that pointer for both
the fullword store and later load.

This establishes local vector allocation, BCPL word-pointer representation,
and `!0` word store/load without GETVEC, FREEVEC, BLIB, or heap allocation.
