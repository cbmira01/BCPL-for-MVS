# Regression 069 Stage 2: explicit linked-module registration

Status: **DESIGN CHECKPOINT**. Stage 1 is verified by JOB 2424. No Stage 2
GO execution has yet occurred.

## Historical evidence and evidence limits

* `richards-bcpltape/bcplib/jcl/makelib` constructs separate
  `BCPLIB.LIBRARY` members including BLIB and BCPLMAIN, and a
  `BCPLIB.COMPILER(BCPL)` root using explicit IEWL INCLUDE operands.
  This proves object/load-library packaging, not an automatic
  BCPL global-vector initialization algorithm.
* Each surviving CG370-generated section starts with a 16-byte
  module prefix; offset +10 contains a two-byte section length and
  offset +12 contains an address of BCPLMAIN. Its trailing words
  carry `[4*MAXGN,0]` followed by `[4*global_number,address]` pairs.
  This layout is established by native execution and assembler listings.
* JOB 2424 establishes application `BCRG0069` at X'000000',
  `BCPLMAIN` at X'000088', BLIB at X'004DA0',
  with both BCPLMAIN references resolved by IEWL. It does NOT
  establish a discoverable CSECT list in the runtime image.
* The historical `makelib` JCL alone does not establish an enumeration
  protocol. In particular, do not search for unknown CSECT boundaries
  by stepping through the IEWL image or by treating its total length as a
  sequence of BCPL modules.

## Experimental (not historical) Stage 2 architecture

Use an **explicit manifest** of BCPL module entry addresses created
at link time, in this narrow regression only. For the first probe,
the manifest is the two symbolic section addresses:

    BCRG0069 (application, supplies G!1 START)
    BLIB     (resident object PDS member, supplies BLIB exports)

An external-reference relocation to each symbol is resolved by IEWL.
After establishing the global-vector sentinel, BCPLMAIN processes the
export trailer for *each declared section*, preserving G!1 from the
application, then installs its machine-supplied globals, establishes
the standard R0/R1/R2/R3/R11/R12 register contract, and enters START.

The manifest must be authoritative: **no implicit memory scanning**.
Each declared section must be bounds-checked, every trailer offset
checked against the global-vector capacity, and duplicate exported
global slots rejected unless the historical override contract is
subsequently recovered. Machine-provided globals remain explicit
runtime policy.

## First executable rung

To avoid destabilizing regressions 000-068, Stage 2 should generate a
**regression-local variant** of BCPLMAIN-wip during the test. The
canonical `asm/bcplmain-wip.asm` and PDS `ASM(BCMWIP)` stay intact.
That test variant may refer to `EXTRN BLIB`, use its relocated entry
address and encoded section length, and import its trailer *before*
branching to START. It should not be installed in a persistent PDS.

Its acceptance is:
1. Application, BCPLMAIN (test variant), and resident BLIB remain three
   distinct independent IEWL CSECTs, with correct dual references.
2. The modified BCPLMAIN also has a resolved relocation to BLIB.
3. The GO step completes RC=0000 and outputs exactly `BLIB 42`.
4. No regenerated BLIB object, no static assembler-source combining,
   no changes to the 000-068 regression baselines.
5. Failure modes and actual exported-global table are documented from
   the MVS listing, rather than inferred from the link map alone.

This is intentionally a bootstrap acceptance test, not a declaration
that the manifest is historically faithful or a general-purpose BCPL
LOAD/UNLOAD implementation. A production manifest representation and
duplicate-definition precedence require further evidence.

## Proposed executable deck now available

`prepare-stage2.py` constructs a separate `RG069X` JCL job from the
resident-compiled 069 assembler. It reuses Stage 1's `ASMAP`, `ASMRUN`,
and `LKED` steps, replacing only the BCPLMAIN SYSIN with an ephemeral
test-local variant, and adds a guarded GO step. That variant declares
`EXTRN BLIB` and imports the resident BLIB module trailer immediately
after importing the application's G!1 trailer. A relocated literal
`=A(BLIB)` supplies the manifest member address. The ordinary
`asm/bcplmain-wip.asm` remains unmodified.

This *two-member manifest hardwired into the test variant* is deliberately
simpler than a production general-purpose manifest. For the first
exercise it uses the app module passed by R15 and BLIB's explicit ESD
symbol. It is an experimental runtime reconstruction only.

From repository root, after `git pull --ff-only`, with the previously
recovered 069 assembler in `workarea/`:

```sh
python3 -m py_compile \
  native-compiler/regression/069-independent-blib-object/prepare-stage2.py
python3 native-compiler/regression/069-independent-blib-object/prepare-stage2.py \
  workarea/native-regression/069-independent-blib-object/generated.s370.asm \
  workarea/native-regression/069-independent-blib-object/069-stage2-go.jcl
```

First inspect the generated deck to confirm distinct `ASMAP`, `ASMRUN`,
`LKED`, `GO` and `EXTRN BLIB`. Then submit:

```sh
tools/submit-jcl \
  workarea/native-regression/069-independent-blib-object/069-stage2-go.jcl
```

**Status: JCL generator committed, not yet run on Hercules/MVS.**
A GO failure is possible and would be diagnostic evidence; neither the
generator nor the test has an established passing runtime result.
