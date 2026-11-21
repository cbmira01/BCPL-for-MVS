# TA.2 — rc2 producer preview, not a tape write

**Date:** 21 November 2026 EST  
**March:** TA.2 — Manifest-Driven Tape Producer  
**State:** Host-side deterministic, JOB-less preview only; candidate-media operation NOT authorized.

The owner-provided real MVS results for BT0021 are recorded in [the qualified stage acceptance](ta2-bt0021-qualified-acceptance-20261121.md). The earlier BT0001–BT0020 acceptance remains unchanged.

`scripts/ta2-rc2-producer-preview` reads the committed **BCPL-0.1.0-rc1** and **BCPL-0.1.0-rc2** manifests, the canonical `config/dspal.yaml`, historical source selection, and the sole release registry. It invokes the existing `compiler-source/successor-contract.py` release identity/hash/selection check and the existing `scripts/ta2-offline.render_write_jcl` generator. It does **not** introduce another JCL transport grammar or a second release identity.

The wrapper supplies ephemeral producer source dataset identities `HERC02.BCPL.TA2STG.BT0001` through `BT0021` to an **in-memory copy** of the manifest. It supplies the accepted four BT0002 installer members, keeps the original 20 rc1 release rows byte-for-byte equivalent in their parsed meaning, and checks the added historical-only fifteenth-member payload. It validates the expected **21 tape-label positions**, **one IEBGENER step**, **20 IEBCOPY steps** and **146 SELECT MEMBER cards**. The rc2 manifest and release registry are not altered.

By default it prints a compact one-line PASS/refusal and a reminder that no MVS operation is authorized. Its optional `--output workarea/<new-file>` writes only a new **JOB-less**, noncredentialed JCL preview under ignored repository `workarea/`, never a submitted JES job or AWS tape.

**Assistant-workspace tests:** Python syntax validation and 8/8 synthetic success/refusal tests passed. Tests exercise the 21 positions, exact stage DSNs, original-manifest immutability, member counts, altered rc1 selections, duplicate members, incorrect DCB, rights qualification, absent native compiler requirement, and malformed renderer output. The canonical renderer already exists; no real MVS write was made or tested by this wrapper.

The preview **does not complete** the production gate: fresh saved MVS staged-input evidence binding, release-rights/provenance clearance, exact media file and drive selection, collision-free AWS creation, a durable one-shot intent gate, JES/IEBCOPY execution, independent standard-label/filemark readback, restored-member validation and clean-target installation are still separate work. Any write runner must fail closed if these inputs/approvals are missing. TA.2 remains IN PROGRESS.
