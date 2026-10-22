# Milestone Runtime Extensions - R.2 consolidated acceptance design

**March:** R.2 - Selective interoperability (ACTIVE).  
**Owner decision:** Approved one consolidated runner and batched remaining
checks, 22 October 2026. **R.3 has not started.**

## Completed positive evidence

Actual MVS **JOB 3080** on 22 October 2026 executed all four selections
0/A/B/A+B. Fourteen IFOX steps, four IEWL links, four GO steps returned
**RC=0000** (22/22). Each unique application success marker appeared
exactly once. The four real IEWL maps showed BCRG lengths **28 / 44 /
44 / 60** bytes, correct presence/absence of `DMODESC`/`DMODISP`
and `R2BDSC`/`R2BDISP`, with the same temporarily assembled `BCPLMAIN`
and `RGINIT` reused across all four links. The four demoted Cambridge
compiler jobs were **3076-3079**, and matrix JOB **3080**. Their separate
compiler JES reports are not individually attested by this record.
The operator supplied the complete JOB 3080 JES/IEWL/GO report for review.
No accepted object PDS was updated.

## Approved consolidated campaign

`tools/bootstrap/run-r2-acceptance --execute` performs credential-free
host preflight, compiles four separately linked BCPL callers, generates
private, authenticated JCL, submits **two batched MVS jobs** (the
positive 0/A/B/A+B matrix and the negative/dependency batch), monitors
JES completion and validates actual step return codes and output.

The negative batch has **21 independent cases**: one valid A -> B
version-compatible dependency, diagnostic categories 1001-1014
(including two-export collision; application, BLIB and Core Runtime
ownership; missing selections; API major/minor requirements; dependency
order/self-reference), and one deliberate IEWL unresolved-symbol case.
Each case has independent IEWL and GO steps. An expected RC=0012 does
**not** suppress following cases. Startup rejection must not publish
G!203 or G!299, and a test-only BCPLMAIN rejection-path witness returns
RC=0016 if either global changed. The deliberately missing object must
fail IEWL, and its GO must not execute. Every GO RC and matching **live**
`BCPLREG` diagnostic is individually verified.

Source and intermediate object datasets are temporary `&&` datasets.
`BOOT_OBJ` is read with `DISP=SHR`; `BOOT_DEVOBJ` is not modified. The
canonical BCPLMAIN, registrar and historical library are not changed.
No Git commit or promotion occurs within the runner.

## Reproducible operator commands

From repository root:

```sh
python3 tools/bootstrap/run-r2-acceptance --check
python3 tools/bootstrap/run-r2-acceptance --execute
```

Each execution keeps its `SUMMARY.md`, `results.json`, case manifest,
input SHA-256, generated assembler, private JCL (mode 0600), step summaries
and complete raw reports under a distinct timestamped
`workarea/runtime-extensions-r2/acceptance/` directory. The reports may
contain machine-local details and are **not** committed.

Passing one campaign yields **READY FOR OWNER REVIEW**, not automatic
R.2 closure. Any unexpected RC, diagnostic, START output, IEWL-map owner,
missing case, ABEND or bypass beyond the deliberate unresolved-link GO
prevents acceptance. Full native regression and an independent PDS
installation decision remain gates of **R.3 - Packaging and acceptance**.

## Optional compiled-BCPL extension

The R.2 milestone says to include a separately compiled BCPL *extension
export* alongside an assembler export **if practical**. The current
R.2 demonstrations compile independent BCPL **callers**, not BCPL
extension implementations; the distinction is material. The campaign
does not claim to exercise a compiled BCPL package export. Before closing
R.2, the owner should explicitly accept deferring that optional extra to
R.3 or request an additional compiled-export implementation.

G!299 remains test-only, not a permanent allocation. G!203 remains
BCPLDEMO. The G!150 FORMTREE/DEBUGINT issue is separate and unresolved.
