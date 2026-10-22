# Milestone Runtime Extensions — R.2 four-link matrix candidate

**March:** R.2 — Selective interoperability (ACTIVE)  
**Status:** Positive 0/A/B/A+B source tested and verified in **actual MVS JOB 3080**; the consolidated R.2 negative/dependency campaign remains unverified. **No R.2 closure.**

## Second independent optional extension: B

- **A:** `BCPLDEMO`, permanently allocated `DEMOSVC:203`,
  separately compiled BCPL caller and assembled `DMODISP`, proven in
  actual MVS [JOB 3075](runtime-extensions-r2-bcpldemo-job-3075-evidence-20261022.md).
- **B:** `R2TESTB`, **test-only** assembler package with BCPL declaration
  `R2BSVC:299`, descriptor `R2BBEG`/`R2BEND` and entry `R2BDISP`.
  G!299 is borrowed solely as a previously exercised R.0 fixture; it is
  **not a new permanent Global Number Registry allocation**.
  `BCPLDEMO` retains exclusive ownership of G!203.

B follows the approved R.0 `BCEX` version-1 layout: 48-byte header
plus one eight-byte export pair, no dependencies, no finalizer, and
API version **3.2**. Its side-effect-free QUERY copies a complete
eight-word descriptor (format 1, API 3.2, size 8, opcode bitmap 5,
flags 0, appended fixture values 77 and 99), or returns 8 for size
inquiry; common error returns are -1 / -3. It returns 201 for opcode 1,
203 for opcode 3, and -2 for unsupported nonzero opcodes. The two
appended words are **not** an extension of the shared public QUERY
format. The distinct versions and opcode bitmap make A/B mixups visible.

## Four selections, one unchanged registration core

| Selection | Compiled BCPL caller | BCRG required IDs | Optional linked BCEX/dispatcher |
| --- | --- | --- | --- |
| 0 | `zero.bcpl` | none | none |
| A | `demo.bcpl` | `BCPLDEMO` | `DMODESC` / `DMODISP` |
| B | `onlyb.bcpl` | `R2TESTB` | `R2BDSC` / `R2BDISP` |
| A+B | `both.bcpl` | both, in that order | both |

Each registry has the exact owner-approved `BCRG` header (28 bytes),
0/1/2 linker-relocated descriptor spans, and matching required
eight-byte IDs. For nonempty selections, the existing R.1 source
provenance checker validates relocated boundary and entry references.
The combined client checks both QUERY descriptors, buffer sentinels,
opcode maps, calls and unsupported-opcode return paths.

The [matrix generator](../bootstrap-toolchain/probes/r2-interoperability/make-matrix.py)
assembles four applications, one R.1-adapted `BCPLMAIN`, one generic
registrar, four `BCPLREG` tables and the two packages. It then
**reuses exactly the same temporary BCPLMAIN and registrar object
datasets** in four distinct IEWL links and GO runs. The core is not
reassembled, rebuilt from a variant, or changed per selection.
Every selected object and load module is a `&&` temporary MVS dataset;
accepted `BOOT_OBJ` is linked read-only, and `BOOT_DEVOBJ` is not used.

## Verification boundary

The source and generator have preliminary offline structural checks,
including four registry shapes, one core assembler step, exact JCL
terminator count, and four different IEWL inclusion lists. Actual
IFOX compilation, IEWL linkage maps, BCPL execution, and JES condition
codes remain **unobserved** for this candidate. Follow the [probe
README](../bootstrap-toolchain/probes/r2-interoperability/README.md)
to run the host suite, compile four callers, submit the MVS job, and
review exact GO markers and object identities.

This is a **positive-selection candidate only**. Later R.2 gates must
exercise rejected collisions, malformed package descriptors, unsatisfied
requirements/dependencies and absent modules, with actual MVS diagnostics
and MAP evidence. R.3 remains not started. No permanent slot assignment,
object promotion, or change to the approved BCEX/BCRG/QUERY ABI follows
from this candidate.
