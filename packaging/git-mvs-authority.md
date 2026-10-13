# Repository authority and the role of resident MVS

Status: **Project architecture policy — 13 October 2026**.

## Principle

**Git is authoritative for what the BCPL reconstruction is. MVS is
authoritative for whether its assembled and linked programs work on
the target operating system.**

The resident TK5/Hercules machine is a target and evidence-producing
build/execution environment, not a parallel source-control system.
An MVS PDS member is not made authoritative merely because an
assembler, linker, or application has successfully consumed it.

## Ownership and reproducibility

| Location | Role |
| --- | --- |
| Git repository | Tracked implementation sources, historical inputs or their documented provenance, JCL bodies, build scripts, configuration templates, regression specifications, and acceptance records |
| Workstation `workarea/` | Regenerable compiler output, temporary JCL, reports and exploratory build artifacts; not a release authority |
| MVS `SOURCE`, `JCL` and associated datasets | Synchronized resident inputs, staged from Git-controlled material when available |
| MVS `DEVOBJ` | Candidate relocatable objects for isolated development and integration tests |
| MVS `OBJ` | Accepted deployed relocatable objects; a useful stable execution baseline, not the authoritative definition of their sources |
| JES, IFOX00, IEWL and application GO evidence | Target-system verification of build, linkage and behavior |

A successful regression proves the **specified tested behavior** of
the resident objects; it does not prove full historical compatibility,
byte-for-byte equality to other objects, or complete source
reproducibility unless those properties were directly tested.

## Working rules

1. Maintain code and JCL changes in Git. Synchronize to MVS using
   controlled `dspal put` or other explicit transfer operations.
   Do not maintain untracked MVS-side source edits as the durable
   implementation. If an emergency resident patch occurs, capture
   and reconcile it in Git before treating the state as reproducible.
2. Build candidate objects in DEVOBJ. Verify using focused MVS tests,
   followed by one full authoritative panel at the end of the march.
   Do not silently switch between OBJ and DEVOBJ.
3. Never overwrite production `HERC02.BCPL.OBJ` without explicit
   operator authorization. Accepted production objects may be retained
   as a safe execution baseline and for short-term recovery, but they
   do not displace source and build procedures in Git.
4. A future synchronization or promotion mechanism should be
   deterministic, explicit about its input revision and member set,
   and fail closed on missing dependencies. Backup/rollback is an
   operational precaution, not a second configuration authority.
5. Preserve reproducible evidence: source revision, resident input
   synchronization, build job identity, assembler/link return codes,
   tested object library, regression results, and relevant exceptions.
6. ChatGPT owns independent source/tooling checks where its execution
   facilities allow; the operator performs tasks that genuinely need
   the workstation's resident files or Hercules/MVS access.

## Reconstruction qualifications

The five BCPL runtime members can now be independently built into
DEVOBJ and have passed integrated MVS regression. This does **not**
mean the entire bootstrapping toolchain has been proved rebuildable
from a pristine Git checkout. BLIB is compiled using the resident
Cambridge/CG370 path, including ICINT19, CAMBCOMP and associated
resident datasets. Treat those inputs as explicit dependencies and
audit their provenance and reconstruction paths rather than assuming
the resident PDS contains canonical originals.

`asm/bcplmain-wip.asm` is retained as a historical/source-only
diagnostic fixture, notably for regression 083; it is not a competing
authoritative runtime source. The normal installed-object workflow
uses canonical `asm/bcplmain.asm`.

## Consequence for M1.8

**M1.8 — Reproducible Runtime Builds and MVS Synchronization** should
audit build-input provenance, demonstrate reconstruction of the five
candidate objects, standardize dataset synchronization, and verify
the resulting runtime by MVS execution. Any update of production OBJ
is a separate explicitly authorized action. Do not turn M1.8 into a
second MVS-side release database or insist on enterprise deployment
ceremony unsupported by the project's actual needs.
