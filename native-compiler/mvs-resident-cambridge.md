# MVS-resident Cambridge compiler path

The Cambridge compiler used by the native-code regressions is still an
INTCODE program executed by ICINT V19. It is not yet a native System/370
compiler load module.

The deployment boundary is deliberately strict:

```text
Git/workarea -> dspal -> HERC02.BCPL.* PDS members
                         |
                         v
                    MVS build JCL
                         |
                         v
          LOAD(ICINT19) + INTCODE(CAMBCOMP)
```

The MVS build does not embed or transfer host files. All host-to-MVS
positioning is performed by `dspal`.

## Host-side preparation

The demoted Cambridge sources and enlarged-name MR10 TRNI are generated
artifacts under `workarea/`:

```sh
python3 native-compiler/bootstrap-cambridge/make-demoted.py
bash native-compiler/bootstrap-cambridge/build-mr10-trni-large-names.sh
```

## dspal population

`config/dspal.yaml` maps the generated Cambridge sources into
`HERC02.BCPL.SOURCE`, ICINT V19 into `HERC02.BCPL.ASM`, and the bootstrap
INTCODE inputs including `TRNILRG` into `HERC02.BCPL.INTCODE`.

After `dspal initbcpl`:

```sh
tools/dspal populate SOURCE
tools/dspal populate ASM
tools/dspal populate INTCODE
```

At this point the source/input PDS state is complete and independently
inspectable.

## MVS build

The authoritative checked-in build body is:

```text
jcl/build-cambridge-resident.jcl
HERC02.BCPL.JCL(CAMBBLD)
```

It deliberately contains no JOB statement and no credential. Populate it with:

```sh
tools/dspal populate JCL
```

Submit it with:

```sh
tools/dspal submit JCL CAMBBLD --wait
```

`dspal submit` generates a small authenticated launcher job. The launcher
writes an authenticated CAMBBLD JOB card followed by the stored PDS member to
the JES internal reader. Passwords come only from the gitignored
`config/dspal.local.yaml`.

The member never makes a round trip through the host.

The job:

1. assembles `HERC02.BCPL.ASM(ICINT19)`;
2. link-edits `HERC02.BCPL.LOAD(ICINT19)`;
3. compiles each demoted Cambridge source from `HERC02.BCPL.SOURCE`;
4. converts each OCODE unit to persistent INTCODE;
5. retains all individual compiler units in `HERC02.BCPL.INTCODE`;
6. concatenates the units plus BLIBI/ICLIB into
   `HERC02.BCPL.INTCODE(CAMBCOMP)`.

`CAMBCOMP` is the single ICINT-runnable Cambridge compiler image used by
the fast compile path.

## Inspection checkpoint

No regression is run by `build-cambridge-mvs`. After the build, inspect:

```sh
tools/dspal ls SOURCE
tools/dspal ls ASM
tools/dspal ls INTCODE
tools/dspal ls LOAD
```

Useful content checks include:

```sh
tools/dspal cat SOURCE BCPL
tools/dspal cat SOURCE CGA
tools/dspal cat INTCODE CAMBCOMP
```

The load library is RECFM=U, so `dspal cat` does not apply to LOAD; use
`dspal ls LOAD` to verify `ICINT19`.

Only after that inspection checkpoint should Test 24 be run through:

```sh
bash native-compiler/regression/run-test-mvs.sh 24
```

## ICINT promotion policy

This workflow does not change `config/CURRENT`. ICINT V19 remains the
specific interpreter required for the resident Cambridge compiler image.
