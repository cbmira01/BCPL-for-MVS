# JCL for the MVS 3.8 Programmer

## Purpose

This briefing introduces Job Control Language from the viewpoint of a
programmer who needs to assemble, link-edit, run, test, and diagnose
programs under MVS 3.8. It is not a complete JCL reference.

## 1. What JCL does

JCL describes work to the operating system and JES. It tells the system:

-   what job is being submitted;
-   which programs or procedures to execute;
-   which data sets and system facilities those programs require;
-   how resources and output should be handled.

JCL is not the application program. It describes the **execution
environment** around the application.

The basic hierarchy is:

``` text
JOB
  |
  +-- STEP 1 (EXEC)
  |      +-- DD
  |      +-- DD
  |
  +-- STEP 2 (EXEC)
         +-- DD
```

## 2. JOB, EXEC, and DD

Three statement types dominate ordinary programmer JCL.

### JOB

The `JOB` statement begins the job and supplies job-level information.

``` jcl
//HELLO    JOB ...
```

Installation-specific accounting and routing fields vary. Do not copy a
JOB card from another installation without checking local conventions.

### EXEC

An `EXEC` statement defines a job step and identifies either a program
or a cataloged/in-stream procedure.

``` jcl
//ASM      EXEC PGM=IFOX00
```

or:

``` jcl
//ASM      EXEC PROC=...
```

The exact assembler invocation in a TK5 environment may use supplied
procedures rather than a raw `PGM=` form.

### DD

A `DD` statement defines one of the step's data definitions.

``` jcl
//SYSIN    DD *
...
/*
//SYSPRINT DD SYSOUT=*
```

DD statements are how JCL connects program DD names to data.

## 3. Step names and DD names

In:

``` jcl
//ASM      EXEC ...
//SYSIN    DD ...
//SYSPRINT DD ...
```

`ASM` is the **step name**.

`SYSIN` and `SYSPRINT` are **DD names** expected by the program or
procedure.

These names matter because messages often refer to them.

## 4. A compile-link-run pipeline

A traditional language-processing job commonly looks conceptually like:

``` text
assembler step
    source -> object

link-edit step
    object + libraries -> load module

execution step
    load module -> program output
```

Temporary data sets can connect the steps:

``` text
ASM.SYSLIN -> &&OBJ
LKED.SYSLIN reads &&OBJ
LKED.SYSLMOD -> &&LOAD(member)
GO.STEPLIB or passed load library -> program
```

Procedures hide much of this plumbing, but understanding the pipeline
makes procedure output far easier to diagnose.

## 5. In-stream source and data

A DD statement can introduce inline records:

``` jcl
//SYSIN DD *
         PRINT NOGEN
...
         END
/*
```

For many tools, `SYSIN` is conventional standard input.

The delimiter ends the in-stream data and returns control to JCL
processing.

## 6. SYSOUT

A DD such as:

``` jcl
//SYSPRINT DD SYSOUT=*
```

routes output to JES spool rather than to a named permanent data set.

Common names such as `SYSPRINT`, `SYSOUT`, `SYSTERM`, or tool-specific
DD names are conventions defined by individual programs and procedures.
JCL itself does not magically assign their semantics.

## 7. Data set naming

A DD may identify a persistent data set:

``` jcl
//INPUT DD DSN=CALVIN.TEST.INPUT,DISP=SHR
```

or a member:

``` jcl
//SOURCE DD DSN=CALVIN.ASM.SOURCE(HELLO),DISP=SHR
```

or a temporary data set:

``` jcl
//OBJ DD DSN=&&OBJ,DISP=(NEW,PASS),...
```

The JCL/data-set briefing boundary is important: JCL **allocates and
connects** data sets; the program accesses them through its access
method.

## 8. DISP

For programmer work, recognize:

``` text
NEW -> create
OLD -> existing, exclusive use
SHR -> existing, shared use
MOD -> modify/append according to context
```

A three-part disposition can describe normal and abnormal outcomes:

``` jcl
DISP=(NEW,PASS,DELETE)
```

`PASS` is especially useful for an intermediate data set needed by a
later step in the same job.

## 9. Temporary data sets

Names beginning with `&&` conventionally identify temporary data sets:

``` jcl
//SYSLIN DD DSN=&&OBJ,...
```

They are useful for intermediate compiler/linker material that need not
survive the job.

Temporary data sets are one reason multi-step JCL can form a
self-contained build pipeline without cluttering the catalog.

## 10. SPACE, UNIT, and DCB

When creating a DASD data set, JCL may need allocation information:

``` jcl
UNIT=SYSDA
SPACE=(TRK,(5,2))
DCB=(RECFM=FB,LRECL=80,BLKSIZE=800)
```

Conceptually:

-   `UNIT` says what kind of device/resource;
-   `SPACE` says how much DASD space;
-   `DCB` supplies data characteristics.

Not every DD requires all of these. Existing cataloged data sets and
installation defaults can provide information.

## 11. Procedures

A **procedure** packages reusable JCL.

Instead of spelling out every DD and EXEC statement for the assembler, a
programmer may invoke a supplied procedure and override selected
parameters or DD statements.

Conceptually:

``` text
cataloged procedure
    |
    +-- standard assembler step
    +-- standard link-edit step
    +-- standard DDs

your job
    |
    +-- invoke procedure
    +-- override only what differs
```

This reduces boilerplate but can obscure what actually ran. When
debugging, expand your mental model back into the constituent steps.

## 12. Symbolic parameters and overrides

Procedures can define symbolic values that the caller supplies or
overrides. DD statements and EXEC parameters can also be overridden
using qualified names.

Exact syntax deserves reference-manual treatment. For orientation, know
why job output sometimes contains generated JCL different from the short
procedure invocation you submitted: JES/JCL processing has expanded the
procedure.

## 13. Program parameters

`EXEC` can pass a parameter string to a program:

``` jcl
//STEP EXEC PGM=MYPROG,PARM='TEST'
```

How `MYPROG` receives and interprets that parameter is defined by the
MVS execution interface and the program itself.

Do not confuse:

``` text
JCL symbolic parameter -> changes JCL/procedure expansion
EXEC PARM=             -> input to executing program
```

## 14. Return codes and step control

A normally completing program commonly supplies a return code. JCL can
use prior step results to decide whether later steps should execute.

Historically, `COND=` is a common mechanism. Its logic can be
unintuitive because it describes conditions under which a step is
**bypassed**.

For orientation, read it as a control-flow facility based on previous
completion codes, and consult the JCL reference before constructing
complicated expressions.

In build jobs, the intended policy is often:

``` text
assemble succeeded?
    yes -> link
    no  -> stop useful processing

link succeeded?
    yes -> run
    no  -> do not execute bad output
```

Procedures frequently encode this policy.

## 15. Condition code versus ABEND

A **condition code** normally describes a program or utility's completed
result.

An **ABEND** describes abnormal termination.

Typical build output might therefore show:

``` text
ASM  CC=0000
LKED CC=0000
GO   CC=0000
```

or an abnormal completion code for a failed execution step.

Always determine whether a step returned normally with a nonzero code or
terminated abnormally; the diagnostic paths differ.

## 16. Libraries

Several library concepts appear in programmer JCL.

### STEPLIB

A `STEPLIB` DD identifies a private load-module library for a particular
step.

### JOBLIB

A `JOBLIB` can provide a job-level private program library.

### Language and macro libraries

Assemblers and link editors may use their own DD names to identify macro
libraries or object libraries. The exact names are tool/procedure
contracts, not universal JCL keywords.

## 17. Concatenation

Multiple data sets can sometimes be presented under one DD name by
coding consecutive DD statements.

Conceptually:

``` text
DDNAME
  |
  +-- library A
  +-- library B
  +-- library C
```

The program/access method sees a concatenation according to the
applicable rules.

This is common for search libraries and sequential input collections.
Compatibility requirements matter; not arbitrary data sets can be
concatenated meaningfully.

## 18. DD DUMMY

A DD can specify `DUMMY` when the program expects a DD name but no real
data set is required.

Depending on whether the DD is input or output, the access method treats
it appropriately.

This is useful for optional reports or optional inputs, but only when
the program's behavior is compatible with a dummy data set.

## 19. JES and the job lifecycle

A programmer's simplified lifecycle is:

``` text
submit JCL
    |
JES reads and queues job
    |
JCL is interpreted / resources prepared
    |
initiator executes steps under MVS
    |
SYSOUT is spooled
    |
JES presents/prints/purges output
```

JES messages such as `$HASP...` describe spool and job-processing
events. MVS messages such as `IEF...` often describe allocation and step
execution.

Recognizing the subsystem producing a message narrows the search.

## 20. Reading job output efficiently

For a failed programming job, do not begin by reading every printed
line.

A useful order is:

1.  Find the job start/end messages.
2.  Identify each step and its completion code.
3.  Find the **first** step that failed.
4.  Read allocation/JCL messages for that step.
5.  Read the program's own diagnostics.
6.  For assembly, inspect error messages and listing around the first
    source error.
7.  For link-edit, inspect unresolved symbols and control statements.
8.  For execution, inspect ABEND information and dumps.

Later failures are often consequences of the first one.

## 21. Common programmer mistakes

Typical problems include:

-   misspelled DD name;
-   wrong data set name or member;
-   incorrect `DISP`;
-   missing allocation information for a new data set;
-   incompatible DCB characteristics;
-   procedure override applied to the wrong step;
-   link step allowed to run after a bad assembly;
-   execution step using the wrong load library;
-   confusing JCL syntax errors with application errors.

Treat JCL as part of the program's reproducible execution environment,
not as administrative decoration.

## 22. Orientation map

``` text
JOB statement
     |
one or more EXEC steps
     |
program/procedure
     |
DD names required by that program
     |
data sets / SYSOUT / inline data / libraries
     |
MVS allocation + JES spool services
```

## 23. Topics for deeper research

Research these as needed:

-   complete JOB/EXEC/DD syntax;
-   cataloged and in-stream procedures;
-   symbolic parameters and overrides;
-   `COND` and step execution rules;
-   GDGs;
-   catalog and volume specification;
-   DD concatenation rules;
-   output classes and JES routing;
-   allocation messages;
-   restart facilities;
-   `JOBLIB`/`STEPLIB` search rules;
-   utility programs such as IEBGENER, IEBCOPY, and IDCAMS where
    applicable;
-   installation-specific JES2 conventions.

The working principle is simple: **the program defines logical resource
names; JCL builds the concrete world in which those names operate**.
