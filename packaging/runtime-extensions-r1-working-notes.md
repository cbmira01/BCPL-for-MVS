# Milestone Runtime Extensions — R.1 implementation working record

**Owner disposition, 21 October 2026:** R.0 closed; R.1 Generic
registration foundation active. The owner approved a separate generic
assembler registrar and application-specific BCPLREG table, integrated
through BCPLMAIN. This record does not assert MVS execution success.

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

Five host-only source-contract checks passed during preparation.
No actual IFOX assembly, IEWL linkage, or GO execution is claimed.
The two temporary MVS tests, integrated 1001–1014 and 2001 evidence,
source-trusted address verification, reverse-order FINISH/STOP behavior,
and full native regression must still be executed and reviewed.

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

All three instructions are corrected in the next candidate. The new
host test guards against register-zero storage-base operands. **A
successful GO run remains required; no MVS success is asserted.**
