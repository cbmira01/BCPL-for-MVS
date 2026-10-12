# EXEC PARM G39 — BCPLMAIN-only production-object promotion

**State:** Generator change committed; no TK5 installation performed by ChatGPT. Source-runtime regression 108 passed in user report after commit `57ec6e1`. Production runtime remains unverified until operator-run steps below.

The `--only-main` mode of `tools/checks/prepare-runtime-object-library.py` performs the existing BCPLBYTE, BCPLAPT, and BCPLMEM externalization transforms and existing BLIB registration transform **to produce BCPLMAIN source only**. It then emits a JCL deck containing **AMAIN IFOX00** and **IMAIN IEBGENER** steps exclusively. It never installs/rebuilds BCPLBYTE, BCPLAPT, BCPLMEM, or BLIB. The IMAIN step is conditioned on AMAIN RC=0000. Failure during IEBGENER replacement remains non-atomic; protect the current member according to the site's backup practices.

## Gate A — prepare (no MVS changes)

From repo root:

```sh
git pull --ff-only
python3 tools/checks/check-bcplmain-modules.py
python3 tools/checks/prepare-runtime-object-library.py \
  --only-main --output-dir workarea/runtime-object-library
```

Inspect `workarea/runtime-object-library/build-runtime-objects.jcl` locally for **only** AMAIN, IMAIN, and destination `HERC02.BCPL.OBJ(BCPLMAIN)`; review generated `bcplmain-object.asm`. The generated JCL can contain a batch password from local dspal configuration: **do not post or commit it**. Recheck the existing OBJ PDS/member and preserve the old object according to operational procedure.

## Gate B — operator submission and job checks

Only after reviewing and safeguarding the existing object:

```sh
tools/submit-jcl workarea/runtime-object-library/build-runtime-objects.jcl
# Use the actual JOB number printed by submit-jcl:
tools/job-summary <job-number>
```

Require AMAIN RC=0000 and IMAIN RC=0000. Do not run installed-object acceptance if either step fails. Remove the credential-bearing generated JCL after use.

## Gate C — installed runtime execution

```sh
BCPL_RUNTIME_PDS=1 tools/run-native-regression 108 --show-output
python3 tools/checks/run-runtime-pds-acceptance.py
tools/run-native-regression
```

Installed regression 108 must read GO `PARM='P'` while the independent BCPIN DD contains `X`, and produce `P`. Installed-object acceptance must report 119/119, excluding instrumented 083 by design. The default regression suite should still pass its 120-test panel (regression 083 uses its special source instrumentation).

If 108 fails, do **not** infer implementation success from earlier source-runtime testing. Capture the GO/IEWL report, keep other runtime members intact, and diagnose against the current installed BCPLMAIN member.

## Architectural scope

This release modifies **G39 FINDPARM** and stream support; **G45 PARMS is not initialized**. No additional runtime module or PDS member is introduced. Later modularization of machine-dependent parameter services may follow a tested interface contract rather than preceding validation.
