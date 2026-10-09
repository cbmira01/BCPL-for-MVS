# 087 — Test-only STOP(100) completion probe

Status: **PENDING TK5**. Verified baseline: 86/86.

START writes S and invokes global G!30 as STOP(100), with no
subsequent FINISH. Test-only `../instrument-stop-probe.py` installs
a STOP adapter into the combined assembler copy. It verifies the
BCPL argument, routes to canonical FINIMPL (flush, CLOSE, RELMEM),
and selects MVS return code 100.

Expected BCPL output: S. Expected IFOX and IEWL RC=0000,
GO RC=0100. Nonzero RC is accepted
only for case 087; all other nonzero GO results remain failures.

**Important:** This does not prove historical STOP maps argument to
MVS return code; the adapter deliberately implements that hypothesis.
The run tests feasibility and the native invocation/lifecycle shape,
not the missing historical STOP entry. No canonical runtime changes.
