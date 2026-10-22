# Milestone Runtime Extensions — R.1 implementation working record

**Owner disposition, 21 October 2026:** R.0 closed; R.1 Generic
registration foundation active. The owner approved a separate generic
assembler registrar and application-specific BCPLREG table, integrated
through BCPLMAIN. Positive MVS integration JOBs 2226 and 2228 passed, but the complete
R.1 exit gate remains open.

## Candidate structure

- `bootstrap-toolchain/asm/bcplrgs.asm`: Core Runtime registrar
  `RGINIT` and generic finalizer driver `RGFINI`.
- `bootstrap-toolchain/asm/bcplreg-empty.asm`: 28-byte empty BCRG
  data object required for no-extension applications.
- `bootstrap-toolchain/probes/r1-registration/`: 44-byte selected
  BCRG, 56-byte BCEX, one QUERY-v1 test dispatcher and two BCPL
  application callers. G!298 is fixture-local, not an allocation.
- `tools/checks/r1_prepare_candidate.py`: guarded generation of a
  temporary BCPLMAIN source; canonical source is not overwritten.
- `bootstrap-toolchain/probes/r1-registration/make-jobs.py`: IFOX,
  IEWL and GO jobs using temporary objects and read-only BOOT_OBJ.

## ABI boundary

BCRG length = 28 + 8N + 8M; BCEX = 48 + 8K + 16D.
Entries use IEWL-relocated MVS byte addresses. Selection is dependency
first; no optional global may be published until validation completes.
Normal finalizers run in reverse order before IOFIN and MEMDRAIN.
The registered dispatcher follows the shared QUERY v1 contract.

The current candidate checks effective initialized global slots, but
**does not yet implement a fully attributed prior-writer ownership
ledger** from actual application, BLIB and Core Runtime exports.
Therefore, the owner-approved Decision E contract and the full
negative-path exit gate are *not yet satisfied*. Runtime pointer
alignment does not establish trusted callable code provenance:
source inspection and IEWL MAP/XREF are still required under Decision A.

G!150 FORMTREE/DEBUGINT remains an unresolved, separately governed
compatibility problem. No historical FORMTREE assignment is altered.

## Evidence and acceptance

Seven host source-contract checks and two additional negative-harness
tests passed at preparation. The positive MVS IFOX/IEWL/GO runs
**JOBs 2226 and 2228 passed**. The first integrated negative, 1001,
ran in JOBs 2229 and 2230 and emitted the correct WTO but both GO
steps ended S322, not RC=0012. No negative case is accepted yet.
The [no-output isolation probe](../bootstrap-toolchain/probes/r1-registration/README.md)
is ready for MVS execution. Remaining diagnostic coverage,
source-trusted address verification, reverse-order FINISH/STOP behavior,
and full native regression still require MVS execution and review.

No changes or promotion to accepted `BOOT_OBJ` are authorized by this
candidate. Keep R.2 Selective interoperability and R.3 Packaging and
acceptance unchanged.

## MVS test evidence and register-zero defect

- **JOB 2223:** demoted Cambridge compiler generated the empty-registry
  BCPL test application.
- **JOB 2224:** R1EMPTY: ASMA/ASMN/ASMG RC=0000, ASMR RC=0008
  (IFO196 from local REGCOUNT/REGFINTB re-declared EXTRN).
- **JOB 2225:** R1EMPTY: all four IFOX assemblies and IEWL RC=0000;
  GO ended **S0C4**. PSW X'000A6646', INTC 0004, identifies
  `ST 13,4(0)` in the RGINIT prologue. On S/370, B=0 specifies
  no base register; the attempted store was to absolute address 4.
  The same save-area error existed in RGFINI; optional-export
  validation also used `L 2,0(0)` with R0 as a putative base.

All three instructions were corrected before successful GO executions
in JOBs 2226 and 2228. The host test guards against R0 storage bases.

## Verified R.1 positive runs and integrated harness

- [JOB 2226 and JOB 2228 positive evidence](runtime-extensions-r1-positive-jobs-2226-2228-evidence-20261022.md).
- [R.1 integrated negative-test plan and harness](../bootstrap-toolchain/probes/r1-registration/NEGATIVE-TESTS.md): 1001–1014 and 2001 each require MVS evidence.
- No accepted BOOT_OBJ promotion; R.1 remains ACTIVE.

## Registration-rejection cleanup issue

JOBs 2229 and 2230 both ended S322 after `BCPLREG 1001` (two-
second and thirty-second GO limits respectively), with a saved PSW
consistent with incomplete `BCPLIO.IOFIN` output CLOSE. Source analysis
alone does not establish root cause. See the
[failed rejection evidence](runtime-extensions-r1-rejection-jobs-2229-2230-evidence-20261022.md).
**JOB 2232 R1NOOUT passed**: four IFOX steps, IEWL and GO all
RC=0000, with no application output. This excludes ordinary no-output
FINISH as the failure mechanism. See the [JOB 2232 evidence](runtime-extensions-r1-no-output-job-2232-evidence-20261022.md).

The R.1 R1BAD rejection adapter was then found not to preserve R10
around IOFIN. IOFIN uses R10 as a private base; the ordinary FINEXIT
path already has LR 9,10 / LR 10,9 bracketing. R1BAD subsequently
branches to RELMEM using R10 as its base, so the missing restore is
an actual register-linkage defect. The temporary candidate adapter
and test-only R1LEAK cleanup now preserve R10, with host checks
passing. **MVS retest of diagnostic 1001 remains outstanding.**
Do not reorder IOINIT and RGINIT or alter accepted runtime objects
based solely on the prior S322 dumps.
