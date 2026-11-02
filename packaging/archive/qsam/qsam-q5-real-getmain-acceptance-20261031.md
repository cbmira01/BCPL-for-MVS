# Milestone QSAM — Q.5 real GETMAIN resource-refusal native acceptance

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** **Q.5 — Hardening & release** (IN PROGRESS)  
**Owner disposition:** **ACCEPTED** — owner reviewed JOB 8154 and requested its acceptance commit on 31 October 2026 (Kentucky local date; the MVS JES listing dates the run `01 NOV 26`).  
**Scope:** The bounded, temporary **real MVS 1024-byte conditional GETMAIN refusal** inside `BCPLQSAM`, successful rollback, surviving-handle integrity, and cleanup. **This is not Q.5 or Milestone QSAM closure**, permanent object installation, or a universal exhaustion claim.  
**Source revision:** GitHub `main` `497555de05a850f1dca84a4ac0af312a43b38203`, using unchanged production `bcplqsam.asm` blob `61daa6da9aa5d95ce7f9e9a0bcce0855806eb535`.

## Design and provenance

The native BCPL application was previously compiled by the interpreter-hosted **demoted Cambridge compiler** in **Q5RFCOMP JOB 8144**. Its accepted 311-line generated assembler at `workarea/bcplqsam-q5/rollback-finish-generated.asm` has SHA-256 `f68e03ea2cdc8bc9a25a8f4df49c8c8cc1fd4b54056eed1a858be952b207d4ed`. The generator uses the existing `prepare-q5-rollback-finish.py` verification of that compiler job, its source digest, archived JES summary and CODE image.

The disposable `Q5RGM` `ASMQ` overlay runs a bounded sequence of actual 1024-byte conditional `GETMAIN RC` requests before the first Q01 private-stage allocation in a 256K `GO` region. It **retains** these blocks while executing the original 1024-byte BCPLQSAM stage `GETMAIN RC`, then frees all pressure allocations and follows production `QCSTFAIL` / `QCCLEAN` / `QSMCLS1` rollback. No failure return code is synthesized. Its WTO is conditional on **both genuine GETMAIN calls returning R15=4**, nonzero pressure-allocation count and equality of allocation/free counters. The compiled BCPL fixture demands `QS_ERR_RESOURCE=-11` with no published Q01 handle, working Q00 `INFO`, a second successful Q01 OPEN/INFO, both successful explicit CLOSE calls, and normal `FINISH`.

## Earlier attempts and corrections

- **Pre-JES attempt:** preparer accidentally read `rollback-generated.asm` from JOB 8141 instead of JOB 8144's `rollback-finish-generated.asm`. Digest mismatch stopped preparation without any JES job; evidence archived as `q5rgm-attempt-preflight-job8141-image/`. The fix reused the existing JOB 8144 provenance verifier.
- **Q5RGM JOB 8153:** submitted 4,035-card JCL SHA-256 `36a81c811090ee09089b4f597e3a92d73198a3cc392c8eb63d641c4f27906819`. `ASMQ` IFOX RC=0008 reported four `IFO209` addressability errors, highest severity 8. `ASMG`, `LKED` and `GO` did **not execute**; this is **failed evidence, not resource-refusal acceptance**. The test-only helpers had been added after the `QSMCORE` `LTORG` and were moved before that literal pool. The original JCL and evidence remain archived as `q5rgm-job8153-asm-rc8.jcl` and `q5rgm-attempt-job8153-asm-rc8/`.

## Accepted native execution — Q5RGM JOB 8154

The owner performed one replacement submission of the corrected **4,035-card** disposable JCL deck, SHA-256 `7e9d7846a7663f140be1d898524b3077fc434ddd2b6203e56f1091c94d93bbf6`.

| Step | Program | Native result |
| --- | --- | --- |
| ASMWR | IFOX00 | RC=0000 |
| LKWR | IEWL | RC=0000 |
| ASMA | IFOX00 | RC=0000 |
| ASMN | IFOX00 | RC=0000 |
| ASMR | IFOX00 | RC=0000 |
| ASMQ | IFOX00 | RC=0000 |
| ASMG | IFOX00 | RC=0000 |
| LKED | IEWL | RC=0000 |
| WGO | temporary load module | RC=0000 |
| GO | temporary load module | **RC=0000** |

**JES result:** SUCCESS; highest RC=0000. **IFOX:** 0 statements flagged, highest severity 0. The printer report contained the standalone native BCPL record:

```text
BCPLQSAM Q5 OPEN ROLLBACK PASS
```

The Hercules console and MVS hardcopy each recorded the identical `$HASP373`–`$HASP395` JOB 8154-bounded runtime WTO:

```text
Q5RGM:REAL:GM1024-RC4:ALL-FREED
```

The operator reported `JES submission RC=0`, `Native summary RC=0`, `Native report RC=0`, `native acceptance RC=0` and `Overall RC=0`. No automatic resubmission or permanent dataset change was reported.

## Interpretation, custody and remaining work

**Established:** a real MVS returned-control failure from BCPLQSAM's normal 1024-byte private-stage `GETMAIN`, correct `QS_ERR_RESOURCE=-11` mapping, rollback through real QSAM CLOSE, survival of the independent Q00 handle, successful Q01 reopen, and normal cleanup. This extends the earlier **JOB 8145** injected-refusal result and is different from the Q.0 **JOB 2177** oversized-request GETMAIN refusal.

**Not established:** every storage-shortage circumstance, recovery after an unrecovered abend, a genuine exceptional MVS CLOSE return, or a universal MVS region budget. This is a temporary memory-pressure experiment, not a claim about uninstrumented application performance.

Original input and results remain in the operator's `workarea/bcplqsam-q5/q5rgm-attempt/`, the two archived failed attempts, and MVS printer/console/hardcopy logs. GitHub records the owner-supplied evidence; this acceptance file is not an independently captured raw MVS dump.

**Q.5 remains IN PROGRESS.** Remaining acceptance includes release packaging, clean-from-Git rebuilding, demonstrated optional candidate-object link-edit, focused/full native regression, a documented object-promotion decision and explicit owner closure. Real exceptional CLOSE and unrecovered-abend cases remain limitations, not presumed successes.

**References:** [Milestone QSAM](../../milestones/qsam/milestone-qsam.md), [JOB 8145 acceptance](qsam-q5-failed-open-rollback-acceptance-20261031.md), [JOB 8152 geometry acceptance](qsam-q5-geometry-negative-acceptance-20261031.md), [repository/MVS authority](../../operations/git-mvs-authority.md), `bootstrap-toolchain/extensions/bcplqsam/prepare-q5-real-getmain.py` and `tools/mvs/run-q5-real-getmain`.
