# MVS 3.8 Storage and Address-Space Model

## Purpose

This briefing orients a programmer to virtual storage, address spaces,
regions, tasks, storage protection, and dynamic storage under MVS 3.8 on
System/370. It deliberately avoids a detailed tour of internal control
blocks and release-specific storage maps.

## 1. Start with the System/370 address

For the MVS 3.8 era, the programmer's architectural address is
fundamentally a **24-bit address**, giving a 16 MiB address range:

``` text
000000 through FFFFFF
```

MVS virtual storage lets a program operate in an address space that need
not correspond one-for-one with installed real memory.

This distinction is foundational:

``` text
virtual address -> translated/mapped by system
real storage    -> physical memory
```

A program normally reasons in virtual addresses.

## 2. Address space

An **address space** is the major MVS virtual-storage context in which
programs execute.

Different jobs or system components can have separate address spaces
even though they may use identical virtual addresses.

Thus:

``` text
address 00100000 in address space A
```

need not denote the same real storage as:

``` text
address 00100000 in address space B
```

This isolation is one of the central purposes of virtual storage.

## 3. Private and common storage

At an orientation level, an MVS address space contains:

-   **private storage**, associated with that address space;
-   **common storage**, mapped so system-wide facilities can be
    accessible across address spaces.

The exact MVS 3.8 layout depends on system configuration and deserves
reference-manual treatment.

For programming, the important idea is:

``` text
private -> primarily belongs to this address space
common  -> system-wide/shared mapping
```

## 4. The nucleus and system areas

MVS itself occupies and manages portions of virtual and real storage for
the nucleus, system control structures, queues, and shared services.

Names such as **CSA** (Common Service Area) and **SQA** (System Queue
Area) appear in systems documentation and dumps.

An ordinary application programmer should recognize the names but
generally should not treat these areas as general-purpose storage.

Systems programming requires more detailed understanding because misuse
of common/system storage can affect more than one program.

## 5. Region

A batch job step is associated with a **region**, which constrains the
private virtual storage available to the step under applicable MVS rules
and installation policy.

JCL may contain a `REGION=` specification.

Do not reduce the concept to "physical RAM assigned to the job." A
region is part of the virtual-storage/resource model, and its practical
limits interact with MVS configuration.

When a program reports insufficient storage, distinguish:

-   virtual-storage/region limits;
-   exhausted subpools or fragmented available storage;
-   real-storage pressure;
-   an application leak or oversized request.

## 6. Tasks are not address spaces

An address space can contain multiple **tasks**.

This is a crucial distinction:

``` text
address space -> storage context
task          -> schedulable/execution context within it
```

Tasks in the same address space can normally address the same private
storage, subject to protection and program design.

`ATTACH` is associated with creating additional task execution, not with
creating an entirely new address space.

## 7. GETMAIN and FREEMAIN

Programs can request dynamic storage from MVS using services
traditionally expressed through macros such as `GETMAIN` and `FREEMAIN`.

Conceptually:

``` asm
         GETMAIN ...
         ...
         FREEMAIN ...
```

The detailed macro forms specify length, location, subpool, and other
attributes.

For orientation, treat them as the MVS-era counterparts of dynamic
storage allocation/deallocation, but do not assume C `malloc/free`
semantics in detail.

## 8. Subpools

MVS organizes dynamically obtained storage into **subpools** with
differing ownership and lifecycle characteristics.

A general-purpose programmer often can rely on conventional choices made
by macros or runtime libraries. A systems programmer eventually needs to
understand subpool ownership because it affects:

-   who may free storage;
-   when storage is released;
-   task versus job-step lifetime;
-   protection and system conventions.

Do not select subpools casually from examples without understanding
their contract.

## 9. Program loading consumes virtual storage

A load module must be brought into the address space before execution.

Program-management services such as `LOAD`, `LINK`, and `XCTL` interact
with this environment.

Thus a program's private storage can contain, conceptually:

``` text
loaded program text
static program data
save areas
dynamic work areas
access-method buffers
runtime/library material
system-managed structures
```

The precise arrangement is not a simple modern process heap/stack
diagram.

## 10. There is no hardware-defined "stack register"

System/370 has general registers, not a dedicated architectural stack
pointer.

A language or program can establish its own stack convention in storage,
but traditional MVS assembler linkage is commonly organized around
**save areas** and explicit work areas rather than a hardware push/pop
stack.

This matters when bringing assumptions from x86 or other stack-oriented
environments.

## 11. Save areas and dynamic work areas

A routine's save area preserves linkage state. It is not automatically a
general-purpose local-variable stack frame.

Programs may:

-   use statically allocated work areas;
-   obtain dynamic work areas with `GETMAIN`;
-   establish a language-specific stack;
-   combine these approaches.

For reentrant code, writable invocation-specific state normally must not
reside in shared static program text/data.

## 12. Reentrant and reusable code

A reentrant routine can be safely entered again while a prior invocation
remains active.

A typical design separates:

``` text
read-only/shareable program portion
          |
per-invocation writable work area
```

MVS can exploit such properties for sharing and system efficiency.

Module attributes and exact MVS sharing behavior are a deeper
linkage-editor/program-management subject.

## 13. Storage keys

System/370 provides **storage protection keys**. Storage blocks have
keys, and the processor's current protection context participates in
deciding whether certain accesses are permitted.

The mechanism helps protect:

-   the operating system from problem programs;
-   one class of storage from inappropriate modification;
-   shared/system structures.

A protection exception may therefore reflect not merely an invalid
numeric address but an access that violates protection rules.

## 14. Problem state and supervisor state

The PSW includes a problem-state indication.

In **problem state**, privileged instructions cannot simply be executed
by an application.

System services are requested through controlled interfaces, notably SVC
mechanisms.

This creates an important boundary:

``` text
problem program
     |
SVC / defined system interface
     |
supervisor processing
```

Systems programming often involves understanding this boundary without
assuming that "systems code" automatically runs privileged.

## 15. Real versus virtual storage pressure

Virtual storage does not eliminate physical constraints.

MVS manages real frames and backing mechanisms so that virtual pages can
be available without all being simultaneously resident.

From a programmer's perspective, ordinary addressing remains virtual.
From a performance and system-programming perspective, working-set
behavior, paging, and real-storage contention matter.

Do not optimize around physical placement unless the problem actually
requires that level of analysis.

## 16. Address-space isolation and communication

Because address spaces provide separate virtual-storage contexts, one
program cannot normally treat another address space's private address as
an ordinary local pointer.

Inter-address-space communication therefore requires operating-system
mechanisms or shared/common arrangements designed for that purpose.

This is one reason MVS system services and control structures are
important: raw pointers alone do not provide general IPC.

## 17. Storage lifetime

When examining any address, ask:

``` text
Who obtained this storage?
Which task/address space owns it?
How long is it valid?
Who may free it?
Can another invocation use it concurrently?
```

These questions catch many systems-programming defects.

A pointer can be numerically plausible and still refer to storage whose
ownership or lifetime is wrong.

## 18. Program checks related to storage

Storage errors often manifest as program checks/ABENDs such as
addressing or protection failures.

Useful evidence includes:

-   failing PSW;
-   effective address;
-   base/index register contents;
-   storage key/protection context where relevant;
-   ownership/lifetime of the referenced area.

The storage model and debugging model therefore meet directly.

## 19. Addressability versus allocation

Two distinct ideas are often confused.

**Allocation** asks:

> Does valid storage exist for this object?

**Assembler addressability** asks:

> Can this instruction encode a reference to that object using the
> assumed base registers?

A program can have perfectly valid allocated storage but fail because
the base register is wrong. Conversely, an instruction can be correctly
encoded yet point to storage the program does not own.

Keep both layers in mind.

## 20. Orientation map

``` text
System/370 24-bit virtual address
        |
MVS address space
        |
private storage + common/system mappings
        |
one or more tasks
        |
loaded modules + static areas + dynamic storage
        |
GETMAIN/FREEMAIN and program-management services
        |
hardware translation/protection
        |
real storage
```

## 21. Topics for deeper research

Research as needed:

-   exact MVS 3.8 virtual-storage layout;
-   CSA, SQA, nucleus, and private-area boundaries;
-   region calculation;
-   `GETMAIN`/`FREEMAIN` macro forms;
-   subpool ownership;
-   task control blocks;
-   paging and page replacement;
-   storage keys and fetch protection;
-   problem/supervisor state;
-   reentrant/reusable module attributes;
-   program fetch and load-module storage;
-   cross-memory concepts only with care, since many familiar facilities
    belong to later MVS generations.

The essential perspective is: **an MVS program executes in a protected
virtual address space containing both program-private and system/common
mappings; tasks execute within that space and obtain storage according
to explicit MVS conventions**.
