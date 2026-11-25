# DR.0 — Record classification and dependency review

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 24 November 2026 EST  
**Status:** IN PROGRESS; grouped inventory for owner review, qualified.  
**Census baseline:** ed0f8066859ed4e1a310bbb91520d0d629c5dca3  
**Reviewed main:** 842e5aa4878205a59a8460740d520c37563b5073

Supplement to the [initial census](dr0-inventory-and-classification-20261124.md) and [semantic inventory](dr0-semantic-inventory-20261124.md). All 857 baseline Markdown paths are accounted for in the disjoint families below. Classification is by tree, indexes, representative content and selected contracts, not a full individual content audit. Unreviewed records default to retain. No architecture or disposition is approved.

## 1. Complete path-family census

| Path family | Count | Primary class / audience | Candidate disposition |
| --- | ---: | --- | --- |
| Root | 4 | Navigation, legal/provenance/audit; all | Revise navigation; preserve legal records |
| docs/ | 27 | Technical explanations/how-to; programmers/operators | Consolidate overlapping subjects; ten empty guides conditional removal candidates |
| bootstrap-toolchain/ | 21 | Source/build/reference/probes; developers | Consolidate active instructions; retain source navigation and fixtures |
| cambridge-compiler/ | 2 | Unfinished subsystem placeholders; developers | Retain honest status |
| config/ | 1 | Configuration reference; maintainers | Retain |
| docker/ | 1 | Operational how-to; operators | Retain canonical procedure |
| mr10-kit-compiler/ | 29 | Options, demos, build/run, evidence; programmers/developers | Consolidate manuals; retain source-local references and test records |
| richards-bcpltape/ | 1 | Historical archive; researchers | Preserve whole corpus |
| standard-library/ | 1 | Design-only scope; developers | Retain |
| system-extensions/ | 13 | APIs, selection, templates, evidence; programmers/developers | Consolidate common material in four approved-preference manuals; preserve contracts |
| tools/ | 11 | Operational procedures and reference; maintainers | Consolidate current guidance, retain executable-adjacent help |
| packaging/README.md | 1 | Navigation | Revise after architecture approval |
| packaging/applications/ | 2 | Exploratory research | Retain; not approved application work |
| packaging/architecture/ | 11 | Terminology, contracts, proposals; developers | Preserve authority; reconcile stale status |
| packaging/archive/ | 175 | Historical evidence and normative exceptions | Retain |
| packaging/distribution/ | 130 | Release instructions, decisions, verification | Keep frozen material; separate reusable procedures |
| packaging/evidence/ | 5 | Audits and evidence | Retain |
| packaging/milestones/ | 209 | Governance, contracts and evidence | Preserve accepted records and fixtures |
| packaging/operations/ | 21 | Policy, procedure, maintenance history | Consolidate active procedures; preserve decisions |
| tests/ | 192 | Test-local intent, contracts and evidence | Retain adjacent to fixtures |
| **Total** | **857** | | |

The seven frozen BT0003 text files, historical extensionless materials, headers, JCL comments, YAML/TSV/JSON, oracles and scripts are outside this Markdown count and not deletion candidates.

### Archive families (175)

Archive index 1; bootstrap 19; core-runtime 62; QSAM 49; Runtime Extensions 44. Indexes identify these as historical records, not current operating instructions. Preserve all, including candidate-specific contracts and executable fixtures. The R.0 owner ABI record explicitly links archived Decision G numerical limits and shared QUERY v1 contracts; these remain normative within their accepted scope despite archive placement.

### Milestone families (209)

Index 1; BCPLIO dynamic stream 12; BCPLTIME 3; coroutines 144; decimal-arithmetic 1; QSAM 7; Runtime Extensions 9; Tape artifact release 32. Preserve formal closure and all evidence, including unsuccessful attempts. Retain BCPLIO stream contracts, coroutine bounded/common behavior, QSAMSVC API, BCEX/BCRG v1, BCPLDEMO support decision, and frozen release acceptance. Decimal Arithmetic remains indefinitely deferred; TA.6 N/A for RC4. Coroutine candidate directories also contain live test sources and oracles.

### Distribution families (130)

Root 19; compiler-source 13; create-tape 66; install-from-tape 11; manifest 19; publication 2. Preserve design/acceptance records and frozen RC4 companion/release notes. BT0021 is historical source, not executable compiler. RC4 companion supersedes BT0003. Create-tape index's statement that there is no accepted candidate-independent live driver is compatible with the new driver being implemented and offline-tested; revise later to clarify this distinction. BC0005 validates the earlier integration, not the new driver. No new release authorized.

### Test documentation (192)

Index 1; Bootstrap 147 (146 cases plus extra case 069 material); Runtime Extensions 13; BCPLTIME 4; BCPLQSAM 14; coroutines 13. Representative reads: Bootstrap 00, 069, 083, 117, 145; R.5 146; T.1 159; Q.4 175; CO.5 177. Retain test-local descriptions and put common procedures in project manuals. Suite manifests govern 00–189, with additional paired cross-compiler suite distinct. Preserve 083 expected source-only SKIP, original case 117 failure history, and QSAM 175 full-panel failure/focused rerun distinction. Every coroutine README is a required executable fixture marker.

## 2. Additional content classifications and reconciliation

| Source | Finding / candidate disposition |
| --- | --- |
| MR10 asm and source READMEs | Interpreter/source-phase maps; retain provenance and correct old native ASM location |
| MR10 JCL and README-ICINT19 | Build how-to and JCL inventory; preserve stored JOB-card contract |
| MR10 language/BCPL demo READMEs | Example catalogs and run guidance; preserve 11 language and 17 BCPL examples |
| MR10 regression-panel and coroutine READMEs | Manifest/contract and historical diagnostics; distinguish baseline 12 cases from supported coroutine suite |
| Bootstrap asm/history, asm/bcplmain-wip, jcl/history | Historical source and deck provenance; retain |
| Bootstrap probes index | Active and dependency-retained source fixtures; retain until proven otherwise |
| CG370 architecture and runtime-interface notes | Source-grounded explanations; retain OCODE/INTCODE and declaration/behavior/ABI distinctions |
| stack-check-contract.md | Bounded historical evidence and reconstructed behavior; retain |
| runtime-contract-v1.md and archive m2-1-runtime-contract-v2.md | M1.9 candidate-era v1; v2 supersedes v1 only for D7; do not treat either as full current production ABI |
| BCPLIO dynamic runtime and final acceptance | DEVOBJ BCPLM6 + BCPLIO scope; no promotion implied; reconcile later production evidence |
| BCPLIO dynamic runtime contract | Missing relative link to early fixed-DD contract, now packaging/archive/core-runtime/regression/native-stream-contract.md |
| BCPLIO evidence index | Former packaging/bcplio-dynamic-stream path in prose; correct active navigation later |
| Tests 146 and 159 | Not-yet-tested statements stale relative to R.5/T.1 accepted MVS execution |
| Tests 069 and 117 | Earlier gate or PENDING TK5 statements; reconcile exact later results without erasing history |
| Coroutine 177 | G!289–305 test-local statement must stay scoped to candidate; production G!289–300 allocated |
| Tests 145 and 175 | Former docs milestone and bootstrap-toolchain/extensions paths; reconcile active references |
| Native panel Q.4 versus Q.5 | Dated 30 October 176 PASS / 0 FAIL / 1 SKIP is distinct from 1 November 175 PASS / 1 FAIL / 1 SKIP plus focused 175 pass |

## 3. Dependency extension

An additional 17 documents were checked for literal relative inline Markdown links (archive/evidence/distribution indexes, BCPLIO and runtime contracts, tests index and release identity decision). 89 occurrences, one absent target (fixed-DD contract above). Combined with prior checkpoint: 34 documents, 259 link occurrences, two links to empty targets and one absent target. No fragment, reference-style, external URL or complete repository graph validation.

| Consumer | Binding / consequence |
| --- | --- |
| tools/tests/run-suite lines 125–145 | Each coroutine case requires source-reference.txt, expected.txt and README.md; retain all 13 READMEs at current paths |
| tests/coroutines/177-co2-native-changeco/source-reference.txt | Points to packaging/milestones/coroutines/candidates/co2-native-changeco/source.bcpl |
| tests/suites/coroutine-contract.tsv | Paired CO.6 expected.txt under milestone candidates |
| tools/coroutines/run-co6-pair.py; run-co6-nested.py | Candidate source/oracle directories, accepted CO.3 dependencies; pair runner checks blob identity |
| tools/reconstruction/contract.py | CO.3 candidate compiler parameter input; retain build bindings |
| packaging/distribution/publication/scripts/ta8-rc4-review | Exact RC4 companion, manifest, license, notices and historical notes |
| tools/distribution/create-release | Legal/provenance byte inputs; generated FB80 documentation and ZIP README |
| config/dspal.yaml | Seven frozen DIST_DOCS paths |
| release registry and frozen manifests | Historical acceptance and provenance record paths |

Also inspected suite coordinator, native entry points, selected host regression tests and release tests. These are positive source findings, not proof of absence of further dependencies. A stale path in a historical note or planner is not proof of a live execution defect. No code execution or modification.

## 4. Disposition and architecture gate

Retain all accepted records, historical sources, frozen releases, normative contracts and live source/test paths. Consolidate common programming/extension explanations, MVS/System/370 background and active build/test/release workflows. Revise current status and navigation without changing contracts or qualifications. Archive only demonstrated obsolete active instructions after authority and dependency review. Ten empty guides are the only affirmative prose-file removal candidates; two inbound links to Guide-to-Project-Tools.md require resolution before removal.

DR.1 should prioritize manual catalog and authority map over directory relocation. Keep original normative references and source-adjacent required files reachable. No Wiki, Pages, rendering or physical architecture is approved.

## 5. Qualification

Every original Markdown path now has at least a conservative family-level provisional disposition. Principal active documentation and selected exceptions have a content-based first pass. The assistant workspace git ls-remote failed DNS resolution for github.com. GitHub code search returned zero incomplete results for two known-present references (Guide-to-Project-Tools.md and README.md in tools/tests/run-suite). Neither can support a negative dependency assertion. Pinned direct reads and full tree enumeration succeeded. A full individual content audit and repository-wide dependency graph remain unverified; retain unreviewed paths until checked. No owner host operation requested. No MVS execution is required for inventory.

DR.0 remains IN PROGRESS pending owner review and formal closure. No source, existing manual, frozen record, release, fixture or MVS state changed. This inventory is not permission to move or remove anything.
