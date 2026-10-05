# Cambridge compiler-image bootstrap phase

## Milestone reached

Jobs 885, 888, 889, and 892 established successful MR10 bootstrap compilation
of all four Cambridge frontend/translator implementation sections:

```text
SYN   -> OCODE -> CGI -> INTCODE
LEX   -> OCODE -> CGI -> INTCODE
TRNA  -> OCODE -> CGI -> INTCODE
TRNB  -> OCODE -> CGI -> INTCODE
```

The isolated final RUN faults are expected: these sections are not complete
START programs by themselves.

The Cambridge master also crosses the MR10 bootstrap boundary. Job 898, using
ICINT V19, saved nonempty `bcpl.ocode`, generated a 2953-word INTCODE image, and
entered the master. Its standalone execution then stopped because the other
compiler sections were absent, which is expected for a master-only image.

The complete native S/370 backend has now crossed as well:

```text
CGA -> OCODE -> CGI -> INTCODE   Job 902, 3441 words
CGB -> OCODE -> CGI -> INTCODE   Job 903, 3507 words
CGC -> OCODE -> CGI -> INTCODE   Job 904, 3089 words
CGD -> OCODE -> CGI -> INTCODE   Job 905, 2996 words
CGE -> OCODE -> CGI -> INTCODE   Job 906, 3215 words
```

No additional CG source-demotion issues were exposed after the token-boundary
fix for Cambridge `~=`. The source-compatibility question for the surviving
Cambridge implementation set is therefore answered: MR10 can compile all ten
units with the controlled bootstrap accommodations documented here and in
`checkpoint-jobs-898-906.md`.

## ICINT V19

ICINT V19 is a capacity/layout-only bootstrap candidate derived from V18:

- global vector enlarged from 401 to 700 words, supporting G!0..G!699;
- matching OP1/GUSED/MAPSTORE bounds enlarged consistently;
- V18 40,001-word PROGVEC retained;
- executable literals flushed explicitly at the executable-code/data boundary;
- the two MAPSTORE messages above x'2FFF' reached through address literals;
- the existing three permanent base-address regions retained unchanged.

Jobs 894-897 isolated the assembler layout/addressability effects of the larger
static area. Job 898 is the first complete V19 master proof.

Do not infer from the master-only run that unused globals should be initialized
to a new negative sentinel. The intended bootstrap is an all-resident image in
which the compiler sections rendezvous through their shared GLOBAL slots.

## MR10 large-name translator derivative

Job 899 exposed the MR10 translator's historical declaration-vector limit:

```text
TREE SIZE 11089
REPORT:   TOO MANY NAMES DECLARED
COMMANDS COMPILED 0
```

The translator stores three words per declaration in a 1200-word vector. The
bootstrap derivative changes only TRN0 capacity:

```text
VEC 1200   -> VEC 2400
DVECT 1200 -> DVECT 2400
```

`make-mr10-trn-large-names.py` generates the source-derived variant and
`build-mr10-trni-large-names.sh` rebuilds it as:

```text
native-compiler/bootstrap-cambridge/trni-large-names.int
```

This derivative is proven sufficient for CGA-CGE. The historical MR10 source is
left untouched.

The current local file-swap used during proof runs is temporary. Permanent
tooling should eventually accept an explicit TRNI phase override rather than
requiring replacement of tracked `intcode/trni.int`.

## Bootstrap-only transformations

Historical sources remain untouched. `make-demoted.py` performs the reproducible
bootstrap transformations.

For SYN/LEX/TRN and CG sections:

- split historical multi-SECTION containers at their SECTION boundaries;
- omit SECTION wrappers and inter-section terminators from the separately
  compiled units;
- map historical `GET "HEADERS(...)"` names to MVS DDNAME-friendly names;
- rewrite Cambridge `~=` to older `NE`, preserving token boundaries;
- split LEX packed reserved-word strings to fit MR10 literal limits;
- replace LEX READFLOAT with an explicit bootstrap-fatal stub because MR10
  cannot parse the later FLOAT/# syntax;
- rewrite TRNB's one unary ABS expression into equivalent older BCPL.

For the master `BCPL` section:

- omit the `SECTION "BCPL"` wrapper;
- omit the leading `NEEDS "$LOAD$"` object dependency directive;
- retain the actual `LOADSEG`/`UNLOAD` code unchanged.

The important Job 901 lesson is that a purely textual `~=` -> `NE` rewrite can
merge tokens (`SHIFT~=0` -> `SHIFTNE0`). The generator now emits token-separated
` NE ` and treats lexical preservation as part of the demotion contract.

## Current phase: resident compiler image

The bootstrap problem is no longer whether the Cambridge source can cross the
MR10 dialect boundary. That phase is complete.

The next controlled experiment is to load these INTCODE units together under
ICINT V19:

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

The global vector is the rendezvous mechanism. Before compiling a real BCPL
program, first prove that one ICINT invocation loads all modules and that the key
compiler globals are simultaneously populated, especially:

```text
FORMTREE   G!150
COMPILEAE  G!245
CODEGEN    G!390
CG370      G!450
CGSTART    G!622
```

Only after this all-resident linkage proof should the bootstrap attempt a tiny
BCPL source through the Cambridge frontend and native CG370.

## Discipline for the next phase

- Keep historical Richards/Cambridge source immutable.
- Keep demotions and capacity changes source-derived, deterministic, auditable,
  and removable.
- Do not promote V19 to `config/CURRENT` merely because this bootstrap requires
  it; promotion needs ordinary regressions and a deliberate decision.
- Do not permanently replace the tracked default TRNI with the large-name
  derivative until tooling/regression policy is settled.
- Treat generated demoted source, generated V19 assembler, rebuilt TRNI, OCODE,
  and workarea output as reproducible artifacts unless deliberately adopted as a
  repository checkpoint.
- Let probes expose the next runtime/linkage incompatibility before changing
  bootstrap semantics.

For the detailed Jobs 898-906 checkpoint, see
`checkpoint-jobs-898-906.md`.
