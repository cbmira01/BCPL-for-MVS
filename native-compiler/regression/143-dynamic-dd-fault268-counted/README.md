# 143 — M4.3 counted buffer268 denial and retry

**FOCUSED TEST ACCEPTED 2026-10-17 (operator-reported PASS).** Reuses accepted regression 136 and the G151/private IOACCT helper from test 139. The synthetic denial occurs only on the second site visit; the successful third visit uses a genuine GETMAIN or SVC19. BCPL asserts exactly ten counters after the denial and after explicit closure of both streams; the test-private IODRAIN terminal check asserts balanced counters, DHEAD=0 and HHEAD=0 on FINISH. No production ABI, BCPLIO canonical assembler or installed PDS member changes.

After denial: 2, 1, 1, 0, 1, 0, 1, 1, 0, 0.
After both explicit closes: 3, 3, 2, 2, 2, 0, 2, 2, 2, 2.
See docs/Milestone-BCPLIO-dynamic-stream-M4.3-plan.md.

## First M4.3.2b attempted run — source-card length

On 2026-10-17 the operator ran the source checker successfully,
but 143 failed in host-side Cambridge preparation
before any MVS assembler or GO step. The inserted comment at
source line 19 was 82 characters (maximum 80). The comment was
shortened, and the repository M4.3 checker now inspects all four
BCPL case files for the Cambridge source-record limit. No
accounting result or MVS pass is claimed for this first attempt.

## Accepted focused MVS run — 2026-10-17

Operator-reported `tools/native/run-regression 142 145 --show-output` after the source-width repair at `ce8d3e1`: regression **143 PASS**, panel **4 PASS / 0 FAIL / 0 SKIP**, with source checker PASS. The deterministic BCPL counter assertions and post-IODRAIN guard executed on this reported passing GO path. The successful JES job number and individual IFOX/IEWL/GO step codes were not in the supplied console summary and remain for final M4.3 evidence extraction. This is synthetic failure, not a real MVS abend or genuine SVC19 rejection.
