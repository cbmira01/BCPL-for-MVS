# Milestone QSAM — Q.5 STOP(8) finalizer accounting, JOB 8140

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** **Q.5 — Hardening & release**  
**Disposition:** **STOP(8) sixteen-handle native finalizer accounting PASSED** on owner-executed MVS 3.8J JOB 8140. This is a bounded Q.5 technical result, **not** closure of Q.5 or Milestone QSAM.  
**Source baseline:** GitHub `main` [`d692bcf6a220fb28aa72d80c7665687e3bb820ab`](https://github.com/cbmira01/BCPL-for-MVS/commit/d692bcf6a220fb28aa72d80c7665687e3bb820ab).  
**Execution date:** 30 October 2026 in operator-local time; JES/TK5 printed **31 OCT 26, 00.17.07–00.17.08**.

## Purpose and traceability

The [Q.1 owner closure](qsam-q1-closure-20261028.md) accepted normal FINISH sixteen-CLOSE accounting in JOB 6636, but explicitly deferred independent STOP(8) finalizer accounting. The Q.2/Q.4 numbered regression 167 subsequently demonstrated the sixteen-handle STOP application and requested GO RC=0008, without independent finalizer counters. Q.5 supplied the missing target-native evidence.

The owner approved a test-only three-checkpoint STOP diagnostic and its single JES submission. The source-selected BCPLQSAM System Extension, generic BCEX/BCRG v1 finalizer ABI, accepted production `BOOT_OBJ` objects and private sixteen-handle F1024 DD configuration were preserved. No production source, installed object PDS, installed BCXCAT member or permanent MVS dataset was modified for this test.

The first attempt to prepare a STOP diagnostic from the preserved Q.1 `q1-campaign-stop.jcl` was **rejected before JES**: its 779-card embedded Q.1 assembler differed from current `bcplqsam.asm` (1,083 cards). The owner supplied this mismatch evidence. Do not describe that first attempt as a native failure or a submission.

The [Q.5 current-source recovery generator](../bootstrap-toolchain/extensions/bcplqsam/prepare-q5-stop-from-regression.py) selected the previously completed, evidence-checked [regression 167 — qsam-sixteen-stop](../bootstrap-toolchain/regression/167-qsam-sixteen-stop/source.bcpl) deck. It required exact current source, established regression 167 JES/GO evidence and the canonical STOP BCPL fixture, then applied the [test-only finalizer instrumentation](../bootstrap-toolchain/extensions/bcplqsam/prepare-q5-stop-diagnostic.py). The preparation retained all 16 temporary F1024 DDs, source-mode selection, and GO `REGION=256K`; it created only ignored workarea JCL. Its synthetic offline-check and two rejection tests passed.

## Prepared and submitted job

| Property | Observed |
| --- | --- |
| Candidate source | `workarea/native-regression/167-qsam-sixteen-stop/native-uuqc1f4f/native.jcl` |
| Diagnostic JCL | `workarea/bcplqsam-q5/q5stdiag.jcl` |
| JCL card count | **4,617** |
| JCL SHA-256 | `d5a4daf025342d6ae45c1e6295973d2944ca0d42ff9682a86f5b82240a8e5d20` |
| JES job | **8140 / Q5STDIAG** |
| Submission | `tools/mvs/submit-jcl` RC=0; response `JOB 8140` |
| JES report | `dump-report-for-job 8140` RC=0 |
| JES summary | `job-summary 8140 --max-rc 8 --verbose` RC=0 |
| JES description | `Q2 NATIVE REG` (preserved source-regression JOB card description; not a claim that the Q.2 march was run) |

An attempt marker, JCL digest, recorded Git HEAD, submission output, JOB number and subsequent JES summary/report are retained locally under `workarea/bcplqsam-q5/q5stdiag-attempt/`. The generated JCL, job listing and console files are operator-local evidence, not Git-tracked source.

## Native MVS result

The owner provided the following complete ten-step `job-summary` result for **JOB 8140**, with `JOB RESULT: SUCCESS`, **HIGHEST RC=0008**, **zero assembler statements flagged**, and **highest assembler severity 0**:

| Step | Program | RC |
| --- | --- | --- |
| ASMWR | IFOX00 | 0000 |
| LKWR | IEWL | 0000 |
| ASMA | IFOX00 | 0000 |
| ASMN | IFOX00 | 0000 |
| ASMR | IFOX00 | 0000 |
| ASMQ | IFOX00 | 0000 |
| ASMG | IFOX00 | 0000 |
| LKED | IEWL | 0000 |
| WGO | PGM=*.DD | 0000 |
| **GO** | PGM=*.DD | **0008** |

The owner-supplied JES report excerpts contain the exact application marker **`BCPLQSAM Q1 16 STOP PASS`** once. GO RC=0008 alone would be ambiguous because the BCPL fixture uses STOP(8) on assertion failures too; the marker confirms the success path reached the intentional final STOP(8).

### Job-correlated generic finalizer snapshots

The following ordered records appear for **JOB 8140**, **Q5STDIAG**, in both `mvs-state/log/3033.log` and the dated 3033 console copy, with the same values in `mvs-state/log/hardcopy.log`. The snapshots were recorded at `00.17.08` MVS time, between JOB 8140 START and END:

| Checkpoint | Exact hexadecimal payload | Meaning |
| --- | --- | --- |
| `Q1F:E` | `00000001:00000010:00000010:00000010` | Reason 1 = STOP; 16 live slots, 16 DCBs, 16 stages |
| `Q1F:L` | `00000010:00000000:00000000:00000000:00000000` | 16 successful CLOSEs; live/DCB/stages/status all zero |
| `Q1F:X` | `00000010:00000000:00000000:00000000:00000000` | Same successful cleanup at finalizer return |

Console evidence shows `$HASP373 Q5STDIAG STARTED`, `IEF403I`, the three `Q1F` records in order, `IEF404I`, `$HASP395 Q5STDIAG ENDED` and eventual `$HASP250 Q5STDIAG IS PURGED`. The `hardcopy.log` additionally lists all ten step RCs for this JOB. Earlier Q1F records from JOBs 6635 and 6636 were present in the same log files; **they were excluded** from the JOB 8140 evidence.

The independently instrumented entry, loop and exit snapshots show the **tracked** handle/DCB/stage counts returned to zero and all sixteen CLOSE operations were counted as successful. This establishes the tested ordinary STOP(8) implicit-finalization path, not every exceptional CLOSE outcome or OS-level resource recovery after an unrecovered abend.

## Acceptance boundary and remaining Q.5 work

**Technical disposition: PASS.** The previously deferred independent sixteen-handle STOP(8) resource-accounting obligation is satisfied by target-native MVS observations on the exact source-controlled Q.5 baseline. The prior normal FINISH JOB 6636 evidence remains separate.

This record is grounded in the operator's JOB summary, report excerpts and three job-correlated console-log extracts supplied in the conversation. The full 10,641-line printer listing and complete raw console log files were **not** independently ingested into Git; no automated cross-log evidence checker PASS is claimed. The underlying source and both test-only preparation scripts are in GitHub `main`.

Q.5 remains open. Distinct obligations include failed/partial OPEN rollback and cleanup-error precedence, returned CLOSE ownership/quarantine and finalizer-failure handling, broader geometry/resource negatives, source-only versus installed-object packaging decision, reproducible clean-from-Git rebuild, examples/docs and a fresh focused/full native regression acceptance panel. Returned MVS errors must not be conflated with unrecovered abends. No further JES submission, permanent PDS modification, installed-object promotion, or Q.5 closure follows from JOB 8140 alone.
