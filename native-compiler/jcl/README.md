# MVS build JCL (M3)

This directory is the authoritative source of reusable MVS build job bodies.
`config/dspal.yaml` maps approved jobs into `NATIVE_JCL`; `dspal populate
NATIVE_JCL` or `dspal put` installs them, and `dspal submit NATIVE_JCL
<MEMBER>` runs them. No competing host-side build driver should be introduced.

## Source ownership

The current `bcplmain.asm` is the D6/M5.5 development source.
It is mapped to `NATIVE_ASM(BCPLMAIN)`, matching its Git filename.
The other four canonical modules map the same way.

**Do not submit BLDBMAIN without separate production approval.** It
would now assemble D6 and replace `NATIVE_OBJ(BCPLMAIN)`.
Populating source members alone does not modify binary objects.

## Current production rebuilds

- `CAMBBLD` — build the resident compiler image in `NATIVE_INTCODE`.
- `BLDBMAIN` — assemble `NATIVE_ASM(BCPLMAIN,BCPLMEM)` into `NATIVE_OBJ`.
- `BLIBBLD` — compile `NATIVE_SOURCE(BLIB)` and install `NATIVE_OBJ(BLIB)`.

## Candidate builds (not production promotion)

- `BLDDEVA` — `NATIVE_ASM(BCPLAPT)` to `NATIVE_DEVOBJ(BCPLAPT)`.
- `BLDDEVB` — `NATIVE_ASM(BCPLBYTE)` to `NATIVE_DEVOBJ(BCPLBYTE)`.
- `BLDDEVI` — `NATIVE_ASM(BCPLIO)` to `NATIVE_DEVOBJ(BCPLIO)`.
- `build-dev-bcplm6.jcl` — optional historical job, **not mapped in the manifest**. Stage it explicitly as `BLDDEVM6` to assemble `NATIVE_ASM(BCPLMAIN)` into `NATIVE_DEVOBJ(BCPLM6)` only.
- `BLDDEVM`, `BLDDEVN`, `BLDDEVL` — existing candidate builds for
  BCPLMEM, BCPLMAIN, and BLIB respectively.

`SEEDDEV` is **not** an initial bootstrap or promotion step: it copies a
specific accepted five-member set and must not be submitted before that set
exists. A successful candidate assembly does **not** authorize copying an
object into `NATIVE_OBJ`. Retain explicit runtime acceptance evidence and
only then establish an authoritative production build procedure if needed.

All M3 source and binary object references use manifest-managed `NATIVE_*`
and `MR10_*` datasets; `CAMB_*` resources are reserved for M4.
