# 142 — M4.3 counted descriptor32 denial and retry

**STAGED ONLY / NOT EXECUTED UNDER MVS.** Reuses accepted regression 135 and the G151/private IOACCT helper from test 139. The synthetic denial occurs only on the second site visit; the successful third visit uses a genuine GETMAIN or SVC19. BCPL asserts exactly ten counters after the denial and after explicit closure of both streams; the test-private IODRAIN terminal check asserts balanced counters, DHEAD=0 and HHEAD=0 on FINISH. No production ABI, BCPLIO canonical assembler or installed PDS member changes.

After denial: 1, 0, 1, 0, 1, 0, 1, 1, 0, 0.
After both explicit closes: 2, 2, 2, 2, 2, 0, 2, 2, 2, 2.
See docs/Milestone-BCPLIO-dynamic-stream-M4.3-plan.md.
