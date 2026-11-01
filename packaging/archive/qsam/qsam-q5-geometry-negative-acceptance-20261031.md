# Milestone QSAM — Q.5 geometry-negative native acceptance

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** **Q.5 — Hardening & release** (IN PROGRESS)  
**Status:** **Native geometry-negative campaign PASSED**, documented from owner-supplied MVS execution and strict acceptance-checker output. Owner approved this record's GitHub commit on 31 October 2026 (local date); JES reports 01 NOV 26.  
**Acceptance scope:** This is the bounded Q.5 geometry-negative test, **not** Q.5 or Milestone QSAM closure, permanent installation, or object promotion.  
**GitHub source revision:** `main` `888266e866d830f795f0d1f8fea65d1aa6c338cb`. Unmodified production `bootstrap-toolchain/extensions/bcplqsam/bcplqsam.asm` blob: `61daa6da9aa5d95ce7f9e9a0bcce0855806eb535`.

## Native compiler and JCL provenance

- **Q5GCOMP JOB 8151:** the resident interpreter-hosted **demoted Cambridge compiler**, `COMP` ICINT19 RC=0000 and `SVCODE` IEBGENER RC=0000; `EXECUTION CYCLES = 1202498, CODE = 0`. The recovered System/370 assembler has SHA-256 `2ee9e94e173be9e18e54326c8298a5d18588c77f95802e9a4e8e6b56ee392b51`.
- **Q5GEOM JOB 8152:** one owner-authorized submission of a temporary **4,166-card** JCL deck, SHA-256 `48583f63b5791d13b262237c09d508f05b97a32e7d86680389bddf04d4ba1046`. The deck linked test-only `Q5GOPEN` instrumentation derived from the unchanged production assembler.
- Previous outcomes remain part of the evidence chain: **JOB 8148** compiled the initial fixture; **JOB 8149** was rejected before execution by malformed Q01 JCL; **JOB 8150** reached GO RC=0012 with the original fixture. The fixture was corrected to set `request!1=0` before INFO and to emit numbered failure diagnostics, then recompiled in JOB 8151. The earlier failures are not acceptance runs.

## Owner-observed MVS results — Q5GEOM JOB 8152

The operator supplied the following JES summary, extracted application record, original job-bounded console and hardcopy lines, and acceptance-checker result.

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

**JES:** `JOB RESULT: SUCCESS`, highest RC=0000. **IFOX:** zero statements flagged and highest severity zero. The printer report contained exactly one standalone BCPL application PASS line:

```text
BCPLQSAM Q5 GEOMETRY NEGATIVE PASS
```

Both Hercules console and MVS hardcopy contained one matching JOB 8152 bounded finalizer WTO:

```text
Q5G:X:00000001:00000000:00000000:00000000:00000000
```

The first counter is the number of attempted QSAM OPEN macros: **one**, for the valid `Q00` F1024 input. The remaining fields establish zero live handles, zero owned DCBs, zero private stages, and zero finalizer status. The BCPL assertions require rejected `QBAD` (FB80/801), `QBIG` (F1025 over the System Extension's approved 1024-byte private stage ceiling), and `Q01` (incomplete GO JFCB geometry) to return `-6` and zero handles **without reaching OPEN**. They additionally require `Q00` INFO, one 1024-byte READ, explicit CLOSE, and normal `FINISH` before the PASS record.

The strict native evidence checker printed:

```text
PASS: Q5GEOM native geometry, single BCPL marker, bounded zero-resource Q5G:X
```

The owner reported submission RC=0, native summary RC=0, printer report RC=0, native checker RC=0, and overall WSL RC=0. No repeated submission or installation of permanent MVS datasets occurred.

## Evidence custody and boundaries

The original compiler and JES output remains available on the operator's WSL system, including `workarea/bcplqsam-q5/q5gcomp-attempt/`, `workarea/bcplqsam-q5/q5geom-attempt/`, `workarea/bcplqsam-q5/q5geom.jcl`, prior archived job evidence, `mvs-state/prt/prt00e.txt`, and job-bounded `mvs-state/log/3033.log` and `hardcopy.log` extracts. This document records the **owner-supplied transcript**, not an independently retrieved raw printer dump; authenticated JCL is not committed to GitHub.

The unrelated local Python `test_40_fixture_missing_failure_stage_is_rejected` had a test-oracle mistake: deleting `FAIL(41,R!0)` tripped the earlier negative-OPEN cardinality check, whereas the test expected the later diagnostic-order error. This commit instead removes `FAIL(51,R!4)` in the deliberately damaged **test-only input**, preserving OPEN guards and reaching the intended exception. The successful compiled BCPL fixture and production `BCPLQSAM` assembler remain unchanged. The full Python suite is to be rerun in WSL after the commit.

**Boundary:** Geometry preflight and clean teardown have passed the bounded native gate. Actual exceptional MVS CLOSE returns, remaining resource negatives, release packaging, optional promotion decisions, clean-from-Git reconstruction, focused/full native regression, and explicit owner closure of Q.5 remain separate obligations.

**Cross-references:** [Geometry-negative campaign design](https://github.com/cbmira01/BCPL-for-MVS/blob/62df114afe16115b1216367b2d827aba790bc9d6/packaging/qsam-q5-geometry-negative-campaign-20261031.md), [Milestone QSAM](../../milestone-qsam.md), [BCPLQSAM public interface](../../bcplqsam-public-interface.md), and `bootstrap-toolchain/extensions/bcplqsam/check-q5-geometry-evidence.py`.
