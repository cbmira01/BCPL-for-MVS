# Milestone QSAM — Q.5 geometry-negative native campaign design

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** **Q.5 — Hardening & release** (IN PROGRESS)  
**Status:** Test-only campaign committed on 31 October 2026 by owner approval. Native compiler and JES execution remain separately gated.  
**Reference baseline:** GitHub `main` `7f3b3ef1c7285761271c76bed770579e1f644dad` and its unchanged `bcplqsam.asm` blob `61daa6da9aa5d95ce7f9e9a0bcce0855806eb535`.

## Bounded native purpose

Prove that **BCPLQSAM**, invoked from a native BCPL program, rejects unsupported/untrusted effective geometry **before attempting QSAM OPEN**, does not issue public handles for failed OPENs, preserves the independently opened valid `Q00` input handle, and leaves zero live DCBs, private stages, and handles after explicit CLOSE and normal FINISH.

This extends the standalone MVS `QS0GEOM` JOB 2172 RDJFCB result and preserves the historical `QS0BADOP` JOB 2171 S013-20 evidence without deliberately invoking an unsafe OPEN. The already accepted JOB 8145 injected post-OPEN stage refusal and JOB 8147 injected returned-CLOSE error are separate tests; the existing `QS0NOMEM` JOB 2177 establishes a genuine returned conditional `GETMAIN` R15=4 independently.

## Test-only inputs and expected BCPL statuses

| DD | Allocation and preflight | Expected `QSAMSVC(OPEN)` | MVS OPEN permitted |
| --- | --- | --- | --- |
| `Q00` | Existing `&&Q1H00` from sixteen-DD writer; GO has explicit F1024/1024 DCB | success, handle 1 | **Yes, exactly once** |
| `QBAD` | Disposable GO `&&Q5BAD`, explicit FB80/801 (invalid blocking ratio) | `QS_ERR_OPEN=-6`, `result!1=0` | **No** |
| `QBIG` | Disposable GO `&&Q5BIG`, explicit F1025/1025 (above BCPLQSAM's approved 1024-byte stage maximum) | `QS_ERR_OPEN=-6`, `result!1=0` | **No** |
| `Q01` | Existing `&&Q1H01` written as F1024, with GO reader DCB intentionally **omitted** (known incomplete JFCB case) | `QS_ERR_OPEN=-6`, `result!1=0` | **No** |

A `QBIG` DD uses a valid physical record size but exceeds **the extension's policy**; the test should not claim an MVS-wide 1024-byte maximum. The intentionally inconsistent FB80/801 DD is allocated but must never be opened. An unexpected JCL/allocation error or MVS abend is a failed/diagnostic result, not success.

The other fourteen Q16FIN writer/reader temporary DDs remain allocated but unopened by the BCPL test. Their original writer and GO DD cards are preserved. The GO uses `REGION=256K` and an unchanged read-only accepted `BOOT_OBJ`; no permanent dataset writes or optional object promotion occur.

## Test-only instrumentation and acceptance signals

The separate `ASMQ` overlay is derived from *exactly* the current production `bcplqsam.asm` and adds a counter `Q5GOPEN` immediately before each `OPEN ((2))` macro. Both input and output paths are counted; neither changes the preflight logic, QSAM status, or handle state. It reuses the proven `QFPROBE` WTO printer solely for finalizer phase X with `Q5GOPEN` replacing the first count and an explicit `=A(Q5GOPEN)` reason pointer. The overlay lives exclusively in the temporary JCL.

The BCPL program checks all three `-6` results and zero handles, then performs `INFO`, a native 1024-byte `READ`, and explicit `CLOSE` on `Q00`, prints one standalone record:

```
BCPLQSAM Q5 GEOMETRY NEGATIVE PASS
```

It calls normal explicit `FINISH`. Unexpected assertion results call `STOP(12)`, never `FINISH`. The expected **single** job-bounded runtime WTO in both Hercules console and MVS hardcopy is:

```
Q5G:X:00000001:00000000:00000000:00000000:00000000
```

The fields represent one counted QSAM OPEN attempt, zero remaining live handles, zero DCB/control areas, zero private stages, and finalizer status zero. Earlier Q5G `E` and `L` phase messages exist as uninvoked WTO templates only and must **not** appear as runtime markers.

Require every `ASMWR/LKWR/ASMA/ASMN/ASMR/ASMQ/ASMG/LKED/WGO/GO` step RC=0000, IFOX severity/flagged statements zero, one exact standalone BCPL PASS record, no BCPLREG 2001 runtime finalizer error, and exactly one matching Q5G:X inside the same JOB's START/END boundaries in both logs.

## Source, generation and custody

- `bootstrap-toolchain/extensions/bcplqsam/test-q5-geometry-negative.bcpl`: 46-line real BCPL fixture, explicit FINISH.
- `bootstrap-toolchain/extensions/bcplqsam/prepare-q5-geometry-negative.py`: source-selected temporary ASMQ and JCL transformations, `--check` synthetic path, and one-shot `--prepare` mode with controlled compiler provenance. It never calls JES. Requires existing `prepare-q1-campaign.py`, `prepare-q1-finalizer-diagnostic.py` and the tested raw-CG370 adapter.
- `bootstrap-toolchain/extensions/bcplqsam/test_prepare_q5_geometry_negative.py`: guard/identity/tampering tests.
- `bootstrap-toolchain/extensions/bcplqsam/check-q5-geometry-evidence.py` and `test_check_q5_geometry_evidence.py`: strict native evidence checker with negative synthetic fixtures.

A separate **owner-authorized** resident demoted Cambridge compilation job, proposed `Q5GCOMP`, must compile the **exact tracked BCPL source** into `workarea/bcplqsam-q5/geometry-negative-generated.asm`. All source digests, compiled output digest, native compiler report, success RC, and job identity must be retained in a new `q5gcomp-attempt` directory. Only then may the prep script emit `workarea/bcplqsam-q5/q5geom.jcl` with `O_EXCL` (no overwrite). The proposed native `Q5GEOM` JES submission is a distinct, separately approved gate; do not resubmit blindly on uncertain outcome.

## Verification limits and post-test decisions

Local Python syntax checks and **42 isolated unit tests passed** using a synthetic Q16FIN template and fabricated printer/console/hardcopy reports. Exact production assembler source anchors were independently checked against GitHub and the transformed source was validated for 71-column IFOX cards. These checks do **not** establish a successful real Q16FIN full JCL generation in this environment, MVS JCL allocation of the proposed F1025 DD, IFOX acceptance or the native BCPL result.

Unsupported-RECFM (`QS_ERR_RECFM=-9`) is deliberately **deferred**: an unambiguous non-opening test needs confirmed JFCB semantics for an actually allocatable unsupported-format DD, and should not be bundled with invalid-geometry cases on a guess. Actual returned MVS OPEN errors and unrecovered abend recovery remain outside this bounded proof. Q.5 remains IN PROGRESS and release packaging and clean-from-Git/native full-panel verification still require separate acceptance.