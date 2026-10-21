# Milestone Runtime Extensions — R.0 G!150 startup owner review

**Date:** 21 October 2026. **March:** **R.0 — Evidence and contract (open)**.
**State:** Owner-approved **test-only G!150 startup observer**
[implemented](../bootstrap-toolchain/probes/r0-g150-startup-probe/README.md)
and verified by **24 offline tests** plus a 143-card synthetic JCL check.
**Actual MVS G!150 execution and IEWL MAP/XREF remain pending**.
No runtime change or G!150 resolution policy is authorized.
**R.1 — Generic registration foundation** not started.
**Authority:** [Global Number Registry](global-number-registry.md),
[Decision E](runtime-extensions-r0-owner-abi-decisions.md) and
[ownership audit](runtime-extensions-r0-global-ownership-audit-20261021.md).

## Source-grounded owner collision

| Source | Confirmed fact |
| --- | --- |
| `bootstrap-toolchain/asm/bcplmain.asm` | After the application `GINST` importer and `BLIMP` library importer, BCPLMAIN unconditionally executes `L 1,=A(DEBUGINT)` then `ST 1,600(12)` around lines 811–812. This publishes provisional DEBUGINT into **G!150** before START. |
| `cambridge-compiler/source/bcpl.bcpl` | **Full Cambridge compiler** declares `FORMTREE:150` at line 16, then calls `FORMTREE()` in its compiler path around line 277. |
| `cambridge-compiler/source/synhdr.bcpl`, `syn.bcpl` | `synhdr` declares `FORMTREE:150` (line 67); SYN defines the function around line 90. |
| `richards-bcpltape/bcplib/bcpl/synhdr` | Historical compiler header confirms `FORMTREE:150`; changing that allocation would alter recovered source compatibility. |
| `cambridge-compiler/asm/bcplmain.asm` | Separate, **unaccepted** full-compiler runtime target also documents the conflict and currently has a G!150 DEBUGINT store. Do not confuse it with installed BOOT_OBJ(BCPLMAIN). |

**Initial startup hazard:** If an actual selected application exports
FORMTREE in its compiled trailer at byte displacement 600, the
current bootstrap runtime's import would be superseded by the
unconditional DEBUGINT publication before START. This is
**inferred from code order**; it is not a measured full-compiler
global-vector value.

**Overlay distinction:** `bcpl.bcpl` sets
`OVERLAYING := CODEGEN < 0` and, in that mode, calls
`LOADSEG("SYN")` before `FORMTREE()`. A later segment import
might repopulate G!150. Whether that occurs in the native compiler,
or works correctly, remains unverified. A startup probe alone
cannot establish the later SYN call-time owner.

## Owner choices requiring separate approval

1. **Preferred direction to investigate:** preserve historical
   `FORMTREE:150` and remove the provisional **global**
   publication of DEBUGINT or make diagnostics private. Audit
   existing regression clients before changing accepted runtime code.
2. **Possible but unapproved:** install DEBUGINT only if G!150 is
   still sentinel, analogous to G!76. G!150 has **no verified
   legacy precedence waiver**; dynamic LOADSEG and diagnostic
   behavior remain unresolved.
3. **Not recommended as first remedy:** renumber FORMTREE,
   because it changes historical compiler declarations and
   downstream source and loading assumptions.

**No G!150 number is free for an optional extension** merely
because an individual program does not export it.

## Proposed isolated R.0 G!150 probe — owner design approval needed

Use the interpreter-hosted **demoted Cambridge compiler** to compile
a minimal native BCPL application with START G!1. A guarded
test adapter adds a **real, independently relocated application
G!150 export** (known temporary function) and a **test-only
G!151 verifier**. The verifier is invoked from START, reads
but **does not modify** G!150, and compares it to the
application export address. It does not call the possibly
overwritten target.

Link the test objects with actual **installed**
`BOOT_OBJ(BCPLMAIN,BCPLIO,BCPLMEM,BCPLBYTE,BCPLAPT,BLIB)`
**read-only** into a temporary load module with
`NCAL,LIST,XREF,MAP`. Record the actual application and BLIB
trailers, all owners, relocation/map, step results and unique GO
marker. This tests **real startup precedence** using a synthetic
application G!150 export, **not** a running full Cambridge compiler.

The full compiler's later SYN/LOADSEG behavior needs a separate
test. A selected optional package's pre-START collision rejection
against an **actual** app/BLIB/core writer also remains distinct
from this observer. Neither is already verified in production
BCPLREG, which belongs to R.1.

**Owner disposition:** the bounded **G!150 startup observer** was
approved for test-only implementation and is now prepared in the
[tracked probe](../bootstrap-toolchain/probes/r0-g150-startup-probe/README.md).
It compiles a synthetic application under the demoted Cambridge compiler,
adds relocatable G!150 and G!151 exports, checks the installed BLIB
trailer, prints runtime G!150 and marker byte addresses, and links
installed `BOOT_OBJ` only as `DISP=SHR` input. It does **not** prove
the final `DEBUGINT` address identity, any full-compiler/LOADSEG behavior,
or startup collision rejection by a real registrar. Inspect real
MVS IFOX/IEWL/GO output before accepting the result. Choose any
future **G!150 resolution policy separately**.
**R.0 open; R.1 not started.**
