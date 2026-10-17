# Native MVS JCL — canonical builds

`config/dspal.yaml` maps **one canonical Git `.jcl` file to each
same-named `NATIVE_JCL` PDS member**. Filenames are lowercase; MVS
member names are uppercase, each within the eight-character limit.

| Git JCL file | PDS member | Role |
|---|---|---|
| `cambbld.jcl` | CAMBBLD | Rebuild demoted Cambridge compiler INTCODE |
| `cg370db.jcl` | CG370DB | Optional diagnostic compiler image |
| `blibbld.jcl` | BLIBBLD | Build BLIB into production NATIVE_OBJ |
| `bldbmain.jcl` | BLDBMAIN | Build BCPLMAIN and BCPLMEM into production NATIVE_OBJ |
| `blddeva.jcl` | BLDDEVA | Development BCPLAPT object |
| `blddevb.jcl` | BLDDEVB | Development BCPLBYTE object |
| `blddevi.jcl` | BLDDEVI | Development BCPLIO object |
| `blddevm.jcl` | BLDDEVM | Development BCPLMEM object |
| `blddevn.jcl` | BLDDEVN | Development BCPLMAIN object |
| `blddevl.jcl` | BLDDEVL | Development BLIB object |

`dspal populate NATIVE_JCL` installs the ten tracked job *bodies*.
They do not execute until submitted. Use `dspal submit NATIVE_JCL
<MEMBER>` only after checking the job's source/output datasets and
whether its target is NATIVE_OBJ or NATIVE_DEVOBJ.

## Production promotion hold

The manifest currently maps canonical Git `native-compiler/asm/bcplmain.asm`
(the accepted D6/M5.5 source) to `NATIVE_ASM(BCPLMAIN)`.
**Submitting BLDBMAIN would therefore replace the existing production
NATIVE_OBJ(BCPLMAIN) with D6** (and rewrite BCPLMEM). This is a
production promotion, **not approved by canonicalizing filenames**.
Do not submit that job, or run the historical destructive clean-room
sequence through it, without an explicit separate production decision.

`BLIBBLD` also installs a production BLIB object; its own
prerequisites and installation must be reviewed independently.
Development builders use `NATIVE_DEVOBJ` and do not promote to
`NATIVE_OBJ`.

## Historical builds, probes and source names

Useful earlier D6/D7 reproducibility decks are isolated under
[`history/`](history/), **not manifest-mapped**. In particular,
`history/build-dev-bcplm6.jcl` can be explicitly staged as
`NATIVE_JCL(BLDDEVM6)` to build canonical
`NATIVE_ASM(BCPLMAIN)` into historical
`NATIVE_DEVOBJ(BCPLM6)`. That object-member name remains relevant
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
tools/datasets/dspal populate NATIVE_JCL --dry-run
```

This check only validates source layout and manifest agreement.
It does not assemble programs, execute jobs, or verify MVS runtime
compatibility.
