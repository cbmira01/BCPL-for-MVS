# BCPL History and Porting

## Purpose

This note is a short orientation to **BCPL** and to the process of moving a BCPL system to a new computer.

It is written for readers who may not already be familiar with compiler construction, operating-system internals, or historical systems programming. It is intentionally a sketch rather than a language manual or a detailed reconstruction log.

The second half of the document describes the approach being used by the **BCPL for MVS** project. That section is expected to evolve as the reconstruction proceeds.

---

## What BCPL is

BCPL is a small systems-programming language designed by **Martin Richards** in 1966 and first implemented at MIT in early 1967.

It grew out of Richards's experience with **CPL (Combined Programming Language)**, a much larger language developed jointly at Cambridge and London. BCPL deliberately removed many of CPL's difficult features in favor of a language that was compact, efficient, and comparatively easy to implement on new machines.

BCPL is often described as a **typeless** language. In traditional BCPL, values are machine words. A word may represent an integer, character, truth value, address, function, or some other quantity depending on how the program uses it. The language provides direct access to words, vectors, bytes, addresses, and control flow, making it suitable for low-level work without requiring every program to be written in assembler.

A useful simplified picture is:

```text
assembler
    |
    | very close to one machine
    v
BCPL
    |
    | small language, direct machine-oriented operations,
    | but intended to move between machines
    v
higher-level application languages
```

BCPL was designed particularly for work where a programmer needed more control over representation and storage than many contemporary high-level languages provided.

Martin Richards's BCPL page is a useful starting point:

<https://www.cl.cam.ac.uk/~mr10/BCPL.html>

His paper *How BCPL evolved from CPL* gives the historical background:

<https://www.cl.cam.ac.uk/~mr10/cpl2bcpl.pdf>

---

## What BCPL was used for

BCPL was designed as a language for **compiler writing and systems programming**. It was subsequently used for a much wider range of software.

Important uses included:

- compilers and compiler support programs;
- operating-system components;
- portable systems software;
- communications and networking research;
- utilities and command processors;
- experimental software systems;
- process-control and data-collection systems;
- ordinary application and demonstration programs.

One of the best-known BCPL systems was **TRIPOS**, a portable operating system begun at Cambridge in the 1970s. TRIPOS was written largely in BCPL plus small amounts of machine-dependent assembly language. It ran on several different computer families and demonstrated the practical value of writing most of a system in portable source while isolating machine-specific operations.

TRIPOS later influenced the operating-system environment of the Commodore Amiga.

BCPL also had an important influence on programming-language history. Ken Thompson's **B** language was derived in part from BCPL, and B in turn was an ancestor of **C**. BCPL is therefore part of the direct historical line leading to C and, indirectly, to much modern systems programming.

---

## Where BCPL has been implemented

BCPL was deliberately designed to be portable and has appeared on many different machines and operating systems.

The first implementation ran under **CTSS on an IBM 7094** at MIT. Richards has preserved a 1968 version of that compiler:

<https://www.cl.cam.ac.uk/~mr10/BCPLCTSS.html>

Later BCPL implementations and BCPL-based systems appeared on a wide range of machines. Historical TRIPOS material, for example, records implementations for systems including:

- PDP-11;
- Data General Nova;
- LSI-4;
- General Automation 16/220;
- IBM Series/1;
- Motorola 68000.

BCPL has also been used on larger machines and has had implementations for several 32-bit and 64-bit environments.

Richards's later **Cintcode** BCPL system is intentionally machine-independent. Versions have been used on environments including Linux, Windows, macOS, Raspberry Pi, and other systems. Experimental native-code implementations have also existed for machines such as the DEC Alpha.

The important point is not the exact list of hosts. BCPL's design assumed from the beginning that the language and most of its software should be able to survive a change of machine.

---

## The portability idea

Porting a compiler is easier if most of the compiler does not know very much about the target machine.

BCPL was organized around that idea.

A compiler can be thought of as several stages:

```text
BCPL source text
      |
      v
syntax analysis
      |
      v
intermediate representation
      |
      v
machine-dependent code generation
      |
      v
machine code or assembler
```

If the front end of the compiler produces a machine-independent intermediate language, then only the final code-generation stage must understand the new processor in detail.

BCPL systems historically used intermediate forms such as **OCODE** and **INTCODE**. This allowed compiler phases and tools to be moved between machines before a fully native compiler existed on the destination system.

This is the central bootstrap idea behind this project.

---

## What "bootstrapping" means

Suppose a compiler for language **L** is itself written in language **L**.

That is convenient once the compiler is working, but it creates an apparent problem when moving to a completely new computer:

```text
We need the compiler to compile the compiler,
but the compiler does not run here yet.
```

A **bootstrap** breaks that circular dependency.

There are several possible techniques. BCPL's historical transport mechanisms make one especially useful approach possible:

1. preserve compiler phases in a machine-independent intermediate form;
2. write a small interpreter for that intermediate form on the new machine;
3. run the preserved compiler under the interpreter;
4. use it to compile or regenerate more of the system;
5. eventually produce a native compiler for the new machine.

The first native program on a new host therefore does not have to be the entire BCPL compiler. It can be a much smaller interpreter and runtime environment.

---

## Interpreter versus native compiler

An interpreted bootstrap and a native compiler solve different problems.

An interpreter executes a portable instruction set in software:

```text
BCPL program
    |
BCPL compiler
    |
INTCODE
    |
ICINT interpreter
    |
real processor
```

A native compiler eventually removes that extra layer:

```text
BCPL program
    |
BCPL compiler
    |
System/370 instructions
    |
real processor
```

The interpreted system is usually slower, but it is extremely valuable during a port because it establishes a known execution environment before all machine-dependent compiler and runtime pieces have been reconstructed.

---

# The BCPL for MVS reconstruction

## Target environment

This project is reconstructing BCPL for:

```text
IBM System/370
OS/VS2 MVS 3.8J
JES2
Hercules
MVS 3.8J Turnkey/TK5
```

Development uses a historical BCPL transport tape associated with Martin Richards together with reconstructed System/370 assembler and MVS support code.

The long-term goal is a BCPL system that can be installed and used directly on an MVS 3.8 system, rather than requiring a modern host computer to perform compilation.

---

## The historical compiler material

The transport material includes preserved compiler phases in **INTCODE** form.

For the current reconstruction, the important compiler phases are:

```text
SYNI    syntax/front-end phase
TRNI    translation phase
CGI     INTCODE code generator
```

In simplified form, the working interpreted pipeline is:

```text
BCPL source
    |
    v
SYNI / TRNI
    |
    v
OCODE
    |
    v
CGI
    |
    v
INTCODE
    |
    v
ICINT
    |
    v
program execution
```

The compiler phases themselves are historical BCPL artifacts. What had to be supplied for MVS was an environment capable of loading and executing their INTCODE.

---

## Step 1: build an INTCODE interpreter

The first major reconstructed component is **ICINT**, an INTCODE interpreter written in System/370 assembler.

Why begin there?

Because ICINT is much smaller than a complete native BCPL compiler. Once it works, it can execute the preserved portable compiler phases.

The current validated interpreter is selected through:

```sh
tools/current-icint
```

At the time of writing the validated baseline is **ICINT V17**.

ICINT also provides the boundary between portable BCPL assumptions and MVS-specific services such as streams, storage, character representation, and program execution.

---

## Step 2: prove the historical compiler pipeline

Once ICINT could execute INTCODE reliably, the project connected the preserved compiler phases together.

A normal test now looks like:

```sh
tools/compile-and-run --results \
    "$(tools/current-icint)" \
    program.bcpl
```

The host-side tool constructs and submits the necessary MVS job, stages the preserved compiler material, runs the compiler phases, and finally executes the resulting INTCODE under ICINT.

This establishes something important: the historical compiler is not merely archived source material. It is again executable in the target MVS environment.

---

## Step 3: reconstruct the portable runtime

Compiling source code is not enough. Programs also expect library and runtime services.

Examples already reconstructed or exercised include:

```text
formatted output
character and stream I/O
GETVEC / FREEVEC storage allocation
coroutines
string and memory utilities
integer and character utilities
numeric conversion
line-oriented I/O
```

Portable services are preferably written in BCPL. Machine-dependent operations remain below them.

For example:

```text
portable BCPL coroutine library
        |
        v
machine-dependent CHANGECO primitive
```

This separation is fundamental to the port. It lets the portable library survive when the interpreter is eventually replaced by native System/370 code.

See:

- [`../library/README.md`](../library/README.md)
- [`../library/GLOBALS.md`](../library/GLOBALS.md)

---

## Step 4: use the BCPL GLOBAL vector as the linkage mechanism

BCPL software historically relies heavily on its **GLOBAL vector**.

A module associates a symbolic name with a numbered global slot. Separately compiled modules can then rendezvous through those agreed positions.

Conceptually:

```text
module A                     module B
--------                     --------
RAND : global 97   <------>  call global 97
```

This reduces dependence on a sophisticated native linker and was particularly useful for software intended to move between very different operating systems.

The current reconstruction continues to use this mechanism for separately compiled BCPL library modules.

---

## Step 5: reconstruct native System/370 code generation

The interpreted system is a bootstrap platform, not the final destination.

The next major compiler milestone is a BCPL code generator that translates the compiler's machine-independent representation into **System/370 assembler or object code**.

The intended direction is approximately:

```text
portable SYN/TRN compiler phases
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
IFOX assembler
             |
             v
native MVS load module
```

This is where many target-specific decisions become unavoidable:

- register use;
- calling conventions;
- base-register management;
- stack/frame layout;
- byte and word addressing;
- external linkage;
- runtime entry points;
- MVS program and data-set services.

The existing interpreted environment allows these decisions to be tested against working BCPL programs rather than guessed in isolation.

---

## Step 6: reconstruct the native runtime boundary

Historical native BCPL systems required a small layer of machine- and operating-system-specific support.

In the surviving MVS material this responsibility is associated in part with **BCPLMAIN** and related runtime services.

The exact contract is still being reconstructed.

Rather than attempt to invent BCPLMAIN all at once, this project is recovering its requirements incrementally from:

- surviving source and documentation;
- compiler-generated code;
- historical library code;
- interpreter behavior;
- small System/370 experiments;
- actual MVS execution results.

The working principle is:

```text
reconstruct only what evidence or running software shows is required
```

This helps avoid accidentally importing assumptions from later BCPL systems or unrelated operating systems.

---

## Step 7: compile the compiler itself

A major bootstrap milestone will be reached when the new native compiler can compile its own BCPL compiler sources.

The desired chain is:

```text
historical interpreted compiler
          |
          v
compile native BCPL compiler
          |
          v
native BCPL compiler runs on MVS
          |
          v
native compiler recompiles itself
```

At that point the system becomes substantially self-hosting.

A particularly useful verification will be to compile the compiler again and compare the generated results. Exact byte-for-byte identity is not necessarily required in every bootstrap scheme, but differences must be explainable.

---

## Step 8: make the system ordinary to use

A successful port is more than a compiler demonstration.

The eventual MVS system should provide a practical workflow for:

- storing BCPL source in MVS data sets;
- compiling multiple modules;
- using reusable BCPL libraries;
- producing native load modules;
- reporting compiler diagnostics;
- running and debugging programs;
- rebuilding the compiler and runtime;
- distributing the system in an archival MVS-friendly form.

The project already maintains regression tests and demonstration programs so that capabilities established during reconstruction remain working as later pieces change.

---

## Why the port is being done incrementally

Historical compiler reconstruction is vulnerable to errors that can hide for a long time.

For example, a wrong pointer convention may allow simple programs to work and fail only when storage grows. A character-translation error may appear only in one operator. An incorrect stack frame may survive ordinary function calls but fail under coroutines.

For that reason this project favors small steps:

```text
identify one requirement
        |
make one change
        |
assemble / compile / run
        |
retain evidence
        |
add regression coverage
        |
continue
```

The regression panel, language demonstrations, library tests, and readable example programs are part of the porting method, not merely final polish.

---

## Current state of the reconstruction

At the time of writing:

- the preserved interpreted compiler pipeline is operational;
- ICINT V17 is the validated interpreter baseline;
- BCPL source can be compiled through SYNI/TRNI and CGI and executed under ICINT;
- multiple separately compiled BCPL modules can communicate through the GLOBAL vector;
- named MVS streams are supported;
- portable storage allocation has been reconstructed;
- portable coroutine services are running;
- a growing set of reusable BCPL library routines is available;
- regression and demonstration suites exercise the working system.

The principal unfinished work is the transition from the interpreted bootstrap to a **native System/370 compiler and runtime**.

For the current project status, see the repository [`README.md`](../README.md), which should be treated as more current than this historical overview.

---

## A simple mental model of the whole port

For a reader new to compiler porting, the reconstruction can be reduced to four layers:

```text
1. Make a tiny portable-machine interpreter run on MVS.

2. Run the preserved BCPL compiler on that interpreter.

3. Use the working compiler to build a System/370-native compiler
   and reconstruct the small machine-dependent runtime it needs.

4. Use the native compiler to rebuild and maintain BCPL entirely
   within MVS.
```

Everything else in the project—assembler experiments, stream handling, runtime libraries, regression tests, code-generator work, and historical research—supports one of those four steps.

---

## Further reading

### BCPL

- Martin Richards, **BCPL**: <https://www.cl.cam.ac.uk/~mr10/BCPL.html>
- Martin Richards, **How BCPL evolved from CPL**: <https://www.cl.cam.ac.uk/~mr10/cpl2bcpl.pdf>
- Martin Richards, **BCPL on CTSS**: <https://www.cl.cam.ac.uk/~mr10/BCPLCTSS.html>
- Martin Richards, **Cintpos / TRIPOS material**: <https://www.cl.cam.ac.uk/~mr10/Cintpos.html>
- Software Preservation Group, **History of BCPL**: <https://softwarepreservation.computerhistory.org/BCPL/>

### This reconstruction

- [`../README.md`](../README.md) — current project status and direction
- [`../richards-bcpltape/README.md`](../richards-bcpltape/README.md) — historical transport-tape material
- [`../asm/README.md`](../asm/README.md) — reconstructed System/370 assembler components
- [`../intcode/README.md`](../intcode/README.md) — INTCODE material
- [`../library/README.md`](../library/README.md) — reconstructed BCPL library
- [`../tests/README.md`](../tests/README.md) — regression tests
- [`../suite/README.md`](../suite/README.md) — readable demonstration programs

---

## Maintenance note

This document is intentionally a **living overview**.

The historical sections should change only when better evidence warrants a correction. The porting sections should be updated as the MVS reconstruction moves from interpreted execution to native code generation, runtime reconstruction, self-hosting, and eventual distribution.
