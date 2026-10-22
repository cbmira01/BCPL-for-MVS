# Milestone Runtime Extensions — R.2 owner closure and acceptance

**March:** R.2 — Selective interoperability  
**Owner disposition:** **CLOSED — 22 October 2026**  
**Next march:** **R.3 — Packaging and acceptance ACTIVE**  
**Tested revision:** [`7141907`](https://github.com/cbmira01/BCPL-for-MVS/commit/71419079a7d48a94b5cdd8e3a87583cb83e0c80b)  
**Campaign:** `20261022T153739889342Z`

## Owner acceptance decision

The owner directed **"Proceed to R.3"** after the consolidated R.2
runner reported both jobs PASS. This constitutes the decision to accept
and close R.2 and begin R.3. It is not authorization to install,
replace or promote any accepted MVS object module, change the ABI, or
close R.3. No additional operator file exchange is required.

The owner supplied the campaign's shell transcript and `SUMMARY.md`
text in the conversation. The summary reports:

| MVS job | Test batch | Campaign result |
| --- | --- | --- |
| 3091 | 0/A/B/A+B interoperability matrix | PASS, no issues |
| 3092 | 21-case consolidated negative/dependency tests | PASS, no issues |

The command on Git revision `7141907` passed host preflight, compiled
four BCPL clients using the **demoted Cambridge compiler**, submitted
both batch jobs, and reported `READY FOR OWNER REVIEW`.

## Functional scope accepted

The tested 0/A/B/A+B matrix selects no extensions, `BCPLDEMO` (A),
test-only `R2TESTB` (B), or both, without changing or reassembling
`BCPLMAIN` per link. Both dispatchers respond to opcode 0 QUERY,
and the BCPL clients check their capabilities and unsupported calls.

The negative fixture manifest contains **21 cases**: one valid
dependency execution; **19 runtime rejections** covering diagnostics
1001–1014 (including same-slot conflicts, application/BLIB/Core
Runtime ownership, malformed BCRG/BCEX, missing requirements,
dependency order and API version mismatches); and one intentional
unresolved-symbol link that must prevent GO. The runner's verification
checks expected step return codes, live diagnostics, the positive
dependency marker and a test-only reject-path witness for G!203 and
G!299. The selected negative batch returned PASS.

The earlier independent positive JOB 3080 review established 22/22
assembly/link/run steps at RC=0000, all four BCPL markers, IEWL
selection identities and BCRG sizes **28/44/44/60** bytes. JOB 3075
separately established BCPLDEMO extension A. The later JOB 3085
positive batch passed; JOB 3086 never ran because of a JCL converter
error, corrected at `7141907`. JOBs 3091/3092 are the
authoritative passing consolidated campaign.

## Exact evidence boundary

- The **operator's** campaign runner read actual JES reports and
  returned PASS for both jobs. That is the basis of this owner
  acceptance.
- The assistant did **not independently inspect** the campaign's
  complete operator-local `results.json` or JOB 3092 raw JES report.
  The full set of 21 actual GO/IEWL records and maps therefore is not
  separately attested in this document.
- The runner did not independently enforce every IEWL MAP owner in
  the negative batch or explicitly assert non-execution of START
  in each rejected case; its returned RCs, diagnostics and witness
  checks form the accepted automated evidence boundary.
- The operator-local evidence remains at
  `workarea/runtime-extensions-r2/acceptance/20261022T153739889342Z/`
  (including `SUMMARY.md`, `results.json`, `cases.json`,
  `sha256.json`, generated sources and JES reports). Those private
  artifacts are **not** committed to GitHub. This record does not
  imply that they were uploaded.
- No separately compiled BCPL **extension implementation/export** was
  demonstrated. The four separately compiled BCPL programs were
  **callers**, while A and B dispatchers were assembler implementations.
  The "if practical" extra is conditional in the R.2 milestone.
  R.3 will assess a source-level BCPL package implementation as part
  of developer-template work, without retroactively claiming it here.

## Controls retained

The version-1 R.0 owner decisions A–H, common QUERY ABI and Decision G
numerical diagnostics remain in force. Permanent **G!203/DEMOSVC**
belongs to `BCPLDEMO`; **G!299** remains **test-only**, with no
public allocation. G!150 FORMTREE/DEBUGINT is a separate unresolved
issue, not an R.2 blocker.

`BOOT_OBJ` and `BOOT_DEVOBJ` were not promoted or altered by the
R.2 campaign. The full fresh native regression and any acceptance of
object-PDS installation belong to **R.3 — Packaging and acceptance**.
GitHub `main` remains source/documentation authority; MVS is the
execution/evidence authority.

See the [R.3 kickoff and design review](runtime-extensions-r3-kickoff-20261022.md).
