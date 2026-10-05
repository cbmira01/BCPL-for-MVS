#!/usr/bin/env python3
"""Generate MR10-source-dialect Cambridge frontend units.

This script performs only the first bootstrap demotion:

- split the historical Cambridge source containers at their SECTION boundaries;
- omit the SECTION wrapper from each resulting compilation unit;
- rewrite the Cambridge not-equal spelling '~=' as the older 'NE' spelling.

It deliberately does not modify headers, runtime assumptions, stream naming,
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
    return text.replace("~=", "NE")


def write_unit(name: str, historical_section: str, text: str) -> None:
    banner = (
        f'|| BOOTSTRAP DERIVATIVE OF CAMBRIDGE SECTION "{historical_section}".\n'
        '|| SECTION wrapper omitted for MR10 source-dialect compilation.\n'
    )
    (OUT / name).write_text(banner + demote(text), encoding="utf-8")


def main() -> None:
    syn_text = (SOURCE / "syn").read_text(encoding="utf-8")
    trn_text = (SOURCE / "trn").read_text(encoding="utf-8")

    # Current source inspection established one Cambridge '~=' occurrence in
    # each historical container.  Keep that assumption explicit so unexpected
    # source drift fails loudly rather than broadening the demotion silently.
    if syn_text.count("~=") != 1:
        raise SystemExit(
            f"source/syn: expected exactly one '~=', found {syn_text.count('~=')}"
        )
    if trn_text.count("~=") != 1:
        raise SystemExit(
            f"source/trn: expected exactly one '~=', found {trn_text.count('~=')}"
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
