# Milestone BCPLTIME — T.0 owner closure (24 October 2026)

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** T.0 — Descriptor, Dispatcher, and Native Execution  
**Owner decision:** **CLOSE T.0; OPEN T.1 — Packaging and Acceptance.**  
**Tested source:** [`20380359cc83d3382abb8c144bf9f77d59d9c061`](https://github.com/cbmira01/BCPL-for-MVS/commit/20380359cc83d3382abb8c144bf9f77d59d9c061)  
**Date:** 24 October 2026  
**Disposition:** T.0 temporary-link native execution accepted; **persistent package installation and T.1 acceptance are not implied**.

## Owner decision

After reviewing successful operator evidence, the owner explicitly directed
**"Close T.0, open T.1."** This closes the current T.0 and activates the
existing **T.1 — Packaging and Acceptance** as defined in the
[official milestone](milestone-date-and-time-services.md). These are
the owner-approved accelerated marches. The earlier 15 October 2026
proposed T.0–T.4 structure remains superseded historical evidence.

## Accepted implementation

- **BCPLTIME** is an optional project-created **System Extension**;
  its BCEX version-1 descriptor and native assembler dispatcher share
  one object (two CSECTs `TIMDESC` / `TIMDISP`).
- G!201 is assigned to BCPLTIME; its tested source-level global
  declaration is `TIMESVC`. Its three operations are QUERY (0),
  STCK (1), and raw MVS TIME (2), with the accepted `-1/-2/-3`
  argument/opcode errors and caller-owned output vectors.
- Source-mode link selection uses existing BCX macros plus temporary
  BCPLTIME catalog/selection source; it does not install or replace
  the production `BCXCAT`.

## MVS 3.8J TK5 evidence

The operator ran `bash tools/bootstrap/run-bcpltime-t0 --check`
and `bash tools/bootstrap/run-bcpltime-t0`, then supplied the
JOB 5436 report from `tools/mvs/dump-report-for-job 5436`.

| Evidence | Job | Observed outcome |
| --- | ---: | --- |
| Demoted Cambridge compiler driver | **5435** | Generated native System/370 assembler CODE saved |
| T.0 IFOX assembly steps | **5436** | ASMA, ASMN, ASMR, ASMT, ASMG **all RC=0000**; no flagged statements; severity 0 |
| T.0 IEWL | **5436** | LKED **RC=0000** |
| Native BCPL execution | **5436** | GO **RC=0000**, no ABEND |
| IEWL map verification | **5436** | **PASS**; `TIMDESC` 0x38 (56 bytes), `TIMDISP`, `BCPLREG` 0x2C (44 bytes), application entry address 0 |
| Integrated direct BCPL behavioral test | **5436** | QUERY/STCK/TIME, unsupported opcode, invalid/undersized buffer and guard cases completed; **`BCPLTIME T0 PASS`** observed |

Observed raw result record (BCPL prints 32-bit words as signed integers):

```text
BCPLTIME STCK HI LO CC -478504444 -1149435904 0
BCPLTIME MVS TIME R0 R1 404894210 19278207
BCPLTIME T0 PASS
```

STCK returned condition code **0** on this invocation. No calendar
conversion or general clock-accuracy guarantee is implied by this
raw-output evidence. The IFOX listing for MVS `TIME DEC` shows its
`LA 1,2(0,0)` / `SVC 11` expansion.

**Corrected failure:** Prior JOB **5434** also assembled and linked
with RC=0000, but GO abended **S0C4** after the TIME service changed
R0/R1, which are permanent CG370 registers. The accepted
`20380359` revision saves R0/R1 in callee-frame words +24/+28,
copies the raw TIME results into the caller vector and restores
R0/R1 before returning. JOB 5436 passed after this correction.

**Evidence limitation:** The automated checker confirmed the
expected SYSPRINT logical record once but reported
`JES DD attribution NOT VERIFIED`. This auxiliary attribution
was not independently verified; the IEWL map, step return codes
and expected output were separately observed. The test's many
negative assertions are integrated BCPL caller checks, not
independent per-call MVS traces. The complete operator-local
JES listing and authenticated JCL have not been committed.

## Retained limits and T.1 handoff

T.0 closure is **not** acceptance of optional-extension PDS
installation, installed-mode behavior, unselected-package linking,
the full production regression panel, a fresh clean-room
reconstruction, historical binary compatibility, or a decoded
calendar representation of the MVS TIME words. The assembler's
private STCK scratch is **non-reentrant**.

**T.1 — Packaging and Acceptance is IN PROGRESS.** Its
already-approved scope is to design and verify optional BCPLTIME
packaging alongside BCPLDEMO, extend the known-package BCX catalog,
document reproducible installation/rollback, test selected and absent
link configurations, exercise installed mode, and run the accepted
native production regression panel. Owner review and acceptance
remain required at T.1 closure.

This march transition authorizes **no permanent writes** to
`EXT_OBJ`, `EXT_MAC`, `BOOT_OBJ`, or `BOOT_DEVOBJ`. Review exact
PDS members, deployment procedure and rollback with the owner
**before installation**. GitHub `main` is the sole official source
of code and documents; no new march, Git branch or ABI revision
is created.

## References

- [Official Milestone BCPLTIME](milestone-date-and-time-services.md)
- [BCPLTIME source and test procedure](../bootstrap-toolchain/extensions/bcpltime/README.md)
- [Runtime Extensions and BCEX/BCRG version 1](milestone-runtime-extensions.md)
- [R.5 optional-extension packaging precedent](runtime-extensions-r5-closure-20261024.md)
- [Global Number Registry](global-number-registry.md)
