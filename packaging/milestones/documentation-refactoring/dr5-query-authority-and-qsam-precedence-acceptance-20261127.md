# DR.5 — Owner acceptance of QUERY authority, BCPLQSAM rollback precedence and BLIB diagnostic limitations

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Documentation Refactoring  
**March:** DR.5 — Validation and Reconciliation (IN PROGRESS)  
**Date:** 27 November 2026 EST  
**Reviewed proposal revision:** `25bc5aa76f757675b2352e24a38a7f75c3088483`  
**Disposition:** OWNER APPROVED; effective in the GitHub main commit introducing this record.

Owner direction: "Approved A and B, accept BLIB diagnostic limitations, proceed. You have authorization to commit."

## Effective decisions

The [reviewed proposal](dr5-query-authority-and-qsam-precedence-proposal.md)
contains the clause mapping, evidence and limitations.

- **A:** Chapter 1 of the [Reference for System Extensions](../../../../docs/product/Reference-for-System-Extensions.md)
  replaces the [R.0 common QUERY v1 decision](../../archive/runtime-extensions/runtime-extensions-r0-query-abi-decision-20261021.md)
  as normative authority for that public interface only. The original
  decision and evidence remain intact. The approved clarification on
  append-only descriptors and incompatible format changes is included.
- **B:** Chapter 5.4 of the same reference records the newly approved
  primary OPEN failure precedence and uncertain ownership policy.
  Preserve primary status, publish no handle, quarantine, no repeated
  CLOSE or unsafe free; existing generic FINISH/STOP policy applies.
  Direct returned CLOSE error remains -14. Case 200 provides private
  instrumented evidence, not genuine exceptional MVS CLOSE proof.
  No change to executable instructions, oracles or installed members.
- **BLIB:** Chapter 5 of the [Runtime and Libraries reference](../../../../docs/product/Reference-for-the-Cambridge-Runtime-and-Libraries.md)
  records accepted historical diagnostic limitations. The owner accepts
  those as DR.5 qualifications; no unsupported postmortem reconstruction
  or unsafe execution is required at this scope.

## Preservation and remaining work

The DR.1 transfer safeguards continue to apply. Other registration,
finalizer, package-specific, language, compiler, runtime, coroutine and
Project Tools authorities are unchanged. Global allocations, configuration,
manifests, test oracles and frozen release documents retain authority.
Genuine exceptional MVS CLOSE, complete diagnostic execution and arbitrary
pointer/register behavior remain qualified. No new native execution,
numbered case, release change or march closure.

The BCPLQSAM source comment update preserves all non-comment cards and
their order, and total line count; changed cards satisfy ASCII and
column-71 checks. No claim of object byte identity or new assembler run.
