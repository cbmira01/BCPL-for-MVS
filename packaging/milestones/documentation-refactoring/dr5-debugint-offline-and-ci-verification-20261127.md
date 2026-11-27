# DR.5 — Focused DEBUGINT offline verification and isolated CI gate

**Project:** BCPL for MVS 3.8 Reconstruction  
**March:** DR.5 — Validation and Reconciliation (IN PROGRESS)  
**Date:** 27 November 2026 EST  
**Inspected product source revision:** `7d4c2924c34191c4c9891f8c7b2f23ccfada21b8`  
**Host-only workflow revision:** `d877309d56a7606fa6a725ec31abf3e980ec6817`

## Actual assistant-side checks

Conventional Git access still fails DNS resolution (RC128); public archive retrieval is also unavailable. The assistant independently inspected the exact pinned GitHub sources, not the installed MVS objects. The current BCPLMAIN blob `061eb84cb3480bf804e66ed2ca8a24e3b3c7d369` equals the original blob `8a4f02de4e6f2c4e02fdbbec16f53b51b53b2fa4` at `0fde1b7c8c7ab1e2d1f6a07e77869030f6c06a24` plus exactly the approved two-card preservation of R7 across the minus-sign append. The static check found no ASCII, tabs, trailing whitespace, column-71 or assembler-name-field violations. Inspection of DEBUGINT and DBGAPND confirms that the latter uses R7 as scratch and leaves R8 intact. The BCPL source and expected records pass static card/record checks.

The assistant independently reconstructed these two complete fixture blobs in its own workspace and verified their Git blob hashes before running Python:

- DEBUGINT source.bcpl: `a7adaeecae847a6d35fe4239979d0dd1688b93e3`
- DEBUGINT expected.txt: `d3ab86e7275e93f1f698dc3ca91297e1f4e3ba3b`

Two contiguous source extracts were copied from pinned Python modules and verified by byte length and FNV-1a-32 fingerprint (a transfer check, not a cryptographic blob identity claim):

| Pinned module | Complete module blob | Extract | Bytes / FNV-1a-32 |
| --- | --- | --- | --- |
| tools/checks/run-dr5-language-verification.py | b7c8952d5a47cfe644311a7cec72ccef9d4c6ad3 | CODE definition through check_candidate, before check() | 2784 / 9ab0fbac |
| tools/checks/run-dr5-debugint-verification.py | a2110eedeabdd9606ebd3bdb96f904bc9bde8f0d | require through baseline_result, before install_cards | 1507 / 7b9d4d1d |

The actual extracted functions executed successfully: check_candidate checks six ordered records, source cards, missing/duplicate/altered/reordered records and JES summary parsing; baseline_result requires reproduction of a signed defect, positive/zero controls and exact record shape; private_cards removes the installed BCPLMAIN link selection, enlarges the private assembly region, preserves the private input and rejects missing/ambiguous anchors and over-width cards on a synthetic deck. These checks used no MVS services. They are not the full DEBUGINT --check invocation or a native candidate result.

## Full host verification strategy

A narrowly scoped [GitHub Actions workflow](../../../.github/workflows/dr5-offline-verification.yml) at the workflow revision above invokes the existing five host-only gates: checker unittest discovery, release unittest discovery, project coordinator --check, bootstrap --check-inputs and DEBUGINT --check. This is an assistant-managed supplementary verification mechanism, not a new product requirement or a replacement for assistant workspace checks. It triggers only on changes to its own workflow on main or an explicit manual dispatch, not on ordinary source pushes. The checkout uses full history, a pinned checkout action, read-only contents permission and no persisted credentials. It has bounded execution, disconnected stdin, logs within repository-root mvs-state, and no target configuration or MVS submissions. All five gates report their exit codes.

The assistant copied the workflow into its own workspace, verified exact Git blob `3d2815229b8bf7ed858cd0aee09db7a279bf130a`, parsed its YAML, checked Bash syntax and confirmed the five host-only commands, trigger scope and permissions. At the first Actions API query after promotion, no run was listed for the workflow revision; no CI execution or outcome is claimed at this checkpoint.

## Disposition

The full post-correction offline gate remains outstanding pending actual receipts. No target mutation, source installation, reconstruction, release or march transition is authorized by this record. Prior [reconstruction host verification](dr5-independent-reconstruction-host-verification-20261127.md) remains valid at its tested revision. The owner performs only MVS-facing operations; the assistant retains responsibility for offline checks, and the prior no-retry rules remain in force.
