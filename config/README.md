# Project Configuration

This directory contains checked-in configuration that selects or describes project-wide defaults used by host-side tooling.

Configuration belongs here when it is part of the reproducible project definition rather than source code, generated output, or machine-local state.

## Files

| File | Purpose |
| --- | --- |
| [`CURRENT`](CURRENT) | Names the current validated ICINT assembler source. `tools/current-icint` reads this filename and resolves it under `asm/`. |
| [`dspal.yaml`](dspal.yaml) | Canonical checked-in `dspal` manifest: MVS namespace defaults, runtime endpoints, text conversion policy, allocation defaults, and the managed BCPL PDS set. |
| `dspal.local.yaml` | Optional machine-local overrides for `dspal`. This file is gitignored and is not part of the shared project definition. |

`CURRENT` contains only an assembler filename, currently:

```text
icintv17.asm
```

Do not infer the current interpreter by selecting the numerically highest `asm/icintv*.asm` file. New numbered sources may exist while still experimental. Promotion of a validated interpreter consists of changing `config/CURRENT` after the appropriate regression work has passed.

## `dspal` configuration

`tools/dspal` loads configuration in this order:

```text
config/dspal.yaml
    ↓
config/dspal.local.yaml, when present
```

The local file is deep-merged over the checked-in manifest. It is the place for installation-specific changes such as another userid/HLQ, a pinned DASD volume, different reader or Hercules ports, another container name, and MVS batch credentials.

The checked-in defaults use `HERC02`, leave physical volume selection to normal MVS allocation, use `SYSDA` as the default allocation unit, use the local TK5 reader on port 3505, and define the ten managed BCPL PDS datasets used by `dspal initbcpl`.

## Batch credentials

Jobs submitted directly to the JES socket reader do not automatically inherit the `HERC02` TSO identity. On a TK5 system with RAKF active, mutating `dspal` jobs therefore need an authenticated JOB card.

The checked-in manifest names the batch userid but deliberately does not contain its password:

```yaml
mvs:
  userid: HERC02
  batch_user: HERC02
  batch_password: null
```

Put the installation-local password in the gitignored override file:

```yaml
mvs:
  batch_password: YOURPASS
```

For a stock TK5 installation, use the current password for the configured `batch_user`; do not commit it to `config/dspal.yaml`.

`dspal initbcpl --show-jcl` shows the authenticated JOB-card form but replaces the password with `REDACTED`. Actual mutating submissions require `mvs.batch_password` to be present in `config/dspal.local.yaml`; otherwise `dspal` fails locally before submitting a job.

Keep shared reproducible policy in `dspal.yaml`; keep host/user-specific policy and credentials in `dspal.local.yaml`.
