# Milestone QSAM — Q.5 clean-room production regression evidence (1 November 2026)

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** **Q.5 — Hardening & release**  
**Source:** Owner-supplied WSL console excerpts in the 1 November 2026 project conversation.  
**Scope:** Final native production regression and one focused punch-output rerun; **not** a newly observed uninterrupted green full panel or a separate installed-BCPLQSAM test.  
**Owner disposition:** Recorded with the [Q.5 owner closure](../../milestones/qsam/qsam-q5-closure-20261101.md).

## Full numbered production panel: cases 00–176

The owner ran the complete production panel following a Git-backed reconstruction workflow, using the installed R.5/T.1 regression profile introduced in GitHub `main` commit `e5076dd755d632dc03fef9606481ce1791a6e13b`. The supplied excerpt is the **end** of the run; it does not preserve the initial shell invocation, all earlier payload job numbers or an independent audit of each earlier case log. The exact checkout HEAD at test execution was not printed in the excerpt.

| Panel metric | Owner-reported result |
| --- | ---: |
| Numbered range | **00–176** (177 entries) |
| PASS | **175** |
| FAIL | **1** — case 175 |
| SKIP | **1** — expected source-instrumentation case 083 |
| TOTAL | **177** |

The excerpt explicitly shows cases **173** and **174** PASS, case **175** FAIL, and case **176** PASS.

### Case 175 initial run — compiled/executed; external punch output not delivered

**Case:** `175-qsam-fb80-sysout-punch`  
**Compiler:** `RG175C`, resident interpreter-hosted **demoted Cambridge compiler**, RC=0; compiler JOB **9200** reported.  
**Native payload:** **JOB 9201 / Q4PUNCH**. JES listing dates execution **01 NOV 26, 18.58.18–18.58.19** (MVS clock).  
**Evidence attempt:** `workarea/native-regression/175-qsam-fb80-sysout-punch/native-iy5ij9pb/`

| Native step | Program | RC |
| --- | --- | --- |
| ASMA | IFOX00 | 0000 |
| ASMV | IFOX00 | 0000 |
| ASMN | IFOX00 | 0000 |
| ASMR | IFOX00 | 0000 |
| ASMQ | IFOX00 | 0000 |
| ASMG | IFOX00 | 0000 |
| LKVR | IEWL | 0000 |
| LKED | IEWL | 0000 |
| WGO | temporary load module | 0000 |
| VGO | temporary load module | 0000 |

JES reported `JOB RESULT: SUCCESS`, highest RC 0000. IFOX reported **zero** flagged statements and **zero** highest severity; native summary and report extraction each returned RC=0.

The runner then reported:

```text
Hercules punch capture: 0 new bytes; NOT VERIFIED
QSAM evidence NOT VERIFIED: class-B punch mismatch: got 0 bytes, expected 172
FAIL  175  175-qsam-fb80-sysout-punch (rc=1)
```

Thus the **original case 175 result is FAIL**, despite successful compile/assembly/link/execution. The expected **172-byte** JES2/Hercules class-B card-image capture was not visible to the verifier. This is consistent with the previously documented paused `PUNCH1` writer, but the excerpt does **not** independently show the writer's device state.

## Focused case 175 rerun with explicit punch-writer opt-in

The owner then executed exactly:

```sh
tools/bootstrap/run-installed-r5-t1-regression --resume-punch 175
echo "Regression RC=$?"
```

The supplied console returned:

```text
NATIVE PRODUCTION REGRESSION: BOOT_OBJ
NATIVE REGRESSION  175..175  (1 tests)
RUN   175  175-qsam-fb80-sysout-punch
PASS  175  175-qsam-fb80-sysout-punch
NATIVE REGRESSION COMPLETE
PASS  1
FAIL  0
SKIP  0
TOTAL 1
Regression RC=0
```

This explicitly opts in to the harness's conditional `Q4_PUNCH_RESUME=1` path, which **may issue JES2 `$S PUN1`** if the capture has not advanced. The rerun's PASS establishes that the case-175 runner accepted the native result and its strict Hercules capture check; the posted excerpt does **not** separately show the rerun's JES job number, console-command acknowledgment, 172 raw bytes or new job listing. Do **not** claim `$S PUN1` was actually issued without its separate log.

## Consolidated interpretation — distinct runs, not an altered first result

| Evidence | PASS | FAIL | SKIP | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Original full 00–176 | 175 | 1 | 1 | One unresolved punch-output capture at that time |
| Focused rerun of 175 | 1 | 0 | 0 | Separate case-175 native PASS, wrapper RC=0 |
| Combined **unique-case** coverage | **176** | **0 unresolved** | **1 expected** | Every executable numbered case passed in one of the two runs |

The accepted combined coverage is **not** a claim that the original full-panel run returned 176 PASS / 0 FAIL / 1 SKIP. That original panel **failed** case 175. An earlier separately reported full 176/0/1 production panel on prior revision `72a5da31` is documented in the [Q.5 packaging campaign](qsam-q5-release-packaging-campaign-20261031.md), and must not be conflated with these two runs.

The wrapper configures **installed BCPLDEMO and BCPLTIME** in cases 146–162. The BCPLQSAM numbered cases **163–176 still link temporary, source-selected BCPLQSAM**. Consequently this evidence does **not** establish that a permanent `EXT_OBJ(BCPLQSAM)` binary was installed, read back, or selected by IEWL; those are separate [Q5QINST/Q5QVFY](qsam-q5-installed-reconstruction-20261101.md) checks.

## Evidence custody and limits

The operator's checkout contains case logs under `workarea/native-regression/logs/` and native attempts under `workarea/native-regression/`. In particular, the initial case-175 attempt path and native JOB **9201** are recorded above. These workarea artifacts and JES/device logs are **not** Git-tracked and were not independently retrieved by the documentation author. No complete new clean-room job ledger (purge, allocation, ICINT19, MR10 suites, CAMBCOMP, runtime object installs, extension installs) accompanied the supplied panel excerpts. The operator describes the runs in the clean-room reconstruction context; this record cannot independently certify every upstream reconstruction stage or its exact commit SHA.

No new MVS job, JES console command, permanent object installation or dataset change was executed to create this record.
