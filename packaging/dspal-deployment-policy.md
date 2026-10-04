# `dspal` Deployment and Population Policy

This note records the current policy for MVS userid, dataset naming, volume placement, and reproducible population of BCPL project datasets.

## Default userid and HLQ

The default development identity is the stock TK5 userid:

```text
HERC02
```

The corresponding default high-level qualifier is:

```text
HERC02
```

Therefore project datasets are normally named beneath:

```text
HERC02.BCPL.**
```

The default configuration should be conceptually equivalent to:

```text
userid = HERC02
hlq = HERC02
default_volume = unset
write_boundary = HERC02.**
```

`default_volume = unset` is deliberate. By default, `dspal` should let ordinary MVS catalog and allocation rules determine the eligible DASD volume.

## Why no dedicated volume by default

A dedicated private volume can provide useful physical isolation, image-level backup, and a clean ownership story, but it also introduces additional system provisioning that must be made reproducible at the Git/Docker level:

- create a CKD image;
- attach it to Hercules;
- initialize it with ICKDSF;
- establish a VTOC;
- add persistent Hercules device configuration;
- add or update MVS volume configuration such as `VATLST00`;
- decide public/private mount policy;
- possibly create and connect a user catalog;
- maintain device addresses and volume serials without conflicting with the user's installation.

That complexity is not justified for the default project installation when the MVS catalog can already abstract physical placement.

The default policy is therefore:

> Name the datasets predictably and let MVS decide where they physically reside.

A dedicated volume remains an optional advanced configuration rather than a prerequisite.

## Why no new userid by default

A dedicated userid such as `BCPL` or `BCPLDEV` could produce attractive names, but defining a new userid turns project setup into broader MVS system provisioning.

Depending on the installation, that can involve security definitions, passwords, TSO setup, catalog aliases, profiles, procedures, and access controls.

For the normal project path, the stock `HERC02` identity already provides a suitable development namespace. The project should avoid requiring a custom userid merely to install and exercise the compiler.

`dspal` should nevertheless keep userid and HLQ configurable so a user can choose another installation policy later.

## Git is the source of truth

The key reproducibility rule is:

```text
Git repository = authoritative project source
MVS datasets   = reproducible deployed/build state
```

Loss of the MVS-side BCPL datasets should be recoverable from the repository and project configuration. A dedicated DASD image may be convenient, but it must not become the only authoritative copy of project source.

This leads to the intended bootstrap sequence:

```text
dspal initbcpl
dspal populate all
```

After those commands, the MVS-side project libraries should be reconstructible from Git without requiring manually accumulated DASD state.

## `dspal populate`

Population is a first-class reproducibility operation.

The intended interface is:

```text
dspal populate all
dspal populate SOURCE
dspal populate ASM
dspal populate JCL
dspal populate INTCODE
dspal populate LIBRARY
dspal populate BCPLDEMO
dspal populate LANGDEMO
dspal populate REGRESS
dspal populate TEST
```

`LOAD` is normally a build-product library rather than a Git-populated source library and therefore should not necessarily participate in ordinary source population.

### `populate all`

```text
dspal populate all
```

Populates every managed source/data PDS from its corresponding repository content.

The exact repo-directory-to-PDS mapping belongs in project configuration or a checked-in manifest so it is inspectable and reproducible.

### `populate PDS`

```text
dspal populate ASM
dspal populate SOURCE
```

Populates one managed BCPL PDS from the repo subtree mapped to that PDS.

The operand is a managed logical PDS name, not an arbitrary unrestricted dataset name.

## Population semantics

The initial policy should be conservative:

- create missing members;
- replace members whose managed Git source has changed;
- leave unrelated or unmanaged members alone;
- do not silently delete MVS members merely because no matching local file exists;
- fail on ambiguous filename-to-member-name mappings;
- fail on member-name collisions;
- fail on record-length violations rather than silently truncating;
- apply the existing text/EBCDIC conversion policy consistently;
- report what changed.

A future explicit pruning option may be added if there is a demonstrated need, but ordinary `populate` should not unexpectedly erase local MVS work.

## Dry-run support

Population should support:

```text
dspal populate all --dry-run
```

and similarly for individual PDSes.

Dry-run mode should report the proposed actions without modifying MVS, including at least:

- members to be added;
- members to be replaced;
- files rejected because of naming or record-format issues;
- source files that do not map to an MVS member.

Where population is implemented by generated jobs, `--show-jcl` remains useful as an independent teaching/debugging facility.

## Managed BCPL dataset set

The current managed PDS set is:

```text
HERC02.BCPL.SOURCE
HERC02.BCPL.ASM
HERC02.BCPL.JCL
HERC02.BCPL.INTCODE
HERC02.BCPL.LIBRARY
HERC02.BCPL.BCPLDEMO
HERC02.BCPL.LANGDEMO
HERC02.BCPL.REGRESS
HERC02.BCPL.TEST
HERC02.BCPL.LOAD
```

Most are expected to use ordinary 80-column text-library attributes, typically `RECFM=FB,LRECL=80`.

`HERC02.BCPL.LOAD` is a load-module PDS and is the principal exception.

## Optional advanced deployment

Users who want stronger physical isolation may later configure something like:

```text
userid = HERC02
hlq = HERC02
default_volume = USR000
```

or may define a separate userid/HLQ and user catalog.

These should remain optional extensions. Core `dspal` commands must not require a specific volume serial, device address, or custom userid unless the user explicitly configures one.

## End-user installation goal

For a user cloning and running the project, the normal MVS-side setup should be as small as practical:

```text
start TK5

dspal initbcpl
dspal populate all
```

The user should not have to understand CKD image creation, VTOCs, private volume mounting, catalog aliases, or userid provisioning merely to try the BCPL system.

Those facilities remain available to advanced users without becoming part of the default installation burden.
