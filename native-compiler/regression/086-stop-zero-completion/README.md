# 086 — Test-only STOP(0) completion probe

Status: **PENDING TK5**. Verified baseline: 86/86.

START writes S and invokes global G!30 as STOP(0), with no
subsequent FINISH. Test-only `../instrument-stop-probe.py` installs
a STOP adapter into the combined assembler copy. It verifies the
BCPL argument, routes to canonical FINIMPL (flush, CLOSE, RELMEM),
and leaves the existing zero completion code.

Expected BCPL output: S. Expected IFOX and IEWL RC=0000,
GO RC=0000. Nonzero RC is accepted
only for case 087; all other nonzero GO results remain failures.

**Important:** This does not prove historical STOP maps argument to
MVS return code; the adapter deliberately implements that hypothesis.
The run tests feasibility and the native invocation/lifecycle shape,
not the missing historical STOP entry. No canonical runtime changes.
