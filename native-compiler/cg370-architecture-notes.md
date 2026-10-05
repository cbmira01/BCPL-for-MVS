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
