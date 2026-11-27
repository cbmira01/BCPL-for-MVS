# DR.5 — Package-specific public API authority transfer acceptance

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.5 — Validation and Reconciliation  
**Date:** 27 November 2026 EST  
**Reviewed proposal revision:** `5dfea1785a1db413e325d61349197901984252a6`  
**Disposition:** OWNER APPROVED — effective in the GitHub main commit introducing this record.

Owner direction: "A, B and C approved; you have authority to commit".

The [reviewed proposals and clause mappings](dr5-extension-package-api-authority-transfer-proposal.md)
are approved individually. The [Reference for System Extensions](../../../../docs/product/Reference-for-System-Extensions.md)
is now normative within these additional scopes:

| Transfer | Destination | Prior public-interface authority superseded |
| --- | --- | --- |
| A — BCPLDEMO | Chapter 3 | [Source README](../../../../system-extensions/bcpldemo/README.md), published API behavior |
| B — BCPLTIME | Chapter 4 | [Source README](../../../../system-extensions/bcpltime/README.md) ABI section and public-interface provisions of [T.0](../bcpltime/bcpltime-t0-closure-20261024.md) / [T.1](../bcpltime/bcpltime-t1-closure-20261024.md) |
| C — BCPLQSAM | Chapter 5, with common chapters 1–2 | [Q.0 public specification](../qsam/bcplqsam-public-interface.md) and externally observable provisions of the [staging decision](../../archive/qsam/qsam-q0-staging-resource-design-decision.md) and [returned-error decision](../../archive/qsam/qsam-q0-error-and-r0-design-decisions-20261020.md), as reconciled with later accepted evidence |

The approved proposal clarifications are incorporated without changing
public constants or executable behavior. QUERY null/zero size probes
remain no-write operations. BCPLQSAM's valid-dispatch result contract,
complete stage before publication, independent-handle failure boundary,
finalizer continuation and PDS/attribute limits are explicit. Previously
approved primary OPEN failure precedence is unchanged.

The BCPLDEMO permanent support decision remains governing for maintenance,
compatibility review and permanent coverage obligations. Package-specific
source and headers, allocations, configuration, manifests, private design,
test oracles, original contracts and acceptance chronology are preserved.
Source READMEs identify the current normative chapters. Macro/tool
interfaces have not been transferred.

Actual exceptional MVS CLOSE, complete geometry and register coverage,
fresh installed-object build/readback, BCPLTIME clock interpretation and
the consolidated current-source regression remain qualified or pending as
previously recorded. No new MVS execution, behavior change, numbered
regression, release action or march closure.
