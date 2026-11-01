# Installed production runtime PDS acceptance — 2026-10-11

## Decision

**Accepted as the native regression integration baseline for the tested
production-object behavior: 119/119 PASS.**

This is **not** a claim of 120/120 installed-object acceptance. Regression
083 remains deliberately excluded because it requires internal FREEMAIN
return counters not exported by the installed production members.

## Operator evidence

On 2026-10-11 the operator pulled main through `143df46` and ran:

```sh
python3 tools/checks/run-runtime-pds-acceptance.py
```

The harness sets `BCPL_RUNTIME_PDS=1` and runs two complete ranges,
without silently skipping any other case:

| Range | Pass | Fail | Total |
| --- | ---: | ---: | ---: |
| 000–082 | 83 | 0 | 83 |
| 084–119 | 36 | 0 | 36 |
| **Accepted production-object suite** | **119** | **0** | **119** |

The final operator output was:

```text
INSTALLED PRODUCTION RUNTIME PDS ACCEPTANCE
PASS  119
FAIL  0
TOTAL 119
EXCLUDED 083 (test-only reclamation instrumentation)
STATUS ACCEPTED: 119/119 production-object behavior tests
Independent 083 counter evidence: JOB 6295; not part of this run
```

The opt-in runner uses the installed five-member
`HERC02.BCPL.OBJ` object library: `BCPLMAIN`, `BCPLBYTE`,
`BCPLAPT`, `BCPLMEM`, and `BLIB`. The suite includes independent
native assembler / separately compiled BCPL linkage (026/025), historical
BLIB consumers (065–068), nonzero STOP completion (087/089),
and output rejection (113).

## Separate instrumentation proof and remaining boundary

Previous independent instrumented two-object regression 083, TK5
**JOB 6295**, completed ASMBCPL, ASMNAT, LKED and GO with RC=0000.
It printed `42` and `V=2 M=1`, showing two returned FREEMAIN
calls from the instrumented BCPLMEM drain and one from the instrumented
BCPLMAIN global/stack cleanup. The test does not independently verify
storage-manager success or leak freedom.

This is **supplementary evidence**, not a measurement of the installed
production BCPLMAIN/BCPLMEM object members. Preserve 083's fail-closed
behavior in `BCPL_RUNTIME_PDS=1`; do not install test-only
instrumentation or report a production-object 120/120 result.

## Operational policy

* Reproduce this gate with `python3 tools/checks/run-runtime-pds-acceptance.py`.
* Maintain the canonical runtime sources and production object members
  independently of test-only instrumentation.
* Keep the ordinary regression runner's defaults unchanged. Installed
  PDS remains an explicit opt-in until a separate decision promotes it.
* Changes to production runtime, PDS population, linker assembly strategy,
  or regression semantics require renewed evidence before reaffirming
  this baseline.

Evidence source: operator console transcript supplied 2026-10-11,
after pull from `fc04863` to `143df46`.


## Subsequent default-linkage decision (commit b215128)

Following the accepted 119/119 production-object integration run, the
native regression runner now defaults to `BCPL_RUNTIME_PDS=1` for ordinary
cases. This means an application-only assembly step followed by IEWL
linkage against the five installed `HERC02.BCPL.OBJ` members, rather
than reconstructing/assembling the runtime on every invocation.

* `tools/native/run-regression 25` uses installed production objects
  by default (provided TK5 already has the accepted object library).
* `BCPL_RUNTIME_PDS=0 tools/native/run-regression 25` explicitly
  selects the development/source-runtime path.
* Regression 083, **when no `BCPL_RUNTIME_PDS` setting is supplied**,
  retains its monolithic source-runtime instrumentation path and must
  still prove `V=2 M=1`. It is not counted as an installed-object test.
* An explicit `BCPL_RUNTIME_PDS=1 tools/native/run-regression 83`
  remains rejected; no unmeasured 083 production-object PASS is fabricated.
* `tools/checks/run-runtime-pds-acceptance.py` continues to require
  119/119 production-object passes, expressly excluding 083.

This is a change of **runner default**, not a claim that the installed
object dataset was regenerated or that TK5 operator validation of the
new default has occurred. The previous 119/119 acceptance result remains
the source of truth. The source-mode flags `BCPLMEM_OBJECT`,
`BCPLBYTE_OBJECT`, and `BCPLAPT_OBJECT` require explicitly choosing
`BCPL_RUNTIME_PDS=0`.

After pulling this default change, the first operator checks should
be a normal `tools/native/run-regression 25` followed by
`tools/native/run-regression 83`, and then a complete ordinary
120-test run. Its count would be a **mixed-mode 120/120** result, not
a 120/120 installed-object result.


## Default-linkage final validation — 120/120 mixed-mode PASS

On 2026-10-11, after pulling through commit `ddbe77f`, the operator
executed `tools/native/run-regression` without environment overrides.
All 120 numbered regressions, 000–119, passed:

```text
NATIVE REGRESSION COMPLETE
PASS  120
FAIL  0
TOTAL 120
```

Tests other than 083 selected the installed production runtime PDS by
default (119 cases). Test 083 selected the legacy source-runtime
instrumentation path and passed its own reclamation assertions. This is
**mixed-mode 120/120**, not installed-production-object 120/120.

Together with the independently accepted installed-object 119/119 run,
this completes the default-linkage migration milestone. Preserve the
explicit `BCPL_RUNTIME_PDS=0` source-development override and the
fail-closed explicit `BCPL_RUNTIME_PDS=1` test 083 restriction.
