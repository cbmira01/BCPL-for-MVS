# Cambridge Compiler — BCPL Sources

This folder holds the original Cambridge BCPL source files copied
unchanged from [`richards-bcpltape/bcplib/bcpl/`](../../richards-bcpltape/bcplib/bcpl/).
These are the historical sources for the **native Cambridge compiler**
project, not the MR10-compatible, interpreter-hosted derivatives in
`bootstrap-toolchain/`.

## Folder contents

| File | Role | What it contains |
| --- | --- | --- |
| [`bcpl.bcpl`](bcpl.bcpl) | Compiler driver | The `BCPL` section: reads compiler options, manages the compilation phases, reports errors, and controls compiler streams and sections. |
| [`syn.bcpl`](syn.bcpl) | Syntax and lexical analysis | Two sections, `SYN` and `LEX`. Reads BCPL text, recognizes tokens and declarations, and builds the syntax tree. |
| [`synhdr.bcpl`](synhdr.bcpl) | Syntax header | Token and syntax-tree constants plus shared globals used by `SYN` and `LEX`. |
| [`trn.bcpl`](trn.bcpl) | Translation | Two sections, `TRNA` and `TRNB`. Translates the syntax tree into intermediate OCODE. |
| [`trnhdr.bcpl`](trnhdr.bcpl) | Translation header | Syntax and OCODE constants and shared globals used by the translator. |
| [`cg.bcpl`](cg.bcpl) | System/370 code generator | Five sections, `CGA`, `CGB`, `CGC`, `CGD`, and `CGE`. Converts OCODE into System/370 assembler or, when enabled, object-deck output. |
| [`cghdr.bcpl`](cghdr.bcpl) | Code-generator header | OCODE definitions, System/370 register and instruction constants, and shared code-generator globals. |
| [`blib.bcpl`](blib.bcpl) | BCPL library | The historical `BLIB` section, including formatting, string, and other general BCPL support routines. |
| [`ios.bcpl`](ios.bcpl) | I/O diagnostics | The historical `$IOS$` section, including routines that report open input and output streams. |
| [`pm.bcpl`](pm.bcpl) | Postmortem support | The historical `PM` section, including backtrace and diagnostic routines. |
| [`editmain.bcpl`](editmain.bcpl) | Runtime source utility | The historical `EDITMAIN` section. Edits the machine-code library's assembler source for the selected host format. It is not a compiler phase. |
| [`README.md`](README.md) | Folder guide | Describes the files and their roles. |

## How the compiler is arranged

The main historical compiler is **ten sections in four source files**:

| Source file | Compiler sections |
| --- | --- |
| `bcpl.bcpl` | `BCPL` |
| `syn.bcpl` | `SYN`, `LEX` |
| `trn.bcpl` | `TRNA`, `TRNB` |
| `cg.bcpl` | `CGA`, `CGB`, `CGC`, `CGD`, `CGE` |

The three `*hdr.bcpl` files supply declarations, not standalone
executable compiler sections. `BLIB`, `$IOS$`, `PM`, and `EDITMAIN`
are supporting historical code. The shared system-wide `LIBHDR`
is held separately under
[`richards-bcpltape/sys3/bcpl/libhdr`](../../richards-bcpltape/sys3/bcpl/libhdr).

The sources retain their original `SECTION` declarations and
historical `GET` file names. The native MVS build must handle those
conventions deliberately; do not change the original files just to
make them resemble the earlier MR10 bootstrap derivatives.
