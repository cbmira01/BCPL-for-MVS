# M1.8 — Reproducible Runtime Builds and MVS Synchronization

Status: **ACTIVE — Gate A inventory, 13 October 2026. No OBJ promotion authorized.**

Governing policy: [Git and MVS authority](git-mvs-authority.md).
Git defines the implementation; resident MVS provides the target
build and execution proof. MVS libraries do not become a second
source-of-truth. This march does not change BCPL runtime semantics.

## Gates

| Gate | Proof |
| --- | --- |
| **A — Provenance audit** | Each of the five component sources, toolchain inputs, JCL and host-to-resident mappings identified, including non-Git dependencies |
| **B — Git-based rebuild readiness** | A clean source checkout can identify and stage its tracked inputs; any externally derived/untracked inputs must have explicit, reproducible provenance |
| **C — Controlled synchronization** | Explicit synchronization of selected source/JCL members, followed by resident independent rebuild into DEVOBJ, with no production write |
| **D — Rebuild acceptance** | Independent builds and focused execution tests for the rebuilt DEVOBJ set; confirm dependencies, member inventory and test evidence |
| **E — Optional production alignment** | Only with **separate, explicit operator authorization**, synchronize approved candidate to OBJ; never implicitly promote |
| **F — Final acceptance** | One full panel against the selected accepted object library, documenting any exceptional skip |

Gate E authorization is not inferred from running Gates A–D. A promotion
may be deferred without invalidating reproducible candidate-build
evidence; production alignment then remains pending.

## Gate A — known source provenance

| Object member | Build input mapping in `config/dspal.yaml` | Build job | Provenance |
| --- | --- | --- | --- |
| BCPLMAIN | `SOURCE(BCPLMAIN) ← asm/bcplmain.asm` | BLDDEVN | Git-tracked canonical assembler |
| BCPLMEM | `SOURCE(BCPLMEM) ← asm/bcplmem.asm` | BLDDEVM | Git-tracked canonical assembler |
| BCPLBYTE | `SOURCE(BCPLBYTE) ← asm/bcplbyte.asm` | BLDDEVB | Git-tracked canonical assembler |
| BCPLAPT | `SOURCE(BCPLAPT) ← asm/bcplapt.asm` | BLDDEVA | Git-tracked canonical assembler |
| BLIB | `SOURCE(BLIB) ← workarea/bootstrap-cambridge/demoted/blib` | BLDDEVL | **Generated (not tracked): deterministic Git-tracked `make-demoted.py --blib-only` derivative of `richards-bcpltape/bcplib/bcpl/blib`; resident sync must be verified** |

The BLIB job also reads resident `LOAD(ICINT19)`,
`INTCODE(CAMBCOMP)`, and `SOURCE(OPTIONS,CAMBPARM,LIBHDR,SYNHDR,
TRNHDR,CGHDR)`; it uses the resident IFOX assembler and an internal
two-card CG370 repair program. The SOURCEmember input paths for most
of these support records are specified by `config/dspal.yaml`, but
the exact resident binaries and their construction must be traced
before claiming clean-checkout rebuildability.

**Gate A finding (refined):** the four assembler modules are tracked
in Git. BLIB is *derivable* from Git: run
`python3 native-compiler/bootstrap-cambridge/make-demoted.py --blib-only`.
Its input is tracked historical `richards-bcpltape/bcplib/bcpl/blib`;
the generator validates the SECTION header, two inequality tokens,
LIBHDR use and an 80-column limit before creating the ignored output.
The build still requires explicit re-generation and SOURCE(BLIB)
synchronization: a successful resident object does not prove its
source matched a particular Git revision.

## Constraints and acceptance evidence

The M1.7 DEVOBJ 00–123 panel passed 123, failed 0 and skipped 083;
that is the accepted **resident baseline**, not a clean-checkout
reconstruction proof. Do not use `dspal put` on binary OBJ or DEVOBJ:
it performs text conversion. The existing IFOX and IEBGENER jobs
produce binary FB80 objects on MVS. Do not overwrite production OBJ.

Next: verify the tracked BLIB generator and source provenance,
trace ICINT19/CAMBCOMP resident bootstrap provenance, then implement
safe, explicit staging and build instructions. No new operator MVS
commands are yet required for the provenance audit.
