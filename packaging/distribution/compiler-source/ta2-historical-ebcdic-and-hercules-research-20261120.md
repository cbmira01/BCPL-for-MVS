# TA.2 — Historical BCPL EBCDIC and Hercules reader-translation research

**Project:** BCPL for MVS 3.8 Reconstruction  
**Milestone/march:** Tape artifact release / TA.2 — Manifest-Driven Tape Producer  
**Date:** 20 November 2026  
**Status:** Read-only historical and external technical research. **Not** an owner encoding decision, MVS write authorization or BT0021 staging approval.

## A. The surviving transport-tape files were not originally ASCII

Primary project archive evidence:

- `richards-bcpltape/INDEX` identifies the compiler files as original IBM datasets, e.g. `BCPLIB.BCPL(SYN)` and `BCPLIB.BCPL(BLIB)`, plus assembler, link and JCL datasets.
- `richards-bcpltape/README.orig.Yap` reports that Martin Richards' transport tape was read by Unix `dd` in EBCDIC mode and warns that Cambridge used a different EBCDIC dialect, producing mistranslated characters.
- `richards-bcpltape/README.Nordier` explicitly says Nordier corrected the character-mapping issues and assigned Unix filenames.
- Consequently the ASCII-compatible Git files are a corrected **character transcription** of EBCDIC historical material, not original byte-preserving ASCII source tapes. Do not confuse characters with their byte values.

Primary, historical System/370 BCPL character references:

- `richards-bcpltape/mr10/print/manual`, Appendix C, states that its table gives the graphics and decimal code values used on the **370 implementation of BCPL**. It lists **66 decimal = X'42' = '['**, **67 = X'43' = ']'**, and **79 = X'4F' = '|'**.
- `richards-bcpltape/mr10/text/charset`, “THE BCPL EBCDIC CHARACTER SET,” agrees with these locations.
- `richards-bcpltape/mr10/bcplkit/syn` contains `EBCDICTOASCII` and a `CHARCODE` setting controlled by its `OPTIONS` processing; source scanning therefore has historical conversion logic beyond a universal OS codepage assumption.
- `richards-bcpltape/bcplib/bcpl/syn` recognizes `|` as a lexical operator and comment delimiter. `richards-bcpltape/bcplib/bcpl/blib` contains explicit “EBCDIC SPECIFIC!” comments.
- **Qualification:** The MR10 manual/charset is direct historical System/370 BCPL evidence; it does not by itself prove every separately compiled `BCPLIB` compiler or runtime used identical on-disk bytes, nor that its current binary would correctly parse any alternate encoding. Verify the intended executable compiler's lexer before asserting compatibility.

## B. Hercules translation is an emulator/device policy, not an MVS universal CCSID

Hercules's documented `CODEPAGE mapping` configuration controls host-to-guest character conversion. The traditional `default` mapping is explicitly non-transparent. The `HERCULES_CP` environment variable is consulted when the configuration omits a mapping; the operator-panel `codepage` command **with no operand** displays the current mapping. `cp_updt` may install custom mappings. The emulated 3505 card reader can be configured as `ascii` (translate input) or `ebcdic` (treat card-image bytes as already EBCDIC). Socket readers default to ASCII when not explicitly configured.

Hercules 3.13 `codepage.c` published by Debian confirms its traditional `ascii_to_ebcdic` table maps ASCII:

| ASCII source character | ASCII byte | Hercules traditional default | CP037 comparator | Historical BCPL manual |
| --- | --- | --- | --- | --- |
| `|` | X'7C' | X'6A' | X'4F' | X'4F' |
| `[` | X'5B' | X'AD' | X'BA' | X'42' |
| `]` | X'5D' | X'BD' | X'BB' | X'43' |

The three default-map values match **exactly** what the existing read-only IFOX/IEWL/QSAM **MVS JOB 9330** measured. The subsequent saved-evidence reconciliation RC=0 established **15/15 members and 6,577 FB80 records**, with all 15 observed transport-profile fingerprints and record counts matching the frozen Git sources. Original literal CP037 comparison was **7/15**. This strongly identifies traditional Hercules input translation as the cause; a live `codepage` query and the exact installed `/tk5/conf/tk5.cnf` remain necessary to assert the current running configuration, rather than infer it solely from byte signatures.

The repository's `docker/run-tk5.sh` launches Hercules with `-f conf/tk5.cnf` under `/tk5`. The runtime config is not the frozen Git source archive, and the authoritative running setting has **not** been read in this research.

External references:

- Hercules configuration and card-reader documentation:
  https://hercules-390.github.io/html/hercconf.html
- Hercules `codepage` panel command:
  https://hercules-390.github.io/html/hercoper.html
- Traditional default codepage source:
  https://sources.debian.org/src/hercules/3.13-8/codepage.c
- Hercules socket-reader explanation:
  https://www.jaymoseley.com/hercules/compiling/how_to.htm

## C. What MVS 3.8 can tell us

MVS 3.8 does not generally attach a modern universally enforced CCSID to an ordinary `RECFM=FB,LRECL=80` source PDS. The bytes are records and their **meaning** depends on the programmer's, compiler's, device's and tools' character conventions. An MVS `D U` or `LISTDS` query reports device or DCB properties, not the definitive source character set.

- **Actual PDS data**: a small read-only IFOX/IEWL QSAM `GET` program can show each raw byte via `IC` and hex output. Our JOB 9330 did this by computing FNV-1a/additive fingerprints over all 80 bytes per record and recording trailing blank records; that evidence should not be repeated unless a specific new question requires it.
- **IBM utility alternative**: MVS 3.8 `IEBPTPCH`, `PRINT TOTCONV=XE`, can display selected record bytes in hex. Use a bounded print selection to avoid giant SYSOUT; distinguish IBM utility's formatted output from the original PDS bytes.
- **Actual conversion policy**: query the **Hercules** operator's no-operand `codepage` and the existing 3505 reader definition; no MVS system command substitutes for this emulator setting. Do not change `CODEPAGE` while investigating and do not assume the reader uses `ascii` without observing the configuration.

MVS utility documentation source:
https://www.jaymoseley.com/hercules/os_utilities/mvs_utilities.html
(see the IEBPTPCH `TOTCONV=XE` example).

## D. Implications for BT0021 and the decision boundary

There are **three distinct objectives**, not just CP037 versus current MVS bytes:

1. **Character-preserving archival distribution:** keep the 15 corrected historical source texts and distribute exactly the verified MVS FB80 byte images by IEBCOPY. This preserves current PDS fidelity but does **not** establish historical BCPL compiler lexing semantics.
2. **Standard CP037 representation:** would normalize host character-to-byte mapping but does **not** reproduce the historical BCPL appendix's bracket positions and is not automatically more historically correct.
3. **Historical 370 BCPL lexical compatibility:** use the contemporaneous compiler/manual's character conventions, verify source literal/operator interpretation against a suitable native/historical compiler, and only then approve an encoding suitable for a source that recipients should compile without translation.

`BCPL-0.1.0-rc2` has `native_compiler: absent` and includes the 15 Cambridge historical source files for preservation/reconstruction, not as a runnable native compiler. It may be sensible to **preserve** the measured MVS bytes for this source-only release **if clearly labeled as an archival, transport-encoded representation**. But the previous unqualified preference for MVS-native bytes must not be mistaken for historical source-language correctness. The direct historical EBCDIC chart introduces a meaningful unresolved design criterion.

**Next research/acceptance decision:** ascertain the actual TK5 running `CODEPAGE`, then examine lexer character handling and a bounded compiler parsing probe before choosing a **canonical source-language** encoding. Record what recipient installation documents and source transformation tools must do for `|`, `[`, `]` (and all other affected symbols), rather than silently promising byte portability or editability.

Do not alter `CAMB_SOURCE`, stage `BT0021`, rerun accepted population, change `BT0001`–`BT0020`, mount/write `BC0002`, or change the manifest/registry under this research note. Existing provenance and redistribution-rights gates remain separate.

**TA.2 IN PROGRESS; encoding-policy design decision remains OPEN.**
