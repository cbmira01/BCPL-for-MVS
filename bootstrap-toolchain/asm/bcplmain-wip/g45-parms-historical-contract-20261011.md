# G45 PARMS: historical contract investigation

**Status:** Evidence checkpoint, no implementation. 2026-10-11.

## Direct historical evidence

| Source | Evidence | Consequence |
| --- | --- | --- |
| `sys3/bcpl/libhdr` | `PARMS:45` | Public global slot G45 exists |
| `km10/bcplmac`, around line 545 | `PARMS EQU 45` followed by `PARAMETER STRING` | Assembler-side global-number alias; not a storage definition |
| `km10/comacro`, around line 673 | Same alias and comment | Corroboration across macro variants |
| `km10/bcplmac` lines 632–642; `comacro` 761–771 | `PARMFLD` defines one-byte field followed by `PSTRING` | Supports length-prefixed parameter-field interpretation; precise external length encoding not established by macro alone |
| `km10/bcplmac` 1084–1090; `comacro` 1320–1326 | Fullword-aligned user-save-area `PARM` byte field, explicitly called parameter-string length | Parameter bytes associated with runtime save area, but G45 value and unit not assigned here |
| `km10/bcplmac` 603–630; `comacro` 732–759 | `PARMAREA` DSECT describes pseudo input stream from PARM string, with DCB-like fields | Historical FINDPARM pseudo-stream uses separate stream descriptor from raw parameter field |
| `bootstrap-toolchain/bootstrap-cambridge/compiler-options-and-parm.md` | `SELECTINPUT(FINDPARM())` consumes runtime-provided pseudo-stream; compiler option `G...` copied into `PARMS` according to earlier analysis | A parameter-string consumer path exists conceptually; *not* proof of identical G45 binding |
| `asm/bcplmain-wip/10-bootstrap-and-system.asmfrag` | G39 installed as PARMENT; no direct G45 store | Current bootstrap does not furnish G45 |
| `richards-bcpltape/bcplib/bcpl/cg`, `syn`, `trn` | No literal `PARMS`/`FINDPARM` occurrences in these particular files | Insufficient to claim absence of compiler consumers elsewhere |

## Contract separation

**G45 PARMS** is identified historically as a *parameter string* in both
macro collections. The macro bodies do not establish whether G45 stores
a BCPL word pointer, byte address, packed string, or another representation.
They do not show a direct `SETGLOB 45` operation.

**G39 FINDPARM** is a callable pseudo-stream provider for parameter options.
`PARMAREA` is explicitly a DCB-like pseudo-stream descriptor; it is not
the same thing as G45's string object.

**PARMFLD / PSTRING / USAEND / PARM** describe the external MVS PARM
field and a runtime save-area allocation location. They point toward a
length-bearing byte string, but **do not prove** the G45 global holds
its address, nor specify its storage lifetime.

The project bootstrap `FINDPARM` currently uses a prepared DD stream;
this is knowingly not historical EXEC PARM behavior.

## Bounded recommendation

**Do not yet initialize G45 with an assumed pointer.** First establish
a real G45 read/write consumer and inspect original BCPLMAIN code if
obtainable. The most economical proof would be a historical module using
`GETGLOB PARMS`, `SETGLOB PARMS`, `APPLY PARMS`, or `45(G)`
and a definition of the backing storage. Then define an explicit
BCPL-address/byte-address conversion and a narrow runtime test.

A safe nearer-term development task is to **specify and separately
implement the native G39 FINDPARM pseudo-stream from EXEC PARM**, with
no speculative change to G45. That change is not made in this checkpoint.

No regressions run; all accepted test evidence remains historical,
not rerun here.
