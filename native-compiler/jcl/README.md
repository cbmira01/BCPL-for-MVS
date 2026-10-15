# MVS build JCL (M3)

This directory is the authoritative source of reusable MVS build job bodies.
`config/dspal.yaml` maps approved jobs into `NATIVE_JCL`; `dspal populate
NATIVE_JCL` or `dspal put` installs them, and `dspal submit NATIVE_JCL
<MEMBER>` runs them. No competing host-side build driver should be introduced.

## Current production rebuilds

- `CAMBBLD` — build the resident compiler image in `NATIVE_INTCODE`.
- `BLDBMAIN` — assemble `NATIVE_ASM(BCPLMAIN,BCPLMEM)` into `NATIVE_OBJ`.
- `BLIBBLD` — compile `NATIVE_SOURCE(BLIB)` and install `NATIVE_OBJ(BLIB)`.

## Candidate builds (not production promotion)

- `BLDDEVA` — `NATIVE_ASM(BCPLAPT)` to `NATIVE_DEVOBJ(BCPLAPT)`.
- `BLDDEVB` — `NATIVE_ASM(BCPLBYTE)` to `NATIVE_DEVOBJ(BCPLBYTE)`.
- `BLDDEVI` — `NATIVE_ASM(BCPLIO)` to `NATIVE_DEVOBJ(BCPLIO)`.
- `BLDDEVM`, `BLDDEVN`, `BLDDEVL` — existing candidate builds for
  BCPLMEM, BCPLMAIN, and BLIB respectively.

`SEEDDEV` is **not** an initial bootstrap or promotion step: it copies a
specific accepted five-member set and must not be submitted before that set
exists. A successful candidate assembly does **not** authorize copying an
object into `NATIVE_OBJ`. Retain explicit runtime acceptance evidence and
only then establish an authoritative production build procedure if needed.

All M3 source and binary object references use manifest-managed `NATIVE_*`
and `MR10_*` datasets; `CAMB_*` resources are reserved for M4.
