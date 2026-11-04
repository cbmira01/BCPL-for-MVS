# Stage 2B — native suite ownership implementation (host-side candidate)

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 4 November 2026 UTC  
**Authority:** [Stage 1 audit](repository-module-and-regression-migration-stage1-audit-20261103.md), [suite architecture](../../architecture/regression-suite-separation-20261103.md), [Stage 2A completion](stage2a-v4-verification-and-completion-20261103.md)  
**Scope:** Owner-approved Stage 2B implementation, on GitHub `main`; **native MVS parity not yet performed or authorized by this commit**.

## Change and compatibility contract

- Root `tests/` has four stable-ID, explicit TSV manifests: Bootstrap 00–145 (146), Runtime Extensions 146–158 (13), BCPLTIME 159–162 (4), BCPLQSAM 163–176 (14): **177 unique cases, no renumbering and no case moves**.
- `tools/tests/run-suite` validates case identity/fixture markers; supports offline `--list`/`--check`, case and tag selection, explicit `production` and `installed-r5-t1` execution profiles, and independent suite PASS/FAIL/SKIP/BLOCKED totals.
- The new runner delegates execution to existing production and installed R.5/T.1 wrappers and preserves source-selected BCPLQSAM for cases 163–176. MR10 remains independent and unmodified.
- A backward-compatible `--log-dir` option in `tools/bootstrap/run-regression` gives the suite runner run-scoped logs without changing the legacy default path or R.1 special-purpose policy.
- JES device cases 175–176 are blocked absent explicit `--allow-device`; inherited `Q4_PUNCH_RESUME` is removed in suite execution. Case 083 is the existing expected production SKIP. No automated JES2 console action is added.
- No BCPL source, MVS assembler, JCL, permanent MVS objects/datasets, official R./T./Q. numbering, or accepted closure records change. `bootstrap-toolchain/regression/` still owns all 177 physical test cases.

## Verification boundary

Host-only verification includes Python syntax/unit tests for the new parser,
manifest uniqueness and exact case coverage, rejection of malformed identities,
fixture markers and unsupported profiles, selection, dispatch via **stub** native
runners, run-scoped output, expected case 083 SKIP, and JES 175–176 blocking.
Static manifest checks compare exact case directories and immutable profile
classification on the current Git tree. Any actual MVS/JES submission, installed
object readback, native output parity or complete-suite acceptance is a **later
and separately approved verification gate**. Do not claim Stage 2B native
acceptance from static checks alone.

## Next verification

After WSL pulls the implementation commit, run offline checks and examine
`run-suite --check`, `--list`, and manifest case assignments. Only then propose
a bounded, separately approved native parity campaign: compare representative
old command vs suite selection on the same resident environment, including
negative selection, installed R.5/T.1, and source-selected BCPLQSAM. Explicitly
defer JES punch/printer cases until authorized. A successful host-side commit
is not the final Stage 2B native parity acceptance.
