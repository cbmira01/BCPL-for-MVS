# BCPLDEMO — permanent supported reference System Extension (owner decision)

**Project:** BCPL for MVS 3.8 Reconstruction  
**Decision date:** 24 October 2026  
**Disposition:** **BCPLDEMO is retained permanently as a supported reference System Extension.**  
**Package / public global:** `BCPLDEMO` / `DEMOSVC:203` (G!203)  
**Authority:** Owner approval in the project conversation after R.5 acceptance; GitHub `main` is the official documentation and source authority.

## Decision and purpose

The owner explicitly agreed to **"retain BCPLDEMO permanently as a
supported reference System Extension"**, then authorized recording the
decision in project documentation. BCPLDEMO is a maintained,
project-created optional package and interoperability benchmark;
it is **not** disposable test scaffolding or an original historical
Cambridge library service.

This continues and strengthens, rather than replaces, the original
[22 October R.2 permanent G!203 allocation](runtime-extensions-r2-bcpldemo-decision-20261022.md).
The [R.5 owner closure](runtime-extensions-r5-closure-20261024.md)
already accepted the installed package and regression tests. Neither
milestone's closure is reopened by this later support policy.

## Supported identity and operating contract

- Retain the BCEX/BCRG v1 package identity `BCPLDEMO`, the public
  dispatcher name `DEMOSVC`, and exclusive global-vector slot
  **G!203**. Its version-1 API includes shared QUERY opcode 0 and
  GETVALUES opcode 1 returning `10,20,30`, plus documented errors.
- Preserve the independently linked, explicitly selected/required
  BCXSEL/BCXREQ and IEWL INCLUDE model. Merely declaring G!203
  neither links an object nor registers the function at startup.
- Do **not** add BCPLDEMO-specific dispatch, autoload or special
  registration rules to `BCPLMAIN`, `BCPLRGS`, or the compiler.
  BCPLDEMO follows the same extension protocol as other packages.
- Maintain the Git-controlled assembler, BCPL public header,
  documentation, MVS build/install reconstruction recipe and
  selective-link examples. Installed MVS object members remain
  rebuildable products of the Git sources, not the source authority.
- Treat compatibility of the public API, BCEX export, package name,
  and G!203 assignment as a maintained interface. Changes require
  explicit design review and owner approval, not silent repurposing.

## Regression obligation

**Native regression cases 146–158 are permanent supported coverage.**
They validate empty/excluded selection, BCPLDEMO QUERY, GETVALUES,
errors, repeated calls and BCX selection/requirement behavior, including
IEWL map verification. The accepted R.5 installed-mode panel reported
**158 PASS, 0 FAIL and one expected SKIP (083)** for cases 00–158;
the installed `EXT_OBJ(BCPLDEMO)` build/readback/compare passed
**JOB 5108** (four steps RC=0000). The R.5 record retains its accepted
limitation: not every individual raw IEWL MAP/XREF was independently
manually audited.

Future native regression harness changes may reorganize tests only
with preservation of the accepted behavior and explicit project review.
Future System Extensions (including BCPLTIME, BCPLQSAM, and BCPLDEC)
can use BCPLDEMO as an independent interoperability partner, testing
distinct global registration, selected and omitted packages, mixed
dispatcher calls and register integrity. BCPLDEMO's own existing tests
need not be rewritten for every extension.

## Boundaries

**Permanent support does not mean mandatory linkage.** BCPLDEMO
remains optional for each application, not part of the Core Runtime or
historical Base Library, and carries no automatic dependency for other
extensions. Nor does it guarantee retention of any particular object
instance in a destructively reconstructed MVS PDS: the approved
rebuild-from-Git and readback policy remains in force.

This decision does **not** alter the R.0–R.5 march dispositions;
establish an additional milestone or march; revise the BCEX/BCRG ABI;
approve new T.1 regression numbers; require a new MVS job; or authorize
persistent writes to `EXT_OBJ`, `EXT_ASM`, `EXT_MAC`, `EXT_SOURCE`,
`BOOT_OBJ`, or `BOOT_DEVOBJ`. All source changes and deployments
remain subject to the project's normal approval and test process.

## Governing references

- [BCPLDEMO source, published API and instructions](../bootstrap-toolchain/extensions/bcpldemo/README.md)
- [Global Number Registry](global-number-registry.md)
- [Cambridge runtime and library nomenclature](runtime-and-library-nomenclature.md)
- [Milestone Runtime Extensions](milestone-runtime-extensions.md)
- [R.2 original allocation](runtime-extensions-r2-bcpldemo-decision-20261022.md)
- [R.5 installed-package owner closure](runtime-extensions-r5-closure-20261024.md)
