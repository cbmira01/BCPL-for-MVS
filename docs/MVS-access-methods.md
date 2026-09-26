# MVS 3.8 Data Sets and Access Methods

## Purpose

This briefing orients a general-purpose or systems programmer to the way
MVS 3.8 stores and accesses program data. It is deliberately not an
access-method manual. The goal is to make MVS terminology, JCL,
assembler interfaces, and diagnostic material intelligible enough to
support later research.

## 1. The central idea: a data set is not a Unix file

MVS normally speaks of **data sets**, not files. A data set is a named
collection of records stored on a device such as DASD or magnetic tape.
The operating system separates several concerns that later systems often
hide behind a single file abstraction:

-   the data set's name and catalog status;
-   where it resides;
-   its physical allocation;
-   its record organization and format;
-   the access method used by the program;
-   the JCL that connects a program's logical name to the actual data
    set.

A program usually does not contain the physical name of its input or
output data set. It refers to a **DD name**. JCL supplies the binding.

``` text
Program:     OPEN INPUT
                |
                v
             DDNAME=INPUT
                |
                v
JCL:       //INPUT DD DSN=MY.DATA,DISP=SHR
                |
                v
          actual MVS data set
```

This separation is fundamental to MVS programming.

## 2. Data set names

A conventional data set name consists of one or more qualifiers
separated by periods:

``` text
CALVIN.BCPL.SOURCE
SYS1.MACLIB
PROJECT.TEST.DATA
```

Each qualifier is normally one through eight characters. The entire name
identifies the data set to MVS and, when cataloged, allows MVS to locate
its volume.

A data set can be:

-   **cataloged**, so its name can normally be used without specifying a
    volume;
-   **uncataloged**, requiring additional location information;
-   **temporary**, usually existing only for the duration of a job.

JCL frequently uses temporary names such as:

``` jcl
//OBJ DD DSN=&&OBJECT,UNIT=SYSDA,SPACE=(TRK,(1,1))
```

The `&&` name denotes a job-temporary data set.

## 3. Sequential data sets and partitioned data sets

For programmer orientation, two organizations dominate.

### 3.1 Physical sequential (PS)

A sequential data set is a sequence of records:

``` text
record 1
record 2
record 3
...
```

Typical uses include source input, reports, intermediate compiler
output, card-image data, and tape files.

Sequential access is natural: read or write records in order.

### 3.2 Partitioned data set (PDS)

A PDS is a container holding named **members**. Conceptually:

``` text
MY.SOURCE
    MEMBER1
    MEMBER2
    TEST
    HELLO
```

A member is referenced as:

``` text
MY.SOURCE(HELLO)
```

PDSs are central to traditional MVS development. They are used for
source libraries, macro libraries, object libraries, JCL libraries, and
load-module libraries.

Internally, a PDS has a directory plus member data. That matters because
directory space can be exhausted independently of the data area, and
repeated replacement of members can leave unusable gaps that
historically required **compressing** the PDS.

For initial orientation, think of a PDS as a named library rather than
as a hierarchical directory.

## 4. Records, not byte streams

Traditional MVS access methods generally expose data as **records**.

Important DCB attributes include:

-   **RECFM** --- record format;
-   **LRECL** --- logical record length;
-   **BLKSIZE** --- physical block size.

Common record formats include:

-   `F` --- fixed-length records;
-   `FB` --- fixed-length records grouped into blocks;
-   `V` --- variable-length records;
-   `VB` --- variable-length records grouped into blocks;
-   `U` --- undefined format, often used for load modules or other
    specialized data.

For example:

``` text
RECFM=FB,LRECL=80,BLKSIZE=800
```

describes 80-byte logical records with ten records per 800-byte block.

The distinction between a **logical record** and a **physical block** is
important. Blocking reduces I/O operations by transferring several
logical records at once.

## 5. The Data Control Block

In assembler programs, a **DCB** describes a data set interface. The DCB
is both a programmer-visible macro construct and an operating-system
control block.

A simplified declaration might look conceptually like:

``` asm
INPUT    DCB   DDNAME=INPUT,DSORG=PS,MACRF=GM
```

The exact operands depend on the access method and intended operations.

Information can come from several places:

-   the DCB coded in the program;
-   the DD statement;
-   the data set label;
-   system defaults.

During `OPEN`, MVS reconciles this information and prepares the DCB for
use.

This is one reason `OPEN` is significant: it is not merely setting a
Boolean "open" flag. It connects program intent, JCL allocation,
device/data-set characteristics, and access-method processing.

## 6. DD statements: the program/JCL boundary

A program normally knows a data set by its DD name:

``` asm
         DCB   DDNAME=SYSIN,...
```

JCL supplies the external definition:

``` jcl
//SYSIN DD DSN=CALVIN.INPUT,DISP=SHR
```

The same program can therefore run against different data without
recompilation.

Common DD concepts include:

-   `DSN=` --- data set name;
-   `DISP=` --- status and disposition;
-   `UNIT=` --- device class or unit;
-   `VOL=` --- volume information;
-   `SPACE=` --- DASD allocation;
-   `DCB=` --- data characteristics;
-   `SYSOUT=` --- route output through JES;
-   `*` or `DATA` --- inline input.

Example:

``` jcl
//REPORT DD SYSOUT=*
```

connects the program's `REPORT` DD name to JES-managed output.

## 7. DISP in one model

`DISP` answers two broad questions:

1.  What is the data set's status when this step begins?
2.  What should happen to it when the step ends normally or abnormally?

Common initial statuses:

-   `NEW` --- create it;
-   `OLD` --- it exists and exclusive use is requested;
-   `SHR` --- it exists and shared use is permitted;
-   `MOD` --- append or otherwise modify according to applicable rules.

A fuller form is:

``` jcl
DISP=(NEW,CATLG,DELETE)
```

Meaning, approximately:

-   allocate a new data set;
-   catalog it after normal completion;
-   delete it after abnormal completion.

`DISP` is both an allocation concept and a job-step lifecycle concept.

## 8. Access methods

An **access method** is IBM system software that mediates between a
program and data organization/device I/O.

### QSAM

**Queued Sequential Access Method (QSAM)** is the normal high-level
choice for sequential record I/O. It provides buffering and
record-oriented operations such as `GET` and `PUT`.

Typical conceptual flow:

``` asm
         OPEN  (INDCB,(INPUT))
LOOP     GET   INDCB,BUFFER
         ...
         B     LOOP
DONE     CLOSE (INDCB)
```

End-of-data handling is normally specified through the DCB/access-method
interface rather than by assuming `GET` simply returns an EOF value like
a C library call.

### BSAM

**Basic Sequential Access Method (BSAM)** operates at a lower level than
QSAM. The program works more explicitly with blocks and
asynchronous-style I/O operations such as `READ`, `WRITE`, and `CHECK`.

Use the distinction as:

``` text
QSAM -> logical-record-oriented, more access-method management
BSAM -> block-oriented, more programmer control
```

### BPAM

**Basic Partitioned Access Method (BPAM)** supports PDS-oriented
operations, including locating and accessing members.

A normal application programmer may rarely need BPAM directly; systems
software, library utilities, language processors, and tools are more
likely to encounter it.

### Other access methods

MVS also supports organizations and access methods beyond this
introductory set. In particular, indexed and direct organizations matter
in some applications. Research them when the data organization of a
program requires them rather than treating all MVS I/O as QSAM.

## 9. OPEN, CLOSE, GET, and PUT

The macros are worth recognizing even before studying their detailed
parameter lists.

### OPEN

`OPEN` establishes access to the data set and completes access-method
initialization.

``` asm
         OPEN  (OUTDCB,(OUTPUT))
```

### GET

With QSAM, `GET` obtains the next logical input record.

``` asm
         GET   INDCB,INAREA
```

### PUT

`PUT` supplies a logical output record.

``` asm
         PUT   OUTDCB,OUTAREA
```

### CLOSE

`CLOSE` terminates access-method processing and performs required
finalization.

``` asm
         CLOSE (OUTDCB)
```

Exact macro forms vary with DCB options. Treat examples here as
orientation, not templates to copy without checking the appropriate
macro documentation.

## 10. Buffering

Buffering is a major part of the access-method model.

A program may think in 80-byte records while the device transfers much
larger blocks. QSAM can manage buffers so that:

``` text
program GET
     |
logical record
     |
QSAM buffer management
     |
physical block
     |
channel/device I/O
```

This division explains why `LRECL` and `BLKSIZE` are separate and why
efficient data-set design historically paid close attention to blocking.

## 11. DASD allocation

A new DASD data set needs physical space. JCL might request:

``` jcl
SPACE=(TRK,(5,2))
```

Conceptually this requests a **primary** allocation and one or more
**secondary** allocations if additional space is needed.

Common allocation units include tracks and cylinders.

A PDS additionally needs directory space, traditionally expressed with a
directory quantity in the `SPACE` specification.

The programmer does not normally need to understand disk geometry to
write ordinary programs, but should recognize allocation failures and
understand that data-set space is explicitly managed.

## 12. JES data sets

Not every DD name maps to a persistent DASD data set.

For example:

``` jcl
//SYSPRINT DD SYSOUT=*
```

routes records to the job's spool output. Similarly:

``` jcl
//SYSIN DD *
input record
another record
/*
```

places inline records into the job input stream.

From the program's perspective these can still look like record-oriented
data sets. This illustrates MVS device independence particularly well.

## 13. Data set labels, catalogs, and volumes

These concepts are related but distinct:

-   the **data set name** identifies the data set;
-   the **catalog** maps names toward their location;
-   the **volume** is the physical or emulated medium;
-   **labels** record identifying and structural information on media.

When diagnosing allocation problems, ask separately:

``` text
Does the name exist?
Is it cataloged?
On what volume?
Is the volume available?
Do the requested DCB attributes agree with the data?
```

## 14. Device independence and its limits

MVS deliberately abstracts many device details. A sequential program can
often operate without knowing whether records ultimately came from
cards, DASD, tape, or JES spool.

But the abstraction is not complete. Device characteristics still
influence:

-   allocation;
-   blocking;
-   positioning;
-   performance;
-   supported access patterns;
-   error behavior.

Systems programmers therefore need both the logical data-set model and a
basic understanding of the underlying device environment.

## 15. What to inspect when an I/O program fails

A useful diagnostic sequence is:

1.  Verify the DD name expected by the program.
2.  Verify that the corresponding DD statement exists.
3.  Check `DSN`, `DISP`, volume, unit, and allocation.
4.  Check `RECFM`, `LRECL`, and `BLKSIZE`.
5.  Determine which access method and macro form the program uses.
6.  Inspect OPEN/CLOSE and end-of-data/error exits.
7.  Read the job log and system messages before changing code.
8.  If necessary, inspect the DCB and dump information.

Many apparent "assembler bugs" are actually mismatches among program DCB
information, JCL, and the existing data set.

## 16. Orientation map

Keep this model in mind:

``` text
application logic
      |
GET / PUT / READ / WRITE
      |
access method (QSAM/BSAM/BPAM/...)
      |
DCB
      |
DD name
      |
JCL DD statement
      |
data set organization + allocation
      |
device / JES spool
```

Each layer answers a different question.

## 17. Topics for deeper research

When a project requires more detail, useful research topics include:

-   complete DCB fields and macro forms;
-   QSAM locate versus move mode;
-   BSAM buffer and DECB processing;
-   BPAM member lookup and directory operations;
-   end-of-data and error exits;
-   concatenated data sets;
-   PDS directory structure and compression;
-   direct-access and indexed organizations;
-   catalog structures;
-   DASD extents and allocation;
-   tape labels and positioning;
-   EXCP for programs that intentionally bypass normal access methods.

The IBM access-method and data-management manuals are the appropriate
next level once one of these mechanisms becomes an implementation
requirement.

## 18. Working perspective

For ordinary MVS programming, the most useful mental shift is this:

> A program processes logical records through an access method and a
> DCB; JCL determines what external data set or system facility that
> logical interface denotes.

Once that separation is understood, much of traditional MVS I/O becomes
considerably easier to read.
