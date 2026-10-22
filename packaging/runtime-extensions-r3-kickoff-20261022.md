# Milestone Runtime Extensions — R.3 kickoff and design review

**March:** **R.3 — Packaging and acceptance (ACTIVE)**  
**Owner instruction:** "Proceed to R.3", 22 October 2026  
**Previous:** [R.2 — Selective interoperability CLOSED](runtime-extensions-r2-closure-20261022.md)  
**Implementation:** Design review only; **no accepted PDS object promotion**.

## Purpose and governing contract

The [official Runtime Extensions milestone](milestone-runtime-extensions.md)
defines the R.3 deliverable as a stable user-facing link-edit recipe,
BCPL declaration conventions, a developer template, and a reproducible
rebuild from Git. Its exit gate also requires a **fresh full native
regression baseline**, a **separately accepted object-PDS installation
decision**, the documented startup contract, and actual JES/IEWL
evidence. These are **R.3**, not additional invented marches.

The approved R.0 A–H and QUERY ABI, R.1 generic registrar, and
R.2 optional selection/rejection behavior are the implementation
baseline. Do not redesign them simply for packaging. Distinguish the
Core Runtime, historical Base Library (BLIB), System Extensions,
Standard Libraries and User/Site Libraries according to
[runtime/library nomenclature](runtime-and-library-nomenclature.md).

## R.3 work and proposed acceptance evidence

| Work | Deliverable | Acceptance evidence |
| --- | --- | --- |
| Package template | A maintainable BCEX descriptor, BCRG/BCPLREG example, dispatcher and optional finalizer template | Source and fixed-column/relocation checks; independently assembled on MVS |
| BCPL declarations | Versioned public header, single dispatcher global and opcode constants; application-required ID convention | Compiled caller with correct QUERY and negative opcode behavior |
| Link-edit and run | Human-readable IEWL INCLUDE/MAP recipe selecting 0/A/B/A+B without BCPLMAIN rebuild; ordinary GO JCL keeps selection fixed | JES condition codes and IEWL MAP/XREF for explicit selected/absent objects |
| Rebuild | Reproduce temporary runtime, registrar and extension objects from Git sources and the documented demoted Cambridge bootstrap environment | Recorded Git SHA, source hashes, tools, generated JCL and clean build outcomes |
| Regression | One fresh full native 00..145 panel using the selected R.3 candidate runtime | **145 PASS, 0 FAIL, 1 expected SKIP 083**, and no unexplained regressions |
| Deployment decision | Document candidate/accepted object membership, PDS target, dependency/provenance and recovery policy | Separate owner decision **before** any persistent BOOT_DEVOBJ/BOOT_OBJ write |
| Final acceptance | Consolidated evidence and reproducible operator procedure | Owner review and explicit R.3 closure |

The existing R.1 acceptance suite passed 145/0/1 with a temporary
registration overlay. It does **not** substitute for R.3's fresh panel.

## Major design choices to approve before implementation

**1. Distribution and examples.** Recommended: retain
`BCPLDEMO` as the maintained, permanently allocated teaching/reference
System Extension (G!203); keep `R2TESTB` strictly a test fixture
(G!299). Publish source templates usable by User/Site Libraries without
inventing a second registration mechanism.

**2. Object packaging.** Recommended: reproduce and test temporary
`&&` objects first. Prepare an explicit `dspal`-manifest-aware
installation recipe, but **do not modify BOOT_DEVOBJ or BOOT_OBJ**
until the owner separately approves its destination and member set.
No automatic production promotion.

**3. Single operator workflow.** Recommended: one source-controlled
R.3 acceptance runner that rebuilds from Git, performs host checks,
submits consolidated MVS jobs, captures JES/IEWL evidence under ignored
`workarea/`, and executes one fresh 00..145 native panel. It should
produce a local summary automatically; no manual upload/download
workflow or packaging of private credentials is required.

**4. Compiled BCPL extension implementation.** R.2's optional "if
practical" demonstration was not exercised. Recommended: investigate
using a compiled BCPL callable export in an R.3 developer-template
example, with assembler-provided descriptor/registration linkage if
needed. Do **not** promise it without checking CG370 object/trailer
contracts, and do not give it an unapproved permanent global number.

**5. Evidence hardening.** Recommended: ensure each negative rejection
proves START did not execute and that expected IEWL MAP/XREF ownership
was inspected; retain source provenance and exact JES job identities.
This strengthens release-quality evidence without reopening R.2.

## Implementation boundary

Only the march transition and this design proposal are approved at
kickoff. **Changes to public ABI, global-number allocations, startup
ordering, an object-PDS deployment, or the final installed-object set
require explicit owner review.** No new milestone/march numbering is
introduced. GitHub `main` is the authoritative record; MVS and JES
are the authority for observed machine behavior.

The standalone G!150 FORMTREE/DEBUGINT concern remains outside R.3
unless the owner expressly brings it into scope. BCPLQSAM, BCPLTIME
and BCPLDEC implementation belongs to their separate milestones,
not this generic registration packaging march.
