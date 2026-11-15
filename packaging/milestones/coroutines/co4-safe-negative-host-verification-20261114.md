# CO.4 — Recoverable negative-path candidate host verification

**Project:** BCPL for MVS 3.8 Reconstruction
**March:** CO.4 — Robustness and Edge-Case Verification (IN PROGRESS)
**Candidate:** `co4-safe-negative`
**Evidence classification:** HOST-CHECKED / NATIVE MVS PENDING
**Baseline:** accepted CO.3 code at `612234b106b5ef450b9d2ee70effd0f39ca96a70`, plus owner-reported CO.4 stress PASS recorded at `55e74259f26e9bd03a328eb6053f770ce9de9e10`

## Testable claims

The new BCPL fixture verifies refused sizes 1023/1025/-1, root `COWAIT`/`RESUMECO` refusal, third worker registration refusal at the accepted two-worker cap, root null/self/nonmember `DELETECO` refusals and worker self-deletion refusal. Both known-live workers then yield, resume to natural return, and are safely deleted, while root G54/G55, parent pointers and list linkage are checked. No arbitrary or freed pointers are passed through `CALLCO` or `RESUMECO`.

A third `CREATECO` after two registered workers exercises the known capacity-refusal path which frees temporary vectors in CO.3 source; the fixture verifies registry consistency and surviving worker operation but **does not directly measure FREEMAIN or live allocation bytes**. No general recovery from allocation failure, malformed stack frames or arbitrary invalid machine addresses is claimed.

## Host verification performed in assistant workspace

- `python3 -B -m unittest discover -s tools/coroutines -p 'test_run_co4_safe_negative.py'`: **10 PASS, 0 FAIL**. Synthetic executor PASS and FAIL cases are not MVS evidence.
- Existing `test_run_co4_bounded_stress.py`: **10 PASS, 0 FAIL** in the same isolated review workspace.
- `python3 -m py_compile` on the new runner and test module: PASS.
- New runner `--check`: PASS; the **actual complete CO.3 library, CO3DROP extension and /CN parameter bytes** were reconstructed from GitHub and matched all three exact pinned Git blob IDs. The candidate source passed its <=80-column, ASCII and oracle marker checks.
- `git diff --cached --check` on all four new code/docs files in a separate review-only local Git repository: PASS; no owner WSL repository was changed.

**Local-validation limitation:** The isolated `--check` mirror used existence-only placeholders for inherited runners and BCPLCO/BCPLMAIN source files. It did not execute those scripts, generate a real candidate IFOX deck, compile BCPL or submit JES. The independently reviewed GitHub baseline supplies those inherited files for the eventual operator `--run`. No native GO or JES outcome is inferred.

## Native evidence still required

After a guarded fast-forward to the committed source revision, the operator can run `python3 -B tools/coroutines/run-co4-safe-negative.py --run`. The inherited MVS pipeline strictly requires two Cambridge compiler jobs, four IFOX steps, IEWL, GO and JES SUCCESS/highest RC=0000 plus **exactly 16 ordered `CO4SAFE` records**. A nonzero RC or wrong record sequence is FAIL, with receipts retained separately under `workarea/co4-safe-negative/`.

This document records candidate preparation only. It does not close CO.4, start CO.5, allocate permanent globals, install runtime objects, overwrite `BOOT_OBJ`, or publish a release.
