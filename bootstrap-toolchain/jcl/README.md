# Native MVS JCL — canonical builds

`config/dspal.yaml` maps **one canonical Git `.jcl` file to each
same-named `BOOT_JCL` PDS member**. Filenames are lowercase; MVS
member names are uppercase, each within the eight-character limit.

| Git JCL file | PDS member | Role |
|---|---|---|
| `cambbld.jcl` | CAMBBLD | Rebuild demoted Cambridge compiler INTCODE |
| `cg370db.jcl` | CG370DB | Optional diagnostic compiler image |
| `blibbld.jcl` | BLIBBLD | Build BLIB into production BOOT_OBJ |
| `bldbmain.jcl` | BLDBMAIN | Build all five canonical runtime modules into BOOT_OBJ |
| `blddeva.jcl` | BLDDEVA | Development BCPLAPT object |
| `blddevb.jcl` | BLDDEVB | Development BCPLBYTE object |
| `blddevi.jcl` | BLDDEVI | Development BCPLIO object |
| `blddevm.jcl` | BLDDEVM | Development BCPLMEM object |
| `blddevn.jcl` | BLDDEVN | Development BCPLMAIN object |
| `blddevl.jcl` | BLDDEVL | Development BLIB object |

`dspal populate BOOT_JCL` installs the ten tracked job *bodies*.
They do not execute until submitted. Use `dspal submit BOOT_JCL
<MEMBER>` only after checking the job's source/output datasets and
whether its target is BOOT_OBJ or BOOT_DEVOBJ.

## Current clean-room production rebuild

The owner authorized a fresh source rebuild of all project-managed PDSes
and installation of the latest runtime into `BOOT_OBJ`.
`BLDBMAIN` now assembles and installs `BCPLMAIN`, `BCPLMEM`,
`BCPLBYTE`, `BCPLAPT` and `BCPLIO` from the five canonical
`BOOT_ASM` members. `BLIBBLD` separately compiles and installs
`BLIB` into `BOOT_OBJ` using the rebuilt resident Cambridge
compiler. The target is a complete **six-member BOOT_OBJ** without
any binary copying or DEVOBJ seeding.

Each BLDBMAIN assembler and install is gated on zero return codes.
The job is not atomic: inspect every payload step before accepting
the output. Build from a freshly purged/initialized PDS environment
using the [current clean-room runbook](../../packaging/clean-room-mvs-reconstruction.md).
The all-OBJ full-panel runner is `tools/native/run-production-regression`.

`BLDDEV*` jobs remain available for later isolated experiments,
but are **not required** by the full production reconstruction.

## Historical builds, probes and source names

Useful earlier D6/D7 reproducibility decks are isolated under
[`history/`](history/), **not manifest-mapped**. In particular,
`history/build-dev-bcplm6.jcl` can be explicitly staged as
`BOOT_JCL(BLDDEVM6)` to build canonical
`BOOT_ASM(BCPLMAIN)` into historical
`BOOT_DEVOBJ(BCPLM6)`. That object-member name remains relevant
to the accepted 145-pass BCPLIO regression profile.

The obsolete `BLIBLINK` consumer, `BLDGFMEM` standalone job and
`SEEDDEV` binary-copy job are removed from the manifest. The
first and third are retired from the working tree; the
single-member F1 job remains only in history.
Other one-off D3–D5 link/assemble decks and test probes were retired;
Git history retains them. Do not assume `dspal populate` deletes
previously installed but now-unmapped members in MVS.

## Verification

```sh
python3 tools/checks/check-native-jcl-manifest.py
tools/datasets/dspal populate BOOT_JCL --dry-run
```

This check only validates source layout and manifest agreement.
It does not assemble programs, execute jobs, or verify MVS runtime
compatibility.
