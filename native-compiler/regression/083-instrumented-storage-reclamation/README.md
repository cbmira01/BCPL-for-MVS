# 083 — Instrumented outstanding storage reclamation

## Intent

This test distinguishes program output from the teardown behavior of
BCPLMAIN. START acquires three vectors, explicitly FREEVECs the middle
one, retains the other two, prints 42, and invokes FINISH.

The test-local assembler transformation `instrument-reclaim.py`
modifies the generated **copy** of BCPLMAIN, never the canonical
`asm/bcplmain-wip.asm`. It increments a vector counter immediately
after each vector FREEMAIN R returns, increments a main counter
immediately after combined-storage FREEMAIN R returns, and emits a
seven-character diagnostic record from RELDONE.

Expected runtime output is two consecutive records:

```text
42
V=2 M=1
```

The first record comes from BCPL DEBUGINT and FINISH's normal flush;
the second comes from test-only instrumentation after cleanup.

A passing test establishes that both vector FREEMAIN macro calls and
the main-storage FREEMAIN macro call returned to their respective
instrumentation sites, in the required teardown order. It does **not**
independently establish successful MVS storage reclamation: this test
does not inspect storage manager return codes or independently query
allocated regions. Canonical runtime behavior is unchanged.

The injection script is strict about unique anchors and refuses source
longer than assembler column 71. The normal native regression source
checker still runs on the instrumented result.

Status: **PENDING TK5**, no assembly, link, or GO result yet.
