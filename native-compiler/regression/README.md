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

### 09-vector-nonzero-subscript

Status: **PASS** — Job 982 emitted `42`; ASM/LKED/GO all RC=0000.

Creates a local `VEC 2`, stores 42 into `V!1`, then reloads that element
and passes it to DEBUGINT.

Generated S/370 inspection confirmed `ST 8,4(7,7)` and `L 7,4(7,7)`.
Compared with Test 08's zero-offset `0(7,7)`, the four-byte displacement
is exactly one 32-bit BCPL target word.

This establishes constant nonzero vector indexing for both store and load.

### 10-vector-variable-subscript

Status: **PASS** — Job 984 emitted `42`; ASM/LKED/GO all RC=0000.

Creates a local `VEC 2`, initializes local `I = 1`, stores 42 into
`V!I`, then reloads that element and passes it to DEBUGINT.

Generated S/370 inspection confirmed runtime index computation. The store
forms V+I in a register before converting the BCPL word address to a native
byte address; the later load independently reloads both I and V and performs
the same address calculation.

This establishes variable vector subscripting for both store and load.

### 11-vector-procedure-argument

Status: **PASS** — Job 986 emitted `42`; ASM/LKED/GO all RC=0000.

START creates a local `VEC 2`, stores 42 in `V!1`, reloads the BCPL word
pointer into R7, and calls SHOW. SHOW receives that pointer in R7 and
dereferences `V!1` before calling DEBUGINT.

Generated S/370 inspection confirms ordinary pointer argument passing and
callee-side vector dereference. This establishes cross-procedure visibility
of local vector storage without GETVEC, FREEVEC, BLIB, or heap allocation.

### 12-vector-callee-mutation

Status: **PASS** — Job 988 emitted `42`; ASM/LKED/GO all RC=0000.

Generated S/370 confirms that SETVALUE stores through the received R7 vector
pointer and that START independently reloads V and dereferences V!1 after the
call. This establishes write-through aliasing across the one-argument BCPL
procedure linkage.

START creates a local `VEC 2`, initializes `V!1` to 17, and passes
`V` to SETVALUE. The callee writes 42 through the received pointer.
After return, START reloads `V!1` and passes it to `DEBUGINT`.

Expected output:

```text
42
```

This extends Test 11 from callee-side read access to write-through aliasing.
Generated S/370 must show the callee store through the passed pointer and the
caller's independent post-return reload before Test 12 is considered fully
proven.

### 13-two-argument-linkage

Status: **PASS** — Job 990 emitted `42`; ASM/LKED/GO all RC=0000.

Generated S/370 confirms argument 1 in R7 and argument 2 in R8. The caller
loads V into R7 and I into R8 before BALR; the callee preserves through R8
and combines the two registers to compute V!I before storing 42.

START creates a local `VEC 2`, initializes `V!1` to 17, then calls
`SET(V,1)`. The callee uses both arguments to compute `V!I` and stores
42. START then reloads `V!1` and reports it through DEBUGINT.

Expected output:

```text
42
```

This extends the linkage evidence from one BCPL argument to two. Generated
S/370 must establish how arguments 1 and 2 are carried across the call and
show both participating in the callee-side vector store before Test 13 is
considered fully proven.

### 14-three-argument-linkage

Status: **PASS** — Job 992 emitted `42`; ASM/LKED/GO all RC=0000.

Generated S/370 confirms argument 1 in R7, argument 2 in R8, and argument 3
in R9. The caller loads V, I, and X into those registers before BALR; the
callee preserves through R9, uses R7/R8 to compute V!I, and stores R9 through
the resulting address.

START creates a local `VEC 2`, initializes `V!1` to 17, then calls
`SET(V,1,42)`. The callee uses V and I to compute the target element and
stores X through that address. START then reloads `V!1` and reports it
through DEBUGINT.

Expected output:

```text
42
```

This extends the linkage evidence from two BCPL arguments to three.
Generated S/370 must establish the register used for argument 3 and show all
three arguments participating in the callee operation before Test 14 is
considered fully proven.

### 15-four-argument-linkage

Status: **PASS** — Job 994 emitted `42`; ASM/LKED/GO all RC=0000.

Generated S/370 confirms argument 1 in R7, argument 2 in R8, argument 3 in
R9, and argument 4 in R10. The caller loads V, I, X, and Y into R7-R10
before BALR; the callee preserves through R10, computes X+Y in R10, uses
R7/R8 to compute V!I, and stores the result through the resulting address.

START creates a local `VEC 2`, initializes `V!1` to 17, then calls
`SET4(V,1,40,2)`. The callee uses V and I to compute the destination and
uses X+Y as the stored value. START then reloads `V!1` and reports it
through DEBUGINT.

Expected output:

```text
42
```

This extends the linkage evidence from three BCPL arguments to four.
Generated S/370 must establish the register used for argument 4 and show all
four arguments participating in the callee operation before Test 15 is
considered fully proven.
