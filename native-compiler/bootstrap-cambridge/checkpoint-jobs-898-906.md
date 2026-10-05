# Cambridge bootstrap checkpoint: Jobs 898-906

This checkpoint records the state of the Cambridge compiler bootstrap after the
complete frontend/master/native-CG source set crossed the MR10 -> OCODE -> CGI ->
INTCODE path under ICINT V19.

## Proven compiler units

All ten Cambridge implementation units now compile successfully through the
bootstrap path:

```text
SYN   -> OCODE -> CGI -> INTCODE   proven earlier
LEX   -> OCODE -> CGI -> INTCODE   proven earlier
TRNA  -> OCODE -> CGI -> INTCODE   proven earlier
TRNB  -> OCODE -> CGI -> INTCODE   Job 892
BCPL  -> OCODE -> CGI -> INTCODE   Job 898 under V19

CGA   -> OCODE -> CGI -> INTCODE   Job 902, 3441 words
CGB   -> OCODE -> CGI -> INTCODE   Job 903, 3507 words
CGC   -> OCODE -> CGI -> INTCODE   Job 904, 3089 words
CGD   -> OCODE -> CGI -> INTCODE   Job 905, 2996 words
CGE   -> OCODE -> CGI -> INTCODE   Job 906, 3215 words
```

For the isolated compiler sections, the final three-cycle `CODE = -1` execution
is expected and is not a compile failure.  These modules do not constitute a
standalone START program.  Success is established by a clean source compile,
nonempty saved OCODE, successful CGI translation, and a substantial INTCODE
image.

## ICINT V19 wisdom

V19 is a capacity/layout derivative of V18, not a new execution architecture.
It keeps the existing three permanent 4K addressing regions and does not consume
a fourth base register.

Changes required by the Cambridge compiler are:

- global vector capacity increased from 401 to 700 words, allowing G!0..G!699;
- all matching OP1, GUSED, tracking, and MAPSTORE bounds increased consistently;
- V18's 40,001-word PROGVEC retained;
- an explicit LTORG placed at the executable-code/data boundary so executable
  literals stay within the existing USING coverage;
- MAPSTORE references to MSGLOB and MSEND changed from direct-address LA forms to
  loads through `=A(...)` literals because those labels moved just above x'2FFF'.

The permanent base-register plan itself is unchanged.

Jobs 894-897 were assembler-layout probes.  Job 898 was the first complete V19
master probe and established that V19 assembled, linked, compiled the Cambridge
master, generated a 2953-word INTCODE image, and entered the master.

## Standalone master execution is not the integrated test

Job 898's master-only run reached 43 cycles before failing because the other
Cambridge sections were absent.  MAPSTORE showed key rendezvous globals such as:

```text
FORMTREE   G!150 = 0
COMPILEAE  G!245 = 0
CODEGEN    G!390 = 0
```

Do not "fix" this by inventing a new unset-global convention in ICINT.  The
bootstrap design is to load all compiler modules resident together so their
GLOBAL definitions rendezvous naturally through the shared global vector.  The
historical overlay test in the master belongs to its original host/linkage
setting and should remain dormant once CODEGEN is resident.

## MR10 translator declaration-capacity derivative

CGA first exposed a separate MR10 translator limit in Job 899:

```text
TREE SIZE 11089
REPORT: TOO MANY NAMES DECLARED
COMMANDS COMPILED 0
```

The historical translator allocates a 1200-word declaration vector and stores
three words per declaration.  The bootstrap derivative therefore changes only
TRN0's capacity:

```text
VEC 1200   -> VEC 2400
DVECT 1200 -> DVECT 2400
```

`make-mr10-trn-large-names.py` generates the source-derived variant and
`build-mr10-trni-large-names.sh` rebuilds its sections and concatenates them as:

```text
native-compiler/bootstrap-cambridge/trni-large-names.int
```

The historical MR10 source remains untouched.  This derivative is now proven
sufficient for CGA-CGE source compilation.

The current tooling still requires temporary local substitution of this TRNI for
`intcode/trni.int`.  That swap is a bootstrap experiment convenience, not the
intended permanent interface.  A future tool change should add an explicit TRNI
phase override rather than require file replacement.

## Source demotion wisdom

Historical Cambridge sources remain untouched.  Bootstrap transformations are
mechanical, reproducible, and kept in `make-demoted.py`.

Proven accommodations are:

1. remove SECTION wrappers when splitting historical multi-section source
   containers into separately compiled MR10 units;
2. map historical `GET "HEADERS(...)"` member names to MVS-friendly DDNAMEs;
3. rewrite Cambridge `~=` to older `NE`, preserving lexical token boundaries;
4. split LEX packed reserved-word strings to stay below the MR10 literal limit;
5. replace later floating READFLOAT syntax with an explicit bootstrap-fatal stub
   rather than silently miscompile floating constants;
6. rewrite TRNB's one unary ABS expression into equivalent older integer BCPL;
7. omit the master's leading `NEEDS "$LOAD$"` directive for the interpreted
   all-resident bootstrap image while leaving its actual LOADSEG/UNLOAD logic
   untouched.

An important generator lesson came from Job 901.  Replacing `~=` with bare `NE`
turned `SHIFT~=0` into the identifier `SHIFTNE0`.  The correct mechanical
rewrite is token-separated ` NE `.  This applies to all adjacent occurrences,
not only that one line.

## Native CG370 section evidence

The MAPSTORE results for Jobs 902-906 show the expected partition of the CGHDR
global namespace: each isolated section populates the routines it owns while
later/other-section rendezvous globals remain zero.  Examples include:

```text
CGA: G!370 GETBYTES, G!390 CODEGEN, G!450 CG370, G!451 CGREPORT
CGB: G!500 CGSWITCH, G!510 CGENTRY, G!530 CGSTRING, G!622 CGSTART
CGC: G!520 CGSTIND, G!521 CGMULT, G!527 CGSHIFT, G!671 CGSLCTST
CGD: G!645 WRCARD, floating register/code routines, G!690 LOCK..G!692 LOCKED
CGE: G!580 COMPILE, G!581 MOVETOANYCR, G!600 GENRXA, G!644 OPCODE
```

This is strong evidence that the five INTCODE modules are meaningful isolated
pieces of the historical S/370 backend, not accidental partial outputs.

## Phase transition

The source-compatibility phase is complete for the surviving Cambridge compiler
implementation set.  The next problem is not "can MR10 compile these sources?"
It can.

The next controlled experiment is to build one resident interpreted compiler
image containing:

```text
BCPL
SYN
LEX
TRNA
TRNB
CGA
CGB
CGC
CGD
CGE
BLIBI / ICLIB / required host runtime support
```

The first integrated test should be deliberately modest.  Before asking the
compiler to translate a real source program, prove that one ICINT invocation can
load all compiler modules and that the critical GLOBAL rendezvous addresses are
simultaneously nonzero, especially:

```text
FORMTREE   G!150
COMPILEAE  G!245
CODEGEN    G!390
CG370      G!450
CGSTART    G!622
```

Only after that global-rendezvous proof should the bootstrap attempt a tiny BCPL
source -> Cambridge frontend OCODE -> CG370 native S/370 generation path.

## Preserve these boundaries

- Do not modify the historical Richards/Cambridge source files in place.
- Do not promote V19 to the default/current ICINT merely because the bootstrap
  needs it; promotion should follow ordinary regressions and a deliberate
  decision.
- Do not permanently replace the tracked MR10 `intcode/trni.int` with the
  large-name derivative until tooling and regression policy are decided.
- Treat generated demoted source, generated V19 assembler, rebuilt TRNI, OCODE,
  and per-job workarea files as reproducible artifacts unless a specific file is
  deliberately adopted as a checked-in checkpoint.
- Continue changing bootstrap semantics only when an empirical probe exposes a
  real incompatibility.
