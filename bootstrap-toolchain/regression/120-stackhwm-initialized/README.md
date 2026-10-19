# Regression 120 — BLIB STACKHWM after BCPLMAIN marker initialization

Exercise the historical BLIB G56 STACKHWM routine, with BCPLMAIN
initializing the alternating sentinel pattern and top metadata words.
The program accepts a stack high-water **word address** within
[STACKBASE, STACKEND) and emits `H`; it emits `?` for error
codes 0/1 or an out-of-range value.

No exact stack address is asserted because GETMAIN placement varies.
The accepted M2.1 candidate is DEVOBJ(BCPLM7). Run with the explicit
`BCPL_RUNTIME_PDS=1 BCPL_RUNTIME_LIBRARY=DEVOBJ BCPL_RUNTIME_CANDIDATE=1 BCPL_RUNTIME_CANDIDATE_MEMBER=BCPLM7`
selectors. This test passed within the accepted 00–123 panel. It does not
authorize any promotion to production HERC02.BCPL.OBJ.

Do not interpret an in-range high-water address as comprehensive proof
of historical stack usage semantics.
