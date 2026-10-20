# Milestone Runtime Extensions — R.0 first linked-descriptor probe evidence

**Date:** 20 October 2026. **March:** R.0 — Evidence and contract
(**in progress**). Source: actual MVS 3.8J/TK5 JES step summaries and
QOUT markers provided by the owner, JOBs **2187–2192**.
No accepted runtime/compiler object or persistent object PDS was changed.

The [tracked first-probe sources](../bootstrap-toolchain/probes/r0-registration-probes/README.md)
assemble four separate IFOX objects, link one temporary load module
with IEWL, and execute a test-only validator. It inspects relocated
start/end symbols and candidate package/table data. Each negative case
has an **expected internal rejection code**; on exactly that
rejection, GO writes the appropriate QOUT line and returns RC=0000.
A GO RC=0000 by itself is not evidence of a successful negative test.

| JOB | Program/profile | Internal result required | Actual QOUT record | Result |
| --- | --- | ---: | --- | --- |
| **2187** | `R0VALID` / `valid` | 0 | `R0 VALID LINK BOUNDS PASS` | PASS |
| **2188** | `R0LENG` / `badlen` | 4 | `R0 BADLEN REJECTED PASS` | PASS |
| **2189** | `R0VERS` / `badversion` | 8 | `R0 BADVERSION REJECTED PASS` | PASS |
| **2190** | `R0DUP` / `duplicate` | 12 | `R0 DUPLICATE EXPORT REJECTED PASS` | PASS |
| **2191** | `R0CORE` / `corecollision` | 16 | `R0 CORE G14 COLLISION REJECTED PASS` | PASS |
| **2192** | `R0REQ` / `missingreq` | 24 | `R0 MISSING REQUIREMENT REJECTED PASS` | PASS |

All **six** JOBs completed `ASMD`, `ASMR`, `ASMP`, `ASMF`,
`LKED`, `GO` at **RC=0000**. The owner reported
**zero flagged assembler statements** and verified the **actual
QOUT** marker for each JOB, rather than relying on assembler
`PASSREC` source listings.

The owner also executed Python syntax checks for the generator and
unit suite, the four Python unit tests (**4 PASS**), and all six
credential-free JCL `--check` profiles before JOB 2187.
The initial missing-`)` test file error was fixed in commit
`a544d9b`; the later syntax and unit re-run passed.

**Limits:** These are bounded *single-package and selected negative*
fixtures, not a general production `BCPLREG` parser or a test of
the true Core Runtime's global-owner ledger. The G!14 collision is
recognized by a test-local validator. No app/BLIB/global import
modification, automatic registration, generic finalization or
actual native BCPL FINISH/STOP behavior was tested.

The owner retained full JES reports in ignored
`workarea/runtime-extensions-r0/job-2187.txt` through
`job-2192.txt`. This Git evidence record was prepared from the
owner-pasted summaries, not from an independent raw JES report audit.

**Next:** Owner requested maximum useful batching for the remaining
R.0 investigations. The [single-job dependency and simulated
finalizer package](../bootstrap-toolchain/probes/r0-batch-probes/README.md)
prepares fourteen additional linked-descriptor cases and six
finalizer-policy cases. It is **not yet MVS-executed**.
R.0 is still open and R.1 has not started.
