# Cambridge BCPL Compiler Options and MVS Parameter Transport

This note records the option grammar of the surviving Cambridge BCPL compiler,
how those options are divided between compiler and code-generator phases, how
the native MVS system supplied them, and how the present bootstrap substitutes
for that native transport.

The primary historical evidence is:

- `richards-bcpltape/bcplib/bcpl/bcpl` — compiler master and option parser;
- `richards-bcpltape/sys1/userproc/bcplclg` — historical MVS compile/link/go
  procedure;
- `richards-bcpltape/bcplib/jcl/makeobj` — historical compiler/library object
  build job;
- `richards-bcpltape/km10/bcplmac` — native runtime macro material describing
  the PARM pseudo-stream.

## Parameter-string grammar

The compiler reads two successive option phases from the stream returned by
`FINDPARM()`.

Conceptually:

```text
<compiler/front-end options>/<code-generator options>
```

The first slash terminates the compiler/front-end option loop. The
code-generator loop then reads from the same stream. Extra slash characters in
the second phase are explicitly ignored.

This is why the present bootstrap parameter record begins:

```text
A/N/
```

The `A` belongs to the first option phase. The first `/` changes phases. The
`N` belongs to the code-generator phase.

## First phase: compiler/front-end options

The surviving master initializes:

```bcpl
SAVESPACESIZE := 3
BACKVEC := FALSE
NOGET, LEXTEST := FALSE, FALSE
PPTRACE, TREE, OCODE := FALSE, FALSE, FALSE
NUMOCODE := FALSE
...
PRSOURCE := FALSE
...
FORCEUPPERCASE := TRUE
QUIET := FALSE
```

The active first-phase options are:

| Option | Effect |
| --- | --- |
| `A` | `ASCII := TRUE`; select the cross-compilation character-code path |
| `B` | `BACKVEC := TRUE` |
| `C` | `FORCEUPPERCASE := FALSE` |
| `F` | `ABORT := STANDARDABORT` |
| `H` | `HARD := TRUE` |
| `N` | `NUMOCODE := TRUE`, then fall through to enable `OCODE` |
| `O` | `OCODE := TRUE` |
| `Pnnn` | set `FREESTACKSIZE` to the following decimal number |
| `Q` | `QUIET := TRUE` |
| `Rnnn` | set `ERRORMAX` to the following decimal number |
| `S` | `PRSOURCE := TRUE` |
| `W` | redirect `WRCH` through `WRITEUPPERCASE` |
| `X` | `TIMING := TRUE` |
| `Z` | `NOCG := TRUE` |
| `1` ... `9` | set `SAVESPACESIZE` to that digit |
| `/` | terminate the first option phase |

The master prints the warning:

```text
Warning, the <option> option is only suitable for cross compilation
```

for options routed through its `OPTWARN` path. In the surviving source this
includes at least `A`, `B`, `O`/first-phase `N`, and `Z`.

The first-phase `N` deliberately falls through:

```bcpl
CASE 'N': NUMOCODE := TRUE          // Set OCODE as well
CASE 'O': OCODE := TRUE; GOTO OPTWARN
```

Therefore first-phase `N` means numeric OCODE output and also enables OCODE
output.

### Disabled first-phase switches

Several option cases remain visible in the source but are commented out and
therefore are not active in this surviving compiler build:

| Option | Historical/source meaning |
| --- | --- |
| `E` | `PPTRACE := TRUE` |
| `M` | `MAPPING := TRUE` |
| `T` | `TREE := TRUE` |
| `V` | `LEXTEST := TRUE` |
| `Y` | `NOTRN := TRUE` |

These should be documented as surviving historical clues, not as supported
options.

## Second phase: code-generator options

After the first slash, the master enters a separate code-generator option loop.

The relevant defaults are:

```bcpl
DECK, LISTDECK, BINING := TRUE, FALSE, TRUE
LISTING, CGTRACE := FALSE, FALSE
STKCKING, CALLCOUNTING, COUNTING := FALSE, FALSE, FALSE
MEMBERNAMEING := FALSE
NAMING, NAMES := FALSE, 0
```

The active second-phase options are:

| Option | Effect |
| --- | --- |
| `C` | `STKCKING := TRUE` |
| `G...` | `LOADGO := TRUE`; copy the remainder of the parameter record into `PARMS`; must be last |
| `Hnnn` | enable `NAMING`; use the following decimal size, default 600 if zero |
| `K` | `CALLCOUNTING := TRUE` |
| `L` | `LISTING := TRUE` |
| `M` | `MEMBERNAMEING := TRUE` |
| `N` | `DECK := FALSE` |
| `P` | enable both `CALLCOUNTING` and `COUNTING` |
| `/` | ignored; extra slashes are explicitly tolerated |

A newline or end of stream terminates the second phase.

### Disabled code-generator switches

Two additional cases remain in comments:

| Option | Historical/source meaning |
| --- | --- |
| `D` | `LISTDECK := TRUE` |
| `T` | `CGTRACE := TRUE` |

Again, these are evidence of historical capabilities, not active options in
the surviving source.

## Important distinction: first-phase N versus second-phase N

The letter `N` has completely different meanings depending on which side of
the first slash it appears.

```text
N/...    first phase: numeric OCODE and OCODE output
.../N    second phase: suppress binary object deck generation
```

This distinction matters for both historical JCL interpretation and bootstrap
testing.

## Native MVS transport: EXEC PARM=

The historical MVS compiler did not normally read these options from a dedicated
compiler-options DD. They entered through the MVS program parameter string.

The surviving `BCPLCLG` procedure contains:

```jcl
//NBCPLCLG PROC TRKS='5,10',PRINTC='SYSOUT=C',REGC=160K,
//             MINC=,SECC=20,CONDC=,PARMC='/CK',LISTC=,
//             ...
//BCPL    EXEC PGM=BCPL,REGION=&REGC,
//             PARM='$0T&IOSPACE.$&LISTC.&PARMC',
//             TIME=(&MINC,&SECC),COND=(&CONDC)
```

With the procedure defaults:

```text
IOSPACE = 60K
LISTC   = empty
PARMC   = /CK
```

the MVS EXEC parameter field is conceptually:

```text
$0T60K.$/CK
```

The prefix before the compiler options belongs to the native BCPL runtime
parameter machinery. The compiler itself does not directly inspect the raw MVS
parameter field. Instead it begins its option processing with:

```bcpl
SELECTINPUT(FINDPARM())
```

and consumes the returned pseudo-stream through ordinary BCPL character input.

The native architecture is therefore:

```text
MVS EXEC PARM=
      |
      v
   BCPLMAIN
      |
      | native runtime option processing
      v
PARM pseudo-input stream
      |
      v
  FINDPARM()
      |
      v
Cambridge compiler option parser
```

The runtime macro material explicitly describes `PARMAREA` as the data area
for:

```text
THE PSEUDO INPUT STREAM FROM THE PARM STRING
```

and defines a `PARMFLD` corresponding to the MVS parameter field. This is
strong historical evidence that `FINDPARM` is an abstraction over the native
MVS EXEC parameter string, not a DD-name convention.

## Historical BCPLCLG default /CK

The historical procedure default is:

```text
PARMC='/CK'
```

This fits the compiler parser exactly:

```text
/       terminate first-phase compiler options
C       enable stack checking in the code generator
K       enable call counting
```

The fact that the historical JCL and compiler parser agree this closely is
important evidence that the option grammar above is the intended native
interface.

## Historical object-build examples

The surviving `makeobj` job uses the compiler procedure with examples such as:

```jcl
//COMPBLIB EXEC BCPLC,PARMC='/C'
...
//BCPL     EXEC BCPLC,PARMC='/C'
...
//SYN      EXEC BCPLC,PARMC='/C'
...
//TRN      EXEC BCPLC,PARMC='/C'
...
//CG       EXEC BCPLC,PARMC='/C'
```

while runtime-library components such as BLIB, IOS and PM are compiled with an
empty `PARMC`.

These examples reinforce two points:

1. `PARMC` is a procedure parameter used to construct the program's EXEC
   `PARM=` value;
2. a leading slash means "no first-phase options; begin with code-generator
   options."

## Relation to CODE and SYSGO

The second-phase `N` option is directly related to CG370 output selection.

By default:

```bcpl
DECK := TRUE
```

and the compiler requires a `SYSGO` output stream for the object deck.

The compiler also searches for `CODE`:

```bcpl
CODESTREAM := FINDOUTPUT("CODE")
TEST CODESTREAM=0 THEN CODESTREAM := SYSOPT
                  OR LISTING := TRUE
```

Providing `CODE` therefore enables textual System/370 assembler output.

When `DECK` remains true, CG370 additionally emits ESD/TXT/RLD/END object
records to `SYSGO` through `WRITEREC(V,80)`.

Thus:

```text
CG370
  +-- CODE  -> textual IBM System/370 assembler
  +-- SYSGO -> 80-byte relocatable object-deck records
```

Second-phase `N` disables only the second path.

## Current bootstrap transport

The present interpreted bootstrap does not yet provide native BCPLMAIN's MVS
PARM pseudo-stream. Its narrow accommodation is:

```bcpl
LET FINDPARM() = FINDINPUT("CAMBPARM")
```

and `tools/cambridge-compile` supplies an FB80 `CAMBPARM` DD.

The current record begins:

```text
A/N/
```

and is filled through column 80 with slash characters.

This has three deliberate effects:

1. first-phase `A` selects the historical cross-compilation character-code
   path;
2. second-phase `N` suppresses the binary object-deck path while the bootstrap
   lacks a byte-preserving WRITEREC transport;
3. slash fill prevents FB80 blank padding from being interpreted as unknown
   code-generator options.

This is a bootstrap transport substitution only. It should not be mistaken for
the historical native MVS interface.

## Desired native end state

Once native `BCPLMAIN` and its parameter pseudo-stream have been reconstructed,
the compiler should again receive application options through the MVS EXEC
parameter field.

The target architecture is therefore:

```text
//BCPL EXEC PGM=BCPL,PARM='...BCPLMAIN runtime controls...<compiler>/<CG>'
```

rather than a permanent `CAMBPARM DD` convention.

The bootstrap DD should disappear from the native compiler path when the
historical `FINDPARM` contract is restored.

## Working rules for reconstruction

- Keep the two option phases distinct.
- Always state which side of the slash an option belongs to.
- Treat commented-out option cases as historical evidence, not active support.
- Do not redefine `FINDPARM` as intrinsically DD-based; native evidence ties it
  to the EXEC `PARM=` pseudo-stream.
- Keep `CAMBPARM` explicitly labeled as a bootstrap accommodation.
- Preserve second-phase `N` until binary `WRITEREC` transport is implemented
  and tested.
- When native BCPLMAIN is brought up, use the historical `BCPLCLG` parameter
  construction as a compatibility test.
