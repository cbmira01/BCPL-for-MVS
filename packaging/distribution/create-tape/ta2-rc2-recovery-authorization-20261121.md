# TA.2 — Owner-approved new conditional pre-stateful BC0002 attempt

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone:** Tape artifact release  
**March:** TA.2 — Manifest-Driven Tape Producer  
**Date:** 21 November 2026 EST  
**Status:** **One new conditional private attempt authorized; no AWS write yet reported.**

The owner explicitly approved a new attempt following the bounded original `BC0002` existing-media preflight refusal. This authorization applies **only** to a new, operator-confirmed private candidate build for `BCPL-0.1.0-rc2`, using reserved VOLSER `BC0002`, image `mvs-state/tape/bcpl-0.1.0-rc2-BC0002.aws`, Hercules device `0480`, and unchanged one-job, 21-position `TA2RC2WR` JCL with SHA-256 `85eca6f3e1e83c2d0e476f24870a20664bde2a50e2de8653606bfa351af54b4f`.

The committed `ta2-rc2-prestateful-recovery-approval.json` binds the original immutable evidence path `workarea/ta2-rc2-production-operations/20261121T145906Z-26113`, the originally inspected scratch image `bcpl-objtest-20261108-01.aws`, and the condition that **no earlier write-attempt marker or candidate image was created**. These conditions are **not asserted as independently verified**: the owner-local preserved evidence must be replayed and both original marker and candidate-image absence independently checked before any new operation. A true `BC0002` VOL1 collision must stop the attempt.

The producer now **unconditionally** replays the original SHA256-sealed failure evidence before trusting the new Git-committed recovery authorization. Missing, changed or incomplete original evidence cannot bypass the gate using the prior media-write approval. It then verifies canonical source manifest/registry, all accepted staged inputs, new image and VOLSER uniqueness across existing media, fresh MVS catalog absence and tape-device readiness. No accepted staging operation is repeated.

If every gate passes, the operator still must explicitly type `INIT MOUNT WRITE BC0002 21`, then `SUBMIT TA2RC2WR BC0002`. The one-shot marker is created before HETINIT, mount and JES submission. On any partial or ambiguous failure, preserve the resulting media and evidence, **do not retry**.

**Offline verification:** Python AST and all **74/74 focused rc2 synthetic/negative tests passed** in the assistant repository workspace. The exact new JSON approval passed the producer's `verify_recovery_approval` contract. The tests include refusal if the prior incident disappears. This is not a claim of successful MVS execution.

Scope remains private AWS initialization/mount and one MVS write only. No automatic retry, media overwrite, clean-target installation, publication, or source-rights clearance is authorized. Historical-source lexical compatibility and native Cambridge Compiler completeness remain qualified.

See [original refusal and parser correction](ta2-rc2-prestateful-halt-analysis-20261121.md) and [original private-write boundary](ta2-rc2-private-build-authorization-20261121.md). **TA.2 remains IN PROGRESS**, pending actual MVS/JES and independent HETMAP evidence.
