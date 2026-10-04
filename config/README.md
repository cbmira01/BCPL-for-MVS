# Project Configuration

This directory contains checked-in configuration that selects or describes project-wide defaults used by host-side tooling.

Configuration belongs here when it is part of the reproducible project definition rather than source code, generated output, or machine-local state.

## Files

| File | Purpose |
| --- | --- |
| [`CURRENT`](CURRENT) | Names the current validated ICINT assembler source. `tools/current-icint` reads this filename and resolves it under `asm/`. |

`CURRENT` contains only an assembler filename, currently:

```text
icintv17.asm
```

Do not infer the current interpreter by selecting the numerically highest `asm/icintv*.asm` file. New numbered sources may exist while still experimental. Promotion of a validated interpreter consists of changing `config/CURRENT` after the appropriate regression work has passed.

Future checked-in configuration, including `dspal` project policy and mappings, should live here when it represents repository-wide reproducible defaults. Machine- or user-specific overrides should remain separate and should not be committed unless they are intentionally part of the shared project configuration.
