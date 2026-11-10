# BCPLQSAM sixteen-handle regression helper dependency — containment and extraction proposal

**Project:** BCPL for MVS 3.8 Reconstruction  
**Date:** 9 November 2026 (US Eastern)  
**Status:** Immediate broken-path correction implemented; shared-helper extraction **PROPOSED, NOT APPROVED**  
**Authority:** GitHub `main`. This maintenance record does not change Milestone QSAM or reopen its owner-closed Q.0–Q.5 marches.

## Incident and verified cause

An owner-run non-batched clean-room rebuild at `b41426d8a23fda67df59e3a2f3f52b8929f75793`
completed. The subsequently run six-suite project regression campaign failed
**BCPLQSAM cases 166 (`qsam-sixteen-finish`) and 167 (`qsam-sixteen-stop`)**,
while other BCPLQSAM cases passed. An independent focused repeat at
`73c7d37585ed974881d655b4313b9289774dc0e5` failed both again.

The focused logs establish that the demoted Cambridge compiler generated
assembler successfully (RG166C/RG167C RC=0), but native QSAM job
construction stopped with `FileNotFoundError` for:

```text
bootstrap-toolchain/probes/q0-qsam-dasd-probes/make-jobs.py
```

The existing import chain is:

```text
tools/checks/run-q2-qsam-regression.py
  -> system-extensions/bcplqsam/prepare-q1-campaign.py
  -> system-extensions/bcplqsam/prepare-q1-3dd.py
  -> bootstrap-toolchain/probes/q0-qsam-16-dcb-probes/make-jobs.py
  -> Q.0 DASD assembler/link-step helper
```

The helper's current Git location is
`packaging/archive/qsam/probes/q0-qsam-dasd-probes/make-jobs.py`.
The live 16-DCB generator still pointed to its earlier sibling location
under `bootstrap-toolchain/probes/`. This is a **repository-path dependency
failure before native Q16FIN/Q16STP job submission**, not evidence of a
QSAMSVC runtime, IFOX, IEWL, FINISH, or STOP defect. Do not convert either
failed regression result into a PASS until fresh MVS evidence exists.

## Immediate containment implemented with this record

Update only the `BASE` reference in
`bootstrap-toolchain/probes/q0-qsam-16-dcb-probes/make-jobs.py` to the
existing archived helper path relative to repository `ROOT`. Do not
copy, rename, rewrite, or execute the archived experiment for this fix.
Retain the original temporary-data JCL generators and all native
QSAM/source/ABI contracts unchanged.

Add `tools/checks/test_qsam_active_probe_dependency.py`, a **host-only**
guard that resolves and imports the real helper, checks synthetic
3- and 16-DCB deck generation, and exercises the Q.0/three-DD/Q.1
`--check` paths without credentials or JES. This prevents a repeat
of silent, mock-only test success while a real generator import is missing.

This change repairs path resolution; it does **not** establish that
cases 166/167 have passed on MVS after repair. Running or authorizing
native regression remains a distinct operator decision.

## Proposed durable design — owner review required

The active regression harness should not rely on `packaging/archive/`
for imported executable Python. The archive is for historical Q.0
experiment custody, not the active implementation dependency tree.

Propose, without implementing here:

1. Extract the **pure, stable JCL construction helpers** currently
   consumed from the archived Q.0 DASD generator—at least
   `asm_step` and `link_step`—to an active source-owned module,
   provisionally under `tools/mvs/`. Confirm the final name and API
   through a design review; no new public interface is accepted yet.
2. Update the active Q.0 16-DCB fixture and dependent Q.1 native JCL
   generators to import that module directly. Keep the archived
   historical generator and research sources intact. Avoid duplicating
   slightly different IFOX/IEWL card recipes.
3. Preserve exact IFOX/IEWL parameters, DD allocations, temporary
   `DISP` behavior, card column limits, entry symbols, the
   `REGION=256K` native GO contract, and cases 166/167's expected
   FINISH/STOP behavior.
4. Add offline old/new **byte-for-byte JCL parity checks** for
   representative 3- and 16-DCB builds, plus failure tests for a
   missing active helper. Audit any remaining active imports or
   references into `packaging/archive/` before removing the temporary
   archived-path compatibility dependency.

There is no approved implementation schedule or new milestone/march.
A future helper extraction must be discussed and approved separately.

## Verification and acceptance gates

**Host-only verification after updating WSL `main`:**

```sh
python3 -B -m unittest discover -s tools/checks \
    -p 'test_qsam_active_probe_dependency.py' -v
python3 -B -m unittest discover -s system-extensions/bcplqsam \
    -p 'test_prepare_q1_*.py' -v
python3 -B system-extensions/bcplqsam/prepare-q1-campaign.py --check
```

Only after those checks pass and the operator separately authorizes JES
submissions, repeat the focused native tests:

```sh
tools/tests/run-suite bcplqsam --run --profile installed-r5-t1 \
    --case 166 --case 167
```

Case **166** requires expected GO RC=0000 and its exact FINISH marker.
Case **167** requires expected GO RC=0008 and its exact STOP marker.
Both require IFOX highest severity zero, required native steps, and
matching MVS/JES evidence. Preserve `workarea/test-suites/` and
`workarea/native-regression/` evidence; do not discard the failed logs
or claim full-project regression acceptance from a focused PASS.

**Safety:** The host-only commands submit no JES jobs and do not modify
MVS datasets. The focused native runner submits new JES jobs, using
temporary test datasets; it is **not** authorization to rebuild MVS,
install objects or begin the full regression campaign.
