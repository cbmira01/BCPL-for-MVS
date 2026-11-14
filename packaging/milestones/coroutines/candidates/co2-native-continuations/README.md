# CO.2 — Native repeated-continuation verification candidate

**Milestone:** Implement coroutine support for native compiler  
**March:** CO.2 — Native CHANGECO Implementation (IN PROGRESS)  
**Status:** Corrected candidate OWNER-REPORTED NATIVE-MVS-TESTED PASS (JOB 5378/5379); CO.2 acceptance pending

This independent native BCPL fixture extends the owner-reported
JOB 5374/5375 positive-path baseline. It tests the **same separate
Core Runtime BCPLCO IFOX implementation**, without modifying its
assembly, accepted BOOT_OBJ objects or permanent public globals.

A starts with value 7. The nested A frame sends 111 to B; B
sends 211 to A; A sends 112 to B; B sends 212 to A. A then
returns 31 through the normal compiler-generated return linkage.
The root resumes B with 313; B returns 42 naturally. Both
nested call chains validate their persistent locals and G54/G55
stack bounds after every resume, and the root rechecks its bounds
after both worker returns. Known terminated workers refuse re-entry.

## 14 November 2026 — First MVS attempt and arithmetic correction

The first native attempt at revision `ae51ea4bd3c142bc3aa349d74ee850f2a6fdc4f5`
reported `X1 Y1 X2 Y2 X3 FVALUE`, runner RC=1. The source expected
`DEEP1(4)=17` and `DEEP2(5)=22`, but the recursive bodies compute
23 and 32. These two source assertions are now corrected, with a
regression test deriving the expected values from the recursion.

See the [failure and correction record](../../co2-native-continuations-failed-oracle-20261114.md).
The earlier result remains **FAIL**. At this documented correction
checkpoint a successful rerun was still required; the separate PASS
is recorded below.

## 14 November 2026 — Corrected MVS rerun PASS

The operator's corrected test at revision `5f941bb34cc70649f0325bd73f42eeb67397c5d6`
passed: compiler JOB 5378, native JOB 5379, three IFOX, one IEWL
and one GO, with all five native steps accepted as RC=0000 by the
runner, and the exact nine-record BCPL oracle; runner RC=0.
Detailed receipts are retained locally at
`workarea/co2-native-continuations/20261114T161730Z-1a8_w7bf`.
See [JOB 5378/5379 evidence](../../co2-native-continuations-jes-5378-5379-pass-20261114.md).

The original failed run at revision `ae51ea4bd3c142bc3aa349d74ee850f2a6fdc4f5`
remains FAIL; its arithmetic error was repaired before the new PASS.
This does not approve any production library/object installation,
public global ABI or CO.2 closure.

Expected exact ordered native output:

    CO2BCPL X1
    CO2BCPL Y1
    CO2BCPL X2
    CO2BCPL Y2
    CO2BCPL X3
    CO2BCPL R1
    CO2BCPL Y3
    CO2BCPL R2
    CO2BCPL PASS

**Native verification:** from the project root, use the guarded
operator command for
tools/coroutines/run-co2-native-continuations.py --run.
The runner reuses the authenticated /CN Cambridge compiler job
and three temporary IFOX objects, followed by IEWL and GO. It
requires five zero-RC steps, exact ordered records and a completed
JES job. Detailed evidence is retained under
workarea/co2-native-continuations/ and console output is compact.

Offline tests for this fixture and wrapper are in
tools/checks/test_co2_native_continuations.py. They are not a
substitute for actual MVS execution.

The 24-word descriptor, small private registry, result values
and test-local globals G!295–299 remain **unapproved** as public
ABI elements. This case does not implement CO.3 lifecycle,
CO.4 robustness, or CO.5 release integration. CO.2 remains open
until separately accepted by the owner.
