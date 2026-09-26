# MVS 3.8 Program Debugging and Diagnostics

## Purpose

This briefing provides an orientation to diagnosing assembler and other
compiled programs under MVS 3.8. It emphasizes a repeatable reasoning
process: determine which stage failed, identify the first meaningful
diagnostic, and connect machine state back to source and build
artifacts.

## 1. Debug the pipeline, not just the program

A traditional MVS programming failure can occur at several distinct
stages:

``` text
JCL/JES processing
      |
allocation
      |
assembly/compilation
      |
link-edit
      |
program loading
      |
execution
      |
data/access-method processing
```

The first diagnostic question should therefore be:

> Which stage actually failed?

Do not start analyzing a dump if the load module was never successfully
produced.

## 2. Completion codes

A job step can complete normally and still report a nonzero **condition
code**.

For many development tools:

``` text
CC 0000 -> successful
CC 0004 -> warnings or minor issues
CC 0008+ -> increasingly serious errors
```

But the meaning is program-specific. There is no universal rule that
every `CC=0004` is harmless or every particular nonzero code has
identical meaning across tools.

Read the program's documented return-code definitions.

## 3. ABENDs

An **ABEND** is abnormal termination.

Codes are commonly shown as system or user ABENDs. System ABENDs often
appear in forms such as:

``` text
S0C1
S0C4
S0C7
```

User ABENDs may be reported with a user code.

The code is a starting point, not a diagnosis. It tells you the broad
class of failure; the PSW, registers, messages, and surrounding
instructions tell you what happened in this instance.

## 4. Important S0Cx families

A systems programmer should at least recognize several common
program-check-related ABENDs.

### S0C1 --- operation exception

Often indicates that the processor attempted to execute an invalid or
unavailable instruction.

Possible causes include:

-   branching into data;
-   corrupted return address;
-   bad entry point;
-   overwritten code;
-   instruction not valid for the configured architecture.

### S0C4 --- protection/addressing-related failure

Often associated with invalid storage references or protection problems.

Possible causes include:

-   bad pointer;
-   bad base register;
-   invalid parameter address;
-   using storage after it is no longer valid;
-   incorrect address arithmetic.

### S0C7 --- data exception

Often encountered when a decimal instruction operates on invalid decimal
data.

Possible causes include:

-   packed/zoned decimal field contains invalid digits/sign;
-   wrong field offset;
-   uninitialized data;
-   record layout mismatch.

These descriptions are intentionally broad. The exact interruption code
and context matter.

## 5. The PSW

The **Program Status Word (PSW)** captures key processor state,
including the instruction address and control/mask information.

After a program check, the diagnostic material usually lets you identify
the relevant PSW and therefore the location at or around which execution
failed.

The practical debugging chain is:

``` text
ABEND
  |
PSW instruction address
  |
load-module offset / map
  |
assembler listing
  |
source instruction
```

This is one of the most important skills in mainframe debugging.

## 6. Registers

A dump of the general registers can explain how the failing instruction
obtained its operands.

Suppose the failing instruction uses an address formed from R3 plus a
displacement. The next question is not merely "what instruction failed?"
but:

> What did R3 contain, and why?

Registers can reveal:

-   invalid pointers;
-   lost base-register addressability;
-   bad parameter lists;
-   corrupted save areas;
-   incorrect lengths and counters;
-   unexpected return addresses.

## 7. The assembler listing

An assembler listing can contain several kinds of evidence:

-   source statements;
-   generated machine code;
-   statement addresses;
-   symbol table;
-   diagnostics;
-   macro expansions, depending on options;
-   cross-reference information.

For runtime debugging, the source-to-address relationship is
particularly valuable.

A good development workflow retains enough listing information to map a
runtime address back to the source that produced it.

## 8. The linkage-editor map

The assembler knows offsets within its own control sections. The linkage
editor decides how input control sections are arranged in the resulting
load module.

A link map helps answer:

``` text
Where did CSECT X end up?
Where is external symbol Y?
What was the selected entry point?
Which modules were included?
```

When a dump supplies an execution address, the link map and assembler
listing together bridge runtime location back to source.

## 9. Save-area traceback

Programs following conventional MVS linkage maintain chained save areas.

In a dump, the chain can help reconstruct a call path:

``` text
MAIN
  |
  +-> ROUTINEA
        |
        +-> ROUTINEB
              |
              +-> failing routine
```

A corrupted save-area chain is itself diagnostic evidence. It can
indicate storage overlay, bad R13 handling, or a routine that failed to
follow linkage conventions.

## 10. Base-register failures

System/370 base-displacement addressing makes base-register correctness
especially important.

Assembler `USING` directives tell the assembler what base relationships
to assume. They do not establish those values at execution time.

Thus code can assemble perfectly while failing because the program never
placed the expected address in the base register.

When an apparently ordinary load/store fails:

1.  identify the base and index registers used;
2.  inspect their runtime contents;
3.  recompute the effective address;
4.  compare it with the intended object.

This often turns an opaque S0C4 into a straightforward addressing bug.

## 11. Parameter-list failures

MVS interfaces frequently pass addresses through R1.

Common mistakes include:

-   treating an address as the value itself;
-   dereferencing one level too many or too few;
-   assuming the wrong parameter-list layout;
-   using the wrong field length;
-   forgetting a convention-specific flag or terminator.

When a routine fails soon after entry, inspect R1 and the storage to
which it points.

## 12. Storage overlays

An overlay occurs when a program writes beyond the intended object and
damages neighboring storage.

Symptoms can appear far from the original write:

-   return address becomes invalid;
-   save-area chain breaks;
-   instructions become corrupted;
-   DCB fields change unexpectedly;
-   a later routine receives nonsensical parameters.

The failure location is then only where the damage became visible.

Clues include recognizable patterns, one field corrupted next to a
buffer, or repeated failures after a particular move/output operation.

## 13. Decimal-data problems

Packed decimal instructions validate digit/sign encodings. A field that
visually "contains a number" in a character record is not automatically
valid packed decimal.

For S0C7-type failures, inspect:

-   actual bytes;
-   expected representation;
-   field offset;
-   field length;
-   sign nibble;
-   initialization and conversion path.

This is where a hex dump is often more informative than a character
rendering.

## 14. Data-set and access-method diagnostics

Not every execution failure is a CPU exception.

OPEN or access-method processing may fail because of:

-   missing DD statement;
-   wrong DSN;
-   incompatible record format;
-   wrong LRECL/BLKSIZE;
-   invalid disposition;
-   unavailable volume;
-   unexpected end of data.

Read MVS allocation and access-method messages before assuming a code
defect.

## 15. JCL and allocation failures

A program may never receive control if JCL or allocation fails.

Useful evidence includes:

-   JES2 `$HASP...` messages;
-   MVS `IEF...` messages;
-   step completion information;
-   DD allocation messages;
-   procedure expansion.

A clean debugging discipline distinguishes:

``` text
job did not start program
        versus
program started and failed
```

## 16. Assembly-time errors

Assembler diagnostics should be handled from the **first substantive
error forward**.

One malformed statement can cause later symbols, literals, or
addressability assumptions to fail, generating many secondary messages.

Use:

1.  assembler condition code;
2.  first error message;
3.  corresponding source/listing line;
4.  macro expansion if relevant;
5.  later errors only after the first is corrected.

## 17. Link-edit errors

Typical link-edit problems include:

-   unresolved external symbols;
-   duplicate definitions;
-   missing object/library input;
-   wrong entry point;
-   unexpected module selection;
-   size or placement issues.

The link editor's map and diagnostics are the authoritative starting
point.

Do not diagnose a runtime linkage problem until the link-edit output
itself is clean enough to justify execution.

## 18. A practical failure workflow

For a failed assemble-link-go job:

### Step 1: Find step results

``` text
ASM   ?
LKED  ?
GO    ?
```

### Step 2: Stop at the first bad stage

If ASM failed, do not debug GO.

### Step 3: Classify the failure

``` text
JCL syntax?
allocation?
assembler?
link editor?
loader?
ABEND?
application return code?
```

### Step 4: Collect the minimum evidence

For runtime failure:

-   ABEND code;
-   relevant system messages;
-   PSW;
-   registers;
-   load map;
-   assembler listing;
-   relevant storage dump.

### Step 5: Reconstruct the failing instruction

Map runtime address to module/CSECT and source.

### Step 6: Reconstruct its operands

Use registers and storage.

### Step 7: Ask what earlier event made that state possible

This last step is crucial for overlays and corrupted linkage.

## 19. Keep reproducible artifacts

For systems development, retain or regenerate consistently:

-   exact source;
-   generated JCL;
-   assembler listing;
-   object module when useful;
-   linkage-editor output/map;
-   program output;
-   console/JES messages;
-   emulator configuration when hardware behavior matters.

A dump is far less useful if it cannot be matched to the exact binary
that failed.

## 20. Hercules adds another layer

Under Hercules, distinguish guest failures from emulator/environment
failures.

``` text
MVS program error
MVS configuration/error
Hercules device/configuration error
host/container problem
```

A guest S0C4 is normally an MVS program diagnostic, not evidence that
Hercules itself failed.

Conversely, an unattached or misconfigured emulated device can create
guest-visible I/O problems.

## 21. Orientation map

``` text
job output
   |
first failing step
   |
failure class
   |
diagnostic code/messages
   |
PSW + registers + storage
   |
link map
   |
assembler listing
   |
source-level cause
```

## 22. Topics for deeper research

Useful next subjects include:

-   System/370 interruption codes and old PSWs;
-   MVS system and user ABEND codes;
-   formatted dumps;
-   SNAP and dump services;
-   save-area conventions;
-   linkage-editor maps;
-   assembler listing options;
-   storage keys and protection;
-   ESTAE/STAE recovery facilities;
-   access-method error exits;
-   JES2 and MVS message manuals;
-   Hercules tracing when a problem genuinely crosses into emulation.

The working rule is: **identify the first failing layer, then use
addresses and machine state to move from symptom back to source**.
