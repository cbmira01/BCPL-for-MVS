# Milestone Runtime Extensions — R.0 batched MVS evidence, JOB 2195

**March:** R.0 — Evidence and contract (**open**).
**Evidence date:** 21 October 2026 (MVS/TK5 JES date).
**Nature:** Test-only proof, **not** production runtime acceptance.

## Reproduction and chain of evidence

[Tracked harness](../bootstrap-toolchain/probes/r0-batch-probes/README.md)
at GitHub commit `8e10539a2746f6301de746cb65bc6092374218d6`.
The owner ran `git pull --ff-only` and
`bash bootstrap-toolchain/probes/r0-batch-probes/run-batch.sh`
from repository root. The runner's **nine** local Python tests passed;
its credential-free generator check produced **815 JCL cards**.
The authenticated JES deck contained **817 cards**.

The actual job was **JOB 2195 / R0BATCH**, started
`21 OCT 26 00:15:20`, ended `00:15:21`. Full owner-supplied
`tools/mvs/dump-report-for-job 2195` evidence showed:

| Step | Program | Observed result |
| --- | --- | --- |
| ASMM | IFOX00 | RC=0000 |
| ASMD | IFOX00 | RC=0000 |
| ASMF | IFOX00 | RC=0000 |
| ASMH | IFOX00 | RC=0000 |
| ASMP | IFOX00 | RC=0000 |
| ASMR | IFOX00 | RC=0000 |
| LKED | IEWL | RC=0000 |
| GO | PGM=*.DD | RC=0000 |

**JOB RESULT: SUCCESS**, highest RC=0000; zero IFOX statements
flagged; highest assembler severity 0. IEWL's map placed
`R0BM`, `R0DCHK`, `R0FCHK`, `R0HOOK`,
ten package-fixture CSECTs and `R0DAT` in one temporary
load module, with resolved external symbol references.
The load module was passed through a temporary `&&` dataset,
**not installed in an accepted object PDS**.

## Actual GO/QOUT outcomes

All **twenty** independently expected records occur in the **GO
QOUT section** of the owner's full JES report, not merely in source
`DC CL80` constants or an IFOX listing. For negative cases the
assembler checks the **expected internal rejection/status code**;
a record ending in PASS is printed only if that comparison succeeds.

| Case | Actual QOUT result |
| --- | --- |
| D01 | `R0 D01 EMPTY SELECTION PASS` |
| D02 | `R0 D02 ONE PACKAGE PASS` |
| D03 | `R0 D03 THREE PACKAGE CHAIN PASS` |
| D04 | `R0 D04 MISSING DEPENDENCY PASS` |
| D05 | `R0 D05 WRONG API MAJOR PASS` |
| D06 | `R0 D06 LOW API MINOR PASS` |
| D07 | `R0 D07 REVERSED ORDER PASS` |
| D08 | `R0 D08 CYCLE ORDER REJECT PASS` |
| D09 | `R0 D09 DUPLICATE PACKAGE ID PASS` |
| D10 | `R0 D10 DUPLICATE GLOBAL PASS` |
| D11 | `R0 D11 CORE G14 REJECT PASS` |
| D12 | `R0 D12 RESERVED G200 REJECT PASS` |
| D13 | `R0 D13 MISSING APP REQUIREMENT PASS` |
| D14 | `R0 D14 TRANSITIVE MISSING DEP PASS` |
| F01 | `R0 F01 EMPTY FINISH RC0 PASS` |
| F02 | `R0 F02 REVERSE BA ONCE PASS` |
| F03 | `R0 F03 FINISH ERROR RC8 PASS` |
| F04 | `R0 F04 STOP4 PRESERVED PASS` |
| F05 | `R0 F05 STOP8 PRESERVED PASS` |
| F06 | `R0 F06 STOP0 PRESERVED PASS` |

The runner concluded:
`R.0 BATCH: ALL 20 CASES VERIFIED IN JOB 2195`.
The same report independently contains the 20 actual QOUT records.
Locally retained report:
`workarea/runtime-extensions-r0-batch/job-2195.txt`
(ignored; **not committed** to Git).

## Earlier attempts (not counted as PASS)

| Attempt | What the owner actually observed | Disposition |
| --- | --- | --- |
| First run before submission | Dry checks passed, then `wrong job card` Python error | Corrected padded authenticated JOB-card parsing |
| JOB 2193 | ASMM RC=0012 (`IFO217` on `OR 15,DEPSTAT`); ASMP RC=0008 (duplicate `EXTRN R0HOOK`); LKED/GO bypassed | Corrected instruction and declaration; also renamed colliding fixture CSECT |
| JOB 2194 | All six IFOX steps and IEWL RC=0000; GO S322 CPU-time abend after D01/D02 | Fixed dependency-loop increment: R0 cannot act as the address base in `LA 0,1(0)` |
| JOB 2195 | Eight steps RC=0000; all 20 actual QOUT lines verified | **PASS** |

Corrective commits: `57e36b7` (JOB card/FB80),
`07d2402` (IFOX/IEWL),
`8e10539` (R0 dependency-loop increment).

Together with [first linked-descriptor JOBs 2187–2192](runtime-extensions-r0-first-probes-evidence-20261020.md),
this makes **26 passing test-only R.0 case outcomes**. The first six
jobs and this batched job are separate experiments; do not call them
26 production acceptance tests.

## Evidence boundary

- Dependency validator: **no more than three selected packages**, one
  export per package, one package-local dependency; test-only local
  G!299–305 identifiers are **not assigned public globals**.
- Real IFOX/IEWL relocation, bounded fixture parsing, status-specific
  rejection, assembler finalizer linkage and reverse B-then-A order
  are supported by the actual run.
- **Not proved:** arbitrary or malicious descriptor pointer safety,
  generic multi-export transactionality, complete app/BLIB/core
  slot-owner ledger, published optional G!N values, real
  `BCPLMAIN` pre-START checking, `FINIMPL`/`STOPENT`/
  `FINEXIT`, `BCPLIO.IOFIN` or `BCPLMEM.MEMDRAIN`.
- The F01–F06 FINISH/STOP policies are **simulations within an
  assembler harness**, not real BCPL completion-path results.
- No exact binary ABI is approved merely because the fixture works.
  See the [R.0 owner-decision review](runtime-extensions-r0-abi-decision-review-20261021.md).

**March remains R.0 — Evidence and contract (open).**
**R.1 — Generic registration foundation has not started.**
