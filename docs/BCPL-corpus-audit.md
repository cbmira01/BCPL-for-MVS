# BCPL corpus audit

This document tracks language and runtime coverage against substantial historical
BCPL source, rather than choosing native regressions only from synthetic examples.

The audit has two complementary purposes:

1. identify constructs and runtime services actually used by large or representative
   BCPL programs of the period; and
2. identify historically specified facilities worth testing even when a particular
   surviving program does not happen to use them.

The second category is deliberate. "Feature fishing" is useful when the feature
has a defensible provenance: a contemporary language definition, runtime manual,
compiler/code-generator contract, or representative historical application.

## Repository policy

Historical source already present in this repository remains the primary local
evidence corpus.

External historical source is **not** to be copied into the tracked repository
merely for audit convenience. If temporary local analysis requires a copy, it
belongs under `workarea/`. Durable tracked output from the audit should be
analysis, provenance, and regression cases written for this reconstruction.

## Primary corpus: surviving Cambridge compiler

The largest and most demanding BCPL artifact currently available to this project
is the Cambridge compiler system.

The audit treats these source containers as the primary compiler corpus:

- `native-compiler/bootstrap-cambridge/source/syn`
  - historical sections SYN and LEX
- `native-compiler/bootstrap-cambridge/source/trn`
  - historical sections TRNA and TRNB
- `richards-bcpltape/bcplib/bcpl/bcpl`
  - compiler master
- `richards-bcpltape/bcplib/bcpl/cg`
  - historical System/370 code generator, sections CGA-CGE
- associated headers including SYNHDR, TRNHDR, CGHDR and LIBHDR

The existing bootstrap tooling deliberately leaves the historical source intact
and creates mechanical derivatives under `workarea/bootstrap-cambridge/`.

### Direct Cambridge source observations

These are representative source occurrences, not inferred language capabilities.

#### SYN / LEX container

The SYN source begins with a VALOF routine:

```bcpl
LET NEWVEC(N) = VALOF
...
RESULTIS TREEP
```

It also contains:

- local `VEC` declarations;
- `SWITCHON` / `CASE`;
- `GETBYTE` and `PUTBYTE`;
- `WRITEF`;
- `GOTO`;
- GLOBAL / STATIC / MANIFEST syntax handling;
- TABLE syntax handling;
- SECTION and NEEDS syntax handling.

The LEX half also contains the historical floating-constant reader. The current
MR10-hosted bootstrap derivative replaces that body with an explicit fatal stub
because the older bootstrap compiler cannot compile Cambridge FLOAT/# operators.
That is a bootstrap accommodation, not evidence that floating-point BCPL is
unimportant.

#### TRN container

TRN contains direct use of:

- `VALOF` / `RESULTIS`;
- local `VEC`;
- `SWITCHON` / `CASE`;
- `GETBYTE` / `PUTBYTE`;
- `WRITEF`;
- `GOTO`;
- TABLE translation;
- STATIC, MANIFEST and GLOBAL translation;
- SECTION and NEEDS translation.

This is especially important: several currently unisolated language features are
not merely accepted by the parser; the translator contains explicit implementation
paths for them.

#### BCPL compiler master

The historical master directly uses:

- `STATIC`;
- `MANIFEST`;
- `VEC`;
- `SWITCHON` / `CASE`;
- `TABLE`;
- `GETBYTE` / `PUTBYTE`;
- `WRITEF`;
- `GOTO`;
- `NEEDS "$LOAD$"`;
- `LOADSEG` and `UNLOAD` overlay logic.

The interpreted bootstrap suppresses the leading NEEDS dependency and keeps the
compiler modules resident together. A native compiler cannot treat that bootstrap
accommodation as the final loader model.

#### Historical System/370 CG

The code generator is a second large BCPL workload in its own right. It contains
substantial use of:

- `VALOF` / `RESULTIS`;
- local vectors;
- `SWITCHON` / `CASE`;
- STATIC and MANIFEST declarations;
- TABLE expressions;
- GETBYTE / PUTBYTE;
- WRITEF;
- GOTO and labels;
- integer shifts and bit manipulation;
- floating-register/code-generation machinery.

### Lexical count snapshot

A simple token scan was used only as a breadth indicator. Counts can include
grammar tables, symbolic constants, comments, or code that implements a language
construct, so they are **not semantic execution counts**.

| Construct | SYN/LEX | TRNA/B | master | CGA-E |
| --- | ---: | ---: | ---: | ---: |
| VALOF | 30 | 6 | 0 | 25 |
| RESULTIS | 93 | 112 | 0 | 129 |
| VEC | 7 | 6 | 2 | 10 |
| SWITCHON | 15 | 20 | 3 | 20 |
| CASE | 310 | 246 | 48 | 222 |
| FOR | 12 | 6 | 7 | 48 |
| GOTO | 60 | 6 | 4 | 84 |
| GETBYTE | 3 | 4 | 3 | 4 |
| PUTBYTE | 1 | 4 | 4 | 2 |
| WRITEF | 8 | 4 | 11 | 26 |
| LOADSEG | 0 | 0 | 5 | 0 |
| UNLOAD | 0 | 0 | 3 | 0 |

The striking point is not the exact counts; it is that the compiler corpus is
large enough to exercise many independent BCPL implementation paths.

## Secondary corpus: historical systems/application BCPL

### TRIPOS

Public historical TRIPOS source is available at:

- https://github.com/borb/tripos

TRIPOS is especially valuable because it is a large systems-programming corpus
from approximately 1976-1982 rather than another copy of the same compiler.

Representative source inspection confirms real use of:

- VALOF / RESULTIS;
- vectors and vector indexing;
- SWITCHON / CASE;
- TABLE;
- GETVEC / FREEVEC;
- GETBYTE / PUTBYTE;
- LOADSEG / UNLOADSEG;
- loops, BREAK and LOOP;
- globals and manifests;
- coroutine services such as CREATECO/COWAIT/RESUMECO in the runtime interface;
- LEVEL/LONGJUMP-style control services.

This independently validates the project decision to treat allocation, byte
operations, dynamic loading and nontrivial control linkage as first-class BCPL
runtime concerns.

### TENEX / PDP-10 BCPL

Public source is available at:

- https://github.com/PDP-10/tenex-bcpl

Representative compiler and application files show heavy use of:

- VALOF / RESULTIS;
- SWITCHON / CASE;
- local and static vectors;
- STATIC;
- MANIFEST;
- TABLE;
- loops;
- labels and GOTO.

This is useful because it represents a different host environment and compiler
lineage. Features appearing in both Cambridge and TENEX code are less likely to
be artifacts of one particular runtime.

### Additional candidate corpora

The Computer History Museum Software Preservation Group BCPL collection indexes
several further period corpora that should be sampled as the audit grows:

- Richards BCPL and TRIPOS archive;
- Essex BCPL;
- John Forecast's POPS;
- PAL/360, whose compiler was written in BCPL;
- MUD1;
- portable BCPL library material.

Index:

- https://softwarepreservation.computerhistory.org/BCPL/

PAL/360 is particularly attractive later because it is an independent compiler
workload from 1970 and has an IBM System/360 connection.

## Historical documentation corpus

Program source answers "what did surviving programs use?" Contemporary
documentation answers the broader question "what did BCPL implementations of the
period claim to provide?"

An important initial source is the 1979 proposed standard prepared by M.D.
Middleton with R. Firth, M. Richards and I. Willers.

Text copy:

- https://github.com/SergeGris/BCPL-compiler/blob/master/doc/standard.txt

Preservation copy:

- https://softwarepreservation.computerhistory.org/BCPL/cambridge/Middleton-Proposed_Definition_of_BCPL-1979.pdf

The core language definition explicitly includes:

- monadic indirection `!E`;
- address-of `@E`;
- dyadic vector application `E1!E2`;
- multiplication, division and REM;
- shifts;
- NOT, &, |, EQV and NEQV;
- conditional expression `E1 -> E2, E3`;
- TABLE;
- VALOF / RESULTIS;
- multiple assignment;
- all principal conditional and repetitive commands;
- GOTO;
- MANIFEST, GLOBAL and STATIC declarations;
- dynamic and vector declarations.

The standard's extension packets provide justified future feature probes even if
a selected corpus does not use them:

- character extensions;
- field selectors;
- optional compilation;
- compound assignment;
- SECTION and NEEDS;
- store allocation;
- scaled arithmetic / MULDIV and RESULT2;
- block I/O;
- binary I/O;
- direct-access I/O;
- system services;
- floating point;
- time and date;
- external procedures.

Other contemporary manuals and implementation reports should be added to this
section as they are audited. Documentation-derived tests should state explicitly
that their provenance is specification/runtime coverage rather than observed use
in a particular program.

## Regression panel 00-39: what it already covers

The existing native panel is much more relevant to real BCPL than a purely
synthetic reading might suggest.

### Strong direct compiler-language coverage

Tests 00-24 and 33-37 establish much of the execution machinery used throughout
the Cambridge corpus:

- procedure and function linkage;
- locals and mutable state;
- globals and callable globals;
- multiple exported globals;
- vectors and indexing;
- pointer values and aliasing;
- one through four arguments;
- function results;
- nested calls and recursion;
- caller-local preservation;
- signed integer arithmetic;
- broad conditional/loop/switch control flow;
- VALOF / RESULTIS, including conditional and nested continuations.

### Runtime coverage with historical value

Tests 27-32 and 39 establish GETVEC/FREEVEC and dynamic pointer behavior.
GETVEC/FREEVEC are not textually called by the four primary Cambridge compiler
source containers inspected above, so these tests should be regarded primarily as
general BCPL runtime/system coverage rather than proof of a direct compiler-source
dependency.

TRIPOS independently demonstrates that GETVEC/FREEVEC are normal period systems
programming facilities, so the work remains well justified.

Test 38 directly establishes PUTBYTE through GETBYTE. Both are present in the
Cambridge corpus and historical runtime interfaces.

### Infrastructure coverage

Tests 25-26 validate separately compiled BCPL and mixed BCPL/native linkage.
These are reconstruction infrastructure tests rather than isolated language
constructs, but they are prerequisites for a realistic library/compiler system.

## Important uncovered or under-isolated areas

The following items now have direct corpus or documentation justification for
new regressions.

### Highest priority: used directly by Cambridge source

1. **STATIC storage**
   - Used directly by the compiler master and CG.
   - No 00-39 test isolates static scalar/vector lifetime and addressing.

2. **MANIFEST constants and constant-expression evaluation**
   - Used directly by compiler source and headers.
   - Needs an explicit compile-time constant regression.

3. **TABLE expressions**
   - Used directly in the master, TRN and CG.
   - The 1979 standard defines TABLE as a static initialized vector.
   - Needs a direct native representation/access regression.

4. **GOTO and labels**
   - Heavily present in SYN/LEX and CG.
   - Test 23 covers structured control flow but does not isolate label/GOTO
     generation.


5. **TABLE semantics beyond basic construction**
   - Test 41 proves that CG370 emits TABLE data as initialized module-resident
     storage and yields a BCPL word pointer to the first element.
   - Additional semantic questions remain worth testing because TABLE can appear
     inside lexical scopes even though its storage is static:
     - if a procedure containing a TABLE is exited and re-entered, does it
       observe the same underlying TABLE object?
     - if TABLE storage is modified through its pointer, is the modification
       visible on the next activation?
     - can a TABLE pointer safely escape its lexical scope and remain valid?
     - do two syntactically distinct TABLE expressions with identical contents
       receive distinct storage objects, or may the compiler coalesce them?
     - what initialization forms are accepted: constants only, manifest
       expressions, addresses, mixed expressions?
     - how are nested or deeply scoped TABLE expressions laid out relative to
       procedure/code bases?
     - is TABLE storage writable in practice on this target, and is that
       behavior relied upon by historical BCPL code?
   - A strong follow-up regression is re-entry persistence:
     mutate one TABLE element on the first call and prove that the second call
     sees the modified value. Expected observation for shared static storage:
     18 then 19, not 18 then 18.
   - This is both corpus-driven and documentation-driven: Cambridge uses TABLE
     directly, while the historical language definition describes TABLE as an
     initialized static vector expression.

5. **Address-of and monadic indirection**
   - Core standard BCPL operations.
   - Existing pointer/vector tests prove pointer values and dyadic `!`, but do
     not deliberately isolate `@E` followed by `!P`.

6. **Integer operator breadth**
   - multiplication;
   - division;
   - REM;
   - shifts;
   - NOT, &, |, EQV, NEQV;
   - conditional expression `-> ,`.
   These are core language operations and are common in compiler/code-generator
   implementation work. Current tests cover only a subset.

7. **Multiple assignment**
   - The language defines it explicitly.
   - The 1979 proposed standard leaves evaluation and assignment order
     undefined and permits assignments before all expressions have been
     evaluated; a swap such as `A,B := B,A` is therefore not a portable
     conformance test.
   - Cambridge TRN recursively translates comma assignments left component
     first, then right component. The first native swap probe consequently
     produced the updated left value in both destinations.
   - Regression coverage should use order-independent right-hand sides and
     record implementation ordering separately from language conformance.

### Compiler/runtime integration gaps

8. **Input and selected-stream I/O**
   - Native WRCH is deliberately narrow.
   - A native compiler must read source and write diagnostics/output through a
     real stream model.

9. **WRITEF / formatted output**
   - Compiler source calls WRITEF frequently.
   - G!76 is still only a temporary native no-op accommodation.

10. **SECTION / NEEDS / GET**
    - These are not ordinary runtime instructions, but they matter for compiling
      the historical compiler source as source rather than as bootstrap-split
      units.

11. **LOADSEG / UNLOAD and module installation**
    - The compiler master contains historical overlay logic.
    - The interpreted bootstrap intentionally bypasses it by keeping all modules
      resident.

12. **Floating-point language/code-generator path**
    - The Cambridge LEX source contains floating-literal parsing.
    - CG370 contains floating register/code machinery.
    - The current bootstrap explicitly stubs one of these paths.

13. **System-vector counting/stack-check services**
    - Still present as runtime stubs.
    - These should be driven by evidence of the exact CG370 emission conditions
      rather than guessed source programs.

## Suggested next regression sequence

The audit changes the immediate priority from system-vector feature exploration
to closing clearly observed compiler-language gaps.

Recommended order, one new thing at a time:

- **40 — STATIC scalar persistence/addressing** — PASS
- **41 — TABLE constant vector** — PASS
- **42 — MANIFEST constant expression** — PASS
- **43 — label/GOTO** — PASS
- **44 — address-of plus monadic indirection** — PASS
- **45 — shifts and bitwise operators** — PASS
- **46 — multiply/divide/REM** — PASS
- **47 — multiple assignment** — revised order-independent probe pending
- **later TABLE semantic probe — re-entry persistence / pointer escape / distinct-object behavior**

The exact numbering after 40 should remain flexible. A failing test or newly
discovered historical requirement may deserve insertion before later candidates.

After these language gaps, return to the larger runtime closure items: real
WRITEF/stream I/O, loader behavior, system-vector services and floating support.

## Audit principle going forward

A new regression may enter the panel for any of three good reasons:

1. **corpus-driven** — a substantial historical BCPL program actually uses it;
2. **contract-driven** — compiler-generated code or the historical runtime ABI
   requires it;
3. **documentation-driven** — contemporary BCPL documentation defines it as a
   core or historically relevant facility worth supporting.

That deliberately leaves room for feature fishing, but requires the reason for
the feature to be recorded.

The regression panel should therefore evolve from "a sequence of things we tried"
into an executable compatibility map tied to historical evidence.
