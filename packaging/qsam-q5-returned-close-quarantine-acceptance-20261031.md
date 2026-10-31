# Milestone QSAM — Q.5 returned-CLOSE quarantine acceptance

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** **Q.5 — Hardening & release** (IN PROGRESS)  
**Owner decision:** **ACCEPTED 31 October 2026.** The owner expressly directed "Accept 8147" after reviewing the native test report.  
**Scope:** Test-only injected returned-CLOSE quarantine behavior in `BCPLQSAM`. This is **not** acceptance of an actual MVS CLOSE failure, promotion of any installed object, or closure of Q.5/Milestone QSAM.

## Native compiler and preparation provenance

- **Q5RCCOMP JOB 8146:** resident demoted Cambridge compiler `COMP` ICINT19 RC=0000, `SVCODE` IEBGENER RC=0000; `EXECUTION CYCLES = 918876, CODE = 0`; 309-line recovered assembler SHA-256 `37607f62e4acc6d0ec2a4cf3ca8908e2516695d4622b73e4e5991d5c2755c1ac`.
- First `Q5RCCLOS` JCL preparation stopped before JES because the preparer wrongly required `ENTRY R0APP` in raw CG370 output. The raw code contains an unnamed CSECT; the accepted `application_source()` adapter adds the entry at JCL construction. The original failure log was retained. No JES job was submitted in that attempt.
- After a source-controlled correction, the successful one-shot preparation produced **4,121 JCL cards**, SHA-256 `2ad6eff04abb325cdc71bddff43a1baaf5c615ff19dce7f5aef1bce8c678e1eb`, at `workarea/bcplqsam-q5/q5rcclos.jcl` from GitHub `main` `3a0c25b4d31849d27149ca57cd157963c6ca8323`. The job's distinct one-shot attempt metadata is under `workarea/bcplqsam-q5/q5rcclos-attempt/`.

## Owner-observed native execution — Q5RCCLOS JOB 8147

The owner submitted the temporary JCL **once** and supplied the JES summary, report excerpts and both original-log extracts.

| Step | Program | Observed |
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
| GO | temporary load module | **RC=0008, expected** |

JES reported **JOB RESULT: SUCCESS**, **HIGHEST RC: 0008**; IFOX reported **0 statements flagged** and **highest severity 0**. The printer report includes the BCPL application record `BCPLQSAM Q5 CLOSE QUARANTINE PASS` and registrar message `BCPLREG 2001 FINALIZER RETURNED NONZERO`. Operator collection reported **Overall RC=0** (accepting the expected GO RC=8 for this specific test). This is not an ordinary RC=0 application exit.

Both Hercules console `mvs-state/log/3033.log` and MVS hardcopy `mvs-state/log/hardcopy.log` show matching job-bounded diagnostic phases:

```text
Q5C:E:00000001:00000002:00000002:00000002
Q5C:L:00000001:00000001:00000001:00000001:00000000
Q5C:X:00000001:00000001:00000001:00000001:00000008
```

The test-only overlay permits a genuine Q00 CLOSE macro call to complete and **only when that returned zero** overrides R15 once to drive the production `QSCQUAR` branch. The native BCPL assertions and diagnostic counts support: `QS_ERR_CLOSE=-14`, invalidation of Q00's public handle (`QS_ERR_HANDLE=-7` thereafter), independent Q01 `INFO`/1024-byte `READ`/successful `CLOSE`, quarantine state retaining one tracked DCB and stage, and `FINISH` returning RC=8 without a blind CLOSE retry or unsafe free.

## Acceptance boundary and remaining work

**Accepted:** response of the existing production control flow to a **test-injected nonzero returned CLOSE status** following a successful real CLOSE, plus native finalizer accounting of that quarantine.

**Not established:** a genuine nonzero MVS CLOSE return or abend path; validity/ownership of OS DCB state after an actually failed CLOSE; recovery from an unrecovered task abend; universal behavior across geometries/devices. The deliberately retained state after the injected status is expected in this bounded experiment.

No production `bootstrap-toolchain/extensions/bcplqsam/bcplqsam.asm`, installed object, or permanent MVS dataset was changed by the test. The separate Q.5 failed-OPEN rollback experiment JOB 8145 was already accepted. Geometry/resource hardening, packaging and optional object-promotion decision, clean-from-Git reconstruction, focused/full native regression, and formal owner Q.5 closure remain outstanding.

**Cross-reference:** [returned-CLOSE test design and incident chronology](qsam-q5-returned-close-quarantine-design-20261031.md), [QSAM milestone](milestone-qsam.md), and retained local `q5rccomp-attempt/`, `q5rcclos-preparation*.log` and `q5rcclos-attempt/` evidence.
