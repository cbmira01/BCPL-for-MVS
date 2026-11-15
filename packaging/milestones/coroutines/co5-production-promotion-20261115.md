# CO.5 — Production coroutine promotion

**Project:** BCPL for MVS 3.8 Reconstruction
**Milestone:** Implement coroutine support for native compiler
**March:** CO.5 — Integration, Regression, and Release
**Decision date:** 15 November 2026
**Owner decision:** Promote complete qualified native coroutine support;
allocate G!289–300 permanently; defer `config/dspal.yaml` changes
**Status:** Git source and installation JCL prepared; MVS installation
and installed-object verification not yet reported

## Accepted functionality and architectural bounds

Production means the **qualified** CO.2–CO.4 implementation: a root
and up to two live workers, independent checked S1 stacks with
`CREATECO(FN,1024)`, worker/parent transfers, normal return,
root-controlled deletion of a known-live inactive worker, and
revocation before storage reclamation. This is not a general
reentrant coroutine engine. Actual GETMAIN exhaustion, arbitrary
stale pointers, ABA-safe handles, exceptional abend recovery, more
workers, preemption and multitasking are not accepted.

The private 24-word descriptor representation remains an
implementation detail, not an ABI promise.

## Production modules and authoritative code

| Source-controlled file | MVS staging member | Production object |
| --- | --- | --- |
| `bootstrap-toolchain/asm/bcplmain.asm` | `BOOT_ASM(BCPLMAIN)` | `BOOT_OBJ(BCPLMAIN)`, rebuilt through existing `BLDBMAIN` |
| `bootstrap-toolchain/asm/bcplco-production.asm` | `BOOT_ASM(BCPLCO)` | `BOOT_OBJ(BCPLCO)` |
| `bootstrap-toolchain/library/coroutines.bcpl` | `BOOT_SOURCE(COROUTIN)` | Separately compiled `BOOT_OBJ(COROUTIN)` |
| `bootstrap-toolchain/library/coroutines.h` | `BOOT_SOURCE(COHDR)` | Declarations, not object code |
| `bootstrap-toolchain/jcl/bldcorco.jcl` | `BOOT_JCL(BLDCORCO)` | IFOX, install, readback, IEBCOMPR |
| `bootstrap-toolchain/jcl/bldcorlb.jcl` | `BOOT_JCL(BLDCORLB)` | IFOX, install, readback, IEBCOMPR |

The production `BCPLCO` combines the accepted CO.2 switch and
accepted CO.3 `CO3DROP` registry revocation. The original CO.2
candidate `bootstrap-toolchain/asm/bcplco.asm` is unchanged
for historical regression reproducibility. The production BCPL
library's executable body is identical to the accepted CO.3
`co3-delete-reuse/library.bcpl` after two commentary lines.
`BCPLMAIN` exports its existing `STKLIM` symbol for the
installed runtime's link-edit; the CO.1/CO.2 development runners
accept the already-exported symbol without adding a duplicate.

G!289–294 designate the six BCPL callable functions
(`CO3INIT`, `CREATECO`, `DELETECO`, `CALLCO`, `COWAIT`,
`RESUMECO`). G!295–297 are the BCPL lifecycle state words
(`CO3CURR`, `CO3ROOT`, `CO3LIST`). G!298–300 are the IFOX
entry points (`CO2INIT`, `CHANGECO`, `CO3DROP`). These names
and numbers are permanently assigned in the Global Number Registry.
A `GLOBAL` declaration, link-editor inclusion, and per-executable
global-vector address registration are distinct actions. They must
all occur for a particular application to call the library.

## Before MVS submission: host-only validation

```sh
python3 -B -m unittest discover -s tools/checks \
    -p 'test_co5_production_coroutines.py' -v
python3 -B tools/coroutines/prepare-production-library.py --check
python3 -B tools/coroutines/verify-installed-production.py --check
tools/tests/run-suite --check
tools/tests/run-project-regressions --check
```

Require zero RC from every check. Preserve original native
regression identities 00–189 and golden-output contracts.

## Source compilation and manual staging

Use an exact Git revision, a working TK5/MVS installation, and
the authenticated `dspal` environment. These are **intentional**
persistent writes to the managed MVS PDS; the owner authorized
promotion, but Git remains authoritative.

```sh
mkdir -p workarea/co5-production
tools/bootstrap/compile-mvs \
    bootstrap-toolchain/library/coroutines.bcpl \
    --job-name COPRLCMP \
    --cambridge-parm \
      packaging/milestones/coroutines/candidates/co3-delete-reuse/cambridge-parm.txt \
    --output workarea/co5-production/coroutines-generated.asm

python3 -B tools/coroutines/prepare-production-library.py \
    --compiled workarea/co5-production/coroutines-generated.asm \
    --output workarea/co5-production/coroutin-prepared.asm

tools/datasets/dspal put BOOT_ASM BCPLMAIN \
    bootstrap-toolchain/asm/bcplmain.asm
tools/datasets/dspal put BOOT_ASM BCPLCO \
    bootstrap-toolchain/asm/bcplco-production.asm
tools/datasets/dspal put BOOT_SOURCE COROUTIN \
    bootstrap-toolchain/library/coroutines.bcpl
tools/datasets/dspal put BOOT_SOURCE COHDR \
    bootstrap-toolchain/library/coroutines.h
tools/datasets/dspal put BOOT_ASM COROUTIN \
    workarea/co5-production/coroutin-prepared.asm
tools/datasets/dspal put BOOT_JCL BLDCORCO \
    bootstrap-toolchain/jcl/bldcorco.jcl
tools/datasets/dspal put BOOT_JCL BLDCORLB \
    bootstrap-toolchain/jcl/bldcorlb.jcl
```

**Do not proceed if any compilation/preparation/put fails.**
The operator commands should be executed in a revision-guarded
and RC-checked shell sequence, not pasted as an unconditional
chain when running a real production installation.

## Production installation and independent verification

After staging, submit in order:

```sh
tools/datasets/dspal submit BOOT_JCL BLDBMAIN
tools/datasets/dspal submit BOOT_JCL BLDCORCO
tools/datasets/dspal submit BOOT_JCL BLDCORLB
tools/datasets/dspal ls BOOT_OBJ
python3 -B tools/coroutines/verify-installed-production.py --run
```

Require `BLDBMAIN` seven IFOX and seven IEBGENER steps, all
RC=0000, severity 0. Each `BLDCOR*` job must report exactly
four successful steps: IFOX, persistent IEBGENER install,
independent IEBGENER readback, and IEBCOMPR (binary identity).
`BOOT_OBJ` should contain the previous eight accepted members
plus `BCPLCO` and `COROUTIN`.

The installed verification runner compiles **only the accepted
CO.3 delete/reuse application**, links the **installed**
`BOOT_OBJ(BCPLMAIN)`, `BOOT_OBJ(BCPLCO)` and
`BOOT_OBJ(COROUTIN)` objects with other installed runtime
members via IEWL, then executes native GO. Its mandatory evidence:
one Cambridge compile job, one native job, IFOX/IEWL/GO
RC=0000 and the exact 21 ordered accepted `CO3BCPL` records.
The runner does not modify MVS object members.

Afterward rerun native coroutine regression 177–189 and applicable
project suites. The known incompatible original MR10 fixed-stack
probe remains FAIL under the documented CO.0 qualification;
SKIP 083 and BCPLQSAM device cases 175–176 retain their
independent status/authorization.

## Manifest deferral and important limitation

The owner explicitly deferred the `config/dspal.yaml` mappings.
Therefore a subsequent `tools/reconstruction/rebuild-from-source
--unattended --batch-populate` will **purge the manually staged
coroutine MVS members and installed objects** and will **not**
recreate them. Do not claim end-to-end clean-room reconstruction of
the *promoted* coroutine objects until the manifest and clean-room
driver are updated and the new build passes on the target.

Record jobs, IFOX severity, IEWL map, IEBCOMPR receipts,
application oracle, source revision, and any exceptional limits.
Release publication and formal CO.5 closure remain distinct
owner acceptance gates.
