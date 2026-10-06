# Cambridge Native System/370 Code Generation Checkpoint

This checkpoint records the first successful end-to-end execution of the
resident Cambridge BCPL compiler through its historical System/370 code
generator under ICINT V19.

The durable milestone is architectural, not the JES job number:

```text
BCPL source
  -> Cambridge SYN / LEX / TRN
  -> Cambridge OCODE
  -> historical CG370
  -> textual System/370 assembler
```

The probe source was the Richards factorial test used elsewhere in the
repository.

## Proven successful compiler run

The resident compiler completed normally and reported:

```text
Warning, the A option is only suitable for cross compilation
BCPL 5th Mar 81  Stacksize = 12850  Parm =
Tree size 422
OCODE size = 66
Length = 64 words
9350 unused words of workspace(workspace size = 9850)
COMPILATION SUCCESSFUL

EXECUTION CYCLES = 186701, CODE = 0
```

The host driver recovered a nonempty textual System/370 source file as:

```text
workarea/richards-factorial.s370.asm
```

The workarea file is generated and reproducible rather than historical source.

## Host and target byte widths are different

The Cambridge translator writes in-memory OCODE through WRBYTE and advances
OBUFP after BYTESPERWORD bytes. Historical System/370 LIBHDR correctly defines
BYTESPERWORD=4.

The bootstrap host executes through the MR10 INTCODE runtime, whose
GETBYTE/PUTBYTE representation stores two bytes per interpreted BCPL word.
Leaving WRBYTE at four host bytes caused adjacent OCODE groups to overlap and
CG370 eventually decoded the impossible OCODE operator 7.

The bootstrap derivative therefore changes only TRN's in-memory OCODE writer to
advance OBUFP after two MR10 host bytes. Historical System/370 BYTESPERWORD=4
and the untouched Cambridge source remain unchanged.

The resulting OCODE size of 66 host words is consistent with the previous
33-word logical payload occupying two bytes per MR10 host word.

CG370, by contrast, constructs 32-bit target words. Its target packing therefore
uses four bytes per System/370 word. The demoted CGA derivative uses a private
PK370 helper only at the two target-packing sites. Ordinary MR10 PACKSTRING
remains unchanged.

Do not globally change GETBYTE, PUTBYTE or PACKSTRING: that would conflate host
representation with target representation.

## Cambridge option policy

CAMBPARM is one complete 80-byte record beginning with:

```text
/N/
```

and filled to column 80 with slash characters.

- the leading slash selects no first-phase compiler option;
- N is a code-generator option that sets DECK := FALSE;
- slash fill prevents FB80 blank padding from becoming bogus options.

The earlier `A/N/` record was wrong for this bootstrap direction.  Historical
`A` installs `CODEA`, an EBCDIC-to-ASCII translation used when the native
System/370 compiler cross-compiles for an ASCII target.  Our host is already
ASCII and the target is System/370 EBCDIC, so the bootstrap derivative instead
installs the inverse translation `CODE370` by default.

DECK suppression is intentional at this checkpoint. Textual CODE is recoverable
through the present host path, but binary object-deck output via SYSGO/WRITEREC
does not yet have a byte-preserving MVS-to-host transport.

This supersedes the earlier bootstrap idea that SYSGO should remain enabled
merely to exercise DECKOUT. The historical N option is the cleaner boundary
until binary deck transport itself is reconstructed.

## Host-service accommodations currently required

The resident compiler bootstrap supplies these evidence-driven services in
`bootstrap-host.bcpl`:

- G!29 DATE
- G!33 WRAPOUTPUT
- G!39 FINDPARM

DATE returns the historical three-word undated header value rather than
fabricating a calendar date.

ICINT V19 additionally publishes:

- G!54 STACKBASE
- G!55 STACKEND

No WRITEREC shim is required for the current textual-code bootstrap because N
suppresses DECKOUT.

## Generated native structure

The generated factorial module begins:

```asm
 CSECT
 EXTRN BCPLMAIN
 USING 4096,1,2,3
L999 EQU *
 STM 14,12,12(13)
 L  4,12(15)
 BCR 15,4
 DC AL2(L998-L999)
 DC A(BCPLMAIN)
```

This is direct evidence that generated BCPL sections expect an external runtime
entry named `BCPLMAIN`.

Historical CGHDR gives the generated register roles:

```text
R4   R.B   branch / callee address
R5   R.P   BCPL workspace pointer
R6   R.L   linkage register
R7   R.A1  first argument / result
R8   R.A2
R9   R.A3
R10  R.A4
R11  R.S   system-vector base
R12  R.G   global-vector base
R15  R.W   new workspace pointer
```

A generated procedure entry follows that convention:

```asm
L3 EQU * ENTRY TO
 STM 4,7,0(15)
 LR 5,15
```

A generated call has the recognizable form:

```asm
 LA 15,16(5)
 L  4,0+L4-L3(4)
 BALR 6,4
```

R15 supplies the new callee workspace pointer, R4 the entry address, and BALR
places the return address in R6.

## Hard evidence for the global vector

The factorial source calls WRITEF, whose LIBHDR global number is 76. The
generated module contains:

```asm
 L  4,304(12)
 BALR 6,4
```

304 is exactly 76*4.

Therefore this module directly proves that:

- R12 is the BCPL global-vector base;
- each global is one 32-bit word;
- global N is addressed at byte displacement 4*N from R12;
- a function-valued global contains a callable entry address.

This is stronger evidence for native BCPLMAIN reconstruction than inference from
ICINT internals.

## Hard evidence for the system vector

CGHDR defines R11 as R.S and S.FIN as byte displacement 40. The generated START
path contains:

```asm
 BC 15,40(11)
```

This directly proves that generated code expects a runtime/system service table
reachable through R11 with FINISH at displacement 40.

Procedure return is separately emitted as:

```asm
 BCR 15,11
```

for C.RTRN after CGSAVE has established procedure linkage. The complete meaning
and initialization of R11 must still be reconstructed from historical runtime
evidence; do not infer the entire system-vector layout from this one module.

## Section prefix and metadata

Immediately after the initial transfer sequence CG370 emits section metadata,
including a halfword section length/reference value, `A(BCPLMAIN)`, DATE data
and packed section/name fields.

The generated DATE words are:

```asm
 DC X'0B40405C'
 DC X'E4D5C4C1'
 DC X'E3C5C45C'
```

which match the intended EBCDIC `"  *UNDATED*"` BCPL string.

Treat this prefix as part of the historical BCPLMAIN rendezvous until proved
otherwise; it is not ordinary procedure code.

## Diagnosed character-representation boundary

The malformed factorial string has been traced to the compiler master's
historical `A` option, not to CGSTRING packing.

The factorial source contains the format string:

```text
F(%N), = %N\n
```

whose expected IBM EBCDIC CP037 bytes are:

```text
C6 4D 6C D5 5D 6B 40 7E 40 6C D5 25
```

CGSTRING stores a BCPL string, so the target pool also begins with the one-byte
length 12.  The corrected four target words should therefore be:

```asm
L995 EQU * STRINGS
 DC X'0CC64D6C'
 DC X'D55D6B40'
 DC X'7E406CD5'
 DC X'25000000'
```

The previous run instead produced:

```asm
L995 EQU * STRINGS
 DC X'0C00000A'
 DC X'2B000000'
 DC X'00000A2B'
 DC X'00000000'
```

Those bytes identify the failure precisely.  After the leading length byte
`0C`, the values are the results of applying historical `CODEA` to the
ASCII host character codes.  For example, ASCII `%` maps through CODEA to
octal `12` (hex `0A`), and ASCII `N` maps to octal `53` (hex `2B`).
Most other ASCII indices in this string map to zero.  This is exactly what the
bad pool contains.

Historical `CODEA` is an EBCDIC-to-ASCII table.  It made sense when the
compiler itself ran natively on System/370 and option A requested an ASCII
cross target.  Under the MR10 bootstrap the direction is reversed: source
characters arrive as ASCII while CG370 is producing native System/370 data.

The bootstrap derivative now installs a private `CODE370` translation that
inverts the surviving CODEA table.  ASCII newline is explicitly mapped to
X'25' because CODEA maps both EBCDIC X'15' and X'25' to ASCII newline and the
factorial target convention requires X'25'.  Historical source remains
unchanged.  CAMBPARM no longer selects A.

This diagnosis leaves the host/target byte-width accommodations unchanged and
does not alter ICINT V19 status.

## Host recovery encoding

The Hercules printer report is consumed as Latin-1 so byte values survive
recovery. `tools/cambridge-compile` likewise writes recovered CODE as Latin-1
rather than narrowing it to ASCII. This is a transport property, not a claim
that arbitrary non-ASCII bytes are valid assembler source.

## ICINT V19 status

This milestone does not promote ICINT V19.

V19 remains a bootstrap candidate with the capacity and diagnostic changes
needed by the resident compiler:

- 40,001-word PROGVEC;
- G!0..G!699 global capacity;
- G!54/G!55 stack bounds;
- 64-entry recent-instruction trace.

The inherited MAPSTORE frame/program bounds still deserve review. Do not change
`config/CURRENT` without explicit review and approval.

## Next controlled experiments

1. Regenerate the demoted resident compiler with the CODE370 accommodation.
2. Re-run factorial and verify L995 is exactly the four expected words above.
3. Confirm at least one additional string/character probe before treating the
   translation boundary as generally validated.
4. Once textual assembler is representation-correct, assemble it with IFOX.
5. Use assembler/link-editor evidence to refine the native BCPLMAIN contract.

The generated module already provides strong linkage evidence, but native
runtime reconstruction should proceed from validated target code rather than a
module whose string constants are still known to be wrong.
