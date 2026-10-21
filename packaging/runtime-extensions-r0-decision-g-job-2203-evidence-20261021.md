# Milestone Runtime Extensions — R.0 Decision G, JOB 2203

**March:** **R.0 — Evidence and contract (open)**.
**Date:** 21 October 2026. **Disposition:** **PASS — isolated Decision G
numeric boundary experiment only**; this does not close R.0.
**Probe source commit:** `2a22f8702abbd7d33a8bcd32b31e1a4f9936e517`.
**Contract:** [owner-approved Decision G](runtime-extensions-r0-decision-g-contract-20261021.md).
**Harness:** [R.0 G limits probe](../bootstrap-toolchain/probes/r0-g-limits-probe/README.md).

## Reproduction and results

The owner pulled commit `2a22f87` from GitHub `main` and ran:

```sh
bash bootstrap-toolchain/probes/r0-g-limits-probe/run.sh
```

Fourteen Python unit tests completed **OK**. The credential-free
generator check reported **167 JCL cards**, 14 cases and no generated
credentials or JCL. The runner generated a private authenticated
deck under ignored `workarea/runtime-extensions-r0-g-limits/`,
then submitted **JOB 2203 / R0GLIMIT** through JES reader port 3505.
The actual JES report covered **21 OCT 26 14:18:03–14:18:03**.

| Step | Program | Observed result |
| --- | --- | --- |
| ASMC | IFOX00 | RC=0000 |
| ASMD | IFOX00 | RC=0000 |
| LKED | IEWL | RC=0000 |
| GO | Temporary linked test executable | RC=0000 |

The job summary reported **SUCCESS**, highest RC **0000**,
**zero assembler statements flagged**, assembler highest severity **0**,
CPU **0.11 seconds**, SRB **0.01 seconds**, **169** JCL cards and
**502** SYSOUT records.

The test's report verifier concluded:

```text
R.0 G LIMITS: 14 GO MARKERS VERIFIED
R.0 Decision G MVS boundary evidence: JOB 2203
```

The full JES listing and linker MAP were retained locally but **were
not supplied for independent line-by-line review** in this conversation.
The result above is grounded in the owner's run output and the tracked
generator/verifier, not a separately reviewed listing.

## Exactly what the fourteen GO scenarios check

The independently assembled `R0GCHK` and `R0GDAT` test objects were
IEWL-linked into a temporary `&&` load module. Each scenario compares
the assembler's **actual internal status** against the expected
Decision G identifier before printing its own PASS marker.

| Group | Cases | Expected internal status |
| --- | --- | --- |
| Registry | N=M=0; N=1,M=0; N=M=32 | 0 (valid) |
| Registry | N=33; M=33; N=-1; M=-1 | **1003** |
| Package | K=1,D=0; K=8,D=16 | 0 (valid) |
| Package | K=0; K=9; D=17; K=-1; D=-1 | **1006** |

The assembler checks `28+8*N+8*M <= 540` and
`48+8*K+16*D <= 368` **after** rejecting negative or excessive
counts. All 14 actual GO markers were verified once, and no scenario
produced the failure marker. The test's complete set is
`make-job.py:CASES`, kept in Git as the repeatable oracle.

Host-side `limits.py` and its unit tests examine wider
`BCRG`/`BCEX` formatting and diagnostic categories using **trusted
local byte arrays and simulated extents**. Those tests do not execute
MVS object code and are not evidence of safe arbitrary-pointer access.

## Scope and limitations

- This is **not** a production `BCPLREG` validator or a parser of
  entire linked `BCRG` and `BCEX` records. The MVS cases cover **only
  count/size envelopes**, specifically identifiers 1003 and 1006.
- IDs 1001–1002, 1004–1005, 1007–1014 and 2001 were **not all
  demonstrated** by this MVS driver. Detailed descriptor parsing,
  untrusted addresses and finalizer execution require distinct tests.
- **RC=12 before START**, complete optional selection rollback and
  full ownership-aware diagnostics remain future integrated runtime
  behavior, **not** claims established by JOB 2203.
- The harness does not execute `BCPLMAIN`, import BLIB, write global
  slots, or install or replace any accepted `BOOT_OBJ` member.
- Actual linked extent trust is partly a source/build/link contract;
  relocation and numeric bounds alone do not prove pointer safety.

**Acceptance of this evidence:** the **Decision G isolated count/size
MVS boundary experiment passed**. The exact approved design values
remain in the contract; this result is **not** R.0 gate acceptance.
R.0 remains open, R.1 has not started.
