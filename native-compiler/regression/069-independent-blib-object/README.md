# 069 — Independently linked BLIB object execution

**Status: DEVELOPMENT — Stage 1 VERIFIED (JOB 2424); GO pending.** This is
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

From the repo root after `git pull --ff-only`, run:

```sh
bash native-compiler/regression/069-independent-blib-object/run-stage1.sh
```

The script compiles the application using `tools/cambridge-compile-mvs`,
generates private authenticated JCL via `prepare-linkage.py`, and submits
the **non-executing** `RG069L` three-CSECT linkage job. The transcript
will print a `JOB N` number; inspect that job using:

```sh
tools/job-summary N
tools/dump-report-for-job N
```

Gate: `ASMAP`, `ASMRUN`, `LKED` must all complete at RC=0000.
IEWL must show `BCRG0069`, `BCPLMAIN`, `BLIB` as separate CSECTs,
`INCLUDE OBJ(BLIB)`, and **both** generated-module external
references to BCPLMAIN resolved. Report the actual link map before
attempting execution. No persistent OBJ member is overwritten.

Generated JCL and recovered assembly remain in `workarea/`. The
ordinary `run-native-regression 69` path **deliberately fails** until
the new object-linked GO path can be validated; otherwise the existing
static combiner could incorrectly mark 069 PASS. Thus an entire
`run-native-regression` sweep currently encounters a planned
in-development 069 failure. The accepted historical full passing
baseline remains 000–068. Invoke `tools/run-native-regression 0 68`
to exercise only the established panel.

### Architectural concern to resolve

Each CG370 module's prefix transfers to BCPLMAIN, and its own trailer
contains exported BCPL global bindings. The current BCPLMAIN startup
can initialize only one trailer. The durable solution must discover and
register both application and library exports, then dispatch G!1 from
the application. The invocation order, module layout metadata, and
possible historic support from BCPLMAC/MAKELIB require investigation
before rewriting the runtime.

## Stage 1 verified: JOB 2424 (2026-10-08)

The resident compilation completed earlier in **JOB 2421** (ICINT19 COMP
RC=0000 and IEBGENER SVCODE RC=0000). The first valid generated
three-CSECT link job was **JOB 2424** after resolving host-side JCL
encoding/syntax and JOB-card length issues in JOBs 2422/2423.

JOB 2424: `ASMAP` IFOX00 RC=0000; `ASMRUN` IFOX00 RC=0000;
`LKED` IEWL RC=0000. IEWL echoes `INCLUDE OBJ(BLIB)`,
`ENTRY BCRG0069`, `NAME RG069OBJ(R)`.

```text
CSECT       ORIGIN   LENGTH
BCRG0069    000000   000088
BCPLMAIN    000088   004D18
BLIB        004DA0   001BB0

XREF location 00000C -> BCPLMAIN in BCPLMAIN
XREF location 004DAC -> BCPLMAIN in BCPLMAIN
ENTRY ADDRESS 000000
TOTAL LENGTH  006950
AUTHORIZATION CODE IS 0
```

This verifies an independently assembled application, independent
BCPLMAIN, and read-only consumption of the persistent BLIB object.
There is no GO step or global-vector merge evidence. **069 is not
PASS until the executable contract and exact output have been proved.**

## Stage 2 question

The application's entry trailer exports only G!1=START. The
persistently linked BLIB section contains additional exported globals
(e.g. WRITES G!60, WRITEN G!62). The present BCPLMAIN startup scans
only the entry module. Before changing the runtime, recover the
historical multi-module registration mechanism (module-entry chain,
load-module descriptor, link-editor convention, or another evidenced
mechanism). In particular, do not assume IEWL relocations themselves
install BCPL global definitions.
