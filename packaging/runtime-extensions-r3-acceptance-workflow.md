# Runtime Extensions — R.3 reproducible acceptance workflow

**Milestone:** Runtime Extensions  
**March:** R.3 — Packaging and acceptance (**CLOSED 22 October 2026**)  
**Status:** Source-controlled and owner-accepted acceptance procedure;
operator MVS campaign **PASSED on 22 October 2026** at Git `a246063`
(JOBs 3101–3104; native 145 PASS / 0 FAIL / 1 expected SKIP 083).
The owner deferred object-PDS installation and then **CLOSED R.3**.
See the [formal owner closure](runtime-extensions-r3-closure-20261022.md)
and [acceptance review](runtime-extensions-r3-acceptance-review-20261022.md).

## Why this runner exists

`tools/bootstrap/run-r3-acceptance` combines the existing, verified
components rather than introducing an alternate compiler, registrar, or
JCL format. It tests the R.3 developer template, re-exercises the
R.2 selective-interoperability campaign, and runs one fresh complete
native regression using the R.1 temporary-object BCPLMAIN/BCPLREG
overlay.

The source of record is GitHub `main`. Run from an updated Git checkout
with the demoted Cambridge bootstrap compiler installed and TK5 MVS
operational. `--execute` refuses uncommitted changes to tracked files.

## How to run

From the repository root:

```sh
# Preflight: no machine-local credentials, JCL creation, or JES work.
python3 -B tools/bootstrap/run-r3-acceptance --check

# Full acceptance candidate: fresh compiler + MVS + native panel.
python3 -B tools/bootstrap/run-r3-acceptance --execute
```

Execution uses the existing `config/dspal.local.yaml` settings through
the established compiler and JCL helpers; do not paste passwords,
operator-specific dataset names, or report contents into tracked files.
The runner is fail-closed on compilation, assembly, linkage, GO,
application-marker, IEWL-map, or regression verification errors.

## Work performed by `--execute`

| Phase | Test | Basis |
| --- | --- | --- |
| Host preflight | R.3 template and R.2 unit tests; generator checks; R.1 preparation; native numbering; R.3 verifier tests | No MVS operations |
| Compile | R.3 BCPL client plus R.2 `zero`, `a`, `b`, `both` clients | Fresh demoted Cambridge compiler output |
| Template without finalizer | `R3TNFIN`: selected `BCPLREG`, BCEX, dispatcher, no hook | Six IFOX RC0, IEWL RC0, GO RC0, one BCPL PASS marker, verified MAP/XREF |
| Template with finalizer | `R3TFIN`: identical ABI with relocated `TMFIN` | Seven IFOX RC0, IEWL RC0, GO RC0, one client marker and one **live** finalizer WTO |
| Four-link selection | R.2 `R2MATRIX`, profiles 0/A/B/A+B | Reused R.2 source-controlled generator and positive verifier |
| Negative/dependency | R.2 `R2NEG`, 21 cases | Reused R.2 source-controlled generator/verifier, with added rejected-START output check |
| Fresh regression | Native **00–145**, production object inputs plus R.1 per-case *temporary* BCPLMAIN/registrar/empty BCRG | **145 PASS, 0 FAIL, 1 SKIP, TOTAL 146**, and **SKIP 083 exactly once** |

The R.2 test fixture `R2TESTB` uses G!299; the R.3 developer
template also uses G!299 **only in separate test executables**.
Neither constitutes a new permanent global-number allocation.
The maintained reference System Extension remains `BCPLDEMO` at G!203.

The historical R.1 regression overlay is deliberately reused with
`R1_ACCEPTANCE=1` and private log/case directories. Its temporary
`BCPLMAIN`, registrar and 28-byte empty `BCPLREG` are assembled in
each regression job, not installed. The existing source-controlled
R.2 generators still produce their established `R2MATRIX` and `R2NEG`
job names; these names do not change the march designation to R.2.

The template jobs assemble a fresh temporary BCPLMAIN **separately in
each job**; the four-link matrix independently checks BCPLMAIN reuse
*within* one multi-link job. Do not confuse those claims.

## Saved evidence

Every full run makes a never-reused timestamped directory:

`workarea/runtime-extensions-r3/acceptance/<UTC-stamp>/`

It contains `SUMMARY.md`, `results.json`, `sha256.json`,
`cases.json`, `generated/` (BCPL source and CODE), `jcl/`,
`compiler-logs/`, `reports/`, `summaries/`, `regression-logs/`,
`regression-cases/`, and `regression-transcript.txt` when executed.
The manifest records the Git revision, SHA-256 of source/generator
inputs, generated assembler, and actual job decks. The full regression
transcript records the native totals and case-by-case progress.

**Do not commit the run directory.** Its authenticated decks and
operator-specific records belong in ignored `workarea/`.
On any incomplete stage the overall result is not ready. The runner
never silently substitutes a previous result or invents JES job IDs.

## What this does not authorize

- No change to the R.0 A–H decisions or shared opcode-0 QUERY ABI.
- No persistent write or object promotion to `BOOT_OBJ` or `BOOT_DEVOBJ`.
- No creation of a public G!299 allocation or System Extension implementation.
- No claim of separately compiled BCPL *extension implementation/export*;
  the template implementation remains assembler with a compiled BCPL caller.
- No **automatic** owner acceptance or closure of R.3. A complete
  passing run is **READY FOR OWNER REVIEW**; the owner subsequently
  approved closure on 22 October 2026.

This consolidated runner reuses the R.2 verifier; independent negative
IEWL MAP owner inspection for every malformed case and a hard
pre-START witness for every rejected GO remain areas to review for
release-quality evidence. Its extra absence check for the rejected
zero-selection START marker strengthens but does not by itself close
all such evidentiary gaps.

The object-PDS membership, destination, recovery/rollback policy,
and permission to install remain a **separate owner decision** after
review of current Git/MVS evidence. The 00–145 native regression does
not substitute for a completely empty-PDS clean-room reconstruction;
that procedure is maintained in
[the clean-room runbook](clean-room-mvs-reconstruction.md).

## Related records

- [R.3 kickoff and exit gates](runtime-extensions-r3-kickoff-20261022.md)
- [JOBs 3093–3095 initial developer-template evidence](runtime-extensions-r3-template-jobs-3093-3095-evidence-20261022.md)
- [R.3 linker/declaration guide](runtime-extensions-r3-linkage-guide.md)
- [R.1 accepted registration/lifecycle/regression evidence](runtime-extensions-r1-closure-20261022.md)
- [R.2 selective-interoperability closure](runtime-extensions-r2-closure-20261022.md)
