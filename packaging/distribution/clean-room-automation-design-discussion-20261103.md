# Design discussion — staged automation of clean-room reconstruction

**Date:** 2026-11-03  
**Status:** Historical research proposal, superseded by the [owner-approved 4 November decision](clean-room-reconstruction-automation-decision-20261104.md). Not an implemented runner or new milestone.  
**Authority:** `docs/Rebuild-BCPL-for-MVS-from-source.md`, `config/dspal.yaml`, applicable packaging policies. The guide governs actual step order and validation until a replacement is accepted.

**Historical note (4 November 2026):** The owner chose a start-from-zero, full-purge/rebuild orchestrator with one explicit scoped approval, individually usable tools, optional WSL-console progress and separate regression testing. The checkpoint/resume approach and multiple approval gates proposed below are **not current requirements**. Retained for provenance.

## Question and finding

Can clean-room reconstruction be automated, or halted at human checkpoints? **Much of the workflow is already scriptable. A resumable stage orchestrator with mandatory checkpoints is more appropriate than an unconditional one-shot script.** This is a feasibility conclusion from the existing commands, **not** evidence of a completed unattended reconstruction.

The documented rebuild has Steps **0–10** and explicitly excludes provisioning Docker/Hercules/TK5 from scratch and building the separate **native Cambridge compiler** in `cambridge-compiler/`. It reconstructs the interpreter-hosted bootstrap toolchain, runtime, optional System Extensions, and regressions. Do not conflate this with rebuilding an eventual native Cambridge compiler.

## Candidate stage plan (guide step numbers unchanged)

| Guide step | Automation candidate | Gate / expected proof |
| --- | --- | --- |
| 0 — Check system | Preflight Git revision/cleanliness; inspect effective `dspal`, services, input availability | Confirm target host, HLQ, MVS session, Git SHA, and private settings without exposing credentials |
| 1 — Clean host work area | Invoke existing interactive `tools/clean-workarea` | Human approval for deletions and checks that tracked files were preserved |
| 2 — Rebuild managed PDS layout | Preview `purgebcpl --show-jcl`, then init and two-pass population *as ordered in the guide* | **Hard destructive checkpoint** before purge; verify dataset inventory, tracked-member counts and documented expected first-pass RC=2 **only when caused by 12 missing generated members** |
| 3–4 — Interpreter and MR10 suites | `dspal submit`, independent JES inspection, installed interpreter smoke and 3 resident suites | Verify payload versus launcher jobs, ASM/LKED codes, interpreted `CODE=0`, actual suite outputs |
| 5–6 — Prepare and build demoted Cambridge compiler | Existing `prepare-bootstrap --with-trnilrg`, generated-only population, `CAMBBLD` | Match generated hashes, second-pass RC=0, 22 phases plus PACKCOMP, ICINT `CODE=0`, installed CAMBCOMP and output assembler smoke |
| 7–8 — Runtime and BLIB | Existing JCL submitted via `dspal` | **Hard object-library installation checkpoint**, especially current `BOOT_OBJ` approval hold; verify all assembler/link/install steps, object inventory and BLIB |
| 9 — Extensions and native regression | Existing extension jobs and installed-regression runner | Per-extension object provenance and selection; analyze per-case results and known exceptional cases; never declare a full green panel from only process RC |
| 10 — Evidence | Consolidate Git SHA, inputs, job IDs, return codes, inventories, per-case results and exceptions | Human signs a completed reproducibility report; no automatic closure or production promotion |

The rebuild guide's gate describing **176 PASS, 0 FAIL, 1 expected SKIP** is a *target*, not the same as the QSAM Q.5 closure evidence: `packaging/milestones/qsam/qsam-q5-closure-20261101.md` documents a separate case-175 rerun following a full panel with one failure. An orchestrator must preserve that distinction and not silently treat the latest guide's aspirational gate as achieved.

## Proposed orchestrator behavior

- Provide `plan`, `run --through STAGE`, `resume`, `status`, and `report` concepts (names are provisional, not implemented).
- Derive dataset inventory and source mappings from the **effective** `config/dspal.yaml`; do not build a competing hard-coded set of 28 names.
- Before execution, pin Git SHA and manifest hashes; fail on unexpected dirty checkout, changed config or wrong target system.
- Journal start/end, command arguments (redacting secrets), launcher **and payload** job IDs, observed evidence and a durable per-stage outcome in an ignored workarea path.
- Separate **execution** success, **validation** success, and **approval**. Checkpoints should not be bypassable through a generic `--yes` flag, especially for purge or permanent-object writes.
- Explicitly model acceptable nonzero codes such as the guide's first-pass populate RC=2; do not use shell fail-fast (`set -e`, `set -u`, `pipefail`) or unconditional `&&` chains for the runbook. Stop through explicit checks and logs.
- On interruption, `resume` must recheck real PDS/JES state; never assume that a killed host command rolled back MVS writes. Re-execution of non-idempotent steps should be reviewed, not automatic.
- Support read-only plan/static validation first, optional independent stage approvals second, and only consider unattended execution of proven *nondestructive* stages afterward.
- Keep GitHub authoritative and JES/IFOX/IEWL/actual MVS programs authoritative for execution evidence.

## Research gaps and validation

1. Determine exactly which current scripts return machine-readable job IDs, per-step RCs and interpreted status; build adapters where needed without parsing brittle free-form summaries.
2. Document partial-write recovery for `initbcpl`, `populate`, `CAMBBLD`, `BLDBMAIN`, `BLIBBLD` and extension installation.
3. Establish explicit promotion/overwrite limits and whether clean-room testing should use isolated MVS/DASD images by default.
4. Verify end-to-end stage replay in a disposable MVS installation; conduct a deliberate interruption/resume rehearsal.
5. Keep the target definition clear: interpreter-hosted bootstrap clean-room first; native Cambridge compiler rebuild later as a distinct, approved extension of the workflow.

**Recommendation:** first implement a **read-only preflight/checkpoint planner**, then stage-by-stage execution with operator confirmation and evidence capture. Do not remove existing interactive safety controls or automatically assert acceptance.

## References

- `docs/Rebuild-BCPL-for-MVS-from-source.md`.
- `tools/datasets/README.md`, `tools/bootstrap/README.md`, `tools/mvs/README.md`.
- `packaging/operations/operator-wsl-command-policy.md`, `packaging/operations/git-mvs-authority.md`.
- `packaging/milestones/qsam/qsam-q5-closure-20261101.md`.
