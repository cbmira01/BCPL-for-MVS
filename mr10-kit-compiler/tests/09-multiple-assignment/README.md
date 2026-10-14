# Multiple assignment in MR10 BCPL

This test records a historical compiler behavior: assignments with comma-separated destinations happen **in order**, not all at once.

| Starting values | Command | Result |
| --- | --- | --- |
| A=1, B=2 | `A, B := B, A` | A=2, B=2 |
| A=1071, B=462 | `A, B := B, A REM B` | A=462, B=0 |

Run `tools/compile-and-run --results "$(tools/current-icint)" mr10-kit-compiler/tests/09-multiple-assignment/multiple-assignment.bcpl`.

Programs needing a true swap must use temporary variables. Keep this test: it records what the MR10 compiler actually does.
