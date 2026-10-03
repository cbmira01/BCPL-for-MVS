
# Programmer Orientation Briefings for System/370, MVS 3.8J, and Hercules

## About This Directory

This directory contains technical orientation briefings prepared for the
**BCPL for MVS** project.

They are intended primarily for general-purpose and systems programmers
approaching IBM System/370 and MVS 3.8J from a modern computing
background. Their purpose is to establish useful conceptual models,
introduce terminology, show how the major pieces fit together, and
identify subjects for deeper research.

These are **briefings, not reference manuals**. They should help a
reader become oriented well enough to use the original documentation
effectively.

## Briefings

| Document | Subject |
| --- | --- |
| [`BCPL-history-and-porting.md`](BCPL-history-and-porting.md) | Brief history of BCPL, its uses and implementations, and a human-oriented sketch of the MVS porting/bootstrap process |
| [`System_370-briefing.md`](System_370-briefing.md) | System/370 architecture from the programmer's viewpoint |
| [`MVS-3_8-briefing.md`](MVS-3_8-briefing.md) | MVS 3.8 organization, services, and programming environment |
| [`Hercules-briefing.md`](Hercules-briefing.md) | Hercules architecture, configuration, operation, devices, interfaces, and tooling |
| [`IFOX-assembler-toolchain-briefing.md`](IFOX-assembler-toolchain-briefing.md) | IFOX assembler, linkage editor, libraries, listings, and development workflow |
| [`JCL-for-the-programmer.md`](JCL-for-the-programmer.md) | Programmer-oriented JCL: JOB, EXEC, DD, procedures, data sets, and job output |
| [`MVS-access-methods.md`](MVS-access-methods.md) | Data sets, record formats, DCBs, QSAM, BSAM, BPAM, and I/O |
| [`MVS-program-execution.md`](MVS-program-execution.md) | Register conventions, save areas, parameters, linkage, and program-management services |
| [`MVS-debugging.md`](MVS-debugging.md) | Condition codes, ABENDs, PSWs, registers, dumps, listings, and link maps |
| [`S370-object-and-load-modules.md`](S370-object-and-load-modules.md) | Object modules, ESD/TXT/RLD/END, relocation, linkage editing, and load modules |
| [`MVS-storage-and-addressing.md`](MVS-storage-and-addressing.md) | Virtual storage, address spaces, regions, tasks, storage protection, and addressability |
| [`MVS-system-programming-interfaces.md`](MVS-system-programming-interfaces.md) | Macros, SVCs, control blocks, task services, synchronization, recovery, and EXCP |
| [`IBM-data-representation.md`](IBM-data-representation.md) | EBCDIC, integers, addresses, decimal data, floating point, records, and host/guest representation |

Some overlap is intentional. A subject such as program linkage appears
differently when viewed from the architecture, assembler,
linkage-editor, and operating-system layers.

## Suggested Reading Order

There is no required order, but a new reader might use:

``` text
BCPL history and porting
    |
    v
System/370
    |
    v
MVS 3.8
    |
    +----> Hercules
    |
    v
IFOX assembler toolchain
    |
    v
JCL
    |
    +----> Data sets and access methods
    +----> Program execution and linkage
    +----> Object and load modules
    +----> Storage and addressing
    +----> Data representation
    +----> Debugging
    |
    v
MVS system-programming interfaces
```

The BCPL history/porting note explains why the project needs these
machine and operating-system topics. The next four establish the broad
environment. The others can increasingly be used as topical references.

## Provenance

These briefings were **generated with the assistance of OpenAI ChatGPT**
for the BCPL for MVS project.

They resulted from iterative conversations specifying the desired
historical scope, organization, level of detail, and emphasis on
general-purpose and systems programming. Some material was refined in
response to practical work with MVS 3.8J under Hercules.

They are therefore **secondary, AI-generated explanatory material**.
They are not authoritative transcriptions of IBM documentation.

AI-generated material can contain errors, omit qualifications, confuse
nearby software releases, or inadvertently apply later MVS concepts to
MVS 3.8J. Details should be verified before they are relied upon for
implementation.

Verification is particularly important for:

-   exact assembler syntax and macro operands;
-   control-block layouts;
-   object- and load-module formats;
-   system-service calling conventions;
-   ABEND and message interpretation;
-   device characteristics;
-   authorization requirements;
-   release-specific behavior.

## Historical Scope

Unless otherwise stated, the intended environment is approximately:

``` text
IBM System/370
OS/VS2 MVS Release 3.8J
JES2
IFOX assembler
Hercules
MVS 3.8J Turnkey/TK5
```

Later MVS/XA, MVS/ESA, OS/390, and z/OS documentation can illuminate
concepts that survived into later systems, but should be used
cautiously. Addressing, interfaces, control blocks, utilities, and
implementation details changed substantially.

For this project, contemporary System/370 and OS/VS2 documentation
should normally take precedence.

## Primary Documentation

The most authoritative sources are the original IBM manuals.
Particularly useful families include:

-   **IBM System/370 Principles of Operation**
-   **IBM System/370 System Summary**
-   **OS/VS2 MVS Overview**
-   **OS/VS2 MVS JCL**
-   **OS/VS2 MVS Data Management**
-   **OS/VS2 MVS Supervisor Services and Macro Instructions**
-   **OS/VS2 MVS System Programming Library**
-   **OS/VS2 MVS Message Library**
-   assembler language and assembler programmer documentation
-   linkage-editor and loader documentation
-   manuals for the particular DASD, tape, printer, card,
    communications, and channel devices involved

IBM publication numbers are excellent search keys. Once a number such as
`GA22-...`, `GC28-...`, or `GY28-...` is known, searching for that
number often locates the correct edition more reliably than title
searches.

Always check the edition and applicability statement near the front of
an IBM manual.

## Online Historical Archives

### Bitsavers

**Bitsavers** is one of the principal repositories of historical
computer documentation.

<https://bitsavers.org/>

Its IBM System/370 archive contains architecture, OS/VS, MVS, hardware,
device, and programming documentation:

<https://bitsavers.org/pdf/ibm/370/>

Bitsavers also preserves IBM bibliographies. These can be especially
useful for discovering the publication number and proper title of a
manual before searching for the manual itself.

### Internet Archive

The **Internet Archive** contains scans of IBM manuals, books, technical
publications, and other historical computing material:

<https://archive.org/>

Searching by exact IBM publication number is often effective. Its
holdings can complement Bitsavers when a particular edition is absent
from one collection.

### CBT Tape

The **CBT Tape** site is a long-running repository of IBM mainframe
community software and historical material:

<https://www.cbttape.org/>

Its MVS 3.8J material is particularly relevant:

<https://www.cbttape.org/mvs38.htm>

CBT Tape becomes especially useful when research moves from IBM manuals
into community utilities, modifications, source code, and practical MVS
knowledge.

### MVS 3.8J Turnkey 5

The **MVS 3.8J Turnkey 5** distribution supplies a configured MVS 3.8J
environment for Hercules:

<https://www.prince-webdesign.nl/tk5>

The documentation supplied with TK5 is important whenever behavior is
specific to the Turnkey installation rather than stock MVS.

Keep these layers distinct:

``` text
System/370 behavior
IBM MVS 3.8J behavior
Hercules behavior
TK5 customization
local project configuration
```

A fact about one layer does not necessarily describe another.

### Hercules

For emulator-specific behavior, consult the Hercules project
documentation:

<https://www.hercules-390.org/>

Hercules documentation is appropriate for subjects such as configuration
statements, operator commands, emulated devices, virtual DASD and tape
formats, networking, tracing, and host integration.

IBM hardware manuals describe the machines and devices being emulated;
Hercules documentation describes the emulator. Low-level investigations
may require both.

## Other Useful Sources

Historical systems research often requires combining several forms of
evidence:

``` text
IBM architecture manual
        +
IBM operating-system manual
        +
IBM language or device manual
        +
Hercules documentation
        +
Turnkey documentation
        +
experiment on the reconstructed system
```

Other useful sources include SHARE proceedings, IBM technical
newsletters, program logic manuals, archived university documentation,
source code distributed with MVS 3.8J, Hercules source code, surviving
assembler programs and utilities, and contemporary textbooks.

Modern web pages and discussions can be excellent aids for locating
terminology and sources, but implementation decisions should preferably
be traced to primary documentation or verified experimentally.

## Using These Briefings

The briefings are intended to answer questions such as:

-   What is this concept or subsystem?
-   Why does it exist?
-   How does it relate to the rest of the system?
-   What terminology should I know before reading the IBM manual?
-   Which layer of the system am I dealing with?
-   What should I research next?

They are less appropriate as the final authority for questions such as:

-   What exact bits occupy this control-block field?
-   What registers and parameters does this exact macro require?
-   What is the precise object-record layout?
-   What does this exact MVS message mean?

For those questions, use the briefing to identify the subject and then
move to the relevant primary reference.

## Verification by Experiment

One advantage of this project is that many historical claims can be
tested directly.

A useful research pattern is:

``` text
briefing or secondary source
        |
identify the concept
        |
find contemporary documentation
        |
construct a small experiment
        |
assemble / link / run under MVS 3.8J
        |
retain listing, job output, and observations
```

Small experiments are particularly effective for assembler behavior,
linkage conventions, object-module generation, JCL, data-set
characteristics, condition codes, ABEND behavior, access methods, and
system macros.

When documentation and observed behavior appear to disagree, first check
the exact software release, assembler version, Turnkey customization,
and Hercules configuration.

## Corrections and Maintenance

These briefings should be treated as living project documentation.

When project work shows that a statement is incorrect, ambiguous, too
broad, or specific to another release, the preferred response is to
correct the briefing and, where useful, record the primary source or
experimental evidence.

The objective is not to reproduce the IBM manuals. It is to maintain a
compact orientation library that makes those manuals---and the
reconstructed system itself---easier to approach.
