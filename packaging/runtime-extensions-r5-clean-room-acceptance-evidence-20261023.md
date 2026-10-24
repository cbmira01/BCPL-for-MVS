# Milestone Runtime Extensions — R.5 clean-room reconstruction acceptance evidence

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** R.5 — Optional Extension Packaging and Regression  
**Date of operator report:** 23 October 2026  
**Record status:** Operator-reported clean-room acceptance result; detailed
MVS evidence and owner march-closure disposition remain outstanding.  
**Official source:** GitHub `main`; do not treat MVS object libraries or
operator-local `workarea/` files as the source of project code.

## Scope and evidence source

The operator reported following the published
[clean-room MVS reconstruction runbook](clean-room-mvs-reconstruction.md)
from the beginning and completing its native production regression panel
successfully. The runbook reconstructs the interpreter-hosted **demoted
Cambridge compiler**, native Core Runtime, Base Library and optional
`BCPLDEMO` package; it does **not** reconstruct the separate native
Cambridge compiler under `cambridge-compiler/`.

This record is grounded in the operator's supplied terminal excerpt,
not an independent review of all local logs or MVS JES reports.
The operator authorized the recording and assessment of this evidence.
That approval was **not** an instruction to close R.5 or R.4.

### Operator-supplied final results

```text
RUN   156  156-optional-select-only
PASS  156  156-optional-select-only
RUN   157  157-optional-upgrade-required
PASS  157  157-optional-upgrade-required
RUN   158  158-optional-exclusion
PASS  158  158-optional-exclusion

NATIVE REGRESSION COMPLETE
PASS  158
FAIL  0
SKIP  1
TOTAL 159
```

**Reported acceptance tally:** numbered native regression cases 00–158
inclusive, **158 PASS, 0 FAIL, 1 expected SKIP**. The expected skip is
case 083, requiring source-only instrumentation in the production profile.

This meets the published full-panel count and supplies operator evidence
that cases 156–158, including optional selection and exclusion, passed.
The full 00–158 summary indicates the R.5 cases 146–158 were included,
but individual per-case logs and IEWL maps were not supplied here.

## Source, build and installation identity

The last GitHub `main` revision published in the conversation before
the operator's report was
[`00379e002c934ea16b06bc275b187bcf1cffa9f0`](https://github.com/cbmira01/BCPL-for-MVS/commit/00379e002c934ea16b06bc275b187bcf1cffa9f0).
It introduces the manifest-managed `BOOT_JCL(R5DINST)` body and
`dspal submit BOOT_JCL R5DINST` clean-room sequence. **This is a
repository reference, not a verified `git rev-parse HEAD` receipt
from the executed run.**

The published procedure's expected installed artifacts are:

| PDS alias | Required result |
| --- | --- |
| `BOOT_INTCODE` | Rebuilt `TRNILRG` and `CAMBCOMP` |
| `BOOT_OBJ` | Exactly `BCPLMAIN`, `BCPLMEM`, `BCPLBYTE`, `BCPLAPT`, `BCPLIO`, `BCPLRGS`, `BCPLREG`, and `BLIB` |
| `BOOT_DEVOBJ` | Empty in production reconstruction |
| `EXT_MAC` | `BCXPRE`, `BCXCAT`, `BCXPOST` |
| `EXT_ASM` | `BCPLDEMO` assembler source |
| `EXT_SOURCE` | `DEMOHDR` public header |
| `EXT_OBJ` | MVS-assembled `BCPLDEMO` relocatable object |
| `BOOT_JCL` | Includes manifest-managed `R5DINST` |

These are **runbook requirements**, not separately captured operator
inventory evidence. Successful full-panel execution is consistent with
their availability but does not independently prove each member count,
record format, source hash, or binary read-back comparison.

## R.5 exit-criteria assessment

The governing
[R.5 plan](runtime-extensions-r5-packaging-and-regression.md) requires
packaging, independent native cases, installed-member selection,
preservation of the prior suite, source-based reconstruction, and
actual JES/IFOX/IEWL MAP/XREF/GO evidence.

| Requirement | Current assessment |
| --- | --- |
| Consolidated one-object `BCPLDEMO` source; public header and BCX macros | Git-controlled package and manifest are present; independently installed artifact details not reviewed for this run |
| Cases 146–158 integrated with single/range/full runner | Full 00–158 runner tally reported; final 156–158 PASS shown |
| Existing 00–145 behavior preserved | Full-panel 158/0/1 tally satisfies the expected combined count; individual case evidence remains operator-local |
| Installed `EXT_OBJ(BCPLDEMO)`, selected through resident macros | Operator reports successful **published clean-room sequence**, which uses installed mode; individual install and linker reports not supplied |
| Fresh reconstruction from Git-managed sources | Operator reports clean-room setup succeeded; precise checkout SHA, JES jobs and source manifests not supplied |
| Installation read-back and comparison | `R5DINST` requires `ASMDEMO`, `PUTDEMO`, `READBACK`, `VERIFY`; their actual per-step RCs have not been provided |
| IEWL MAP/XREF and GO evidence for inclusion/exclusion | End-to-end runner PASS reported; independent MAP/XREF/GO inspection not recorded here |
| Recovery procedure | Source-controlled rebuild procedure exists; no independently observed failed-install recovery exercise is claimed |
| Explicit R.5 owner-closure disposition | **Not given**; R.5 remains **IN PROGRESS** |

The operator's reported success supports acceptance of the **full-panel
clean-room test result**, but is not a substitute for a detailed raw
JES/IEWL acceptance audit or a formal milestone-closure decision.

## Evidence needed for a final R.5 owner review

Retain or provide, without exposing credentials:

- Executed checkout SHA, clean-room run date and effective PDS aliases.
- Purge/init/populate, `ICINT19`, `CAMBBLD`, `BLDBMAIN`, `BLIBBLD`,
  and `R5DINST` payload JES job numbers and step summaries.
- Post-build `BOOT_OBJ`, `BOOT_DEVOBJ`, `EXT_OBJ`, `EXT_MAC`,
  `EXT_ASM`, `EXT_SOURCE`, and `BOOT_JCL` member listings.
- Actual `R5DINST` IFOX, binary installation, read-back, and
  `IEBCOMPR` return codes; installed-mode IEWL MAP/XREF/GO evidence
  for representative selected and excluded cases (notably 147, 156–158).
- Full `workarea/native-regression/` panel summary and saved case
  reports, including the explicit expected skip of case 083.

Do not commit authenticated JCL, batch passwords, raw private site
configuration, or unrelated operator-local files. Store safe evidence
references/checksums and conclusions in Git; raw artifacts may remain
operator-local if that is the approved handling policy.

## Disposition

**R.5 — Optional Extension Packaging and Regression: IN PROGRESS.**
The clean-room regression **acceptance target is achieved according
to the operator's report** (158 PASS, 0 FAIL, one expected SKIP).
Formal R.5 closure awaits a separate explicit owner decision and
resolution/documentation of the raw-evidence limitations above.

**R.4 — IEWL-Driven Extension Selection:** technical evidence remains
accepted on its own terms; formal closure is still pending. The
R.0–R.3 closures are unaffected.
