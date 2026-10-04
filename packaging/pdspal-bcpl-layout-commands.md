# `pdspal` BCPL Project-Layout Commands

This note records two deliberately distinctive `pdspal` commands for reproducibly creating and removing the standard BCPL-on-MVS dataset layout.

These commands complement the general PDS-management interface documented in `pdspal-and-mvs-storage.md`.

## `pdspal initbcpl`

```text
pdspal initbcpl
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
HERC02.BCPL.LOAD
HERC02.BCPL.TEST
```

The command should be **idempotent**:

- create any managed dataset that is missing;
- leave an existing managed dataset alone if its definition is acceptable;
- report incompatible existing definitions rather than silently replacing them;
- never remove or recreate an existing dataset merely to make the command succeed.

The exact DCB and allocation attributes for each managed dataset belong to the `pdspal` project-layout definition and should be visible through `pdspal info`, `pdspal stat`, documentation, or generated JCL.

As with other MVS-changing commands:

```text
pdspal --show-jcl initbcpl
```

should emit the complete JCL required to establish the missing project layout without submitting it.

## `pdspal purgebcpl`

```text
pdspal purgebcpl
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
pdspal purgebcpl --yes
```

should perform the same defined deletion set without prompting.

`purgebcpl` must still obey the configured `pdspal` write boundary. `--yes` means "do not ask for interactive confirmation"; it must **not** mean "bypass safety policy".

Generated-JCL mode should also work:

```text
pdspal --show-jcl purgebcpl
```

and should emit the exact deletion job without submitting it.

## Reproducibility role

Together these commands provide a repeatable lifecycle for the MVS-side BCPL development area:

```text
pdspal initbcpl
    ... populate/build/test ...
pdspal purgebcpl --yes
pdspal initbcpl
```

This makes it possible to prove that the project's required MVS data structures can be reconstructed from the repository and `pdspal` configuration rather than depending on manually accumulated DASD state.

That reproducibility property is one of the reasons these commands should remain first-class `pdspal` operations rather than external shell scripts containing a sequence of `mkpds` and `rmpds` calls.
