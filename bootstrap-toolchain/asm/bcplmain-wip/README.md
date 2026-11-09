# BCPLMAIN-WIP historical assembler fragment staging

These four fragments are **ordered parts of one historical assembler
translation unit**; they are not independent runtime CSECTs and should not be
assembled or link-edited separately.

| Fragment | Contents |
| --- | --- |
| `00-contract.asmfrag` | Historical startup/linkage notes and assembler source header |
| `10-bootstrap-and-system.asmfrag` | Entry, startup, system vector and stack services |
| `20-streams-and-services.asmfrag` | Stream, byte, vector and diagnostic routines |
| `30-control-data-and-end.asmfrag` | Static controls, DCBs and assembler END |

The reference byte stream is
[`asm/history/bcplmain-wip.asm`](../history/bcplmain-wip.asm).
The **current canonical Core Runtime** uses
[`asm/bcplmain.asm`](../bcplmain.asm); this fragment set is retained for
reproducing the older source-mode regression path.

From the repository root, validate the fragments **without JES submission**:

```sh
python3 -B tools/checks/check-bcplmain-modules.py
```

`bootstrap-toolchain/regression/run-test.sh` supports the historical
opt-in `BCPLMAIN_MODULAR_SOURCE=1` mode and checks byte-for-byte
fragment reconstruction before using it.

All dated modularization checkpoints, source audits, early contracts
and MVS probe evidence formerly stored beside these fragments are in
[`packaging/archive/core-runtime/bcplmain-wip/`](../../../packaging/archive/core-runtime/bcplmain-wip/README.md).
Those documents are historical evidence, not an alternative authoritative
runtime specification.
