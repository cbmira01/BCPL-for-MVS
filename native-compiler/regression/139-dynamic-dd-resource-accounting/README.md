# 139 — dynamic DD resource accounting (isolated test-only BCPLIO)

**STAGED: no reported IFOX/MVS execution.** Requires BCPL_RUNTIME_PDS=1, BCPL_RUNTIME_LIBRARY=DEVOBJ, BCPL_RUNTIME_CANDIDATE=1 and BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6.

Compiles a normal BCPL application. G151 points only in this test to separately assembled NATIVEAD, which calls private test-only BCPLIO entry IOACCT. Checks exact dynamic GETMAIN/FREEMAIN and SVC19/SVC20 counts, duplicate FIND, ENDREAD, stale handle, and fresh DD02 identity after reopen. The installed candidate runtime modules are not changed.

Expected marker: M43 PRE-DRAIN COUNTS OK.

This test does not prove post-IOFIN 16-byte tombstone reclamation, real MVS free semantics, or system abend recovery. Consult docs/Milestone-BCPLIO-dynamic-stream-M4.3-plan.md for further gates.
