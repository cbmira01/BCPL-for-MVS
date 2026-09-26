# MVS 3.8 Program Execution and Linkage Conventions

## Purpose

This briefing explains how System/370 assembler routines cooperate under
MVS 3.8: registers, save areas, parameter lists, entry points, loading,
and transfer of control. It is an orientation to conventions and system
mechanisms, not a complete ABI specification.

## 1. Hardware permits; conventions organize

System/370 hardware provides registers and branch instructions. It does
not itself require a standard subroutine convention. MVS software
nevertheless depends heavily on established linkage conventions.

A routine that follows those conventions can cooperate with:

-   its caller;
-   assembler subroutines;
-   language runtimes;
-   operating-system services;
-   diagnostic and dump facilities.

The central ideas are:

``` text
R1   -> parameter information
R13  -> current save area
R14  -> return address
R15  -> entry address / commonly return code
```

These are conventions, not immutable properties of the registers.

## 2. The important registers

Traditional MVS assembler code commonly assigns these roles at routine
entry:

  Register   Conventional role
  ---------- --------------------------------------------------
  R0         work register; sometimes parameter/result use
  R1         address of parameter list
  R13        address of caller-provided save area
  R14        return address
  R15        entry-point address; often return code on return

Other registers are generally available for working use, subject to the
requirement that the called routine preserve the caller's expected
environment according to the linkage convention being used.

R12 is often chosen as a base register, but that is a programming
convention rather than a universal rule.

## 3. Why a save area exists

A called routine needs registers for its own work without destroying the
caller's register state.

The standard solution is a **save area**, traditionally 18 fullwords (72
bytes).

A routine commonly:

1.  receives R13 pointing to the caller's save area;
2.  saves the caller's registers;
3.  obtains or uses its own save area;
4.  chains its save area to the caller's;
5.  sets R13 to its own save area;
6.  performs its work;
7.  restores the caller's registers and R13;
8.  returns through R14.

Conceptually:

``` text
caller save area <----> callee save area <----> next callee ...
```

The forward/backward linkage makes the chain useful during diagnostic
traceback.

## 4. SAVE and RETURN macros

Assembler macros can express conventional linkage operations. A routine
may begin with a form of `SAVE` and end with a form of `RETURN`.

Conceptually:

``` asm
MYROUT   CSECT
         SAVE  (14,12)
         ...
         RETURN (14,12),RC=0
```

The exact macro expansion and appropriate register ranges should be
checked against the MVS macro documentation.

The important point is that these macros implement conventions using
ordinary machine instructions and established save-area layout. They are
not special System/370 call instructions.

## 5. Establishing addressability

System/370 instructions normally use base-plus-displacement addressing.
A routine therefore needs one or more base registers that make its code
and static data addressable.

A common pattern is conceptually:

``` asm
         BALR  12,0
         USING *,12
```

or entry conventions may allow the routine to establish addressability
from its entry address.

`USING` does not execute at run time. It tells the assembler which
register values it may assume when resolving addresses.

This distinction is essential:

``` text
BALR / LA / LR etc. -> executable instructions
USING / DROP         -> assembler addressability directives
```

## 6. Parameters

The conventional R1 interface usually passes the **address of a
parameter list**, not all arguments directly in registers.

Conceptually:

``` text
R1 -> +0  address of parameter 1
      +4  address of parameter 2
      +8  address of parameter 3
```

The called routine follows the pointers to obtain the actual data.

A simplified caller might construct:

``` asm
PARMLIST DC    A(PARM1)
         DC    A(PARM2)
```

and arrange for R1 to point at `PARMLIST` before transferring control.

The exact conventions can vary by interface. System services, language
runtimes, and application conventions may define different
parameter-list structures.

## 7. CALL is a macro-level convention

Assembler source may use the `CALL` macro:

``` asm
         CALL  SUBROUT,(PARM1,PARM2)
```

The macro helps construct the expected parameter list and linkage
sequence.

At the machine level, transfer of control ultimately uses System/370
branch-and-link facilities. This distinction helps when reading
listings:

``` text
source-level CALL
       |
macro expansion
       |
machine instructions + parameter list
```

Do not expect a System/370 opcode named `CALL` corresponding directly to
a modern ISA call instruction.

## 8. Returning

A conventional return transfers control to the address originally
supplied in R14.

A routine may also place a return code in R15.

Thus a caller often sees:

``` text
control -> R14
status  -> R15
```

But an individual interface can define different result conventions.
Always distinguish the general linkage convention from the contract of a
specific routine.

## 9. Static versus dynamic resolution

There are two separate questions:

1.  How is a symbolic reference resolved into an executable module?
2.  When does the target module become resident and receive control?

A reference may be resolved by the linkage editor when building a load
module, or a program may request modules dynamically at execution time.

Understanding this distinction prevents confusion between
**link-editing** and **runtime loading**.

## 10. LOAD

The MVS `LOAD` service makes a load module available and returns its
entry address, but does not by itself mean "call this routine."

Conceptually:

``` text
LOAD module
   |
entry address returned
   |
program later transfers control
```

A corresponding deletion mechanism can release the program's logical use
of a loaded module when appropriate.

`LOAD` is therefore about module availability and addressability, not
ordinary subroutine linkage alone.

## 11. LINK

`LINK` loads or locates another program and gives it control with an
expectation of return.

Conceptually:

``` text
A
|
LINK B
|    |
|    B executes
|    |
+<--- return
|
A continues
```

This is an MVS program-management service, not merely the linkage
editor.

## 12. XCTL

`XCTL` transfers control to another program **without an expected return
to the transferring program**.

Conceptually:

``` text
A ----XCTL----> B
```

This is useful when program A's role is finished and B should continue
in its place.

Compare:

``` text
CALL/BALR   ordinary routine linkage
LINK        invoke another program, then return
XCTL        transfer to another program, no return to caller
LOAD        make module available; caller controls later transfer
```

These are conceptual distinctions; detailed storage and task effects
belong in the relevant MVS program-management documentation.

## 13. ATTACH is different again

`ATTACH` creates another **task** within the address space and
establishes execution under that task.

It should not be mentally grouped with an ordinary subroutine call:

``` text
LINK  -> nested program invocation in the task
ATTACH -> additional task with its own execution context
```

Task management deserves separate study when concurrency becomes
relevant.

## 14. Entry points

A load module can have an entry point identifying where execution
begins. Object modules and load modules can also expose external symbols
that other modules reference.

Assembler source may define symbols and control sections that later
participate in link-edit processing.

Important concepts are:

-   **control section (CSECT)** --- independently relocatable unit;
-   **external definition** --- symbol made available to other modules;
-   **external reference** --- symbol required from elsewhere;
-   **entry point** --- address at which execution is to begin.

The object/load-module briefing develops these further.

## 15. Reentrancy

A **reentrant** routine can be entered again before an earlier
invocation has finished without corrupting shared writable state.

A common strategy is to keep executable/static areas read-only and place
invocation-specific writable data in separately obtained storage.

This matters for:

-   shared system code;
-   recursive or concurrent execution;
-   reusable library routines;
-   storage protection and sharing.

Do not equate "reentrant" simply with "does not modify its
instructions." Writable static data can also make a routine
non-reentrant.

## 16. Recursive execution

The classic save-area convention can support nested calls, but recursion
requires more than register saving. Each invocation also needs separate
mutable state.

A routine that uses a single static work area will generally not become
safely recursive merely because it chains save areas correctly.

Think in two layers:

``` text
linkage state -> registers, return address, save areas
local state   -> per-invocation writable data
```

## 17. Return codes versus abnormal termination

A routine may return normally with a status code, commonly in R15.

That is fundamentally different from an **ABEND**, which terminates a
task or job step abnormally under MVS rules.

For diagnostic purposes:

``` text
R15 return code -> program-defined or interface-defined normal result
ABEND code      -> abnormal termination information
```

Do not use the terms interchangeably.

## 18. Program libraries

At execution time, MVS must locate load modules in appropriate
libraries. JCL and system configuration determine the search
environment.

A programmer commonly encounters DD names such as `STEPLIB` or `JOBLIB`
to identify private load libraries.

The detailed search order is operationally important and should be
researched when module-location problems arise. For orientation,
remember that a successfully link-edited module still has to be
**findable at execution time**.

## 19. A conceptual two-module example

Suppose `MAIN` calls `SUB`.

At source level:

``` text
MAIN:
    establish linkage
    construct parameter list
    CALL SUB
    inspect result
    return

SUB:
    save caller environment
    establish own environment
    use parameters
    place result/status
    restore caller environment
    return
```

At build time:

``` text
MAIN object ----\
                 +---- linkage editor ----> load module
SUB object  ----/
```

At execution time, the machine sees addresses, registers, branches, and
storage. The symbolic relationships have already been resolved or are
handled by MVS program-management services.

## 20. What to inspect when linkage fails

A useful sequence is:

1.  Was the external symbol spelled and defined correctly?
2.  Did the assembler produce the expected ESD information?
3.  Did the linkage editor report unresolved references?
4.  Is the intended entry point selected?
5.  Can MVS locate the resulting load module?
6.  On entry, are R1, R13, R14, and R15 being interpreted correctly?
7.  Is a valid save area being used?
8.  Is addressability correctly established?
9.  Are parameters addresses or values as the interface expects?
10. On return, were registers and R13 restored correctly?

The assembler listing, linkage-editor map, and dump complement one
another.

## 21. Orientation map

``` text
source routine
    |
assembler
    |
object module
    |
linkage editor
    |
load module
    |
MVS program management
    |
entry with conventional register state
    |
save area / parameters / base registers
    |
routine execution
    |
return through linkage convention
```

## 22. Topics for deeper research

Useful next-level topics include:

-   exact standard save-area layout;
-   `SAVE`, `RETURN`, `CALL`, `LINK`, `LOAD`, `DELETE`, `XCTL`, and
    `ATTACH`;
-   parameter-list conventions for specific services;
-   `ENTRY`, external symbols, and aliases;
-   reentrant and reusable modules;
-   overlay structures where historically relevant;
-   program-library search order;
-   task control blocks and request blocks;
-   linkage-editor control statements;
-   dump traceback through save-area chains.

The key orientation principle is that **System/370 provides the branch
machinery; MVS conventions and services turn it into a cooperative
program environment**.
