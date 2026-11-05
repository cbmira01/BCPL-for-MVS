# Decision — clean-room reconstruction automation

**Project:** BCPL for MVS 3.8 Reconstruction  
**Decision date:** 4 November 2026  
**Status:** Owner-approved design direction; automation not yet implemented or MVS-verified  
**Authority:** GitHub `main` for source and documentation, and actual MVS 3.8J / IFOX / IEWL / JES evidence for build results.

This decision replaces the checkpoint/resume design recommended in the [3 November proposal](clean-room-automation-design-discussion-20261103.md). It does not create or renumber a milestone or march; it does not authorize an actual MVS write or JES job.

## Project engineering goals and workflow separation

At all times the project should remain easy to **modify**, **reconstruct from scratch**, **test at any useful level**, and **produce a release**.

Three independent but coordinated workflows serve those goals:

| Workflow | Purpose | Typical timing |
| --- | --- | --- |
| Testing | Individual checks, selected cases, suites or whole-project regression | Whenever needed during development |
| Reconstruction | Prove the agreed sources reproduce a coherent managed system, destroying obsolete development outputs | End of a development cycle |
| Release | Deliberately package, verify an independent installation and publish an accepted baseline | Only by separate owner decision |

Reconstruction will not automatically run MR10 resident regression suites, native regression suites, or the project regression coordinator. It *will* retain the necessary build-result checks and minimal smoke executions that prove the newly built interpreter and compiler actually work. The dedicated testing workflow supplies broader regression evidence for subsequent baseline acceptance.

A successful reconstruction does not automatically become an accepted baseline, receive a `buildable/` tag, or become a release. An annotated GitHub baseline tag is permitted **only** when the owner explicitly accepts a reconstruction as a project baseline; tags and release publication are never side effects of the reconstruction runner.

## Repeatability rather than resumability

**Every attempt starts from zero.** After an interruption or failed run, restart the whole automation, discard the previous managed build outputs, and rebuild from the chosen Git commit and configuration.

- No persistent completion checkpoints, reconciliation framework, `resume` mechanism, or automatic skip of prior completed stages.
- No reuse of old generated INTCODE, relocatable objects, load modules or host files to fill gaps.
- Preserve execution reports for diagnosis, **not** to determine resume positions.
- Fresh review and fresh approval on each attempt; earlier approval does not carry forward.
- If interrupted MVS/JES work might still be writing target datasets, stop before a new purge until that work has ceased. This is a basic safety preflight, not recovery of old stages.

This is *whole-run idempotence*: reexecuting the full purge/rebuild from the same authoritative inputs must converge on the same intended system. Individual partially completed MVS jobs do not have to be reentrant or safely repeatable without a purge.

The destructive scope is **only** the project-managed datasets selected by the effective `config/dspal.yaml`, plus expressly listed disposable host-generated paths. Never erase unrelated or system MVS datasets, Hercules/TK5 system state, Git source, private credentials or `config/dspal.local.yaml`. Derive the managed dataset inventory from configuration rather than hard-coding its current size.

## One operator authorization for the entire run

1. **Preflight (read-only).** Report Git SHA, unexpected working-tree changes, source/dependency availability, effective `dspal` configuration, MVS identity/HLQ, and environment readiness.
2. **Plan/dry-run (read-only).** Show what will be deleted and rebuilt: exact host paths, datasets, allocations, both population passes, JCL/build operations and accepted object-library writes. No JES submission or file/dataset mutation.
3. **One explicit operator acknowledgment.** The operator approves this entire displayed *target, source revision and destructive/reconstruction scope*. This also covers subsequent listed `BOOT_OBJ` and `EXT_OBJ` installation writes; no recurring prompt for each planned operation. Unexpected/out-of-scope destructive actions stop for separate review. A commit is not installation authorization.
4. **Clean and rebuild.** Execute the complete approved sequence without further routine prompts.
5. **Report.** Record actual actions, evidence, omitted steps and failure reasons; do not silently declare acceptance.

The orchestrator should **call existing tools**, not reimplement them; individual tools must stay independently executable with their normal standalone prompts and guards. If automation needs a noninteractive approval interface to those tools, design it to be restricted to the one reviewed scope. Do **not** silently pipe `YES`/`DELETE` into existing prompts or introduce a blanket unsafe bypass.

## Build sequence and verification

Maintain the present [reconstruction guide's](../../docs/Rebuild-BCPL-for-MVS-from-source.md) **Steps 0–10** as reference points; do not invent new milestone/march numbers. The initial automated target is the interpreter-hosted bootstrap chain, Core Runtime, historical Base Library and currently managed System Extensions. The separate *native Cambridge compiler* in `cambridge-compiler/` is excluded until a future decision. Docker/Hercules/TK5 provisioning is a prerequisite.

Within that scope, reuse the manual, separately callable tools in dependency order:

1. Preflight, preview/approval, `tools/clean-workarea`, then `dspal` project PDS purge, initialization and first tracked-source population.
2. Assemble/link/install `ICINT19`, verify MVS members and execute a minimal installed-interpreter smoke test.
3. Run `prepare-bootstrap --with-trnilrg`, generate the demoted Cambridge inputs, then perform the generated-only `dspal` population.
4. Build `CAMBCOMP`; check the interpreted compiler succeeds and emits native System/370 assembler.
5. Build the Core Runtime, compile and assemble `BLIB`, then build/install the selected optional System Extensions.
6. Verify final member inventories and actual MVS results, then write the reconstruction report. Do not launch the manual guide's MR10 suite section (Step 4) or separate project regression section (part of Step 9).

Keep the two-pass `dspal` contract: the first population may return **RC=2** only for the precisely expected missing generated inputs **after successful tracked-source installation**; the second generated-only pass must succeed. Inspect **payload** rather than launcher JES jobs, assembler and linkage RC/severity, interpreter `CODE=0`, resulting PDS members and MVS program behavior. Do not substitute a previously installed object for a failed new build.

## Console experience, failure, and evidence

- Support optional live **WSL-console progress**, similar to the project regression runner: named steps, operation names, relevant commands, JES launcher/payload IDs and RCs, and concise PASS/FAIL summaries. Keep full output available in logs.
- On a failed required operation, **stop** with a clear error and evidence. Do not automatically resume, retry, proceed to dependent operations or pretend a partially installed build is complete.
- Store output and logs **outside paths erased by host cleanup** so evidence survives interruptions. Logs are not checkpoints; protect credentials and local secrets.
- Honor [operator WSL command policy](../operations/operator-wsl-command-policy.md): no fail-fast shell options in operator-pasted commands, explicit dependency gating and return-code reporting, and a usable WSL interactive shell after failure.
- Never combine reconstruction with tags, candidate promotion outside the approved scope, distribution tape creation, release publication or full regression execution.

Names such as `plan`, `--dry-run`, `run`, `--progress` and `report` are **possible interfaces only**, not implemented commands.

## Implementation and acceptance

First implement read-only preflight and a reviewable plan. Adapt existing tools carefully for one narrowly scoped authorization while retaining standalone safety. Add simple sequential orchestration, progress and preserved logs. Test a complete fresh rebuild, plus interruption followed by an entirely new rebuild, against a disposable MVS installation. Confirm outputs and run independent regression checks when deciding whether the resulting revision deserves acceptance as a baseline.

The [current manual guide](../../docs/Rebuild-BCPL-for-MVS-from-source.md) remains operationally authoritative until an automated replacement is implemented and accepted. Its existing approval holds, historical evidence and milestones are unaffected by this design decision.
