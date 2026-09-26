# MVS 3.8 Programmer's Briefing

## 1. Purpose and Scope

MVS 3.8 is an IBM operating system for the System/370 architecture. It represents the mature mainframe operating-system model of the late 1970s: virtual storage, multiprogramming, asynchronous I/O, batch processing, data-set management, task scheduling, resource serialization, recovery facilities, and extensive operator control.

This briefing concentrates on MVS from the standpoint of the **general-purpose programmer and systems programmer**.

The central distinction is:

> **System/370 defines the machine. MVS defines the operating environment in which programs use that machine.**

System/370 supplies facilities such as:

- General and floating-point registers
- Machine instructions
- The Program Status Word (PSW)
- Interruptions
- Supervisor and problem states
- Storage protection
- Dynamic Address Translation (DAT)
- Channels and channel commands
- Privileged instructions

MVS builds operating-system abstractions and services on those facilities:

- Address spaces
- Tasks
- Program loading
- Virtual-storage management
- Synchronization
- Supervisor services
- Abnormal termination and recovery
- Data sets
- Access methods
- Device management
- Job processing
- Spooling
- Communications
- Security
- Operator control

The result is a programming environment substantially more abstract than bare System/370, while still exposing considerably more of the underlying machine than most modern application environments.

---

# 2. Overall MVS Model

A useful first approximation is:

```text
                        Users / Operators
                              |
             +----------------+----------------+
             |                                 |
            TSO                               JES2
             |                                 |
             +----------------+----------------+
                              |
                              v
                         MVS Services
                              |
        +---------------------+----------------------+
        |                     |                      |
        v                     v                      v
 Virtual Storage         Task Management        Data Management
        |                     |                      |
        +---------------------+----------------------+
                              |
                              v
                    System/370 Architecture
                              |
            +-----------------+----------------+
            |                 |                |
            v                 v                v
           CPU              Storage          Channels
                                               |
                                               v
                                      Control Units/Devices
```

MVS is not simply a collection of system calls. It establishes conventions governing:

- how programs receive control,
- how registers are used,
- how storage is obtained,
- how programs call other programs,
- how tasks are created,
- how events are represented,
- how resources are serialized,
- how data sets are described,
- how I/O is requested,
- how errors are reported,
- and how work enters and leaves the system.

---

# 3. Jobs, Address Spaces, Tasks, and Programs

Several MVS concepts that can initially appear interchangeable are actually distinct.

## 3.1 Job

A **job** is a unit of work presented to the system, normally through Job Control Language (JCL) and JES.

A job can contain multiple **job steps**.

```text
JOB
 |
 +-- STEP1
 |
 +-- STEP2
 |
 `-- STEP3
```

Each step normally executes a program.

---

## 3.2 Address Space

An **address space** is a virtual-storage environment.

A conventional MVS address space provides a 24-bit virtual address range:

```text
000000
   .
   .
   .
FFFFFF
```

This represents 16 MiB of virtual addressability.

Different address spaces can use the same virtual address while referring to different real-storage locations.

---

## 3.3 Task

A **task** is a schedulable unit of work within an address space.

A task is represented principally by a:

**TCB — Task Control Block**

An address space can contain multiple tasks:

```text
Address Space
     |
     +-- Main Task
     |
     +-- Subtask A
     |
     `-- Subtask B
```

Tasks share the address-space environment but can execute independently under MVS scheduling.

---

## 3.4 Program

A **program** is executable code, normally contained in a load module.

A task can execute one program and subsequently transfer control to another.

Therefore:

> A job is not a task, a task is not an address space, and a program is not necessarily a task.

These distinctions are fundamental to MVS systems programming.

---

# 4. Program Preparation

A conventional assembler development path is:

```text
Assembler Source
      |
      v
IFOX Assembler
      |
      v
Object Module
      |
      v
Linkage Editor
      |
      v
Load Module
      |
      v
Loader
      |
      v
Execution
```

The assembler translates symbolic System/370 instructions and MVS macros into an object module.

The linkage editor resolves external references and constructs a load module.

The load module can reside in a partitioned data set such as:

```text
USER.LOADLIB(MYPROG)
```

JCL can execute it:

```jcl
//RUN EXEC PGM=MYPROG
```

---

# 5. Program Entry and Register Conventions

System/370 itself does not impose a high-level subroutine calling convention.

MVS software conventions provide one.

At entry to a conventional program, several registers have special significance.

| Register | Conventional purpose |
|---|---|
| R0 | Work or parameter information |
| R1 | Parameter-list address |
| R13 | Save-area address |
| R14 | Return address |
| R15 | Entry address / return code |

The remaining registers are generally available for program use subject to calling conventions.

A program commonly begins with code resembling:

```asm
MYPROG   CSECT
         STM   14,12,12(13)
         LR    12,15
         USING MYPROG,12
```

The `STM` preserves the caller's registers.

`LR 12,15` establishes a base-register value.

`USING` tells the assembler that register 12 can be used as a base for addresses within the program.

---

# 6. Save Areas

A standard MVS linkage convention uses **save areas**.

Register 13 points to the caller's save area.

The called routine normally establishes its own save area and chains it with the caller's.

Conceptually:

```text
Caller Save Area
       |
       v
Callee Save Area
       |
       v
Next Routine Save Area
```

The chain assists both normal linkage and diagnostic processing.

A routine normally restores the caller's registers before returning.

Conceptually:

```asm
         LM    14,12,12(13)
         BR    14
```

Register 15 conventionally carries the return code.

This illustrates an important distinction:

> Register linkage is primarily a software convention layered on the System/370 register architecture.

---

# 7. Parameter Passing

Register 1 conventionally points to a parameter list.

Rather than placing an entire structure directly in registers, the caller commonly supplies a list of addresses:

```text
R1
 |
 v
+-------------+
| Address ----+----> Parameter 1
+-------------+
| Address ----+----> Parameter 2
+-------------+
| Address ----+----> Parameter 3
+-------------+
```

This convention appears extensively in MVS programs and system services.

---

# 8. Program Loading and Transfer of Control

MVS provides several related but distinct services.

## 8.1 LOAD

`LOAD` makes a load module available in storage and returns information allowing the program to locate its entry point.

It does not inherently mean "call this program."

---

## 8.2 LINK

`LINK` invokes another program with the expectation that control will return.

```text
Program A
    |
    +---- LINK ----> Program B
    |                  |
    <------------------+
```

This resembles a dynamically resolved procedure call.

---

## 8.3 XCTL

`XCTL` transfers control to another program without expecting control to return to the current program.

```text
Program A ---- XCTL ----> Program B
```

It effectively replaces the current program in the linkage sequence.

---

## 8.4 ATTACH

`ATTACH` creates another task.

```text
             Main Task
             /       \
            /         \
      Subtask A     Subtask B
```

This is fundamentally different from `LINK`.

`LINK` changes the program being executed in a linkage sequence.

`ATTACH` creates another schedulable task.

---

# 9. Virtual Storage

Virtual storage is one of the defining features of MVS.

A program ordinarily works with virtual addresses.

```text
Program Virtual Address
          |
          v
 Dynamic Address Translation
          |
          v
      Real Storage
```

The System/370 DAT hardware performs address translation using structures maintained under operating-system control.

MVS therefore allows an address space larger than the amount of real storage physically assigned to it at any particular instant.

---

# 10. Private and Common Storage

Not all virtual storage belongs exclusively to one program.

An MVS address space contains private and common areas.

Simplified:

```text
+---------------------------+
| Common System Storage     |
+---------------------------+
|                           |
| Private Address-Space     |
| Storage                   |
|                           |
+---------------------------+
| System Areas              |
+---------------------------+
```

Common areas allow important MVS code and data to be mapped into multiple address spaces.

Private storage belongs to the individual address-space environment.

This arrangement permits system services to remain accessible while maintaining separation among user address spaces.

---

# 11. Paging

Virtual storage need not continuously occupy real memory.

Conceptually:

```text
Virtual Storage
      |
      v
Real Storage
      |
      v
Paging Data Sets
```

If a program references a virtual page that is not currently resident, the hardware and MVS cooperate to bring the required page into real storage.

The task may wait while this occurs.

Once the page becomes available, execution can continue.

The application generally does not explicitly manage this process.

---

# 12. Dynamic Storage: GETMAIN and FREEMAIN

Programs often require storage whose size or lifetime cannot conveniently be determined at assembly time.

MVS provides `GETMAIN`.

Conceptually:

```asm
         GETMAIN R,LV=256
```

The program requests 256 bytes of storage.

When that storage is no longer required, the program can use `FREEMAIN`.

```asm
         FREEMAIN ...
```

At a conceptual level:

```text
GETMAIN   ~ allocate memory
FREEMAIN  ~ release memory
```

This is somewhat analogous to modern dynamic-memory allocation, although the MVS facilities expose different storage classes, conventions, and control options.

---

# 13. Task Scheduling

MVS dispatches runnable tasks onto available processors.

A simplified task-state model is:

```text
              event occurs
                   |
                   v
WAITING --------> READY
                    |
                    | dispatched
                    v
                 RUNNING
                    |
                    | wait
                    v
                 WAITING
```

A program normally does not directly select the next task to execute.

Instead, task state changes result from events such as:

- requesting I/O,
- waiting for an event,
- completion of I/O,
- posting an event,
- expiration of timing intervals,
- termination,
- or supervisor activity.

---

# 14. WAIT and POST

One of the fundamental MVS synchronization mechanisms is the:

**ECB — Event Control Block**

A task can wait for an event:

```asm
         WAIT  ECB=MYECB
```

Another task, interrupt handler, or system component can signal the event:

```asm
         POST  MYECB
```

Conceptually:

```text
Task A                          Task B

WAIT ECB
   |
   | suspended
   |
   |                            work
   |                             |
   |                          POST ECB
   |                             |
   +------ becomes ready <-------+
```

The ECB provides a simple representation of event completion.

WAIT/POST is heavily used throughout MVS, particularly in asynchronous processing.

---

# 15. Resource Serialization: ENQ and DEQ

WAIT/POST deals principally with **events**.

ENQ/DEQ deals principally with **resource ownership**.

A task requests control of a named resource:

```asm
         ENQ   ...
```

When finished:

```asm
         DEQ   ...
```

Conceptually:

```text
                 RESOURCE

Task A ---- ENQ ----> owns resource

Task B ---- ENQ ----> waits

Task A ---- DEQ ----> releases resource

Task B -------------> obtains resource
```

MVS can serialize resources at different scopes.

ENQ/DEQ therefore provides an important mechanism for coordinating access to shared system resources.

---

# 16. Problem State and Supervisor State

System/370 provides two execution states:

- **problem state**
- **supervisor state**

Ordinary programs normally execute in problem state.

Certain instructions are privileged and cannot normally be executed by a problem-state program.

MVS itself performs privileged operations in supervisor state.

This establishes a fundamental protection boundary:

```text
Problem Program
      |
      | request service
      v
MVS Supervisor
      |
      | privileged operation
      v
Hardware
```

---

# 17. Supervisor Calls

System/370 provides the `SVC` instruction:

```asm
         SVC   n
```

Executing an SVC causes a supervisor-call interruption.

Conceptually:

```text
Problem Program
      |
      | SVC
      v
MVS Supervisor
      |
      | service processing
      v
Problem Program
```

The SVC mechanism provides a controlled path into privileged operating-system services.

---

# 18. MVS Macros and SVCs

An important programming distinction is:

> An MVS macro and an SVC are not the same thing.

A programmer might write:

```asm
         GETMAIN ...
```

The assembler expands that macro.

The expansion can include:

- ordinary machine instructions,
- parameter lists,
- control-block manipulation,
- an SVC instruction,
- branches to system routines,
- or combinations of these.

The macro is the **documented programming interface**.

The SVC is one mechanism by which the generated code may enter the supervisor.

Consequently, systems programmers normally use the documented macro rather than directly coding an SVC number unless there is a specific reason to work at that lower level.

---

# 19. Interruptions and MVS

System/370 defines several interruption classes.

Important examples include:

- Program interruptions
- Supervisor-call interruptions
- I/O interruptions
- External interruptions
- Machine-check interruptions

The hardware detects the event and transfers control according to architectural rules.

MVS then performs the software-level processing appropriate to the interruption.

Thus:

```text
Hardware Event
      |
      v
System/370 Interruption
      |
      v
MVS Interrupt Processing
      |
      v
Operating-System Action
```

The distinction between **hardware interruption** and **operating-system response** is essential.

---

# 20. Program Exceptions

System/370 can detect conditions such as:

- operation exceptions,
- privileged-operation exceptions,
- addressing exceptions,
- protection exceptions,
- specification exceptions,
- data exceptions,
- arithmetic exceptions.

Suppose a program accesses an invalid location.

Conceptually:

```text
Faulting Instruction
       |
       v
Program Interruption
       |
       v
MVS
       |
       +--> recovery processing
       |
       `--> abnormal termination
```

MVS interprets the architectural interruption in the context of the executing task.

---

# 21. ABEND

MVS uses the term:

**ABEND — abnormal end**

to describe abnormal termination.

An ABEND can result from:

- a hardware-detected program exception,
- an MVS-detected error,
- an explicit software request,
- an unrecoverable system-service failure.

ABENDs are represented using completion codes.

One familiar example is:

```text
S0C4
```

which is associated with addressing/protection-related program exceptions.

The important conceptual relationship is:

```text
Architectural Exception
        |
        v
MVS Exception Processing
        |
        v
ABEND / Recovery
```

An ABEND is therefore an operating-system concept built partly upon System/370 exception mechanisms.

---

# 22. Dumps and Diagnostics

When a program fails, MVS can produce diagnostic information.

Useful information can include:

- PSW
- General registers
- Floating-point registers where relevant
- Failing instruction
- Storage contents
- Task information
- Load-module information
- System control blocks
- Completion codes

A systems programmer often begins debugging with:

```text
ABEND code
    +
PSW
    +
registers
    +
failing instruction
    +
storage contents
```

From these, it is often possible to reconstruct what the program was attempting when the failure occurred.

---

# 23. Recovery

MVS is designed for environments in which terminating an entire system component for every software error would be unacceptable.

It therefore provides recovery facilities.

One important application-level facility is **STAE**, which allows a program to establish an abnormal-termination exit.

Conceptually:

```text
Normal Program
      |
      | exception
      v
MVS Recovery Processing
      |
      v
Recovery Routine
      |
      +--> diagnose
      +--> clean up
      +--> retry where permitted
      `--> terminate
```

Recovery inside the operating system can be considerably more elaborate.

The general objective is to contain failures and preserve as much useful system operation as possible.

---

# 24. Data Sets

MVS normally uses the term **data set** rather than file.

A data-set name might be:

```text
USER.BCPL.SOURCE
```

or:

```text
SYS1.LINKLIB
```

Data sets have attributes that affect how MVS stores and accesses their contents.

A data set is not simply an uninterpreted sequence of bytes.

Its organization and record format are significant parts of its definition.

---

# 25. Data-Set Organizations

Important organizations include several broad categories.

## Sequential

Records are processed sequentially:

```text
Record 1
Record 2
Record 3
Record 4
...
```

This organization is common for:

- text input,
- reports,
- intermediate files,
- tapes.

---

## Partitioned

A Partitioned Data Set (**PDS**) contains named members.

```text
USER.SOURCE
     |
     +-- PROGRAM1
     +-- PROGRAM2
     +-- PROGRAM3
     `-- MACRO1
```

PDS data sets are widely used for:

- assembler source,
- JCL,
- macros,
- procedures,
- load modules.

A PDS resembles a combination of a file and a simple directory/library.

---

## Direct and Indexed Organizations

MVS also supports organizations permitting records to be accessed without reading every preceding record.

These become important for database-like and indexed applications.

---

# 26. Records and Blocks

Traditional MVS data management is strongly **record oriented**.

This differs significantly from the UNIX byte-stream model.

A data set has attributes such as:

- `RECFM`
- `LRECL`
- `BLKSIZE`

Common record formats include:

| Format | Meaning |
|---|---|
| F | Fixed |
| FB | Fixed blocked |
| V | Variable |
| VB | Variable blocked |
| U | Undefined |

For example:

```text
RECFM=FB
LRECL=80
BLKSIZE=800
```

means that logical records are 80 bytes long and ten records can be stored in an 800-byte physical block.

Conceptually:

```text
Physical Block
+--------+--------+--------+-----+
| Rec 1  | Rec 2  | Rec 3  | ... |
+--------+--------+--------+-----+
```

Blocking reduces the number of physical I/O operations required.

---

# 27. The DCB

A major programmer-visible data-management structure is the:

**DCB — Data Control Block**

An assembler program can declare one with a macro such as:

```asm
INDCB    DCB   DDNAME=INPUT,DSORG=PS,MACRF=GM
```

The DCB contains or references information describing how the program intends to access the data set.

It forms an important interface between:

```text
Program
   |
   v
DCB
   |
   v
Access Method
   |
   v
MVS I/O
```

---

# 28. DD Names

A program normally does not contain the complete physical identity of every data set it uses.

Instead, it refers to a logical **DD name**.

Suppose the program uses:

```text
INPUT
```

JCL can associate that name with an actual data set:

```jcl
//INPUT DD DSN=USER.TEST.DATA,DISP=SHR
```

Thus:

```text
Program
   |
   | DDNAME=INPUT
   v
JCL DD Statement
   |
   v
USER.TEST.DATA
   |
   v
Allocated Volume
   |
   v
Physical Device
```

This indirection is one of the most important abstractions in MVS programming.

The same executable program can process different data sets without being rebuilt.

---

# 29. OPEN and CLOSE

Before using many data sets, a program issues `OPEN`.

For example:

```asm
         OPEN  (INDCB,(INPUT))
```

OPEN establishes the relationship among:

- the DCB,
- JCL allocation information,
- data-set characteristics,
- access-method structures,
- device-related structures.

When processing finishes:

```asm
         CLOSE (INDCB)
```

releases or finalizes the corresponding data-management environment.

---

# 30. Access Methods

MVS provides access methods between applications and lower-level I/O.

Important examples include:

- BSAM — Basic Sequential Access Method
- QSAM — Queued Sequential Access Method
- BPAM — Basic Partitioned Access Method
- BDAM — Basic Direct Access Method
- ISAM — Indexed Sequential Access Method
- VSAM — Virtual Storage Access Method

These are not simply libraries in the modern sense.

They define significant portions of the programming model used to access particular classes of data.

---

# 31. QSAM

QSAM provides queued sequential processing.

A program can perform operations conceptually resembling:

```asm
         OPEN  (INDCB,(INPUT))

LOOP     GET   INDCB,BUFFER
         ...
         B     LOOP

         CLOSE (INDCB)
```

The application operates principally on logical records.

QSAM handles much of the buffering and physical I/O activity.

The layers can be visualized as:

```text
Application
     |
     | GET / PUT
     v
    QSAM
     |
     v
MVS I/O Services
     |
     v
Channel Program
     |
     v
Device
```

---

# 32. Basic Access Methods

Basic access methods such as BSAM expose more of the underlying block-I/O operation.

This gives the programmer more control but also requires greater responsibility.

The distinction is broadly:

```text
Queued Access Method
        |
        +--> more buffering handled by system

Basic Access Method
        |
        +--> more explicit control by program
```

Systems programs often operate at lower levels than ordinary applications.

---

# 33. Device Independence

One of MVS's major objectives is to prevent normal programs from depending unnecessarily on physical device addresses.

A program requests:

```text
INPUT
```

JCL identifies:

```text
USER.TEST.DATA
```

MVS allocation determines:

```text
volume
```

and ultimately:

```text
physical device
```

Therefore:

```text
Program
   |
   v
Logical Data Set
   |
   v
Allocation
   |
   v
Device
```

This permits hardware configuration and data placement to change without requiring corresponding changes to ordinary application code.

---

# 34. System/370 Channel I/O

At the hardware level, System/370 uses channels to perform I/O.

The CPU does not normally copy every byte between memory and a peripheral itself.

Instead:

```text
CPU
 |
 | starts I/O
 v
Channel
 |
 v
Control Unit
 |
 v
Device
```

The channel executes a sequence of:

**CCWs — Channel Command Words**

A channel program describes operations such as:

- read,
- write,
- control,
- sense,
- transfer within the channel program.

This allows the CPU to perform other work while the channel handles the device operation.

---

# 35. Asynchronous I/O

System/370 I/O is fundamentally asynchronous.

```text
CPU                            Channel

Start I/O -------------------> begins operation

execute other
instructions

                               operation completes
                                      |
                                      v
<-------------------------- I/O interruption
```

MVS receives the interruption, processes device status, and eventually makes the completion visible to the requesting software.

This is one reason ECBs and WAIT/POST are so important in MVS.

---

# 36. EXCP

Systems programs requiring lower-level device access can use:

**EXCP — Execute Channel Program**

At this level the program operates much closer to System/370 channel architecture.

Conceptually:

```text
High-Level Application
         |
         v
     QSAM/BSAM
         |
         v
      MVS I/O
         |
         v
   Channel Program
         |
         v
       CCWs
```

With EXCP:

```text
Systems Program
         |
         v
        EXCP
         |
         v
Program-Supplied Channel Structures
         |
         v
      MVS I/O
         |
         v
      Channel
```

The program gains control but assumes more responsibility.

For most general-purpose programs, access methods are preferable.

For device-oriented systems programming, understanding EXCP and channel programs becomes important.

---

# 37. I/O Control Structures

MVS uses numerous control blocks to connect logical data-set operations with physical I/O.

Among the important structures encountered by systems programmers are:

- DCB — Data Control Block
- DEB — Data Extent Block
- UCB — Unit Control Block
- JFCB — Job File Control Block
- TIOT — Task Input/Output Table

A simplified relationship is:

```text
Program
   |
   v
DCB
   |
   v
Data-Set / Allocation Structures
   |
   v
Device Structures
   |
   v
UCB
   |
   v
Physical Device
```

The exact relationships are more complex, but the important principle is that MVS represents its operating state through interconnected control blocks.

---

# 38. JES

The **Job Entry Subsystem** handles major portions of batch-job entry and output processing.

MVS 3.8 installations commonly use JES2 or JES3. A TK5 environment normally presents JES2.

JES and MVS should not be regarded as identical.

A simplified flow is:

```text
JCL Submission
      |
      v
     JES2
      |
      v
 Input Spool
      |
      v
 Job Queue
      |
      v
 Initiator
      |
      v
 MVS Execution
      |
      v
SYSOUT Data
      |
      v
 Output Spool
      |
      v
 Printer / Punch / Other Destination
```

JES handles the external flow of batch work around the MVS execution environment.

---

# 39. JCL

**JCL — Job Control Language** describes work to be performed.

Three fundamental statements are:

```text
JOB
EXEC
DD
```

The JOB statement describes the job.

The EXEC statement describes a program or procedure to execute.

The DD statement describes data required by a job step.

Example:

```jcl
//HELLO    JOB ...
//RUN      EXEC PGM=HELLO
//STEPLIB  DD DSN=USER.LOADLIB,DISP=SHR
//INPUT    DD DSN=USER.INPUT,DISP=SHR
//SYSPRINT DD SYSOUT=*
```

JCL is not merely a scripting language.

It is also a **resource-description language**.

It tells the operating environment what resources the program requires without embedding those choices directly into the executable.

---

# 40. Job Steps

A job can execute several steps:

```jcl
//JOB1     JOB ...
//ASM      EXEC PGM=IFOX00
//...
//LINK     EXEC PGM=IEWL
//...
//GO       EXEC PGM=MYPROG
//...
```

This produces a workflow such as:

```text
ASM
 |
 | object module
 v
LINK
 |
 | load module
 v
GO
```

The completion status of one step can influence whether subsequent steps execute.

This is the classic MVS compile/link/run model.

---

# 41. Initiators

An **initiator** selects eligible work and executes job steps.

Conceptually:

```text
JES Queue
    |
    v
Initiator
    |
    +--> establish job-step environment
    |
    +--> allocate resources
    |
    +--> load program
    |
    +--> execute
    |
    +--> perform termination processing
    |
    `--> proceed to next step
```

Multiple initiators allow multiple batch jobs to execute concurrently.

Job classes and system configuration influence which work an initiator can select.

---

# 42. Spooling

**SPOOL** historically means:

**Simultaneous Peripheral Operations On-Line**

Instead of tying an executing job directly to a slow card reader or printer, data is staged on faster storage.

Input:

```text
Card Reader / Submitted Job
          |
          v
       Spool DASD
          |
          v
       Job Queue
          |
          v
       Execution
```

Output:

```text
Program
   |
   v
SYSOUT
   |
   v
Spool DASD
   |
   v
Output Queue
   |
   v
Printer
```

The program can therefore complete before the physical printer has produced its output.

Under Hercules, host files often represent the external side of these historically physical unit-record devices.

---

# 43. SYSOUT

A DD statement such as:

```jcl
//SYSPRINT DD SYSOUT=*
```

directs output into the JES spool environment.

The program writes output without directly controlling a printer.

JES later determines its disposition.

This provides another example of MVS/JES separating the program's logical requirements from physical devices.

---

# 44. Interactive Computing

MVS is strongly associated with batch processing, but it also supports interactive operation.

A major interactive environment is:

**TSO — Time Sharing Option**

Conceptually:

```text
Terminal
   |
   v
Communications System
   |
   v
TSO
   |
   v
MVS Address Space
   |
   v
Command / Program
```

A TSO user receives an interactive MVS environment while still operating within the larger MVS resource-management architecture.

---

# 45. Communications

Communications in the MVS 3.8 period differ considerably from the modern TCP/IP-centered model.

Important IBM technologies included:

- telecommunications access methods,
- VTAM,
- SNA,
- remote terminals,
- remote job entry.

A typical terminal path could resemble:

```text
Terminal
   |
   v
Communications Controller
   |
   v
VTAM / Communications Services
   |
   v
TSO or Application
```

Communications programming should therefore be viewed as a substantial subsystem of MVS rather than merely a collection of socket calls.

---

# 46. Interprocess Communication

MVS provides several mechanisms serving purposes now grouped under **interprocess communication**.

These include:

- common storage,
- shared control blocks,
- ECBs,
- WAIT/POST,
- ENQ/DEQ,
- cross-task communication,
- data sets,
- specialized messaging facilities,
- IPCF.

**IPCF — Inter-Process Communication Facility** provides structured communications among participating address spaces.

The MVS IPC model should not be forced into the later UNIX vocabulary of:

- pipes,
- POSIX signals,
- sockets,
- POSIX shared-memory objects.

MVS evolved around different abstractions.

---

# 47. Protection

System protection begins with System/370 hardware.

Important architectural mechanisms include:

- supervisor/problem state,
- privileged instructions,
- storage protection,
- storage keys,
- interruption mechanisms.

MVS builds additional software protection on those mechanisms.

Thus:

```text
Application
    |
    v
MVS Protection Rules
    |
    v
System/370 Protection
    |
    v
Hardware
```

A problem-state application cannot simply bypass MVS and execute arbitrary privileged operations.

---

# 48. Security

Security in an MVS installation includes issues such as:

- user identification,
- authentication,
- data-set access,
- resource authorization,
- privileged operations,
- auditing,
- installation policy.

IBM security products such as RACF can provide extensive authorization facilities.

However, security configuration was highly installation-dependent.

It is useful to distinguish three layers:

```text
Hardware Protection
        |
        v
Operating-System Protection
        |
        v
Installation Security Policy
```

These are related but not identical.

---

# 49. Operator Control

MVS assumes an actively managed computing installation.

The operator console provides a privileged interface to the system.

Operators can perform actions such as:

- display system status,
- start components,
- stop components,
- control devices,
- respond to mount requests,
- communicate with jobs,
- cancel jobs,
- control JES,
- vary devices online or offline,
- initiate shutdown procedures.

The operator is therefore part of the traditional operational model.

```text
                  Operator
                     |
                     v
               System Console
                     |
                     v
+-------------------------------------------+
|                    MVS                    |
|                                           |
| Jobs | JES | Devices | Tasks | Subsystems |
+-------------------------------------------+
```

---

# 50. Messages and Replies

MVS components can issue messages requiring operator attention.

Some messages are informational.

Others request a response.

For example, a system component might require:

- a volume to be mounted,
- a device decision,
- confirmation of an operation,
- configuration information.

The operator-console model is consequently integrated into normal system operation much more deeply than the console of a typical modern personal computer.

---

# 51. IPL

Starting the system is called:

**IPL — Initial Program Load**

IPL begins as a hardware operation and eventually transfers control to the operating system.

A highly simplified sequence is:

```text
System/370 Hardware
       |
       | IPL
       v
Initial Loader
       |
       v
MVS Nucleus
       |
       v
System Initialization
       |
       +--> Storage Management
       +--> I/O Management
       +--> System Services
       +--> JES
       +--> Communications
       +--> Other Subsystems
       |
       v
Operational System
```

IPL should not be confused with merely starting a user program.

It establishes the operating-system environment itself.

---

# 52. System Generation

Mainframe operating systems of this period often require considerably more installation-time system generation and configuration than modern general-purpose operating systems.

A **SYSGEN** determines or builds significant portions of the operating-system configuration.

The installation can specify characteristics such as:

- processor configuration,
- devices,
- system components,
- operating parameters,
- supporting facilities.

Configuration is therefore distributed among:

- generated system components,
- system data sets,
- parameter libraries,
- startup procedures,
- JES configuration,
- communications configuration,
- operator commands.

The boundary between "installing" and "configuring" the operating system is consequently different from modern systems.

---

# 53. Control Blocks

One of the most important concepts for an MVS systems programmer is the **control block**.

MVS represents much of its internal state using structured blocks of storage linked together by pointers.

Examples include:

| Control block | General role |
|---|---|
| TCB | Task information |
| ECB | Event synchronization |
| DCB | Data-set/access information |
| DEB | Data-set extent/device information |
| UCB | Device information |
| JFCB | Job/file-control information |
| TIOT | Task I/O allocation information |

Conceptually:

```text
TCB
 |
 +--> Task information
 |
 +--> Related structures
          |
          +--> I/O structures
          |
          +--> Data-set structures
          |
          +--> Synchronization structures
```

Much MVS diagnostic and systems programming consists of locating one control block and following pointers to related structures.

---

# 54. Control-Block Topology

Modern programmers often think principally in terms of APIs.

An MVS systems programmer must additionally think in terms of **control-block topology**.

For example:

```text
Task
 |
 v
TCB
 |
 +-------> TIOT
 |           |
 |           +----> allocated DD information
 |
 +-------> related task structures
 |
 `-------> synchronization/recovery information
```

The exact topology depends on the subsystem and service involved.

The important principle is that the operating system exposes much of its internal state through documented or semi-documented structures.

This makes MVS unusually tangible to an assembler systems programmer.

---

# 55. Return Codes

Normal completion and abnormal completion are separate concepts.

A normally terminating program commonly supplies a **return code**, conventionally through register 15.

Conceptually:

```asm
         SR    15,15
         BR    14
```

sets R15 to zero before returning.

A caller or JCL processing can use completion status to decide what happens next.

Typical conventions distinguish:

```text
Return Code
    |
    +--> normal completion with status

ABEND
    |
    `--> abnormal completion
```

The exact interpretation of nonzero return codes belongs to the particular program or utility.

---

# 56. Program Termination

Normal termination can occur by returning through the expected linkage or through appropriate system facilities.

During termination, MVS can perform cleanup involving resources associated with the task or job step.

Abnormal termination invokes ABEND processing and potentially recovery facilities.

Thus termination is not simply:

```text
stop CPU
```

It is an operating-system operation involving task and resource management.

---

# 57. Timing Services

MVS provides facilities for obtaining and managing time-related information.

Uses include:

- obtaining time of day,
- measuring elapsed time,
- measuring CPU usage,
- setting intervals,
- implementing timeouts,
- scheduling delayed actions.

Hardware timer facilities generate architectural events; MVS converts those facilities into operating-system services.

Again:

```text
System/370 Timer Hardware
          |
          v
        MVS
          |
          v
Programmer-Visible Timing Service
```

---

# 58. Accounting

MVS originated in environments where computer resources were expensive and often shared among many departments or customers.

Consequently, accounting is a significant operating-system concern.

Resources of interest can include:

- CPU time,
- elapsed time,
- I/O activity,
- storage,
- job execution,
- printed output.

JCL, JES, SMF, and installation procedures can all participate in resource accounting and measurement.

---

# 59. SMF

**SMF — System Management Facilities** provides structured recording of system activity.

SMF records can describe events such as:

- job activity,
- step activity,
- resource usage,
- system events,
- subsystem events.

Conceptually:

```text
System Activity
      |
      v
     SMF
      |
      v
SMF Records
      |
      v
Accounting / Reporting / Analysis
```

For systems programming, SMF is important because it provides a standardized way for MVS and participating software to record operational information.

---

# 60. Libraries

MVS makes extensive use of partitioned data sets as libraries.

Examples include:

- source libraries,
- macro libraries,
- procedure libraries,
- load libraries.

A program may be found through library-search mechanisms rather than through an explicit disk path.

For example:

```jcl
//STEPLIB DD DSN=USER.LOADLIB,DISP=SHR
```

can identify a private load library used for a particular job step.

System libraries provide commonly available modules.

This is the MVS equivalent of an executable/library search environment, although the mechanism differs substantially from modern filesystem paths.

---

# 61. Reentrant Code

Because memory and virtual-storage resources are shared, MVS places considerable value on **reentrant** programs.

A reentrant program can be safely used by multiple executions without modifying shared program text or otherwise corrupting shared state.

Conceptually:

```text
                 Shared Program Code
                  /              \
                 /                \
             Task A              Task B
               |                   |
         private data         private data
```

Reentrant design permits code to be shared efficiently.

This is particularly important for frequently used system routines.

---

# 62. Reusable and Refreshable Programs

IBM program-management terminology distinguishes properties such as whether a module is:

- reentrant,
- reusable,
- refreshable.

These describe different guarantees concerning whether program storage can safely be reused, shared, or reconstructed.

The important systems-programming lesson is:

> Code-sharing properties are part of the program's contract with the operating system.

Careless modification of program text or shared state can violate that contract.

---

# 63. Putting Program Execution Together

Consider a simple program invoked from a batch job.

```text
JCL
 |
 v
JES2
 |
 v
Job Queue
 |
 v
Initiator
 |
 v
Address Space
 |
 v
Task / TCB
 |
 v
Load Module
 |
 v
Program Entry
 |
 +--> establish register conventions
 |
 +--> establish save area
 |
 +--> obtain storage
 |
 +--> OPEN data sets
 |
 +--> process records
 |
 +--> CLOSE data sets
 |
 +--> release storage
 |
 `--> return completion code
```

Each layer performs a distinct role.

---

# 64. Putting I/O Together

Suppose an assembler program reads a sequential data set using QSAM.

```text
Application
    |
    | GET
    v
   QSAM
    |
    | buffer empty?
    v
MVS I/O Processing
    |
    v
Channel Program
    |
    v
Channel
    |
    v
Control Unit
    |
    v
DASD
```

If physical I/O is required:

```text
Task
 |
 | request I/O
 v
MVS
 |
 | start channel operation
 v
WAIT
 |
 |                          Channel performs I/O
 |                                  |
 |                           device completes
 |                                  |
 |                         I/O interruption
 |                                  |
 |                                MVS
 |                                  |
 +------------- POST <--------------+
 |
 v
READY
 |
 v
RUNNING
```

This single example connects several major concepts:

- access methods,
- channels,
- interruptions,
- tasks,
- ECBs,
- WAIT/POST,
- scheduling.

---

# 65. Putting Exception Processing Together

Suppose a program references an invalid address.

```text
Assembler Program
       |
       v
Faulting Instruction
       |
       v
System/370 Program Interruption
       |
       v
MVS Interruption Processing
       |
       +--> established recovery?
       |          |
       |          v
       |     Recovery Routine
       |
       `--> no recovery / recovery fails
                  |
                  v
                ABEND
                  |
                  v
           Diagnostic Processing
                  |
                  v
             Task Termination
```

The hardware detects the architectural error.

MVS decides what operating-system action follows.

---

# 66. Putting Batch Processing Together

A conventional assemble-link-run job can be viewed as:

```text
                  JES2
                    |
                    v
                 JOB
                    |
        +-----------+-----------+
        |                       |
        v                       |
      ASM STEP                  |
        |                       |
        v                       |
 Object Module                  |
        |                       |
        v                       |
      LINK STEP                 |
        |                       |
        v                       |
   Load Module                  |
        |                       |
        v                       |
       GO STEP                  |
        |                       |
        v                       |
   Program Output               |
        |                       |
        +-----------> SYSOUT ---+
                                |
                                v
                            JES Spool
                                |
                                v
                             Printer
```

This is the classic environment in which an IFOX assembler programmer works.

---

# 67. Hardware Architecture versus MVS Service

A useful classification is:

| Concept | Primarily System/370 | Primarily MVS |
|---|---:|---:|
| General registers | Yes | |
| PSW | Yes | |
| Machine instructions | Yes | |
| DAT hardware | Yes | |
| Storage keys | Yes | |
| Interruptions | Yes | |
| Channels | Yes | |
| CCWs | Yes | |
| Address spaces | | Yes |
| Tasks/TCBs | | Yes |
| GETMAIN/FREEMAIN | | Yes |
| WAIT/POST | | Yes |
| ENQ/DEQ | | Yes |
| ABEND | | Yes |
| Recovery facilities | | Yes |
| DCBs | | Yes |
| Access methods | | Yes |
| EXCP interface | | Yes |
| Data sets | | Yes |
| JCL | | Yes |
| JES | | Yes |
| Spooling | | Yes |
| TSO | | Yes |
| Operator commands | | Yes |

The boundary is not absolute.

MVS is deliberately designed around System/370 architectural facilities, so many MVS abstractions correspond closely to underlying hardware mechanisms.

---

# 68. MVS versus a Modern UNIX-Like Mental Model

Approximate analogies can help, provided they are not taken literally.

| MVS concept | Rough modern analogy |
|---|---|
| Address space | Process address space |
| TCB/task | Thread/process execution context |
| Load module | Executable/shared program image |
| GETMAIN | Dynamic allocation |
| FREEMAIN | Dynamic deallocation |
| LINK | Dynamic program call |
| ATTACH | Create concurrent execution |
| WAIT/POST | Event wait/signal |
| ENQ/DEQ | Named locking |
| Data set | File/storage object |
| PDS | Library/directory-like container |
| DD name | Logical I/O binding |
| QSAM | Buffered record I/O |
| EXCP | Low-level device I/O |
| SVC | System-call trap |
| ABEND | Abnormal process termination |
| SYSOUT | Spool output |
| JES | Batch/spool workload manager |
| JCL | Job/resource description |
| TSO | Interactive user environment |

These analogies are useful only as orientation.

MVS has its own architecture and should ultimately be understood in its own terminology.

---

# 69. A Systems Programmer's Layer Model

For systems programming, MVS can be approached in layers:

```text
+--------------------------------------+
| Application / Utility Program        |
+--------------------------------------+
| MVS Macros and Programming Services  |
+--------------------------------------+
| Data / Task / Storage Management     |
+--------------------------------------+
| Supervisor Services                  |
+--------------------------------------+
| Interrupt and I/O Processing         |
+--------------------------------------+
| System/370 Architecture              |
+--------------------------------------+
| Processor / Storage / Channels       |
+--------------------------------------+
| Control Units and Devices            |
+--------------------------------------+
```

A general-purpose application mostly remains near the top.

A systems program may deliberately descend through several layers.

---

# 70. Essential IFOX Concepts for MVS Programming

An assembler programmer working on MVS should become comfortable with several groups of concepts.

## Machine level

```text
Registers
PSW
Condition code
Branches
Address calculation
Storage operands
Privileged state
Interruptions
```

## Linkage level

```text
R1
R13
R14
R15
Save areas
Parameter lists
Base registers
```

## Storage level

```text
Address spaces
Virtual storage
GETMAIN
FREEMAIN
Common/private storage
```

## Task level

```text
TCB
ATTACH
WAIT
POST
ENQ
DEQ
```

## Data level

```text
Data sets
DD names
DCB
OPEN
CLOSE
GET
PUT
READ
WRITE
Access methods
```

## Failure level

```text
Program interruptions
ABEND
Completion codes
Dumps
Recovery
```

## Batch level

```text
JCL
JOB
EXEC
DD
JES2
Initiators
SYSOUT
Spooling
```

These concepts form the practical vocabulary of MVS programming.

---

# 71. Minimal General-Purpose Program Model

A conventional assembler program can be thought of as following this lifecycle:

```text
Receive Control
      |
      v
Save Caller State
      |
      v
Establish Addressability
      |
      v
Establish Own Save Area
      |
      v
Obtain Required Storage
      |
      v
Open Required Data Sets
      |
      v
Perform Work
      |
      +--> invoke services
      +--> call programs
      +--> perform I/O
      +--> wait for events
      |
      v
Close Data Sets
      |
      v
Release Storage
      |
      v
Set Return Code
      |
      v
Restore Caller State
      |
      v
Return
```

This is a useful starting template for understanding ordinary MVS assembler programs.

---

# 72. Minimal Systems-Programming Model

A systems program may additionally need to understand:

```text
PSW
 |
 v
Interruption Handling

TCB
 |
 v
Task Structures

DCB / DEB / UCB
 |
 v
I/O Structures

ECB
 |
 v
Asynchronous Events

SVC
 |
 v
Supervisor Services

EXCP
 |
 v
Channel Programs
 |
 v
CCWs

ABEND
 |
 v
Recovery and Dumps
```

At this level, the distinction between "using MVS" and "understanding MVS internals" begins to narrow.

---

# 73. The MVS Programmer's Central Abstractions

The most important abstractions can be summarized as follows.

### Address Space

The virtual-storage environment in which execution occurs.

### Task

The schedulable execution entity within an address space.

### Load Module

The executable program representation loaded by MVS.

### Save Area

A structure supporting conventional program linkage and register preservation.

### SVC

An architectural mechanism for controlled entry into supervisor services.

### ECB

A representation of an event used extensively with WAIT/POST.

### ENQ Resource

A named resource whose ownership can be serialized.

### Data Set

The primary MVS persistent-data abstraction.

### DD Name

The logical connection between a program and externally specified data.

### DCB

The program-visible control structure describing data-set access.

### Access Method

The MVS software layer implementing particular styles of data access.

### EXCP

A lower-level interface for initiating channel-program-based I/O.

### ABEND

The MVS abstraction for abnormal task or step termination.

### JCL

The language describing batch execution and resource requirements.

### JES

The subsystem managing job entry, queues, spool data, and output processing.

### Control Block

The general MVS technique for representing and connecting operating-system state.

---

# 74. Final Architectural View

The entire environment can be reduced to the following conceptual picture:

```text
                         PROGRAMMER
                             |
                             v
                     IFOX / Application
                             |
            +----------------+----------------+
            |                |                |
            v                v                v
        Programs          Storage          Data Sets
            |                |                |
        LINK/XCTL         GETMAIN          DCB/OPEN
        ATTACH            FREEMAIN         GET/PUT
            |                |                |
            +----------------+----------------+
                             |
                             v
                      MVS SERVICES
                             |
       +---------------------+---------------------+
       |                     |                     |
       v                     v                     v
 Task Management       Data Management       Recovery
 WAIT/POST             Access Methods        ABEND
 ENQ/DEQ               EXCP                  STAE
       |                     |                     |
       +---------------------+---------------------+
                             |
                             v
                       SUPERVISOR
                             |
              +--------------+--------------+
              |                             |
              v                             v
       Virtual Storage                 I/O Management
              |                             |
              v                             v
             DAT                         Channels
              |                             |
              v                             v
        Real Storage                      CCWs
                                            |
                                            v
                                      Control Units
                                            |
                                            v
                                         Devices

                     Surrounding this:

                +---------------------------+
                | JES2 / JCL / Spooling     |
                | TSO / Communications      |
                | Security                  |
                | SMF / Accounting          |
                | Operator Control          |
                | IPL / Initialization      |
                +---------------------------+
```

The essential idea is that MVS provides a structured operating environment between a System/370 program and the physical machine.

A program does not normally allocate physical memory, dispatch processors, manipulate disk-device addresses, operate printers, or directly handle hardware interruptions. Instead it works through MVS abstractions:

```text
Virtual storage instead of physical memory

Tasks instead of direct CPU dispatch

GETMAIN instead of physical-memory allocation

WAIT/POST instead of polling hardware events

ENQ/DEQ instead of ad hoc shared-resource locking

Data sets instead of physical disk locations

DD names instead of embedded device assignments

Access methods instead of raw channel programs

ABEND/recovery instead of simply halting the processor

JCL instead of embedding execution configuration in the program

JES spool output instead of directly owning a printer
```

At the same time, MVS retains a close relationship with System/370 architecture. An assembler systems programmer can progressively descend from macros and control blocks through SVCs, interruptions, EXCP, channel programs, CCWs, storage protection, and the PSW until reaching the machine architecture itself.

That combination—**high-level operating-system abstractions built very visibly upon the underlying hardware architecture**—is one of the defining characteristics of MVS systems programming.

