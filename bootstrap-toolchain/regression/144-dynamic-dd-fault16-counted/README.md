# 144 — M4.3 counted handle16 denial and retry

## Formal acceptance evidence — 2026-10-17

**M4.3 CLOSED, regression 144 PASS.**
Compiler JOB 7890; GO JOB 7891 (RG144R).
ASMAP IFOX00 RC0000; ASMFIO IFOX00 RC0000; ASMNAT IFOX00 RC0000;
LKED IEWL RC0000; GO RC0000.
Job-level RESULT=SUCCESS; the regression runner reports PASS.
Only test-private BCPLIO was linked; no installed runtime was changed.
See `docs/Milestone-BCPLIO-dynamic-stream-M4.3-plan.md`.

**FOCUSED TEST ACCEPTED 2026-10-17 (operator-reported PASS).** Reuses accepted regression 137 and the G151/private IOACCT helper from test 139. The synthetic denial occurs only on the second site visit; the successful third visit uses a genuine GETMAIN or SVC19. BCPL asserts exactly ten counters after the denial and after explicit closure of both streams; the test-private IODRAIN terminal check asserts balanced counters, DHEAD=0 and HHEAD=0 on FINISH. No production ABI, BCPLIO canonical assembler or installed PDS member changes.

After denial: 2, 1, 2, 1, 1, 0, 2, 2, 1, 1.
After both explicit closes: 3, 3, 3, 3, 2, 0, 3, 3, 3, 3.
See docs/Milestone-BCPLIO-dynamic-stream-M4.3-plan.md.

## First M4.3.2b attempted run — source-card length

On 2026-10-17 the operator ran the source checker successfully,
but 144 failed in host-side Cambridge preparation
before any MVS assembler or GO step. The inserted comment at
source line 19 was 82 characters (maximum 80). The comment was
shortened, and the repository M4.3 checker now inspects all four
BCPL case files for the Cambridge source-record limit. No
accounting result or MVS pass is claimed for this first attempt.

## Accepted focused MVS run — 2026-10-17

Operator-reported `tools/native/run-regression 142 145 --show-output` after the source-width repair at `ce8d3e1`: regression **144 PASS**, panel **4 PASS / 0 FAIL / 0 SKIP**, with source checker PASS. The deterministic BCPL counter assertions and post-IODRAIN guard executed on this reported passing GO path. The successful JES job number and individual IFOX/IEWL/GO step codes were not in the supplied console summary and remain for final M4.3 evidence extraction. This is synthetic failure, not a real MVS abend or genuine SVC19 rejection.
