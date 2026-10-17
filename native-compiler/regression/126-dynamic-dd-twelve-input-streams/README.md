# 126 — Twelve simultaneously open dynamic input streams

**Status:** permanent native compiled-BCPL candidate-only stress regression,
staged for first MVS execution. Not yet accepted or MVS-validated.

The harness generates twelve separate GO-step DD DATA allocations,
`DD01` through `DD12`, using `input-dd01.records` through
`input-dd12.records`. Each contains two one-character FB80
logical records; `RDCH` exposes a newline (10) at each boundary.

The compiled BCPL source opens **all twelve streams before any reading**,
asserts that their twelve handles are nonzero and pairwise distinct,
interleaves the first and second records across every stream, verifies
an independent trailing newline and EOF for each, and checks UNRDCH on
a character and EOF. It then closes all twelve in **reverse open order**,
asserting selected-handle invalidation on each close. Any assertion
calls STOP(8), while only a successful execution prints the exact marker
`BCPL TWELVE INPUT OK` and FINISHes normally.

```sh
BCPL_RUNTIME_PDS=1 \
BCPL_RUNTIME_LIBRARY=DEVOBJ \
BCPL_RUNTIME_CANDIDATE=1 \
BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM6 \
tools/native/run-regression 126 --show-output
```

Acceptance: resident Cambridge compiler success, IFOX assembly RC0000,
IEWL link RC0000, GO RC0000 without abend, expected exact output, and
the runner reporting PASS 126. Failure to open twelve handles, cursor
cross-talk, or leaking a selected closed handle must not count as PASS.

This tests a twelve-concurrent-stream capability, not repeated
OPEN of the same DD, DASD seek semantics, dynamic FINISH/STOP cleanup,
read-error recovery, or arbitrary JCL allocation limits.
Keep it candidate-only until production BCPLIO is explicitly promoted.
