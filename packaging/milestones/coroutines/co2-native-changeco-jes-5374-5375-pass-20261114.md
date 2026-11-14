# CO.2 — Native CHANGECO: JOB 5374/5375 positive-path PASS

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.2 — Native CHANGECO Implementation — IN PROGRESS  
**Evidence date:** 14 November 2026  
**Source revision:** 3ba79577b171216ed809bfb37d21b0d27270d88d  
**Evidence class:** OWNER-REPORTED NATIVE-MVS-TESTED

## Operator-reported outcome

The owner executed the guarded CO.2 native runner from the source revision
above. The report states:

| Stage | JOB | Observation |
| --- | --- | --- |
| Cambridge compiler | 5374 | Compiler driver accepted the result |
| IFOX | 5375 | ASMA, ASMM, ASMS — 3/3 RC=0000 |
| IEWL | 5375 | LKED — RC=0000 |
| Native execution | 5375 | GO — RC=0000 |
| BCPL behavioral oracle | 5375 | A1 B1 A2 R1 B2 R2 PASS, exact order |
| Native runner | — | Exit status 0 |

Runner transcript:

    CO.2 BCPL PASS: compiler JOB 5374, GO JOB 5375; IFOX 3, IEWL 1, GO 1; A1 B1 A2 R1 B2 R2 PASS
    CO.2 BCPL evidence: workarea/co2-native-changeco/20261114T141120Z-w7s__us5
    CO.2 native runner RC=0

The owner retained detailed local receipts in
workarea/co2-native-changeco/20261114T141120Z-w7s__us5. The original JES
reports, generated assembler listing, and result.json were not supplied for
independent examination in this conversation. Do not classify this as an
assistant-replayed native MVS test.

## Scope established

The test executes two separate worker stacks, direct worker-to-worker
context transfer, nested checked frames, continuation values, normal worker
return, known-terminated-descriptor re-entry refusal, and root G54/G55
restoration. Source-level implementation additionally updates STKLIM and
APLIMIT on every transfer; this test does not independently measure their
values. Full PSW/condition-code preservation is not established.

The runner assembles isolated temporary candidate objects, links a temporary
load module, and uses accepted BOOT_OBJ objects read-only. There is no
evidence of production object installation or replacement. Test-local
G!295–299, the 24-word descriptor, limited registry, and private result
codes remain experimental and are not permanent public interfaces.

## Promotion and next verification

**Promoted in source evidence:** JOB 5374/5375 is the initial CO.2
native-positive-path reference baseline. Keep bootstrap-toolchain/asm/bcplco.asm
as the separate Core Runtime candidate. This is **not** a production binary
promotion, permanent global allocation, release, or a CO.2 closure.

Next run the independent CO.2 repeated-continuation BCPL case from
packaging/milestones/coroutines/candidates/co2-native-continuations
using tools/coroutines/run-co2-native-continuations.py. Its distinct
nine-record oracle and full IFOX/IEWL/GO/JES receipt are pending real MVS.

**Disposition:** CO.0 CLOSED (qualified), CO.1 CLOSED (qualified);
CO.2 IN PROGRESS, pending explicit owner acceptance;
CO.3–CO.5 NOT STARTED.
