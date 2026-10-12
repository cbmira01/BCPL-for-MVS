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


## Installed runtime PDS acceptance boundary (11 October 2026)

The isolated two-object instrumented BCPLMEM probe has already executed
successfully on TK5 (JOB 6295): its output was exactly `42` followed by
`V=2 M=1`, and ASMBCPL/ASMNAT/LKED/GO returned RC=0000.
This is evidence for the instrumented *test copies*, not instrumentation
of installed `HERC02.BCPL.OBJ(BCPLMAIN)` or `(BCPLMEM)`.

The production installed objects do not export `MEMDCNT` or `TRM083`.
Their FREEMAIN macros were assembled into machine instructions. The
regression harness cannot inspect how many times those internal call
sites returned merely by linking an application against the unchanged
object members. The other installed-runtime-PDS tests establish behavioral
compatibility; they do not turn 083 into a call-count test.

**Preserve the fail-closed block for `BCPL_RUNTIME_PDS=1` test 083.**
Do not mark it PASS on successful execution/output alone, substitute a
probe using different BCPLMAIN/BCPLMEM objects without reporting that
substitution, or install instrumented production OBJ members.

A defensible two-tier acceptance report is:

1. **Installed production objects:** run tests 000–119 except 083; require
   119/119 PASS, and explicitly label 083 not measurable in this mode.
2. **Separate instrumentation evidence:** retain JOB 6295's successful
   test-only two-object `V=2 M=1` result and revalidate that probe after
   any BCPLMAIN/BCPLMEM source changes.

A future true 120/120 *installed-object* instrumentation gate requires an
explicit observation mechanism designed into and validated for the installed
runtime (for example, an opt-in diagnostic ABI or system-level traced service
calls). Both alternatives are architectural changes, not harness fixes.

## MEMBIND-compatible probe update (12 October 2026)

`tools/checks/prepare-bcplmem-083-probe.py` now starts from canonical
`asm/bcplmem.asm` (including `MEMBIND` and G6!48 publication). The
instrumented temporary copy additionally exports `MEMDCNT` and counts
successful returns from the `MEMDRAIN` FREEMAIN macro only. The
externalized BCPLMAIN copy imports both `MEMBIND` and `MEMDCNT`;
its own `TRM083` counter still counts its final combined-storage
FREEMAIN. Neither production source nor the installed object PDS is
instrumented.

The expected two output records remain `42` and `V=2 M=1`.
**TK5 rerun is pending for this revised probe**. The older JOB 6295
result predates this MEMBIND-compatible update and is not acceptance
of the new probe. Installed-PDS mode remains deliberately excluded.
