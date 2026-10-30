# Milestone QSAM — Q.5 failed-OPEN rollback experiment

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** **Q.5 — Hardening & release**  
**Design:** Owner authorized proceeding with the bounded failed-OPEN rollback experiment.  
**Status:** Test-only source and evidence checker prepared; **native MVS compiler/IFOX/IEWL/GO evidence NOT YET OBSERVED**. Do not treat the offline check as acceptance.  
**Authority:** GitHub `main`, native MVS 3.8J and actual JES/IFOX/IEWL/GO for target behavior.

## Design and limits

This experiment deliberately **injects one stage-allocation refusal after an actual QSAM OPEN succeeds**; it does **not** claim that MVS GETMAIN returned a real failure. The tested production control-flow is the existing `QCSTFAIL` → `QCCLEAN` → `QSMCLS1` branch, with a **real QSAM CLOSE macro** for the partially opened `Q01` DCB. It does not inject a failure into MVS CLOSE, retry an uncertain CLOSE, change error precedence, or modify the accepted assembler source. On actual returned CLOSE failure, the accepted quarantine/no-blind-free policy remains in force and requires a separate experiment.

Source-controlled components:

- [`test-q5-open-rollback.bcpl`](../bootstrap-toolchain/extensions/bcplqsam/test-q5-open-rollback.bcpl): open `Q00` successfully; first `Q01` OPEN should return `QS_ERR_RESOURCE=-11` without a public handle; verify `Q00` still works; reopen `Q01` successfully; verify both handles and explicit CLOSEs; print one exact PASS record; normal FINISH RC=0. Assertions use `STOP(12)` so a failure is not mistaken for success.
- [`prepare-q5-open-rollback.py`](../bootstrap-toolchain/extensions/bcplqsam/prepare-q5-open-rollback.py): builds temporary `Q5RBOPEN` from the already source-controlled 16-DD `Q16FIN` JCL preparation machinery and a separately compiled real BCPL application. Requires exact current `bcplqsam.asm`; makes a **test-only ASMQ overlay** with one-shot `Q01` injection, the approved three-checkpoint `QFPROBE` logic relabeled `Q5R`, and no changes to other JCL beyond the temporary job/load identity. Preserves 16 independent temporary F1024 DDs, `REGION=256K`, BCEX/BCRG v1 and read-only production `BOOT_OBJ`.
- [`check-q5-open-rollback-evidence.py`](../bootstrap-toolchain/extensions/bcplqsam/check-q5-open-rollback-evidence.py): verifies a real JOB's ten IFOX/IEWL/GO steps, zero assembler flagged statements/severity, exact BCPL PASS, and one ordered E/L/X sequence inside that JOB's console START/END interval. No automated submission or retry.
- [`test_check_q5_open_rollback.py`](../bootstrap-toolchain/extensions/bcplqsam/test_check_q5_open_rollback.py): synthetic positive and negative evidence-checker tests. Their PASS is not MVS evidence.

## Expected native trace

The injected probe emits these **hexadecimal fullword** payloads:

| Checkpoint | Exact expected payload | Interpretation |
| --- | --- | --- |
| `Q5R:E` | `00000001:00000002:00000002:00000001` | Injection reason 1, Q00+Q01 live, two DCBs, one stage (Q00 only) |
| `Q5R:L` | `00000001:00000001:00000001:00000001:00000000` | One actual rollback CLOSE success; only Q00 DCB/stage remains, CLOSE status zero |
| `Q5R:X` | `00000000:00000000:00000000:00000000:00000000` | After BCPL explicitly closes both handles, normal FINISH finds zero outstanding resources |

`Q5R:L` uses the **actual `QSMCLS1` return status** to set its close-success counter. The `Q5R:X` record is emitted from the real optional-package finalizer path. Require **ASMWR, LKWR, ASMA, ASMN, ASMR, ASMQ, ASMG, LKED, WGO, GO all RC=0000**, no abend, zero IFOX severity/flagged statements, exact `BCPLQSAM Q5 OPEN ROLLBACK PASS`, and exactly one job-correlated sequence matching the table. GO RC=0000 alone does not prove rollback.

## Operator gates (no local source editing)

1. Fast-forward GitHub `main`; check Python syntax, `prepare-q5-open-rollback.py --check` and `python3 .../test_check_q5_open_rollback.py -v`. The `--check` path uses a **synthetic** BCPL assembler sample and does not contact MVS. Halt on any nonzero return.
2. **Separate MVS compiler JES authorization:** compile exactly `test-q5-open-rollback.bcpl` using the resident demoted Cambridge compiler via `tools/bootstrap/compile-mvs` with `--job-name Q5RBCOMP --output workarea/bcplqsam-q5/rollback-generated.asm`. Save full compiler JOB, CODE extraction and RC. This is a *real MVS compiler job*, not an offline conversion.
3. **JCL preparation only:** run `python3 bootstrap-toolchain/extensions/bcplqsam/prepare-q5-open-rollback.py --prepare`. It requires that compiled file in the ignored Q.5 workarea, authenticates the job card via the local manifest, produces `workarea/bcplqsam-q5/q5rbopen.jcl` once, and prints card count/SHA-256. It never submits JES or installs a PDS. It refuses to overwrite an existing JCL file.
4. **Separate `Q5RBOPEN` JES authorization:** submit the prepared deck **once** through `tools/mvs/submit-jcl`, with a persistent one-attempt marker recorded before the socket-reader call. On uncertain result, inspect JES; do **not** retry blindly.
5. Capture `job-summary --max-rc 0`, `dump-report-for-job`, and one console log with a complete `JOB N Q5RBOPEN` start/end interval. Then run `check-q5-open-rollback-evidence.py --job N --summary ... --report ... --console ...` and preserve full evidence regardless of result.

The operator shell command policy forbids fail-fast options in pasted WSL blocks; use conditional return-code gates and leave the interactive shell usable on failures. Do not remove earlier attempt markers or replace historical Q.1/Q.4 evidence. The runbook does not authorize either native JES job or permanent object installation merely because its test-only code is committed.

## Acceptance and follow-on decisions

A target-native PASS establishes **safe ordinary rollback after a simulated stage allocation refusal**, one actual successful CLOSE on the rollback path, retention of an independent Q00 handle, successful slot reuse on fresh Q01 OPEN, and full tracked-resource cleanup. It does **not** establish a real GETMAIN allocation denial from BCPLQSAM, returned MVS CLOSE failure, uncertain ownership quarantine, unrecovered MVS abend recovery, or promotion to `EXT_OBJ`. The source's provisional primary-OPEN-error precedence if cleanup CLOSE also fails remains a separate owner decision.

Q.5 remains **IN PROGRESS** until the remaining exceptional scenarios, packaging decision, clean-from-Git verification, native focused/full regression and owner acceptance.
