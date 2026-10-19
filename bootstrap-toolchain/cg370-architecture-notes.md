# CG370 architecture notes

These notes capture the current understanding of the surviving Cambridge System/370 BCPL code generator and the distinction between the bootstrap kit and the later native compiler system.

## OCODE and INTCODE are different levels

The compiler pipeline is best understood as two alternative back ends from OCODE:

```text
BCPL source
    |
    v
SYN / TRN
    |
    v
  OCODE
    |\
    | \__ native target code generator, e.g. CG370
    |
    \____ CGI -> INTCODE -> ICINT
```

OCODE is the compiler's real machine-independent intermediate representation. It is stack-oriented and remains close to the applicative-expression tree walked by TRN.

INTCODE is produced by a code generator. It is a deliberately simpler register-oriented virtual machine intended to make bootstrap implementation practical. The surviving MR10 kit uses this path: OCODE is lowered by CGI and the resulting INTCODE is interpreted by ICINT.

This means INTCODE should not be treated as the normal input language of native target code generators. The surviving Cambridge CG370 consumes OCODE directly.

## Bootstrap kit versus programming system

The MR10 kit is narrowly bootstrap-oriented. Its purpose is to get BCPL compiler phases running on a new host with the smallest practical implementation burden.

The kit frontend does not recognize `SECTION` as a source-language construct. In particular, the system-word table used by SYN/SYNI contains the ordinary BCPL reserved words but no `SECTION`, and TRN/TRNI has no corresponding syntax/operator node.

The practical model is therefore approximately:

```text
one sufficiently large interpreted INTCODE image
    + compiler phases
    + globals / labels resolved inside that image
```

There is no evidence that the kit was designed to be a production multi-section native programming environment.

The later Cambridge compiler is different. `SECTION "name"` is a compiler construct, and native code generation turns a BCPL section into an independently relocatable System/370 control section. Large programs are composed from multiple such sections rather than by allowing one generated section to grow without bound.

A useful distinction is:

- the kit is a porting vehicle;
- the Cambridge native system is a programming system.

## Cambridge SYN/TRN: recognized language versus bootstrap language

A crucial bootstrap distinction is now established: the Cambridge compiler **recognizes** a considerably richer BCPL language than it appears to **use in its own implementation source**.

The Cambridge `SYNHDR` and parser recognize, among other additions relative to the MR10 kit frontend:

- `SECTION` and `NEEDS`;
- `FIX` and `ABS`;
- selectors such as `SLCT` and `SLCTAP`;
- byte application;
- augmented-assignment support through `BECOMESBIT`;
- the floating-point family: `FMULT`, `FDIV`, `FPLUS`, `FMINUS`, `FNEG`, `FLOAT`, `FABS`, and floating comparisons.

Those appearances inside `SYN` and `TRN` are largely compiler data and dispatch logic. For example, `SYN` has parser cases for floating operators because it must recognize them in programs being compiled, and `TRN` has translation cases for floating AST operators because it must emit the corresponding OCODE. That does **not** imply that the implementation of `SYN` or `TRN` itself performs floating-point arithmetic.

Current source inspection has found no actual floating-point expressions required to compile the Cambridge `SYN` and `TRN` implementation sources themselves.

The currently identified *source-language* incompatibilities that prevent direct compilation of Cambridge `SYN`/`TRN` by the MR10 kit are much smaller:

1. The files begin with named sections, e.g.:

   ```bcpl
   SECTION "SYN"
   SECTION "TRNA"
   ```

   The MR10 kit frontend has no `SECTION` keyword.

2. Cambridge source uses the later not-equal spelling `~=` in places such as:

   ```bcpl
   GETBYTE(SECTIONNAME, 0) ~= 0
   ```

   The MR10 lexer recognizes older forms such as `\=` / `NE`, but has no `~` lexical case.

`NEEDS` is particularly instructive. Cambridge `SYN` recognizes it and Cambridge `TRN` passes `SECTION` and `NEEDS` records into OCODE, but the implementation sources inspected so far do not themselves require a source-level `NEEDS "..."` directive in order to compile. Thus `NEEDS` may be needed in the *compiler being bootstrapped* without being needed in the *bootstrap language subset used to compile that compiler*.

This substantially changes the bootstrap strategy. Do not equate “features supported by Cambridge BCPL” with “features that MR10 must learn before it can compile Cambridge SYN/TRN.” The latter set may be very small.

A plausible first bootstrap experiment is therefore to create minimally adapted Cambridge compiler sources that preserve semantics while changing only unsupported surface syntax, for example:

```text
Cambridge SYN/TRN source
        |
        +-- remove or temporarily neutralize top-level SECTION wrappers
        +-- rewrite ~= to an MR10-supported not-equal spelling
        +-- make only proven runtime/header accommodations
        v
MR10 SYNI/TRNI
        v
OCODE -> CGI -> INTCODE -> ICINT
```

If successful, the resulting interpreted Cambridge `SYN/TRN` would then recognize the richer production language, including `SECTION` and `NEEDS`, and could emit authentic Cambridge OCODE for CG370.

## Preferred bootstrap strategy: temporarily demote the Cambridge sources

The preferred strategy is **not** to promote the MR10 kit compiler into a full Cambridge compiler. Instead, temporarily demote the Cambridge compiler sources into the older source dialect accepted by the kit.

This distinction matters:

```text
not preferred:
    extend kit SYN/TRN until the kit understands all Cambridge syntax

preferred:
    minimally rewrite Cambridge SYN/TRN so the existing kit can compile them
```

The adapted sources remain Cambridge `SYN` and Cambridge `TRN`. Their implementation logic, parser tables, operator set, AST representation, and OCODE semantics must remain intact. Only unsupported source spelling and host assumptions should change.

Typical bootstrap adaptations should therefore be of the form:

```text
SECTION "SYN"   -> temporarily omit/neutralize wrapper
SECTION "TRNA"  -> temporarily omit/neutralize wrapper
~=               -> \= or NE
missing runtime global declarations -> compatible bootstrap declarations/shims
host-specific stream assumptions -> controlled bootstrap equivalents
```

The adaptation must be treated as a bootstrap derivative, not as a replacement or modernization of the historical Cambridge sources. Keep the originals untouched and make every semantic or environmental deviation explicit.

The important consequence is that the output of the kit compiler is still an implementation of the **Cambridge** frontend. Once the demoted sources have been compiled through MR10 and converted by CGI to INTCODE, ICINT is running Cambridge `SYN` and `TRN`, not enhanced MR10 phases. Those phases can then recognize the full richer language they were written to recognize.

Conceptually:

```text
historical Cambridge SYN/TRN
            |
            v
 temporary source demotion
  (bootstrap dialect only)
            |
            v
       MR10 SYNI/TRNI
            |
            v
          OCODE
            |
            v
            CGI
            |
            v
 Cambridge SYN/TRN in INTCODE
            |
            v
           ICINT
            |
            v
 full Cambridge frontend behavior
            |
            v
     authentic OCODE -> CG370
```

This is preferable to implementing the later language in MR10 because it minimizes new compiler logic, limits bootstrap changes to source compatibility, and gets the project onto the surviving Cambridge compiler lineage as quickly as possible.

## Runtime/header compatibility for the demoted Cambridge frontend

Source inspection shows that the Cambridge System/370 `LIBHDR` deliberately preserves the important global-vector numbers used by the MR10 kit. Examples include:

```text
SELECTINPUT   11
SELECTOUTPUT  12
RDCH          13
WRCH          14
STOP          30
LEVEL         31
LONGJUMP      32
REWIND        35
APTOVEC       40
FINDOUTPUT    41
FINDINPUT     42
ENDREAD       46
ENDWRITE      47
WRITES        60
WRITEN        62
NEWLINE       63
PACKSTRING    66
UNPACKSTRING  67
READN         70
WRITEF        76
MAPSTORE      78
GETBYTE       85
PUTBYTE       86
```

This is strong evidence of deliberate ABI continuity. The bootstrap problem is therefore not a wholesale global-vector renumbering problem.

### Word geometry

One conspicuous environmental difference is word geometry:

```text
MR10 kit:       BYTESPERWORD = 2
Cambridge/370:  BYTESPERWORD = 4, BITSPERWORD = 32
```

Cambridge `SYN` does not appear to depend directly on `BYTESPERWORD`. Cambridge `TRN` does, notably when packing binary OCODE bytes into its workspace through `WRBYTE`.

For execution under ICINT, do not blindly substitute the native 370 value. `BYTESPERWORD` during bootstrap should describe the semantics of the interpreted machine on which the compiler is running. The correct bootstrap value must be chosen according to ICINT/CGI representation, even though the eventual native target is 32-bit System/370.

### Small missing primitives

Cambridge `SYN` uses `SKIPREC`, global 26 in the Cambridge `LIBHDR`; the reduced kit header does not expose it. This is a real but small runtime gap.

Its use is associated with historical source-record termination/handling. A controlled bootstrap stream may avoid the path initially, but the global still needs to be declared and eventually supplied or shimmed. Missing services of this kind should be treated individually rather than as evidence that a new runtime is required.

### GET and named streams

Cambridge `SYN` implements `GET` by resolving the requested name with `FINDINPUT`, switching with `SELECTINPUT`, and restoring nested inputs through `ENDREAD` and `SELECTINPUT`.

This aligns well with the named-DD stream support already developed for the MVS ICINT host. Therefore header inclusion is likely to be principally a stream provisioning/naming issue. During the earliest bootstrap it is also acceptable to flatten headers if that reduces variables, provided the unmodified `GET` path is subsequently exercised.

### Do not bootstrap the full Cambridge driver first

The full Cambridge `bcpl` driver depends on a much broader runtime surface, including facilities such as parameter streams, output wrapping, logging, stack-limit globals, dynamic segment loading/unloading, code-generator options, and native-system conventions.

Those dependencies are not prerequisites for proving Cambridge `SYN/TRN` under ICINT.

Instead, construct a small bootstrap driver that performs only the initialization actually needed by the frontend:

```text
establish compiler globals and streams
allocate workspace
set WORKBASE / WORKTOP / TREEP
initialize SECTIONNAME and report state
call FORMTREE()
set OBUFP / OBUFB
call COMPILEAE(tree)
capture emitted OCODE
```

The historical compiler driver is evidence for the required initialization sequence; it need not itself be brought up before the frontend.

### Bootstrap proof target

The first decisive proof should be deliberately small. Once demoted Cambridge `SYN/TRN` run under ICINT, compile a source containing at least:

```bcpl
SECTION "TEST"
NEEDS "FOO"
```

and inspect the emitted OCODE. Success demonstrates that the project has crossed from the reduced MR10 bootstrap language into the richer Cambridge frontend without first implementing that richer language in the kit compiler.

The resulting strategy is therefore:

```text
1. preserve original Cambridge sources
2. create auditable bootstrap-demoted copies
3. compile those copies with existing MR10 SYNI/TRNI
4. lower their OCODE through CGI to INTCODE
5. run Cambridge SYN/TRN under ICINT with a small bootstrap driver
6. prove SECTION/NEEDS in emitted OCODE
7. then bring CG370 into the same hosted path
```

The key principle is: **demote the source briefly; do not demote the compiler semantics.**

## CG370 directly consumes OCODE

The surviving `bcplib/bcpl/cg` source explicitly dispatches OCODE operators such as `C.LG`, `C.LP`, `C.LL`, `C.PLUS`, `C.JUMP`, `C.ENTRY`, `C.SAVE`, `C.FNAP`, and `C.RTAP`.

CG370 statically simulates the OCODE evaluation stack rather than translating each OCODE operation into a fixed instruction macro. Temporary values are represented by descriptors, retained in registers when useful, and spilled to BCPL workspace when necessary.

That is an important design point: the higher-level stack semantics of OCODE give the native backend optimization opportunities that would have been lost after lowering to INTCODE.

## System/370 section-size and base-addressing model

CG370 imposes a hard generated-section size limit of approximately 16 KB:

```text
4 * 4095 bytes
```

The diagnostic is explicit:

```text
Code exceeds 4K words - section must be split
```

This is not a whole-program size restriction. It is a restriction on one native BCPL section. The expected remedy is to divide a large program into multiple BCPL sections.

CG370 reserves registers/constants for the four 4-KB windows of a 16-KB section:

```text
R.K4   = register 1
R.K8   = register 2
R.K12  = register 3
R.B    = register 4

K4     = 4096
K8     = 8192
K12    = 12288
```

In listing mode, section setup includes:

```asm
USING 4096,1,2,3
```

The conceptual addressing scheme is therefore:

```text
R.B   = base of the current generated section
R1    = 4096
R2    = 8192
R3    = 12288
```

An RX address can be formed from the section base, one of the 4-KB offset registers, and a legal 12-bit displacement.

This is a much simpler design than continuously assigning arbitrary base registers across a huge compilation unit. The generator instead constrains one section to a size that can be covered by four 4-KB regions.

There is currently no evidence that overlays or GETMAIN are used to solve ordinary generated-code reachability. Dynamic storage allocation is a separate runtime concern.

## Address normalization

All generated RX-form instructions pass through `GENRXA`.

If a displacement already satisfies:

```text
0 <= displacement < 4096
```

it can be emitted directly.

Otherwise `GENRXA` calls `ADJUSTADDR`, which rewrites the effective address so that the final RX instruction uses a legal 12-bit displacement plus an additional register contribution.

Thus CG370 explicitly knows and manages the System/370 12-bit displacement constraint.

BCPL locals and globals are a different addressing problem. They are normally addressed relative to the BCPL runtime registers:

```text
local/workspace  -> R.P
global vector    -> R.G
```

The section-base machinery is mainly for generated code, literal/data references, labels, and other addresses belonging to the generated control section.

## Procedure versus section

Procedure entry does not create a new independently linked control section.

CG370 keeps `BASELAB` and `BASEADDR` state on an internal stack while nested procedure definitions are processed, and restores that state at procedure end. This is code-generation bookkeeping inside one BCPL section.

A BCPL `SECTION`, by contrast, is the unit that becomes an independently relocatable native section/CSECT.

Do not confuse:

- procedure-local base/location accounting inside CG370;
- BCPL section boundaries used for native modularity and linkage.

## Location counting and internal fixups

CG370 maintains its own generated-text location counter, `TXTP`.

Internal labels are recorded in `LABV`. References that cannot yet be resolved are accumulated in halfword and fullword reference lists (`HREFLIST` and `FREFLIST`).

At `CGEND`, CG370 resolves these internal references before writing the object deck:

```text
HREFLIST -> FNHREF -> patch final label value
FREFLIST -> FNFREF -> patch final label value
```

Only after these patches are applied does binary/object-deck generation complete.

This means CG370 is doing substantial assembler-like work itself. It is not merely printing symbolic assembler and expecting IFOX to resolve all ordinary internal labels.

## Object-deck generation

The surviving generator contains both symbolic-listing and binary/object-deck paths.

The listing path emits assembler-like constructs such as instruction mnemonics, `CSECT`, `EXTRN`, `USING`, `DC`, and `END`.

The binary path constructs IBM object-deck records directly, including ESD-style information and relocation/reference machinery.

The current architectural model is therefore:

```text
                 +-> assembler-like listing
OCODE -> CG370 --|
                 +-> relocatable IBM object deck
```

For reconstruction work, the listing path is valuable for inspection and IFOX validation, while the binary path documents the intended native linkage semantics even if the project initially chooses to assemble textual output under MVS.

## External linkage

`CGSTART` establishes the native section and records external requirements. `BCPLMAIN` is always added as a required external, followed by any OCODE `NEEDS` names.

This reinforces the native model:

```text
BCPL SECTION
    -> CSECT
    -> external references / NEEDS
    -> relocatable object
    -> linkage editor
```

The global vector remains the principal BCPL rendezvous mechanism for routines and data, while the native loader/linkage layer handles control sections and the small set of required external objects.

## Consequences for this project

The native compiler path should not be designed as an INTCODE-to-S/370 translator unless such a translator is useful as a separate experiment. The historical native architecture already exists and should be preserved where practical:

```text
BCPL -> SYN/TRN -> OCODE -> CG370 -> native S/370
```

The bootstrap path remains useful because it gives us a runnable environment in which historical BCPL compiler components can execute:

```text
BCPL -> SYN/TRN -> OCODE -> CGI -> INTCODE -> ICINT
```

The strategic goal is to use the bootstrap environment to bring up enough of the Cambridge native machinery that native BCPL itself becomes a development tool. Once that happens, more project code can move from assembler into BCPL, leaving assembler concentrated in startup, MVS interfaces, runtime primitives, and other genuinely machine-facing areas.

## Working rules

1. Treat OCODE as the native backend interface.
2. Treat INTCODE primarily as the bootstrap/interpreter target.
3. Preserve CG370's section model unless MVS hosting proves that a change is necessary.
4. Expect one generated BCPL section to remain below the historical ~16-KB limit.
5. Use multiple BCPL sections for larger native programs.
6. Preserve the historical P/G/global-vector calling model as evidence is reconstructed.
7. Prefer observable historical behavior over speculative redesign.
8. Keep the textual/listing and binary/object paths conceptually separate while studying CG370.
9. Record every host-required divergence from the surviving Cambridge source.
10. Distinguish rigorously between features the Cambridge compiler recognizes and features required to compile the compiler itself.
11. Before extending MR10 language support, prove that the Cambridge compiler implementation actually uses the missing feature.
12. Prefer minimal source-compatible bootstrap adaptations over implementing the entire later Cambridge language in the kit compiler.
13. Keep historical Cambridge sources pristine; perform bootstrap demotion in separate derivative copies.
14. Prefer a small bootstrap driver for hosted Cambridge SYN/TRN over reconstructing the full production compiler driver prematurely.
15. Treat runtime/header gaps as individually provable shims; do not infer a new runtime is required from isolated missing services.
16. Demote source syntax only as far as necessary; preserve Cambridge compiler semantics exactly.
