# Stage 2B — host verification and owner-approved completion

**Project:** BCPL for MVS 3.8 Reconstruction  
**Owner evidence:** 3 November 2026 local / 4 November 2026 UTC  
**Decision:** **Stage 2B COMPLETE — accepted within the host-side suite-ownership implementation and verification scope.**  
**GitHub implementation baseline:** `d192ace00a2e43b7975e22c3ce55faa00baee6e8` (`main`).  
**Authorities:** [Stage 1 audit](repository-module-and-regression-migration-stage1-audit-20261103.md), [suite-separation design](../../architecture/regression-suite-separation-20261103.md), [Stage 2A completion](stage2a-v4-verification-and-completion-20261103.md), and [Stage 2B implementation](stage2b-manifest-implementation-20261104.md).

This is an owner-approved **repository maintenance work-package completion**, not an opening, renaming or closure of an official milestone or march. It does not revise any accepted R., T. or Q. milestone evidence. On 3 November 2026 local time the owner supplied the following WSL host-verification output and explicitly directed recording Stage 2B as complete, with approval to commit.

## Accepted operator verification

The operator ran guarded, non-fail-fast commands from the WSL repository root, then supplied their terminal output. Results reported by that output:

| Check | Result |
| --- | --- |
| `git pull --ff-only origin main` | RC=0, fast-forward to `d192ace00a2e43b7975e22c3ce55faa00baee6e8` |
| `git rev-parse HEAD` | Exactly `d192ace00a2e43b7975e22c3ce55faa00baee6e8` |
| `python3 -B -m unittest discover -s tools/checks -p 'test_stage2b_suite.py' -v` | 7 tests; OK; RC=0 |
| `tools/tests/run-suite --check` | Manifest integrity OK; RC=0 |
| `tools/tests/run-suite --list` | Four native suites and independent MR10 listing; RC=0 |
| `tools/tests/run-suite bcplqsam --list --tag integration` | Case 170 selected; RC=0 |
| `tools/bootstrap/run-regression --check-numbering` | Legacy case naming/numbering OK; RC=0 |
| `git status --short` | No output (clean working tree) |

Manifest inventory: **177 unique native cases (00–176)**, with **Bootstrap 146 (00–145), Runtime Extensions 13 (146–158), BCPLTIME 4 (159–162), and BCPLQSAM 14 (163–176)**. The MR10 panel remains independent. No case ID was renumbered, moved, or counted twice.

The seven host unit tests covered manifest/ownership coverage, invalid/duplicate entries, unsupported paths/profiles, suite and case selection, stubbed runner dispatch and isolated logging, expected case-083 SKIP, and device opt-in protection. During tests, fake runners generated PASS, SKIP and BLOCKED transcripts; those synthetic results are **not actual MVS executions**.

## Accepted implementation scope

Stage 2B delivers the four `tests/suites/*.tsv` ownership manifests, `tools/tests/run-suite` offline validation/listing and explicit profile-aware execution selection, compatible native-runner delegation, independent suite counts, run-scoped evidence logging, and an optional backward-compatible `--log-dir` in the legacy runner. Case 083 retains its expected installed-production SKIP. Cases 175–176 require explicit device opt-in; the suite runner never resumes the JES punch. All 177 physical case directories and execution fixtures remain under `bootstrap-toolchain/regression/`; legacy commands and the separate MR10 panel remain intact.

## Verification boundary and deferred gate

The owner accepts **Stage 2B completion on this bounded host-side evidence** notwithstanding the implementation note's earlier plan for native parity before final Stage 2B acceptance. The outstanding **native old-versus-new runner parity** is expressly deferred; no such parity is claimed here.

In particular, this record does **not** establish a fresh 00–176 native panel, installed/source object equivalence, BCPLQSAM installed-object verification, MVS/JES execution using `run-suite --run`, or JES printer/punch readiness. No MVS jobs, PDS writes, object promotion, operator console commands, or device-state changes were authorized by these host checks. Historical QSAM Q.5 acceptance remains **175 PASS / 1 FAIL (175) / 1 expected SKIP (083)** on the full panel, followed by a **separate successful rerun of case 175**.

## Next bounded work

**First, plan and separately authorize a native suite-runner parity campaign.** On one pinned Git revision and unchanged resident MVS object/profile baseline, compare a small set of old-wrapper runs with `tools/tests/run-suite` selections, using per-case outcome, expected output and GO RC, JCL/IEWL selection, and preserved JES/job evidence—not only aggregate counts. Include a baseline Bootstrap case, Runtime Extensions, BCPLTIME in installed R.5/T.1 profile, and source-selected BCPLQSAM; verify the expected case-083 SKIP without treating it as an executed native PASS. Exclude JES device cases 175–176 unless specifically approved. No native execution is authorized by this document.

**Then decide whether Stage 2C — optional physical test relocation — is worth its path-migration risk.** The Stage 1 proposal places physical relocation **after** parity. Relocation is optional, not an automatic consequence of Stage 2B closure. If retained in place, the next design work can instead address **Stage 3 — independent coordinated regression**; **Stage 4 — verification** requires its own target-system authority and clean-room evidence. These stage labels are maintenance work packages, not official project marches.

**Disposition:** Stage 2B host implementation and validation **COMPLETE by owner decision**; native parity **deferred and unverified**; no further source or MVS work implicitly authorized.
