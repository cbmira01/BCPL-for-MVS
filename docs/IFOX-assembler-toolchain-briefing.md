# The IFOX Assembler Toolchain on MVS 3.8 / System/370

## 1. Purpose and Scope

This briefing introduces the assembler toolchain used by a general-purpose or systems programmer working in **System/370 assembler under MVS 3.8**, with particular emphasis on the **IFOX assembler**, the MVS linkage editor, libraries, program loading, and the conventions that connect separately assembled routines.

The objective is orientation rather than exhaustive reference. A new programmer should finish this briefing with a working mental model of:

- how assembler source is organized;
- how IFOX is invoked and what it produces;
- the distinction between machine instructions, assembler instructions, macros, and copied source;
- symbols, expressions, constants, storage, literals, and addressability;
- control sections and external symbols;
- what an object module contains conceptually;
- how the linkage editor combines object modules and searches libraries;
- the distinction between source, macro, object, and load-module libraries;
- what a load module is and how MVS finds and starts it;
- MVS linkage conventions between independently written routines;
- runtime program-management facilities such as `LOAD`, `LINK`, and `XCTL`;
- how assembler macros relate to MVS operating-system services;
- how listings, maps, return codes, ABEND information, and dumps support debugging.

This is a **toolchain briefing**, not a complete System/370 architecture manual or MVS services manual. Hardware and operating-system topics are included only where they illuminate the assembly, linkage, loading, or execution process.

---

## 2. The Toolchain at a Glance

The normal development path is:

```text
             assembler source
                    |
        +-----------+-----------+
        |                       |
   copied source             macro definitions
   and libraries             and libraries
        |                       |
        +-----------+-----------+
                    |
                    v
                  IFOX
                    |
          +---------+---------+
          |                   |
          v                   v
   assembly listing      object module(s)
                              |
                        object libraries
                              |
                              v
                       LINKAGE EDITOR
                              |
                    +---------+---------+
                    |                   |
                    v                   v
                link map          load module
                                      |
                               load-module library
                                      |
                                      v
                                MVS program fetch
                                      |
                                      v
                              executing program
                                      |
                   +------------------+------------------+
                   |                  |                  |
                   v                  v                  v
              MVS services       other modules        data sets
```

A rough modern analogy is:

```text
source.asm -> assembler -> source.o -> linker -> executable -> OS loader
```

The analogy is useful, but MVS terminology matters:

- an **object module** is relocatable assembler output intended for the linkage editor;
- a **load module** is an executable program representation produced by the linkage editor;
- a **PDS member** is commonly the unit used to store source, macros, object modules, or load modules;
- the **linkage editor** performs the role broadly called linking today;
- **program fetch** is part of MVS program management that locates and makes a load module executable.

Keep these stages separate even when cataloged procedures or local tooling make them appear to be one operation.

---

## 3. The Principal Components

### 3.1 IFOX

IFOX translates symbolic assembler language into System/370 machine code and object-module information.

Its work includes:

- parsing assembler statements;
- assigning locations;
- translating machine-instruction mnemonics;
- evaluating symbols and expressions;
- defining and reserving storage;
- maintaining literal pools;
- expanding macros;
- performing conditional assembly;
- processing copied source;
- recording external definitions and references;
- generating relocation information;
- reporting diagnostics;
- producing an assembly listing;
- writing an object module.

IFOX normally does **not** produce the final executable load module.

### 3.2 The linkage editor

The MVS linkage editor accepts one or more object modules and constructs a load module.

Its responsibilities include:

- collecting control sections;
- resolving external references against external definitions;
- searching object libraries;
- assigning relative locations;
- processing relocation information;
- determining the executable entry point;
- diagnosing unresolved or conflicting symbols;
- producing a load module;
- producing maps and cross-reference information when requested.

### 3.3 MVS program management

Once a load module exists, MVS can locate it in an appropriate program library, make it available in virtual storage, establish the execution environment, and transfer control to its entry point.

Thus there are three major transformations:

```text
ASSEMBLY               LINK-EDIT                 EXECUTION

source                  object module            load module
  |                           |                       |
  v                           v                       v
IFOX                    linkage editor             MVS
  |                           |                       |
  v                           v                       v
object module           load module             executing code
```

---

## 4. Invocation Under MVS

MVS development is normally performed through batch jobs and job steps.

At its simplest, an assembler development job contains three logical operations:

```text
ASSEMBLE -> LINK-EDIT -> GO
```

Conceptually, the JCL resembles:

```jcl
//ASM      EXEC PGM=IFOX00,...
     ...
//LKED     EXEC PGM=IEWL,...
     ...
//GO       EXEC PGM=MYPROG
     ...
```

The exact DD statements, data-set names, and parameters depend on the installation and cataloged procedures in use.

Cataloged procedures commonly package the boilerplate for operations such as:

- assemble only;
- assemble and link-edit;
- assemble, link-edit, and execute.

A programmer should nevertheless retain the underlying model. Each step has independent inputs, outputs, return codes, diagnostics, and failure modes.

---

## 5. Source-Line Layout and Card-Image Heritage

Assembler source of this period reflects punched-card conventions. A statement is organized into fields resembling:

```text
LABEL    OPERATION    OPERANDS                    COMMENTS
```

For example:

```asm
LOOP     LA    3,1(3)              ADVANCE COUNTER
         C     3,LIMIT             COMPARE WITH LIMIT
         BL    LOOP                CONTINUE IF LOW
```

The source format is not merely visual style. Traditional assembler input assigns meanings to columns and provides defined continuation and sequence conventions.

A programmer needs to recognize:

- the name or label field;
- the operation field;
- the operand field;
- comments;
- continuation rules;
- sequence fields;
- full-line comments.

Even when source is maintained today as ordinary text, IFOX syntax retains this card-oriented ancestry.

---

## 6. Labels and Symbols

A label associates a symbolic name with the value appropriate to a statement.

For example:

```asm
BUFFER   DS    CL80
```

`BUFFER` denotes the location assigned to that storage.

A label on an instruction identifies the location of the instruction:

```asm
AGAIN    LA    3,1(3)
         B     AGAIN
```

Symbols remove the need to manually calculate most addresses.

A symbol need not represent a runtime variable. For example:

```asm
BUFLEN   EQU   80
```

creates an assembly-time symbolic value.

A symbol may therefore identify:

- code;
- data;
- an absolute value;
- a relocatable value;
- an offset;
- a register number;
- another assembly-time property.

This is an important distinction: **symbols belong first to the assembler's model of the program**.

---

## 7. Machine Instructions

A System/370 machine instruction can be represented symbolically:

```asm
         LR    3,4
```

IFOX converts the mnemonic and operands into the corresponding binary instruction.

Typical instruction categories include:

- loads and stores;
- register transfers;
- fixed-point arithmetic;
- decimal arithmetic;
- floating-point arithmetic;
- comparisons;
- logical operations;
- shifts and rotates where provided by the architecture;
- conditional and unconditional branches;
- branch-and-link operations;
- selected system or privileged operations.

For example:

```asm
         L     3,COUNT
         A     3,ONE
         ST    3,COUNT
```

conceptually performs:

```text
R3 <- COUNT
R3 <- R3 + ONE
COUNT <- R3
```

The detailed semantics belong to the System/370 architecture. The assembler's role is to encode the requested instruction and represent address-dependent information correctly.

---

## 8. Assembler Instructions Versus Machine Instructions

Not every source statement becomes a CPU instruction.

For example:

```asm
ONE      DC    F'1'
BUFFER   DS    CL80
```

`DC` and `DS` are instructions to the assembler, not instructions executed by System/370.

The distinction is fundamental:

```text
machine instruction
        |
        v
generates an instruction executed by the CPU

assembler instruction
        |
        v
controls assembly, symbols, storage, sections,
or the generated object representation
```

Assembler instructions are also called **directives** or **pseudo-operations**.

Important families include facilities for:

- defining storage;
- reserving storage;
- defining symbols;
- controlling location and alignment;
- defining control sections;
- declaring external symbols;
- controlling base-register assumptions;
- managing literal pools;
- controlling listings;
- ending assembly.

---

## 9. Data Definition and Layout

### 9.1 `DC` — Define Constant

`DC` creates initialized storage.

Examples:

```asm
ONE      DC    F'1'
ZERO     DC    F'0'
LETTER   DC    C'A'
MESSAGE  DC    C'HELLO, WORLD'
```

The represented bytes become part of the generated program.

### 9.2 `DS` — Define Storage

`DS` reserves storage without supplying ordinary initialized contents:

```asm
WORK     DS    F
BUFFER   DS    CL80
```

### 9.3 Representation is explicit

The assembler programmer must understand the representation selected by each declaration, including such things as:

- characters;
- bytes;
- halfwords;
- fullwords;
- doublewords;
- addresses;
- packed decimal data;
- floating-point values;
- repeated fields;
- structures constructed from consecutive definitions.

Assembler gives the programmer direct control over byte-level layout.

---

## 10. Alignment and the Location Counter

IFOX maintains a current assembly location. As statements generate code or data, the location advances.

Conceptually:

```text
current location = X

4-byte instruction
current location = X + 4

4-byte constant
current location = X + 8
```

Labels normally acquire values based on this evolving location.

Alignment matters because instructions and data objects may have natural or required boundaries. Assembler facilities can establish suitable boundaries or explicitly alter location organization.

Understanding the location counter explains:

- how labels receive values;
- how structures are laid out;
- why padding can appear;
- how section lengths are determined;
- what the location column in a listing means.

---

## 11. Expressions and `EQU`

Assembler operands can contain expressions evaluated during assembly.

`EQU` is especially useful for defining:

- constants;
- register names;
- offsets;
- lengths;
- aliases;
- values derived from other symbols.

For example:

```asm
BUFLEN   EQU   80
R3       EQU   3
R13      EQU   13
```

The assembler distinguishes between absolute values and values whose meaning is tied to relocatable sections. That distinction becomes important when object-module relocation information is produced.

---

## 12. Literals and Literal Pools

Assembler allows an operand to request a literal value without requiring the programmer to define a separately named constant.

Conceptually, instead of:

```asm
ONE      DC    F'1'
         L     3,ONE
```

a programmer can request an appropriate literal directly in an operand.

IFOX collects literals into **literal pools** and assigns them storage.

This means some storage in the generated program exists because the assembler created it in response to literal references rather than because the source explicitly contained a normal labeled `DC`.

Literal-pool placement can matter because System/370 base-displacement addressing has finite reach. Facilities such as `LTORG` allow the programmer to cause a literal pool to be emitted at an appropriate point.

---

## 13. Control Sections

A separately relocatable portion of a program is represented by a **control section**, usually abbreviated **CSECT**.

For example:

```asm
MYPROG   CSECT
```

A control section has such properties as:

- a name;
- a length;
- generated contents;
- symbols associated with locations within it;
- relocation properties.

The key mental model is:

> A CSECT is a relocatable program section, not an absolute physical-memory address.

The assembler establishes the internal organization of a CSECT. The linkage editor later establishes its relationship to other control sections in the completed load module.

---

## 14. Addressability: `USING` and `DROP`

One of the most important System/370 assembler concepts is **base-register addressability**.

Many storage-reference instructions encode an effective address using a base register plus a limited displacement. IFOX therefore needs to know which registers the programmer intends to contain useful base addresses.

A statement such as:

```asm
         USING MYPROG,12
```

tells the assembler, conceptually:

> Assume register 12 contains the address represented by `MYPROG`, and use that relationship when forming address operands.

It does **not** itself load register 12.

The runtime program must establish the actual register contents.

`DROP` tells the assembler to stop using a specified base-register assumption.

Thus:

```text
ASSEMBLY-TIME KNOWLEDGE             RUNTIME CPU STATE

USING relationship           !=    loading the register
DROP relationship            !=    changing the register
```

Addressability errors are therefore assembler errors even though the underlying problem concerns what addresses a runtime instruction can represent.

---

## 15. Macros

The IFOX macro facility is much more powerful than simple textual substitution.

A macro can encapsulate:

- sequences of assembler statements;
- positional parameters;
- keyword parameters;
- defaults;
- generated symbols;
- assembly-time variables;
- conditional assembly;
- repetitive generation.

Conceptually:

```asm
         SOMEMAC ARG1,ARG2
```

may generate many ordinary assembler statements.

Macros are particularly important under MVS because many operating-system programming interfaces are presented to assembler programmers as macros.

For example, a source statement resembling:

```asm
         OPEN  (...)
```

is not a System/370 `OPEN` instruction. The assembler macro processor expands the macro into the required code and/or control structures for the MVS interface.

---

## 16. Conditional Assembly

Conditional assembly makes decisions **while the source is being assembled**.

```text
assembler evaluates condition
          |
     +----+----+
     |         |
  generate   omit
  source     source
```

This differs fundamentally from a runtime conditional branch:

```text
CPU executes condition
          |
     +----+----+
     |         |
   branch    continue
```

Conditional assembly is useful for:

- optional features;
- configuration variants;
- reusable macros;
- debug instrumentation;
- different calling environments;
- selecting declarations or generated instruction sequences.

A condition resolved during assembly need leave no runtime test in the program.

---

## 17. `COPY` and Source Inclusion

Assembler source can be included from libraries.

Conceptually:

```text
main source
    |
    +------ COPY MEMBER ------+
                              |
                       source library
                              |
                              v
                     included statements
```

This is an **assembly-time source inclusion** operation.

It must be distinguished from object-module inclusion by the linkage editor:

```text
COPY / source inclusion
        |
        v
assembler consumes more source

object-library inclusion
        |
        v
linkage editor consumes an already assembled module
```

A library utility may maintain either library, but the consuming operation belongs to the assembler or linkage editor respectively.

---

## 18. Macro and Source Libraries

Assembler installations normally provide libraries containing reusable material such as:

- system macro definitions;
- installation macros;
- application macros;
- copied declarations;
- control-block mappings;
- common symbolic definitions.

MVS commonly stores such material in **partitioned data sets (PDSs)**.

Conceptually:

```text
SOMELIB
   |
   +-- MEMBER1
   +-- MEMBER2
   +-- MEMBER3
```

A PDS is an organizational mechanism. Different PDSs can contain fundamentally different kinds of members.

---

## 19. What IFOX Produces

Two assembler outputs are especially important to the programmer:

1. the **assembly listing**;
2. the **object module**.

The listing is primarily a human diagnostic and reference artifact.

The object module is primarily machine-readable input to the linkage editor.

---

## 20. The Assembly Listing

The assembly listing is one of the principal debugging tools in this environment.

Depending on selected options, it can show:

- source statements;
- assigned locations;
- generated machine code;
- generated data;
- macro expansion;
- symbol definitions;
- symbol cross-references;
- literal information;
- diagnostics;
- statement numbers.

A conceptual listing line might resemble:

```text
LOCATION     OBJECT CODE            SOURCE
000120       5830 C180              L     3,VALUE
```

The important relationship is:

```text
source statement
       |
       +--> assigned address
       +--> generated bytes
       +--> diagnostic information
```

When debugging a dump, the listing connects machine addresses and bytes back to source statements.

---

## 21. Symbol Tables and Cross-References

A symbol table reports symbols recognized by the assembler and their values or attributes.

A cross-reference additionally indicates where symbols were referenced.

These facilities are useful for:

- locating definitions;
- checking spelling;
- understanding assigned addresses;
- finding all uses of a symbol;
- tracing macro-generated references;
- interpreting dumps.

For a substantial assembler program, the cross-reference describes what the assembler actually understood, which can be more informative than textual searching alone.

---

## 22. Diagnostics and Return Codes

IFOX reports source problems and assigns diagnostic severity.

Examples include:

- invalid operation codes;
- malformed operands;
- undefined symbols;
- duplicate symbols;
- invalid expressions;
- addressability failures;
- incorrect macro usage.

A job step also returns a completion or condition code.

A programmer therefore asks two questions:

1. Did the assembler step complete?
2. Were its diagnostics acceptable?

Some errors may still permit object output to be produced. Whether subsequent linkage should proceed is a separate decision, often controlled by JCL or cataloged-procedure conventions.

---

## 23. Object Modules

The object module is the bridge between assembly and linkage editing.

It contains more than machine-code bytes. Conceptually it must communicate information such as:

```text
+-----------------------------------+
| section definitions               |
+-----------------------------------+
| generated text / machine code     |
+-----------------------------------+
| externally visible symbols        |
+-----------------------------------+
| unresolved external references    |
+-----------------------------------+
| relocation information            |
+-----------------------------------+
| identification / entry data       |
+-----------------------------------+
```

IBM object formats expose these concepts through records such as **ESD**, **TXT**, and **RLD**.

At orientation level:

- **ESD** describes external symbols and sections;
- **TXT** carries generated text;
- **RLD** describes relocation relationships.

The exact binary/card format is less important initially than understanding why the information is necessary.

---

## 24. Why Relocation Is Necessary

IFOX generally does not know the final execution address of a control section.

Suppose a section contains:

```text
offset 0000   instruction
offset 0004   instruction
offset 0008   address-dependent field
```

The final value needed at offset `0008` may depend on where the linkage editor places this section relative to others.

The object module therefore identifies fields that require relocation. The linkage editor adjusts them when it determines the final organization of the program.

Keep these concepts distinct:

```text
offset within a control section
```

and:

```text
address when the program executes
```

---

## 25. External Definitions and References

Separate assembly requires a way for one module to refer to symbols defined by another.

Suppose module A calls a routine defined in module B.

Module A may declare an external reference conceptually as:

```asm
         EXTRN ROUTINEB
```

Module B makes the corresponding symbol available for external linkage.

The object modules then communicate:

```text
MODULE A
    |
    +-- "I require ROUTINEB"

MODULE B
    |
    +-- "I define ROUTINEB"
```

The linkage editor reconciles them:

```text
MODULE A ---- external reference ----+
                                     |
                                     v
                               linkage editor
                                     ^
                                     |
MODULE B ---- external definition ---+
```

This is the basis of separately assembled modular programs.

---

## 26. Entry Points

A program may contain symbols intended as externally callable entry points, and the resulting load module must have an execution entry point.

Several concepts are related but distinct:

- control-section name;
- externally visible symbol;
- callable entry point;
- load-module member name;
- load-module execution entry point.

They are often intentionally given the same name, but they need not represent the same namespace or toolchain stage.

---

## 27. The Linkage Editor in More Detail

The linkage editor receives object modules and produces an executable load-module organization.

```text
          object A
             |
          object B
             |
          object C
             |
             +------------+
                          |
                    linkage editor
                          |
                  +-------+-------+
                  |               |
             object library      |
                  |               |
                  +-------+-------+
                          |
                          v
                     load module
```

Its principal work includes:

- collecting input control sections;
- resolving external references;
- extracting required library members;
- assigning relative locations;
- processing relocation;
- selecting or accepting an entry point;
- diagnosing duplicate or unresolved symbols;
- constructing the load module.

---

## 28. Linkage-Editor Control

The linkage editor accepts control information in addition to object modules.

A programmer may need to control matters such as:

- the entry point;
- library searches;
- explicit module inclusion;
- module naming;
- aliases;
- section relationships;
- replacement or modification of sections;
- output characteristics.

Ordinary programs may rely on cataloged procedures and defaults. Systems work, reusable libraries, unusual module structures, or maintenance of existing load modules can expose these facilities directly.

---

## 29. Object Libraries and Automatic Inclusion

Suppose module A requires `SUBRTN`, but the object module containing `SUBRTN` was not explicitly supplied in the input stream.

The linkage editor can search an object library:

```text
A requires SUBRTN
       |
       v
linkage editor
       |
       +--> search object library
                 |
                 +-- X
                 +-- Y
                 +-- SUBRTN  <--- selected
                 +-- Z
```

The required member can be extracted automatically.

Compare this with assembly-time inclusion:

```text
ASSEMBLY TIME                       LINK-EDIT TIME

COPY MEMBER                         unresolved SUBRTN
     |                                     |
     v                                     v
source library                       object library
     |                                     |
     v                                     v
source statements                    object module
     |                                     |
     v                                     v
IFOX                                linkage editor
```

These mechanisms solve different problems at different stages.

---

## 30. The Load Module

The linkage editor's persistent executable product is a **load module**.

It is not merely an object module under another name. By this stage:

- input control sections have been organized;
- external references have been reconciled as appropriate;
- relocation relationships have been processed;
- executable organization has been established;
- an entry point is known.

Load modules are commonly stored as members of a PDS used as a program library:

```text
MY.LOADLIB
    |
    +-- MYPROG
    +-- UTILITY
    +-- SUBSYS
```

These members are executable load modules, not source text.

---

## 31. Source, Macro, Object, and Load Libraries

A programmer should distinguish these immediately:

| Library role | Typical contents | Principal consumer |
|---|---|---|
| Source library | assembler source / copied members | assembler |
| Macro library | macro definitions | assembler macro processor |
| Object library | relocatable object modules | linkage editor |
| Load library | executable load modules | MVS program management |

All may use PDS organization, but their contents and consumers differ.

---

## 32. Library Management

Library-management utilities maintain PDS members and other data-set content.

Typical operations include:

- create;
- copy;
- add a member;
- replace a member;
- delete a member;
- list members;
- reorganize a library.

The library utility should not be confused with the assembler or linkage editor.

For example:

```text
library utility
      |
      +--> stores MEMBERX in source library

assembler
      |
      +--> later reads MEMBERX
```

or:

```text
library utility
      |
      +--> stores SUBRTN object member

linkage editor
      |
      +--> later extracts SUBRTN
```

The library organizes material; another tool interprets it.

---

## 33. Program Fetch and Execution

Once a load module exists, execution becomes an MVS program-management operation.

A job step can request:

```jcl
//STEP1 EXEC PGM=MYPROG
```

Conceptually, MVS performs:

```text
EXEC PGM=MYPROG
       |
       v
search applicable program libraries
       |
       v
locate load module
       |
       v
make executable program available in virtual storage
       |
       v
establish execution environment
       |
       v
transfer control to entry point
```

The linkage editor creates the executable artifact. MVS subsequently locates and executes it.

---

## 34. Linkage Conventions: The Runtime Glue

Machine instructions explain how a branch occurs, but not how independently written routines cooperate.

That requires conventions.

Under conventional MVS assembler linkage, several general registers have customary roles:

| Register | Common role |
|---|---|
| R1 | address of parameter list |
| R13 | address of save area |
| R14 | return address |
| R15 | entry-point address and commonly return code |

These roles are conventions, not universal properties of the System/370 hardware.

They allow independently written modules to agree about:

- parameters;
- return addresses;
- saved registers;
- routine entry;
- routine return;
- return codes.

The assembler and linkage editor can connect addresses. The linkage convention determines how the code at those addresses cooperates.

---

## 35. Save Areas

A called routine normally must preserve the caller's required register environment.

MVS assembler conventions use a save area, conventionally addressed by R13.

Conceptually:

```text
CALLER SAVE AREA
        |
        +-- saved registers
        +-- linkage fields
        |
        v
      CALLER
        |
        | call
        v
      CALLEE
        |
        +--> establish/use appropriate save area
        +--> save required state
        +--> perform work
        +--> restore required state
        |
        v
      RETURN
```

A real routine must follow the exact applicable convention, but the orientation-level lesson is simple: **external symbol resolution does not itself create a valid subroutine call**. The caller and callee must also agree on runtime linkage.

---

## 36. Parameter Lists

A common MVS convention passes the address of a parameter list in R1.

Conceptually:

```text
R1
 |
 v
+----------+
| addr P1  |----> parameter 1
+----------+
| addr P2  |----> parameter 2
+----------+
| addr P3  |----> parameter 3
+----------+
```

The called program often receives addresses of parameters rather than all parameter values directly in registers.

The exact layout depends on the interface, but the R1 parameter-list convention is pervasive enough that a new MVS assembler programmer should recognize it immediately.

---

## 37. A Call Across Separately Assembled Modules

A call to an external routine involves several layers:

```text
SOURCE
    name ROUTINEB
       |
       v
ASSEMBLY
    encode call machinery
    record external reference
       |
       v
LINK-EDIT
    resolve ROUTINEB to its definition
       |
       v
RUNTIME
    establish linkage registers/parameters
    transfer control
       |
       v
CALLEE
    obey entry convention
    perform work
    return correctly
```

A successful link proves that the symbol relationship could be resolved. It does **not** prove that caller and callee use compatible parameter or save-area conventions.

---

## 38. Reentrant and Reusable Code

MVS frequently uses code that may need to be safely reused.

A routine that modifies its own instructions or permanent writable data embedded in shared program text may not be suitable where reentrancy is required.

A common organization separates reusable code from per-invocation storage:

```text
reusable program code
         |
         +--------------------+
                              |
                              v
                    invocation work area
```

This affects:

- source organization;
- register usage;
- storage allocation;
- linkage conventions;
- module attributes;
- use by MVS system components.

The detailed rules belong in a deeper MVS programming discussion, but the concept is central to systems programming.

---

## 39. Static Linkage Versus Runtime Program Management

Not every program relationship must be resolved into one permanent load-module organization by the linkage editor.

### Link-edit relationship

```text
object A + object B
       |
       v
 linkage editor
       |
       v
linked load-module organization
```

### Runtime relationship

```text
running A
   |
   +--> ask MVS to locate/load/invoke B
```

MVS provides program-management services for runtime relationships. Important names include:

- `LOAD`;
- `LINK`;
- `XCTL`;
- `ATTACH`;
- `DELETE`.

Their full semantics belong to MVS services, but a toolchain-oriented programmer needs to know where they fit.

---

## 40. `LOAD`, `LINK`, `XCTL`, `ATTACH`, and `DELETE`

At orientation level:

### `LOAD`

Makes another load module available and obtains information needed to address its entry point without making the operation simply equivalent to an ordinary source-level subroutine call.

### `LINK`

Invokes another program under MVS program management with an expected return relationship:

```text
A -> LINK B -> B executes -> return to A
```

### `XCTL`

Transfers control to another program without retaining the ordinary call-and-return relationship to the transferring program:

```text
A -> XCTL B
```

### `ATTACH`

Creates another task to execute work. This is therefore also a task-management concept.

### `DELETE`

Releases an appropriate loaded-program relationship when applicable.

These are **runtime operations**. They are not linkage-editor external-symbol resolution merely because some of them concern program linkage.

---

## 41. Overlays, Chaining, and Virtual Storage

Historically, programs often had to operate under tight storage limits. Several different mechanisms can address that problem and should not be confused.

### Linkage-editor overlays

A program can be organized so that selected portions do not need to occupy storage simultaneously. The linkage editor can participate in constructing such an organization.

### Program chaining

One executing program can explicitly transfer to another.

### MVS virtual-storage management

MVS manages virtual storage and the residency of pages in real storage.

These are distinct mechanisms. Ordinary paging or swapping by MVS is not the same thing as a programmer-defined overlay structure.

---

## 42. MVS Services and Assembler Macros

MVS exposes many programming interfaces through assembler macros.

Representative names include:

```text
OPEN
CLOSE
GET
PUT
GETMAIN
FREEMAIN
LOAD
LINK
XCTL
ATTACH
```

It is important not to mistake these for System/370 machine instructions.

The conceptual stack is:

```text
assembler source
      |
      | MVS macro
      v
assembler macro expansion
      |
      v
generated instructions / control structures
      |
      v
MVS runtime interface
      |
      v
supervisor / system components
```

The macro is a programmer-facing assembly interface. The operating-system service exists below it.

---

## 43. SVCs and the Supervisor Boundary

System/370 provides the **SVC** instruction as a mechanism for requesting supervisor services.

MVS macros may generate an SVC or otherwise arrange access to system services.

The useful distinction is:

```text
MVS macro name
       |
       v
assembly-time programming interface

macro-generated code/control blocks
       |
       v
runtime calling interface

SVC or other system mechanism
       |
       v
MVS implementation
```

A macro should not be assumed to correspond trivially to exactly one SVC, nor should its expansion be confused with the service implementation itself.

---

## 44. Access Methods as an Example

Data-set I/O illustrates how the layers fit together.

Assembler source may contain operations conceptually resembling:

```asm
         OPEN  (...)
         GET   ...
         PUT   ...
         CLOSE (...)
```

The assembler processes these as macros. At runtime, the generated program interacts with MVS access methods and system services.

```text
programmer
   |
   v
assembler macro interface
   |
   v
generated program
   |
   v
MVS access method
   |
   v
I/O subsystem
```

IFOX turns the symbolic programming interface into executable material; MVS provides the runtime service.

---

## 45. There Is No Implicit Modern Language Runtime

A modern high-level-language programmer often expects substantial runtime machinery to accompany a small program.

Raw assembler is different.

IFOX primarily supplies:

- symbolic translation;
- storage construction;
- macro processing;
- object-module construction.

The programmer, libraries, conventions, and operating system provide such things as:

- entry linkage;
- save areas;
- parameter conventions;
- dynamic storage;
- I/O;
- program termination;
- recovery and error handling.

Reusable routines may form libraries, but they should not be confused with an intrinsic assembler runtime environment.

---

## 46. Program Return and Condition Codes

A routine normally returns control according to the applicable MVS linkage convention.

R15 is conventionally used to communicate a return code.

Conceptually:

```text
program work
     |
     v
set return code
     |
     v
restore required caller state
     |
     v
branch to return address
```

For a program invoked as a job step, the program return code becomes meaningful at the job-control level.

```text
assembler program
      |
      | R15
      v
program return code
      |
      v
step condition code
      |
      v
JCL decision making
```

This is an important connection between assembler linkage conventions and batch processing.

---

## 47. ABENDs and Exceptional Termination

Not all programs return normally.

Abnormal termination can result from such conditions as:

- invalid storage references;
- invalid instructions;
- arithmetic exceptions;
- explicit ABEND requests;
- failures detected by MVS services;
- environmental errors.

A programmer diagnosing an ABEND commonly correlates:

```text
ABEND information
       +
register contents
       +
PSW / failing address
       +
storage dump
       +
assembler listing
       +
linkage map
       =
source-level understanding
```

This is why listings and linkage maps are important engineering artifacts rather than disposable build output.

---

## 48. Postmortem Debugging

Interactive source-level debugging is not the only important debugging model in this environment. Systems programmers must be comfortable with **postmortem debugging**.

A typical procedure is:

```text
1. program ABENDs
2. identify the ABEND/interruption information
3. obtain the failing instruction address
4. inspect registers and PSW
5. determine the containing module/control section
6. use the linkage map to establish module layout
7. use the assembler listing to locate the instruction
8. inspect nearby generated code and storage
9. reconstruct program state
```

The build artifacts are therefore part of the runtime diagnostic environment.

---

## 49. The Linkage Map

A linkage-editor map describes how the linked program was organized.

Depending on options, useful information can include:

- included control sections;
- section lengths;
- assigned locations;
- entry information;
- symbols;
- selected library members;
- unresolved or duplicate references.

A useful division of labor is:

```text
assembler listing:
    What did IFOX generate from this source?

linkage map:
    How did the linkage editor organize the assembled pieces?

dump:
    What was the execution state when the program failed?
```

Together they provide a path from source to failure.

---

## 50. A Separately Assembled Example

Consider two conceptual modules.

### Module A

```asm
PROGA    CSECT
         USING PROGA,12
         ...
         EXTRN SUBA
         ...
         * establish normal linkage
         * invoke SUBA
         ...
         END
```

### Module B

```asm
SUBA     CSECT
         USING SUBA,12
         ...
         * establish normal entry linkage
         * perform work
         * return
         ...
         END
```

IFOX assembles them independently:

```text
PROGA source                 SUBA source
     |                            |
     v                            v
   IFOX                         IFOX
     |                            |
     v                            v
PROGA object                SUBA object
     |                            |
     +-------------+--------------+
                   |
                   v
             linkage editor
                   |
                   v
              load module
```

`PROGA` does not need to know `SUBA`'s final execution address during its own assembly. It needs a symbolic external relationship that the linkage editor can resolve.

---

## 51. A Typical Program Shape

A small assembler program often has a conceptual organization resembling:

```asm
MYPROG   CSECT
         * establish entry conventions

         USING MYPROG,12

         * save caller state
         * establish base register
         * establish save area if required

         * program logic
         ...

         * set return code
         * restore caller state
         * return

         * constants
         ...

         * working storage, if appropriate
         ...

         END   MYPROG
```

Real programs vary, particularly when reentrancy or separately allocated work areas are involved, but this shape exposes the principal concerns:

- section definition;
- entry linkage;
- addressability;
- executable instructions;
- data;
- exit linkage;
- assembly termination.

---

## 52. Assemble-Link-Go as Three Separate Tests

### Stage 1 — Assembly

Input:

```text
assembler source
```

Outputs:

```text
object module
assembly listing
assembler return code
```

Questions include:

- Is the syntax valid?
- Are symbols defined appropriately?
- Is storage addressable?
- Did macros expand as intended?
- Were serious diagnostics issued?

### Stage 2 — Link-edit

Inputs:

```text
object modules
object libraries
linkage-editor control
```

Outputs:

```text
load module
linkage map
linkage-editor return code
```

Questions include:

- Were external references resolved?
- Were intended library members selected?
- Is the entry point correct?
- Is the module organized as intended?

### Stage 3 — Execute

Inputs:

```text
load module
runtime DD statements
parameters
MVS environment
```

Outputs:

```text
program results
return code
or ABEND information
```

Questions include:

- Was the program found?
- Was its runtime environment correct?
- Did it obey linkage conventions?
- Did MVS services succeed?
- Did it terminate normally?

---

## 53. Temporary and Permanent Build Products

During development, object code and load modules can be passed between job steps using temporary data sets.

Conceptually:

```text
ASM step
   |
   +--> temporary object data set
              |
              v
          LKED step
              |
              +--> temporary load library/module
                         |
                         v
                      GO step
```

For reusable software, object modules may instead be retained in object libraries and load modules installed in persistent load libraries.

This roughly corresponds to the distinction between a temporary build artifact and an installed reusable artifact.

---

## 54. Cataloged Procedures

MVS installations commonly define cataloged procedures for standard language-processing sequences.

A procedure can hide:

- assembler program names;
- standard DD statements;
- temporary data-set definitions;
- linkage-editor invocation;
- standard libraries;
- listing destinations;
- common options.

The convenience is substantial, but a programmer should be able to mentally expand the procedure into its underlying stages whenever a problem occurs.

---

## 55. IFOX Options and Listing Weight

IFOX behavior can be controlled by assembler options. Exact option names and availability should be taken from the assembler documentation for the installed version.

Common concerns include whether to produce or display:

- object output;
- source listings;
- macro-generated statements;
- symbol cross-references;
- external-symbol information;
- relocation information;
- differing levels of diagnostic detail.

For practical development it is useful to think informally in terms of listing weight:

```text
light
    routine successful builds

medium
    source plus useful symbols/cross-reference information

heavy
    detailed investigation of generated code, macros,
    symbols, relocation, or linkage
```

These are workflow concepts rather than formal IFOX option names.

---

## 56. Why Macro Listings Become Large

A single macro invocation can generate many assembler statements.

```asm
         SOMEOSMACRO ...
```

may conceptually expand into:

```text
macro invocation
     |
     +--> generated declaration
     +--> generated instruction
     +--> generated instruction
     +--> generated constant
     +--> generated instruction
     +--> ...
```

A listing configured to show macro expansion can therefore be much larger than the original source.

This is extremely useful when diagnosing generated code but unnecessary for every successful assembly.

---

## 57. Object Decks and Historical Media

Historically, assembler object modules could be represented as card-oriented object decks. Even when the same logical records are stored in disk data sets, terminology and formats retain that heritage.

Keep three artifacts distinct:

```text
source deck
    symbolic assembler statements

object deck/module
    generated text plus linkage and relocation information

load module
    linkage-edited executable representation
```

A load module is not merely an object deck copied into another data set.

---

## 58. Names Exist in Different Toolchain Domains

One program may have several relevant names:

- source PDS member name;
- CSECT name;
- external symbol name;
- object-library member name;
- load-module member name;
- entry-point symbol;
- `PGM=` name in JCL.

Programmers often make these identical for convenience, which can conceal the fact that they belong to different namespaces and stages.

When diagnosing a naming problem, ask:

> Which toolchain stage owns this name?

---

## 59. Addressability Versus Relocation

These concepts are related to addresses but solve different problems.

### Addressability

Can a generated System/370 instruction represent the desired storage operand using an available base register and displacement?

This is primarily an assembly-time issue involving such concepts as `USING`, base registers, and displacement range.

### Relocation

Can address-dependent contents be adjusted when control sections are placed relative to one another?

This is primarily an object-module and linkage-editor issue.

```text
USING / base displacement
          |
          v
Can this instruction address the operand?

RLD / linkage processing
          |
          v
Can this address-dependent field be relocated?
```

A program can have perfectly valid relocation semantics and still fail assembly because an operand is not addressable with the current base-register assumptions.

---

## 60. Assembly Time, Link-Edit Time, and Runtime

A reliable way to reason about assembler systems is to assign every operation to its proper time domain.

| Time | Representative operations |
|---|---|
| Assembly time | macro expansion, `COPY`, `EQU`, conditional assembly, instruction encoding, `USING` assumptions |
| Link-edit time | external-symbol resolution, object-library extraction, section organization, relocation processing |
| Load/runtime | program fetch, register contents, parameter lists, dynamic loading, MVS service calls |

Examples:

- `COPY X` does not perform a runtime operation.
- `EXTRN X` does not load or execute `X`.
- `USING X,12` does not place `X` into R12.
- runtime `LINK` is not the same operation as linkage editing.

Many assembler misunderstandings are really **time-domain errors**.

---

## 61. Text Inclusion Versus Object Inclusion

This distinction deserves explicit emphasis.

### Text inclusion

```text
source A
   |
   +-- COPY B
          |
          v
      source text B
          |
          v
        IFOX
```

`B` becomes part of the source being assembled.

### Object inclusion

```text
object A says "need B"
          |
          v
    linkage editor
          |
          v
   find object B in library
```

`B` has already been assembled separately.

The first mechanism creates one assembly from more source. The second combines independently assembled modules.

---

## 62. Static Inclusion Versus Dynamic Invocation

A further distinction is required at runtime.

```text
SOURCE INCLUSION
COPY
   -> happens during assembly

OBJECT INCLUSION
linkage-editor library search
   -> happens during link-edit

DYNAMIC PROGRAM MANAGEMENT
LOAD / LINK / XCTL / ATTACH
   -> happens while programs execute
```

These three mechanisms may all be described informally as "bringing in another routine," but they occur at completely different stages and produce different program organizations.

---

## 63. What the Library Manager Does — and Does Not Do

A library utility manages stored members. It can create, copy, replace, delete, list, or reorganize them.

It does not itself mean that source has been included in an assembly or that an object module has been included in a link-edit.

The division of responsibility is:

```text
LIBRARY UTILITY
    stores and manages members

IFOX
    consumes source and macro members

LINKAGE EDITOR
    consumes object modules and object-library members

MVS PROGRAM MANAGEMENT
    consumes executable load modules
```

This separation is useful when thinking about historical build systems.

---

## 64. Programmer-Supplied Versus System-Supplied Material

A typical assembly may depend on material from several sources:

```text
programmer source
      |
      +-- programmer COPY members
      +-- programmer macros
      +-- installation macros
      +-- MVS system macros
      |
      v
     IFOX
```

Likewise, a link-edit may combine:

```text
programmer object modules
      |
      +-- application object libraries
      +-- language/runtime support modules
      +-- system-supplied modules where applicable
      |
      v
 linkage editor
```

The programmer needs to understand the applicable search order because two libraries can contain members or symbols with the same names.

---

## 65. Search Order Matters

Whenever multiple libraries are available, their search order can affect which member is found.

This can matter for:

- macro libraries;
- copied source libraries;
- object libraries;
- load libraries.

A program may therefore assemble, link, or execute differently if library concatenations change.

For diagnosis, record not merely the member name but also **which library supplied it**.

---

## 66. Separate Assembly as an Engineering Technique

Separate assembly is not only a way to reduce build time. It establishes explicit module boundaries.

Advantages include:

- independently maintained routines;
- reusable object libraries;
- clearer external interfaces;
- replacement of one implementation without reassembling all callers;
- sharing common routines among programs.

The cost is that interfaces must be disciplined:

- symbol names must agree;
- calling conventions must agree;
- parameter layouts must agree;
- register usage must agree;
- data structures shared across modules must agree.

The linkage editor verifies names and relocation relationships. It generally cannot verify the semantic correctness of the calling convention.

---

## 67. The ABI Concept in MVS Terms

Modern programmers often use the term **ABI**, or application binary interface.

For MVS assembler work, the corresponding practical concerns include:

- entry-register conventions;
- parameter-list conventions;
- save-area format;
- register preservation;
- return-address convention;
- return-code convention;
- external symbol naming;
- shared control-block layouts.

MVS documentation may describe these through linkage conventions rather than presenting them as one modern ABI specification, but the engineering role is similar.

---

## 68. Inter-Language Linkage

Assembler routines can interact with programs written in higher-level languages, but the assembler programmer must obey the language's calling conventions and runtime expectations.

Potential differences include:

- parameter representation;
- by-reference versus by-value conventions;
- character-string representation;
- return values;
- save-area use;
- initialization requirements;
- external symbol naming.

The fact that the linkage editor can resolve a symbol does not prove that the two languages agree on the binary interface.

---

## 69. Program Organization and Writable Storage

A simple program may place code and writable storage in the same general assembly organization. More reusable system code often separates them conceptually.

```text
program text
    |
    +-- constants
    +-- read-only tables
    +-- executable instructions

per-use storage
    |
    +-- counters
    +-- buffers
    +-- temporary pointers
    +-- work fields
```

This separation becomes increasingly important for reentrancy, task sharing, and system-level modules.

---

## 70. Generated Control Blocks

MVS programming frequently depends on structured control blocks.

Some may be:

- declared directly in source;
- generated by macros;
- mapped using system-supplied mapping macros;
- dynamically obtained at runtime.

For the assembler programmer, these are byte-level structures with symbolic field names and defined layouts.

The toolchain relationship is:

```text
mapping/generation macro
          |
          v
assembler symbols and storage layout
          |
          v
runtime control block interpreted by program/MVS
```

This is another example of an assembly-time facility describing a runtime data structure.

---

## 71. The Role of the `END` Statement

The assembler must be told where the source assembly ends.

An `END` statement terminates the assembly and can participate in identifying the intended entry symbol according to the source organization and assembler rules.

Conceptually:

```asm
         ...
         ...
         END   MYPROG
```

Do not confuse:

- ending the **assembly**;
- defining a **control section**;
- returning from the **executing program**.

These occur in different domains.

---

## 72. Listings as Reproducibility Evidence

For systems work, a useful assembly listing records more than whether the source succeeded.

It can preserve evidence of:

- the exact source statements seen by IFOX;
- macro expansion;
- selected assembler options;
- assigned addresses;
- generated object bytes;
- symbol values;
- diagnostics.

A linkage map similarly records the organization chosen by the linkage editor.

For historical-system reconstruction and maintenance, retaining these artifacts can make a build much easier to reproduce and diagnose later.

---

## 73. A Practical Diagnostic Hierarchy

When a program fails, first determine **which toolchain stage failed**.

### Assembly failure

Look first at:

- IFOX diagnostics;
- statement numbers;
- generated source around macros;
- symbol table;
- addressability information.

### Link-edit failure

Look first at:

- unresolved external symbols;
- duplicate definitions;
- object-library search results;
- entry-point information;
- linkage map;
- linkage-editor return code.

### Program-fetch failure

Look first at:

- requested `PGM=` name;
- load-library concatenation;
- load-module member existence;
- module validity and authorization requirements where applicable.

### Runtime failure

Look first at:

- ABEND code;
- PSW;
- registers;
- dump;
- linkage conventions;
- runtime DD statements;
- MVS service return codes;
- assembler listing and linkage map.

This stage-oriented approach avoids debugging the wrong problem.

---

## 74. Common Conceptual Mistakes

### Mistake 1: Treating `USING` as a register load

It is an assembler addressability declaration. The program must establish the register contents separately.

### Mistake 2: Treating an MVS macro as a CPU instruction

Macros are expanded by the assembler; the generated code implements the runtime interface.

### Mistake 3: Treating an object module as an executable load module

The object module still requires linkage processing.

### Mistake 4: Assuming a resolved external symbol means a valid call

The caller and callee must also obey compatible linkage and parameter conventions.

### Mistake 5: Confusing `COPY` with linkage-editor library inclusion

`COPY` brings in source at assembly time. Linkage-editor library search brings in object modules at link-edit time.

### Mistake 6: Confusing linkage editing with runtime `LINK`

The linkage editor constructs a load module. The MVS `LINK` service invokes another program during execution.

### Mistake 7: Confusing overlays with ordinary MVS paging

An overlay is explicit program organization. Paging is operating-system virtual-storage management.

### Mistake 8: Assuming all PDS members contain the same kind of thing

Source, macro, object, and load libraries can all be PDSs while containing very different representations.

---

## 75. Mapping the Toolchain to Modern Concepts

For a programmer familiar with contemporary Unix-like development, the following analogies are useful but approximate:

| MVS / IFOX concept | Rough modern analogy |
|---|---|
| IFOX source | `.s` / `.asm` source |
| IFOX | assembler |
| object module | `.o` file |
| external symbol | linker symbol |
| object library | static object archive/library |
| linkage editor | linker |
| load module | executable binary |
| load library PDS | executable/program library |
| program fetch | executable loader/program manager |
| `COPY` member | source include |
| macro library | assembler macro/include library |
| linkage map | linker map |
| assembler listing | assembler listing/disassembly-oriented build artifact |
| save-area convention | calling-convention stack/frame discipline, approximately |

The analogy breaks down if pushed too far. MVS data-set organization, PDS members, program management, and linkage conventions have their own semantics.

---

## 76. A Compact End-to-End Example

Consider a source member `HELLOWOR` containing an assembler program.

### Step 1: Assemble

```text
HELLOWOR source
      |
      +-- system macros as required
      |
      v
     IFOX
      |
      +--> assembly listing
      |
      +--> HELLOWOR object module
```

The listing tells the programmer what IFOX generated and whether errors occurred.

### Step 2: Link-edit

```text
HELLOWOR object
       |
       +-- required object-library members
       |
       v
 linkage editor
       |
       +--> linkage map
       |
       +--> HELLOWOR load module
```

The linkage editor resolves external symbols and constructs executable organization.

### Step 3: Execute

```text
EXEC PGM=HELLOWOR
       |
       v
MVS locates load module
       |
       v
program fetch
       |
       v
entry linkage established
       |
       v
HELLOWOR executes
       |
       +--> MVS services as required
       |
       v
return code / normal termination
```

This three-stage picture is the basic toolchain model to retain.

---

## 77. Toolchain Boundaries

It is useful to state explicitly what each major component **does not** do.

### IFOX does not normally:

- decide the final relationship among all separately assembled modules;
- resolve every external symbol by itself;
- provide a complete runtime operating environment;
- fetch executable programs at runtime.

### The linkage editor does not:

- execute assembler macros;
- interpret ordinary assembler source;
- enforce calling-convention semantics;
- perform the runtime work of `LINK`, `XCTL`, or `ATTACH`.

### The library utility does not:

- assemble source merely by storing it;
- link object modules merely by storing them;
- execute load modules.

### MVS program management does not:

- replace the assembler's source translation;
- replace the linkage editor's ordinary external-symbol resolution.

Keeping these boundaries clear makes the entire environment easier to reason about.

---

## 78. What a New Programmer Should Learn First

A productive learning sequence is:

1. Read and write correctly formatted IFOX source statements.
2. Understand labels, machine instructions, `DC`, `DS`, and `EQU`.
3. Understand CSECTs and the location counter.
4. Learn base-displacement addressing and `USING`/`DROP`.
5. Learn to read an assembly listing.
6. Understand macros and the difference between macro expansion and CPU execution.
7. Understand object modules, external symbols, and relocation conceptually.
8. Understand the linkage editor and load modules.
9. Learn the R1/R13/R14/R15 linkage conventions and save areas.
10. Learn the common MVS macros and services needed by the program.
11. Learn to interpret linkage maps, return codes, ABENDs, and dumps.
12. Only then move into advanced linkage-editor structures, reentrancy details, overlays, or sophisticated macro programming as needed.

This sequence follows the path from source text to executing system program.

---

## 79. The Core Mental Model

A new programmer should be able to reconstruct this diagram from memory:

```text
                         ASSEMBLY TIME

 source program -------------------------------+
      |                                        |
      +--> COPY/source libraries               |
      +--> macro libraries                     |
      |                                        |
      v                                        |
     IFOX                                      |
      |                                        |
      +--> listing                             |
      |                                        |
      v                                        |
 object module                                 |
                                               |
                         LINK-EDIT TIME         |
                                               |
 object module(s) -----------------------------+
      |
      +--> object libraries
      |
      v
 linkage editor
      |
      +--> map / diagnostics
      |
      v
 load module
      |
      v
 load library
      |
                         LOAD / RUNTIME
      |
      v
 MVS program fetch
      |
      v
 executing program
      |
      +--> linkage conventions
      +--> parameters and save areas
      +--> MVS macros/services
      +--> dynamically managed programs
      +--> data sets and devices
      |
      v
 return code or ABEND
```

The most important boundaries are:

```text
SOURCE  ->  OBJECT  ->  LOAD MODULE  ->  EXECUTION
   ^           ^             ^               ^
   |           |             |               |
 IFOX       linkage       program         runtime
            editor         library        environment
```

---

## 80. Glossary

**ABEND**  
Abnormal termination of a program or task.

**Addressability**  
The ability of an instruction to represent the address of an operand using the available System/370 addressing form, especially base register plus displacement.

**Assembler instruction**  
A statement interpreted by IFOX to control assembly rather than executed directly by the CPU.

**Cataloged procedure**  
Stored JCL that packages a commonly used sequence of job steps and DD statements.

**Control section (CSECT)**  
A named relocatable section of code or data.

**COPY member**  
Source statements incorporated into an assembly from a library member.

**Entry point**  
A location at which control may enter a program or routine; in the load-module context, the location at which execution begins.

**ESD**  
Object-module information describing external symbols and sections.

**External definition**  
A symbol made available to other object modules during linkage editing.

**External reference**  
A reference to a symbol expected to be defined outside the current assembly.

**IFOX**  
The IBM assembler used here to translate System/370 assembler source into object modules.

**Linkage editor**  
The MVS program that combines object modules, resolves external symbols, processes relocation, and constructs load modules.

**Linkage map**  
A linkage-editor report describing the organization of the resulting program.

**Literal pool**  
Assembler-generated storage containing literal values requested by instructions.

**Load library**  
A library, commonly a PDS, containing executable load modules.

**Load module**  
The executable program representation produced by linkage editing and consumed by MVS program management.

**Macro**  
An assembly-time facility that generates assembler statements from a parameterized invocation.

**Object library**  
A library containing object modules available for selection by the linkage editor.

**Object module**  
Relocatable assembler output containing generated text and information needed for linkage editing.

**PDS**  
Partitioned data set; an MVS data-set organization containing named members.

**Program fetch**  
MVS program-management processing that locates and makes a load module available for execution.

**Relocation**  
Adjustment of address-dependent program contents when relocatable sections are assigned their linked relationships.

**RLD**  
Object-module relocation information used by the linkage editor.

**Save area**  
Storage used by conventional MVS assembler linkage to preserve registers and maintain calling relationships.

**SVC**  
Supervisor Call; a System/370 instruction and mechanism used to request supervisor services.

**TXT**  
Object-module records carrying generated program text.

**`USING`**  
An assembler instruction declaring an assumed base-register relationship for address calculation; it does not load the register.

---

## 81. Final Orientation

For a general-purpose or systems programmer, the IFOX environment becomes much simpler once it is viewed as several cooperating systems rather than one monolithic assembler command.

IFOX owns the transformation:

```text
symbolic source -> relocatable object module
```

The linkage editor owns:

```text
object modules -> resolved executable load-module organization
```

MVS program management owns:

```text
load module -> executing program
```

Libraries supply reusable material at each appropriate stage, while MVS linkage conventions define how separately written routines cooperate once execution begins.

The essential distinctions to retain are:

- machine instructions versus assembler instructions;
- macros versus runtime services;
- source inclusion versus object-library inclusion;
- object modules versus load modules;
- addressability versus relocation;
- linkage editing versus runtime program linkage;
- symbol resolution versus calling-convention correctness;
- assembly-time, link-edit-time, and runtime operations.

With those concepts in place, the details of IFOX syntax, linkage-editor control statements, MVS macros, access methods, and dump analysis fit into a coherent toolchain rather than appearing as unrelated historical mechanisms.
