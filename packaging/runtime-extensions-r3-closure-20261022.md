# Milestone Runtime Extensions — R.3 owner closure (22 October 2026)

**Owner decision:** **CLOSE R.3 — Packaging and acceptance.**  
**Milestone disposition:** **Milestone Runtime Extensions CLOSED.**  
**Date:** 22 October 2026  
**Acceptance candidate Git revision:** [`a24606328810187c85f9e680eb82d7380b53c55c`](https://github.com/cbmira01/BCPL-for-MVS/commit/a24606328810187c85f9e680eb82d7380b53c55c)  
**Review/evidence record:** [R.3 acceptance and closure review](runtime-extensions-r3-acceptance-review-20261022.md)  
**Disposition:** Accepted for the *source-distributed, temporary-link registration foundation* and its reproducible test procedure; **not** accepted for persistent MVS object installation.

## Owner approval

Following the owner-reported successful consolidated R.3 campaign, the
owner directed: **"Close R.3, give me a handoff prompt for R.4."** This
is the explicit authorization missing from the preceding closure
review. R.3 is now closed by the owner. The documented R.0–R.3 plan
has no further approved march, so Milestone Runtime Extensions is
closed on the evidence and scope below.

The accompanying request for an **R.4 handoff** does not by itself
define or approve a new official march, objective, acceptance gate,
or implementation scope. Such a definition requires a future owner
decision and an explicit update to the milestone plan before work
begins. No new march is created by this closure.

## Accepted R.3 evidence

At Git `a246063`, the operator ran the tracked
`tools/bootstrap/run-r3-acceptance --check` and `--execute`
workflow. The operator's supplied console and generated summary
report:

| Evidence | MVS job | Verified campaign result |
| --- | --- | --- |
| R.3 developer template, without finalizer | 3101 | PASS |
| R.3 developer template, with finalizer | 3102 | PASS |
| R.2-derived 0/A/B/A+B link-edit and run matrix | 3103 | PASS |
| R.2-derived 21-case negative/dependency batch | 3104 | PASS |
| Fresh native 00..145 regression | Individual case jobs | **145 PASS, 0 FAIL, one expected SKIP 083** |

The operator-local campaign directory is
`workarea/runtime-extensions-r3/acceptance/20261022T185250588162Z/`.
The full reports, authenticated JCL, source/JCL SHA-256 manifest, and
case logs stay there and are not committed. The reviewer independently
examined the supplied console/summary, not all of the individual raw
JES and IEWL outputs. The runner's PASS verdict verifies its declared
JES, code, MAP/XREF, marker and regression rules. The accepted native
panel used installed `BOOT_OBJ` inputs plus *temporary*
R.1 `BCPLMAIN`/registrar/empty-`BCPLREG` overlays, not a newly
installed candidate runtime.

The accepted scope includes the BCEX/BCRG registration ABI, documented
startup and finalizer contracts, public header/declaration convention,
link-edit selection recipes, source developer template, and reproducible
operator acceptance runner. Supporting R.0 ABI and R.1/R.2 acceptance
evidence remains applicable.

## Deferred installation and retained limits

**The owner expressly deferred object-PDS installation.** Neither
`BOOT_OBJ` nor `BOOT_DEVOBJ` is authorized for change, and no
member set or deployment/rollback plan has been approved. A later
installation requires a separate owner decision identifying member
provenance, manifest-managed target, dependencies, and recovery policy.
Source-controlled GitHub `main` remains the official code and
documentation authority.

This closure **does not claim** any of the following:

- Persistent registration objects were installed in MVS libraries.
- An empty-PDS clean-room rebuild or post-installation regression was
  performed as part of this R.3 campaign.
- A separately compiled BCPL extension *implementation* was exported;
  compiled BCPL *callers* were demonstrated, while extension
  dispatchers remained in assembler.
- Exhaustive independent IEWL symbol-owner and hard pre-START
  execution witnesses were checked for every malformed negative case.
- Full historical System/370 BCPL compatibility was certified.

These are documented scope/evidence limits, not undisclosed successful
tests. They do **not** reopen R.0, R.1, R.2 or R.3.

## Official disposition and subsequent work

**R.0 — Evidence and contract CLOSED.**  
**R.1 — Generic registration foundation CLOSED.**  
**R.2 — Selective interoperability CLOSED.**  
**R.3 — Packaging and acceptance CLOSED.**  
**Milestone Runtime Extensions CLOSED.**

The official milestone currently defines only R.0–R.3. No R.4
objective, name, gates or active status is established. If the owner
wishes to pursue work under **R.4**, the next conversation must
first review the charter, nomenclature and existing milestone records;
agree on whether to extend this completed milestone or establish
another formal scope; document the approved objective and gates;
and obtain owner approval before implementing changes. This is a
scoping checkpoint, not a dormant automatic release.

Future `BCPLQSAM`, `BCPLDEC` and `BCPLTIME` implementation
remains governed by their **own** milestone documents. The G!150
FORMTREE/DEBUGINT concern remains separate. No ABI, compiler,
global-number assignment, MVS object, or Git branch is changed
by this closure.

## Related source records

- [Official Milestone Runtime Extensions](milestone-runtime-extensions.md)
- [R.3 acceptance and closure review](runtime-extensions-r3-acceptance-review-20261022.md)
- [R.3 acceptance operator workflow](runtime-extensions-r3-acceptance-workflow.md)
- [R.3 linkage and declaration guide](runtime-extensions-r3-linkage-guide.md)
- [R.0 owner-approved ABI decisions](runtime-extensions-r0-owner-abi-decisions.md)
- [R.1 closure](runtime-extensions-r1-closure-20261022.md)
- [R.2 closure](runtime-extensions-r2-closure-20261022.md)
