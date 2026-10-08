# WRITEF third-data-argument: instrumented CG370 capture

## Observed evidence, unchanged

- Regression 075, TK5 JOB 2583: expected `C:Z S:HI N:42`, actual
  `C:Z S:HI N:2`; ASMAP, ASMRUN, LKED, GO all RC=0000.
- Regression 076, TK5 JOB 2585: expected `A:42 B:11,22,33 C:HI,42`,
  actual `A:42 B:11,22,2 C:HI,42`; all four steps RC=0000.
- Regression 077: `@A` across three formal parameters PASS.
- Regression 078: fourth formal in R10 and `@A` PASS.
- Regression 079: twelve-formal procedure and `@A` PASS.
- Regression 080: twelve-formal `@A` survives nested library calls PASS.
- Regression 081: nested lexical declarations / cursor advance PASS.

These results do not establish that the installed PDS BLIB object is
bit-identical to output from the current diagnostic compiler. Historical
`WRITEF` has `FORMAT,A,B,C,D,E,F,G,H,I,J,K` formal parameters and uses
`LET T=@A`, `ARG=T!0` and then advances T. The cause of the third
data-argument corruption remains unknown.

## Existing instrumentation (verified from repository)

- `jcl/build-cg370-diagnostic.jcl` builds the diagnostic compiler image
  `HERC02.BCPL.INTCODE(CG370D)` independently of `CAMBCOMP`.
- `tools/cambridge-compile-mvs` supports `--compiler-image`, `--output`
  and `--job-name` to compile without changing the default image.
- `native-compiler/bootstrap-cambridge/check-cg370-diagnostic.py`
  checks that removing lines beginning `* CG370-DIAG:` from the diagnostic
  assembler reproduces the baseline output **exactly**.
- `native-compiler/bootstrap-cambridge/make-demoted.py --blib-only`
  prepares the canonical historical BLIB source for the resident
  compiler, without modifying historical originals.

## Capture instructions

First verify that the diagnostic member `CG370D` is installed and current;
if necessary, use the existing diagnostic build/deployment procedure
(`tools/dspal populate SOURCE`, `tools/dspal populate JCL`,
`tools/dspal submit JCL CG370DB --wait`). Do not rebuild or replace BLIB.

Then execute:

```sh
python3 native-compiler/bootstrap-cambridge/make-demoted.py --blib-only
python3 tools/capture-writef-cg370 --cases 75 76 79 80 81 --include-blib
```

The capture runs both `CAMBCOMP` and `CG370D` for each listed source,
stores the paired assembler outputs plus the extracted diagnostic comments,
then checks exact assembler equivalence after comment stripping. All
artifacts stay in `workarea/writef-cg370-evidence/<timestamp>/`. A
nonzero exit indicates a compile failure, missing diagnostic image, or
semantic-equivalence mismatch; such a result must **not** be called
instrumentation PASS.

The evidence directory includes `MANIFEST.txt`, per-unit compile logs,
`*.baseline.s370.asm`, `*.cg370d.s370.asm`,
`*.diagnostics.txt`, and `*.equivalence.log`.

For discussion, supply the `MANIFEST.txt`, historical BLIB diagnostic
extract, and any portions of its diagnostic assembler around the
`WRITEF` procedure and argument cursor. Inspect the generated
instructions, procedure entry, `@A` address calculation, argument homes,
`T!0` load, and indirect call setup. Compare the current compiled BLIB
source with the object installed in `HERC02.BCPL.OBJ(BLIB)` using actual
assembly/build evidence rather than assuming identity.

## Guardrails

No generated assembler or diagnostic log is claimed to have been run by
this repository documentation. Do not change CG370, BCPLMAIN, canonical
BLIB, or the object PDS to make failing output pass. Preserve the
existing expected outputs of regressions 075 and 076.
