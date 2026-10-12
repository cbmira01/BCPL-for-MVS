# Regression 120 — BLIB STACKHWM after BCPLMAIN marker initialization

Exercise the historical BLIB G56 STACKHWM routine, with BCPLMAIN
initializing the alternating sentinel pattern and top metadata words.
The program accepts a stack high-water **word address** within
[STACKBASE, STACKEND) and emits `H`; it emits `?` for error
codes 0/1 or an out-of-range value.

No exact stack address is asserted because GETMAIN placement varies.
The regression uses the existing installed-PDS suite runner by default;
for the first gate run `BCPL_RUNTIME_PDS=0 tools/run-native-regression 120
--show-output` so the staged new BCPLMAIN is assembled into the test
without changing HERC02.BCPL.OBJ. The source-mode object strategy must
include resident BLIB via the existing `object-blib.txt` fixture.

Only after source mode passes should BCPLMAIN alone be promoted to OBJ.
Do not interpret an in-range high-water address as comprehensive proof
of historical stack usage semantics.
