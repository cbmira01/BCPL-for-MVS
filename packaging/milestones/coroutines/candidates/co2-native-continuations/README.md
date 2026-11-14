# CO.2 — Native repeated-continuation verification candidate

**Milestone:** Implement coroutine support for native compiler  
**March:** CO.2 — Native CHANGECO Implementation (IN PROGRESS)  
**Status:** Offline tests PASS; real MVS evidence PENDING

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
