# Runtime Extensions — reusable developer template (R.3)

These are **source templates**, not a new registered package. Their
`@...@` tokens must be replaced before assembling or compiling. They do
**not** allocate any BCPL global number, and must not be linked as-is.
Use [`BCPLDEMO`](../bcpldemo/README.md) for an actual maintained,
registered G!203 example. Use `R2TESTB` only within its R.2 tests.

## Instantiate a package

1. Read `packaging/runtime-and-library-nomenclature.md`,
   `packaging/global-number-registry.md`, and R.0 decisions A–H.
   Obtain ownership of a global number **before** publishing a header.
2. Choose an eight-character-or-shorter, uppercase EBCDIC package ID
   and unique assembler CSECT/ENTRY symbols no longer than eight bytes.
   In these templates, rename the example `TM*` symbols throughout;
   do not reuse them unchanged alongside another instantiation.
3. Replace `@PACKAGE@` (1–8 uppercase characters, CL8 padded),
   `@GLOBAL@` (an approved numeric G!1..699 owner), and `@SERVICE@`
   (the declared BCPL dispatcher name). Keep version 1 BCEX/BCRG
   binary layouts and an identical QUERY major/minor in dispatcher
   and descriptor. Review the API before changing GETVALUES.
4. For **no finalizer**, replace `@FINEX@` with a blank assembler
   comment line and `@FINADR@` with `F'0'`. Do not link `finalizer.asm`.
   For a **finalizer**, replace `@FINEX@` with
   `         EXTRN TMFIN` and `@FINADR@` with `A(TMFIN)`; assemble/link
   `finalizer.asm` with the same application. Rename symbols consistently.
5. Assemble `dispatcher.asm` and `descriptor.asm` separately using
   IFOX; link with the application-specific `registry.asm`. Include
   the **same** generic `RGINIT`/`RGFINI` registrar and unchanged
   candidate `BCPLMAIN` across selections. For no selected packages,
   use `bootstrap-toolchain/asm/bcplreg-empty.asm` instead.
6. Make the application explicitly require the same package ID in
   `BCPLREG`. Add dependency records to BCEX and list selected packages
   in dependency-first order if it depends on other packages. Recompute
   exact declared lengths: BCEX `48+8*K+16*D`, BCRG `28+8*N+8*M`.
   This small example uses K=1, D=0, N=1, M=1.

## Interface and lifecycle

`@SERVICE@(0,0,0)` returns six, then a valid six-word vector and
capacity six return six and the QUERY prefix `(1,1,0,6,1,0)`.
Opcode 1 fills three BCPL words `(10,20,30)` on sufficient capacity.
Insufficient capacity returns -1 with no writes, unsupported opcodes
return -2, and bad QUERY arguments return -3. BCPL vector pointers
arrive as **word addresses** in R8; convert to bytes only after
validation. R7 carries the opcode and signed result; R9 the capacity.

There is no version-1 initializer hook. Registration runs before
`START`; the optional finalizer runs once, in reverse selection order,
before `BCPLIO.IOFIN` and `BCPLMEM.MEMDRAIN`. It is passed an 8-byte
MVS pointer through R1 with FINISH/STOP reason and STOP code. Nonzero
finalizer return is diagnosed as 2001. `FINISH` yields job RC=8 on
such an error, while STOP(n) retains n.

The template makes **no** claim that it protects against fabricated
caller pointers, that it has been independently assembled under MVS,
or that a newly chosen global number is available. Use the established
R.1 relocation provenance check and inspect actual IEWL MAP/XREF.

## Public header conventions

`public.h.in` is only a declaration pattern. Rename the `TEMPLATE_`
manifest prefix for the new package and document each opcode. A `GLOBAL` changes how
compiled BCPL refers to G!N; it neither includes object code nor
registers a package. `MANIFEST` constants are package-local opcode
and version values, not global slots. The demoted Cambridge compiler
R.2 build has **not proven general header inclusion**, so compiled
examples may need those declarations present directly in their source
until that mechanism is separately demonstrated.

The `client.bcpl.in` example repeats declarations inline (as do the
R.2 compiled clients) and exercises QUERY, capability values,
GETVALUES and an unsupported opcode. It checks the exact teaching
version 1.0; production clients should accept the required major
and a compatible minor greater than or equal to their minimum.
The selected package must still be listed in the application BCRG.

Consult `packaging/runtime-extensions-r3-linkage-guide.md` for the
0/A/B/A+B build and IEWL selection recipe. Generated JCL, compiled
source and JES evidence must remain under ignored `workarea/`.
