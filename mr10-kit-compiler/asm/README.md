# ICINT assembler sources

ICINT runs BCPL programs in the historical INTCODE format on MVS 3.8.

| File | Use |
| --- | --- |
| `icintv12.asm`–`icintv18.asm` | Saved stages of the interpreter |
| `icintv14-trace.asm` | Diagnostic variant |
| `icintv19.asm` | Version installed as `ICINT19` in MR10KIT |
| `CURRENT` | Selects the default interpreter for host tools |

Run `tools/mr10/current-icint` from the repository root to see the host-tool default. The installed MVS `ICINT19` is a separate choice. Native BCPL runtime assembler is in the repository-root `asm/` directory.
