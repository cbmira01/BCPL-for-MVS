# Milestone Runtime Extensions — R.3 campaign acceptance and closure review

**March:** R.3 — Packaging and acceptance (**ACTIVE; closure under owner review**)  
**Owner decisions, 22 October 2026:** Record the consolidated campaign
as **successful**; **defer object-PDS installation**; conduct the R.3
closure review. These instructions are **not** an explicit decision
to mark the march CLOSED.  
**Tested Git revision:** [`a24606328810187c85f9e680eb82d7380b53c55c`](https://github.com/cbmira01/BCPL-for-MVS/commit/a24606328810187c85f9e680eb82d7380b53c55c)  
**Operator-local campaign:** `20261022T185250588162Z`  
**Review disposition:** **READY FOR OWNER CLOSURE DECISION**, with
the limitations below retained.

## Successful consolidated R.3 campaign

The owner supplied the operator terminal transcript, including the
successful `git pull --ff-only`, `--check` output, complete
`--execute` progress output, and generated `SUMMARY.md` text.

| Phase | MVS job | Operator campaign verdict | Tested behavior |
| --- | --- | --- | --- |
| Developer template without finalizer | **3101** (`R3TNFIN`) | **PASS**, no issues | Rebuilt BCPL caller, BCEX/BCRG, dispatcher and IEWL selection without `TMFIN` |
| Developer template with finalizer | **3102** (`R3TFIN`) | **PASS**, no issues | Same pattern, with relocated `TMFIN` and live finalizer witness |
| Selective interoperability | **3103** (`R2MATRIX`) | **PASS**, no issues | Four link-edits, 0/A/B/A+B, shared temporary BCPLMAIN within this matrix |
| Negative/dependency checks | **3104** (`R2NEG`) | **PASS**, no issues | Existing 21-case matrix: valid dependency, 19 runtime rejections, one unresolved-link rejection |
| Native 00–145 | Multiple case jobs | **PASS**, no issues | Fresh installed-OBJ inputs with **temporary R.1 BCPLMAIN/registrar/empty BCPLREG overlay** |

Host preflight reported eight `HOST PASS` commands in each
`--check` and `--execute` invocation. The demoted Cambridge compiler
generated fresh System/370 assembler for the template client and four
R.2 BCPL callers before the consolidated MVS jobs were submitted.
The runner's per-job `PASS` verdict checks actual JES step results,
expected live client/finalizer diagnostics, and relevant IEWL MAP/XREF
selection against its source-controlled verification rules.

### Fresh native panel

The supplied terminal transcript contains **145 distinct native
`REGRESSION PASS` case records, zero case FAIL records, and exactly one
SKIP record for case 083**. It prints:

```
NATIVE REGRESSION  00..145  (146 tests)
REGRESSION SKIP  083  083-instrumented-storage-reclamation (source-only instrumentation)
NATIVE REGRESSION COMPLETE
REGRESSION PASS  145
```

The source-controlled R.3 runner independently rejects a regression
unless the underlying transcript contains totals **PASS=145, FAIL=0,
SKIP=1, TOTAL=146** and exactly one `SKIP 083`, with process RC=0.
The returned phase verdict was `PASS`. This is a **fresh R.3 run**,
not a reuse of the R.1 panel's earlier PASS receipt.

The console capture provided in the conversation is **21,540 bytes**
(SHA-256
`c958818021c72940026a13b1c8926df2b9f32f644e718222a6ac859b181795e8`).
It contains the printed campaign summary but not the underlying complete
JES job reports, `results.json` or `sha256.json`.

## Reproducibility and evidence boundary

The operator invoked, from the source checkout:

```sh
git pull --ff-only
python3 tools/bootstrap/run-r3-acceptance --check
python3 tools/bootstrap/run-r3-acceptance --execute
```

The runner reported **READY FOR OWNER REVIEW** with all five phases
PASS, no issues. Its ignored local evidence directory is:

```
workarea/runtime-extensions-r3/acceptance/20261022T185250588162Z/
```

Its `SUMMARY.md`, `results.json`, `sha256.json`,
`cases.json`, generated sources, authenticated JCL, JES reports,
IEWL maps, compile logs and native case logs remain **operator-local**.
This Git record is a verifiable account of the operator's supplied
console and campaign verdict, **not** a claim that the assistant
independently inspected the four raw JES reports or their individual
return codes and complete maps. No raw printer output, machine-local
credentials or generated JCL is committed.

The native baseline is the accepted **`BOOT_OBJ` library inputs**
with an **opt-in temporary registration-runtime overlay** assembled
during each case. It is not a panel using newly installed
`BCPLREG`/registrar objects in a persistent runtime PDS and is not
a fresh empty-PDS reconstruction from the clean-room runbook.
Similarly, the independently compiled BCPL units demonstrated here
are **callers**, not a separately compiled BCPL extension export;
the optional service implementations remain assembler.

The R.2-derived negative verifier checks expected conditions,
diagnostics and a rejected-START absence marker. Independent IEWL
owner assertions for **every** malformed case, and an exhaustive
hard pre-START execution witness on **every** rejected path, were
not added. This residual assurance limitation is recorded, not
silently described as completed. The R.1 lifecycle campaign provides
earlier accepted reverse-order, FINISH/STOP and error-return evidence;
these behaviors were not all rerun as independent R.3 cases.

## Owner-approved R.3 object-PDS disposition: DEFERRED

On 22 October 2026 the owner explicitly decided to **defer
object-PDS installation** after seeing the passing R.3 campaign.

- **`BOOT_OBJ`:** no change, replace, or promotion authorized.
- **`BOOT_DEVOBJ`:** no change or candidate installation authorized.
- **Distribution:** source, templates, public headers, build
  instructions, and temporary-object acceptance workflow remain
  authoritative in GitHub `main`.
- **Final membership and target:** **not selected** by this decision.
  `BCPLREG` is application-selected per link; no generic registrar,
  descriptor, or extension member is deemed installed merely because
  its temporary source was assembled and tested.
- **Provenance and rollback:** because no installation is authorized,
  no new persistent object requires recovery. Any *future* proposal
  must identify the intended manifest-managed PDS, exact member
  identities, source/build provenance, dependency and link-edit recipe,
  backup/replacement/rollback procedure, and receive separate owner
  approval before writing any object members.

**The R.3 deployment-decision gate is satisfied by the explicit
DEFER decision; it is not evidence of installed-object acceptance.**
G!203/`BCPLDEMO` remains the permanently allocated reference
extension; G!299/`R2TESTB` and the developer-template instance
remain test-only. No ABI change or new GLOBAL allocation follows.

## Review of the official R.3 exit gates

| Official R.3 requirement | Review | Evidence or qualification |
| --- | --- | --- |
| Stable developer template and BCPL declarations | **MET** | Git sources, host tests, actual JOBs 3101–3102 |
| Stable 0/A/B/A+B link-edit recipe and startup contract | **MET within tested scope** | Linkage guide, R.0 approved A–H and QUERY ABI, JOB 3103, earlier R.1/R.2 evidence |
| Rebuild from Git and authentic MVS JES/IEWL evidence | **MET for candidate workflow** | Fixed Git SHA, fresh five-client compile, four PASS MVS batches; source/JCL digests operator-local |
| Fresh native 00–145 panel | **MET** | 145 PASS / 0 FAIL / 1 expected SKIP 083 on temporary registration overlay |
| Separate object-PDS installation decision | **MET: DEFER** | Owner decision above; no installation conducted or authorized |
| Consolidated review and reproducible operator procedure | **MET for documentation; owner closure pending** | This record, tracked runner and workflow guide, local evidence path |

### Closure recommendation

**Recommend approval to close R.3 — Packaging and acceptance as
a verified source-distributed, temporary-link registration
foundation**, expressly *without* claiming installed runtime
objects, an empty-PDS clean-room rebuild, full original historical
compatibility, or exhaustive negative-case provenance assurance.

The project owner's instruction was to record the successful
campaign, defer object-PDS installation and **review for closure**.
It did not explicitly approve **closing R.3**. Accordingly **R.3
remains ACTIVE** and the official milestone status must stay
unchanged until the owner explicitly directs closure. No new R
march is proposed.

## Related authoritative records

- [Milestone Runtime Extensions](milestone-runtime-extensions.md)
- [R.3 kickoff and design review](runtime-extensions-r3-kickoff-20261022.md)
- [R.3 reproducible acceptance workflow](runtime-extensions-r3-acceptance-workflow.md)
- [R.3 template JOB 3094/3095 evidence](runtime-extensions-r3-template-jobs-3093-3095-evidence-20261022.md)
- [R.3 IEWL linkage guide](runtime-extensions-r3-linkage-guide.md)
- [R.2 closure record](runtime-extensions-r2-closure-20261022.md)
- [R.1 closure record](runtime-extensions-r1-closure-20261022.md)
