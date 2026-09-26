# System/370 Architecture — A Programmer's Reference

## 1. Architectural Perspective

IBM System/370 is a family of general-purpose mainframe computers introduced in 1970 as the successor to System/360.

The most useful way to study System/370 is as an **instruction-set and machine architecture**, rather than as a particular physical computer. Different System/370 models varied substantially in implementation, speed, memory capacity, channel configuration, and peripheral equipment while presenting substantially the same architecture to a machine-language programmer.

This reference concentrates on the aspects visible to a systems programmer:

- data representation
- registers
- instructions
- addressing
- arithmetic and logical operations
- branching
- condition codes
- storage
- protection
- virtual storage
- privileged execution
- interruptions
- timing
- multiprocessing
- channel I/O
- machine initialization and control

MVS is frequently associated with System/370, but **MVS is not part of the processor architecture**. Concepts such as JCL, datasets, tasks, ABEND processing, and most IPC mechanisms are operating-system facilities and are deliberately outside the main scope here.

---

# 2. Fundamental Data Organization

## 2.1 Bits and Bytes

The fundamental addressable storage unit is the **8-bit byte**.

Storage addresses identify bytes.

Larger quantities are constructed from consecutive bytes:

| Quantity | Size |
|---|---:|
| Byte | 8 bits |
| Halfword | 16 bits / 2 bytes |
| Fullword | 32 bits / 4 bytes |
| Doubleword | 64 bits / 8 bytes |

System/370 is therefore commonly described as a **32-bit architecture**, although it supports operations on several operand sizes.

---

## 2.2 Big-Endian Representation

System/370 stores multibyte binary values **most-significant byte first**.

For example, the fullword:

```text
12345678
```

in hexadecimal is stored at increasing addresses as:

```text
Address +0   12
Address +1   34
Address +2   56
Address +3   78
```

This organization is now commonly called **big-endian**.

---

## 2.3 Binary Integers

Signed binary integers use **two's-complement representation**.

Common integer sizes are:

- 16-bit halfword
- 32-bit fullword
- 64-bit doubleword in certain operations

An IFOX assembler declaration illustrates the storage sizes:

```asm
BYTE     DC X'12'
HALF     DC H'1234'
FULL     DC F'123456'
DOUBLE   DC D'123.456'
```

`H` and `F` describe binary integer constants. `D` above denotes a double-precision floating-point constant, not a 64-bit integer declaration.

---

## 2.4 Character Data

System/370 normally uses **EBCDIC** for character representation.

Assembler character constants can be written:

```asm
MESSAGE  DC C'HELLO, WORLD'
```

The assembler translates the characters into the appropriate EBCDIC byte values.

Character data is fundamentally byte-oriented; the processor does not attach a type such as "string" to the storage.

---

## 2.5 Packed Decimal

System/370 has extensive hardware support for decimal arithmetic.

Packed decimal stores two decimal digits per byte, except that the low-order nibble of the final byte contains the sign.

For example:

```asm
VALUE    DC PL4'1234567'
```

allocates four bytes containing a signed packed-decimal value.

Instructions exist for operations such as:

- decimal addition
- subtraction
- multiplication
- division
- comparison
- conversion

This hardware support was particularly important for commercial computing.

---

# 3. Storage Alignment

System/370 defines **natural boundaries** for many quantities.

Typical boundaries are:

| Quantity | Natural boundary |
|---|---:|
| Byte | 1 byte |
| Halfword | 2 bytes |
| Fullword | 4 bytes |
| Doubleword | 8 bytes |

Assembler programs commonly explicitly align data:

```asm
         DS 0F
VALUE    DC F'100'
```

`DS 0F` reserves no storage but advances the location counter to a fullword boundary when necessary.

Similarly:

```asm
         DS 0D
FLOAT    DC D'1.0'
```

establishes doubleword alignment.

Alignment requirements vary with the instruction and operand involved; they should be regarded as part of each instruction's architectural definition rather than as a universal rule that every multibyte operand must always be naturally aligned.

---

# 4. General Registers

The System/370 programmer sees **16 general-purpose registers**, numbered:

```text
R0 through R15
```

Each is 32 bits wide.

Conceptually:

```text
R0   32 bits
R1   32 bits
...
R15  32 bits
```

These registers can contain:

- signed or unsigned binary values
- addresses
- indexes
- base addresses
- counters
- pointers
- temporary values

The architecture does not impose a universal role such as "stack pointer" upon one of them.

---

# 5. Conventional Register Usage

Although the hardware provides general-purpose registers, software conventions assign common meanings to some registers.

Typical assembler conventions include:

| Register | Common use |
|---|---|
| R0 | temporary / special instruction operand |
| R1 | parameter pointer |
| R13 | save-area pointer |
| R14 | return address |
| R15 | entry address / return code |

These are **software conventions**, not fundamental properties of the CPU.

A standalone machine-code program is free to use registers differently unless some external calling convention must be obeyed.

---

# 6. Register Zero Is Special in Address Formation

Register 0 requires special attention.

When a register field is used as a **base or index register**, specifying register zero generally means:

> no base or index register

rather than "use the contents of R0."

Thus R0 is a perfectly usable arithmetic register but has special semantics in address calculation.

This distinction is fundamental when reading System/370 machine instructions.

---

# 7. Program Status Word

The **Program Status Word (PSW)** describes essential CPU execution state.

Conceptually, it contains information such as:

- current instruction address
- condition code
- interrupt masks
- execution mode/control information
- protection-related state

The PSW therefore combines roles that other architectures may divide among a:

- program counter
- flags register
- interrupt-control register
- processor-status register

The PSW is one of the central concepts of the System/370 architecture.

---

# 8. The Condition Code

System/370 does not use a collection of individual condition flags in quite the style of many microprocessors.

Instead, the PSW contains a **two-bit condition code (CC)**:

```text
CC = 0
CC = 1
CC = 2
CC = 3
```

The interpretation depends upon the instruction that established it.

For a comparison, for example, the states can represent relationships such as:

```text
equal
low
high
```

For arithmetic instructions, they may indicate:

```text
zero
negative
positive
overflow
```

The exact interpretation must therefore be understood in the context of the preceding instruction.

---

# 9. Conditional Branching

A typical comparison might be:

```asm
         C     3,VALUE
         BE    EQUAL
         BL    LOWER
         BH    HIGHER
```

The `C` instruction compares a fullword in a register against a fullword in storage and establishes the condition code.

The branch instructions then test that condition.

Other familiar mnemonics include:

```text
B     unconditional branch
BE    branch equal
BNE   branch not equal
BH    branch high
BL    branch low
BNH   branch not high
BNL   branch not low
```

Many of these are assembler mnemonic forms of the underlying **Branch on Condition** instruction.

---

# 10. Instruction Formats

System/370 instructions use several standardized instruction formats.

Important forms include:

- RR — register-to-register
- RX — register-and-indexed-storage
- RS — register-and-storage
- SI — storage-and-immediate
- SS — storage-to-storage

This regularity is one of the characteristic features inherited from System/360.

For example:

```asm
         LR    3,4
```

is an RR-style register operation.

```asm
         L     3,VALUE
```

loads from storage using an RX-format instruction.

```asm
         MVC   TARGET(10),SOURCE
```

uses an SS-format storage-to-storage instruction.

---

# 11. Effective Address Formation

One of the most important System/370 concepts is **base-displacement addressing**.

For a typical RX-format storage operand, the effective address is:

```text
EA = base register + index register + displacement
```

The displacement field is 12 bits:

```text
0 through 4095
```

The base and index components come from general registers.

If either register field specifies zero, that component contributes zero rather than the contents of R0.

---

# 12. Base Registers

Because the instruction does not normally contain a complete storage address, assembler programs establish one or more registers as **base registers**.

For example:

```asm
START    CSECT
         USING START,12
```

`USING` tells the assembler that register 12 can be used as a base for addressing locations relative to `START`.

Importantly:

> `USING` does not load register 12.

It is an assembler directive, not a machine instruction.

The program must arrange for R12 actually to contain the corresponding address.

This distinction between **assembler addressability** and **machine execution** is crucial in System/370 programming.

---

# 13. Loading Addresses

The `LA` instruction computes an effective address and places it into a general register.

For example:

```asm
         LA    3,BUFFER
```

places the address of `BUFFER` in R3.

Contrast this with:

```asm
         L     3,BUFFER
```

which loads the **32-bit contents stored at `BUFFER`**.

Thus:

```text
LA → address
L  → contents
```

This distinction appears constantly in assembler programming.

---

# 14. Integer Data Movement

Important instructions include:

```asm
         L     3,VALUE
         ST    3,RESULT
         LR    4,3
         LH    5,SHORT
         STH   5,SHORT2
```

Conceptually:

```text
L    Load fullword
ST   Store fullword
LR   Load Register
LH   Load Halfword
STH  Store Halfword
```

A halfword loaded into a general register is extended appropriately to the register's 32-bit representation.

---

# 15. Integer Arithmetic

Representative instructions include:

```asm
         A     3,VALUE
         AR    3,4
         S     3,VALUE
         SR    3,4
```

where the `R` forms operate register-to-register.

Example:

```asm
         L     3,A
         A     3,B
         ST    3,C
```

implements conceptually:

```text
C = A + B
```

Arithmetic instructions generally establish the condition code.

---

# 16. Multiplication and Division

Multiplication and division expose an important architectural feature: some operations use **register pairs**.

Certain instructions treat adjacent general registers as a larger operand or result.

Consequently, register selection for these instructions is not arbitrary.

When reading or writing System/370 assembler, always consult the instruction definition for:

- required register parity
- which register receives which result
- operand width
- overflow behavior

---

# 17. Logical Operations

System/370 provides logical operations both in registers and storage.

Typical operations include:

```text
AND
OR
exclusive OR
logical compare
test under mask
```

Representative instructions include:

```asm
         NR    3,4
         OR    3,4
         XR    3,3
```

A particularly famous idiom is:

```asm
         XR    3,3
```

which XORs R3 with itself and therefore clears it to zero.

---

# 18. Masks and Bit Testing

System/370 software frequently manipulates individual fields using masks.

The **Test Under Mask** family is particularly characteristic.

Conceptually, these operations permit programs to ask:

```text
Are selected bits zero?
Are selected bits one?
Is there a mixture?
```

without first having to destructively alter the operand.

This is heavily used in systems programming for control bytes and bit fields.

---

# 19. Shift Operations

The architecture provides arithmetic and logical shifting.

Representative operations include:

- shift left single
- shift right single
- shift left double
- shift right double
- logical shifts
- arithmetic shifts

Arithmetic right shifts preserve the sign interpretation.

Logical shifts introduce zero bits.

Double-length variants operate on register pairs and permit manipulation of quantities wider than a single 32-bit register.

---

# 20. Rotates

Unlike architectures in which rotate instructions are central to everyday integer programming, System/370 programming is more strongly characterized by its shift, mask, logical, and bit-manipulation facilities.

When translating algorithms from architectures such as the PDP-11 or later microprocessors, one should therefore avoid assuming that their exact rotate-and-carry idioms map directly onto System/370 instructions.

---

# 21. Character and Storage-to-Storage Operations

A major characteristic of System/370 is that not everything must pass through general registers.

The architecture includes powerful **storage-to-storage** instructions.

For example:

```asm
         MVC   TARGET(20),SOURCE
```

moves 20 bytes.

Conceptually:

```text
SOURCE → TARGET
```

without requiring a software loop that loads and stores each byte individually.

Other instructions compare, translate, and manipulate sequences of bytes.

---

# 22. Decimal Arithmetic

Packed-decimal instructions operate directly on storage operands.

Important operations include:

- Add Decimal
- Subtract Decimal
- Multiply Decimal
- Divide Decimal
- Compare Decimal
- Pack
- Unpack
- Convert between binary and decimal forms

This illustrates an important architectural philosophy:

> System/370 is not merely a load/store integer processor.

It contains substantial hardware support for business data processing.

---

# 23. Floating-Point Architecture

System/370 provides a separate floating-point facility.

Floating-point registers are distinct from the general-purpose registers.

The architecture supports IBM hexadecimal floating-point representations rather than the later IEEE-754 format.

Floating-point operations include:

- load/store
- add
- subtract
- multiply
- divide
- compare
- precision conversion

The representation and normalization rules are architecturally significant and differ substantially from modern IEEE floating point.

---

# 24. Branch and Linkage

A fundamental control-transfer mechanism is **Branch and Link**.

A branch-and-link operation both:

1. preserves information needed for return, and
2. transfers execution to another address.

This supports subroutine linkage without requiring a hardware call stack.

System/370 therefore does **not require a hardware-defined stack architecture** for procedure calls.

Software conventions build higher-level linkage mechanisms from registers and storage.

---

# 25. No Architecturally Mandatory Stack

This is an important contrast with many later architectures.

System/370 has:

- no dedicated stack-pointer register
- no fundamental PUSH instruction
- no fundamental POP instruction
- no mandatory hardware call stack

Programs can certainly construct stacks in memory.

However, the traditional IBM linkage model instead makes extensive use of:

- registers
- save areas
- branch-and-link instructions

A stack is therefore a **software data structure**, not a defining CPU mechanism.

---

# 26. Real Storage Addressing

Early System/370 systems continued the System/360-style 24-bit addressing model.

A 24-bit address permits:

```text
2^24 = 16,777,216 bytes
```

or:

```text
16 MiB
```

of addressability.

Thus the architecture combines:

- 32-bit general registers
- 24-bit addresses

This distinction is important: **register width and address width are not necessarily the same thing.**

---

# 27. Virtual Storage

Virtual storage became one of the defining System/370 developments.

Later System/370 architecture added **Dynamic Address Translation (DAT)**.

Conceptually:

```text
virtual address
      ↓
segment translation
      ↓
page translation
      ↓
real storage address
```

Programs can therefore execute using virtual addresses without requiring corresponding addresses to identify the same physical storage locations.

---

# 28. Segmentation and Paging

System/370 DAT uses a combination of:

- segments
- pages
- translation tables
- hardware translation state

The CPU translates virtual addresses through structures established by privileged software.

Translation failure can produce an interruption that allows an operating system to arrange for the required page to become available.

The mechanism is architectural.

Policies such as:

- which page to evict
- where pages reside on disk
- which process receives how much memory

belong to the operating system rather than the hardware architecture.

---

# 29. Translation Lookaside Buffer

Address translation would be expensive if the processor had to perform complete table lookup activity for every storage reference.

Implementations therefore use high-speed translation caching, commonly described in terms of a **Translation Lookaside Buffer (TLB)**.

Conceptually:

```text
virtual page → recently translated real page
```

The architectural rules define the required translation behavior; particular processor models can differ in their internal implementation.

---

# 30. Storage Protection

System/370 provides hardware mechanisms allowing storage access to be protected.

One important mechanism is **storage protection keys**.

Storage blocks can be associated with protection information, while the executing program has corresponding protection state.

The CPU can therefore detect prohibited storage accesses.

This mechanism supports operating-system isolation without requiring every program to voluntarily obey memory boundaries.

---

# 31. Problem State and Supervisor State

The processor distinguishes execution privilege.

Conceptually there are two important modes:

```text
problem state
supervisor state
```

Ordinary applications normally execute in problem state.

Instructions capable of directly changing critical machine state are privileged and require supervisor state.

Examples include operations associated with:

- I/O initiation
- machine-control state
- interruption control
- address-translation control

Attempting a privileged operation from problem state causes a program interruption rather than executing the operation.

---

# 32. Interruptions

IBM terminology generally uses **interruption** where many architectures use "interrupt" or "exception."

Major classes include:

- program interruptions
- supervisor-call interruptions
- external interruptions
- I/O interruptions
- machine-check interruptions

The architecture provides defined mechanisms for saving the current machine state and loading new execution state.

---

# 33. Program Interruptions

Program interruptions report conditions detected during instruction execution.

Examples include:

- invalid operation
- privileged operation
- addressing error
- protection violation
- specification error
- arithmetic exceptions
- translation exceptions

These are hardware architectural events.

What an operating system subsequently does—terminate a task, issue an ABEND, produce a dump, recover, or retry—is software policy.

Thus:

```text
hardware exception ≠ ABEND
```

An ABEND is an operating-system response or abstraction built above the machine interruption architecture.

---

# 34. Supervisor Call

The **SVC instruction** deliberately generates a supervisor-call interruption.

Conceptually:

```asm
         SVC   n
```

causes controlled transfer from ordinary execution into privileged software.

Architecturally, SVC provides a hardware mechanism for crossing the protection boundary.

What service number `n` means is defined by the operating system.

---

# 35. External Interruptions

External interruptions allow events outside the normal instruction stream to obtain processor attention.

Sources can include facilities such as:

- timers
- operator/external signals
- interprocessor signaling

Masking controls determine which classes of interruption are currently permitted.

---

# 36. Machine Checks

Hardware faults can generate **machine-check interruptions**.

These concern conditions such as processor, storage, or other machine malfunctions.

The architecture provides information enabling privileged software to determine what occurred and, where possible, recover or isolate the failure.

A severe failure can instead leave the machine unable to continue normally.

---

# 37. Wait State

System/370 can enter a **wait state** in which normal instruction execution stops while the processor awaits an interruption.

This is not necessarily an error.

A supervisor may deliberately place a CPU into a wait state when it has no work to execute.

A **disabled wait** is different: if the interruptions necessary to resume useful execution are disabled, the machine effectively stops pending operator or external intervention.

---

# 38. Timing Facilities

System/370 provides hardware timing facilities used for purposes such as:

- timekeeping
- scheduling
- interval timing
- accounting
- timeout detection

Depending upon architectural level and model, facilities include concepts such as:

- interval timer
- CPU timer
- time-of-day clock

These facilities can generate external interruptions.

---

# 39. Atomic Operations

Multiprogramming and multiprocessing require safe synchronization.

System/370 provides instructions suitable for implementing locks and other synchronization primitives.

A particularly important operation is **Compare and Swap**.

Conceptually:

```text
if memory == expected:
    memory = replacement
    report success
else:
    expected = memory
    report failure
```

The comparison and replacement are performed atomically with respect to competing processors.

This permits construction of:

- spin locks
- mutex primitives
- lock-free structures
- operating-system synchronization mechanisms

---

# 40. Multiprocessing

Some System/370 configurations support multiple processors sharing storage and I/O resources.

Architectural concerns therefore include:

- shared main storage
- processor synchronization
- atomic operations
- signaling between CPUs
- interruption handling
- serialization

Multiprocessing makes memory ordering and synchronization properties part of systems programming rather than merely an operating-system implementation detail.

---

# 41. System/370 I/O Philosophy

System/370 I/O differs dramatically from the simple device-register model common on minicomputers and microprocessors.

The CPU generally does **not** perform every byte transfer itself.

Instead, I/O is delegated to **channels**.

Conceptually:

```text
CPU
 │
 ├── Main Storage
 │
 └── Channel
       │
       └── Control Unit
              │
              └── Device
```

A channel is an intelligent I/O facility capable of executing an I/O program independently of normal CPU instruction execution.

---

# 42. Channel Programs

The CPU establishes a **channel program** in memory.

The channel program consists primarily of **Channel Command Words (CCWs)**.

A CCW describes an operation such as:

```text
READ
WRITE
CONTROL
SENSE
```

and provides information such as:

- data address
- byte count
- command
- control flags

The CPU initiates the operation, after which the channel can transfer data independently.

---

# 43. Channel Command Words

Conceptually a CCW says:

```text
perform this device command
using this area of memory
for this amount of data
with these control options
```

Multiple CCWs can be chained together.

This allows a channel to execute relatively sophisticated sequences without requiring the CPU to intervene after every transfer.

---

# 44. Command and Data Chaining

CCWs support chaining.

**Command chaining** allows one device command to be followed by another.

Conceptually:

```text
SEEK
 ↓
SEARCH
 ↓
READ
```

**Data chaining** permits multiple memory areas to participate in a larger transfer.

These facilities make channel programs somewhat analogous to specialized programs executed by an I/O processor.

---

# 45. Channel Types

System/370 systems can employ different channel organizations.

Important historical categories include:

### Byte Multiplexer Channel

Designed to multiplex many relatively slow devices.

Typical examples include:

- terminals
- card equipment
- printers
- communications devices

### Selector Channel

Devotes channel resources to a relatively high-speed operation for its duration.

### Block Multiplexer Channel

Permits high-speed block-oriented devices to share channel resources more efficiently.

DASD is an important use case.

---

# 46. Control Units

A device generally does not connect conceptually straight to the CPU.

Instead:

```text
CPU
 ↓
Channel
 ↓
Control Unit
 ↓
Device
```

The **control unit** translates channel commands into device-specific actions.

One control unit can support multiple devices.

This separation permits the processor and channel architecture to remain relatively independent of the detailed mechanics of particular disks, tapes, and printers.

---

# 47. Device Addressing

Devices are identified through the I/O architecture rather than through ordinary CPU memory addresses.

A device address identifies an I/O unit reachable through the configured channel/control-unit structure.

Consequently:

> System/370 is not fundamentally a memory-mapped-I/O architecture.

A normal load instruction does not simply load a "tape drive register."

I/O uses dedicated privileged instructions and channel machinery.

---

# 48. Starting I/O

The CPU can initiate channel activity with privileged I/O instructions.

The traditional instruction set includes operations such as:

```text
Start I/O
Test I/O
Halt I/O
Test Channel
```

The processor initiates work but does not normally remain occupied waiting for the device to complete.

CPU computation and device activity can proceed concurrently.

---

# 49. I/O Interruptions

When an I/O operation completes or requires attention, the channel subsystem can cause an **I/O interruption**.

The processor can then determine:

- which device requires attention
- completion status
- channel status
- device/unit status
- exceptional conditions

This provides asynchronous I/O:

```text
CPU starts I/O
      ↓
CPU continues executing
      ↓
channel performs operation
      ↓
I/O interruption
      ↓
CPU handles completion
```

This architecture is fundamental to mainframe throughput.

---

# 50. Channel Status

Channel execution can produce status describing the result of an operation.

The architecture distinguishes conditions associated with:

- channel execution
- device execution
- transfer completion
- exceptional conditions

Status information allows privileged software to distinguish successful completion from situations such as:

- device error
- incorrect length
- channel-program error
- exceptional device status

---

# 51. Direct Access Storage

DASD devices are accessed through the channel architecture.

Historically important IBM disks use concepts such as:

- cylinders
- tracks
- records
- count fields
- key fields
- data fields

The resulting **Count-Key-Data (CKD)** organization differs considerably from the simple fixed-sector abstraction familiar from later personal computers.

Channel programs can perform sequences involving:

```text
seek
search
read/write
```

with considerable work occurring outside the CPU.

---

# 52. Magnetic Tape

Tape devices likewise operate through channel programs.

Architecturally significant concepts include:

- sequential records
- variable-length blocks
- tape marks
- forward/backward positioning
- rewind
- device status
- end-of-tape conditions

The channel transfers records between the tape subsystem and main storage while the CPU is free to perform other work.

---

# 53. Initial Program Load

System startup uses **Initial Program Load (IPL)**.

IPL establishes the initial path from a selected device into executable machine state.

Conceptually:

```text
operator selects device
        ↓
hardware performs IPL operation
        ↓
initial information enters storage
        ↓
new PSW establishes execution
        ↓
bootstrap code executes
```

The operating system builds its much larger initialization procedure upon this relatively small architectural mechanism.

---

# 54. Console and Machine Control

Physical System/370 installations provide operator and maintenance facilities beyond the ordinary application-programming interface.

Depending upon the model these can support functions such as:

- CPU start/stop
- IPL
- machine reset
- examination of machine state
- configuration and diagnostics
- operator signaling

Exact facilities differ between physical System/370 models and should not be confused with the common instruction-set architecture.

---

# 55. Architectural Versus Implementation Features

A critical distinction when studying System/370 is:

> **Architecture describes what software can depend upon. Implementation describes how a particular processor achieves it.**

For example, the architecture can define:

```text
L 3,VALUE
```

to load a 32-bit value into R3.

It does not require every System/370 processor to implement that operation with identical:

- microcode
- datapaths
- cache organization
- memory timing
- pipelines
- execution cycles

Consequently, two processors can be architecturally compatible while being physically very different machines.

---

# 56. Architectural Versus Operating-System Concepts

For reference, it is useful to maintain this boundary.

## Hardware architecture

Examples:

- general registers
- PSW
- condition code
- instruction formats
- addressing
- arithmetic
- floating point
- DAT
- protection keys
- problem/supervisor state
- interruptions
- SVC mechanism
- timers
- atomic operations
- channels
- CCWs
- IPL

## Operating-system mechanisms

Examples:

- jobs
- tasks
- address-space management policy
- JCL
- datasets
- DD statements
- ABEND processing
- IPCF
- scheduling policy
- spooling
- system catalogs

The hardware supplies mechanisms upon which an operating system such as MVS constructs these abstractions.

---

# 57. A Small Programmer's Example

The following fragment demonstrates several architectural ideas at once:

```asm
EXAMPLE  CSECT
         USING EXAMPLE,12

         L     3,VALUE1
         A     3,VALUE2
         ST    3,RESULT

         C     3,LIMIT
         BH    TOOBIG

         XR    15,15
         BR    14

TOOBIG   LA    15,1
         BR    14

         DS    0F
VALUE1   DC    F'100'
VALUE2   DC    F'25'
LIMIT    DC    F'200'
RESULT   DS    F

         END   EXAMPLE
```

Architecturally, this illustrates:

- 32-bit general registers
- base-displacement storage addressing
- binary fullwords
- register/storage arithmetic
- condition-code generation
- conditional branching
- register-to-register logical operations
- address loading
- register-indirect return

The particular meanings assigned to R12, R14, and R15 reflect software conventions rather than immutable hardware requirements.

---

# 58. Mental Model of System/370

A useful condensed picture is:

```text
                    SYSTEM/370 CPU
             ┌────────────────────────┐
             │ 16 × 32-bit GPRs       │
             │ Floating-point regs    │
             │ PSW                    │
             │ Condition Code         │
             │                        │
             │ Integer instructions   │
             │ Decimal instructions   │
             │ Character instructions │
             │ Floating point         │
             │ DAT / protection       │
             └───────────┬────────────┘
                         │
                    Main Storage
                         │
          ┌──────────────┴──────────────┐
          │                             │
       CPU access                  Channel access
                                        │
                                   Channel Program
                                        │
                                      CCWs
                                        │
                                   Control Unit
                                        │
                                      Device
```

The architecture is notable for combining several characteristics:

1. **32-bit general-purpose registers with historically 24-bit addressing**
2. **base-displacement addressing**
3. **a PSW rather than a conventional PC-plus-flags model**
4. **four-state condition-code semantics**
5. **no mandatory hardware stack**
6. **rich storage-to-storage character operations**
7. **hardware packed-decimal arithmetic**
8. **hardware floating point**
9. **problem/supervisor privilege separation**
10. **storage protection**
11. **dynamic address translation**
12. **architected interruption classes**
13. **atomic multiprocessing primitives**
14. **channel-programmed I/O**
15. **strong separation between CPU execution and peripheral operation**

Taken together, these characteristics explain much of the distinctive style of System/370 systems programming. The architecture was designed not merely to execute arithmetic quickly, but to provide a general machine interface capable of supporting large-scale multiprogramming, commercial data processing, scientific computation, and high-throughput asynchronous I/O.
