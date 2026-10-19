# Native compiler strategy: return to the surviving kit compiler

## Status

This document records a deliberate change in project direction.

The native compiler effort will proceed from the surviving MR10 BCPL kit rather than treating that kit only as a bootstrap vehicle for the later Cambridge compiler.

The new target is a native System/370 BCPL implementation for MVS 3.8J whose source language is, initially, the language accepted by the surviving MR10 compiler.

The intended path is:

```text
BCPL source
   |
   v
MR10 SYN
   |
   v
MR10 TRN
   |
   v
OCODE
   |
   v
new System/370 code generator
   |
   v
System/370 assembler
   |
   v
IFOX / linkage editor
   |
   v
native MVS BCPL program
```

The interpreted MR10 compiler and the reconstructed ICINT remain valuable development and validation tools, but the goal is no longer to make the MR10 compiler understand the complete later Cambridge compiler source before native code generation can begin.

---

## Why the approach changed

The surviving material appears to span two materially different stages of BCPL development.

The MR10 kit looks like an early portable compiler baseline. It contains the familiar bootstrap components:

- `syn` / `syni`
- `trn` / `trni`
- `cg` / `cgi`
- `blib` / `blibi`
- `icint`

The later `bcplib` material is a substantially evolved Cambridge compiler. Its source and headers show facilities not accepted by the kit front end, including later compilation-unit syntax and additional expression machinery.

The exact historical chain between these compiler generations is not completely reconstructed here, but the practical evidence is unambiguous: the later compiler has outgrown the bootstrap compiler preserved in the kit.

That should not be treated as a defect in the kit. It is better understood as evidence that several years of compiler evolution occurred after the portable bootstrap baseline.

The project therefore returns to the earlier historical position: we have a small working compiler, a portable intermediate form, and an opportunity to make a new native target implementation from that point.

---

## What the Cambridge bootstrap experiment taught us

The attempted bootstrap of the later Cambridge compiler was useful and should be regarded as a successful experiment even though it did not produce a later native compiler.

It established that the MVS hosting infrastructure can:

- assemble and link the reconstructed ICINT;
- run the preserved MR10 compiler phases under MVS;
- compile ordinary source accepted by the MR10 dialect;
- pass textual OCODE into CGI;
- stage multiple interpreted compiler components;
- discover MVS DDNAME streams dynamically;
- support sufficiently large interpreter vectors when configured correctly.

It also exposed the real language boundary.

When the later Cambridge sources were presented to the MR10 front end, the compiler rejected constructs that are not part of the older dialect. Examples observed directly include:

- `SECTION "..."`;
- later source organization involving `NEEDS`;
- byte-application syntax and other later operators;
- later lexical conveniences;
- floating-point syntax and operators;
- additional selector/application machinery;
- generalized compound-assignment handling.

The later Cambridge compiler source and header explicitly contain floating-point operators and conversions, including floating arithmetic, floating comparisons, `FLOAT`, `FIX`, and `FABS`. The older MR10 front end does not have this language surface.

The bootstrap run also demonstrated an important tooling lesson: an MVS step RC of zero from ICINT does not by itself mean that the interpreted BCPL program succeeded. Compiler-level completion codes and diagnostics must be treated as first-class results in future tooling.

---

## Working historical interpretation

The current working interpretation is:

1. the portable kit represents an older, roughly early-1970s BCPL compiler baseline;
2. the later Cambridge compiler represents a significantly evolved implementation by about 1981;
3. much of the intervening compiler development is not represented as an obvious, continuous sequence in the surviving material;
4. by the later stage, the production compiler source language itself contains facilities the bootstrap compiler does not understand;
5. forcing the old compiler to absorb the whole later compiler before doing native code generation would turn the project into a language-reconstruction exercise rather than a straightforward native port.

This interpretation is deliberately phrased as a project model rather than a claim that every missing historical revision has been proven lost. What matters for implementation is that the surviving executable bootstrap compiler and the later source tree are not source-compatible.

---

## New success criterion

A successful first native compiler does **not** need to reproduce every facility of the later Cambridge compiler.

The first native implementation should provide a sound MR10-family BCPL suitable for systems programming on MVS.

The core language already includes the facilities that make BCPL useful:

- integer arithmetic;
- Boolean and bitwise operations;
- shifts and comparisons;
- `LET` and `AND` definitions;
- functions and routines;
- `VALOF` and `RESULTIS`;
- `GLOBAL`, `STATIC`, and `MANIFEST` declarations;
- vectors and word-addressed pointer idioms;
- strings;
- conditional expressions and commands;
- `IF`, `UNLESS`, `TEST`;
- `FOR`, `WHILE`, `UNTIL`, and repeat forms;
- `SWITCHON`, `CASE`, and `DEFAULT`;
- `GOTO`, labels, `BREAK`, `LOOP`, `RETURN`, and `FINISH`;
- `GET` source inclusion;
- separate modules through the global-vector model.

That is enough to form a serious systems-programming language for MVS.

Later facilities are improvements, not prerequisites.

---

## Later Cambridge features are optional forward development

Facilities seen in the later compiler should be treated as candidates for future work rather than bootstrap dependencies.

Examples include:

- `SECTION` and `NEEDS`;
- byte-application syntax;
- selector expressions and selector application;
- generalized compound assignments;
- case-folding and broader lexical conveniences;
- floating-point literals and operators;
- later compiler diagnostics and source-organization features.

Some of these may be cheap to add later. Others may not be worth adding at all.

The important policy is that no later feature should block completion of a useful native MR10-family compiler.

---

## Floating point: prefer a library first

Floating point is a good example of the new philosophy.

The initial compiler need not acquire floating-point syntax.

A useful first floating-point facility can be supplied through ordinary BCPL library calls. For example:

```text
FADD
FSUB
FMUL
FDIV
FCMP
ITOF
FTOI
```

On System/370 these routines can initially be implemented in assembler using the machine floating-point instructions, while their BCPL interfaces pass ordinary word values according to an agreed representation.

A natural first representation is IBM short floating point in one 32-bit BCPL word. Long floating point could later be represented by two words if useful.

Higher mathematical functions can then be built over the primitive operations.

This approach has several advantages:

- no front-end change is required;
- no new OCODE operators are required initially;
- no new code-generator expression cases are required initially;
- the runtime work remains useful if floating syntax is added later;
- later compiler operators could simply lower to the same runtime ABI.

Therefore integrated floating-point language syntax is explicitly **not** a first-release requirement.

---

## The later Cambridge compiler remains valuable

Abandoning the Cambridge-first bootstrap does not make the later source irrelevant.

It remains useful as historical and engineering evidence, especially for:

- System/370 code-generation strategy;
- procedure entry and exit conventions;
- register use;
- global-vector access;
- stack and workspace organization;
- emitted assembler style;
- runtime expectations;
- MVS-specific design choices;
- examples of how BCPL evolved after the kit compiler.

The canonical surviving later source remains under `richards-bcpltape/bcplib/`.

It should be consulted as a reference implementation, not treated as the source that the MR10 bootstrap must compile.

---

## Native code generator direction

The most direct native path is to replace the kit's INTCODE-target code generator with a System/370-target code generator that consumes the same OCODE produced by MR10 TRN.

The initial code generator should favor transparency over optimization.

Recommended principles:

1. preserve the meaning of the MR10 OCODE exactly before optimizing;
2. emit readable IFOX-compatible assembler;
3. make procedure, stack, global, and pointer conventions explicit in comments and documentation;
4. use small acceptance programs to validate each OCODE family;
5. compare native execution against ICINT execution of the same source;
6. keep the global-vector rendezvous model central rather than depending heavily on the native linker;
7. treat the later Cambridge S/370 generator as evidence, not as an implementation that must be copied blindly.

The likely development sequence is:

1. inventory the exact OCODE emitted by MR10 TRN;
2. define the native BCPL ABI for System/370;
3. implement a minimal generator for constants, local variables, arithmetic, branches, and `FINISH`;
4. add procedure calls and results;
5. add globals and multiple compilation units;
6. add vectors and indirect addressing;
7. add switches and remaining control forms;
8. connect native runtime I/O and storage services;
9. compile increasingly substantial BCPL programs;
10. eventually compile the compiler's own MR10 source if useful and practical.

Self-hosting is desirable but should follow a usable native compiler rather than precede it.

---

## Runtime direction

The native runtime should be built to satisfy the actual contracts required by the kit language and generated programs.

Expected areas include:

- program startup and termination;
- global-vector construction and initialization;
- BCPL procedure-call conventions;
- stack/workspace management;
- stream selection and character I/O;
- DDNAME discovery for MVS datasets;
- `GETVEC` / `FREEVEC`;
- string and byte helpers;
- `WRITEF` and related library services;
- diagnostics and failure paths;
- optional coroutine services if retained in the supported runtime profile.

The reconstructed ICINT host work remains useful here because it has already forced many abstract BCPL service contracts to be made explicit on MVS.

---

## Programmer documentation is part of the product

A native compiler is not complete merely because it accepts source and produces load modules.

The project should provide programmer-facing documentation for the exact dialect and implementation delivered on MVS.

This is especially important because later BCPL references may show facilities that the MR10 compiler does not support.

### Important discovery: a contemporary manual survives

The preserved tape contains:

`richards-bcpltape/mr10/print/manual`

This is *The BCPL Programming Manual* by M. Richards, dated November 1974.

Its table of contents includes:

- a language definition;
- expressions and addressing operators;
- arithmetic, relations, shifts, logical and conditional operators;
- section brackets;
- commands and declarations;
- `GET`;
- comments and synonyms;
- the run-time library;
- input/output routines;
- library variables;
- a complete section titled **Using BCPL on the 370**;
- compilation, diagnostics, options, loading, execution faults, and a complete job;
- appendices for syntax, symbols, EBCDIC, and common extensions.

This is exceptionally strong evidence that the kit-era language was intended to be usable by programmers, not merely as an undocumented bootstrap representation.

The manual should become a principal historical source for the new implementation.

### Proposed BCPL for MVS Programmer's Guide

The project should eventually produce a concise modern guide tied to the actual implementation. It should include at least:

1. **Getting started**
   - minimal BCPL program;
   - compile, assemble, link, run;
   - example JCL.

2. **Exact language accepted**
   - lexical rules;
   - constants and strings;
   - expressions and precedence;
   - declarations;
   - commands;
   - functions and routines;
   - vectors and pointer idioms;
   - globals and separate modules.

3. **MVS programming model**
   - DDNAME streams;
   - record-oriented host I/O versus BCPL character streams;
   - dataset expectations;
   - reopenable datasets versus JES in-stream data;
   - EBCDIC considerations.

4. **Runtime library**
   - standard globals;
   - I/O services;
   - storage services;
   - string and byte utilities;
   - diagnostics;
   - optional floating-point library.

5. **Compiler and linkage model**
   - SYN/TRN/code-generator phases;
   - OCODE in brief;
   - assembler and linkage editor flow;
   - global-vector linkage philosophy.

6. **Limits and implementation-defined behavior**
   - word size;
   - address representation;
   - vector and stack limits;
   - source record rules;
   - character representation.

7. **Dialect differences**
   - a table of kit-era BCPL versus later Cambridge/modern BCPL;
   - explicit warnings when historical examples use unsupported later syntax.

8. **Examples**
   - arithmetic;
   - vectors;
   - strings;
   - recursion;
   - switches;
   - file I/O;
   - multiple modules;
   - systems-programming idioms.

The surviving 1974 manual should be mined carefully, but the new guide should describe the implementation we actually deliver rather than silently assuming every feature of every historical BCPL system.

---

## Source-of-truth hierarchy

For the new native compiler effort, use the following evidence order when behavior is uncertain:

1. the executable behavior of the preserved MR10 compiler phases;
2. the MR10 `syn`, `trn`, and related source;
3. the 1974 BCPL Programming Manual preserved under `mr10/print/manual`;
4. bootstrap and INTCODE documentation under `mr10/text/`;
5. other contemporary MR10 material in the tape;
6. later Cambridge sources as evolutionary and S/370 implementation evidence;
7. modern BCPL documentation only when clearly identified as later context.

This keeps the implemented language tied to evidence from the compiler we actually possess.

---

## What has been retired

The previous active `native-compiler/` contents were removed as part of this reset, including:

- the staged duplicate Cambridge compiler tree;
- the previous native ABI/OCODE planning documents;
- the old native acceptance plan and fixtures.

The Cambridge bootstrap job generator was also removed from `tools/`.

Historical evidence was **not** removed from `richards-bcpltape/`.

General ICINT, compiler, runtime, regression, demo-suite, MVS, and Hercules material elsewhere in the repository remains valid unless separately superseded.

---

## Immediate next questions

The reset leaves a deliberately small active workspace. The next work should answer these questions in order:

1. What is the complete OCODE contract emitted by the MR10 TRN phase?
2. Which existing target code generators from the same period are closest structurally to a System/370 generator?
3. What minimal native ABI best preserves BCPL's global-vector and workspace model on MVS?
4. Which runtime calls are required to execute the smallest generated native program?
5. What acceptance ladder should validate the new generator one OCODE family at a time?
6. Which parts of the 1974 manual exactly match the preserved compiler, and which are installation-specific or optional extensions?

Only after those are understood should the new native compiler directory begin accumulating implementation files again.

---

## Project philosophy after the reset

The project is no longer trying to recover every missing compiler improvement between the old bootstrap kit and the later Cambridge system before it can succeed.

Instead:

> Start from the compiler that survives, make it native on MVS, document it well, and leave clear ground for future improvement.

That produces a historically grounded, useful BCPL implementation sooner, while keeping later language evolution available as optional work for anyone who wants to extend the system.
