# Milestone Runtime Extensions — R.1 owner acceptance and closure

**March:** R.1 — Generic registration foundation  
**Owner disposition:** **CLOSED — approved 22 October 2026**  
**Next march:** R.2 — Selective interoperability (planning; no R.2 implementation accepted here)  
**Evidence:** complete consolidated MVS run `20261022T121711413085Z`, submitted by the operator  
**Implementation baseline:** [Git commit `badbf49`](https://github.com/cbmira01/BCPL-for-MVS/commit/badbf499545a97b94b52f3a303a2ec88f5d8767f)

## Acceptance decision

On 22 October 2026, the project owner explicitly approved closure of R.1
after reviewing the consolidated MVS campaign summary. The campaign reported
**24 PASS / 0 FAIL** integrated jobs and **five PASS / zero FAIL** acceptance
gates, plus a fresh candidate-runtime native regression with **145 PASS,
0 FAIL, 1 expected SKIP (083)**. This record captures the owner's closure
decision; it does not declare the later R.2 or R.3 marches complete.

| Acceptance gate | Result | Evidence scope |
| --- | --- | --- |
| Registration and diagnostics | PASS | Real empty/selected BCRG; 1001–1014 rejections and transactional validation |
| Effective owner ledger | PASS | Actual application G!1, BLIB G!76, Core Runtime G!30 collisions |
| Finalizer lifecycle | PASS | Two-package reverse order and exactly once; FINISH, STOP(7), and injected errors |
| Source trust and linker provenance | PASS | Build-time A(SYMBOL)/ENTRY guards and IEWL MAP owner verification in the campaign |
| Candidate native regression | PASS | 00..145 panel using temporary R.1 runtime overlay; 145 PASS, 0 FAIL, 1 expected SKIP 083 |

## Integrated MVS job inventory

| JES jobs | Tests | Result |
| --- | --- | --- |
| 2760–2761 | Empty/selected registration, application START | 2 PASS |
| 2762–2775 | Diagnostics 1001–1014 | 14 PASS |
| 2776 | Diagnostic 2001 on FINISH | PASS |
| 2777–2779 | Ownership against application, BLIB, Core Runtime | 3 PASS |
| 2780–2783 | FINISH, STOP(7), FINISH-error, STOP-error finalization | 4 PASS |

The campaign's reported disposition was **READY FOR OWNER REVIEW**.
The subsequent explicit owner approval closes the R.1 gate; it is not a
claim that each raw JES report was independently reviewed in this conversation.
The runner checked each job's recorded completion, live output markers and
applicable IEWL MAP owners. Earlier failed campaign runs and their corrections
remain historical evidence, superseded by this passing campaign.

## Reproducibility and evidence location

The operator executed:

```sh
git pull --ff-only &&
python3 tools/bootstrap/run-r1-acceptance --execute
```

Evidence remains on the operator's machine at
`workarea/runtime-extensions-r1/acceptance/20261022T121711413085Z/`,
including `SUMMARY.md`, `results.json`, per-job reports and summaries,
JCL decks, IEWL maps and the regression transcript. These generated outputs
are not represented as committed Git files.

The campaign used **temporary object and load modules**. It did not
install, replace, or promote accepted `BOOT_OBJ` or `BOOT_DEVOBJ` members.
GitHub `main` remains the source of project code and tracked documentation.

The standalone G!150 FORMTREE/DEBUGINT compatibility issue remains unresolved.
Source trust is a controlled source/link-preparation guarantee, not arbitrary
runtime protection against malicious executable data.

## Handoff to R.2

[R.2 — Selective interoperability](milestone-runtime-extensions.md)
will validate two independent optional extension probes in 0/A/B/A+B
link configurations, common opcode-0 QUERY behavior, absence/dependency/
collision diagnostics and IEWL linkage evidence, without rebuilding
`BCPLMAIN` for each selection. A compiled BCPL export plus assembler export
is an optional additional demonstration **if practical**.

The exact probes, temporary JCL, and campaign design require review
before implementation. R.3 — Packaging and acceptance remains separate.
