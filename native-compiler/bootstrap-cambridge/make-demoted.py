#!/usr/bin/env python3
"""Generate MR10-hostable Cambridge frontend units.

The bootstrap derivative is deliberately mechanical:

- split the historical Cambridge source containers at their SECTION boundaries;
- omit the SECTION wrapper from each resulting compilation unit;
- rewrite the Cambridge not-equal spelling '~=' as the older 'NE' spelling;
- map historical library-member GET names to MVS-DD-friendly names:
    HEADERS(SYNHDR) -> SYNHDR
    HEADERS(TRNHDR) -> TRNHDR
- split Cambridge LEX's packed reserved-word strings into shorter D(...) calls
  that fit the MR10 compiler's 255-character string-literal limit while
  preserving the original reserved-word order.

The GET-name and packed-string rewrites are bootstrap accommodations only. They
do not change header contents or intended compiler semantics.

This script deliberately does not modify header contents, runtime assumptions,
BYTESPERWORD, SKIPREC, compiler initialization, or compiler semantics.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
OUT = ROOT / "demoted"


def split_container(path: Path, first_name: str, second_name: str):
    text = path.read_text(encoding="utf-8")

    first_header = f'SECTION "{first_name}"\n'
    second_marker = f'\n.\nSECTION "{second_name}"\n'

    if not text.startswith(first_header):
        raise SystemExit(f"{path}: expected leading {first_header!r}")
    if text.count(second_marker) != 1:
        raise SystemExit(
            f"{path}: expected exactly one boundary {second_marker!r}, "
            f"found {text.count(second_marker)}"
        )

    first, second = text[len(first_header):].split(second_marker, 1)
    return first, second


def demote(text: str) -> str:
    text = text.replace("~=", "NE")
    text = text.replace('GET "HEADERS(SYNHDR)"', 'GET "SYNHDR"')
    text = text.replace('GET "HEADERS(TRNHDR)"', 'GET "TRNHDR"')
    return text


def demote_lex_word_table(text: str) -> str:
    """Split Cambridge LEX packed word lists for MR10 string compatibility.

    Cambridge LEX uses D(WORDS) to scan slash-delimited names and advances the
    static CODEP across calls. Splitting one long D string into several D calls
    therefore preserves the exact sequence of reserved words and S.* values.
    Each replacement string ends in // so D returns cleanly before the next call.
    """

    first = '''       D("AND/ABS/*
         *BE/BREAK/BY/*
         *CASE/*
         *DO/DEFAULT/*
         *EQ/EQV/ELSE/ENDCASE/*
         *FALSE/FOR/FINISH/FLOAT/FIX/*
         *GOTO/GE/GR/GLOBAL/GET/*
         *IF/INTO/*
         *LET/LV/LE/LS/LOGOR/LOGAND/LOOP/LSHIFT//")'''

    first_replacement = '''       D("AND/ABS/BE/BREAK/BY/CASE/DO/DEFAULT//")
       D("EQ/EQV/ELSE/ENDCASE/FALSE/FOR/FINISH/FLOAT/FIX//")
       D("GOTO/GE/GR/GLOBAL/GET/IF/INTO//")
       D("LET/LV/LE/LS/LOGOR/LOGAND/LOOP/LSHIFT//")'''

    second = '''       D("MANIFEST/*
         *NE/NOT/NEQV/NEEDS/*
         *OF/OR/*
         *RESULTIS/RETURN/REM/RSHIFT/RV/*
         *REPEAT/REPEATWHILE/REPEATUNTIL/*
         *SWITCHON/STATIC/SLCT/SECTION/*
         *TO/TEST/TRUE/THEN/TABLE/*
         *UNTIL/UNLESS/*
         *VEC/VALOF/*
         *WHILE/*
         *$//")'''

    second_replacement = '''       D("MANIFEST/NE/NOT/NEQV/NEEDS/OF/OR//")
       D("RESULTIS/RETURN/REM/RSHIFT/RV//")
       D("REPEAT/REPEATWHILE/REPEATUNTIL//")
       D("SWITCHON/STATIC/SLCT/SECTION//")
       D("TO/TEST/TRUE/THEN/TABLE/UNTIL/UNLESS//")
       D("VEC/VALOF/WHILE/$//")'''

    if text.count(first) != 1:
        raise SystemExit(
            f"LEX: expected exactly one first packed word table, found {text.count(first)}"
        )
    if text.count(second) != 1:
        raise SystemExit(
            f"LEX: expected exactly one second packed word table, found {text.count(second)}"
        )

    text = text.replace(first, first_replacement, 1)
    text = text.replace(second, second_replacement, 1)
    return text


def write_unit(name: str, historical_section: str, text: str) -> None:
    text = demote(text)
    if historical_section == "LEX":
        text = demote_lex_word_table(text)

    banner = (
        f'|| BOOTSTRAP DERIVATIVE OF CAMBRIDGE SECTION "{historical_section}".\n'
        '|| SECTION wrapper omitted for MR10 source-dialect compilation.\n'
        '|| Historical HEADERS(...) GET names mapped to MVS DDNAMEs.\n'
    )
    if historical_section == "LEX":
        banner += (
            '|| Packed reserved-word strings split to fit MR10 literal limits.\n'
        )

    (OUT / name).write_text(banner + text, encoding="utf-8")


def main() -> None:
    syn_text = (SOURCE / "syn").read_text(encoding="utf-8")
    trn_text = (SOURCE / "trn").read_text(encoding="utf-8")

    # Keep all currently known bootstrap rewrites explicit. Unexpected source
    # drift must fail loudly rather than silently broadening the demotion.
    if syn_text.count("~=") != 1:
        raise SystemExit(
            f"source/syn: expected exactly one '~=', found {syn_text.count('~=')}"
        )
    if trn_text.count("~=") != 1:
        raise SystemExit(
            f"source/trn: expected exactly one '~=', found {trn_text.count('~=')}"
        )
    if syn_text.count('GET "HEADERS(SYNHDR)"') != 2:
        raise SystemExit(
            "source/syn: expected exactly two GET \"HEADERS(SYNHDR)\" occurrences"
        )
    if trn_text.count('GET "HEADERS(TRNHDR)"') != 2:
        raise SystemExit(
            "source/trn: expected exactly two GET \"HEADERS(TRNHDR)\" occurrences"
        )

    syn, lex = split_container(SOURCE / "syn", "SYN", "LEX")
    trna, trnb = split_container(SOURCE / "trn", "TRNA", "TRNB")

    OUT.mkdir(exist_ok=True)
    write_unit("syn", "SYN", syn)
    write_unit("lex", "LEX", lex)
    write_unit("trna", "TRNA", trna)
    write_unit("trnb", "TRNB", trnb)

    print("generated:")
    for name in ("syn", "lex", "trna", "trnb"):
        p = OUT / name
        print(f"  {p.relative_to(ROOT)}  {p.stat().st_size} bytes")


if __name__ == "__main__":
    main()
