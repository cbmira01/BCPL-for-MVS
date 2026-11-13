# CO.1 — Native GO behavioral failure and diagnostic checkpoint

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Implement coroutine support for native compiler  
**March:** CO.1 — Native ABI and Stack Architecture (IN PROGRESS)  
**Date:** 13 November 2026  
**Status:** Owner-reported native GO behavioral failure. Candidate diagnosis
is source-staged only; no native success or CO.1 closure is claimed.

## Observed native execution

The owner ran `tools/coroutines/run-co1-bcpl-switch.py --run` at
GitHub `main` `4464bb96a71b89e92a320bebc7b64df6673f179e`.
The saved run directory is
`workarea/co1-bcpl-switch/20261113T194332Z-v06i7zvd/`.

The runner reported:

```text
CO.1 BCPL FAIL: native BCPL records differ: ['FAIL']
CO.1 native BCPL runner RC=1
```

Unlike JOB 5351 (ASMS RC=0008), this run reached the exact
`assess()` output comparison. Under the committed runner's fail-closed
ordering, that requires a successful summary, highest RC=0000, and
all five ASMA/ASMM/ASMS/LKED/GO steps present with RC=0000. The
individual new JES job numbers and the full job-summary content were
**not** present in the owner's console excerpt and are not invented here.
The MVS program itself printed one `CO1BCPL FAIL` record; that is
a real *behavioral mismatch*, not an accepted context-switch result.

## Why the first output does not isolate the defect

`source.bcpl` used the *same* FAIL record if heap stack allocation
failed, if `CO1INIT` returned nonzero, or if the first `CHANGECO`
returned a value other than nine. A first-time WORKER entry receiving
the wrong argument could also return the sentinel 99 before printing
`A1`. Since `A1` is absent, current evidence does not distinguish
those hypotheses. No further assembler change is warranted yet.

## Diagnostic-only candidate change

Keep `co1change.asm`, production BOOT_OBJ members, and the successful
output sequence unchanged. Instrument only *failed* BCPL paths:

| Record | Failure classification |
| --- | --- |
| FALLOC | GETVEC stack allocation reported zero |
| FINIT | CO1INIT returned nonzero |
| FARG | Worker saw an initial argument other than seven (return 97) |
| FLOCAL | Worker reported corrupted locals or wrong resume argument (return 98) |
| FVALUE | First root resume returned an unexpected other value |
| FSECOND | Second root resume returned an unexpected value |

The original successful trace remains
`A1 R1 A2 R2 PASS`, with no extra instrumentation on success.
`tools/coroutines/run-co1-bcpl-switch.py` now identifies these complete
diagnostic records in the JES report, rejects them as failures, and
retains `observed_native_records` in the result receipt even when
GO produced a behavioral mismatch. Synthetic tests require all six
diagnostics to be extracted and **never** accepted as PASS.

## Assistant-side evidence and next action

The revised BCPL source was checked in the assistant's independent
workspace: six focused tests passed for ASCII/80-column records,
failure-marker presence, distinct 97/98 worker sentinel returns,
unchanged ordered success records, all six negative records, and
rejection of an assembler literal that merely contains a marker.
The locally tested file's Git blob identity was
`8cd14b35ad4212815fd3196ee1f28306c3cdf9b3`.
Full native proof is still pending. The next action is one isolated
compiler/IFOX/IEWL/GO candidate rerun using the new Git commit.
Use the observed failure category to direct the *next* machine-level
investigation; do not claim the candidate is repaired merely because
the trace is now more specific.

No MR10-kit development, installed-object modification, production
global registration, numbered regression, CO.1 acceptance or CO.2
opening is implied.
