# Milestone Runtime Extensions — R.0 native global-owner source inventory

**Status:** Source-derived partial owner ledger, 20 October 2026.
**March:** R.0 — Evidence and contract (**open**). This is an
inventory of current direct writes in the **bootstrap-toolchain**
`BCPLMAIN`; it is not a complete executable global-owner map,
a verified CG370/BLIB trailer decode, or new global assignments.
Nothing is implemented or approved by this record.

**Source:** `bootstrap-toolchain/asm/bcplmain.asm` in the GitHub
repository reviewed at `0bc9245`. The importer walks the
application CG370 trailer, then the BLIB trailer, then installs
the following direct native values. The table uses System/370
byte displacement `4*N` from R12 to identify BCPL G!N.

## Explicit native writes

| G!N | Byte offset in G | Value/source expression | Source character |
| ---: | ---: | --- | --- |
| 0 | 0 | `GLOBCNT` (=699), not a procedure entry | Runtime extent metadata |
| 6 | 24 | `R13 >> 2` (provisional `SAVEAREA`) | Native direct |
| 11 | 44 | `IOSELIN` | Native direct |
| 12 | 48 | `IOSOUT` | Native direct |
| 13 | 52 | `IORDCH` | Native direct |
| 14 | 56 | `IOWRCH` | Native direct |
| 15 | 60 | `IOUNRD` | Native direct |
| 16 | 64 | `IOINP` | Native direct |
| 17 | 68 | `IOOUT` | Native direct |
| 30 | 120 | `STOPENT` | Native direct |
| 33 | 132 | `IOWRAP` | Native direct |
| 39 | 156 | `IOPARMST` | Native direct |
| 40 | 160 | `APTOVEC` | Native direct |
| 41 | 164 | `IOFOUT` | Native direct |
| 42 | 168 | `IOFINDIN` | Native direct |
| 46 | 184 | `IOENDRD` | Native direct |
| 47 | 188 | `IOENDW` | Native direct |
| 52 | 208 | `MODBASE >> 2` | Provisional metadata |
| 53 | 212 | `MODEND >> 2` | Provisional metadata |
| 54 | 216 | `DYNWORK >> 2` | Provisional metadata |
| 55 | 220 | `DYNEND >> 2` | Provisional metadata |
| 76 | 304 | `WRITEST` **only if G!76 still equals its sentinel**; otherwise preserve imported `WRITEF` | Existing intentional fallback |
| 85 | 340 | `GETBYTE` | Native direct |
| 86 | 344 | `PUTBYTE` | Native direct |
| 87 | 348 | `GETVEC` | Native direct |
| 88 | 352 | `FREEVEC` | Native direct |
| 150 | 600 | `DEBUGINT` | Native direct |

The source also installs application G!1 START through
`GINST`, validates that it is no longer a sentinel after
`BLIMP`, and transfers control through G!1.
Other application and BLIB trailer exports are **variable**; they
cannot be inferred solely from the direct-write table above.

The list reflects visible direct `ST value,offset(12)` and
initializer statements. It does not claim to inventory every possible
indirect write or generated symbol in the full compiler. The
**separate** `cambridge-compiler/asm/bcplmain.asm` is a distinct
target and may have different internals.

## Current precedence hazards

1. **Application trailer importer** `GSCAN/GINST` writes globals
   to G!N with no general owner table or duplicate rejection.
2. **BLIB importer** `GIDONE/BLIMP` writes a second set of
   globals directly; a prior application's assigned global may
   be overwritten without preserving provenance.
3. **Native assignments** subsequently replace or fill slots.
   The explicit G!76 sentinel-aware conditional is documented
   existing behavior and must remain unchanged.
4. **Historical LIBHDR slot 94** has two names recorded by the
   official Global Number Registry; this is a naming collision
   in historical headers, **not evidence** that two procedures
   were both installed at runtime.
5. **G!150** has a known native DEBUGINT versus full-compiler
   FORMTREE conflict in the registry. Do not silently treat
   G!150 or all values above FIRSTFREEGLOBAL=150 as free.
6. **G!200–202** are assigned in the Global Number Registry to
   BCPLQSAM, BCPLTIME and BCPLDEC. Those declarations do not
   install code, and their owners must be enforced at registry
   validation. JOB 2157's G!200 application-trailer injection
   was a **test-only** linkage mechanism, not production
   permission for an application to override selected packages.

## What remains before a full R.0 collision contract

- Decode the **actual generated application and separate BLIB**
  trailer pair lists from a reproducible current native program,
  not merely historical LIBHDR names.
- Inventory potentially written globals in other runtime
  components and list any **intentional existing precedence**
  with a regression test. Record exact waivers, not a blanket
  override permission.
- Validate effective app/BLIB/core owners against extension
  descriptor exports **before publishing any optional G!N**.
- Test a genuine conflict across an application, BLIB/core and
  a selected optional module. A normal pre-START failure
  requires evidence; this inventory alone cannot prove it.

See [the R.0 three-question review](runtime-extensions-r0-three-design-questions-review-20261020.md)
for candidate validation and dependency rules.
