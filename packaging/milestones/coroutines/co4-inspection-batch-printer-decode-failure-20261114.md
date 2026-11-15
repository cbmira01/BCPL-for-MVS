# CO.4 — Inspection batch first-run report-decoding failure

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.4 — Robustness and Edge-Case Verification (**IN PROGRESS**)
**Tested GitHub `main`:** `bdd1c4716cc0012d0ae314576d35bd489f4765bb`
**Observed:** 14 November 2026, Louisville local time (15 November UTC)
**Classification:** OWNER-REPORTED **FAIL**, source-diagnosed I/O decoding failure; native GO outcome **not independently verified**.

## Original operator evidence (preserved as FAIL)

```text
CO.3 first lifecycle FAIL: 'utf-8' codec can't decode byte 0xd7 in position 258981: invalid continuation byte
CO.4 LIMITS FAIL
CO.4 inspection batch FAIL (0/3)
CO.4 inspection evidence: /home/calvin/Source/Repos/BCPL-for-MVS/workarea/co4-inspection-batch/20261115T025919Z-ypmhu6wh
CO.4 inspection batch RC=1
```

The original local evidence directory must remain intact. LIMITS did not pass its native oracle; the fail-fast coordinator did not attempt ACCOUNT or DENY. A native job may have been submitted before report decoding failed, but the console report does not establish a native JOB number, step RC, or GO behavioral result. Do not relabel this attempt PASS.

## Source-grounded diagnosis

The inherited CO.3 executor calls `driver.co2.shell` for `tools/mvs/dump-report-for-job` and then reads its stdout. That wrapper uses `subprocess.run(text=True)` without an explicit encoding, which defaults to the host locale (UTF-8 under the operator's reported failure). `dump-report-for-job` emits the selected printer stream as raw bytes via an AWK process; it need not be valid UTF-8. The invalid `0xd7` byte and high output offset are consistent with failure in that subprocess capture. The project's `tools/datasets/dspal-core.py` already explicitly decodes the same report utility with `encoding="latin-1"`. This is an I/O boundary defect, not evidence that the BCPL fixture or IFOX observer failed.

The exact failed subprocess stream and target JOB numbers were not supplied, so identification of the failing report capture is **source-supported inference**, not direct inspection of the owner-local printer bytes.

## Narrow repair

The candidate-local `configure_report_decoder(driver)` in `tools/coroutines/run-co4-inspection-batch.py` overrides only the inherited shell call whose executable is precisely `driver.REPORT`. That call runs with explicit `encoding='latin-1'` and otherwise retains subprocess arguments, timeout, working directory, stdout/stderr capture, and return-code behavior. All other commands—including `git`, independent Cambridge compilation, JCL submission and JES summaries—delegate unchanged to the accepted CO.2 shell wrapper. Neither the CO.2/CO.3 runners, `BCPLCO`, installed `BOOT_OBJ`, nor any BCPL fixture changes.

Latin-1 maps each possible byte to one Unicode code point, so binary/high-bit bytes cannot cause this decoding exception. The strict case-specific `CO4LIM`, `CO4MEM`, and `CO4DENY` text oracles and the full set of JES RC requirements remain unchanged. No MVS object is modified.

## Host verification (assistant workspace)

- Local synthetic subprocess emits ASCII oracle text plus literal byte `0xd7`; selective report decoding succeeds and the parser still extracts the exact record.
- Separate tests prove non-report commands delegate to the accepted wrapper and the raw-report subprocess uses the precise Latin-1 arguments.
- Inspection batch: **20/20** host tests PASS (17 previous + 3 decoding checks).
- Previous CO.4 bounded stress, safe-negative, and three-case batch host suites: **10/10**, **10/10**, and **15/15** PASS respectively (**55/55** combined).
- Inspection runner `--check`: PASS; Python compile/syntax: PASS; staged Git whitespace check: PASS.

These are host-only checks. The complete native three-case batch remains **MVS-PENDING** after the repair. The next operator command is a guarded fast-forward and a **single** `tools/coroutines/run-co4-inspection-batch.py --run`, preserving separate case/JES receipts and stopping on the first failure.

**CO.4 remains IN PROGRESS; CO.5 remains NOT STARTED.** No release, permanent globals or target installation are authorized by this repair.
