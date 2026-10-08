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

The numeric prefix is part of the test identity. It records the intended
progression through the native execution contract.

Numbering has one deliberate historical width break:

```text
00..52   existing two-digit test identities, retained unchanged
053..999 three-digit identities for all new tests
```

The command-line runners accept natural decimal integers and normalize them
internally. Thus `tools/run-native-regression 53` resolves `053-*`, while
`tools/run-native-regression 7` continues to resolve `07-*`. Existing tests
must not be renamed merely to make their prefixes three digits.

Each numbered test owns its executable output contract in `expected.txt`.
An empty `expected.txt` means that the test has no BCPL output assertion.
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

## Running the native regression panel

With the resident Cambridge compiler installed on MVS, the canonical full-panel
command is:

```sh
tools/run-native-regression
```

With no arguments, this discovers the highest numbered test and runs every
contiguous case from 00 through that test.  One number runs one test; two
numbers run an inclusive range:

```sh
tools/run-native-regression 30
tools/run-native-regression 27 30
```

The runner continues after individual failures, records each test's complete
output under `workarea/native-regression/logs/`, prints a compact PASS/FAIL
summary, and returns nonzero if any test fails. A numbering gap inside the
requested range is treated as an error rather than silently skipped. Add
`--show-output` to display each test's BCPL output; on an output mismatch the
runner also exposes the saved native job report for diagnosis.

The numbering boundary itself can be checked without MVS:

```sh
tools/run-native-regression --check-numbering
```

That verifies representative directory IDs and the compact MVS job/entry names
through test 999.

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

## Full-panel verification

On 2026-10-07 the entire 00-47 panel was rerun after hardening output matching.
Tests 00-46 all passed. The original Test 47 swap probe correctly failed under
the hardened matcher; subsequent standards/source review showed that its
simultaneous-swap expectation was stronger than historical BCPL guarantees.
The revised order-independent Test 47 then passed, giving a clean 48/48 panel.

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

### 16-function-return-value

Status: **PASS** — Job 996 emitted `42`; ASM/LKED/GO all RC=0000.

Generated S/370 confirms that ADD receives A/B in R7/R8, computes the sum,
moves the function result into R7 with `LR 7,8`, and returns. The caller
immediately consumes the returned R7 value after BALR.

Calls `ADD(17,25)`, stores the returned value in a local, and passes that
value to `DEBUGINT`.

Expected output:

```text
42
```

This establishes the function-result side of the native BCPL calling
convention. Generated S/370 must show ADD returning its result in the
caller-visible result register and START consuming that returned value before
Test 16 is considered fully proven.

### 17-nested-calls

Status: **PASS** — Job 998 emitted `42`; ASM/LKED/GO all RC=0000.

Generated S/370 confirms that DOUBLE establishes its own workspace, prepares
a nested call to ADD with a new W at `16(R5)`, receives ADD's R7 result,
and returns that same result to START through the ordinary BCPL return path.

START calls `DOUBLE(21)`; DOUBLE calls `ADD(X,X)`; ADD returns 42;
DOUBLE propagates that result; START passes the final value to DEBUGINT.

Expected output:

```text
42
```

This extends Test 16 from one ordinary function call to nested generated
calls. Generated S/370 must show DOUBLE creating its own call frame,
invoking ADD, receiving the R7 result, and returning that result to START
before Test 17 is considered fully proven.

### 18-recursion

Status: **PASS** — Job 1000 emitted `42`; ASM/LKED/GO all RC=0000.

Generated S/370 confirms genuine non-tail recursion: DEPTH advances W to
`16(R5)`, recursively calls itself, then adds one to the returned R7 value
before returning. This proves repeated frame creation and unwind through the
ordinary BCPL linkage.

Calls non-tail-recursive `DEPTH(5)`. The base case returns 37 and each
recursive caller adds one after the nested call, producing 42 after five
levels unwind.

Expected output:

```text
42
```

This extends Test 17 from fixed nested calls to repeated recursive calls to
the same generated function. Generated S/370 must show recursive call-frame
creation plus post-return result processing before Test 18 is considered
fully proven.

### 19-local-scalars-across-call

Status: **PASS** — Job 1002 emitted `42`; ASM/LKED/GO all RC=0000.

Generated S/370 confirms that A, B, and C are spilled to the caller workspace
before ID is called, then reloaded after return and combined with the R7
function result. This establishes caller-local scalar preservation across an
ordinary call.

START establishes three scalar locals, calls `ID(3)`, then uses all three
pre-call locals plus the returned value after the call to compute 42.

Expected output:

```text
42
```

This extends the linkage regressions by proving caller-local scalar lifetime
across an ordinary function call. Generated S/370 must show how the pre-call
locals remain available after ID returns before Test 19 is considered fully
proven.

### 20-pointer-return

Status: **PASS** — Job 1004 emitted `42`; ASM/LKED/GO all RC=0000.

Generated S/370 confirms that IDPTR receives V in R7 and returns the same
BCPL word pointer in R7. START stores the returned pointer in local P and
then dereferences P!1 successfully.

START creates a local vector, stores 42 in `V!1`, calls `IDPTR(V)`,
stores the returned pointer in P, then dereferences `P!1` and reports the
value through DEBUGINT.

Expected output:

```text
42
```

This extends the function-result evidence from scalar values to BCPL pointer
values. Generated S/370 must show the pointer returning through the ordinary
result convention and being dereferenced by the caller before Test 20 is
considered fully proven.

### 21-pointer-store-reload

Status: **PASS** — Jobs 1006 and 1008 both emitted `42`; ASM/LKED/GO all
RC=0000.

Generated S/370 confirms that pointer V is stored as a fullword into W!0,
reloaded from W!0, saved as local P, and then dereferenced successfully.
This establishes pointer identity across an ordinary store/load round trip.

START creates vectors V and W, stores 42 in `V!1`, stores pointer V into
`W!0`, reloads that pointer into P, then dereferences `P!1` and reports
the value through DEBUGINT.

Expected output:

```text
42
```

This proves that a BCPL word pointer survives a fullword store/load round
trip as ordinary data. Generated S/370 must show the pointer store into W,
reload from W, and later dereference before Test 21 is considered fully
proven.

### 22-signed-arithmetic

Status: **PASS** — Job 1010 emitted `42`; ASM/LKED/GO all RC=0000.

Generated S/370 confirms runtime signed negation with `LCR 7,7` and
subsequent subtraction with `SR 8,7`, producing 25-(-17)=42.

START establishes A=17 and B=25, negates A at runtime, then computes
`B-A`. Since A becomes -17, the expected result is 42.

Expected output:

```text
42
```

This isolates signed unary negation and arithmetic involving a negative
operand while keeping the final DEBUGINT value positive. Generated S/370
must show actual runtime negation and subsequent arithmetic before Test 22
is considered fully proven.

### 23-control-flow

Status: **PASS** — Job 1012 emitted `42`; ASM/LKED/GO all RC=0000.

Generated S/370 confirms the targeted conditional, loop, BREAK/LOOP, and
SWITCHON/CASE/DEFAULT/ENDCASE forms using ordinary compare-and-branch
sequences. No new BCPLMAIN service is required.

Exercises IF, UNLESS, TEST/THEN/ELSE, WHILE, UNTIL, FOR, REPEAT,
REPEATWHILE, REPEATUNTIL, BREAK, LOOP, and SWITCHON/CASE/DEFAULT/ENDCASE
in one accumulator-based program.

Expected output:

```text
42
```

Incorrect ELSE or DEFAULT selection deliberately drives the accumulator to
999. Generated S/370 must be inspected across the individual branch and loop
constructs before Test 23 is considered fully proven.

### 24-callable-global-through-g

Status: **PASS** — Job 1014 emitted `42`; ASM/LKED/GO all RC=0000.

Generated S/370 confirms that START loads ADD from G!151 with
`L 4,604(12)` and calls it with `BALR 6,4`. The module trailer exports
ADD at the corresponding global-vector displacement, proving callable user
globals through R12/G.

Declares user function `ADD` as global 151, calls `ADD(17,25)` from
START, and reports the returned value through DEBUGINT.

Expected output:

```text
42
```

This exercises callable user globals through R12/G. Generated S/370 must
show ADD exported as G!151 and START loading its callable address from
`604(R12)` before Test 24 is considered fully proven.

### 25-separately-compiled-bcpl-library

Status: **PASS** — Jobs 1133/1134 compiled the application and library
separately; Job 1135 assembled, link-edited, and executed the combined native
result successfully on 2026-10-07, emitting `42`.

Compiles the application and a tiny ADD library as two independent BCPL
compilation units. The application declares ADD as G!151 but does not define
it; the library defines and exports ADD as G!151.

Because the current WIP BCPLMAIN only scans the trailer of the one generated
module that enters it, the regression runner uses a deliberately temporary
static combiner after both Cambridge compilations. The combiner renames the
library's generated local labels, incorporates its generated code, and merges
its exported-global trailer pair into the application module trailer.

Expected output:

```text
42
```

This test is intended to establish:

- separate BCPL compilation of application and library source;
- preservation of generated BCPL calling conventions across that boundary;
- installation of the library-generated ADD address into G!151;
- application lookup of ADD through `604(R12)`;
- invocation through the ordinary global-call `BALR` path; and
- return of the library function result through R7.

It does **not** claim that native LOAD/UNLOAD or unchanged independently
linked BCPL sections work yet. Removing the static-combiner accommodation is
a later loader/linkage milestone.

### 26-separately-assembled-native-through-g

Status: **PASS** — Job 1136 compiled the BCPL application; Job 1137 assembled
the BCPL/runtime source and native routine separately, linked them with IEWL,
and executed successfully on 2026-10-07, emitting `42`.

Compiles a BCPL application that declares NATIVEADD as G!151 but provides no
BCPL definition. Regression scaffolding extends the generated trailer with an
external `NATIVEAD` address. The BCPL/runtime source and `native.asm` are
then assembled in separate IFOX steps, and IEWL resolves NATIVEAD across the
two object decks.

Expected output:

```text
42
```

This test is intended to establish:

- an application-written native routine can be linked separately from the
  generated BCPL module;
- G!151 can contain the linkage-editor-resolved native entry address;
- generated BCPL can call that native routine through R12/G;
- R7/R8 argument passing survives the BCPL-to-assembler boundary; and
- a native routine can return a function result in R7 through the ordinary
  BCPL system-vector return trampoline.

The generated-trailer augmentation remains regression scaffolding; this test
does not yet define the final mixed-language programmer interface.

### 27-getvec

Status: **PASS** — Job 1138 compiled the BCPL test; Job 1139 assembled,
link-edited, and executed successfully on 2026-10-07, emitting `42`.

Introduces native G!87 GETVEC and the first MVS-backed dynamic vector. The
test calls `GETVEC(2)`, writes both V!0 and V!2, and reports V!2 through
DEBUGINT.

Expected output:

```text
42
```

The WIP GETVEC obtains N+1 BCPL payload words and prefixes the MVS allocation
with a three-word control record modeled on the surviving BCPLMAC VECAREA
fields: VECBASE, VECLEN, and VECNEXT. BCPLMAIN retains a VECLIST head for the
following FREEVEC and cleanup regressions.

This first rung uses unconditional MVS GETMAIN. It proves only successful
allocation and BCPL word-pointer use; allocation failure semantics are
deliberately deferred.

### 28-freevec

Status: **PASS** — Job 1140 compiled the BCPL test; Job 1141 assembled,
link-edited, and executed successfully on 2026-10-07, emitting `42`.

Introduces native G!88 FREEVEC using the VECLIST records established by
GETVEC. The test allocates and uses one vector, releases it, allocates and
uses a second vector, releases that one, and terminates normally.

Expected output:

```text
42
```

FREEVEC matches the incoming BCPL word pointer against VECBASE, unlinks the
matching record from VECLIST, and issues MVS FREEMAIN with the recorded
allocation base and byte length. The regression does not require exact address
reuse; source/listing inspection establishes that FREEMAIN is actually issued.

Invalid-pointer behavior and allocation-failure behavior remain deferred edge
cases.

### 29-multiple-allocations

Status: **PASS** — Job 1142 compiled the BCPL test; Job 1143 assembled,
link-edited, and executed successfully on 2026-10-07, emitting `424242`.

Exercises several simultaneously live GETVEC allocations and deliberately
removes VECLIST records from the middle, head, and tail positions. Surviving
vectors are read after each release operation.

Expected output:

```text
424242
```

The list sequence is intentionally:

```text
C -> B -> A
C -> A
D -> C -> A
C -> A
C
empty
```

This test should require no BCPLMAIN change if the Test 28 FREEVEC list logic
is correct. Exact MVS address reuse is not tested.

### 30-getvec-failure

Status: **PASS** — Job 1150 compiled the BCPL test; Job 1151 assembled,
link-edited, and executed successfully on 2026-10-07, emitting `4242`.

Changes GETVEC from unconditional GETMAIN to conditional GETMAIN EC and
establishes failure-to-zero behavior. The test first proves that a normal
small allocation still works, then requests an almost-16-MiB vector that
cannot fit in the running 24-bit MVS address space.

Expected output:

```text
4242
```

The first 42 proves the successful allocation path still works. The second
42 is emitted only if the large GETVEC returns zero rather than ABENDing.
An unexpected successful allocation emits 99.

GETVEC also rejects negative or overlarge N values before computing the byte
length, keeping the WIP allocation length within the 24-bit runtime model.

### 31-dynamic-vector-across-calls

Status: **PASS** — validated in the full 00..32 panel on 2026-10-07.

Composes the dynamic allocation contract from Tests 27-30 with the pointer
aliasing and one-argument procedure linkage established earlier.

START obtains `V = GETVEC(2)`, initializes `V!1` to 17, passes V to
SETVALUE, and the callee stores 42 through the received pointer. START then
reloads `V!1`, reports it through DEBUGINT, and releases the same vector with
FREEVEC.

Expected output:

```text
42
```

An unexpected allocation failure emits 99. No BCPLMAIN change should be
required; this is deliberately a composition/stability test rather than a new
runtime feature.

### 32-dynamic-pointer-return

Status: **PASS** — emitted `42`; after the RETIMPL correction the complete
00..32 native panel passed 33/33 on 2026-10-07.

MAKE is now deliberately only `GETVEC(2)` returned as the function result.
START stores the returned pointer in P, writes 42 to `P!1`, reloads and
reports it. Test 32 deliberately does not call FREEVEC.

Expected output:

```text
42
```

The first version also used `VALOF/RESULTIS` and callee-side vector access,
introducing more than one unproven construct. Its native run compiled,
assembled, and linked successfully but ABENDed S0C4 inside generated MAKE.
Those semantics have been removed from Test 32 and should be isolated in a
later regression. The narrowed test exposed a reconstruction error in the
system-vector procedure-return trampoline: R4 must be reloaded from the restored
caller frame, not from the callee frame. A later FREEVEC-specific regression may
also make successful MVS storage release more directly observable.

### 33-caller-base-after-function-return

Status: **PASS** — emitted `42` on 2026-10-07.

Calls a trivial function returning 17, then immediately performs caller-side
conditional control flow and emits 42 on the correct path or 99 on failure.

This is a foundation regression for the corrected procedure-return trampoline.
Its purpose is to distinguish restoration of R4 from the callee frame from the
required restoration of R4 from the restored caller frame. On the first run,
the generated S/370 must be inspected to confirm that the post-call TEST uses an
R4-relative branch; otherwise the source should be reshaped before the test is
considered established.

Expected output:

```text
42
```

### 34-valof-resultis

Status: **PASS** — emitted `42` on 2026-10-07.

Introduces the minimal `VALOF ... RESULTIS ...` expression form. START assigns
the value of a VALOF block containing only `RESULTIS 42` to a local, reports
that local through DEBUGINT, and terminates normally.

Expected output:

```text
42
```

This test isolates only the basic VALOF/RESULTIS result-continuation contract.
Conditional and nested RESULTIS cases are deliberately deferred.

### 35-conditional-resultis

Status: **PASS** — emitted `42` on 2026-10-07.

Extends Test 34 from one RESULTIS path to two distinct control-flow paths that
both exit the same VALOF expression.

Expected output:

```text
42
```

The generated S/370 should show the true and false RESULTIS paths converging on
the same VALOF continuation while preserving the selected value in the ordinary
expression/result register.

### 36-nested-valof-resultis

Status: **PASS** — emitted `42` on 2026-10-07.

Extends the VALOF/RESULTIS regressions to nested continuations. The inner
RESULTIS must exit only the inner VALOF and yield 17; execution then resumes in
the outer VALOF, whose RESULTIS yields 42.

Expected output:

```text
42
```

The generated S/370 should show two distinct continuation labels: one for the
inner VALOF and one for the outer VALOF.

### 37-multiple-exported-globals

Status: **PASS** — emitted `42` on 2026-10-07.

Defines and exports three user functions in one generated module:

```text
LEFT  -> G!151
RIGHT -> G!152
ADD   -> G!153
```

START calls all three through R12/G and reports 42.

Expected output:

```text
42
```

The first successful run should be inspected to verify that the generated
trailer contains all user-global export pairs plus START, and that START loads
the three callable addresses from G at byte displacements 604, 608, and 612.

### 38-putbyte-getbyte-roundtrip

Status: **PASS** — emitted `42` on 2026-10-07.

Introduces native G!86 PUTBYTE and verifies the stored byte by reading the same
location through already-proven G!85 GETBYTE.

Expected output:

```text
42
```

This isolates the machine-dependent byte-store path, including BCPL word-pointer
to byte-address conversion, byte-offset arithmetic, and three-argument linkage.

### 39-freevec-storage-release

Status: **PASS** — emitted `42` on 2026-10-07.

Repeatedly allocates exact 1 KiB GETVEC blocks until allocation fails, frees one
known live block, then immediately retries the same 1 KiB allocation.

Expected output:

```text
42
```

Output 42 is possible only if at least one allocation succeeded, exhaustion was
reached, FREEVEC released one live extent, and the same-sized GETVEC then
succeeded. This strengthens Tests 28/29 by making successful storage release
behaviorally observable.

### 40-static-scalar-persistence

Status: **PASS** — emitted `42` on 2026-10-07.

Declares a STATIC scalar initialized to 17, updates it from a separate procedure,
then reads it from START.

Expected output:

```text
42
```

This isolates persistent module static storage and generated addressing. The
Cambridge compiler master and historical CG370 both use STATIC declarations, so
this is direct corpus-driven coverage.

### 41-table-constant-vector

Status: **PASS** — emitted `42` on 2026-10-07.

Uses `TABLE 17,25` and emits `T!0 + T!1` through DEBUGINT.

Expected output:

```text
42
```

This isolates TABLE representation and module-relative addressing. TABLE is used
directly by the Cambridge compiler master, TRN, and CG370, and is defined in the
historical BCPL language documentation.

### 42-manifest-constant-expression

Status: **PASS** — emitted `42` on 2026-10-07.

Declares `LEFT=17`, `RIGHT=25`, and `ANSWER=LEFT+RIGHT` in a MANIFEST block,
then emits ANSWER through DEBUGINT.

Expected output:

```text
42
```

This isolates compile-time MANIFEST binding and constant-expression folding. The
Cambridge compiler corpus uses MANIFEST directly, and TRN contains explicit
MANIFEST translation paths.

### 43-label-goto

Status: **PASS** — emitted `42` on 2026-10-07.

Initializes `X=17`, executes `GOTO ADD25`, places an unreachable `X := 99`
between the GOTO and label, then adds 25 and emits the result.

Expected output:

```text
42
```

This isolates explicit label/GOTO generation. The Cambridge compiler corpus uses
GOTO heavily, especially in SYN/LEX and CG370.

### 44-address-indirection

Status: **PASS** — emitted `42` on 2026-10-07.

Forms `P=@X`, updates X through `!P`, then reads X directly.

Expected output:

```text
42
```

This isolates BCPL address-of and monadic indirection while reusing already
proven local-scalar, arithmetic, and DEBUGINT behavior.

### 45-shifts-bitwise

Status: **PASS** — emitted `42` on 2026-10-07.

Exercises left shift, right shift, OR, AND, EQV, and NEQV in one compact
expression chain and emits the resulting value.

Expected output:

```text
42
```

This is both corpus-driven and documentation-driven coverage of core BCPL
bitwise and shift operators.

### 46-multiply-divide-rem

Status: **PASS** — emitted `42` on 2026-10-07.

Exercises multiplication, integer division, and remainder with small positive
operands and combines the results to emit 42.

Expected output:

```text
42
```

This isolates the core arithmetic operators without adding runtime dependencies
or sign/overflow edge cases.

### 47-multiple-assignment

Status: **PASS** — revised order-independent probe emitted `422517` on 2026-10-07.

Assigns two locals with `A,B := 25,17` and emits their sum plus both values.

Expected output:

```text
422517
```

The three DEBUGINT calls share the current buffered output record. The original `A,B := B,A` swap probe was invalid as a conformance test:
historical BCPL explicitly leaves multiple-assignment evaluation/assignment
order undefined. Cambridge's observed left-to-right lowering is permitted.

### 48-stack-check-emission

Status: **PASS** — compile-only generated-code contract probe, 2026-10-07.

Reuses the minimal Test 00 source but supplies a private Cambridge bootstrap
parameter record beginning `/CN`. The second-phase `C` enables CG370 stack
checking; `N` preserves the bootstrap requirement that suppresses binary
object-deck output.

Acceptance requires the recovered System/370 assembler to contain the
contiguous checked-entry sequence:

```asm
BAL   14,60(11)
DC    A(Lnnn) STACK FRAME SIZE
```

Observed minimal generated entry:

```asm
STM 4,6,0(15)
BAL 14,60(11)
DC A(L994) STACK FRAME SIZE
BC 15,40(11)
L994 EQU 12 STACK FRAME SIZE
```

This establishes a 12-byte minimal frame and confirms that checked entry replaces
the ordinary `LR 5,15` operation. The regression deliberately stops after
generated-code assertions because BCPLMAIN's current stack-check entry is still
a stub. Runtime semantics begin with the next regression.

### 49-checked-procedure-entry

Status: **PASS** — emitted `X42` under checked entry on 2026-10-07.

Runs the already-proven mutable-local/WRCH/reload shape under code-generator
option `C`. The generated code must contain the checked-entry BAL and inline
frame-size word, and the native run must emit:

```text
X42
```

BCPLMAIN's `STKIMPL` now performs only the minimum entry mechanics:

```asm
LR    5,15
LA    14,4(14)
BR    14
```

Observed generated frame size was 44 bytes:

```asm
BAL 14,60(11)
DC A(L994) STACK FRAME SIZE
...
L994 EQU 44 STACK FRAME SIZE
```

No stack-limit comparison is claimed yet. The successful `X42` run isolates
correct workspace establishment and resumption after the inline frame-size
fullword.

### 50-stack-frame-size

Status: **PASS** — emitted `42` with a 172-byte checked frame on 2026-10-07.

Uses a local `VEC 31` so CG370 must publish a substantially larger frame than
Test 49's 44-byte case. Generated-code assertions require both the checked-entry
BAL/inline fullword and a three-digit-or-larger `STACK FRAME SIZE` EQU.

BCPLMAIN now loads the inline frame size from `0(R14)`, verifies that it is
positive and word aligned, restores R4 from the just-saved workspace, skips the
inline word, and resumes generated code.

Observed generated frame:

```asm
BAL 14,60(11)
DC A(L994) STACK FRAME SIZE
...
L994 EQU 172 STACK FRAME SIZE
```

The native run emitted:

```text
42
```

This proves the inline frame-size word was decoded and structurally accepted.
The runtime still does **not** compare the required frame against WORKEND, so
stack-overflow detection is not yet claimed.

### 51-checked-recursion

Status: **PASS** — emitted `42` through five checked recursive levels on 2026-10-07.

Reuses the proven Test 18 non-tail-recursive DEPTH(5) shape, but compiles with
second-phase Cambridge option `C`. Generated-code assertions require at least
two checked-entry BAL/inline-frame sequences plus ordinary W advancement and
`BALR 6,4` linkage.

The expected native result remains:

```text
42
```

Observed recursive entry and call sequence:

```asm
STM 4,7,0(15)
BAL 14,60(11)
DC A(L994) STACK FRAME SIZE
...
LA 15,16(5)
L  4,0+L2-L1(4)
BALR 6,4
...
L994 EQU 44 STACK FRAME SIZE
```

START also used checked entry with a 44-byte frame. This test changes no runtime
code; its successful five-level non-tail-recursive run proves that the checked
entry contract from Tests 48-50 composes across repeated workspaces and ordinary
unwind. No WORKEND comparison or overflow behavior is claimed.

### 52-controlled-stack-overflow

Status: **PASS** — emitted `STACK OVERFLOW` through the controlled checked-stack boundary on 2026-10-07.

Uses a non-tail-recursive DEPTH with local `VEC 255`, making each activation
large enough to cross the current 16 KiB static WORK area after a modest number
of calls.

The historical checkpoint is recorded in `docs/stack-check-contract.md`.
BCPLMAC proves the existence of a byte-addressed safe stack limit (`STKLIM`)
distinct from the byte beyond allocated stack (`STKHIGH`), and BLIB identifies
system code `X'0D3'` as stack overflow.

Because the original machine-code STKCK body is not present, the WIP rule is:

```text
W + generated-frame-size <= STKLIM
```

with WORKEND provisionally serving as STKLIM. Expected bootstrap output is:

```text
STACK OVERFLOW
```

Observed DEPTH generation:

```asm
BAL 14,60(11)
DC A(L994) STACK FRAME SIZE
...
LA 15,1044(5)
...
BALR 6,4
...
L994 EQU 1072 STACK FRAME SIZE
```

The 1044-byte W advance and 1072-byte required frame are not identical. The
successful controlled failure therefore strengthens the contract: STKIMPL must
use the inline frame-size word when testing the boundary, not merely the
caller's next-W displacement.

The run emitted `STACK OVERFLOW` and avoided uncontrolled storage corruption.
The test does not yet claim historical ABORT/STOP(100) integration.

### 053-basic-writef

Status: **PASS** — emitted `HELLO` on 2026-10-07.

Begins the WRITEF runtime sprint by replacing the former G!76 no-op with the
smallest executable bootstrap contract. The source calls:

```bcpl
WRITEF("BASIC WRITEF")
```

Expected output:

```text
BASIC WRITEF
```

For this test only, WRITEF treats argument 1 as a BCPL length-prefixed string
and copies its data bytes literally into the existing SYSPRINT buffer. FINISH
performs the already-proven buffered PUT. Format conversions, newline handling,
width controls, additional arguments, and selected-stream behavior remain
deferred.

Generated-code assertions require the G!76 load at byte displacement 304 and
ordinary BALR linkage.

### 054-writef-integer

Status: **PASS** — emitted `42` on 2026-10-08.

Calls `WRITEF("%N", 42)`. The surviving BLIB WRITEF maps `%N` directly to
signed decimal `WRITED(ARG,0)`, so this regression isolates one integer
argument with no width field.

Expected output:

```text
42
```

Generated-code assertions require the second argument in R8, the G!76 load at
byte displacement 304, and ordinary BALR linkage. The bootstrap runtime now
handles literal text plus `%N`; additional directives, multiple formatting
arguments, field widths, and newline semantics remain deferred.

### 055-writef-character-string

Status: **PASS** — emitted `AHELLO` on 2026-10-08.

Constructs the target-format string as `TABLE #X046CC36C,#XE2000000`, binds
`S = "HELLO"`, then calls `WRITEF(F, 193, S)` and expects:

```text
AHELLO
```

The surviving BLIB WRITEF maps `%C` to `WRCH` and `%S` to `WRITES`,
advancing the formatting-argument pointer after each conversion. This
regression therefore proves two conversions in one call: R8 supplies the
character and R9 supplies the BCPL string pointer.

Generated-code assertions check the target EBCDIC character value in R8, the
word-pointer construction in R9, the G!76 load at byte displacement 304, and
ordinary BALR linkage. The runtime now uses a shared bootstrap argument cursor
for `%N`, `%C`, and `%S`.

## MVS-resident Cambridge compile path

The ordinary per-test runner retains the full Cambridge bootstrap path:

```sh
bash native-compiler/regression/run-test.sh NN
```

After the one-time resident compiler installation, the same regression can
use the persistent MVS compiler image:

```sh
bash native-compiler/regression/run-test-mvs.sh NN
```

The two runners share the same downstream generated-S/370 assembly,
BCPLMAIN, native assemble/link/run, and output checks.  Only the Cambridge
compile delivery path changes.  Test 24 is the initial A/B acceptance test
for this resident workflow.

See `native-compiler/mvs-resident-cambridge.md`.
