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

The local file is deep-merged over the checked-in manifest. It is the place for installation-specific changes such as another userid/HLQ, a pinned DASD volume, different reader or Hercules ports, or another container name.

The checked-in defaults use `HERC02`, leave physical volume selection to normal MVS allocation, use the local TK5 reader on port 3505, and define the ten managed BCPL PDS datasets used by `dspal initbcpl`.

Keep shared reproducible policy in `dspal.yaml`; keep host/user-specific policy in `dspal.local.yaml`.
