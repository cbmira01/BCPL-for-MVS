# MR10 kit compiler options

**Status:** Source-code inventory, 9 November 2026. This is a description of
the option handling found in the surviving MR10 kit BCPL source, **not** a
claim that every switch has been independently tested on MVS.

## Source and scope

Primary authority:

- [Historical `syn`](../../richards-bcpltape/mr10/bcplkit/syn) —
  `START` reads options (lines 115–158), applies them (lines 165–203),
  and the lexer uses the relevant flags (lines 214, 519, 553, 652).
- [Historical `trn`](../../richards-bcpltape/mr10/bcplkit/trn) —
  uses the shared `SAVESPACESIZE` global in translation.
- [Historical `cg`](../../richards-bcpltape/mr10/bcplkit/cg) —
  the separate OCODE-to-INTCODE converter; its `START` does not
  read the `OPTIONS` input stream.
- [Installed kit source images](../source/README.md) — tracked
  `syni.int`, `trni.int`, and `cgi.int` used by the MVS driver.

These options belong to the **MR10 SYN/TRN compiler**. They are distinct
from the [demoted Cambridge compiler's two-phase option grammar](../../bootstrap-toolchain/bootstrap-cambridge/compiler-options-and-parm.md)
and from the command-line options of `tools/mr10/compile-and-run`.

## Input and defaults

The MR10 source executes:

```bcpl
SOURCESTREAM := FINDINPUT("OPTIONS")
```

If `OPTIONS` is absent, the default configuration is used. If it is
present, the compiler reads the **first record up to newline or end-of-stream**
as a sequence of option characters. It echoes the option record to
`SYSPRINT` with the prefix `OPTIONS  `. There is **no slash separator**
and no second (CG370) option phase in this parser.

Initial state in `syn`:

| Setting | Default |
| --- | --- |
| `TREESIZE` | `5500` BCPL words |
| `SAVESPACESIZE` | `2` |
| `OPTION!0` … `OPTION!20` | `FALSE` |
| `PPTRACE` | `FALSE` |
| `PRSOURCE` | `FALSE` |
| `CHARCODE` | Identity conversion (defined by `LET CHARCODE(CH) = CH`) |
| `REPORTMAX` | `20` (hard-coded; not an option) |

## Options found in the MR10 source

| Option | Source-side action | Operational effect |
| --- | --- | --- |
| `P` | Sets `OPTION!1` | Parser/lexer debugging: print symbol number and `WORDV` at each token, then stop on `S.END`. This is a diagnostic token walk, **not** an ordinary compile. |
| `T` | Sets `OPTION!2` | Print the abstract-expression (AE) parse tree using `PLIST(A, 0, 20)` after `FORMTREE()`. |
| `C` | Sets `OPTION!3` | Suppress `COMPILEAE(A)`: parse input without emitting the normal OCODE for each tree. |
| `M` | Sets `OPTION!4` | Call `MAPSTORE()` after the compiler's `APTOVEC` work finishes. |
| `N` | Sets `OPTION!5` | Suppress following `GET` inclusions: `PERFORMGET()` consumes the requested filename but returns without opening it. |
| `A` | `CHARCODE := EBCDICTOASCII` | Enable the historical EBCDIC-to-ASCII lookup for single-character literal conversion. It is **not** a general input-stream or target-code translation switch. |
| `S` | `PRSOURCE := TRUE` | Echo characters of the top-level source during lexical reading; nested `GET` input is excluded by the `GETP=0` check. |
| `E` | `PPTRACE := TRUE` | Emit the current lexer character when `NEXTSYMB` starts, for debugging. This is separate from the `S` source listing. |
| `L<decimal>` | `TREESIZE := READN()` | Set the tree/workspace allocation passed to `APTOVEC(COMP, TREESIZE)`, replacing the default of 5500 words. The number's terminating character is reprocessed by the option scanner. |
| `3` | `SAVESPACESIZE := 3` | Change the translator's initial and per-call workspace/save-space allowance from 2 to 3 BCPL words. |

The `OPTION!1`–`OPTION!5` uses are visible in `syn`;
`trn` uses `SAVESPACESIZE` in its stack-offset bookkeeping.
There is no evidence in these MR10 sources of the Cambridge
compiler's `/<code-generator-options>` switches.

## Supplying options on MVS

For the current host driver, put a single option record in a plain
ASCII file and bind it to the `OPTIONS` DD using `--dd`:

```sh
# Example: tree workspace used when MR10 bootstraps the Cambridge sources.
# This command submits real JES jobs; run only with operator authorization.
tools/mr10/compile-and-run --installed-icint MR10_LOAD \
    --dd OPTIONS=bootstrap-toolchain/bootstrap-cambridge/options-large-tree.txt \
    mr10-kit-compiler/tests/00-regression-panel/data-movement/scalar-vector.bcpl
```

The referenced options file contains exactly:

```text
L12000
```

The `--dd NAME=PATH` argument to `compile-and-run` stages the named
input file into the compilation steps. It is a **host-driver argument**
that supplies the MR10 compiler's `FINDINPUT("OPTIONS")` stream;
it does not alter the option syntax. Alternatively, traditional JCL
can supply an `OPTIONS DD` alongside the MR10 compiler's input.
The MR10 `START(PARM)` source does not parse the MVS `EXEC PARM=`
field for these options.

Do not confuse this MR10 `OPTIONS` DD with the demoted Cambridge
compiler's `CAMBPARM` DD. In a bootstrap job, **MR10 consumes
`OPTIONS` while building the Cambridge compiler**, and the subsequently
executing Cambridge compiler consumes `CAMBPARM`.

## Parser quirks and verification limits

The historical option scanner is permissive rather than validating a
defined grammar. It uses a mutable local index `N`, initialized to
zero; `P/T/C/M/N` assign that index, and **each** character processed
then writes `OPTION!N := TRUE`. `A/S/E/L/3` have their own side effects.
Other characters are not explicitly rejected; they can set `OPTION!0`
or reassert the most recently selected indexed flag. Therefore do not
treat an arbitrary letter as a supported option just because the scanner
does not report an error.

The source examination establishes the ten recognized spellings and
their implementation sites, but it does **not** establish that every
combination, debug output, numeric limit, or the historical source's
equivalence to the precompiled `syni.int` image has been verified on MVS.
A full behavioral acceptance would require separately authorized MVS
compiler runs and observed ICINT/JES evidence.

**Source-based conclusion:** `P`, `T`, `C`, `M`, `N`, `A`,
`S`, `E`, `L<decimal>`, and `3` are the MR10 source-recognized
options found in this audit.
