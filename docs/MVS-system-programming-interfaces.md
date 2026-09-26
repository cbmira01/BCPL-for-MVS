# MVS 3.8 System-Programming Interfaces

## Purpose

This briefing introduces the principal ways an assembler program
interacts with MVS itself. It focuses on conceptual boundaries: macros,
SVCs, control blocks, task services, synchronization, recovery, and
lower-level I/O. It is not an authorization or control-block programming
manual.

## 1. MVS is exposed largely through conventions and macros

A System/370 program does not normally invoke an operating-system
function through a modern dynamically linked API.

Instead, MVS programming commonly uses:

-   assembler macros;
-   defined parameter lists;
-   control blocks;
-   supervisor calls;
-   program-management services;
-   access methods;
-   documented system conventions.

A source statement may therefore look high-level:

``` asm
         GETMAIN ...
```

while the generated code and runtime path involve parameter construction
and an MVS supervisor interface.

## 2. Macro is not synonymous with system call

An assembler **macro** is a source-generation facility.

An MVS macro may expand into:

-   inline instructions;
-   a parameter list;
-   an SVC instruction;
-   branches to system routines;
-   combinations of these.

Therefore:

``` text
macro invocation
     != necessarily
one supervisor call
```

To understand a particular interface, inspect its documentation and,
when useful, the macro expansion in the assembler listing.

## 3. SVC: controlled entry to supervisor services

The System/370 `SVC` instruction causes a supervisor-call interruption.

Conceptually:

``` text
problem-state program
      |
      | SVC n
      v
MVS supervisor dispatch
      |
service processing
      |
return to caller
```

The SVC number identifies a defined supervisor function or dispatch
path.

This mechanism permits a problem-state program to request privileged
operating-system work without itself executing privileged instructions.

## 4. Parameter lists

Many MVS interfaces receive information through registers pointing to
structured parameter lists.

This is why systems assembler programming requires careful attention to:

-   field size;
-   alignment;
-   flags;
-   addresses versus values;
-   reserved fields;
-   storage lifetime.

A parameter list is an interface contract. Treating it as "just some
words near R1" is a common route to subtle failures.

## 5. Control blocks

MVS represents much of its state in structured storage areas called
**control blocks**.

Examples of names encountered in MVS literature include structures
associated with:

-   tasks;
-   address spaces;
-   data sets;
-   requests;
-   devices;
-   jobs and system resources.

Systems programs may receive pointers to documented control blocks or
navigate documented relationships.

The important discipline is:

> Do not infer that every visible internal field is a supported
> programming interface.

Release dependencies and authorization requirements matter.

## 6. Mapping macros

IBM commonly supplies assembler mappings that give symbolic names to
fields in control blocks.

Instead of hard-coding:

``` asm
         L     3,40(,2)
```

systems code can use a symbolic mapping describing what offset 40 means.

This improves readability and protects somewhat against layout changes,
though it does not make an undocumented interface supported.

## 7. Program-management services

Important concepts include:

-   `LOAD` --- make a module available and obtain its entry address;
-   `LINK` --- invoke another program with expected return;
-   `XCTL` --- transfer to another program without return to the
    transferring program;
-   `ATTACH` --- create execution under another task;
-   corresponding termination/release services where applicable.

These services sit above ordinary branch-and-link instructions because
MVS may need to locate, load, account for, and manage modules/tasks.

## 8. Dynamic storage

`GETMAIN` and `FREEMAIN` provide dynamic-storage services.

Systems programmers eventually need to understand:

-   requested length;
-   subpool;
-   ownership;
-   location constraints;
-   lifetime;
-   failure behavior.

For ordinary orientation:

``` text
GETMAIN -> obtain MVS-managed storage
FREEMAIN -> release storage according to its contract
```

Do not assume arbitrary storage can be freed merely because its address
is known.

## 9. WAIT and POST

MVS supports synchronization using event-control mechanisms commonly
associated with **ECB** structures and `WAIT`/`POST`.

Conceptually:

``` text
task A:
    start/request work
    WAIT for event

task B or system:
    work completes
    POST event

task A:
    becomes eligible to continue
```

This is a basic building block for asynchronous system activity.

Exact ECB formats and waiting rules should be taken from the MVS
supervisor-services documentation.

## 10. ENQ and DEQ

For serialization of named resources, MVS provides enqueue/dequeue
concepts.

Conceptually:

``` text
ENQ resource-name
    |
exclusive/shared ownership rules
    |
critical work
    |
DEQ resource-name
```

This is higher-level resource serialization than simply setting a byte
in shared storage.

Systems programmers must understand scope, naming, and deadlock
implications before using it.

## 11. Task management

An MVS address space can contain multiple tasks.

Services such as `ATTACH` establish subordinate task execution. Task
termination and synchronization then involve MVS control structures and
rules.

This introduces concerns familiar from concurrency elsewhere:

-   shared mutable storage;
-   synchronization;
-   ownership;
-   termination;
-   error propagation.

But the specific MVS task model should be learned on its own terms
rather than mapped mechanically to POSIX threads.

## 12. Timer and timing services

MVS provides timing and interval-related services used for:

-   elapsed/CPU timing;
-   delays;
-   interval notification;
-   accounting and performance work.

The exact macros and semantics vary by need. For orientation, recognize
timing as an OS service rather than assuming direct manipulation of
hardware timers is appropriate for a problem-state program.

## 13. Recovery and abnormal termination

MVS supports structured recovery mechanisms in addition to simply
allowing a task to terminate.

Terms such as **STAE** and related recovery facilities appear in systems
programming.

Conceptually, recovery mechanisms can let a program establish an
environment to receive control after certain abnormal conditions,
inspect diagnostic information, clean up, or determine whether recovery
is possible.

This is advanced territory. Recovery code runs under strict conventions
and should not be improvised from fragments.

## 14. ABEND service

Programs can intentionally request abnormal termination through
documented services.

This can be appropriate when continuing would corrupt data or violate an
interface contract.

A deliberate user ABEND is different from a CPU-detected program check,
even though both may ultimately appear as abnormal step termination.

## 15. Access methods as system interfaces

QSAM, BSAM, BPAM, and related access methods are themselves major MVS
programming interfaces.

They provide a higher-level path:

``` text
program
  |
GET/PUT/READ/WRITE
  |
access method
  |
MVS I/O machinery
```

Most programs should remain at this level unless they have a concrete
reason to descend further.

## 16. EXCP

**Execute Channel Program (EXCP)** is a lower-level I/O interface that
gives a program substantially more responsibility for device-oriented
I/O.

Conceptually:

``` text
ordinary program -> access method -> system/device machinery

EXCP program     -> builds lower-level I/O description
                 -> requests execution
                 -> handles completion/status at lower level
```

EXCP matters for specialized systems software, access methods,
utilities, and unusual devices.

It is not the normal way to read a sequential data set.

## 17. Channel programs and CCWs

At the hardware level, System/370 channel I/O uses **Channel Command
Words (CCWs)** to describe device operations.

A channel program can specify sequences such as:

``` text
seek/position
read/write
sense/status-related operations
```

depending on device type.

MVS normally shields applications from this level. Systems programmers
working with EXCP, device support, or emulator/device diagnostics may
need to understand it.

The device's hardware manual becomes as important as the MVS manual at
this layer.

## 18. Privileged instructions and authorization

Some processor instructions and MVS services are restricted.

Two distinct ideas matter:

-   **supervisor state** controls execution of privileged machine
    instructions;
-   **MVS authorization** controls access to certain sensitive
    operating-system facilities.

Do not assume that running assembler code, using an SVC, or residing in
a system library automatically grants arbitrary privilege.

Authorization is an explicit systems topic with serious integrity
consequences.

## 19. Branch-entry interfaces

Not every operating-system interaction necessarily appears as an SVC.
Some documented interfaces can involve branches to known entry points,
linkage conventions, or macro-generated paths.

Therefore the right question is:

> What interface does this MVS service document?

not:

> What SVC number must every service have?

The macro and service documentation define the supported entry
mechanism.

## 20. Interrupts versus program interfaces

Hardware interruptions include classes such as:

-   program interruptions;
-   I/O interruptions;
-   external interruptions;
-   supervisor calls.

An application does not normally install an arbitrary modern-style
interrupt handler for each event.

MVS receives and dispatches interruptions according to its control
structures, then exposes appropriate higher-level mechanisms such as
completion posting, recovery, or access-method exits.

Keep hardware interruption handling distinct from application
callbacks/exits.

## 21. Asynchronous exits

MVS has facilities in which code may receive control asynchronously or
under special system conditions.

Such code has stricter rules than ordinary sequential application code
because it may interrupt an existing execution context.

Before using any asynchronous exit mechanism, research:

-   what state is guaranteed;
-   which registers/storage are valid;
-   which services may safely be called;
-   serialization requirements;
-   reentrancy.

This is an area where "it assembled" says very little about correctness.

## 22. Systems-programming discipline

When using a low-level MVS interface:

1.  Identify the authoritative interface documentation.
2.  Determine whether it is intended for problem-state use.
3.  Determine authorization requirements.
4.  Use the supplied mapping/macros where appropriate.
5.  Respect parameter-list alignment and reserved fields.
6.  Understand storage ownership and lifetime.
7.  Understand task and asynchronous context.
8.  Check documented return and reason information.
9.  Have a dump/debugging plan before testing destructive paths.

This discipline is more valuable than memorizing large numbers of macro
operands.

## 23. Orientation map

``` text
application/system program
        |
assembler macro / documented convention
        |
parameter list + registers
        |
SVC / branch interface / access method
        |
MVS supervisor and control blocks
        |
task, storage, program, synchronization, or I/O service
        |
hardware facilities where necessary
```

## 24. Topics for deeper research

Useful research areas include:

-   MVS Supervisor Services and Macro Instructions;
-   SVC processing;
-   TCB/RB relationships;
-   ECB, WAIT, and POST;
-   ENQ/DEQ serialization;
-   GETMAIN/FREEMAIN and subpools;
-   ATTACH and task termination;
-   STAE and recovery environments;
-   authorized-program facilities;
-   EXCP;
-   IOS and device control blocks;
-   CCW/channel-program construction;
-   asynchronous exits;
-   system control-block mappings.

The key principle is: **use the highest documented MVS interface that
solves the problem; descend toward control blocks, EXCP, and hardware
only when the software genuinely requires that level of control**.
