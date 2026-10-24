# R.5 - MVS-native BCX package-selection sources

**Status:** **R.5 optional package-selection sources CLOSED and accepted by owner, 24 October 2026** following resident-MVS installed-mode regression. See the [formal closure](../../../packaging/runtime-extensions-r5-closure-20261024.md).

These three IFOX source members provide the native BCXSEL and BCXREQ
application-selection interface. They run *entirely on MVS*. The
assembler emits a single BCRG v1 object (BCPLREG CSECT), with
corresponding PUNCH records that IEWL sees as INCLUDE directives.

| File | Purpose |
| --- | --- |
| BCXPRE.asm | BCXSEL, BCXREQ and BCXEND definitions |
| BCXCAT.asm | Known installed-package catalog; BCPLDEMO only |
| BCXPOST.asm | Expands BCXEND and emits END |

The current catalog defines exactly one known package:

| Package | PDS object member | IEWL DD | BCEX exports |
| --- | --- | --- | --- |
| BCPLDEMO | BCPLDEMO | EXTLIB | DMOBEG, DMOEND |

It produces a member-qualified control statement equivalent to:

```text
 INCLUDE EXTLIB(BCPLDEMO)
```

One implementation-specific point **must be tested on IFOX/IEWL**:
the BCXCAT SETC value is an IEWL DD/member expression, substituted
inside PUNCH. The R.4 validated catalog used a sequential temporary
object DD named PKGA. It did not prove member-qualified PDS output.

In the intended installed application link, supply EXTLIB DD as an
approved read-only object PDS; it must contain a verified relocatable
binary FB80 BCPLDEMO member assembled from
[bcpldemo.asm](../bcpldemo/bcpldemo.asm). PDS creation, population,
replacement and rollback require an explicit manifest/owner approval.
Do not install into BOOT_OBJ or BOOT_DEVOBJ by assumption.

MVS source concatenation order for IFOX:

```text
BCXPRE
BCXCAT
         BCXREQ BCPLDEMO
BCXPOST
```

The registry deck's SYSPUNCH output and the ordinary IEWL SYSLIN
objects are concatenated in the final link. Core Runtime, Base
Library and BCPLRGS are still essential link components; a header
alone cannot register a package. The optional extension is never
loaded dynamically at run time.

The original R.4 standalone proof remains at
[probes/r4-bcx-macros](../../probes/r4-bcx-macros/README.md).
It retains a **test-only** R2TESTB catalog entry; that entry must not
be installed as a permanent public extension or global allocation.

## R.5 owner-approved installed layout (design only)

The manifest-managed text members are EXT_MAC(BCXPRE),
EXT_MAC(BCXCAT), and EXT_MAC(BCXPOST) under
HERC02.BCPL.EXT.MAC. Installed regressions will concatenate these
MVS-resident members with the application's selection cards, rather than
embed host copies of the macro definitions. The extension object is
EXT_OBJ(BCPLDEMO) under HERC02.BCPL.EXT.OBJ.

See [the approved installation design](../../../packaging/runtime-extensions-r5-installation-design.md).
Neither permanent dataset creation nor MVS linkage acceptance has been
authorized or performed by this design work.

## R.5 closure and installed proof — 24 October 2026

The earlier catalog/PDS notes above preserve the R.4/R.5 *design*
history. The subsequent full clean-room build installed
`EXT_MAC(BCXPRE/BCXCAT/BCXPOST)` and `EXT_OBJ(BCPLDEMO)`,
then ran native installed-mode 00–158: **158 PASS, 0 FAIL,
one expected SKIP 083**. For numbered cases 146–158, the
regression harness checked actual JES/IEWL MAP contents before PASS,
including optional member inclusion and exclusion.

The owner formally **CLOSED R.5** on this evidence, accepting the
recorded limitation that per-case raw IEWL reports were not each
manually audited. See [R.5 owner closure](../../../packaging/runtime-extensions-r5-closure-20261024.md).
The catalog is still intentionally limited to known BCPLDEMO;
no general package discovery or transitive dependency resolution
is claimed. R.4 remains pending *formal* closure.
