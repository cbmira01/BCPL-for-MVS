# MVS deployment model

This directory used to contain design notes for `pdspal` and early `dspal` work. Those decisions are now implemented, so the superseded planning files have been removed from the current tree. Their history remains available in Git.

The current deployment interface is `tools/dspal`; the checked-in manifest is `config/dspal.yaml`.

## Authority and lifecycle

The basic rule is:

```text
Git repository = authoritative project source
MVS data sets  = reproducible deployed/build state
```

The managed MVS libraries are normally under `HERC02.BCPL.*`. Source-oriented libraries use FB/80 text records and CP037 conversion; `LOAD` is a load-module library.

Create and populate the managed set with:

```sh
tools/dspal initbcpl
tools/dspal populate all
```

Inspect it with:

```sh
tools/dspal stat
tools/dspal ls
```

Remove the complete managed set with:

```sh
tools/dspal purgebcpl
```

`purgebcpl` operates only on the explicit manifest-defined data sets and requires confirmation unless `--yes` is supplied. Re-running it after the data sets are already absent is a clean no-op.

The create -> populate -> purge -> recreate -> repopulate lifecycle has been exercised successfully on the TK5 development system.

## Population rules

`populate` is authoritative for mapped members but deliberately does not prune unrelated MVS members.

It:

- validates all selected host files before mutation;
- converts UTF-8 host text to EBCDIC CP037 strictly;
- refuses records longer than the target LRECL;
- replaces explicitly mapped members;
- leaves unrelated members alone;
- refuses ambiguous member mappings; and
- supports `--dry-run` and redacted `--show-jcl` inspection.

`SOURCE` has explicit Cambridge bootstrap/compiler member mappings, including generated demoted sources under `workarea/bootstrap-cambridge/`. Those generated host artifacts must exist before `dspal populate SOURCE`. `LOAD` remains build output and is not populated from Git.

## Local configuration and credentials

Checked-in defaults live in `config/dspal.yaml`. Installation-specific values, including the MVS batch password, belong in:

```text
config/dspal.local.yaml
```

That file is gitignored and was confirmed during the public-release audit never to have been committed to the repository's reachable history.

See `config/README.md` for configuration details and `tools/README.md` for the command interface.