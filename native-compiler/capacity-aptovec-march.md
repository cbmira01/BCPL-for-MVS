# BCPLMAIN capacity and APTOVEC march

Status: **OPEN — historical contract established; baseline preserved**
Date: 2026-10-09. Starting native regression baseline: **90/90 PASS**.

## Purpose

Make the historical Cambridge compiler's global-vector and workspace
requirements explicit and design the native implementation of G40
APTOVEC before altering canonical `asm/bcplmain-wip.asm`.

## Primary-source APTOVEC contract

Martin Richards, *The BCPL Programming Manual* (1974), "Other useful
subroutines", defines `APTOVEC(F,N)`: apply F to arguments V and N,
where V is a temporary stack vector of size N. Its explanatory,
intentionally invalid BCPL analogue is:

```bcpl
LET APTOVEC(F,N) = VALOF
$( LET V = VEC N
   RESULTIS F(V,N)
$)
```

Facsimile (alternate scan):
https://people.csail.mit.edu/saltzer/Multics/MHP-Saltzer-060508/filedrawers/177.bcpl/Scan%202.PDF

The 1977 *Finning BCPL System Reference Manual* further describes
constructing the variable-sized stack vector **and calling sequence**
on the stack, checking stack overflow regardless of generator options,
and returning F's result through APTOVEC. This is corroborating
implementation detail from a related BCPL system, not proof of
identical Cambridge S/370 machine instructions:
https://softwarepreservation.computerhistory.org/BCPL/finning/Finning_BCPL_Compiler_Reference_Manual__1977.pdf

**Do not implement G40 by simply calling GETVEC.** APTOVEC's vector
must have the lifetime and layout of the nested F call; N is
passed through as F's second argument. `VEC N` contains elements
V!0 through V!N (N+1 words), according to the project's verified
native vector convention. Validate bounds, frame overlap and stack
headroom against emitted CG370 linkage before choosing assembly.

## Capacity evidence from current source

In `asm/bcplmain-wip.asm`:

- `GLOBCNT EQU 200`, `GVBYTES=(GLOBCNT+1)*4`: 804 bytes
  for G!0..G!200.
- Startup scans module-export trailer entries and rejects offsets
  greater than `=F'800'` at both trailer validation and installation.
  Enlarging GLOBCNT alone **does not** lift that limit.
- `DYNLEN DC F'17444'` = 804 global bytes + 16,384 stack bytes
  + 256 clearance bytes; one GETMAIN region.
- `DYNWORK` follows the global vector; `STKLIM=DYNWORK+16384`;
  `DYNEND=STKLIM+256`.
- The public `STACKBASE` and `STACKEND` globals are BCPL word
  pointers to DYNWORK and DYNEND, respectively.
- G!0 contains 200 as the global vector maximum; keep its meaning
  synchronized with the allocated extent and module trailer checks.

The compiler master in `richards-bcpltape/bcplib/bcpl/bcpl` sets
`STACKSIZE=STACKEND-STACKBASE`, defaults `FREESTACKSIZE=3000`,
computes `WORKSPACESIZE=STACKSIZE-FREESTACKSIZE`, and requires
`WORKSPACESIZE >= 5000` before
`APTOVEC(COMP,WORKSPACESIZE)`. Even counting the 256-byte
clearance as published (64 words), current `STACKSIZE` is only
4160 words, leaving 1160 after the default reserve: **below 5000**.
The current **safe** stack extent is 4096 words, leaving only 1096
after the same reserve. Either way, the native compiler cannot
enter its main compilation workspace under current defaults.

The resident INTCODE bootstrap used a 700-word global vector
and exercised `FORMTREE G!150`, `COMPILEAE G!245`,
`CODEGEN G!390`, `CG370 G!450`, `CGSTART G!622`;
see `native-compiler/bootstrap-cambridge/compiler-image-next.md`.
These demonstrate need for at least G!622 in that image, but do
**not** yet prove the maximum global number in the independently
linked native compiler sections.

## Design constraints and proposed first implementation

1. **Capacity survey first:** derive compiler native maximum-G
   requirements from all ten source sections' GLOBAL declarations,
   plus their CG370-generated module trailers and runtime-supplied
   slots. Record maximum slot and the highest export before choosing
   a global-vector capacity. A capacity of at least 700 words is a
   plausible initial target **only after** validating the native
   compiler requirement.
2. **Parameterize the allocation:** bind GLOBCNT, byte extent,
   workspace size and clearance to one documented layout.
   Remove duplicate hard-coded 800-byte global limits. Respect
   IFOX base/addressability and MVS GETMAIN macro constraints.
3. **Clarify STACKEND:** reconcile publicly visible STACKEND with
   the stack-check safe boundary STKLIM so APTOVEC never allocates
   into reserved clearance. Preserve prior regression behavior
   until a targeted test establishes the policy.
4. **APTOVEC design:** reconstruct a function invocation with
   a variable-sized BCPL stack vector and second argument N,
   honoring R4=B, R5=P, R6=L, R7/R8 arguments, R15=W,
   BCPL word pointers and stack checks. Do not assume the
   vector can be placed outside the activation or that
   R14/R15 survive MVS macros.
5. **Acceptance ladder:**
   - A test-local high-global allocation/trailer probe, then
     a canonical capacity change with existing cases passing.
   - A G40 APTOVEC probe that checks V!0, V!N, N,
     nested function invocation and return value.
   - A near-limit APTOVEC stack-overflow test that fails in a
     controlled fashion, not through an S0C4 overwrite.
   - A compile/link probe for the full compiler's real global
     assignments and workspace entry.
   - Full native regression panel after each accepted submilestone.

## Explicit non-goals of first rung

Do not yet add extension-library procedures, stream I/O or
general LOAD/UNLOAD support. Do not adopt an arbitrary huge static
allocation without checking native compiler globals and real
compiler workspace usage. Do not interpret the 1977 Finning manual
as machine-specific S/370 code evidence.

## Current status

Historical APTOVEC semantics are identified and quantitative
capacity blockers established. **No executable BCPLMAIN changes
or new native regression tests yet.** Existing 90/90 acceptance
remains the entry baseline, not a claim that a larger compiler
image or APTOVEC has passed.
