# BCPLMAIN modularization — first checkpoint

Status: **source staging only**, not separately assembled or link-edited object modules.

## Boundary decision

Keep the compiler-visible entry point **BCPLMAIN**, the single CSECT,
global-vector conventions, and all generated-code linkage unchanged while
modularization is validated. The historical runtime may eventually be
multi-member (`BCPLMAIN`, `$LOAD$`, `$BLOCK$`, `$TPUT$`, `$IOS$`);
those contracts are not sufficiently recovered to split object modules yet.

Four ordered fragments are staged under `asm/bcplmain-wip/`:

| File | Current content |
| --- | --- |
| `00-contract.asmfrag` | Historical responsibility contract, provenance, public ABI notes |
| `10-bootstrap-and-system.asmfrag` | BCPLMAIN entry, startup, system vector, termination, stack, APTOVEC |
| `20-streams-and-services.asmfrag` | Stream operations, WRITEF bootstrap, byte and vector services, diagnostics |
| `30-control-data-and-end.asmfrag` | Static controls, DCBs, buffers, final assembler END |

The parts are **ordered lexical fragments of one assembler translation unit**.
They are not independently assembled CSECTs, cannot be used directly as
link-edit input, and should not be called finished component boundaries.
Data and code cross-reference each other extensively. In particular,
BLIB remains a separately compiled/linked BCPL object, and LIBHDR
remains an interface definition, not implementation.

## Non-regression gate

The split was established from the existing `asm/bcplmain-wip.asm`
without source edits. The four fragment contents were concatenated
during preparation and independently compared to the source string:
**63,153 bytes identical**.

To reproduce on the development host:

```sh
python3 tools/checks/check-bcplmain-modules.py
python3 tools/checks/check-bcplmain-modules.py --output workarea/bcplmain-modular-rebuilt.asm
cmp asm/bcplmain-wip.asm workarea/bcplmain-modular-rebuilt.asm
```

The check fails closed on **any** differing byte. Neither it nor the
`--output` option changes the baseline source. All pre-existing native
regression tools continue consuming `asm/bcplmain-wip.asm` and
therefore retain their previously accepted behavior.

## Next gated change

After the operator reports the check passing, change the native assembly
preparation path to consume a generated, independently compared modular
source, first on a disposable regression and then on the full panel.
Only after that should we extract independently assembled CSECT/object
members or change MVS PDS linkage, subject to module ABI evidence.

The historically described library division is a goal to investigate,
not grounds for inventing new calling conventions.
