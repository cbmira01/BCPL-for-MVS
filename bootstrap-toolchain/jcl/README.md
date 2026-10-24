# Native MVS JCL — canonical builds

`config/dspal.yaml` maps one Git-controlled JCL job body to each
same-named member of `BOOT_JCL`. Git filenames are lowercase and
MVS member names are uppercase (maximum eight characters). The
`dspal submit` command generates authenticated JOB cards; stored
job bodies must not contain credentials.

| Git JCL file | `BOOT_JCL` member | Purpose |
| --- | --- | --- |
| `blibbld.jcl` | `BLIBBLD` | Build Base Library `BLIB` into `BOOT_OBJ` |
| `bldbmain.jcl` | `BLDBMAIN` | Assemble/install six Core Runtime objects and the empty `BCPLREG` table |
| `blddeva.jcl` | `BLDDEVA` | Development `BCPLAPT` object |
| `blddevb.jcl` | `BLDDEVB` | Development `BCPLBYTE` object |
| `blddevi.jcl` | `BLDDEVI` | Development `BCPLIO` object |
| `blddevm.jcl` | `BLDDEVM` | Development `BCPLMEM` object |
| `blddevn.jcl` | `BLDDEVN` | Development `BCPLMAIN` object |
| `blddevl.jcl` | `BLDDEVL` | Development `BLIB` object |
| `cambbld.jcl` | `CAMBBLD` | Build the demoted Cambridge compiler INTCODE |
| `cg370db.jcl` | `CG370DB` | Optional diagnostic compiler image |
| `bldrgchk.jcl` | `BLDRGCHK` | Non-installing registrar source assembly checks |
| `r5dinst.jcl` | `R5DINST` | Assemble, install, read back and compare `EXT_OBJ(BCPLDEMO)` |

`tools/datasets/dspal populate BOOT_JCL` installs the twelve
tracked FB80 JCL *bodies*; it does not submit any of them.
`dspal submit BOOT_JCL <MEMBER>` uses the configured MVS batch
identity and JES internal reader, reports both launcher and payload
job numbers, and waits for the payload result.

## Installation boundaries

The approved production target consists of six Core Runtime objects,
the empty default `BCPLREG` table, and the Base Library `BLIB`:
**eight members in `BOOT_OBJ`**. The revised `BLDBMAIN` installs
the seven assembler-built members; `BLIBBLD` installs `BLIB`
separately. The R.1–R.3 registration acceptance used temporary
objects. The corrected `BOOT_OBJ` installation remains subject to
separate owner authorization.

`R5DINST` builds the optional System Extension `BCPLDEMO` from
`EXT_ASM(BCPLDEMO)`, installs only `EXT_OBJ(BCPLDEMO)`, and
verifies the binary records by read-back and IEBCOMPR. It does
**not** modify `BOOT_OBJ` or `BOOT_DEVOBJ`. Permanent object
installation requires the owner's authorization. The operation is
not atomic; inspect all four payload return codes before acceptance.

After permission and successful PDS population, the documented
R.5 installation command is:

```sh
tools/datasets/dspal submit BOOT_JCL R5DINST
```

See the [clean-room reconstruction runbook](../../packaging/clean-room-mvs-reconstruction.md)
and [R.5 installation design](../../packaging/runtime-extensions-r5-installation-design.md)
for preconditions, recovery and MVS acceptance evidence.

## Historical builds and diagnostics

Prior five-module production builds and D6/D7 candidate experiments
remain historical, not the current eight-member clean-room target.
Retained `BLDDEV*` jobs are not required for the production rebuild.
Historical JCL and probes are under [`history/`](history/) and are
not mapped by the canonical manifest. For example,
`history/build-dev-bcplm6.jcl` may be explicitly staged to
reproduce the historical `BOOT_DEVOBJ(BCPLM6)` profile.
`dspal populate` does not remove previously installed, now-unmapped
members from an existing MVS PDS.

## Host verification (no MVS submission)

```sh
python3 tools/checks/check-native-jcl-manifest.py
tools/datasets/dspal populate BOOT_JCL --dry-run
```

These checks validate the Git-to-PDS source inventory and planned
population, not runtime execution or installation success.
