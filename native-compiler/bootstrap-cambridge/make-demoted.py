#!/usr/bin/env python3
"""Generate MR10-hostable Cambridge compiler units.

The bootstrap derivative is deliberately mechanical:

- split historical source containers at SECTION boundaries;
- omit SECTION wrappers from resulting compilation units;
- rewrite Cambridge '~=' as token-separated older 'NE';
- map historical member-style GET names to MVS-DD-friendly names;
- split LEX packed reserved-word strings to fit MR10's 255-character limit;
- replace LEX READFLOAT with an explicit bootstrap-only fatal stub because
  MR10 cannot parse Cambridge FLOAT/# floating arithmetic;
- rewrite TRNB's one unary ABS source expression as equivalent older BCPL;
- omit the BCPL master's leading NEEDS "$LOAD$" dependency directive for the
  interpreted all-modules-loaded bootstrap image.

Historical sources remain untouched.  Unexpected source drift fails loudly.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source"
OUT = ROOT / "demoted"
HIST = ROOT.parent.parent / "richards-bcpltape" / "bcplib" / "bcpl"


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


def split_sections(path: Path, names):
    """Split a historical multi-SECTION container into named bodies."""
    text = path.read_text(encoding="utf-8")
    first_header = f'SECTION "{names[0]}"\n'
    if not text.startswith(first_header):
        raise SystemExit(f"{path}: expected leading {first_header!r}")
    rest = text[len(first_header):]
    units = []
    for name in names[1:]:
        marker = f'\n.\nSECTION "{name}"\n'
        if rest.count(marker) != 1:
            raise SystemExit(
                f"{path}: expected exactly one boundary {marker!r}, "
                f"found {rest.count(marker)}"
            )
        body, rest = rest.split(marker, 1)
        units.append(body)
    units.append(rest)
    return units


def demote(text: str) -> str:
    # NE is alphabetic in the MR10 syntax.  Surround it with whitespace so
    # adjacent Cambridge spelling such as SHIFT~=0 cannot become SHIFTNE0.
    text = text.replace("~=", " NE ")
    text = text.replace('GET "HEADERS(SYNHDR)"', 'GET "SYNHDR"')
    text = text.replace('GET "HEADERS(TRNHDR)"', 'GET "TRNHDR"')
    text = text.replace('GET "HEADERS(CGHDR)"', 'GET "CGHDR"')
    return text


def demote_lex_word_table(text: str) -> str:
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
        raise SystemExit(f"LEX: expected one first packed word table, found {text.count(first)}")
    if text.count(second) != 1:
        raise SystemExit(f"LEX: expected one second packed word table, found {text.count(second)}")
    return text.replace(first, first_replacement, 1).replace(second, second_replacement, 1)


def demote_lex_readfloat(text: str) -> str:
    original = '''AND READFLOAT() BE

$(  LET EXP, N = 0, 0
    LET FLTEN = FLOAT 10
    DECVAL := FLOAT DECVAL; SYMB := S.NUMBER
    IF CH='.' THEN
    $(  RCH(); N := VALUE(CH)
        IF N>=10 THEN BREAK
        EXP := EXP-1
        DECVAL := DECVAL #* FLTEN #+ FLOAT N
    $) REPEAT
    IF CH='E' | CH='e' THEN
    $(  LET NEG = FALSE
        RCH(); IF CH='+' | CH='-' THEN  $( NEG := CH='-'; RCH()  $)
        N := DECVAL
        READNUMBER(10)
        TEST NEG THEN EXP := EXP - DECVAL
                   OR EXP := EXP + DECVAL
        DECVAL := N
    $)
    WHILE EXP NE 0 DO
    $(  TEST EXP<0
        THEN  $(  DECVAL := DECVAL #/ FLTEN; EXP := EXP + 1  $)
          OR  $(  DECVAL := DECVAL #* FLTEN; EXP := EXP - 1  $)
    $)
$)'''
    replacement = '''AND READFLOAT() BE
$(  || BOOTSTRAP ONLY: MR10 CANNOT COMPILE CAMBRIDGE FLOAT/# OPERATORS.
    || FAIL RATHER THAN PRODUCE AN INCORRECT FLOATING CONSTANT.
    CAEREPORT(-33)
$)'''
    if text.count(original) != 1:
        raise SystemExit(f"LEX: expected one READFLOAT body, found {text.count(original)}")
    return text.replace(original, replacement, 1)


def demote_trnb_abs(text: str) -> str:
    original = '            CASE S.ABS: RESULTIS ABS EVALCONST(H2X)'
    replacement = '''            CASE S.ABS:
            $(  LET E = EVALCONST(H2X)
                RESULTIS E<0 -> -E, E
            $)'''
    if text.count(original) != 1:
        raise SystemExit(f"TRNB: expected one unary ABS expression, found {text.count(original)}")
    return text.replace(original, replacement, 1)


def demote_master(text: str) -> str:
    prefix = 'SECTION "BCPL"\nNEEDS "$LOAD$"\n\n'
    if not text.startswith(prefix):
        raise SystemExit("bcpl master: expected SECTION BCPL followed by NEEDS $LOAD$")
    return demote(text[len(prefix):])


def demote_cg_target_pack(text: str, section: str) -> str:
    """Use 4-byte target packing only where CG370 constructs target words.

    Both historical target PACKSTRING calls are in section CGA.  The bootstrap
    executes under the MR10 two-bytes-per-word string runtime, while CG370
    expects four 8-bit characters per 32-bit target word.
    """
    if section != "CGA":
        return text

    replacements = (
        ("        PACKSTRING(W, N)",
         "        PACKSTRING370(W, N)"),
        ("        L := PACKSTRING(V, NAMET+2)",
         "        L := PACKSTRING370(V, NAMET+2)"),
    )
    for old, new in replacements:
        if text.count(old) != 1:
            raise SystemExit(
                f"CGA: expected one target PACKSTRING call {old!r}, "
                f"found {text.count(old)}"
            )
        text = text.replace(old, new, 1)

    helper = r"""

AND PACKSTRING370(V, S) = VALOF
$(  || BOOTSTRAP ONLY: pack an unpacked character vector using the
    || System/370 target convention: four 8-bit bytes per 32-bit word.
    LET N = V!0 & #XFF
    LET LAST = N/4

    FOR I = 0 TO LAST DO S!I := 0

    FOR I = 0 TO N DO
    $(  LET J = I/4
        LET SH = 24 - (I&3)*8
        S!J := S!J | ((V!I & #XFF) << SH)
    $)

    RESULTIS LAST
$)
"""
    return text + helper


def write_unit(name: str, historical_section: str, text: str, extra_banner=()) -> None:
    text = demote(text)
    if historical_section == "LEX":
        text = demote_lex_word_table(text)
        text = demote_lex_readfloat(text)
    if historical_section == "TRNB":
        text = demote_trnb_abs(text)

    banner = [
        f'|| BOOTSTRAP DERIVATIVE OF CAMBRIDGE SECTION "{historical_section}".',
        '|| SECTION wrapper omitted for MR10 source-dialect compilation.',
        '|| Historical HEADERS(...) GET names mapped to MVS DDNAMEs.',
    ]
    if historical_section == "LEX":
        banner += [
            '|| Packed reserved-word strings split to fit MR10 literal limits.',
            '|| READFLOAT is a fatal bootstrap stub; floating literals unsupported.',
        ]
    if historical_section == "TRNB":
        banner += ['|| Unary ABS implementation spelling demoted for MR10 compatibility.']
    banner += list(extra_banner)
    (OUT / name).write_text("\n".join(banner) + "\n" + text, encoding="utf-8")


def main() -> None:
    syn_text = (SOURCE / "syn").read_text(encoding="utf-8")
    trn_text = (SOURCE / "trn").read_text(encoding="utf-8")
    master_text = (HIST / "bcpl").read_text(encoding="utf-8")
    cg_text = (HIST / "cg").read_text(encoding="utf-8")

    if syn_text.count("~=") != 1:
        raise SystemExit(f"source/syn: expected one '~=', found {syn_text.count('~=')}")
    if trn_text.count("~=") != 1:
        raise SystemExit(f"source/trn: expected one '~=', found {trn_text.count('~=')}")
    if syn_text.count('GET "HEADERS(SYNHDR)"') != 2:
        raise SystemExit('source/syn: expected exactly two GET "HEADERS(SYNHDR)" occurrences')
    if trn_text.count('GET "HEADERS(TRNHDR)"') != 2:
        raise SystemExit('source/trn: expected exactly two GET "HEADERS(TRNHDR)" occurrences')
    if cg_text.count('GET "HEADERS(CGHDR)"') != 5:
        raise SystemExit('historical cg: expected exactly five GET "HEADERS(CGHDR)" occurrences')

    syn, lex = split_container(SOURCE / "syn", "SYN", "LEX")
    trna, trnb = split_container(SOURCE / "trn", "TRNA", "TRNB")
    cga, cgb, cgc, cgd, cge = split_sections(HIST / "cg", ["CGA", "CGB", "CGC", "CGD", "CGE"])

    OUT.mkdir(exist_ok=True)
    write_unit("syn", "SYN", syn)
    write_unit("lex", "LEX", lex)
    write_unit("trna", "TRNA", trna)
    write_unit("trnb", "TRNB", trnb)

    master = demote_master(master_text)
    master_banner = (
        '|| BOOTSTRAP DERIVATIVE OF CAMBRIDGE SECTION "BCPL".',
        '|| SECTION wrapper omitted for MR10 source-dialect compilation.',
        '|| NEEDS "$LOAD$" omitted: bootstrap loads all compiler units together.',
    )
    (OUT / "bcpl").write_text("\n".join(master_banner) + "\n" + master, encoding="utf-8")

    for name, section, body in (
        ("cga", "CGA", cga), ("cgb", "CGB", cgb), ("cgc", "CGC", cgc),
        ("cgd", "CGD", cgd), ("cge", "CGE", cge),
    ):
        body = demote_cg_target_pack(body, section)
        extra_banner = ()
        if section == "CGA":
            extra_banner = (
                "|| Target PACKSTRING calls use a private 4-byte/word packer;",
                "|| the MR10 host runtime remains two bytes per word.",
            )
        write_unit(name, section, body, extra_banner=extra_banner)

    names = ("syn", "lex", "trna", "trnb", "bcpl", "cga", "cgb", "cgc", "cgd", "cge")
    print("generated:")
    for name in names:
        p = OUT / name
        print(f"  {p.relative_to(ROOT)}  {p.stat().st_size} bytes")


if __name__ == "__main__":
    main()
