# `dspal` BCPL Project-Layout Commands

This note records two deliberately distinctive `dspal` commands for reproducibly creating and removing the standard BCPL-on-MVS dataset layout.

The original name for the proposed tool was `pdspal`. The tool has since been broadened to cover sequential as well as partitioned data sets and is now named **`dspal`**. See `dspal-direction.md`.

## `dspal initbcpl`

```text
dspal initbcpl
```

Creates the standard managed BCPL PDS datasets beneath the configured MVS high-level qualifier.

With the current recommended configuration:

```text
userid = HERC02
hlq = HERC02
```

that means the initial managed set is:

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

The command should be **idempotent**:

- create any managed dataset that is missing;
- leave an existing managed dataset alone if its definition is acceptable;
- report incompatible existing definitions rather than silently replacing them;
- never remove or recreate an existing dataset merely to make the command succeed.

Most of these are expected to be ordinary 80-column text PDSes, typically `RECFM=FB,LRECL=80`. `HERC02.BCPL.LOAD` is a load-module library and should use appropriate load-library attributes, normally `RECFM=U`.

The exact DCB and allocation attributes for each managed dataset belong to the `dspal` project-layout definition and should be visible through `dspal info`, `dspal stat`, documentation, or generated JCL.

As with other MVS-changing commands:

```text
dspal --show-jcl initbcpl
```

should emit the complete JCL required to establish the missing project layout without submitting it.

## `dspal purgebcpl`

```text
dspal purgebcpl
```

Removes the standard managed BCPL datasets created by `initbcpl`.

This command is intentionally named conspicuously because it is destructive.

The deletion set should be the **defined managed BCPL dataset set**, not an unrestricted wildcard over every dataset whose name happens to match `HERC02.BCPL.*`.

This protects future or manually-created datasets such as:

```text
HERC02.BCPL.EXPERIMENT
HERC02.BCPL.ARCHIVE
```

unless they have explicitly become part of the managed project layout.

Interactive use should display the datasets that will be removed and require confirmation.

For noninteractive and reproducible automation:

```text
dspal purgebcpl --yes
```

should perform the same defined deletion set without prompting.

`purgebcpl` must still obey the configured `dspal` write boundary. `--yes` means "do not ask for interactive confirmation"; it must **not** mean "bypass safety policy".

Generated-JCL mode should also work:

```text
dspal --show-jcl purgebcpl
```

and should emit the exact deletion job without submitting it.

## Reproducibility role

Together these commands provide a repeatable lifecycle for the MVS-side BCPL development area:

```text
dspal initbcpl
    ... populate/build/test ...
dspal purgebcpl --yes
dspal initbcpl
```

This makes it possible to prove that the project's required MVS data structures can be reconstructed from the repository and `dspal` configuration rather than depending on manually accumulated DASD state.

That reproducibility property is one of the reasons these commands should remain first-class `dspal` operations rather than external shell scripts containing a sequence of `mkpds` and `rmds` calls.
