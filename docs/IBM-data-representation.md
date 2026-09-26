# IBM System/370 Character and Data Representation

## Purpose

This briefing orients a general-purpose or systems programmer to the
representations commonly encountered in System/370 and MVS 3.8 programs:
bytes, words, EBCDIC, integers, decimal data, floating point, addresses,
bit fields, and record data.

## 1. Units of storage

System/370 uses an 8-bit byte.

Common sizes are:

``` text
byte       8 bits
halfword  16 bits = 2 bytes
fullword  32 bits = 4 bytes
doubleword 64 bits = 8 bytes
```

Assembler terminology frequently uses these size names directly.

Alignment matters for various instructions and data structures. A
programmer should recognize directives that align or define objects
appropriately rather than assuming arbitrary byte placement is always
equivalent.

## 2. Big-endian byte order

System/370 stores multi-byte binary quantities with the most significant
byte at the lowest address.

For the fullword:

``` text
12345678 hex
```

memory contains:

``` text
address +0 : 12
address +1 : 34
address +2 : 56
address +3 : 78
```

This is conventionally called **big-endian** byte order.

It matters when interpreting dumps, binary files, network-like
encodings, and data exchanged with little-endian modern hosts.

## 3. EBCDIC

Traditional IBM mainframes use **EBCDIC** character encoding rather than
ASCII.

Therefore the byte representing character `A` is not the ASCII byte for
`A`, and character ordering differs in ways that can affect comparisons
and translation.

This matters whenever data crosses between:

-   MVS and a modern workstation;
-   card/deck files and host text;
-   Hercules host files and guest data;
-   ASCII-oriented tooling and EBCDIC-oriented programs.

Never assume that a host text file's bytes are directly usable as guest
EBCDIC text.

## 4. Character constants in assembler

Assembler source can define character data with character constants, for
example conceptually:

``` asm
MESSAGE  DC    C'HELLO'
```

The assembler emits the target character encoding expected for the
environment.

Hex constants are useful when the exact byte representation matters:

``` asm
BYTE     DC    X'F1'
```

Use character constants to express characters and hex constants to
express exact bits; do not mix the two concepts mentally.

## 5. Fixed-length character fields

Traditional MVS records and control blocks frequently use fixed-width
character fields.

A ten-byte field is ten bytes whether its meaningful text contains two
characters or ten.

Padding is therefore common, often with EBCDIC blanks according to the
interface.

This differs from C's NUL-terminated string model:

``` text
MVS fixed field:  [A][B][blank][blank]...
C string:         [A][B][00]
```

Always determine the convention of the specific interface.

## 6. BC and MVC-style thinking

System/370 has instructions well suited to moving and comparing
character fields in storage.

Character operations often work with explicit lengths rather than
terminators.

This makes record layouts and field lengths central programming
concepts.

When debugging, know both:

-   the address of a field;
-   its defined length.

## 7. Binary integers

System/370 commonly works with signed binary integers in halfwords and
fullwords.

Assembler constants can define binary numeric values in appropriate
forms, for example fullword constants.

The representation follows ordinary two's-complement signed binary
conventions for the relevant integer instructions.

A fullword contains 32 bits and is a natural unit for many counters,
lengths, addresses, and parameter fields.

## 8. Addresses

In the MVS 3.8/System/370 environment, architectural addresses are
fundamentally 24-bit even though they are commonly carried in 32-bit
general registers and fullword fields.

This creates an important historical detail: not every bit in a 32-bit
word containing an address necessarily belongs to the address in every
interface.

Some conventions use high-order bits for flags.

Therefore:

> Never assume that every fullword described as an "address field" is
> simply an unrestricted modern 32-bit pointer.

Read the interface definition.

## 9. Bit fields and flags

System control blocks and parameter lists make extensive use of
individual bits.

Assembler provides ways to define masks and instructions for logical
operations and bit testing.

A field may conceptually contain:

``` text
bit 0 -> option A
bit 1 -> option B
bit 2 -> state C
...
```

Systems programming often requires preserving unrelated bits while
changing one option.

Hexadecimal notation is particularly useful because each hex digit
corresponds to four bits.

## 10. Zoned decimal

**Zoned decimal** stores one decimal digit per byte, with zone/sign
information encoded in the byte.

It is closely related to character decimal representations and is useful
in commercial data processing.

Conceptually:

``` text
"123" -> three digit-bearing bytes
```

but the exact high-order nibbles and sign representation matter to
decimal instructions.

Do not treat arbitrary EBCDIC digit strings as interchangeable with
every zoned-decimal numeric format.

## 11. Packed decimal

**Packed decimal** stores two decimal digits per byte except for the
final sign nibble.

Conceptually, positive 12345 may occupy nibbles like:

``` text
1 2 | 3 4 | 5 sign
```

Packed decimal is space-efficient and directly supported by System/370
decimal arithmetic instructions.

It is extremely important in business-oriented software.

## 12. Packed-decimal sign

The low-order nibble of the final byte carries the sign.

Several sign encodings can be valid depending on operation and
convention.

This is why corrupt or improperly constructed packed data can produce a
**data exception**, commonly observed as an S0C7-type failure under MVS.

When debugging packed decimal, inspect the actual hex bytes.

## 13. Decimal versus binary arithmetic

Binary and decimal representations solve different problems.

Binary arithmetic is natural for:

-   addresses;
-   counters;
-   indexes;
-   bit operations;
-   many systems calculations.

Decimal arithmetic is valuable where exact base-10 digit behavior
matters, especially financial/business processing.

A programmer must explicitly convert when moving between
representations.

The bytes for packed decimal `123` are not the same thing as binary
integer 123 or EBCDIC characters `"123"`.

## 14. Three different "123"s

Conceptually:

``` text
binary integer 123
    -> numeric binary representation

EBCDIC "123"
    -> three character bytes

packed decimal 123
    -> packed decimal digit nibbles + sign
```

They may print the same way after conversion, but they are different
data types at the machine level.

Many assembler bugs are type errors expressed only as incorrect bytes.

## 15. Floating point

System/370 provides IBM hexadecimal floating-point formats and
instructions.

These are not identical to the IEEE 754 formats familiar from modern
systems.

The representation uses a hexadecimal-oriented exponent/fraction scheme.

For orientation, remember:

-   floating-point values have dedicated formats;
-   short and long forms exist;
-   arithmetic uses floating-point registers/instructions;
-   host IEEE binary floating point should not be assumed
    byte-compatible.

Detailed numerical behavior belongs in the System/370 Principles of
Operation.

## 16. Alignment

Some data is naturally placed on boundaries such as halfword, fullword,
or doubleword boundaries.

Assembler directives can control alignment.

Correct alignment matters for:

-   architectural instruction requirements;
-   conventional control-block layouts;
-   performance and clarity;
-   interoperability with system interfaces.

Do not insert or remove bytes from a documented structure without
considering the resulting offsets and alignment.

## 17. Length fields

MVS structures often contain explicit lengths.

A length might describe:

-   a buffer;
-   a record;
-   a parameter list;
-   a variable-length field;
-   an entire control block.

Determine whether a length counts:

-   bytes;
-   words;
-   records;
-   data only;
-   header plus data.

The representation is interface-specific.

## 18. Variable-length records

A variable-length MVS record can contain control information such as a
**Record Descriptor Word (RDW)** in the physical/logical representation
used by the access method.

Blocked variable records can add block-level descriptor information.

This means that "record length" and "application payload length" may not
always be the same number.

Access methods often hide some of this detail from ordinary record
processing, while dumps and raw-device work expose it.

## 19. Card-image records

Assembler source and JCL historically inherit an 80-column punched-card
model.

Even when no physical card exists, an 80-byte fixed record can still
represent a card image.

This historical model explains many formatting conventions in:

-   assembler source;
-   JCL;
-   object decks;
-   utilities;
-   interchange files.

The emulator may use ordinary host files to represent material whose
guest semantics remain card-oriented.

## 20. Object decks are binary structures in records

Traditional object modules use structured records containing ESD, TXT,
RLD, and END information.

Although historically card-oriented, the contents are not ordinary
source text.

A tool that translates bytes indiscriminately between ASCII and EBCDIC
can destroy such data.

Always know whether a file is:

``` text
text needing character translation
binary/structured data needing byte preservation
record-oriented transport representation
```

before converting it.

## 21. Host/guest interchange under Hercules

When moving material between a modern host and MVS under Hercules, three
questions matter:

1.  What character encoding is used on each side?
2.  What record structure does MVS expect?
3.  Is the material text or byte-sensitive binary data?

For example, converting an ASCII source file to EBCDIC card images is a
fundamentally different operation from transferring an object deck
byte-for-byte.

The transfer tool's record and translation options are therefore part of
the data format.

## 22. Dumps: read both hex and character forms

A storage dump commonly becomes much more useful when read in two views:

``` text
hexadecimal bytes -> exact representation
character view    -> recognizable EBCDIC text where applicable
```

The character view helps identify labels, messages, and fields.

The hex view is authoritative for:

-   addresses;
-   packed decimal;
-   binary integers;
-   flags;
-   corrupted data;
-   instructions.

## 23. Data declarations as documentation

Assembler declarations should communicate intended representation.

Conceptually:

``` asm
COUNT    DC    F'0'          binary fullword
HALF     DC    H'1'          binary halfword
TEXT     DC    C'HELLO'      character bytes
MASK     DC    X'80'         exact bit pattern
AREA     DS    256C          character/byte work area
```

Precise syntax and supported constant forms should be checked in the
assembler reference.

Good declarations make the program's machine-level types visible.

## 24. Orientation map

``` text
bits
 |
bytes
 |
+-- EBCDIC characters / fixed fields
+-- binary integers / addresses
+-- flags and masks
+-- zoned decimal
+-- packed decimal
+-- hexadecimal floating point
 |
records and control structures
 |
data sets / parameter lists / object modules / dumps
```

## 25. Topics for deeper research

Useful next subjects include:

-   EBCDIC code pages used by the target installation;
-   System/370 integer instructions and condition codes;
-   packed/zoned decimal instruction formats;
-   decimal sign conventions;
-   IBM hexadecimal floating point;
-   alignment requirements;
-   24-bit address-field conventions;
-   RDW/BDW formats;
-   object-deck record formats;
-   host-to-EBCDIC translation tools;
-   DASD/tape physical record representations when doing low-level I/O.

The essential habit is: **before operating on storage, identify the
representation, length, alignment, and ownership of the bytes. A
System/370 program has no runtime type system to correct a mistaken
interpretation for you.**
