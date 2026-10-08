# 069 — Independently linked BLIB object execution

**Status: DEVELOPMENT — Stage 1 (non-executing linkage) only.** This is
the next native regression identity, but **not yet a passing regression**.

## Contract

Compile the exact BCPL application exercised by 067 using the resident
Cambridge compiler. Assemble it as its **own relocatable control section**;
do not statically combine generated assembler or recompile BLIB. Explicitly
include the resident persistent `HERC02.BCPL.OBJ(BLIB)` at link edit
alongside the separately assembled BCPLMAIN-wip runtime.

Acceptance (future Stage B):
- IEWL map has three distinct sections: application, BLIB, BCPLMAIN.
- Both generated-module references to BCPLMAIN are resolved.
- BCPLMAIN initializes application G!1 and BLIB globals G!60 and G!62
  before dispatch to START, with no incorrect overwrites.
- GO executes and prints exactly `BLIB 42`; all MVS steps RC=0000.

The prior single-module BCPLMAIN implementation reads a trailer relative
to the entry module base. IEWL relocations alone cannot merge BCPL
global export trailers. Implementing multi-module initialization must be
guided by the historical Cambridge module/linkage contract.

## First gate: non-executing independent object linkage

The current gate is a standalone application-object and runtime-object
assembly with `INCLUDE OBJ(BLIB)` against the previously installed
binary object member. **No GO step.** No changes to BCPLMAIN, BLIB,
CG370, or regression 067/068.

Use the dedicated preparation script in this directory; its generated
JCL and recovered assembly remain in `workarea/` and never install into
the persistent OBJ PDS. The standard full regression panel should not
treat 069 as passing until its behavioral execution gate exists.

### Architectural concern to resolve

Each CG370 module's prefix transfers to BCPLMAIN, and its own trailer
contains exported BCPL global bindings. The current BCPLMAIN startup
can initialize only one trailer. The durable solution must discover and
register both application and library exports, then dispatch G!1 from
the application. The invocation order, module layout metadata, and
possible historic support from BCPLMAC/MAKELIB require investigation
before rewriting the runtime.
